#!/usr/bin/env python3
"""
多线程基础示例
演示：线程创建、同步机制（Lock、RLock、Semaphore、Event）
"""

import threading
import time
import random

print("=" * 60)
print("多线程基础示例")
print("=" * 60)

# ============================================
# 1. 基本线程创建
# ============================================

print("\n【1. 基本线程创建】")

def worker(name, delay):
    """工作函数"""
    print(f"  Thread {name} 开始执行")
    time.sleep(delay)
    print(f"  Thread {name} 执行完毕（耗时 {delay}s）")

# 方式1：使用 Thread 类
thread1 = threading.Thread(target=worker, args=("A", 2))
thread2 = threading.Thread(target=worker, args=("B", 1))

thread1.start()
thread2.start()

thread1.join()  # 等待线程完成
thread2.join()

print("  所有线程执行完毕")

# ============================================
# 2. 继承 Thread 类
# ============================================

print("\n【2. 继承 Thread 类】")

class WorkerThread(threading.Thread):
    def __init__(self, name, delay):
        super().__init__()
        self.worker_name = name
        self.delay = delay
    
    def run(self):
        """线程执行的方法"""
        print(f"  Thread {self.worker_name} 开始执行")
        time.sleep(self.delay)
        print(f"  Thread {self.worker_name} 执行完毕")

t1 = WorkerThread("X", 1)
t2 = WorkerThread("Y", 1.5)

t1.start()
t2.start()

t1.join()
t2.join()

# ============================================
# 3. 线程同步 - Lock（锁）
# ============================================

print("\n【3. Lock - 解决竞态条件】")
print("  竞态条件说明：")
print("  - counter += 1 不是原子操作")
print("  - 实际分为：读取 → 计算 → 写入 三步")
print("  - 多线程可能在这三步之间交替执行")
print()

# 3.1 不使用锁的问题 - 增加复现概率
counter_no_lock = 0

def increment_no_lock():
    global counter_no_lock
    for _ in range(100000):
        # 这行代码实际上是三个操作：
        # 1. temp = counter_no_lock (读取)
        # 2. temp = temp + 1       (计算)
        # 3. counter_no_lock = temp (写入)
        counter_no_lock += 1

print("  运行5次测试，观察是否有数据丢失:")
for test_num in range(5):
    counter_no_lock = 0
    threads = []
    for _ in range(10):  # 增加到10个线程
        t = threading.Thread(target=increment_no_lock)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    expected = 1000000  # 10个线程 × 100000
    lost = expected - counter_no_lock
    status = "✗ 丢失" if lost > 0 else "✓ 正常"
    print(f"  测试{test_num + 1}: {counter_no_lock:8d} / {expected} | {status} {lost:6d}")

print("\n  ⚠️  如果所有测试都是1000000，说明运气好没触发竞态")
print("  ⚠️  多运行几次，或者增加线程数，就会看到数据丢失")

# 3.2 使用锁
counter_with_lock = 0
lock = threading.Lock()

def increment_with_lock():
    global counter_with_lock
    for _ in range(100000):
        with lock:  # 自动获取和释放锁
            counter_with_lock += 1

threads = []
for _ in range(5):
    t = threading.Thread(target=increment_with_lock)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"  使用锁的结果: {counter_with_lock} (期望: 500000)")

# ============================================
# 4. RLock（可重入锁）
# ============================================

print("\n【4. RLock - 可重入锁】")

rlock = threading.RLock()

def recursive_function(n):
    """递归函数，需要可重入锁"""
    with rlock:
        if n > 0:
            print(f"  递归层级: {n}")
            recursive_function(n - 1)

thread = threading.Thread(target=recursive_function, args=(3,))
thread.start()
thread.join()

# ============================================
# 5. Semaphore（信号量）
# ============================================

print("\n【5. Semaphore - 限制并发数】")

# 模拟资源池（如数据库连接池）
semaphore = threading.Semaphore(3)  # 最多3个线程同时访问

def access_resource(name):
    """访问受限资源"""
    print(f"  {name} 等待资源...")
    with semaphore:
        print(f"  {name} 获得资源，开始使用")
        time.sleep(random.uniform(0.5, 1.5))
        print(f"  {name} 释放资源")

threads = []
for i in range(8):
    t = threading.Thread(target=access_resource, args=(f"Thread-{i}",))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("  所有线程完成")

# ============================================
# 6. Event（事件）
# ============================================

print("\n【6. Event - 线程间信号】")

event = threading.Event()

def waiter(name):
    """等待事件的线程"""
    print(f"  {name} 等待信号...")
    event.wait()  # 阻塞直到事件被设置
    print(f"  {name} 收到信号，继续执行")

def setter():
    """设置事件的线程"""
    print(f"  Setter 准备中...")
    time.sleep(2)
    print(f"  Setter 发送信号")
    event.set()  # 设置事件，唤醒所有等待的线程

# 创建多个等待线程
threads = []
for i in range(3):
    t = threading.Thread(target=waiter, args=(f"Waiter-{i}",))
    t.start()
    threads.append(t)

# 创建设置线程
setter_thread = threading.Thread(target=setter)
setter_thread.start()

for t in threads:
    t.join()
setter_thread.join()

# ============================================
# 7. 线程本地存储（Thread Local Storage）
# ============================================

print("\n【7. Thread Local Storage】")

thread_local = threading.local()

def process_data(value):
    """处理数据，每个线程独立"""
    thread_local.data = value
    thread_local.name = threading.current_thread().name
    
    print(f"  {thread_local.name} 存储数据: {thread_local.data}")
    time.sleep(0.1)
    
    # 数据仍然是独立的
    print(f"  {thread_local.name} 读取数据: {thread_local.data}")

threads = []
for i in range(5):
    t = threading.Thread(target=process_data, args=(i,), name=f"Thread-{i}")
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# ============================================
# 8. 死锁示例和避免
# ============================================

print("\n【8. 死锁问题】")

lock1 = threading.Lock()
lock2 = threading.Lock()

def task1():
    """任务1：先获取lock1，再获取lock2"""
    print("  Task1: 尝试获取 lock1")
    with lock1:
        print("  Task1: 获得 lock1")
        time.sleep(0.1)
        print("  Task1: 尝试获取 lock2")
        with lock2:
            print("  Task1: 获得 lock2")

def task2():
    """任务2：先获取lock2，再获取lock1 - 可能死锁"""
    print("  Task2: 尝试获取 lock2")
    with lock2:
        print("  Task2: 获得 lock2")
        time.sleep(0.1)
        print("  Task2: 尝试获取 lock1")
        with lock1:
            print("  Task2: 获得 lock1")

# 避免死锁：统一加锁顺序
def task2_fixed():
    """任务2修正：使用相同的加锁顺序"""
    print("  Task2-Fixed: 尝试获取 lock1")
    with lock1:
        print("  Task2-Fixed: 获得 lock1")
        time.sleep(0.1)
        print("  Task2-Fixed: 尝试获取 lock2")
        with lock2:
            print("  Task2-Fixed: 获得 lock2")

print("  避免死锁的方法：统一加锁顺序")
t1 = threading.Thread(target=task1, name="Task1")
t2 = threading.Thread(target=task2_fixed, name="Task2-Fixed")

t1.start()
t2.start()

t1.join()
t2.join()

print("\n" + "=" * 60)
print("多线程基础示例完成")
print("=" * 60)
print("\n提示：")
print("  1. Lock 用于保护共享资源")
print("  2. RLock 支持递归调用")
print("  3. Semaphore 限制并发数")
print("  4. Event 用于线程间信号")
print("  5. 注意避免死锁（统一加锁顺序）")
