# Python 并发编程完全指南：多进程 vs 多线程 vs 异步

## 目录
- [核心概念](#核心概念)
- [架构对比](#架构对比)
- [多线程详解](#多线程详解)
- [多进程详解](#多进程详解)
- [异步编程详解](#异步编程详解)
- [性能对比](#性能对比)
- [选择指南](#选择指南)
- [实战案例](#实战案例)

---

## 核心概念

### 1. 并发 vs 并行

```
并发（Concurrency）：交替执行，看起来同时进行
┌─────────────────────────────────────┐
│  Time  →                            │
│  Task1: ████░░░░████░░░░████        │
│  Task2: ░░░░████░░░░████░░░░████    │
│  单核CPU上通过时间片轮转             │
└─────────────────────────────────────┘

并行（Parallelism）：真正同时执行
┌─────────────────────────────────────┐
│  Time  →                            │
│  CPU1:  ████████████████████        │
│  CPU2:  ████████████████████        │
│  多核CPU上真正同时执行               │
└─────────────────────────────────────┘
```

### 2. 三种并发模型对比

| 特性 | 多线程 Threading | 多进程 Multiprocessing | 异步 Asyncio |
|------|-----------------|----------------------|--------------|
| **并发类型** | 并发（受GIL限制） | 并行（真正多核） | 并发（单线程） |
| **适用场景** | I/O密集型 | CPU密集型 | I/O密集型 |
| **内存占用** | 低（共享内存） | 高（独立内存） | 极低 |
| **启动开销** | 小 | 大 | 极小 |
| **通信方式** | 共享变量 | 进程间通信(IPC) | 协程切换 |
| **数据共享** | 简单（需要锁） | 复杂（需要序列化） | 简单 |
| **GIL影响** | ❌ 受限 | ✅ 不受限 | ✅ 不受限 |
| **典型用途** | 网络请求、文件读写 | 图像处理、数据计算 | Web服务、爬虫 |

### 3. GIL（全局解释器锁）详解

```python
# PHP 没有 GIL，Python CPython 有 GIL

GIL 的影响：
┌─────────────────────────────────────────────┐
│  没有 GIL（如 PHP、Java）                    │
│  Thread1: ████████████████ (真正并行)        │
│  Thread2: ████████████████                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  有 GIL（Python CPython）                    │
│  Thread1: ████░░░░████░░░░████ (交替执行)   │
│  Thread2: ░░░░████░░░░████░░░░████          │
│  同一时刻只有一个线程执行 Python 字节码      │
└─────────────────────────────────────────────┘

结论：
✅ I/O 操作时会释放 GIL，多线程有效
❌ CPU 密集计算不释放 GIL，多线程无效
✅ 多进程不受 GIL 限制，可以真正并行
```

---

## 架构对比

### 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Python 并发编程架构                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼─────┐ ┌────▼──────┐ ┌───▼──────────┐
        │  多线程      │ │ 多进程     │ │  异步编程    │
        │ Threading   │ │Multiproc   │ │  Asyncio    │
        └───────┬─────┘ └────┬──────┘ └───┬──────────┘
                │             │             │
    ┌───────────┼─────┐      │      ┌──────┼──────────┐
    │           │     │      │      │      │          │
┌───▼───┐  ┌───▼──┐ ┌▼──┐  ┌▼──┐  ┌▼────┐ ┌▼──────┐ ┌▼─────┐
│Thread1│  │Thread│ │共享│  │进程│  │Event│ │Corout │ │Task  │
│       │  │Pool  │ │变量│  │Pool│  │Loop │ │ine   │ │Queue │
└───────┘  └──────┘ └───┘  └───┘  └─────┘ └───────┘ └──────┘
```

### 2. 内存模型对比

```
多线程内存模型：
┌────────────────────────────────────────┐
│         进程内存空间                    │
│  ┌────────────────────────────────┐   │
│  │  共享内存区域                   │   │
│  │  - 全局变量                     │   │
│  │  - 堆内存                       │   │
│  │  - 代码段                       │   │
│  └────────────────────────────────┘   │
│                                        │
│  ┌──────────┐  ┌──────────┐          │
│  │ Thread 1 │  │ Thread 2 │          │
│  │  Stack   │  │  Stack   │  独立栈  │
│  └──────────┘  └──────────┘          │
└────────────────────────────────────────┘

多进程内存模型：
┌──────────────┐  ┌──────────────┐
│  进程 1       │  │  进程 2       │
│ ┌──────────┐ │  │ ┌──────────┐ │
│ │全局变量  │ │  │ │全局变量  │ │  完全隔离
│ │堆内存    │ │  │ │堆内存    │ │
│ │代码段    │ │  │ │代码段    │ │
│ │栈        │ │  │ │栈        │ │
│ └──────────┘ │  │ └──────────┘ │
└──────────────┘  └──────────────┘
     │                    │
     └────────┬───────────┘
          IPC 通信
       (管道、队列、共享内存)
```

---

## 多线程详解

### 1. 基础使用

```python
import threading
import time

# 方式1：直接创建线程
def worker(name, delay):
    """工作函数"""
    print(f"Thread {name} starting")
    time.sleep(delay)
    print(f"Thread {name} finishing")

# 创建并启动线程
thread1 = threading.Thread(target=worker, args=("A", 2))
thread2 = threading.Thread(target=worker, args=("B", 1))

thread1.start()
thread2.start()

# 等待线程完成
thread1.join()
thread2.join()

print("All threads completed")

# 方式2：继承 Thread 类
class WorkerThread(threading.Thread):
    def __init__(self, name, delay):
        super().__init__()
        self.name = name
        self.delay = delay
    
    def run(self):
        """线程执行的方法"""
        print(f"Thread {self.name} starting")
        time.sleep(self.delay)
        print(f"Thread {self.name} finishing")

# 使用自定义线程类
t1 = WorkerThread("X", 1)
t2 = WorkerThread("Y", 2)

t1.start()
t2.start()

t1.join()
t2.join()
```

### 2. 线程同步：锁（Lock）

```python
import threading

# 不使用锁的问题示例
counter = 0

def increment_without_lock():
    """不安全的计数器"""
    global counter
    for _ in range(100000):
        counter += 1  # 非原子操作，可能出现竞态条件

threads = []
for _ in range(10):
    t = threading.Thread(target=increment_without_lock)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"Counter without lock: {counter}")  # 结果可能不是 1000000

# ============================================
# 使用锁保证线程安全
# ============================================

counter = 0
lock = threading.Lock()

def increment_with_lock():
    """线程安全的计数器"""
    global counter
    for _ in range(100000):
        with lock:  # 使用 with 语句自动获取和释放锁
            counter += 1

threads = []
for _ in range(10):
    t = threading.Thread(target=increment_with_lock)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"Counter with lock: {counter}")  # 总是 1000000

# 锁的手动使用方式
def manual_lock_usage():
    lock.acquire()
    try:
        # 临界区代码
        counter += 1
    finally:
        lock.release()
```

### 3. 线程同步：RLock（可重入锁）

```python
import threading

lock = threading.RLock()  # 可重入锁

def recursive_function(n):
    """递归函数，同一线程可以多次获取锁"""
    with lock:
        if n > 0:
            print(f"Level {n}")
            recursive_function(n - 1)

# 普通 Lock 会死锁，RLock 不会
thread = threading.Thread(target=recursive_function, args=(3,))
thread.start()
thread.join()
```

### 4. 线程同步：Semaphore（信号量）

```python
import threading
import time

# 限制同时访问资源的线程数量
semaphore = threading.Semaphore(3)  # 最多3个线程同时执行

def access_resource(name):
    """访问受限资源"""
    print(f"{name} waiting for semaphore...")
    with semaphore:
        print(f"{name} acquired semaphore")
        time.sleep(2)  # 模拟资源使用
        print(f"{name} releasing semaphore")

# 创建10个线程，但最多3个同时执行
threads = []
for i in range(10):
    t = threading.Thread(target=access_resource, args=(f"Thread-{i}",))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### 5. 线程通信：Queue（队列）

```python
import threading
import queue
import time

# 创建队列
task_queue = queue.Queue()
result_queue = queue.Queue()

def producer():
    """生产者线程"""
    for i in range(10):
        task = f"Task-{i}"
        task_queue.put(task)
        print(f"Produced: {task}")
        time.sleep(0.1)
    
    # 发送结束信号
    task_queue.put(None)

def consumer(name):
    """消费者线程"""
    while True:
        task = task_queue.get()
        if task is None:
            task_queue.put(None)  # 传递结束信号给其他消费者
            break
        
        # 处理任务
        result = f"{name} processed {task}"
        print(result)
        result_queue.put(result)
        time.sleep(0.2)
        
        task_queue.task_done()

# 启动生产者
prod = threading.Thread(target=producer)
prod.start()

# 启动多个消费者
consumers = []
for i in range(3):
    cons = threading.Thread(target=consumer, args=(f"Consumer-{i}",))
    cons.start()
    consumers.append(cons)

# 等待完成
prod.join()
for cons in consumers:
    cons.join()

print("\nAll results:")
while not result_queue.empty():
    print(result_queue.get())
```

### 6. 线程池（ThreadPoolExecutor）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_file(url):
    """模拟文件下载"""
    print(f"Downloading {url}...")
    time.sleep(2)
    return f"Content from {url}"

# 方式1：使用 map()
urls = [f"http://example.com/file{i}" for i in range(5)]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(download_file, urls)
    
    for result in results:
        print(result)

# 方式2：使用 submit() 和 as_completed()
with ThreadPoolExecutor(max_workers=3) as executor:
    # 提交任务
    future_to_url = {
        executor.submit(download_file, url): url 
        for url in urls
    }
    
    # 处理完成的任务（按完成顺序）
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            print(f"✓ {url}: {result}")
        except Exception as e:
            print(f"✗ {url}: {e}")
```

### 7. 线程本地存储（Thread Local Storage）

```python
import threading

# 每个线程都有自己独立的数据副本
thread_local = threading.local()

def process_data(value):
    """处理数据"""
    # 每个线程独立的数据
    thread_local.data = value
    print(f"{threading.current_thread().name}: {thread_local.data}")
    
    # 其他线程无法访问这个值
    time.sleep(0.1)
    print(f"{threading.current_thread().name} still has: {thread_local.data}")

threads = []
for i in range(5):
    t = threading.Thread(target=process_data, args=(i,), name=f"Thread-{i}")
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

---

## 多进程详解

### 1. 基础使用

```python
import multiprocessing
import time
import os

# 方式1：直接创建进程
def worker(name, delay):
    """工作函数"""
    print(f"Process {name} (PID: {os.getpid()}) starting")
    time.sleep(delay)
    print(f"Process {name} (PID: {os.getpid()}) finishing")

if __name__ == '__main__':
    # 必须在 if __name__ == '__main__' 中创建进程
    p1 = multiprocessing.Process(target=worker, args=("A", 2))
    p2 = multiprocessing.Process(target=worker, args=("B", 1))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print("All processes completed")

# 方式2：继承 Process 类
class WorkerProcess(multiprocessing.Process):
    def __init__(self, name, delay):
        super().__init__()
        self.worker_name = name
        self.delay = delay
    
    def run(self):
        """进程执行的方法"""
        print(f"Process {self.worker_name} (PID: {os.getpid()}) starting")
        time.sleep(self.delay)
        print(f"Process {self.worker_name} finishing")

if __name__ == '__main__':
    p1 = WorkerProcess("X", 1)
    p2 = WorkerProcess("Y", 2)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

### 2. 进程间通信：Queue

```python
import multiprocessing
import time

def producer(queue):
    """生产者进程"""
    for i in range(5):
        item = f"Item-{i}"
        queue.put(item)
        print(f"Produced: {item}")
        time.sleep(0.5)
    
    queue.put(None)  # 结束信号

def consumer(queue):
    """消费者进程"""
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        time.sleep(1)

if __name__ == '__main__':
    # 创建进程间队列
    queue = multiprocessing.Queue()
    
    # 创建进程
    prod = multiprocessing.Process(target=producer, args=(queue,))
    cons = multiprocessing.Process(target=consumer, args=(queue,))
    
    prod.start()
    cons.start()
    
    prod.join()
    cons.join()
```

### 3. 进程间通信：Pipe

```python
import multiprocessing

def sender(conn):
    """发送数据的进程"""
    messages = ['hello', 'world', 'from', 'pipe']
    for msg in messages:
        conn.send(msg)
        print(f"Sent: {msg}")
    conn.close()

def receiver(conn):
    """接收数据的进程"""
    while True:
        try:
            msg = conn.recv()
            print(f"Received: {msg}")
        except EOFError:
            break

if __name__ == '__main__':
    # 创建管道
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # 创建进程
    p1 = multiprocessing.Process(target=sender, args=(parent_conn,))
    p2 = multiprocessing.Process(target=receiver, args=(child_conn,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

### 4. 共享内存：Value 和 Array

```python
import multiprocessing
import time

def increment_shared_value(shared_val, lock):
    """增加共享值"""
    for _ in range(10000):
        with lock:
            shared_val.value += 1

def modify_shared_array(shared_arr, lock, index):
    """修改共享数组"""
    with lock:
        shared_arr[index] = multiprocessing.current_process().pid

if __name__ == '__main__':
    # 共享值（需要类型代码）
    # 'i' = 整数, 'd' = 浮点数
    shared_value = multiprocessing.Value('i', 0)
    
    # 共享数组
    shared_array = multiprocessing.Array('i', 10)
    
    # 创建锁
    lock = multiprocessing.Lock()
    
    # 创建进程
    processes = []
    for i in range(5):
        p = multiprocessing.Process(
            target=increment_shared_value,
            args=(shared_value, lock)
        )
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"Shared value: {shared_value.value}")  # 50000
    
    # 测试共享数组
    processes = []
    for i in range(10):
        p = multiprocessing.Process(
            target=modify_shared_array,
            args=(shared_array, lock, i)
        )
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"Shared array: {list(shared_array)}")
```

### 5. 进程池（ProcessPoolExecutor）

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_intensive_task(n):
    """CPU 密集型任务"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

if __name__ == '__main__':
    numbers = [10000000, 20000000, 30000000, 40000000]
    
    # 串行执行（用于对比）
    start = time.time()
    results_serial = [cpu_intensive_task(n) for n in numbers]
    serial_time = time.time() - start
    print(f"Serial execution: {serial_time:.2f}s")
    
    # 并行执行
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results_parallel = list(executor.map(cpu_intensive_task, numbers))
    parallel_time = time.time() - start
    print(f"Parallel execution: {parallel_time:.2f}s")
    print(f"Speedup: {serial_time / parallel_time:.2f}x")
```

### 6. Manager：高级共享数据

```python
import multiprocessing

def modify_shared_dict(shared_dict, key, value):
    """修改共享字典"""
    shared_dict[key] = value
    print(f"Set {key} = {value}")

def modify_shared_list(shared_list, value):
    """修改共享列表"""
    shared_list.append(value)
    print(f"Appended {value}")

if __name__ == '__main__':
    # 创建 Manager
    manager = multiprocessing.Manager()
    
    # 创建共享数据结构
    shared_dict = manager.dict()
    shared_list = manager.list()
    
    # 创建进程
    processes = []
    
    for i in range(5):
        p1 = multiprocessing.Process(
            target=modify_shared_dict,
            args=(shared_dict, f'key{i}', i)
        )
        p2 = multiprocessing.Process(
            target=modify_shared_list,
            args=(shared_list, i)
        )
        processes.extend([p1, p2])
        p1.start()
        p2.start()
    
    for p in processes:
        p.join()
    
    print(f"\nShared dict: {dict(shared_dict)}")
    print(f"Shared list: {list(shared_list)}")
```

---

## 异步编程详解

### 1. 基础语法

```python
import asyncio
import time

# 同步版本
def sync_task(name, delay):
    """同步任务"""
    print(f"{name} starting")
    time.sleep(delay)
    print(f"{name} finished")
    return f"Result from {name}"

# 异步版本
async def async_task(name, delay):
    """异步任务"""
    print(f"{name} starting")
    await asyncio.sleep(delay)  # 注意：使用 asyncio.sleep
    print(f"{name} finished")
    return f"Result from {name}"

# 运行异步任务
async def main():
    # 串行执行
    result1 = await async_task("Task1", 2)
    result2 = await async_task("Task2", 1)
    
    # 并发执行
    results = await asyncio.gather(
        async_task("Task3", 2),
        async_task("Task4", 1),
        async_task("Task5", 1.5)
    )
    print(results)

# 运行
asyncio.run(main())
```

### 2. 异步HTTP请求

```python
import asyncio
import aiohttp
import time

async def fetch_url(session, url):
    """异步获取URL"""
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
        'http://httpbin.org/delay/2',
        'http://httpbin.org/delay/1',
        'http://httpbin.org/delay/3',
    ]
    
    async with aiohttp.ClientSession() as session:
        # 并发请求
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for url, result in zip(urls, results):
            print(f"{url}: {len(result)} bytes")

# 对比性能
def sync_version():
    """同步版本（使用 requests）"""
    import requests
    urls = ['http://httpbin.org/delay/1'] * 5
    
    start = time.time()
    for url in urls:
        requests.get(url)
    print(f"Sync: {time.time() - start:.2f}s")

async def async_version():
    """异步版本"""
    urls = ['http://httpbin.org/delay/1'] * 5
    
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        await asyncio.gather(*tasks)
    print(f"Async: {time.time() - start:.2f}s")

# sync_version()  # 约 5 秒
# asyncio.run(async_version())  # 约 1 秒
```

### 3. 异步文件操作

```python
import asyncio
import aiofiles

async def read_file(filename):
    """异步读取文件"""
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
        return content

async def write_file(filename, content):
    """异步写入文件"""
    async with aiofiles.open(filename, 'w') as f:
        await f.write(content)

async def main():
    # 并发读取多个文件
    files = ['file1.txt', 'file2.txt', 'file3.txt']
    contents = await asyncio.gather(*[read_file(f) for f in files])
    
    # 处理并写入
    for i, content in enumerate(contents):
        await write_file(f'output{i}.txt', content.upper())

asyncio.run(main())
```

### 4. 异步生成器

```python
import asyncio

async def async_generator(n):
    """异步生成器"""
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    # 使用 async for 遍历
    async for value in async_generator(10):
        print(value)

asyncio.run(main())
```

---

## 性能对比

### 实战测试：下载100个URL

```python
import time
import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 测试URL
TEST_URLS = [f'http://httpbin.org/delay/0.1' for _ in range(100)]

# 1. 串行（同步）
def sync_download():
    """串行下载"""
    start = time.time()
    for url in TEST_URLS:
        response = requests.get(url)
    elapsed = time.time() - start
    print(f"串行: {elapsed:.2f}s")
    return elapsed

# 2. 多线程
def thread_download():
    """多线程下载"""
    start = time.time()
    
    def fetch(url):
        return requests.get(url)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(fetch, TEST_URLS))
    
    elapsed = time.time() - start
    print(f"多线程: {elapsed:.2f}s")
    return elapsed

# 3. 多进程（不适合I/O密集型）
def process_download():
    """多进程下载"""
    start = time.time()
    
    def fetch(url):
        return requests.get(url)
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(fetch, TEST_URLS))
    
    elapsed = time.time() - start
    print(f"多进程: {elapsed:.2f}s")
    return elapsed

# 4. 异步
async def async_download():
    """异步下载"""
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()
    
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in TEST_URLS]
        await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"异步: {elapsed:.2f}s")
    return elapsed

if __name__ == '__main__':
    # sync_time = sync_download()      # ~10s
    # thread_time = thread_download()  # ~1s
    # process_time = process_download()  # ~2s (启动开销大)
    # async_time = asyncio.run(async_download())  # ~0.2s
    pass
```

### 测试结果分析

```
场景：下载100个URL，每个延迟0.1秒

┌──────────┬──────────┬──────────┬────────────┐
│ 方法     │ 耗时     │ 倍率     │ 适用场景    │
├──────────┼──────────┼──────────┼────────────┤
│ 串行     │ ~10s    │ 1x       │ 简单脚本    │
│ 多线程   │ ~1s     │ 10x      │ I/O密集型   │
│ 多进程   │ ~2s     │ 5x       │ CPU密集型   │
│ 异步     │ ~0.2s   │ 50x      │ 大量I/O     │
└──────────┴──────────┴──────────┴────────────┘

结论：
✅ I/O密集型：异步 > 多线程 > 多进程 > 串行
✅ CPU密集型：多进程 > 串行 > 多线程 ≈ 异步
```

---

## 选择指南

### 决策树

```
┌─────────────────────────────────────┐
│   你的任务是什么类型？               │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌────▼────────┐
│CPU密集型  │    │ I/O密集型    │
│计算、处理 │    │网络、文件    │
└───┬──────┘    └────┬────────┘
    │                │
    │           ┌────┴────┐
    │           │         │
    │      ┌────▼──┐  ┌──▼──────┐
    │      │并发量  │  │并发量   │
    │      │< 100  │  │> 100    │
    │      └────┬──┘  └──┬──────┘
    │           │         │
┌───▼────────┐ ┌▼─────┐ ┌▼──────┐
│多进程       │ │多线程│ │异步    │
│Multiproc   │ │Thread│ │Asyncio │
└────────────┘ └──────┘ └────────┘
```

### 具体场景推荐

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| **网络爬虫** | Asyncio | 大量网络I/O，异步效率最高 |
| **图像处理** | Multiprocessing | CPU密集，需要真正并行 |
| **文件转换** | Multiprocessing | CPU密集计算 |
| **API服务** | Asyncio | 高并发I/O，单线程即可 |
| **数据下载** | Threading 或 Asyncio | I/O密集，看并发量选择 |
| **数据分析** | Multiprocessing | 大量计算 |
| **日志处理** | Threading | 文件I/O，中等并发 |
| **机器学习训练** | Multiprocessing | CPU密集 |

---

## 实战案例

### 案例1：并发下载器（对比三种方式）

```python
import time
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List

class Downloader:
    """下载器基类"""
    
    def __init__(self, urls: List[str]):
        self.urls = urls
    
    def download_sync(self):
        """串行下载"""
        start = time.time()
        results = []
        
        for url in self.urls:
            try:
                response = requests.get(url, timeout=10)
                results.append({
                    'url': url,
                    'status': response.status_code,
                    'size': len(response.content)
                })
            except Exception as e:
                results.append({'url': url, 'error': str(e)})
        
        elapsed = time.time() - start
        print(f"串行下载: {elapsed:.2f}s, {len(results)} 个文件")
        return results
    
    def download_thread(self, max_workers=10):
        """多线程下载"""
        start = time.time()
        
        def fetch(url):
            try:
                response = requests.get(url, timeout=10)
                return {
                    'url': url,
                    'status': response.status_code,
                    'size': len(response.content)
                }
            except Exception as e:
                return {'url': url, 'error': str(e)}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(fetch, self.urls))
        
        elapsed = time.time() - start
        print(f"多线程下载: {elapsed:.2f}s, {len(results)} 个文件, {max_workers} 线程")
        return results
    
    async def download_async(self, max_concurrent=100):
        """异步下载"""
        start = time.time()
        
        async def fetch(session, url):
            try:
                async with session.get(url, timeout=10) as response:
                    content = await response.read()
                    return {
                        'url': url,
                        'status': response.status,
                        'size': len(content)
                    }
            except Exception as e:
                return {'url': url, 'error': str(e)}
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_sem(session, url):
            async with semaphore:
                return await fetch(session, url)
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_with_sem(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        print(f"异步下载: {elapsed:.2f}s, {len(results)} 个文件, 最大并发 {max_concurrent}")
        return results

# 使用示例
if __name__ == '__main__':
    urls = [f'http://httpbin.org/delay/{i%3+1}' for i in range(20)]
    downloader = Downloader(urls)
    
    # 对比三种方式
    # results1 = downloader.download_sync()
    # results2 = downloader.download_thread(max_workers=5)
    # results3 = asyncio.run(downloader.download_async(max_concurrent=10))
```

### 案例2：图像处理（CPU密集型）

```python
from PIL import Image
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import os

def process_image(input_path, output_path):
    """处理单张图片"""
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 各种处理（CPU密集型）
        img = img.resize((800, 600))
        img = img.convert('L')  # 转灰度
        img = img.rotate(45)
        
        # 保存
        img.save(output_path)
        return f"✓ {input_path}"
    except Exception as e:
        return f"✗ {input_path}: {e}"

def batch_process_sync(image_files, output_dir):
    """串行处理"""
    start = time.time()
    
    results = []
    for img_file in image_files:
        output_path = os.path.join(output_dir, f"processed_{img_file}")
        result = process_image(img_file, output_path)
        results.append(result)
    
    elapsed = time.time() - start
    print(f"串行处理: {elapsed:.2f}s")
    return results

def batch_process_parallel(image_files, output_dir, max_workers=None):
    """并行处理"""
    start = time.time()
    
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    args = [
        (img_file, os.path.join(output_dir, f"processed_{img_file}"))
        for img_file in image_files
    ]
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.starmap(process_image, args))
    
    elapsed = time.time() - start
    print(f"并行处理({max_workers}进程): {elapsed:.2f}s")
    return results

# 使用
if __name__ == '__main__':
    image_files = ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg']
    output_dir = 'processed'
    
    # results1 = batch_process_sync(image_files, output_dir)
    # results2 = batch_process_parallel(image_files, output_dir, max_workers=4)
```

### 案例3：Web服务器（异步I/O）

```python
import asyncio
from aiohttp import web

class AsyncWebServer:
    """异步Web服务器"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/slow', self.handle_slow)
        self.app.router.add_post('/data', self.handle_data)
    
    async def handle_index(self, request):
        """首页"""
        return web.Response(text="Hello, Async World!")
    
    async def handle_slow(self, request):
        """模拟慢请求"""
        # 不会阻塞其他请求
        await asyncio.sleep(5)
        return web.Response(text="Slow response")
    
    async def handle_data(self, request):
        """处理POST数据"""
        data = await request.json()
        # 异步处理数据
        result = await self.process_data(data)
        return web.json_response(result)
    
    async def process_data(self, data):
        """异步处理数据"""
        await asyncio.sleep(0.1)
        return {'processed': True, 'data': data}
    
    def run(self, host='0.0.0.0', port=8080):
        """运行服务器"""
        web.run_app(self.app, host=host, port=port)

# 使用
if __name__ == '__main__':
    server = AsyncWebServer()
    # server.run()
```

---

## 总结

### 核心要点

1. **GIL 限制**：
   - 多线程不适合 CPU 密集型任务
   - 多进程不受 GIL 限制
   - 异步适合大量 I/O 操作

2. **内存占用**：
   - 线程：共享内存，低开销
   - 进程：独立内存，高开销
   - 异步：单线程，极低开销

3. **通信方式**：
   - 线程：共享变量（需要锁）
   - 进程：队列、管道、共享内存
   - 异步：直接共享数据

4. **使用场景**：
   - CPU密集型 → 多进程
   - I/O密集型（中等并发）→ 多线程
   - I/O密集型（高并发）→ 异步

### 最佳实践

```python
# ✅ 推荐：根据任务类型选择合适的方式

# CPU密集型：计算、图像处理
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as executor:
    results = executor.map(cpu_intensive_task, data)

# I/O密集型（中等并发）：文件操作、数据库
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(io_task, data)

# I/O密集型（高并发）：网络请求、API调用
import asyncio
async def main():
    results = await asyncio.gather(*[async_task(d) for d in data])
asyncio.run(main())
```

### 对比 PHP

```php
// PHP 多线程（需要 pthreads 扩展，很少使用）
$thread = new Thread();
$thread->start();

// PHP 通常使用多进程
pcntl_fork();

// PHP 异步（Swoole、ReactPHP）
Swoole\Coroutine::create(function() {
    // 异步代码
});
```

Python 的并发模型比 PHP 更成熟和标准化，三种方式都有很好的标准库支持。

---

**掌握这三种并发模型，你就能应对各种性能优化场景！** 🚀
