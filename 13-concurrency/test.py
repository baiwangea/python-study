#!/usr/bin/env python3
"""
多线程基础示例
演示：线程创建、同步机制（Lock、RLock、Semaphore、Event）
"""

import threading
import time
import random

# ============================================
# 3. 线程同步 - Lock（锁）
# ============================================

print("\n【3. Lock - 解决竞态条件】")

# 3.1 不使用锁的问题
counter_no_lock = 0

def increment_no_lock():
    global counter_no_lock
    for _ in range(100000):
        counter_no_lock += 1

threads = []
for _ in range(5):
    t = threading.Thread(target=increment_no_lock)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"  不使用锁的结果: {counter_no_lock} (期望: 500000)")
print(f"  数据丢失: {500000 - counter_no_lock}")