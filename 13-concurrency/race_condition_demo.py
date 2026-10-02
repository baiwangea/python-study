#!/usr/bin/env python3
"""
竞态条件（Race Condition）详细演示
帮助理解为什么需要锁
"""

import threading
import time

print("=" * 70)
print("竞态条件演示：为什么会丢失数据？")
print("=" * 70)

# ============================================
# 演示1：可视化竞态条件过程
# ============================================

print("\n【演示1：竞态条件的发生过程】\n")

print("假设 counter = 0，两个线程同时执行 counter += 1")
print()
print("正常情况（有锁保护）：")
print("  时间 | 线程1          | 线程2          | counter")
print("  -----|----------------|----------------|--------")
print("  t0   | 读取: 0        |                | 0")
print("  t1   | 计算: 0+1=1    |                | 0")
print("  t2   | 写入: 1        |                | 1")
print("  t3   |                | 读取: 1        | 1")
print("  t4   |                | 计算: 1+1=2    | 1")
print("  t5   |                | 写入: 2        | 2")
print("  结果: counter = 2 ✓ 正确")
print()

print("竞态条件（无锁保护）：")
print("  时间 | 线程1          | 线程2          | counter")
print("  -----|----------------|----------------|--------")
print("  t0   | 读取: 0        | 读取: 0        | 0")
print("  t1   | 计算: 0+1=1    | 计算: 0+1=1    | 0")
print("  t2   | 写入: 1        |                | 1")
print("  t3   |                | 写入: 1        | 1")
print("  结果: counter = 1 ✗ 错误！应该是2")
print()
print("  → 两个线程都读到0，最后都写入1，丢失了一次增量！")

# ============================================
# 演示2：真实的竞态条件
# ============================================

print("\n" + "=" * 70)
print("【演示2：多次运行观察数据丢失】")
print("=" * 70)

def test_race_condition(num_threads, iterations_per_thread, num_tests=10):
    """测试竞态条件"""
    expected = num_threads * iterations_per_thread
    results = []
    
    print(f"\n配置: {num_threads}个线程 × {iterations_per_thread:,}次 = 期望 {expected:,}")
    print("-" * 70)
    
    for test_num in range(num_tests):
        counter = 0
        
        def increment():
            nonlocal counter
            for _ in range(iterations_per_thread):
                counter += 1
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=increment)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        lost = expected - counter
        loss_pct = (lost / expected) * 100 if expected > 0 else 0
        results.append(counter)
        
        status = "✗ 数据丢失" if lost > 0 else "✓ 正常"
        print(f"测试 {test_num + 1:2d}: {counter:10,} / {expected:,} | "
              f"{status:12s} | 丢失: {lost:8,} ({loss_pct:5.2f}%)")
    
    lost_count = sum(1 for r in results if r != expected)
    print("-" * 70)
    print(f"总结: {lost_count}/{num_tests} 次测试出现数据丢失")
    
    if lost_count == 0:
        print("⚠️  所有测试都正常？这是运气好！让我们增加压力...")
        return False
    else:
        print(f"✓ 成功复现竞态条件！")
        return True

# 逐步增加测试强度
print("\n尝试1: 5个线程 × 50,000次")
if not test_race_condition(5, 50000, 5):
    print("\n尝试2: 10个线程 × 100,000次")
    if not test_race_condition(10, 100000, 5):
        print("\n尝试3: 20个线程 × 100,000次")
        test_race_condition(20, 100000, 5)

# ============================================
# 演示3：使用锁解决问题
# ============================================

print("\n" + "=" * 70)
print("【演示3：使用锁解决竞态条件】")
print("=" * 70)

def test_with_lock(num_threads, iterations_per_thread, num_tests=10):
    """使用锁的版本"""
    expected = num_threads * iterations_per_thread
    
    print(f"\n配置: {num_threads}个线程 × {iterations_per_thread:,}次 = 期望 {expected:,}")
    print("使用 Lock 保护")
    print("-" * 70)
    
    all_correct = True
    
    for test_num in range(num_tests):
        counter = 0
        lock = threading.Lock()
        
        def increment_with_lock():
            nonlocal counter
            for _ in range(iterations_per_thread):
                with lock:
                    counter += 1
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=increment_with_lock)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        lost = expected - counter
        status = "✓ 正确" if lost == 0 else "✗ 错误"
        print(f"测试 {test_num + 1:2d}: {counter:10,} / {expected:,} | {status}")
        
        if lost != 0:
            all_correct = False
    
    print("-" * 70)
    if all_correct:
        print("✓ 所有测试都正确！锁有效地防止了竞态条件")
    else:
        print("✗ 有测试失败（不应该发生）")

test_with_lock(10, 100000, 10)

# ============================================
# 演示4：性能对比
# ============================================

print("\n" + "=" * 70)
print("【演示4：锁的性能开销】")
print("=" * 70)

def benchmark(use_lock=False, num_threads=10, iterations=100000):
    """性能测试"""
    counter = 0
    lock = threading.Lock() if use_lock else None
    
    def increment():
        nonlocal counter
        for _ in range(iterations):
            if use_lock:
                with lock:
                    counter += 1
            else:
                counter += 1
    
    start = time.time()
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=increment)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start
    expected = num_threads * iterations
    
    return elapsed, counter, expected

print("\n配置: 10个线程 × 100,000次\n")

# 不使用锁
time_no_lock, result_no_lock, expected = benchmark(use_lock=False)
lost = expected - result_no_lock
print(f"不使用锁:")
print(f"  耗时: {time_no_lock:.3f}s")
print(f"  结果: {result_no_lock:,} / {expected:,}")
print(f"  丢失: {lost:,} ({(lost/expected*100):.2f}%)")
print(f"  正确性: {'✗ 错误' if lost > 0 else '✓ 正确'}")

print()

# 使用锁
time_with_lock, result_with_lock, expected = benchmark(use_lock=True)
lost = expected - result_with_lock
print(f"使用锁:")
print(f"  耗时: {time_with_lock:.3f}s")
print(f"  结果: {result_with_lock:,} / {expected:,}")
print(f"  丢失: {lost:,}")
print(f"  正确性: {'✓ 正确' if lost == 0 else '✗ 错误'}")

print()
print(f"性能开销: {((time_with_lock/time_no_lock - 1) * 100):.1f}% 变慢")
print("  → 这是为了保证正确性必须付出的代价")

# ============================================
# 总结
# ============================================

print("\n" + "=" * 70)
print("总结")
print("=" * 70)

print("""
1. 为什么有时看不到数据丢失？
   - 竞态条件不是每次都发生
   - 取决于线程调度的时机
   - 线程数越多、操作越频繁，越容易触发
   - 这正是bug难以重现的原因！

2. counter += 1 为什么不安全？
   实际执行步骤:
   ┌──────────────────────────────┐
   │ 1. temp = counter    (读)    │
   │ 2. temp = temp + 1   (算)    │
   │ 3. counter = temp    (写)    │
   └──────────────────────────────┘
   其他线程可能在这三步之间插入执行！

3. 什么时候需要锁？
   ✓ 多个线程访问共享变量
   ✓ 至少有一个线程修改变量
   ✓ 操作不是原子的

4. PHP vs Python:
   PHP (多进程):
   - 每个请求独立进程
   - 不共享内存，无竞态问题
   - 通过Redis/Memcached共享数据
   
   Python (多线程):
   - 线程共享内存
   - 需要手动加锁保护
   - 更灵活但更容易出错

5. 实战建议:
   - 能避免共享状态就避免
   - 必须共享时用锁保护
   - 考虑使用 queue.Queue (线程安全)
   - 复杂场景考虑用进程或异步
""")

print("💡 关键：竞态条件是并发编程中最常见的bug之一！")
print("   即使测试通过，不代表代码正确。")
print("   生产环境中，在高负载下才会暴露问题。")
print()
print("=" * 70)
