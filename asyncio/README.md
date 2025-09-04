# Python asyncio 全面学习手册

本手册分为 **入门 → 进阶 → 精通** 三个阶段，涵盖从基础概念到复杂应用案例，帮助你完全掌握 `asyncio` 模块。

---

# 入门篇

## 核心概念速览
- **协程 (Coroutine)**：可以挂起和恢复的函数，用 `async def` 定义。
- **事件循环 (Event Loop)**：调度和运行协程的核心机制。
- **任务 (Task)**：协程的封装，可以并发运行。
- **await**：挂起当前协程，等待另一个协程完成。
- **asyncio.run()**：运行事件循环的入口。
- **asyncio.create_task()**：创建任务并提交调度。
- **asyncio.gather()**：并发运行多个协程并收集结果。
- **asyncio.wait()**：等待一组任务，支持不同策略。
- **超时处理**：用 `wait_for()` 限制时间。
- **Queue**：实现生产者消费者模型。

## 方法对比表格

| 方法 | 作用 | 返回值 | 典型场景 |
|------|------|--------|-----------|
| `asyncio.run(coro)` | 启动事件循环并运行协程 | 协程返回结果 | 程序入口 |
| `asyncio.create_task(coro)` | 提交协程为任务 | `Task` 对象 | 并发运行多个任务 |
| `asyncio.gather(*coros)` | 并发运行多个协程 | 协程返回值列表 | 并发抓取数据 |
| `asyncio.wait(tasks, return_when=...)` | 等待任务集合 | (done, pending) | 灵活等待策略 |

## 入门示例

### 示例一：Hello World
```python
import asyncio

async def hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

asyncio.run(hello())
```

### 示例二：并发运行多个任务
```python
import asyncio

async def task(name, delay):
    print(f"Task {name} start")
    await asyncio.sleep(delay)
    print(f"Task {name} end")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1)
    )

asyncio.run(main())
```

### 示例三：create_task
```python
import asyncio

async def work():
    print("Working...")
    await asyncio.sleep(2)
    print("Done")

async def main():
    task = asyncio.create_task(work())
    await task

asyncio.run(main())
```

### 示例四：等待第一个完成
```python
import asyncio

async def foo():
    await asyncio.sleep(2)
    return "foo done"

async def bar():
    await asyncio.sleep(1)
    return "bar done"

async def main():
    done, pending = await asyncio.wait(
        [foo(), bar()],
        return_when=asyncio.FIRST_COMPLETED
    )
    for d in done:
        print(await d)

asyncio.run(main())
```

### 示例五：超时控制
```python
import asyncio

async def slow():
    await asyncio.sleep(5)
    return "done"

async def main():
    try:
        await asyncio.wait_for(slow(), timeout=2)
    except asyncio.TimeoutError:
        print("Task timeout!")

asyncio.run(main())
```

### 示例六：异步队列
```python
import asyncio

async def producer(queue):
    for i in range(3):
        await queue.put(i)
        print(f"Produced {i}")

async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Consumed {item}")
        queue.task_done()

async def main():
    q = asyncio.Queue()
    prod = asyncio.create_task(producer(q))
    cons = asyncio.create_task(consumer(q))
    await prod
    await q.join()
    cons.cancel()

asyncio.run(main())
```

### 示例七：异步上下文与迭代
```python
import asyncio

class AsyncCounter:
    def __init__(self):
        self.count = 0
    async def __aenter__(self):
        print("Enter")
        return self
    async def __aexit__(self, exc_type, exc, tb):
        print("Exit")
    def __aiter__(self):
        return self
    async def __anext__(self):
        self.count += 1
        if self.count > 3:
            raise StopAsyncIteration
        await asyncio.sleep(1)
        return self.count

async def main():
    async with AsyncCounter() as ac:
        async for num in ac:
            print(num)

asyncio.run(main())
```

---

# 进阶篇

### Semaphore 控制并发
```python
import asyncio

async def limited_task(name, sem):
    async with sem:
        print(f"{name} acquired")
        await asyncio.sleep(2)
        print(f"{name} released")

async def main():
    sem = asyncio.Semaphore(2)
    tasks = [limited_task(f"Task{i}", sem) for i in range(5)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

### Lock 避免竞争
```python
import asyncio

async def safe_increment(lock, counter):
    async with lock:
        tmp = counter[0]
        await asyncio.sleep(0.1)
        counter[0] = tmp + 1

async def main():
    lock = asyncio.Lock()
    counter = [0]
    tasks = [safe_increment(lock, counter) for _ in range(10)]
    await asyncio.gather(*tasks)
    print("Counter:", counter[0])

asyncio.run(main())
```

### Event 协程同步
```python
import asyncio

async def waiter(event):
    print("Waiter waiting...")
    await event.wait()
    print("Waiter triggered!")

async def setter(event):
    await asyncio.sleep(2)
    print("Setter sets event")
    event.set()

async def main():
    event = asyncio.Event()
    await asyncio.gather(waiter(event), setter(event))

asyncio.run(main())
```

### as_completed 获取最早完成的结果
```python
import asyncio

async def task(n):
    await asyncio.sleep(n)
    return f"Task {n} done"

async def main():
    tasks = [task(3), task(1), task(2)]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(result)

asyncio.run(main())
```

### 任务取消与异常处理
```python
import asyncio

async def long_task():
    try:
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise

async def main():
    t = asyncio.create_task(long_task())
    await asyncio.sleep(1)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("Handled cancellation")

asyncio.run(main())
```

---

# 精通篇

### 异步 TCP 服务器
```python
import asyncio

async def handle(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    print(f"Received: {message}")
    writer.write(data.upper().encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

### 异步 TCP 客户端
```python
import asyncio

async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    writer.write(b"hello")
    await writer.drain()
    data = await reader.read(100)
    print("Received:", data.decode())
    writer.close()

asyncio.run(tcp_client())
```

### 异步子进程
```python
import asyncio

async def run_cmd():
    proc = await asyncio.create_subprocess_exec(
        'echo', 'hello',
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    print(stdout.decode())

asyncio.run(run_cmd())
```

### 异步爬虫案例
```python
import asyncio
import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://python.org"
]

async def fetch(session, url):
    async with session.get(url) as resp:
        print(f"Fetched {url}: {resp.status}")
        return await resp.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, u) for u in urls]
        results = await asyncio.gather(*tasks)
        print("Total pages:", len(results))

asyncio.run(main())
```

### 批量文件下载器
```python
import asyncio
import aiohttp

files = {
    "python.html": "https://www.python.org",
    "httpbin.html": "https://httpbin.org/html"
}

async def download(session, url, filename):
    async with session.get(url) as resp:
        content = await resp.text()
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Saved {filename}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [download(session, url, fname) for fname, url in files.items()]
        await asyncio.gather(*tasks)

asyncio.run(main())
```

### 聊天服务器 Demo
```python
import asyncio

clients = []

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    clients.append(writer)
    print(f"New client {addr}")
    try:
        while data := await reader.readline():
            message = data.decode().strip()
            print(f"{addr}: {message}")
            for client in clients:
                if client != writer:
                    client.write(f"{addr}: {message}\n".encode())
                    await client.drain()
    except Exception:
        pass
    finally:
        clients.remove(writer)
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

---

# 总结
通过本手册的 **入门 → 进阶 → 精通** 学习路径，你将掌握：
- `asyncio` 核心概念与 API
- 并发控制与同步原语
- 网络编程与子进程
- 实战案例（爬虫、下载器、聊天服务器）

掌握这些后，你基本可以独立编写任何基于 `asyncio` 的异步程序。
