#!/usr/bin/env python3
"""
异步 HTTP 实战示例（aiohttp）
演示：连接池复用、并发限流、超时重试退避、异步分页抓取、断点续爬、优雅取消

全部请求打向本文件内置的本地 HTTP 服务，不依赖外网，可离线反复运行。
依赖：pip install aiohttp requests
"""

import asyncio
import json
import os
import random
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import aiohttp
import requests

# 只对可恢复状态码重试
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
TOTAL_PAGES = 8


# ============================================
# 被测端：本地多线程 HTTP 服务
# ============================================

class Stats:
    """服务端侧统计，用来反向验证客户端的并发/重试行为真的生效"""

    def __init__(self):
        self.lock = threading.Lock()
        self.active = 0
        self.peak = 0
        self.requests = 0
        self.flaky_hits = {}

    def snapshot(self):
        with self.lock:
            return {"peak": self.peak, "requests": self.requests}

    def reset_peak(self):
        with self.lock:
            self.peak = self.active


class QuietHTTPServer(ThreadingHTTPServer):
    """客户端超时/取消会留下半开连接，socketserver 默认会打印整段 traceback，
    把示例输出刷乱；这里静默掉这类良性错误。"""

    daemon_threads = True
    allow_reuse_address = True
    # socketserver 默认 backlog=SMALL_BACKLOG(5)，高并发下新连接会被直接 RST；
    # 这是「客户端并发一上去就 ConnectionReset」的经典坑，必须显式调大
    request_queue_size = 256
    # socketserver 默认 backlog 只有 5（SMALL_BACKLOG），
    # 异步一次并发几十个连接会直接被内核 RST -> ConnectionResetError
    request_queue_size = 128

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, TimeoutError)):
            try:
                request.close()
            except OSError:
                pass
            return
        super().handle_error(request, client_address)


class DemoAPIHandler(BaseHTTPRequestHandler):
    # 声明 HTTP/1.1 才启用 keep-alive，连接池复用才是可测量的
    protocol_version = "HTTP/1.1"
    server_version = "DemoAPI/1.0"
    # 测试端延迟很短，超时若设成默认 5s，协程取消后会在 accept 线程里留下
    # 大量长时间挂起的半开连接；调到 2s 让服务端主动回收
    timeout = 2

    def log_message(self, fmt, *args):
        """静音默认访问日志，避免干扰示例输出"""

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (TimeoutError, ConnectionResetError, BrokenPipeError):
            self.close_connection = True  # 空闲超时或对端断开：正常关闭该连接

    @property
    def stats(self):
        return self.server.stats

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        delay = float(query.get("delay", ["0"])[0])
        path = parsed.path.rstrip("/") or "/"

        with self.stats.lock:
            self.stats.active += 1
            self.stats.requests += 1
            self.stats.peak = max(self.stats.peak, self.stats.active)
        try:
            if delay:
                time.sleep(delay)  # 每请求一个线程，这里阻塞不影响其它请求

            if path == "/health":
                self._json({"ok": True})
            elif path.startswith("/item/"):
                self._json({"id": path.split("/")[-1], "name": f"记录-{path.split('/')[-1]}"})
            elif path.startswith("/page/"):
                self._page(path)
            elif path.startswith("/flaky/"):
                self._flaky(path)
            elif path.startswith("/boom"):
                self._json({"error": "internal"}, status=500)
            else:
                self._json({"error": "not found", "path": path}, status=404)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass  # 客户端超时/取消后提前断开，属正常（3.10+ 的 socket.timeout 即 TimeoutError）
        finally:
            with self.stats.lock:
                self.stats.active -= 1

    def _page(self, path):
        page = int(path.split("/")[-1])
        self._json(
            {
                "page": page,
                "items": [{"page": page, "n": i} for i in range(3)],
                "has_next": page < TOTAL_PAGES,
            }
        )

    def _flaky(self, path):
        """同一 key 前两次 503，第三次起成功"""
        key = path.split("/")[-1]
        with self.stats.lock:
            self.stats.flaky_hits[key] = self.stats.flaky_hits.get(key, 0) + 1
            attempt = self.stats.flaky_hits[key]
        if attempt <= 2:
            self._json({"attempt": attempt, "error": "temporarily unavailable"}, status=503)
        else:
            self._json({"attempt": attempt, "ok": True})


def start_server():
    """守护线程里启动本地服务，返回 (server, base_url, stats)"""
    server = QuietHTTPServer(("127.0.0.1", 0), DemoAPIHandler)
    server.stats = Stats()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}", server.stats


def banner(title):
    print(f"\n【{title}】")


# ============================================
# 1. 会话复用：一个 ClientSession = 一个连接池
# ============================================

async def demo_session_reuse(base_url):
    banner("1. ClientSession 复用 vs 每次新建")

    urls = [f"{base_url}/item/{i}" for i in range(30)]

    # 反例：每次请求新建 session，等于每次都重新建连
    start = time.time()
    for url in urls:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                await resp.json()
    cold = time.time() - start

    # 正解：复用同一个 session（内部 TCPConnector 连接池）
    start = time.time()
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*(session.get(url) for url in urls))
        bodies = [await resp.json() for resp in responses]
        for resp in responses:
            resp.release()
    reused = time.time() - start

    print(f"  每请求新建 session: {cold:.3f}s / {len(urls)} 次")
    print(f"  复用单 session   : {reused:.3f}s / {len(urls)} 次，解析 {len(bodies)} 条 JSON")
    print("  本机回环握手极便宜，所以差距只有几毫秒；换成真实 HTTPS 站点通常是数倍差距")
    print("  要点：session 全程共用，进程结束前统一关闭；频繁新建会耗尽端口与 FD")


# ============================================
# 2. 吞吐：同步线程池 vs 异步全并发（服务端实测并发数佐证）
# ============================================

def sync_versions(base_url, count, delay):
    """同步 requests + 10 线程：并发上限由线程数决定"""
    from concurrent.futures import ThreadPoolExecutor

    def fetch(i):
        resp = requests.get(f"{base_url}/item/{i}", params={"delay": delay}, timeout=5)
        return resp.json()

    with ThreadPoolExecutor(max_workers=10) as pool:
        return list(pool.map(fetch, range(count)))


async def async_version(base_url, count, delay, stats):
    """异步：40 个慢请求同时发起，上限由 connector.limit 决定"""
    stats.reset_peak()
    connector = aiohttp.TCPConnector(limit=40)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [session.get(f"{base_url}/item/{i}", params={"delay": delay}) for i in range(count)]
        responses = await asyncio.gather(*tasks)
        results = [await resp.json() for resp in responses]
        for resp in responses:
            resp.release()
    return results, stats.snapshot()["peak"]


async def demo_throughput(base_url, stats):
    banner("2. 高并发吞吐：requests+线程池 vs aiohttp")

    count, delay = 40, 0.3
    print(f"  任务：{count} 个 {delay}s 的慢接口，理论串行 {count * delay:.1f}s")

    stats.reset_peak()
    start = time.time()
    sync_results = await asyncio.to_thread(sync_versions, base_url, count, delay)
    sync_time = time.time() - start
    sync_peak = stats.snapshot()["peak"]

    start = time.time()
    async_results, async_peak = await async_version(base_url, count, delay, stats)
    async_time = time.time() - start

    print(f"  requests(10 线程): {sync_time:.2f}s，{len(sync_results)} 条，服务端实测并发 {sync_peak}")
    print(f"  aiohttp(limit=40): {async_time:.2f}s，{len(async_results)} 条，服务端实测并发 {async_peak}")
    print(f"  异步比同步快 {sync_time / async_time:.1f}x；瓶颈从「线程数」变成「下游能不能扛住」")


# ============================================
# 3. 限流：客户端 Semaphore，服务端验证
# ============================================

async def demo_rate_limit(base_url, stats):
    banner("3. 并发限流（保护下游）")

    async def fetch_all(limit, count=20):
        semaphore = asyncio.Semaphore(limit)

        async def fetch(session, i):
            async with semaphore:  # 拿到令牌才发请求
                async with session.get(f"{base_url}/item/{i}", params={"delay": 0.3}) as resp:
                    return await resp.json()

        async with aiohttp.ClientSession() as session:
            start = time.time()
            stats.reset_peak()
            results = await asyncio.gather(*(fetch(session, i) for i in range(count)))
            return time.time() - start, len(results), stats.snapshot()["peak"]

    for limit in (5, 20):
        elapsed, ok, peak = await fetch_all(limit)
        print(f"  Semaphore({limit:>2}): 20 个请求耗时 {elapsed:.2f}s，成功 {ok}，服务端观测并发 {peak}")

    print("  说明：Semaphore 限制的是「同时在途请求数」，服务端并发峰值随之一致")
    print("  进阶：需要限制 QPS（而非并发数）时用令牌桶，见 08_real_world_examples.py 场景 2")


# ============================================
# 4. 超时 / 重试 / 指数退避
# ============================================

async def fetch_with_retry(session, url, *, retries=4, base_delay=0.05):
    """只重试可恢复错误，指数退避 + 随机抖动"""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=1.0)) as resp:
                if resp.status in RETRYABLE_STATUS:
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history, status=resp.status, message=f"可重试 {resp.status}"
                    )
                resp.raise_for_status()  # 其余 4xx 直接抛，不重试
                return await resp.json(), attempt
        except asyncio.TimeoutError as exc:
            last_error = exc
        except aiohttp.ClientResponseError as exc:
            if exc.status not in RETRYABLE_STATUS:
                raise
            last_error = exc
        except aiohttp.ClientError as exc:  # 连接类错误
            last_error = exc

        if attempt == retries:
            break
        backoff = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
        print(f"    第 {attempt} 次失败({type(last_error).__name__})，{backoff * 1000:.0f}ms 后重试")
        await asyncio.sleep(backoff)

    raise last_error


async def demo_retry(base_url, stats):
    banner("4. 超时 / 重试 / 退避 / 不重试 4xx")

    async with aiohttp.ClientSession() as session:
        # 4.1 前两次 503，第三次成功
        before = stats.snapshot()["requests"]
        payload, attempts = await fetch_with_retry(session, f"{base_url}/flaky/order-1")
        print(f"  503 重试: 共 {attempts} 次请求后成功 -> {payload}（服务端收到 {stats.snapshot()['requests'] - before} 次）")

        # 4.2 404 不重试：服务端只应收到 1 次请求
        before = stats.snapshot()["requests"]
        try:
            await fetch_with_retry(session, f"{base_url}/not-exist", retries=4)
        except aiohttp.ClientResponseError as exc:
            print(f"  404 立刻失败: {exc.status}，服务端实际收到 {stats.snapshot()['requests'] - before} 次请求")

        # 4.3 持续 500：重试到上限后放弃（必须放弃，否则雪崩）
        before = stats.snapshot()["requests"]
        try:
            await fetch_with_retry(session, f"{base_url}/boom", retries=3, base_delay=0.02)
        except aiohttp.ClientResponseError as exc:
            print(f"  重试上限: 3 次仍失败，抛出 {exc.status}；服务端收到 {stats.snapshot()['requests'] - before} 次")

        # 4.4 总超时：3 秒响应只等 0.5 秒
        start = time.time()
        try:
            async with session.get(f"{base_url}/item/1", params={"delay": 3},
                                   timeout=aiohttp.ClientTimeout(total=0.5)):
                pass
        except asyncio.TimeoutError:
            print(f"  ClientTimeout(total=0.5) 生效，{time.time() - start:.2f}s 丢弃慢请求，不拖垮整批")

        # 4.5 分段超时：建连/读取/总时长可分别设置
        precise = aiohttp.ClientTimeout(connect=0.2, sock_read=1.0, total=2.0)
        async with session.get(f"{base_url}/item/2", timeout=precise) as resp:
            print(f"  分段超时示例: {resp.status}")

    print("  要点：重试要有上限、要退避加抖动，且绝不重试 4xx（除了 408/429）")


# ============================================
# 5. 异步分页抓取
# ============================================

async def paginate(session, base_url, start_page=1, max_pages=None):
    """按 has_next 逐页推进，边拿边产出，不在内存堆全量"""
    page = start_page
    count = 0
    while True:
        async with session.get(f"{base_url}/page/{page}") as resp:
            resp.raise_for_status()
            data = await resp.json()
        yield data
        count += 1
        if not data["has_next"] or (max_pages and count >= max_pages):
            return
        page += 1


async def demo_pagination(base_url):
    banner("5. 异步分页抓取")

    async with aiohttp.ClientSession() as session:
        pages = []
        async for data in paginate(session, base_url, max_pages=3):
            pages.append(data["page"])
        print(f"  流式 + 提前停止: 只抓了 {pages}")

        async def one(page):
            async with session.get(f"{base_url}/page/{page}") as resp:
                return await resp.json()

        results = await asyncio.gather(*(one(p) for p in range(1, TOTAL_PAGES + 1)))
        print(f"  并发抓 {TOTAL_PAGES} 页: 共 {sum(len(r['items']) for r in results)} 条，"
              f"页序保持 {[r['page'] for r in results]}")


# ============================================
# 6. 断点续爬：checkpoint + 增量落盘
# ============================================

def load_checkpoint(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"done": [], "failed": []}


def save_checkpoint(path, state):
    """先写临时文件再原子替换：进程被 kill 也不会留下半截 JSON"""
    tmp = str(path) + ".tmp"
    Path(tmp).write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


async def append_lines(path, lines):
    """文件 IO 交给线程，避免卡住事件循环"""

    def _write():
        with open(path, "a", encoding="utf-8") as fp:
            fp.writelines(line + "\n" for line in lines)

    await asyncio.to_thread(_write)


async def crawl(base_url, workdir, *, break_on=None):
    """抓全部页；break_on 模拟本地处理崩溃，验证续跑"""
    ckpt_path = Path(workdir) / "checkpoint.json"
    out_path = Path(workdir) / "results.jsonl"
    state = load_checkpoint(ckpt_path)
    done = set(state["done"])
    pending = [p for p in range(1, TOTAL_PAGES + 1) if p not in done]
    print(f"  已完成 {len(done)} 页，本次待抓 {len(pending)} 页: {pending}")

    semaphore = asyncio.Semaphore(4)
    server_requests = 0

    async def worker(session, page):
        nonlocal server_requests
        async with semaphore:
            async with session.get(f"{base_url}/page/{page}") as resp:
                resp.raise_for_status()
                data = await resp.json()
            server_requests += 1
            if page == break_on:
                raise ValueError(f"模拟第 {page} 页解析失败")
            await append_lines(out_path, [json.dumps(data, ensure_ascii=False)])
            done.add(page)
            state["done"] = sorted(done)
            save_checkpoint(ckpt_path, state)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(worker(session, p) for p in pending), return_exceptions=True)

    errors = [r for r in results if isinstance(r, Exception)]
    state["failed"] = sorted({p for p in pending if p not in done})
    save_checkpoint(ckpt_path, state)
    print(f"  本轮真实发出 {server_requests} 个请求，失败 {len(errors)} 页"
          f"{'（' + str(errors[0]) + '）' if errors else ''}")
    print(f"  checkpoint: done={state['done']} failed={state['failed']}")
    return state


async def demo_checkpoint(base_url):
    banner("6. 断点续爬（checkpoint + 原子写入）")

    with tempfile.TemporaryDirectory() as workdir:
        await crawl(base_url, workdir, break_on=5)
        print("  —— 修复解析逻辑后重跑（期望：只补抓失败的那 1 页）——")
        second = await crawl(base_url, workdir)

        lines = (Path(workdir) / "results.jsonl").read_text(encoding="utf-8").strip().splitlines()
        print(f"  最终落盘 {len(lines)} 行 JSONL，全部页 done={second['done']}")
        print("  要点：done 集合 + 原子 checkpoint + 追加式 JSONL = 跑一半也不怕挂")


# ============================================
# 7. 优雅取消
# ============================================

async def demo_graceful_cancel(base_url):
    banner("7. 优雅停止（模拟 Ctrl+C）")

    finished = []

    async def worker(session, i):
        async with session.get(f"{base_url}/item/{i}", params={"delay": 0.4}) as resp:
            await resp.json()
            finished.append(i)

    async def runner():
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*(worker(session, i) for i in range(20)))

    task = asyncio.create_task(runner())
    await asyncio.sleep(0.5)
    print(f"  运行 0.5s 后发出停止信号，此刻完成 {len(finished)} 个")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print(f"  取消后未再推进: 最终完成 {len(finished)} 个（session 由 async with 兜底关闭）")
    print("""
  常驻服务的标准写法：
      loop = asyncio.get_running_loop()
      for sig in (signal.SIGINT, signal.SIGTERM):
          loop.add_signal_handler(sig, lambda: stop_event.set())
      # 收到信号后：停止投递新任务 -> 等在途任务跑完 -> 保存 checkpoint -> 关闭 session
      # 绝不能用 task.cancel() 硬切正在写库/扣款的协程（用 05 节的 shield 保护临界段）""")


# ============================================
# 8. 生产配置与常见坑
# ============================================

def demo_production_tips():
    banner("8. 生产环境配置清单")

    print("""
  connector = aiohttp.TCPConnector(
      limit=100,             # 全局最大连接数
      limit_per_host=20,     # 单主机连接数：尊重对方容量，别把自己变成 DoS
      ttl_dns_cache=300,     # DNS 缓存，避免每请求重新解析
      enable_cleanup_closed=True,
  )
  timeout = aiohttp.ClientTimeout(total=10, connect=3, sock_read=5)
  session = aiohttp.ClientSession(connector=connector, timeout=timeout,
                                  headers={"User-Agent": "study-bot/1.0"},
                                  raise_for_status=True)   # TLS 校验保持默认开启

  常见坑：
  1. 忘关 session / 每请求新建 session -> FD 与临时端口耗尽，长跑必崩
  2. 不设 limit_per_host -> 单站点被打爆，会被对方封 IP
  3. gather 一次提交 10 万个协程 -> 内存与 FD 双爆，务必配合 Semaphore
  4. 协程里混用 requests -> 事件循环被冻住，吞吐不如单线程（见第 2 节）
  5. 只设 total 不设 connect -> 建连卡死时整个 total 被吃光，定位困难
  6. resp.json() 前不检查 Content-Type -> HTML 错误页抛 ContentTypeError
  7. 重试不加抖动 -> 下游恢复瞬间被同步重试的客户端再次打挂
""")


async def main():
    print("=" * 60)
    print("异步 HTTP 实战示例（aiohttp）")
    print("=" * 60)

    server, base_url, stats = start_server()
    print(f"  本地被测服务: {base_url}（全程离线，可反复运行）")
    try:
        await demo_session_reuse(base_url)
        await demo_throughput(base_url, stats)
        await demo_rate_limit(base_url, stats)
        await demo_retry(base_url, stats)
        await demo_pagination(base_url)
        await demo_checkpoint(base_url)
        await demo_graceful_cancel(base_url)
        demo_production_tips()
    finally:
        snap = stats.snapshot()
        print(f"\n  服务端累计处理 {snap['requests']} 个请求，全程观测到的最大并发 {snap['peak']}")
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 60)
    print("异步 HTTP 实战示例完成")
    print("=" * 60)
    print("\n提示：")
    print("  1. 一个进程一个 ClientSession，连接池 / 超时 / TLS 都配在它上面")
    print("  2. 真实并发 = Semaphore 与 TCPConnector.limit 中较小者，两层都要设")
    print("  3. 重试只针对 5xx / 超时 / 连接错误，且必须退避 + 抖动 + 次数上限")
    print("  4. 断点续爬三件套：done 集合、原子 checkpoint、追加式 JSONL")
    print("  5. CPU 解析放协程里没收益，交给进程池（见 04 节）")


if __name__ == "__main__":
    asyncio.run(main())
