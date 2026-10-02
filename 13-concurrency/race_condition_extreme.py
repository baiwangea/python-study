#!/usr/bin/env python3
"""
极端测试：强制触发竞态条件
通过增加中间步骤，增大窗口期
"""

import threading
import time

print("=" * 70)
print("极端测试：强制触发竞态条件")
print("=" * 70)

# ============================================
# 方法1：增加操作的时间窗口
# ============================================

print("\n【方法1：增加操作的时间窗口】")
print("通过在读-写之间添加延迟，强制暴露竞态条件\n")

counter = 0

def increment_with_delay():
    """故意增加时间窗口"""
    global counter
    
    # 第1步：读取
    temp = counter
    
    # 🔥 关键：人为增加窗口期
    time.sleep(0.0001)  # 0.1毫秒延迟
    
    # 第2步：计算
    temp = temp + 1
    
    # 第3步：写入
    counter = temp

print("运行5个线程，每个执行50次:")
for test_num in range(3):
    counter = 0
    threads = []
    
    for i in range(5):
        t = threading.Thread(target=lambda: [increment_with_delay() for _ in range(50)])
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    expected = 250
    lost = expected - counter
    status = "✗ 数据丢失" if lost > 0 else "✓ 正常"
    print(f"测试 {test_num + 1}: {counter:3d} / {expected} | {status} | 丢失: {lost}")

# ============================================
# 方法2：更细粒度的操作
# ============================================

print("\n【方法2：更复杂的操作】")
print("使用列表操作，更容易触发竞态\n")

shared_list = []

def append_to_list(value):
    """向列表追加元素（会有竞态吗？）"""
    # list.append() 本身是原子的
    shared_list.append(value)

def complex_list_operation(value):
    """复杂的列表操作（非原子）"""
    # 读取长度
    length = len(shared_list)
    
    # 延迟
    time.sleep(0.0001)
    
    # 基于长度做操作
    if length < 100:
        shared_list.append(value)

print("测试1: list.append() - 原子操作")
for test_num in range(3):
    shared_list = []
    threads = []
    
    for i in range(10):
        t = threading.Thread(target=lambda i=i: [append_to_list(i) for _ in range(50)])
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    expected = 500
    actual = len(shared_list)
    status = "✓ 正确" if actual == expected else "✗ 错误"
    print(f"测试 {test_num + 1}: {actual} / {expected} | {status}")

print("\n测试2: 复杂列表操作 - 非原子")
for test_num in range(3):
    shared_list = []
    threads = []
    
    for i in range(10):
        t = threading.Thread(target=lambda i=i: [complex_list_operation(i) for _ in range(20)])
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    actual = len(shared_list)
    print(f"测试 {test_num + 1}: 列表长度 = {actual} (不确定，因为有竞态)")

# ============================================
# 方法3：银行转账示例
# ============================================

print("\n【方法3：银行转账 - 真实场景】")
print("这是竞态条件最危险的地方\n")

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
    
    def transfer_unsafe(self, to_account, amount):
        """不安全的转账"""
        # 第1步：检查余额
        if self.balance >= amount:
            # 🔥 窗口期：其他线程可能在这里执行
            time.sleep(0.001)  # 模拟网络延迟
            
            # 第2步：扣款
            self.balance -= amount
            
            # 🔥 窗口期：其他线程可能在这里执行
            time.sleep(0.001)
            
            # 第3步：入账
            to_account.balance += amount
            return True
        return False
    
    def transfer_safe(self, to_account, amount, lock):
        """安全的转账"""
        with lock:
            if self.balance >= amount:
                time.sleep(0.001)
                self.balance -= amount
                time.sleep(0.001)
                to_account.balance += amount
                return True
        return False

# 测试不安全的转账
print("不安全的转账:")
account_a = BankAccount(1000)
account_b = BankAccount(0)

def concurrent_transfer():
    """并发转账"""
    account_a.transfer_unsafe(account_b, 300)

threads = []
for _ in range(5):  # 5个线程同时转账
    t = threading.Thread(target=concurrent_transfer)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"  账户A余额: {account_a.balance:6.0f} (初始: 1000)")
print(f"  账户B余额: {account_b.balance:6.0f} (初始: 0)")
print(f"  总金额: {account_a.balance + account_b.balance:6.0f} (应该: 1000)")

if account_a.balance < 0:
    print(f"  ❌ 严重问题：账户A透支了 {abs(account_a.balance)} 元！")
elif account_a.balance + account_b.balance != 1000:
    print(f"  ❌ 问题：总金额不对，凭空 {'增加' if account_a.balance + account_b.balance > 1000 else '丢失'} "
          f"了 {abs(1000 - account_a.balance - account_b.balance)} 元！")
else:
    print(f"  ⚠️  这次碰巧正确，但不代表代码没问题")

# 测试安全的转账
print("\n安全的转账（使用锁）:")
account_c = BankAccount(1000)
account_d = BankAccount(0)
lock = threading.Lock()

def safe_transfer():
    account_c.transfer_safe(account_d, 300, lock)

threads = []
for _ in range(5):
    t = threading.Thread(target=safe_transfer)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"  账户C余额: {account_c.balance:6.0f} (初始: 1000)")
print(f"  账户D余额: {account_d.balance:6.0f} (初始: 0)")
print(f"  总金额: {account_c.balance + account_d.balance:6.0f} (应该: 1000)")

if account_c.balance + account_d.balance == 1000 and account_c.balance >= 0:
    print(f"  ✓ 正确：总金额守恒，没有透支")
else:
    print(f"  ✗ 错误：不应该发生")

# ============================================
# 总结
# ============================================

print("\n" + "=" * 70)
print("总结")
print("=" * 70)

print("""
为什么你的机器上没有复现竞态条件？

1. 现代CPU太快了
   - 操作完成得太快，线程切换来不及
   - 需要增加人为延迟来暴露问题

2. Python的GIL
   - 在某些情况下反而提供了"意外保护"
   - 但不能依赖GIL，因为：
     * I/O操作会释放GIL
     * 不同Python实现可能没有GIL
     * 某些操作仍然不是原子的

3. 系统调度器
   - macOS的调度器可能比较"友好"
   - 线程切换时机可能恰好避开了问题

4. 运气成分
   - 竞态条件本身就是概率性的
   - 可能需要运行成千上万次才会触发

🎯 关键教训：

❌ 错误心态："我测试了，没问题"
✓ 正确心态："即使测试没问题，我也要加锁"

因为：
- 开发环境 ≠ 生产环境
- 低负载 ≠ 高负载
- 测试100次正常 ≠ 第101次也正常

💡 实战建议：

1. 不要依赖测试发现竞态条件
2. 代码审查时检查并发安全性
3. 多线程 + 共享变量 + 修改操作 = 必须加锁
4. 优先使用线程安全的数据结构（Queue）
5. 能避免共享状态就避免

🔥 真实故事：

某银行系统在生产环境运行3个月都正常，
某天流量突然增大，出现了转账金额错误。
调查发现：转账代码有竞态条件。
只是之前流量小，并发度低，没有触发。

这就是为什么我们要：
- 代码审查
- 并发压力测试
- 遵循最佳实践
- 不要等bug出现才修复
""")

print("=" * 70)
