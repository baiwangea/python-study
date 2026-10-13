#!/usr/bin/env python3
"""
多进程高级示例
演示：进程池进阶用法、Manager 共享数据、进程同步原语、共享内存、异常与超时处理

对标 00-docs/python_concurrency_guide.md 的「多进程详解」章节。
"""

import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED

# 注意：spawn 模式下每个子进程都会重新 import 本文件，
# 所以模块级只能有定义，不能有 print / 建池 / 启动进程等副作用（否则输出重复、进程爆炸）

# ============================================
# 1. 进程池 - ProcessPoolExecutor 三种提交方式
# ============================================

def slow_square(n):
    """计算平方，模拟耗时任务"""
    time.sleep(0.2)
    return n * n, os.getpid()


def demo_executor_modes():
    print("\n【1. ProcessPoolExecutor 三种用法】")

    numbers = [1, 2, 3, 4, 5, 6]

    # 方式1：map() —— 结果按输入顺序返回，内部惰性产出
    print("\n  方式1: map() 保持输入顺序")
    with ProcessPoolExecutor(max_workers=3) as executor:
        for n, (result, pid) in zip(numbers, executor.map(slow_square, numbers)):
            print(f"    {n}² = {result} (PID: {pid})")

    # 方式2：submit() + as_completed() —— 按完成顺序返回，适合处理长尾任务
    print("\n  方式2: submit() + as_completed() 按完成顺序")
    with ProcessPoolExecutor(max_workers=3) as executor:
        future_to_n = {executor.submit(slow_square, n): n for n in numbers}
        for future in as_completed(future_to_n):
            n = future_to_n[future]
            result, pid = future.result()
            print(f"    ✓ {n}² = {result} (PID: {pid})")

    # 方式3：wait() —— 只关心「谁先完成」，可对未完成任务做超时处理
    print("\n  方式3: wait(FIRST_COMPLETED) 提前拿到第一个结果")
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(slow_square, n) for n in numbers]
        done, pending = wait(futures, return_when=FIRST_COMPLETED)
        print(f"    第一批完成 {len(done)} 个，仍在跑 {len(pending)} 个")
        for future in done:
            print(f"    最早结果: {future.result()[0]}")
        executor.shutdown(wait=True, cancel_futures=True)
        print(f"    剩余 {len(pending)} 个任务已取消或等待结束")


# ============================================
# 2. chunksize：减少进程间往返开销
# ============================================

def cpu_sum(n):
    """CPU 密集任务：累加平方和"""
    return sum(i * i for i in range(n))


def demo_chunksize():
    print("\n【2. chunksize 对吞吐的影响】")

    # 大量轻量任务：默认 chunksize 会让每个任务都走一次 IPC，开销显著
    tasks = list(range(1, 65)) * 8  # 512 个小任务

    with ProcessPoolExecutor(max_workers=4) as executor:
        start = time.time()
        list(executor.map(cpu_sum, tasks, chunksize=1))
        one_by_one = time.time() - start

        start = time.time()
        list(executor.map(cpu_sum, tasks, chunksize=32))
        batched = time.time() - start

    print(f"  chunksize=1  (512 次 IPC): {one_by_one * 1000:.1f} ms")
    print(f"  chunksize=32 (16 次 IPC) : {batched * 1000:.1f} ms")
    print(f"  加速比: {one_by_one / batched:.1f}x")
    print("  结论：任务多且单个很轻时，调大 chunksize 显著降低调度开销")


# ============================================
# 3. initializer：每个 worker 只初始化一次重量级资源
# ============================================

# 进程内全局变量，由 initializer 填充（等价于 PHP-FPM 的 worker 复用连接）
_DB_CONN = None


def init_worker():
    """worker 进程启动时执行一次"""
    global _DB_CONN
    time.sleep(0.5)  # 模拟建立连接
    _DB_CONN = f"conn@{os.getpid()}"


def query_something(key):
    """复用已建立的连接"""
    return f"{key} -> {_DB_CONN}"


def demo_initializer():
    print("\n【3. initializer 复用连接】")

    keys = [f"query-{i}" for i in range(8)]

    # 不用 initializer：每个任务都重新「建连接」
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(query_no_init, keys))
    without = time.time() - start

    # 用 initializer：4 个 worker 各建一次连接
    start = time.time()
    with ProcessPoolExecutor(max_workers=4, initializer=init_worker) as executor:
        results = list(executor.map(query_something, keys))
    with_init = time.time() - start

    print(f"  无 initializer: {without:.2f}s（每个任务重建连接）")
    print(f"  有 initializer: {with_init:.2f}s（每个 worker 只建一次）")
    print(f"  连接分布: {sorted(set(r.split(' -> ')[1] for r in results))}")


def query_no_init(key):
    """没有 initializer 时，任务内部自建连接"""
    time.sleep(0.5)
    return f"{key} -> conn@{os.getpid()}#fresh"


# ============================================
# 4. Manager：跨进程共享 Python 对象
# ============================================

def manager_writer(shared_dict, shared_list, lock, name, count):
    """向 Manager 对象写入数据"""
    for i in range(count):
        with lock:  # Manager 的容器本身不是原子复合操作，写入需加锁
            shared_dict[name] = shared_dict.get(name, 0) + 1
            shared_list.append(f"{name}-{i}")
        time.sleep(0.02)


def demo_manager():
    print("\n【4. Manager 共享 dict / list / Namespace】")

    # Manager 是一个独立的服务进程，所有操作走 IPC，比共享内存慢
    with multiprocessing.Manager() as manager:
        shared_dict = manager.dict()
        shared_list = manager.list()
        lock = manager.Lock()
        namespace = manager.Namespace()
        namespace.status = "running"
        namespace.progress = 0

        processes = [
            multiprocessing.Process(
                target=manager_writer, args=(shared_dict, shared_list, lock, f"P{i}", 5)
            )
            for i in range(4)
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        namespace.progress = 100
        print(f"  共享 dict: {dict(shared_dict)}")
        print(f"  共享 list 长度: {len(shared_list)}（期望 4×5=20）")
        print(f"  Namespace: status={namespace.status}, progress={namespace.progress}")
        print("  注意：Manager 对象只在 manager 存活期间可用，务必用 with 包裹")


# ============================================
# 5. 进程同步原语：Barrier 与 Semaphore
# ============================================

def barrier_worker(barrier, name):
    """所有进程到齐后才一起继续"""
    print(f"  {name} 到达检查点")
    barrier.wait()  # 阻塞直到 parties 个进程全部到达
    print(f"  {name} 放行，开始下一阶段")


def sem_worker(semaphore, name):
    """信号量限制同时进入的数量"""
    with semaphore:
        print(f"  {name} 获取令牌 (可访问的 worker 受限)")
        time.sleep(0.5)
    # 离开 with 时自动释放令牌


def demo_sync_primitives():
    print("\n【5. Barrier 同步栅栏 / Semaphore 限流】")

    print("\n  Barrier: 3 个进程必须同时到齐")
    barrier = multiprocessing.Barrier(parties=3)
    processes = [
        multiprocessing.Process(target=barrier_worker, args=(barrier, f"W{i}"))
        for i in range(3)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print("\n  Semaphore(2): 8 个进程最多 2 个同时执行")
    semaphore = multiprocessing.Semaphore(2)
    processes = [
        multiprocessing.Process(target=sem_worker, args=(semaphore, f"S{i}"))
        for i in range(8)
    ]
    start = time.time()
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print(f"  耗时 {time.time() - start:.2f}s ≈ 8/2 × 0.5s，说明限流生效")


# ============================================
# 6. shared_memory：零拷贝共享大块数据
# ============================================

def fill_shared_block(block_name, name, offset, length):
    """子进程直接写入父进程创建的共享内存块"""
    from multiprocessing import shared_memory

    existing = shared_memory.SharedMemory(name=block_name)
    try:
        # memoryview 切片赋值要求左右长度严格相等，否则 ValueError
        existing.buf[offset:offset + length] = f"[{name}]".encode().ljust(length, b".")
    finally:
        existing.close()  # 只关闭本进程的映射，不销毁内存块


def demo_shared_memory():
    print("\n【6. shared_memory 零拷贝大数据】")

    from multiprocessing import shared_memory

    size = 64
    # 父进程创建一块共享内存，子进程按名字附着，不复制数据
    block = shared_memory.SharedMemory(create=True, size=size)
    try:
        prefix = b"parent-init."
        block.buf[:len(prefix)] = prefix
        print(f"  创建共享块 {block.name}, {size} 字节")

        half = size // 2
        processes = [
            multiprocessing.Process(
                target=fill_shared_block, args=(block.name, f"W{i}", i * half, half)
            )
            for i in range(2)
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        print(f"  父进程读到: {bytes(block.buf[:size]).decode()}")
    finally:
        block.close()
        block.unlink()  # 必须 unlink，否则共享内存泄漏在 /dev/shm

    print("  对比：Value/Array 适合小标量与定长数组，shared_memory 适合 MB 级缓冲")


# ============================================
# 7. 异常传播与超时处理
# ============================================

def broken_task(n):
    """必定抛异常的任务"""
    if n % 2 == 0:
        raise ValueError(f"拒绝处理偶数: {n}")
    return n


def hanging_task(seconds):
    """模拟卡死的任务"""
    time.sleep(seconds)
    return "done"


def demo_error_handling():
    print("\n【7. 异常传播与超时】")

    # 7.1 异常在子进程抛出，父进程 result() 时重新抛到调用栈
    print("\n  7.1 异常传播")
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(broken_task, n) for n in range(1, 5)]
        for future in as_completed(futures):
            try:
                print(f"    成功: {future.result()}")
            except ValueError as e:
                # 不捕获会让整个进程池退出，生产环境应当记录后继续
                print(f"    捕获异常: {e}")

    # 7.2 任务级超时：wait + timeout，超时的任务可以取消或降级
    print("\n  7.2 超时控制")
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(hanging_task, delay): delay
            for delay in (0.2, 3.0)
        }
        start = time.time()
        done, pending = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
        print(f"    1s 内完成 {len(done)} 个: {[futures[f] for f in done]}")
        print(f"    超时未完成 {len(pending)} 个: {[futures[f] for f in pending]}")

        # 尚未开始运行的任务可以取消；已经在跑的取消不了
        cancelled = [f.cancel() for f in pending]
        print(f"    cancel() 结果: {cancelled}（已开始执行的任务无法取消）")
        executor.shutdown(wait=False, cancel_futures=True)
        print(f"    耗时 {time.time() - start:.2f}s")

    # 7.3 子进程硬退出（被信号杀掉 / 调用 os._exit）会污染整个进程池
    print("\n  7.3 worker 崩溃后进程池不可用")
    from concurrent.futures.process import BrokenProcessPool

    executor = ProcessPoolExecutor(max_workers=2)
    try:
        executor.submit(os._exit, 1).result()
    except BaseException as e:
        print(f"    第一个任务: {type(e).__name__} -> {str(e)[:60]}")
    try:
        executor.submit(slow_square, 9).result()
        print("    进程池仍能处理后续任务")
    except BrokenProcessPool as e:
        print(f"    后续任务: {type(e).__name__} -> {str(e)[:60]}")
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    # 唯一恢复手段：重建进程池
    recovered = ProcessPoolExecutor(max_workers=2)
    print(f"    重建进程池后可继续: 9² = {recovered.submit(slow_square, 9).result()[0]}")
    recovered.shutdown()
    print("    生产实践：捕获 BrokenProcessPool → 重建池 → 重试任务，并给任务本身加超时")


# ============================================
# 8. 启动方式：fork / spawn / forkserver
# ============================================

def get_start_info():
    """在子进程中返回启动方式与 PID"""
    return multiprocessing.get_start_method(), os.getpid()


def demo_start_methods():
    print("\n【8. 启动方式对比】")

    available = multiprocessing.get_all_start_methods()
    current = multiprocessing.get_start_method()
    print(f"  当前系统支持: {available}")
    print(f"  默认使用: {current}")

    with multiprocessing.Pool(processes=1) as pool:
        child_method, child_pid = pool.apply(get_start_info)
    print(f"  子进程内确认: start_method={child_method}, PID={child_pid} (主进程 {os.getpid()})")

    print("""
  fork      : 直接复制父进程内存，最快；但多线程 + fork 容易死锁（macOS 已不推荐）
  spawn     : 全新解释器进程，安全但慢；要求任务函数可 pickle，必须有 __main__ 保护
  forkserver: 折中方案，预启动一个干净的 fork 服务进程

  PHP 对照：PHP-FPM 是「常驻进程 + fork」模型，spawn 的开销更接近每次重新 php-cli 启动""")


# ============================================
# 9. 可 pickle 的坑：哪些任务发不进子进程
# ============================================

def demo_pickle_limits():
    print("\n【9. pickle 限制（spawn 模式必看）】")

    def local_lambda(n):
        return n

    with ProcessPoolExecutor(max_workers=1) as executor:
        # 局部函数 / lambda / 连接对象 / 打开的文件句柄都无法 pickle
        try:
            executor.submit(local_lambda, 1).result()
        except Exception as e:
            print(f"  局部函数: {type(e).__name__} -> {str(e)[:60]}")

        try:
            executor.submit(lambda n: n, 1).result()
        except Exception as e:
            print(f"  lambda  : {type(e).__name__} -> {str(e)[:60]}")

    print("  解决：任务函数与参数都定义在模块顶层，或使用 multiprocessing 的可 pickle 类型")


if __name__ == "__main__":
    print("=" * 60)
    print("多进程高级示例")
    print("=" * 60)

    demo_executor_modes()
    demo_chunksize()
    demo_initializer()
    demo_manager()
    demo_sync_primitives()
    demo_shared_memory()
    demo_error_handling()
    demo_start_methods()
    demo_pickle_limits()

    print("\n" + "=" * 60)
    print("多进程高级示例完成")
    print("=" * 60)
    print("\n提示：")
    print("  1. chunksize 决定 IPC 次数，任务越轻越要批量化")
    print("  2. initializer 是复用数据库/HTTP 连接的标准做法")
    print("  3. Manager 方便但走 IPC，大数据用 shared_memory / Value / Array")
    print("  4. 子进程异常只在 result() 时抛出，必须逐个捕获否则整体崩")
    print("  5. 已开始执行的任务无法 cancel，超时靠 wait(timeout=) + 任务内部超时")
    print("  6. macOS/Windows 用 spawn：任务函数必须顶层定义 + __main__ 保护")
    print("\n调试建议：")
    print("  python3 04_multiprocessing_advanced.py 2>&1 | tee /tmp/mp.log")
