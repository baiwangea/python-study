# PHP 开发者的 Python 30 天学习计划

## 总体目标
- ✅ 掌握 Python 核心语法和特性
- ✅ 能独立开发 Web API 和爬虫项目
- ✅ 理解 Python 生态和最佳实践
- ✅ 达到能在工作中使用 Python 的水平

---

## 第一周：Python 基础 (Day 1-7)

### Day 1: 环境搭建 & 语法基础
**学习时间**: 2-3 小时

**任务清单**:
- [ ] 确认 Python 环境（建议 Python 3.11+）
- [ ] 熟悉 conda 环境管理
- [ ] 阅读：`00-docs/php_python_cheatsheet.md`
- [ ] 阅读：`00-docs/python_data_types.markdown`

**实战练习**:
```python
# 练习 1: 改写你常用的 PHP 函数
# 例如：改写一个 array 处理函数

# PHP 版本
# function filterPositive($arr) {
#     return array_filter($arr, fn($x) => $x > 0);
# }

# Python 版本
def filter_positive(arr):
    return [x for x in arr if x > 0]

# 练习 2: 数据类型转换
data = "1,2,3,4,5"
# 转换为整数列表并求和
numbers = [int(x) for x in data.split(',')]
total = sum(numbers)
print(total)  # 15

# 练习 3: 字典操作
user = {
    'name': 'Alice',
    'age': 25,
    'email': 'alice@example.com'
}

# 获取所有键值对
for key, value in user.items():
    print(f"{key}: {value}")
```

**今日目标**: 能不看文档写出基本的变量、列表、字典操作

---

### Day 2: 控制流 & 函数
**学习时间**: 2-3 小时

**任务清单**:
- [ ] 掌握 if/elif/else、for、while
- [ ] 理解列表推导式和生成器表达式
- [ ] 学习函数定义、参数、返回值

**实战练习**:
```python
# 练习 1: FizzBuzz
def fizzbuzz(n):
    """经典编程题"""
    for i in range(1, n + 1):
        if i % 15 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

# 练习 2: 列表推导式
# 生成 1-100 中所有 3 或 5 的倍数
multiples = [x for x in range(1, 101) if x % 3 == 0 or x % 5 == 0]

# 练习 3: 函数参数
def create_user(name, age=18, **kwargs):
    """演示不同类型的参数"""
    user = {
        'name': name,
        'age': age,
        **kwargs
    }
    return user

user1 = create_user('Alice')
user2 = create_user('Bob', age=25, city='NYC', role='admin')

# 练习 4: Lambda 表达式
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
# 但推荐使用列表推导式
squared = [x**2 for x in numbers]
```

**今日目标**: 能写出清晰的函数和循环逻辑

---

### Day 3: 面向对象编程
**学习时间**: 3-4 小时

**任务清单**:
- [ ] 阅读：`00-docs/python_functions_classes_oop.markdown`
- [ ] 理解类、对象、继承
- [ ] 掌握 `@property`、`@staticmethod`、`@classmethod`

**实战练习**:
```python
# 练习 1: 基础类定义
class User:
    """用户类"""
    
    def __init__(self, name, email):
        self._name = name
        self.email = email
        self._created_at = datetime.now()
    
    @property
    def name(self):
        """使用 property 访问私有属性"""
        return self._name
    
    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value
    
    def __str__(self):
        return f"User({self.name}, {self.email})"
    
    def __repr__(self):
        return f"User(name='{self.name}', email='{self.email}')"

# 练习 2: 继承
class Admin(User):
    def __init__(self, name, email, permissions=None):
        super().__init__(name, email)
        self.permissions = permissions or []
    
    def has_permission(self, perm):
        return perm in self.permissions

# 练习 3: 工厂方法
class User:
    # ... 其他代码 ...
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建用户"""
        return cls(
            name=data['name'],
            email=data['email']
        )
    
    @staticmethod
    def is_valid_email(email):
        """验证邮箱格式"""
        return '@' in email

# 使用
user_data = {'name': 'Alice', 'email': 'alice@example.com'}
user = User.from_dict(user_data)
```

**今日目标**: 能写出结构清晰的类和继承关系

---

### Day 4: 文件操作 & 异常处理
**学习时间**: 2-3 小时

**任务清单**:
- [ ] 掌握文件读写操作
- [ ] 理解 `with` 语句（上下文管理器）
- [ ] 学习异常处理机制

**实战练习**:
```python
# 练习 1: 文件读写
def read_config(filename):
    """读取配置文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
        return None
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None

def write_log(message, filename='app.log'):
    """追加日志"""
    with open(filename, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")

# 练习 2: CSV 处理
import csv

def read_csv(filename):
    """读取 CSV 文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(data, filename):
    """写入 CSV 文件"""
    if not data:
        return
    
    keys = data[0].keys()
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# 练习 3: JSON 处理
import json

def load_json(filename):
    """加载 JSON 文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None

def save_json(data, filename):
    """保存 JSON 文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

**小项目**: CSV 数据清洗工具
```python
"""
项目：CSV 数据清洗工具
功能：
1. 读取 CSV 文件
2. 过滤空行和无效数据
3. 统计数据
4. 导出清洗后的数据
"""

import csv
from pathlib import Path

class CSVCleaner:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = []
    
    def load(self):
        """加载数据"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        return self
    
    def remove_empty_rows(self):
        """移除空行"""
        self.data = [row for row in self.data if any(row.values())]
        return self
    
    def filter_by_column(self, column, condition):
        """按条件过滤"""
        self.data = [row for row in self.data if condition(row.get(column))]
        return self
    
    def stats(self):
        """统计信息"""
        return {
            'total_rows': len(self.data),
            'columns': list(self.data[0].keys()) if self.data else []
        }
    
    def save(self, output_file):
        """保存数据"""
        if not self.data:
            print("没有数据可保存")
            return
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)
        print(f"已保存到 {output_file}")

# 使用
cleaner = CSVCleaner('data.csv')
cleaner.load() \
    .remove_empty_rows() \
    .filter_by_column('age', lambda x: x and int(x) >= 18) \
    .save('cleaned.csv')

print(cleaner.stats())
```

**今日目标**: 能处理常见的文件格式（TXT、CSV、JSON）

---

### Day 5: 模块和包
**学习时间**: 2-3 小时

**任务清单**:
- [ ] 理解模块导入机制
- [ ] 学习创建自己的模块
- [ ] 掌握常用标准库

**实战练习**:
```python
# 项目结构
# myproject/
#   ├── __init__.py
#   ├── utils.py
#   ├── models.py
#   └── main.py

# utils.py
"""工具函数模块"""

def format_date(dt):
    """格式化日期"""
    return dt.strftime('%Y-%m-%d')

def validate_email(email):
    """验证邮箱"""
    return '@' in email and '.' in email

# models.py
"""数据模型模块"""

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

# main.py
"""主程序"""

from datetime import datetime
from utils import format_date, validate_email
from models import User

def main():
    user = User('Alice', 'alice@example.com')
    print(f"User: {user.name}")
    print(f"Today: {format_date(datetime.now())}")

if __name__ == '__main__':
    main()

# 练习：常用标准库
import os
import sys
import pathlib
import datetime
import json
import re
from collections import defaultdict, Counter
from itertools import groupby

# pathlib 示例（推荐使用）
from pathlib import Path

# 获取当前目录
current_dir = Path.cwd()

# 列出所有 Python 文件
py_files = list(current_dir.glob('*.py'))

# 读取文件
config_path = Path('config.json')
if config_path.exists():
    config = json.loads(config_path.read_text())

# collections 示例
# defaultdict - 带默认值的字典
word_count = defaultdict(int)
for word in ['apple', 'banana', 'apple']:
    word_count[word] += 1

# Counter - 计数器
from collections import Counter
words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
counter = Counter(words)
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]
```

**今日目标**: 理解 Python 的模块系统，能组织项目结构

---

### Day 6: 函数式编程特性
**学习时间**: 2-3 小时

**任务清单**:
- [ ] 掌握装饰器
- [ ] 理解生成器和迭代器
- [ ] 学习函数式编程工具

**实战练习**:
```python
# 练习 1: 装饰器基础
import time
from functools import wraps

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

# 练习 2: 带参数的装饰器
def retry(max_attempts=3):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
        return wrapper
    return decorator

@retry(max_attempts=3)
def flaky_api_call():
    # 模拟不稳定的 API
    import random
    if random.random() < 0.7:
        raise Exception("API Error")
    return "Success"

# 练习 3: 生成器
def read_large_file(filename):
    """逐行读取大文件（节省内存）"""
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

# 使用生成器
for line in read_large_file('large.log'):
    if 'ERROR' in line:
        print(line)

def fibonacci(n):
    """斐波那契数列生成器"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 生成前 10 个斐波那契数
fibs = list(fibonacci(10))
print(fibs)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# 练习 4: 函数式工具
from functools import reduce
from itertools import chain, islice

# reduce 示例
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)  # 120

# chain - 连接多个迭代器
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list(chain(list1, list2))  # [1, 2, 3, 4, 5, 6]

# islice - 切片迭代器
from itertools import islice
numbers = range(100)
first_10 = list(islice(numbers, 10))  # [0, 1, ..., 9]
```

**小项目**: 日志分析工具
```python
"""
项目：日志分析工具
使用装饰器和生成器处理大日志文件
"""

import re
from datetime import datetime
from collections import Counter, defaultdict

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.2f}s")
        return result
    return wrapper

class LogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
    
    def parse_lines(self):
        """生成器：逐行解析日志"""
        pattern = r'\[(.*?)\] (\w+): (.*)'
        with open(self.log_file, 'r') as f:
            for line in f:
                match = re.match(pattern, line)
                if match:
                    timestamp, level, message = match.groups()
                    yield {
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    }
    
    @timer
    def count_by_level(self):
        """统计各级别日志数量"""
        counter = Counter(
            entry['level'] for entry in self.parse_lines()
        )
        return counter
    
    @timer
    def find_errors(self):
        """查找错误日志"""
        return [
            entry for entry in self.parse_lines()
            if entry['level'] == 'ERROR'
        ]
    
    @timer
    def group_by_hour(self):
        """按小时分组"""
        groups = defaultdict(int)
        for entry in self.parse_lines():
            hour = entry['timestamp'][:13]  # YYYY-MM-DD HH
            groups[hour] += 1
        return dict(groups)

# 使用
analyzer = LogAnalyzer('app.log')
print(analyzer.count_by_level())
errors = analyzer.find_errors()
print(f"Found {len(errors)} errors")
```

**今日目标**: 掌握装饰器和生成器，能写出优雅的 Python 代码

---

### Day 7: 第一周总结 & 综合项目
**学习时间**: 3-4 小时

**任务清单**:
- [ ] 复习本周学习内容
- [ ] 完成综合小项目
- [ ] 自我评估

**综合项目**: 命令行待办事项管理器
```python
"""
项目：命令行待办事项管理器
功能：
1. 添加任务
2. 列出任务
3. 完成任务
4. 删除任务
5. 数据持久化（JSON）
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class TodoItem:
    """待办事项"""
    
    def __init__(self, title, description='', done=False, created_at=None):
        self.title = title
        self.description = description
        self.done = done
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'done': self.done,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def __str__(self):
        status = '✓' if self.done else ' '
        return f"[{status}] {self.title}"

class TodoManager:
    """待办事项管理器"""
    
    def __init__(self, data_file='todos.json'):
        self.data_file = Path(data_file)
        self.todos: List[TodoItem] = []
        self.load()
    
    def load(self):
        """加载数据"""
        if self.data_file.exists():
            data = json.loads(self.data_file.read_text())
            self.todos = [TodoItem.from_dict(item) for item in data]
    
    def save(self):
        """保存数据"""
        data = [todo.to_dict() for todo in self.todos]
        self.data_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def add(self, title, description=''):
        """添加任务"""
        todo = TodoItem(title, description)
        self.todos.append(todo)
        self.save()
        print(f"✓ 已添加: {title}")
    
    def list(self, show_all=True):
        """列出任务"""
        todos = self.todos if show_all else [t for t in self.todos if not t.done]
        
        if not todos:
            print("没有任务")
            return
        
        for i, todo in enumerate(todos, 1):
            print(f"{i}. {todo}")
            if todo.description:
                print(f"   {todo.description}")
    
    def complete(self, index):
        """完成任务"""
        if 0 <= index < len(self.todos):
            self.todos[index].done = True
            self.save()
            print(f"✓ 已完成: {self.todos[index].title}")
        else:
            print("无效的任务编号")
    
    def delete(self, index):
        """删除任务"""
        if 0 <= index < len(self.todos):
            todo = self.todos.pop(index)
            self.save()
            print(f"✓ 已删除: {todo.title}")
        else:
            print("无效的任务编号")
    
    def stats(self):
        """统计信息"""
        total = len(self.todos)
        done = sum(1 for t in self.todos if t.done)
        pending = total - done
        print(f"总计: {total} | 完成: {done} | 待办: {pending}")

def main():
    """主程序"""
    manager = TodoManager()
    
    while True:
        print("\n" + "="*50)
        print("待办事项管理器")
        print("="*50)
        print("1. 添加任务")
        print("2. 列出所有任务")
        print("3. 列出待办任务")
        print("4. 完成任务")
        print("5. 删除任务")
        print("6. 统计")
        print("0. 退出")
        
        choice = input("\n请选择操作: ").strip()
        
        if choice == '1':
            title = input("任务标题: ").strip()
            description = input("任务描述（可选）: ").strip()
            manager.add(title, description)
        
        elif choice == '2':
            manager.list(show_all=True)
        
        elif choice == '3':
            manager.list(show_all=False)
        
        elif choice == '4':
            manager.list(show_all=False)
            try:
                index = int(input("请输入任务编号: ")) - 1
                manager.complete(index)
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '5':
            manager.list(show_all=True)
            try:
                index = int(input("请输入任务编号: ")) - 1
                manager.delete(index)
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '6':
            manager.stats()
        
        elif choice == '0':
            print("再见!")
            break
        
        else:
            print("无效的选择")

if __name__ == '__main__':
    main()
```

**第一周学习检查清单**:
- [ ] 能不看文档写出基本的类和函数
- [ ] 理解列表推导式和字典推导式
- [ ] 掌握文件读写和异常处理
- [ ] 能使用装饰器和生成器
- [ ] 完成待办事项管理器项目

---

## 第二周：异步编程 & CLI 工具 (Day 8-14)

### Day 8-9: 异步编程 (asyncio)
**参考项目**: `01-asyncio/`

**学习内容**:
- async/await 语法
- 并发 HTTP 请求
- 异步文件操作

**实战练习**:
```python
import asyncio
import aiohttp
from typing import List

async def fetch_url(session, url):
    """异步获取 URL"""
    async with session.get(url) as response:
        return await response.text()

async def fetch_multiple(urls: List[str]):
    """并发获取多个 URL"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# 使用
urls = [
    'https://api.github.com/users/github',
    'https://api.github.com/users/python',
]
results = asyncio.run(fetch_multiple(urls))
```

---

### Day 10-11: CLI 工具开发 (Typer)
**参考项目**: `05-typer/`

**实战项目**: 文件批量处理工具
```python
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def rename(
    directory: Path = typer.Argument(..., help="目标目录"),
    pattern: str = typer.Option("", help="文件名模式"),
    prefix: str = typer.Option("", help="添加前缀"),
):
    """批量重命名文件"""
    files = directory.glob(pattern or "*")
    for file in files:
        new_name = f"{prefix}{file.name}"
        file.rename(file.parent / new_name)
        typer.echo(f"Renamed: {file.name} -> {new_name}")

if __name__ == "__main__":
    app()
```

---

### Day 12-13: 数据处理与可视化
**参考项目**: `02-dash-apps/`

**学习内容**:
- Pandas 基础
- 数据清洗和转换
- Dash 可视化

---

### Day 14: 第二周总结项目
**综合项目**: 数据采集和分析工具

---

## 第三周：Web 开发 (Day 15-21)

### Day 15-17: FastAPI 开发
**参考项目**: `03-fastapi/`

**学习目标**:
- RESTful API 设计
- 数据验证（Pydantic）
- 数据库操作（SQLAlchemy）
- 认证和授权

---

### Day 18-19: 队列和异步任务
**参考项目**: `07-queue/`

**学习内容**:
- RabbitMQ 基础
- 生产者消费者模式
- 延迟任务和重试机制

---

### Day 20-21: 第三周项目
**综合项目**: 完整的 Web API 服务
- FastAPI 后端
- SQLAlchemy ORM
- RabbitMQ 任务队列
- JWT 认证

---

## 第四周：爬虫与实战 (Day 22-30)

### Day 22-24: 网页爬虫
**参考项目**: `08-zaubacorp/`

**学习内容**:
- requests + BeautifulSoup
- 数据提取和清洗
- Excel 导出
- 错误处理和重试

---

### Day 25-26: 高性能请求
**参考项目**: `04-rusty_req/`

**学习内容**:
- httpx 异步请求
- 连接池管理
- 性能优化

---

### Day 27-28: 测试
**学习内容**:
- pytest 基础
- 单元测试
- Mock 和 Fixture
- 覆盖率报告

---

### Day 29-30: 毕业项目
**选择一个项目完成**:

1. **全栈应用**: FastAPI + React
2. **数据平台**: Dash + Pandas
3. **爬虫系统**: Scrapy + RabbitMQ

---

## 学习资源

### 在线文档
- [Python 官方文档（中文）](https://docs.python.org/zh-cn/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
- [Real Python](https://realpython.com/)

### 推荐书籍
- 《Fluent Python》（流畅的Python）
- 《Python Cookbook》
- 《Effective Python》

### 实践平台
- LeetCode Python 专题
- HackerRank
- Real Python 实战教程

---

## 每日学习建议

### 时间分配
- **工作日**: 2-3小时
  - 理论学习: 1小时
  - 编码实践: 1-2小时

- **周末**: 4-6小时
  - 项目开发为主

### 学习方法
1. **先理解，再记忆**: 理解概念比死记语法重要
2. **边学边做**: 每个知识点都要写代码验证
3. **对比学习**: 对比 PHP 和 Python 的差异
4. **查文档**: 遇到问题先查官方文档
5. **写总结**: 每天写学习笔记

### 进度跟踪
- 每天完成后打勾
- 记录遇到的问题和解决方案
- 定期回顾之前的代码

---

## 常见问题

### Q: 我应该用 Python 2 还是 Python 3?
A: 一定用 Python 3.11+，Python 2 已经停止维护。

### Q: 需要掌握所有标准库吗?
A: 不需要。重点掌握常用的（os, sys, pathlib, json, datetime, collections）。

### Q: 要不要学机器学习?
A: 先打好基础，Web 开发熟练后再考虑。

### Q: 如何避免忘记?
A: 多写代码，多做项目，定期复习。

---

## 结语

30 天是一个紧凑的学习周期，但作为有经验的 PHP 开发者，你已经具备：
- ✅ 编程思维
- ✅ Web 开发经验
- ✅ 问题解决能力

现在只需要适应 Python 的语法和生态。保持每天编码，一个月后你就能用 Python 开发项目了！

**记住**: 
- 不要追求完美，先完成再完美
- 遇到问题多查文档和 Stack Overflow
- 保持好奇心，享受学习过程

祝你学习顺利！🚀

---

## 附录：快速参考

### Python vs PHP 关键差异
| 特性 | PHP | Python |
|------|-----|--------|
| 变量 | `$var` | `var` |
| 字符串拼接 | `.` | `+` 或 f-string |
| 数组 | `array()` | `list` / `dict` |
| 代码块 | `{}` | 缩进 |
| 打印 | `echo` | `print()` |
| 空值 | `null` | `None` |
| 布尔值 | `true/false` | `True/False` |

### 必装工具
- IDE: VS Code + Python 扩展
- 包管理: pip, poetry
- 虚拟环境: conda, venv
- 代码格式化: black, ruff
- 类型检查: mypy

### 常用命令
```bash
# 创建虚拟环境
conda create -n myenv python=3.11

# 激活环境
conda activate myenv

# 安装包
pip install requests fastapi

# 运行脚本
python script.py

# 安装项目依赖
pip install -r requirements.txt
```
