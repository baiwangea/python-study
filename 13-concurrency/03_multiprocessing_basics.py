#!/usr/bin/env python3
"""
多进程基础示例
演示：进程创建、进程间通信（Queue、Pipe）、共享内存
"""

import multiprocessing
import time
import os

print("=" * 60)
print("多进程基础示例")
print("=" * 60)

# ============================================
# 1. 基本进程创建
# ============================================

def worker(name, delay):
    """工作函数"""
    pid = os.getpid()
    print(f"  Process {name} (PID: {pid}) 开始执行")
    time.sleep(delay)
    print(f"  Process {name} (PID: {pid}) 执行完毕")

if __name__ == '__main__':
    print("\n【1. 基本进程创建】")
    print(f"  主进程 PID: {os.getpid()}")
    
    # 创建进程
    p1 = multiprocessing.Process(target=worker, args=("A", 2))
    p2 = multiprocessing.Process(target=worker, args=("B", 1))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print("  所有进程执行完毕")

# ============================================
# 2. 继承 Process 类
# ============================================

class WorkerProcess(multiprocessing.Process):
    def __init__(self, name, delay):
        super().__init__()
        self.worker_name = name
        self.delay = delay
    
    def run(self):
        """进程执行的方法"""
        pid = os.getpid()
        print(f"  Process {self.worker_name} (PID: {pid}) 开始执行")
        time.sleep(self.delay)
        print(f"  Process {self.worker_name} 执行完毕")

if __name__ == '__main__':
    print("\n【2. 继承 Process 类】")
    
    p1 = WorkerProcess("X", 1)
    p2 = WorkerProcess("Y", 1.5)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

# ============================================
# 3. 进程间通信 - Queue
# ============================================

def producer(queue, name, count):
    """生产者进程"""
    pid = os.getpid()
    for i in range(count):
        item = f"{name}-Item-{i}"
        queue.put(item)
        print(f"  Producer {name} (PID: {pid}) 生产: {item}")
        time.sleep(0.2)
    print(f"  Producer {name} 完成")

def consumer(queue, name):
    """消费者进程"""
    pid = os.getpid()
    while True:
        try:
            item = queue.get(timeout=2)
            if item is None:  # 结束信号
                break
            print(f"  Consumer {name} (PID: {pid}) 消费: {item}")
            time.sleep(0.3)
        except:
            break
    print(f"  Consumer {name} 退出")

if __name__ == '__main__':
    print("\n【3. 进程间通信 - Queue】")
    
    # 创建进程安全的队列
    queue = multiprocessing.Queue()
    
    # 创建生产者进程
    p1 = multiprocessing.Process(target=producer, args=(queue, "P1", 5))
    p2 = multiprocessing.Process(target=producer, args=(queue, "P2", 3))
    
    # 创建消费者进程
    c1 = multiprocessing.Process(target=consumer, args=(queue, "C1"))
    c2 = multiprocessing.Process(target=consumer, args=(queue, "C2"))
    
    # 启动所有进程
    p1.start()
    p2.start()
    c1.start()
    c2.start()
    
    # 等待生产者完成
    p1.join()
    p2.join()
    
    # 发送结束信号
    queue.put(None)
    queue.put(None)
    
    # 等待消费者完成
    c1.join()
    c2.join()

# ============================================
# 4. 进程间通信 - Pipe
# ============================================

def sender(conn, messages):
    """发送数据的进程"""
    pid = os.getpid()
    for msg in messages:
        conn.send(msg)
        print(f"  Sender (PID: {pid}) 发送: {msg}")
        time.sleep(0.3)
    conn.close()

def receiver(conn):
    """接收数据的进程"""
    pid = os.getpid()
    while True:
        try:
            msg = conn.recv()
            print(f"  Receiver (PID: {pid}) 接收: {msg}")
        except EOFError:
            break
    print(f"  Receiver 退出")

if __name__ == '__main__':
    print("\n【4. 进程间通信 - Pipe】")
    
    # 创建管道
    parent_conn, child_conn = multiprocessing.Pipe()
    
    messages = ['Hello', 'World', 'From', 'Pipe']
    
    # 创建进程
    p1 = multiprocessing.Process(target=sender, args=(parent_conn, messages))
    p2 = multiprocessing.Process(target=receiver, args=(child_conn,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

# ============================================
# 5. 共享内存 - Value
# ============================================

def increment_value(shared_val, lock, name, count):
    """增加共享值"""
    pid = os.getpid()
    for _ in range(count):
        with lock:
            shared_val.value += 1
            print(f"  {name} (PID: {pid}): counter = {shared_val.value}")
        time.sleep(0.1)

if __name__ == '__main__':
    print("\n【5. 共享内存 - Value】")
    
    # 创建共享值 ('i' = 整数类型)
    shared_value = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()
    
    # 创建进程
    processes = []
    for i in range(3):
        p = multiprocessing.Process(
            target=increment_value,
            args=(shared_value, lock, f"P{i}", 5)
        )
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"  最终值: {shared_value.value}")

# ============================================
# 6. 共享内存 - Array
# ============================================

def modify_array(shared_arr, lock, index, value):
    """修改共享数组"""
    pid = os.getpid()
    with lock:
        shared_arr[index] = value
        print(f"  Process (PID: {pid}) 设置 arr[{index}] = {value}")

if __name__ == '__main__':
    print("\n【6. 共享内存 - Array】")
    
    # 创建共享数组 ('i' = 整数类型, 10个元素)
    shared_array = multiprocessing.Array('i', 10)
    lock = multiprocessing.Lock()
    
    # 创建进程修改数组
    processes = []
    for i in range(10):
        p = multiprocessing.Process(
            target=modify_array,
            args=(shared_array, lock, i, i * 10)
        )
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"  最终数组: {list(shared_array)}")

# ============================================
# 7. 进程同步 - Event
# ============================================

def waiter(event, name):
    """等待事件的进程"""
    pid = os.getpid()
    print(f"  {name} (PID: {pid}) 等待信号...")
    event.wait()
    print(f"  {name} (PID: {pid}) 收到信号，继续执行")

def setter(event):
    """设置事件的进程"""
    pid = os.getpid()
    print(f"  Setter (PID: {pid}) 准备中...")
    time.sleep(2)
    print(f"  Setter 发送信号")
    event.set()

if __name__ == '__main__':
    print("\n【7. 进程同步 - Event】")
    
    event = multiprocessing.Event()
    
    # 创建等待进程
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=waiter, args=(event, f"Waiter-{i}"))
        processes.append(p)
        p.start()
    
    # 创建设置进程
    setter_proc = multiprocessing.Process(target=setter, args=(event,))
    setter_proc.start()
    
    for p in processes:
        p.join()
    setter_proc.join()

# ============================================
# 8. 进程池 - Pool
# ============================================

def square(n):
    """计算平方"""
    pid = os.getpid()
    result = n * n
    print(f"  PID {pid}: {n}² = {result}")
    return result

if __name__ == '__main__':
    print("\n【8. 进程池 - Pool】")
    
    numbers = list(range(1, 11))
    
    # 创建进程池（4个工作进程）
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(square, numbers)
    
    print(f"  结果: {results}")

# ============================================
# 9. CPU密集型任务示例
# ============================================

def cpu_intensive(n):
    """CPU密集型任务"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

if __name__ == '__main__':
    print("\n【9. CPU密集型任务对比】")
    
    numbers = [10000000, 20000000, 15000000, 25000000]
    
    # 串行执行
    print("  串行执行:")
    start = time.time()
    results_serial = [cpu_intensive(n) for n in numbers]
    serial_time = time.time() - start
    print(f"    耗时: {serial_time:.2f}s")
    
    # 并行执行
    print("  并行执行:")
    start = time.time()
    with multiprocessing.Pool(processes=4) as pool:
        results_parallel = pool.map(cpu_intensive, numbers)
    parallel_time = time.time() - start
    print(f"    耗时: {parallel_time:.2f}s")
    print(f"    加速比: {serial_time / parallel_time:.2f}x")

print("\n" + "=" * 60)
print("多进程基础示例完成")
print("=" * 60)
print("\n提示：")
print("  1. 进程独立内存空间，不受GIL限制")
print("  2. Queue 和 Pipe 用于进程间通信")
print("  3. Value 和 Array 用于共享内存")
print("  4. 多进程适合CPU密集型任务")
print("  5. 必须在 if __name__ == '__main__' 中创建进程")
