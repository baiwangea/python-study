#!/usr/bin/env python3
"""
PHP 开发者的第一个 Python 程序
演示 Python 核心特性对比 PHP
"""

# ============================================
# 1. 基础语法对比
# ============================================

# PHP: $name = "Alice";
name = "Alice"

# PHP: echo "Hello, $name";
print(f"Hello, {name}")

# PHP: $arr = [1, 2, 3];
arr = [1, 2, 3]

# PHP: $dict = ['name' => 'Alice', 'age' => 25];
user = {'name': 'Alice', 'age': 25}

# ============================================
# 2. 函数定义
# ============================================

# PHP:
# function greet($name, $greeting = "Hello") {
#     return "$greeting, $name!";
# }

def greet(name, greeting="Hello"):
    """问候函数"""
    return f"{greeting}, {name}!"

print(greet("Bob"))  # Hello, Bob!
print(greet("Alice", "Hi"))  # Hi, Alice!

# ============================================
# 3. 列表推导式（Python 特色）
# ============================================

# PHP: array_map(fn($x) => $x * 2, $arr)
doubled = [x * 2 for x in arr]
print(f"Doubled: {doubled}")  # [2, 4, 6]

# PHP: array_filter($arr, fn($x) => $x > 1)
filtered = [x for x in arr if x > 1]
print(f"Filtered: {filtered}")  # [2, 3]

# ============================================
# 4. 字典操作
# ============================================

# 遍历字典
# PHP: foreach ($user as $key => $value)
for key, value in user.items():
    print(f"{key}: {value}")

# 获取值（带默认值）
# PHP: $user['email'] ?? 'N/A'
email = user.get('email', 'N/A')
print(f"Email: {email}")  # N/A

# ============================================
# 5. 类和对象
# ============================================

class User:
    """用户类"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    @property
    def info(self):
        """使用 @property 像访问属性一样调用方法"""
        return f"{self.name} ({self.age} years old)"
    
    def __str__(self):
        """PHP 的 __toString()"""
        return f"User: {self.name}"

user_obj = User("Charlie", 30)
print(user_obj)  # User: Charlie
print(user_obj.info)  # Charlie (30 years old)

# ============================================
# 6. 异常处理
# ============================================

def divide(a, b):
    """除法函数"""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Error: Division by zero")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        print("Division attempt completed")

print(divide(10, 2))   # 5.0
print(divide(10, 0))   # Error: Division by zero

# ============================================
# 7. 文件操作
# ============================================

# 使用 with 语句（自动关闭文件）
def write_file_example():
    """写文件示例"""
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write("Hello from Python!\n")
        f.write("This is line 2\n")
    
    # 读文件
    with open('test.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        print("File content:")
        print(content)

# write_file_example()  # 取消注释以运行

# ============================================
# 8. 装饰器（Python 特色）
# ============================================

import time
from functools import wraps

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    """模拟耗时操作"""
    time.sleep(0.5)
    return "Done"

result = slow_function()

# ============================================
# 9. 生成器（节省内存）
# ============================================

def fibonacci(n):
    """斐波那契数列生成器"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 只在需要时生成，不占用大量内存
print("Fibonacci numbers:")
for num in fibonacci(10):
    print(num, end=' ')
print()

# ============================================
# 10. 常用标准库
# ============================================

import json
import datetime
from collections import Counter

# JSON 操作
data = {'name': 'Alice', 'age': 25}
json_str = json.dumps(data, indent=2)
print("\nJSON:")
print(json_str)

# 日期时间
now = datetime.datetime.now()
print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Counter（计数器）
words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
counter = Counter(words)
print(f"\nWord count: {counter}")
print(f"Most common: {counter.most_common(2)}")

# ============================================
# 总结
# ============================================

print("\n" + "="*50)
print("Python vs PHP 关键差异总结:")
print("="*50)
print("""
1. 变量：去掉 $ 符号
2. 字符串拼接：用 + 或 f-string，不用 .
3. 数组：索引用 list，关联用 dict
4. 代码块：用缩进代替花括号
5. 对象访问：-> 改为 .
6. 空值：null → None
7. 布尔值：true/false → True/False
8. 打印：echo → print()
9. 长度：count()/strlen() → len()
10. 类型：更强调鸭子类型，少做类型检查

Python 的优势：
✓ 列表推导式（简洁优雅）
✓ 装饰器（AOP 编程）
✓ 生成器（内存高效）
✓ with 语句（资源管理）
✓ 丰富的标准库
✓ 清晰的代码风格
""")

if __name__ == '__main__':
    print("\n✅ 恭喜！你已经运行了第一个 Python 程序！")
    print("📚 接下来查看: 00-docs/php_to_python_guide.md")
