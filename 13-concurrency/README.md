# Python 并发编程实战示例

多线程、多进程、异步编程的完整实战示例。所有示例**自带输出校验**（跑完会打印实际测得的加速比、并发峰值、落盘行数），可直接反复运行。

## 📁 文件说明

| 文件 | 内容 | 依赖 |
|------|------|------|
| `01_threading_basics.py` | 线程创建、Lock / RLock / Semaphore / Event、DAEMON 线程 | 标准库 |
| `02_threading_advanced.py` | ThreadPoolExecutor、生产者消费者、优先级队列、线程安全单例、Timer | 标准库 |
| `03_multiprocessing_basics.py` | Process 创建、Queue / Pipe、Value / Array、Event、Pool | 标准库 |
| `04_multiprocessing_advanced.py` | ProcessPoolExecutor(map/submit/chunksize/initializer)、Manager、Barrier、shared_memory、BrokenProcessPool、fork/spawn/forkserver、pickle 限制 | 标准库 |
| `05_asyncio_basics.py` | 协程本质、gather / create_task / TaskGroup、超时取消 shield、asyncio 原语、async generator、to_thread 桥接 | 标准库 |
| `06_asyncio_advanced.py` | aiohttp 连接池、QPS 限流、超时重试退避、分页抓取、断点续爬 checkpoint、优雅取消（内置本地 HTTP 被测服务，**离线可跑**） | aiohttp, requests |
| `07_performance_comparison.py` | I/O 密集 / CPU 密集 / 混合任务三种模型横向对比 | requests, aiohttp |
| `08_real_world_examples.py` | 批量文件原子写、令牌桶 + 熔断、日志异步落盘、IO+CPU 三段流水线（背压）、SIGTERM 优雅停机、选型速查 | 标准库 |
| `race_condition_demo.py` | 竞态条件成因：无锁累加丢失更新的详细演示 | 标准库 |
| `race_condition_extreme.py` | 极端复现：放大窗口期，让竞态几乎每次都发生 | 标准库 |
| `test.py` | 练习草稿（`01` 的片段改写，非完整示例） | 标准库 |

## 🚀 运行

```bash
# 01-05、08 只依赖标准库，直接跑
python3 01_threading_basics.py

# 06 / 07 需要第三方库
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 06_asyncio_advanced.py

# 单独跑某个场景（每个场景都是独立函数，参数可调）
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('s08', '08_real_world_examples.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.scenario_pipeline(item_count=20, cpu_workers=4)
"
```

## 🎯 学习路径

```
第一步  理解模型        ../00-docs/python_concurrency_guide.md
第二步  多线程          01 → 02 → race_condition_demo → race_condition_extreme
第三步  多进程          03 → 04（GIL 为什么要用进程，chunksize / initializer 怎么调）
第四步  异步            05 → 06（协程的本质、限流重试、断点续爬）
第五步  横向对比        07（同一负载三种写法的实测数据）
第六步  综合落地        08（真实工程场景 + 选型速查表）
```

## 🧠 思维导图

```
                    Python 并发编程
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    多线程           多进程            异步编程
   Threading      Multiprocessing      Asyncio
        │                 │                 │
    ────┴────         ────┴────         ────┴────
    │       │         │       │         │       │
  基础   同步      基础   通信      基础   HTTP
  Thread Lock    Process Queue    async  aiohttp
  Pool  Event    Pool   Pipe     await  限流重试
  Queue RLock    Value  Manager  Task   checkpoint
  Timer 信号量   Array  sharedmem Timeout 断点续爬
```

## 🔍 快速对比

| 特性 | 多线程 | 多进程 | 异步 |
|------|-------|-------|------|
| **性能** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **内存** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **CPU密集** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **I/O密集** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 使用建议

### 什么时候用多线程？
- ✅ 文件 I/O、带 fsync 的持久化写
- ✅ 网络请求（中等并发）
- ✅ 数据库查询、只能同步驱动的 SDK
- ❌ 大量计算（受 GIL 限制）

### 什么时候用多进程？
- ✅ CPU 密集型计算
- ✅ 图像/视频处理、数据分析
- ✅ 需要进程级隔离（会崩的插件、独立内存）
- ❌ 大量 I/O 操作（IPC 与启动开销不划算）

### 什么时候用异步？
- ✅ 高并发网络请求、爬虫、Web 服务
- ✅ WebSocket、长连接
- ❌ CPU 密集型任务（会卡死整个事件循环）
- ❌ 依赖大量同步阻塞库且来不及改造（先用线程池）

## ⚠️ 实测踩过的坑（本目录示例的由来）

1. **spawn 重复执行**：macOS/Windows 默认 `spawn`，子进程会重新 import 整个文件。
   模块级写 `print` / 建线程池 → 输出重复几十份。所有顶层代码必须放进 `if __name__ == "__main__"`。
2. **`time.sleep` 混进协程**：不会报错，只是整条事件循环被冻住，吞吐不如单线程。
3. **socketserver 默认 backlog=5**：异步并发一上来就 `ConnectionResetError`，
   不是客户端的错，是 `request_queue_size` 太小（见 `06` 的 `QuietHTTPServer`）。
4. **`cancel()` 取消不了已开始的任务**：超时只能靠 `wait(timeout=)` + 任务内部自身超时。
5. **worker 崩溃会污染整个进程池**：`ProcessPoolExecutor` 抛 `BrokenProcessPool` 后必须重建，
   `multiprocessing.Pool` 会自动补 worker（见 `04` 第 7 节）。
6. **`Manager` 不是免费共享内存**：每次读写都走 IPC，大数据要用 `shared_memory`。
7. **异步日志不减少总开销**：它只是把 IO 搬到后台线程，且 `QueueHandler` 仍在业务线程格式化；
   退出前不 `listener.stop()` 会丢队列里未落盘的日志（见 `08` 场景 3）。

## 📚 相关资源

- [Python 并发编程完全指南](../00-docs/python_concurrency_guide.md)
- [Python 官方文档 - threading](https://docs.python.org/3/library/threading.html)
- [Python 官方文档 - multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Python 官方文档 - asyncio](https://docs.python.org/3/library/asyncio.html)
- [aiohttp 文档](https://docs.aiohttp.org/)
