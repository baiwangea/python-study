#!/usr/bin/env python3
"""
多线程高级示例
演示：线程池、生产者消费者模式、队列
"""

import threading
import queue
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 60)
print("多线程高级示例")
print("=" * 60)

# ============================================
# 1. 线程池 - ThreadPoolExecutor
# ============================================

print("\n【1. 线程池 - ThreadPoolExecutor】")

def download_file(url):
    """模拟文件下载"""
    time.sleep(random.uniform(0.5, 1.5))
    return f"Downloaded: {url}"

urls = [f"http://example.com/file{i}.jpg" for i in range(10)]

# 方式1：使用 map()
print("\n  方式1: 使用 map()")
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(download_file, urls)
    for result in results:
        print(f"    {result}")

# 方式2：使用 submit() 和 as_completed()
print("\n  方式2: 使用 submit() - 按完成顺序处理")
with ThreadPoolExecutor(max_workers=3) as executor:
    # 提交所有任务
    future_to_url = {executor.submit(download_file, url): url for url in urls}
    
    # 按完成顺序处理结果
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            print(f"    ✓ {url} -> {result}")
        except Exception as e:
            print(f"    ✗ {url} 失败: {e}")

# ============================================
# 2. 生产者消费者模式 - Queue
# ============================================

print("\n【2. 生产者消费者模式】")

task_queue = queue.Queue()
result_queue = queue.Queue()

def producer(name, num_tasks):
    """生产者：生成任务"""
    for i in range(num_tasks):
        task = f"{name}-Task-{i}"
        task_queue.put(task)
        print(f"  ✓ {name} 生产: {task}")
        time.sleep(random.uniform(0.1, 0.3))
    print(f"  {name} 完成生产")

def consumer(name):
    """消费者：处理任务"""
    while True:
        try:
            # 设置超时，避免永久阻塞
            task = task_queue.get(timeout=2)
            print(f"  → {name} 处理: {task}")
            time.sleep(random.uniform(0.2, 0.5))
            
            result = f"{name} 完成 {task}"
            result_queue.put(result)
            
            task_queue.task_done()
        except queue.Empty:
            print(f"  {name} 退出（队列为空）")
            break

# 创建生产者线程
producers = []
for i in range(2):
    p = threading.Thread(target=producer, args=(f"Producer-{i}", 5))
    p.start()
    producers.append(p)

# 创建消费者线程
consumers = []
for i in range(3):
    c = threading.Thread(target=consumer, args=(f"Consumer-{i}",))
    c.start()
    consumers.append(c)

# 等待生产者完成
for p in producers:
    p.join()

# 等待所有任务完成
task_queue.join()

# 等待消费者完成
for c in consumers:
    c.join()

print("\n  所有结果:")
while not result_queue.empty():
    print(f"    {result_queue.get()}")

# ============================================
# 3. 优先级队列 - PriorityQueue
# ============================================

print("\n【3. 优先级队列】")

priority_queue = queue.PriorityQueue()

def worker_priority():
    """处理优先级任务"""
    while True:
        try:
            priority, task = priority_queue.get(timeout=1)
            print(f"  处理任务: 优先级={priority}, 任务={task}")
            time.sleep(0.2)
            priority_queue.task_done()
        except queue.Empty:
            break

# 添加任务（数字越小优先级越高）
tasks = [
    (3, "低优先级任务1"),
    (1, "高优先级任务1"),
    (2, "中优先级任务1"),
    (1, "高优先级任务2"),
    (3, "低优先级任务2"),
]

for priority, task in tasks:
    priority_queue.put((priority, task))
    print(f"  添加: 优先级={priority}, 任务={task}")

# 启动工作线程
threads = []
for i in range(2):
    t = threading.Thread(target=worker_priority)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# ============================================
# 4. 线程安全的单例模式
# ============================================

print("\n【4. 线程安全的单例模式】")

class Singleton:
    """线程安全的单例类"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查
                if cls._instance is None:
                    print("  创建单例实例")
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.value = 0

def create_singleton(name):
    """尝试创建单例"""
    instance = Singleton()
    print(f"  {name}: {id(instance)}")

threads = []
for i in range(5):
    t = threading.Thread(target=create_singleton, args=(f"Thread-{i}",))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("  结论: 所有线程获得相同的实例ID")

# ============================================
# 5. 定时器线程 - Timer
# ============================================

print("\n【5. 定时器线程】")

def delayed_task(name):
    """延迟执行的任务"""
    print(f"  ⏰ {name} 执行于 {time.strftime('%H:%M:%S')}")

print(f"  当前时间: {time.strftime('%H:%M:%S')}")

# 创建定时器（2秒后执行）
timer1 = threading.Timer(2, delayed_task, args=("Timer1",))
timer2 = threading.Timer(1, delayed_task, args=("Timer2",))

timer1.start()
timer2.start()

timer1.join()
timer2.join()

# ============================================
# 6. 线程池复用示例
# ============================================

print("\n【6. 线程池复用示例】")

def process_item(item):
    """处理单个项目"""
    thread_id = threading.current_thread().ident
    print(f"  线程 {thread_id} 处理 {item}")
    time.sleep(0.3)
    return f"Result-{item}"

items = list(range(15))

print("  使用3个工作线程处理15个任务:")
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_item, items))

print(f"  完成 {len(results)} 个任务")

# ============================================
# 7. 批量任务处理示例
# ============================================

print("\n【7. 批量任务处理】")

class BatchProcessor:
    """批量任务处理器"""
    
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.results = []
        self.lock = threading.Lock()
    
    def process_batch(self, items):
        """处理批量任务"""
        def process_item(item):
            # 模拟处理
            time.sleep(random.uniform(0.1, 0.3))
            result = f"Processed-{item}"
            
            # 线程安全地添加结果
            with self.lock:
                self.results.append(result)
            
            return result
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_item, item) for item in items]
            
            # 显示进度
            completed = 0
            for future in as_completed(futures):
                completed += 1
                print(f"  进度: {completed}/{len(items)}")
        
        return self.results

processor = BatchProcessor(max_workers=3)
items = [f"Item-{i}" for i in range(10)]
results = processor.process_batch(items)
print(f"  完成 {len(results)} 个任务")

# ============================================
# 8. 线程通信示例
# ============================================

print("\n【8. 线程通信示例】")

class Pipeline:
    """管道：线程间传递数据"""
    
    def __init__(self):
        self.queue = queue.Queue()
    
    def stage1(self, data):
        """阶段1：处理数据"""
        for item in data:
            processed = f"Stage1({item})"
            self.queue.put(processed)
            print(f"  Stage1 -> {processed}")
            time.sleep(0.1)
        self.queue.put(None)  # 结束信号
    
    def stage2(self):
        """阶段2：进一步处理"""
        results = []
        while True:
            item = self.queue.get()
            if item is None:
                break
            processed = f"Stage2({item})"
            results.append(processed)
            print(f"  Stage2 -> {processed}")
            time.sleep(0.1)
        return results

pipeline = Pipeline()
data = [1, 2, 3, 4, 5]

# 创建管道线程
t1 = threading.Thread(target=pipeline.stage1, args=(data,))
t2 = threading.Thread(target=pipeline.stage2)

t1.start()
t2.start()

t1.join()
t2.join()

print("\n" + "=" * 60)
print("多线程高级示例完成")
print("=" * 60)
print("\n提示：")
print("  1. ThreadPoolExecutor 简化线程池管理")
print("  2. Queue 实现线程安全的生产者消费者模式")
print("  3. PriorityQueue 处理优先级任务")
print("  4. Timer 实现延迟执行")
print("  5. 使用 with 语句自动管理资源")
