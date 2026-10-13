#!/usr/bin/env python3
"""
并发选型真实场景案例
演示：批量文件处理、令牌桶限 QPS + 熔断降级、日志异步落盘、
     IO+CPU 混合流水线（背压）、常驻服务优雅停机

全部用本地模拟负载，不依赖外网与第三方库，可反复运行。
"""

import logging
import os
import queue
import signal
import threading
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from tempfile import TemporaryDirectory

# ============================================
# 场景 1：批量文件处理（线程池 + 进度 + 原子替换）
# ============================================


def transform_file(src: Path, dst: Path) -> int:
    """读取 -> 处理 -> 原子且持久地写回

    标准写法：写 .tmp -> flush -> fsync -> os.replace。
    只 replace 不 fsync，断电时可能留下 0 字节文件；fsync 才是真正的磁盘等待，
    也正是它让线程池有意义的地方。
    """
    text = src.read_text(encoding="utf-8")
    lines = [line.strip().upper() for line in text.splitlines() if line.strip()]
    payload = f"{src.name}|{len(lines)}\n" + "\n".join(lines) + "\n"

    tmp = dst.with_suffix(dst.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fp:
        fp.write(payload)
        fp.flush()
        os.fsync(fp.fileno())
    os.replace(tmp, dst)
    return len(lines)


def scenario_batch_files(worker_count=8, file_count=200):
    print("\n" + "=" * 60)
    print("【场景 1：批量文件处理 —— 线程池 + 进度反馈 + 原子写】")
    print("=" * 60)

    with TemporaryDirectory() as workdir:
        root = Path(workdir)
        src_dir = root / "src"
        dst_dir = root / "out"
        src_dir.mkdir()
        dst_dir.mkdir()

        for i in range(file_count):
            (src_dir / f"data_{i:03d}.txt").write_text(
                "\n".join(f"row {i}-{j}" for j in range(200)), encoding="utf-8"
            )

        files = sorted(src_dir.glob("*.txt"))

        start = time.time()
        serial_lines = sum(transform_file(f, dst_dir / f.name) for f in files)
        serial_time = time.time() - start

        # 重置输出目录再并发跑，保证两次统计可比
        for f in dst_dir.glob("*.txt"):
            f.unlink()

        start = time.time()
        done_count = 0
        lock = threading.Lock()

        def handle(f):
            nonlocal done_count
            lines = transform_file(f, dst_dir / f.name)
            with lock:
                done_count += 1
                if done_count % 20 == 0:
                    print(f"    进度 {done_count}/{len(files)}")
            return lines

        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(handle, files))

        thread_time = time.time() - start
        produced = len(list(dst_dir.glob("*.txt")))
        print(f"  {file_count} 个文件（各 200 行）")
        print(f"  串行: {serial_time:.2f}s   {worker_count} 线程: {thread_time:.2f}s"
              f"   加速 {serial_time / thread_time:.1f}x")
        print(f"  产出校验: {produced}/{file_count} 个文件，累计 {sum(results)} 行（串行口径 {serial_lines} 行）")
        print("  要点：进度计数必须加锁；写文件走 .tmp -> fsync -> os.replace 才算原子且持久")
        print("  经验：加速比 = 等待占比 × 并行度。本机 SSD 上 fsync 很快，所以只有 1.5x；")
        print("        远程挂载盘/NFS 上这段等待会变成几十倍 —— 先量测再决定是否并发")


# ============================================
# 场景 2：令牌桶限 QPS + 熔断降级
# ============================================


class TokenBucket:
    """线程安全令牌桶：限制「每秒请求数」

    Semaphore 限的是并发数，令牌桶限的是速率 —— 下游按 QPS 配额时必须用后者。
    """

    def __init__(self, rate, capacity=None):
        self.rate = rate
        self.capacity = capacity or rate
        self.tokens = self.capacity
        self.updated = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self, timeout=None):
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                wait = (1 - self.tokens) / self.rate
            if deadline is not None and time.monotonic() + wait > deadline:
                return False
            time.sleep(wait)


class CircuitBreaker:
    """熔断器：连续失败达阈值后快速失败，给下游恢复时间"""

    CLOSED, OPEN, HALF = "closed", "open", "half-open"

    def __init__(self, failure_threshold=3, recovery_seconds=1.0):
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.state = self.CLOSED
        self.failures = 0
        self.opened_at = 0.0
        self.lock = threading.Lock()

    def allow(self):
        with self.lock:
            if self.state == self.CLOSED:
                return True
            if time.monotonic() - self.opened_at >= self.recovery_seconds:
                self.state = self.HALF  # 放一个探测请求过去
                return True
            return False

    def record(self, ok):
        with self.lock:
            if ok:
                self.failures = 0
                self.state = self.CLOSED
            else:
                self.failures += 1
                if self.state == self.HALF or self.failures >= self.failure_threshold:
                    self.state = self.OPEN
                    self.opened_at = time.monotonic()


def scenario_rate_limit(requests=60, qps=20, workers=30):
    print("\n" + "=" * 60)
    print("【场景 2：限流 —— 令牌桶控 QPS + 熔断降级】")
    print("=" * 60)

    stats = defaultdict(int)
    lock = threading.Lock()
    bucket = TokenBucket(rate=qps, capacity=min(5, qps))
    breaker = CircuitBreaker(failure_threshold=3, recovery_seconds=0.6)

    outage = range(20, 34)  # 模拟下游一段持续故障窗口

    def call_api(i):
        """模拟外部接口调用：落在故障窗口内的请求由下游返回失败"""
        if not bucket.acquire(timeout=5):
            with lock:
                stats["等待超时放弃"] += 1
            return
        if not breaker.allow():
            with lock:
                stats["熔断快速失败(走缓存)"] += 1
            return
        ok = i not in outage
        time.sleep(0.02)  # 模拟网络往返
        breaker.record(ok)
        with lock:
            stats["成功" if ok else "下游返回失败"] += 1

    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(call_api, range(requests)))
    elapsed = time.time() - start

    print(f"  {requests} 个请求，桶速 {qps} QPS，突发额度 {bucket.capacity}，"
          f"耗时 {elapsed:.2f}s -> 平均 {requests / elapsed:.1f} QPS")
    print(f"  平均值略高于桶速属正常：起始 {bucket.capacity} 个令牌可一次性突发，稳态速率被钳在 {qps}")
    for key, value in sorted(stats.items()):
        print(f"    {key}: {value}")
    print(f"  结束时熔断状态: {breaker.state}")
    print("  要点：限流保护下游配额，熔断保护自己在雪崩时不排队，两者都要有降级路径")
    print("  协程版限流只需把 time.sleep 换成 asyncio.sleep + asyncio.Lock（见 06 第 3 节）")


# ============================================
# 场景 3：日志异步落盘（业务线程不做磁盘 IO）
# ============================================


class SlowSinkHandler(logging.Handler):
    """模拟远程日志服务 / 带 fsync 的落盘：每条记录固定耗时，放大同步日志的代价"""

    def __init__(self, sink, per_record_ms=0.3):
        super().__init__()
        self.sink = sink
        self.per_record_ms = per_record_ms

    def emit(self, record):
        self.sink.append(self.format(record))
        time.sleep(self.per_record_ms / 1000)


def _make_logger(name, handler):
    logger = logging.getLogger(name)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def scenario_async_logging(count=3000, per_record_ms=0.3):
    print("\n" + "=" * 60)
    print("【场景 3：日志异步落盘 —— QueueHandler + QueueListener】")
    print("=" * 60)

    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler_cost = count * per_record_ms / 1000

    # A. 同步：慢 handler 直接挂在业务线程上
    sink_sync = []
    sync_handler = SlowSinkHandler(sink_sync, per_record_ms)
    sync_handler.setFormatter(formatter)
    logger_sync = _make_logger("demo.sync_log", sync_handler)

    start = time.time()
    for i in range(count):
        logger_sync.info("处理订单 %s 完成", i)
    sync_time = time.time() - start

    # B. 异步：业务线程只做一次 put_nowait，慢 IO 由 listener 线程承担
    sink_async = []
    async_handler = SlowSinkHandler(sink_async, per_record_ms)
    async_handler.setFormatter(formatter)
    log_queue = queue.Queue(maxsize=count * 2)
    logger_async = _make_logger("demo.async_log", QueueHandler(log_queue))
    listener = QueueListener(log_queue, async_handler, respect_handler_level=True)
    listener.start()

    start = time.time()
    for i in range(count):
        logger_async.info("处理订单 %s 完成", i)
    business_time = time.time() - start

    start = time.time()
    listener.stop()  # stop 会排空队列，保证不丢日志
    drain_time = time.time() - start

    print(f"  模拟慢 handler：每条 {per_record_ms}ms（远程 syslog / 带 fsync 的落盘），"
          f"纯 handler 成本约 {handler_cost * 1000:.0f} ms")
    print(f"  同步：业务线程被占用 {sync_time * 1000:6.0f} ms")
    print(f"  异步：业务线程只占用 {business_time * 1000:6.0f} ms，"
          f"后台线程再排空 {drain_time * 1000:6.0f} ms")
    print(f"  业务线程解放 {sync_time / max(business_time, 1e-6):.0f}x；"
          f"落盘校验 同步 {len(sink_sync)} 条 / 异步 {len(sink_async)} 条，均应为 {count}")
    print("  注意：异步不减少总开销，只是把 IO 搬到后台线程 —— 收益是日志服务卡顿时主流程不受牵连")
    print("  注意：QueueHandler 仍在业务线程做格式化，所以日志本身的构造成本（f-string / dict 序列化）仍要省着写")
    print("  要点：进程退出前必须 listener.stop()，否则队列里未落盘的日志直接丢")


# ============================================
# 场景 4：IO + CPU 混合流水线（有界队列 = 背压）
# ============================================


def parse_cpu(text):
    """CPU 密集解析：必须放子进程，否则 GIL 下线程池毫无收益"""
    total = 0
    for n in range(400000):
        total += (n * 3) % 7
    return {"raw": text, "checksum": total}


def fake_fetch(index):
    """模拟网络抓取"""
    time.sleep(0.15)
    return f"payload-{index}"


def scenario_pipeline(item_count=12, fetch_workers=4, cpu_workers=2):
    print("\n" + "=" * 60)
    print("【场景 4：抓取(线程) -> 解析(进程) -> 落盘(线程) 三段流水线】")
    print("=" * 60)

    # 单位成本先量一次，用于给出诚实的串行基线
    t0 = time.time()
    fake_fetch(0)
    fetch_cost = time.time() - t0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=1) as probe:
        probe.submit(parse_cpu, "probe").result()
    parse_cost = time.time() - t0

    raw_q = queue.Queue(maxsize=fetch_workers * 2)  # 有界 -> 下游慢时上游自动阻塞
    parsed_q = queue.Queue()
    counts = defaultdict(int)
    lock = threading.Lock()

    def bump(key):
        with lock:
            counts[key] += 1

    def fetch_stage(i):
        raw_q.put(fake_fetch(i))
        bump("fetched")

    def parse_relay(cpu_pool):
        """从 raw_q 取任务丢进进程池；收到哨兵后把完成的结果转发给落盘阶段"""
        futures = []
        while True:
            item = raw_q.get()
            raw_q.task_done()
            if item is None:  # 上游结束哨兵
                break
            futures.append(cpu_pool.submit(parse_cpu, item))

        for future in as_completed(futures):
            parsed_q.put(future.result())
            bump("parsed")
        parsed_q.put(None)

    def write_stage(results_path):
        while True:
            record = parsed_q.get()
            if record is None:
                parsed_q.task_done()
                break
            with open(results_path, "a", encoding="utf-8") as fp:
                fp.write(f"{record['raw']} -> {record['checksum']}\n")
            bump("written")
            parsed_q.task_done()

    with TemporaryDirectory() as workdir:
        out = Path(workdir) / "pipeline.txt"
        start = time.time()

        with ProcessPoolExecutor(max_workers=cpu_workers) as cpu_pool, \
                ThreadPoolExecutor(max_workers=fetch_workers) as fetch_pool:
            relay = threading.Thread(target=parse_relay, args=(cpu_pool,))
            writer = threading.Thread(target=write_stage, args=(out,))
            relay.start()
            writer.start()

            list(fetch_pool.map(fetch_stage, range(item_count)))
            raw_q.put(None)  # 抓取全部完成，通知 relay 收尾

            relay.join(timeout=30)
            writer.join(timeout=30)

        pipeline_time = time.time() - start
        lines_written = out.read_text(encoding="utf-8").count("\n")

    serial_time = item_count * (fetch_cost + parse_cost)
    print(f"  单位成本：抓取 {fetch_cost * 1000:.0f}ms，解析 {parse_cost * 1000:.0f}ms")
    print(f"  若完全串行: 约 {serial_time:.2f}s")
    print(f"  流水线实际: {pipeline_time:.2f}s（抓取 {counts['fetched']}"
          f" / 解析 {counts['parsed']} / 落盘 {counts['written']}，文件 {lines_written} 行）")
    print(f"  加速比: {serial_time / pipeline_time:.1f}x —— 三段同时在跑，互不等待")
    print("  要点：有界 Queue 提供背压；哨兵 None 表示阶段结束；CPU 段必须用进程池")


# ============================================
# 场景 5：常驻消费者服务 + 优雅停机
# ============================================

stop_flag = threading.Event()


def worker_loop(name, task_q):
    """常驻 worker：只在安全点退出，不在处理任务的中途被切断"""
    while not stop_flag.is_set():
        try:
            task = task_q.get(timeout=0.2)
        except queue.Empty:
            continue
        try:
            time.sleep(0.1)  # 模拟一段不宜中断的工作
            print(f"    {name} 处理完 {task}")
        finally:
            task_q.task_done()  # 必须归还，否则 join() 永不返回
    print(f"    {name} 收到停机信号，安全退出")


def scenario_graceful_shutdown(pending=10, drain_seconds=0.6):
    print("\n" + "=" * 60)
    print("【场景 5：常驻服务优雅停机（SIGTERM -> 排空队列 -> 退出）】")
    print("=" * 60)

    task_q = queue.Queue()
    workers = [threading.Thread(target=worker_loop, args=(f"W{i}", task_q)) for i in range(3)]
    for w in workers:
        w.start()

    for i in range(pending):
        task_q.put(f"task-{i}")

    def on_signal(signum, frame):
        """信号处理函数只做一件事：置标志位。绝不能在里面写业务逻辑"""
        print(f"\n  收到 {signal.Signals(signum).name}，停止接收新任务并开始排空")
        stop_flag.set()

    prev_int = signal.signal(signal.SIGINT, on_signal)
    prev_term = signal.signal(signal.SIGTERM, on_signal)

    time.sleep(0.2)
    start = time.time()
    os.kill(os.getpid(), signal.SIGTERM)  # 模拟运维发起滚动发布

    # 排空在途任务（有超时兜底，避免永久卡住）
    deadline = time.time() + drain_seconds
    drained = 0
    while not task_q.empty() and time.time() < deadline:
        time.sleep(0.05)
        drained += 1
    drain_time = time.time() - start

    for w in workers:
        w.join(timeout=2)

    signal.signal(signal.SIGINT, prev_int)
    signal.signal(signal.SIGTERM, prev_term)
    stop_flag.clear()

    print(f"  停机耗时 {drain_time:.2f}s，退出时队列剩余 {task_q.qsize()} 个任务")
    print(f"  worker 全部退出: {not any(w.is_alive() for w in workers)}")
    print("  要点：SIGTERM 是把内存状态落盘的最后机会；kill -9 没有这个机会")
    print("  生产建议：K8s 里把 terminationGracePeriodSeconds 设得大于最坏排空时间")


# ============================================
# 场景 6：选型速查
# ============================================

def scenario_decision_table():
    print("\n" + "=" * 60)
    print("【场景 6：选型速查（对应本目录其它示例）】")
    print("=" * 60)

    print(f"""
  负载特征                      推荐方案             对应示例
  ──────────────────────────────────────────────────────────────
  几百个文件 / DB 查询          线程池               场景 1、02_threading_advanced
  上千并发 HTTP（纯 I/O 等待）  asyncio + aiohttp    06_asyncio_advanced
  按 QPS 配额调第三方 API       令牌桶 + 熔断        场景 2
  图像/视频/数值计算            进程池               04_multiprocessing_advanced
  CPU + IO 混合长任务           线程抓取 + 进程计算  场景 4
  日志/埋点不能拖慢主流程       队列 + 后台线程      场景 3
  常驻消费者服务                线程 + 信号处理      场景 5
  FastAPI 里只能用同步 DB 驱动  asyncio.to_thread    05_asyncio_basics 第 8 节
  CPU 核数利用率上不去          先量测再改           07_performance_comparison

  三条通用原则：
  1. 先量测再并发：没有对比数据的优化都是猜测
  2. 并发免费带来 bug：共享状态一律加锁，或干脆用队列传递所有权
     （见 race_condition_demo.py / race_condition_extreme.py）
  3. 长跑任务必须能安全停机：信号处理 + 有界队列 + checkpoint 三件套
""")


def main():
    print("=" * 60)
    print("并发编程真实场景案例")
    print("=" * 60)

    scenario_batch_files()
    scenario_rate_limit()
    scenario_async_logging()
    scenario_pipeline()
    scenario_graceful_shutdown()
    scenario_decision_table()

    print("\n" + "=" * 60)
    print("真实场景案例完成")
    print("=" * 60)
    print("\n提示：")
    print("  1. 每个场景都是独立函数，参数可调，方便单独跑或改成压测脚本")
    print("  2. 场景 2 的令牌桶与熔断器是可直接搬进生产代码的最小实现")
    print("  3. 场景 4 的有界队列 + 哨兵，是多阶段流水线的标准骨架")
    print("  4. 想改造成真实项目：把 fake_fetch 换成 aiohttp/requests，parse 换成实际解析")


if __name__ == "__main__":
    main()
