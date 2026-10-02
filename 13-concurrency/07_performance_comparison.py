#!/usr/bin/env python3
"""
性能对比：多线程 vs 多进程 vs 异步
通过实际测试对比三种并发模型的性能
"""

import time
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

print("=" * 70)
print("Python 并发编程性能对比")
print("=" * 70)

# ============================================
# 测试1：I/O密集型 - 网络请求
# ============================================

print("\n【测试1：I/O密集型 - 模拟网络请求】")
print("任务：执行20次休眠操作（模拟网络延迟）")

def io_task(n):
    """模拟I/O操作（网络请求）"""
    time.sleep(0.1)  # 模拟网络延迟
    return f"Result-{n}"

# 1.1 串行执行
def test_io_serial(count=20):
    """串行执行I/O任务"""
    start = time.time()
    results = []
    for i in range(count):
        results.append(io_task(i))
    elapsed = time.time() - start
    return elapsed, len(results)

# 1.2 多线程
def test_io_threading(count=20, workers=5):
    """多线程执行I/O任务"""
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(io_task, range(count)))
    elapsed = time.time() - start
    return elapsed, len(results)

# 1.3 多进程
def test_io_multiprocessing(count=20, workers=5):
    """多进程执行I/O任务"""
    start = time.time()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(io_task, range(count)))
    elapsed = time.time() - start
    return elapsed, len(results)

# 1.4 异步
async def async_io_task(n):
    """异步I/O任务"""
    await asyncio.sleep(0.1)
    return f"Result-{n}"

async def test_io_async(count=20):
    """异步执行I/O任务"""
    start = time.time()
    tasks = [async_io_task(i) for i in range(count)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    return elapsed, len(results)

# 运行I/O测试
if __name__ == '__main__':
    print("\n串行执行:")
    elapsed, count = test_io_serial()
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    baseline = elapsed
    
    print("\n多线程 (5 workers):")
    elapsed, count = test_io_threading(workers=5)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")
    
    print("\n多进程 (5 workers):")
    elapsed, count = test_io_multiprocessing(workers=5)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")
    
    print("\n异步:")
    elapsed, count = asyncio.run(test_io_async())
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")

# ============================================
# 测试2：CPU密集型 - 计算任务
# ============================================

print("\n\n【测试2：CPU密集型 - 数值计算】")
print("任务：计算大量数字的平方和")

def cpu_task(n):
    """CPU密集型任务"""
    total = 0
    for i in range(n):
        total += i ** 2
    return total

# 2.1 串行执行
def test_cpu_serial(numbers):
    """串行执行CPU任务"""
    start = time.time()
    results = [cpu_task(n) for n in numbers]
    elapsed = time.time() - start
    return elapsed, len(results)

# 2.2 多线程
def test_cpu_threading(numbers, workers=4):
    """多线程执行CPU任务"""
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(cpu_task, numbers))
    elapsed = time.time() - start
    return elapsed, len(results)

# 2.3 多进程
def test_cpu_multiprocessing(numbers, workers=4):
    """多进程执行CPU任务"""
    start = time.time()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(cpu_task, numbers))
    elapsed = time.time() - start
    return elapsed, len(results)

# 运行CPU测试
if __name__ == '__main__':
    # 测试数据（调整大小以适应你的机器）
    test_numbers = [5000000, 6000000, 7000000, 8000000]
    cpu_count = multiprocessing.cpu_count()
    
    print(f"\n系统CPU核心数: {cpu_count}")
    
    print("\n串行执行:")
    elapsed, count = test_cpu_serial(test_numbers)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    baseline = elapsed
    
    print(f"\n多线程 ({cpu_count} workers):")
    elapsed, count = test_cpu_threading(test_numbers, workers=cpu_count)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")
    print(f"  ⚠️  受GIL限制，几乎没有加速")
    
    print(f"\n多进程 ({cpu_count} workers):")
    elapsed, count = test_cpu_multiprocessing(test_numbers, workers=cpu_count)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")
    print(f"  ✓ 真正的并行计算")

# ============================================
# 测试3：混合任务
# ============================================

print("\n\n【测试3：混合任务 - I/O + CPU】")
print("任务：下载数据后进行计算")

def mixed_task(n):
    """混合任务：I/O + CPU"""
    # I/O部分
    time.sleep(0.05)
    # CPU部分
    result = 0
    for i in range(1000000):
        result += i ** 2
    return result

# 3.1 串行
def test_mixed_serial(count=10):
    start = time.time()
    results = [mixed_task(i) for i in range(count)]
    elapsed = time.time() - start
    return elapsed, len(results)

# 3.2 多线程
def test_mixed_threading(count=10, workers=4):
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(mixed_task, range(count)))
    elapsed = time.time() - start
    return elapsed, len(results)

# 3.3 多进程
def test_mixed_multiprocessing(count=10, workers=4):
    start = time.time()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(mixed_task, range(count)))
    elapsed = time.time() - start
    return elapsed, len(results)

if __name__ == '__main__':
    print("\n串行执行:")
    elapsed, count = test_mixed_serial()
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    baseline = elapsed
    
    print("\n多线程 (4 workers):")
    elapsed, count = test_mixed_threading(workers=4)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")
    
    print("\n多进程 (4 workers):")
    elapsed, count = test_mixed_multiprocessing(workers=4)
    print(f"  耗时: {elapsed:.2f}s, 完成: {count} 任务")
    print(f"  加速比: {baseline/elapsed:.2f}x")

# ============================================
# 性能总结
# ============================================

if __name__ == '__main__':
    print("\n\n" + "=" * 70)
    print("性能测试总结")
    print("=" * 70)
    
    print("""
┌────────────────┬──────────────┬──────────────┬──────────────┐
│ 任务类型       │ 串行         │ 多线程       │ 多进程       │ 异步        │
├────────────────┼──────────────┼──────────────┼──────────────┤
│ I/O密集型      │ ⭐ (最慢)     │ ⭐⭐⭐⭐      │ ⭐⭐⭐       │ ⭐⭐⭐⭐⭐  │
│ (网络、文件)   │ 基准         │ 显著加速     │ 有加速       │ 最快        │
├────────────────┼──────────────┼──────────────┼──────────────┤
│ CPU密集型      │ ⭐⭐         │ ⭐⭐ (受GIL)  │ ⭐⭐⭐⭐⭐   │ ⭐⭐ (不适用)│
│ (计算、处理)   │ 较慢         │ 几乎无加速   │ 最佳选择     │ 不适合      │
├────────────────┼──────────────┼──────────────┼──────────────┤
│ 混合任务       │ ⭐           │ ⭐⭐⭐       │ ⭐⭐⭐⭐     │ ⭐⭐⭐      │
│ (I/O + CPU)    │ 最慢         │ 中等加速     │ 较好加速     │ 看I/O比例   │
└────────────────┴──────────────┴──────────────┴──────────────┘

关键结论：

1. I/O密集型任务:
   - ✅ 异步 > 多线程 > 多进程 > 串行
   - ✅ 异步在高并发下性能最佳
   - ✅ 多线程是I/O密集型的经典解决方案

2. CPU密集型任务:
   - ✅ 多进程 > 串行 ≈ 多线程
   - ❌ 多线程受GIL限制，几乎无加速
   - ✅ 多进程可以充分利用多核CPU

3. 内存和开销:
   - 异步：内存占用最小，启动开销最小
   - 多线程：共享内存，开销较小
   - 多进程：独立内存，开销最大

4. 选择建议:
   - 网络爬虫 → 异步 (asyncio + aiohttp)
   - Web服务 → 异步 (FastAPI, aiohttp)
   - 图像处理 → 多进程
   - 数据分析 → 多进程
   - 文件I/O → 多线程
   - 数据库操作 → 多线程

5. PHP对比:
   - PHP主要使用多进程（PHP-FPM）
   - Python三种方式都很成熟
   - Python的异步模型比PHP更先进
    """)

    print("\n💡 实战建议:")
    print("  1. 优先考虑异步，除非需要CPU密集型计算")
    print("  2. CPU密集型必须用多进程")
    print("  3. 多线程适合中等并发的I/O操作")
    print("  4. 先串行实现，性能瓶颈时再并发")
    print("  5. 测试对比，选择最适合的方案")
    
    print("\n" + "=" * 70)
