#!/usr/bin/env python3
"""
异步编程基础示例
演示：协程本质、并发调度、超时取消、asyncio 同步原语、与同步代码桥接

对标 00-docs/python_concurrency_guide.md 的「异步编程详解」章节。
"""

import asyncio
import threading
import time

# 同上：不要在模块级产生副作用，asyncio 相关示例也遵守这个习惯


async def say_after(delay, what):
    """最简单的协程：等 delay 秒后返回 what"""
    await asyncio.sleep(delay)
    return f"{what} (等待 {delay}s)"


def banner(title):
    print(f"\n【{title}】")


# ============================================
# 1. 协程不会自己执行
# ============================================

async def demo_coroutine_is_lazy():
    banner("1. 协程对象不会自动执行")

    coro = say_after(0.1, "Hello")
    print(f"  调用 async 函数得到的是: {type(coro).__name__} -> {coro}")
    print("  ⚠️  此时一行代码都没执行，必须 await 或交给事件循环")

    result = await coro
    print(f"  await 之后才有结果: {result}")

    # 同一个协程对象不能重复 await（已被消费）
    try:
        await coro
    except RuntimeError as e:
        print(f"  重复 await 同一个协程: {type(e).__name__}: {e}")

    # 未 await 的协程会被 GC 报警
    async def leak():
        await say_after(0.01, "x")

    leak()  # 故意不 await
    await asyncio.sleep(0.05)
    print("  上面调用 leak() 未 await，运行时会输出 'coroutine was never awaited' 警告")


# ============================================
# 2. 串行 await vs 并发调度（最常见的性能陷阱）
# ============================================

async def demo_sequential_vs_concurrent():
    banner("2. await 串行 ≠ 并发")

    tasks_spec = [(1, "A"), (1, "B"), (1, "C")]

    # 2.1 逐个 await：前一个完成才开始下一个
    start = time.time()
    for delay, what in tasks_spec:
        await say_after(delay, what)
    sequential = time.time() - start
    print(f"  逐个 await      : {sequential:.2f}s  ← 3 个 1 秒任务串成 3 秒")

    # 2.2 gather：并发执行，等全部完成
    start = time.time()
    results = await asyncio.gather(*(say_after(d, w) for d, w in tasks_spec))
    gathered = time.time() - start
    print(f"  gather 并发     : {gathered:.2f}s  结果顺序与传入一致: {len(results)}")

    # 2.3 create_task：立即排入调度队列，后续再收结果
    start = time.time()
    created = [asyncio.create_task(say_after(d, w)) for d, w in tasks_spec]
    print(f"  create_task 之后立刻检查: done={any(t.done() for t in created)}"
          f"（任务只是排队，要等事件循环拿到控制权才真正开始）")
    await asyncio.gather(*created)
    print(f"  统一 await 收结果      : {time.time() - start:.2f}s，3 个 1 秒任务只花了 1 秒")

    print(f"  加速比: {sequential / gathered:.1f}x")


# ============================================
# 3. TaskGroup：Python 3.11+ 结构化并发
# ============================================

async def maybe_fail(name, delay, should_fail=False):
    await asyncio.sleep(delay)
    if should_fail:
        raise RuntimeError(f"{name} 失败")
    return name


async def demo_task_group():
    banner("3. TaskGroup 结构化并发 (3.11+)")

    # 任一子任务抛错 -> 取消其余兄弟任务 -> 聚合成 ExceptionGroup 抛出
    start = time.time()
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(maybe_fail("ok-1", 0.2))
            tg.create_task(maybe_fail("boom", 0.1, should_fail=True))
            tg.create_task(maybe_fail("slow", 5))  # 会被取消，不会等 5 秒
    except* RuntimeError as eg:
        for exc in eg.exceptions:
            print(f"  捕获子任务异常: {exc}")
    print(f"  耗时 {time.time() - start:.2f}s：出错后其余任务被立即取消，不会拖到超时")
    print("  对比 gather：gather 默认 return_exceptions=False 时异常直接冒泡，")
    print("             但兄弟任务不会被自动取消，容易泄漏")


# ============================================
# 4. 超时：wait_for 与 timeout 上下文
# ============================================

async def demo_timeout():
    banner("4. 超时控制")

    # 方式1：wait_for 包住单个协程
    try:
        await asyncio.wait_for(say_after(2, "慢任务"), timeout=0.5)
    except asyncio.TimeoutError:
        print("  wait_for: 0.5s 后超时，协程已被取消")

    # 方式2：timeout 上下文包住一段代码（3.11+ 推荐，可覆盖多个 await）
    start = time.time()
    try:
        async with asyncio.timeout(0.5):
            await asyncio.gather(say_after(0.2, "快"), say_after(3, "慢"))
    except TimeoutError:
        print(f"  timeout 上下文: {time.time() - start:.2f}s 后整段被取消")

    # 方式3：给部分任务留容错空间
    results = await asyncio.gather(
        asyncio.wait_for(say_after(0.1, "正常"), timeout=1),
        asyncio.wait_for(say_after(2, "会超时"), timeout=0.3),
        return_exceptions=True,
    )
    print(f"  return_exceptions=True: {[type(r).__name__ if isinstance(r, Exception) else r for r in results]}")


# ============================================
# 5. 取消与清理
# ============================================

async def cleanup_task(name):
    """展示取消时的资源清理"""
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print(f"  {name}: 收到取消信号，执行清理（关连接/回滚/上报）")
        await asyncio.sleep(0.05)  # 清理期间允许少量 await
        raise  # 必须重新抛出，否则取消不生效
    finally:
        print(f"  {name}: finally 一定会执行")


async def demo_cancellation():
    banner("5. 取消机制")

    task = asyncio.create_task(cleanup_task("worker-1"))
    await asyncio.sleep(0.2)
    print(f"  调用 task.cancel()，cancel() 只是请求，任务自己决定收尾")
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("  主协程确认收到 CancelledError")

    # shield：保护关键段落不被取消（例如提交事务、扣款回执）
    committed = {"done": False}

    async def commit():
        await asyncio.sleep(0.3)
        committed["done"] = True

    async def critical():
        await asyncio.shield(commit())

    protected = asyncio.create_task(critical())
    await asyncio.sleep(0.1)
    protected.cancel()
    try:
        await protected
    except asyncio.CancelledError:
        print("  外层任务已被取消，但 shield 保护的内层仍在继续")
    await asyncio.sleep(0.25)
    print(f"  内层最终是否完成: {committed['done']}")

    print("  要点：CancelledError 继承 BaseException，`except Exception` 抓不到它")


# ============================================
# 6. asyncio 版同步原语
# ============================================

async def demo_async_primitives():
    banner("6. asyncio Queue / Semaphore / Event")

    # 6.1 异步队列：没有锁，天然协程安全
    q = asyncio.Queue(maxsize=5)

    async def producer(n):
        for i in range(n):
            await q.put(f"item-{i}")
            await asyncio.sleep(0.01)  # 模拟真实生产速率，让多个消费者有机会分摊
        await q.put(None)

    async def consumer(name):
        got = []
        while True:
            item = await q.get()
            if item is None:
                await q.put(None)  # 转发结束信号给其他消费者
                q.task_done()
                break
            got.append(item)
            q.task_done()
        return f"{name} 处理 {len(got)} 个"

    consumers = [asyncio.create_task(consumer(f"C{i}")) for i in range(2)]
    await asyncio.gather(producer(6), *consumers)
    print(f"  Queue: {[c.result() for c in consumers]}")

    # 6.2 Semaphore：限制并发数，避免打爆下游
    sem = asyncio.Semaphore(3)
    active = peak = 0

    async def limited(i):
        nonlocal active, peak
        async with sem:
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.1)
            active -= 1

    start = time.time()
    await asyncio.gather(*(limited(i) for i in range(12)))
    print(f"  Semaphore(3): 12 个任务耗时 {time.time() - start:.2f}s，实测峰值并发 {peak}")

    # 6.3 Event：等待外部信号（如配置加载完成）
    ready = asyncio.Event()

    async def waiter():
        await ready.wait()
        return "收到通知才开始干活"

    w = asyncio.create_task(waiter())
    await asyncio.sleep(0.1)
    print(f"  Event 未 set 时任务状态: done={w.done()}")
    ready.set()
    print(f"  Event set 后: {await w}")


# ============================================
# 7. 异步生成器
# ============================================

async def range_async(stop, step=1, start=0):
    """异步生成器：产出需要等待的数据源，例如分页接口/大文件行"""
    for i in range(start, stop, step):
        await asyncio.sleep(0.02)
        yield i


async def demo_async_generator():
    banner("7. async generator / async for")

    total = 0
    async for value in range_async(10, 2):
        total += value
    print(f"  async for 累加: {total}")

    # 并发消费多个异步生成器（例如同时抓多个分页源）
    pages = await asyncio.gather(collect(range_async(6)), collect(range_async(12, 2, 6)))
    print(f"  并发收集两个数据源: {pages}")
    print("  要点：async for 是流式消费（内存友好），collect 是整包收集（可并发聚合）")

    # 提前 break 时，建议用 aclosing 保证 generator 的 finally 被执行
    from contextlib import aclosing

    async with aclosing(range_async(100)) as gen:
        async for value in gen:
            if value >= 4:
                break
    print("  aclosing 提前退出：生成器内的清理逻辑被正确执行")


async def collect(agen):
    return [item async for item in agen]


# ============================================
# 8. 与同步世界桥接（关键：不要在协程里写阻塞代码）
# ============================================

def blocking_io(name):
    """同步阻塞函数：模拟旧 SDK / requests / 复杂计算"""
    time.sleep(0.5)
    return f"{name} 同步完成，线程={threading.current_thread().name}"


async def demo_bridge():
    banner("8. 阻塞代码桥接与反例")

    # 8.1 反例：直接调用 time.sleep 会卡住整个事件循环
    start = time.time()
    await asyncio.gather(slow_direct(), slow_direct())
    direct = time.time() - start
    print(f"  协程里用 time.sleep（反例）: {direct:.2f}s  ← 完全没有并发，整条循环被冻住")

    # 8.2 正解1：asyncio.to_thread 丢给线程池
    start = time.time()
    results = await asyncio.gather(*(asyncio.to_thread(blocking_io, f"T{i}") for i in range(4)))
    via_thread = time.time() - start
    print(f"  asyncio.to_thread: {via_thread:.2f}s，{results[0]}")

    # 8.3 正解2：run_in_executor 自定义线程池大小（to_thread 用的是默认 executor）
    from concurrent.futures import ThreadPoolExecutor

    loop = asyncio.get_running_loop()
    start = time.time()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = await asyncio.gather(
            *(loop.run_in_executor(pool, blocking_io, f"E{i}") for i in range(8))
        )
    print(f"  run_in_executor(8 workers): {time.time() - start:.2f}s，共 {len(results)} 个")

    # 8.4 事件循环卡住时，其他协程连计时器都跑不动 —— 用一个心跳验证
    async def heartbeat(stop_after):
        beats = 0
        while time.time() < stop_after:
            beats += 1
            await asyncio.sleep(0.05)
        return beats

    hb_start = time.time()
    hb = asyncio.create_task(heartbeat(hb_start + 1))
    await asyncio.to_thread(time.sleep, 0.5)
    beats = await hb
    print(f"  阻塞函数交给线程后，事件循环照常心跳: 1s 内测得 {beats} 次（≈20 为正常）")


async def slow_direct():
    """故意在协程里用阻塞 sleep，用于对比"""
    time.sleep(0.5)
    return "blocked"


# ============================================
# 9. 常见坑速查
# ============================================

async def demo_pitfalls():
    banner("9. 从 PHP 转过来最容易踩的坑")

    print("""
  1. 忘了 await：得到 coroutine 对象，代码静默不执行（见第 1 节警告）
  2. 在协程里调用阻塞函数（requests / time.sleep / 同步 DB 驱动）→ 全局卡死
     PHP 里每个请求是独立进程，不会互相阻塞；Python 的 loop 是单线程共享的
  3. asyncio 不是多线程：单线程内共享变量不需要加锁，但 CPU 密集会拖垮所有协程
  4. gather(*coros) 会一次性全部调度，10 万个 URL 会瞬间创建 10 万个 Task
     → 配合 Semaphore 或分批提交
  5. 不要在模块级 asyncio.run()，也不要在已有 loop 里再调 run_until_complete
  6. CPU 密集放协程里没收益 → 用第 04 节的进程池，或 loop.run_in_executor(ProcessPoolExecutor)
""")


async def main():
    print("=" * 60)
    print("异步编程基础示例")
    print("=" * 60)

    await demo_coroutine_is_lazy()
    await demo_sequential_vs_concurrent()
    await demo_task_group()
    await demo_timeout()
    await demo_cancellation()
    await demo_async_primitives()
    await demo_async_generator()
    await demo_bridge()
    await demo_pitfalls()

    print("\n" + "=" * 60)
    print("异步编程基础示例完成")
    print("=" * 60)
    print("\n提示：")
    print("  1. async 函数调用只创建协程对象，await / create_task 才真正执行")
    print("  2. 并发的关键是「同时调度、统一等待」，不是多写几个 await")
    print("  3. 3.11+ 优先用 TaskGroup + asyncio.timeout，取消与异常语义更清晰")
    print("  4. 阻塞代码一律走 to_thread / run_in_executor，否则整条循环陪葬")
    print("  5. asyncio 适合海量 I/O 等待，CPU 计算请交给进程池")
    print("\n运行耗时参考：本文件约 10 秒，可加 -O 或按节注释单独跑")


if __name__ == "__main__":
    # debug=True 会打印慢回调与未 await 协程的告警，学习阶段建议打开
    asyncio.run(main(), debug=False)
