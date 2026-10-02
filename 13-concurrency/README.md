# Python 并发编程实战示例

本目录包含 Python 多线程、多进程、异步编程的完整实战示例。

## 📁 文件说明

- `01_threading_basics.py` - 多线程基础和同步机制
- `02_threading_advanced.py` - 线程池和生产者消费者模式
- `03_multiprocessing_basics.py` - 多进程基础
- `04_multiprocessing_advanced.py` - 进程池和进程间通信
- `05_asyncio_basics.py` - 异步编程基础
- `06_asyncio_advanced.py` - 异步HTTP和实战
- `07_performance_comparison.py` - 三种方式性能对比
- `08_real_world_examples.py` - 真实场景案例

## 🎯 学习路径

### 第一步：理解架构
```
查看：../00-docs/python_concurrency_guide.md
```

### 第二步：运行示例
```bash
# 多线程示例
python 01_threading_basics.py
python 02_threading_advanced.py

# 多进程示例
python 03_multiprocessing_basics.py
python 04_multiprocessing_advanced.py

# 异步示例
python 05_asyncio_basics.py
python 06_asyncio_advanced.py

# 性能对比
python 07_performance_comparison.py
```

### 第三步：实战练习
修改和扩展 `08_real_world_examples.py` 中的案例。

## 📊 思维导图

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
  Pool  Event    Pool   Pipe     await  aiofiles
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
- ✅ 文件I/O操作
- ✅ 网络请求（中等并发）
- ✅ 数据库查询
- ❌ 大量计算

### 什么时候用多进程？
- ✅ CPU密集型计算
- ✅ 图像/视频处理
- ✅ 数据分析
- ❌ 大量I/O操作

### 什么时候用异步？
- ✅ 高并发网络请求
- ✅ Web服务器
- ✅ WebSocket
- ✅ 爬虫
- ❌ CPU密集型任务

## 🚀 开始学习

1. 先阅读：`../00-docs/python_concurrency_guide.md`
2. 运行基础示例理解概念
3. 查看性能对比理解差异
4. 实践真实案例掌握应用

## 📚 相关资源

- [Python 并发编程完全指南](../00-docs/python_concurrency_guide.md)
- [Python 官方文档 - threading](https://docs.python.org/3/library/threading.html)
- [Python 官方文档 - multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Python 官方文档 - asyncio](https://docs.python.org/3/library/asyncio.html)
