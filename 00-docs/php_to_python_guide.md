# PHP 开发者快速上手 Python 指南

## 目录
- [核心语法对比](#核心语法对比)
- [快速学习路径](#快速学习路径)
- [关键差异点](#关键差异点)
- [实战项目建议](#实战项目建议)
- [常见陷阱](#常见陷阱)

---

## 核心语法对比

### 1. 基础语法差异

| 特性 | PHP | Python |
|------|-----|--------|
| 变量声明 | `$var = 10;` | `var = 10` |
| 常量 | `define('PI', 3.14);` | `PI = 3.14` (约定大写) |
| 字符串拼接 | `$name . " Smith"` | `f"{name} Smith"` 或 `name + " Smith"` |
| 数组/列表 | `$arr = [1, 2, 3];` | `arr = [1, 2, 3]` |
| 关联数组/字典 | `$dict = ['key' => 'value'];` | `dict = {'key': 'value'}` |
| 打印输出 | `echo "Hello";` | `print("Hello")` |
| 代码块 | 花括号 `{}` | 缩进（4个空格或Tab） |
| 注释 | `// 单行` 或 `/* 多行 */` | `# 单行` 或 `''' 多行 '''` |
| 函数定义 | `function add($a, $b) { return $a + $b; }` | `def add(a, b): return a + b` |
| 类定义 | `class User { public $name; }` | `class User: def __init__(self): self.name = ""` |

### 2. 数据结构对照

```php
// PHP
$indexed_array = [1, 2, 3];
$assoc_array = ['name' => 'John', 'age' => 30];
$multi = ['users' => [['name' => 'Alice'], ['name' => 'Bob']]];
```

```python
# Python
indexed_list = [1, 2, 3]
dictionary = {'name': 'John', 'age': 30}
multi = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}

# Python 额外的数据结构
tuple_data = (1, 2, 3)  # 不可变列表
set_data = {1, 2, 3}    # 无序唯一集合
```

### 3. 控制流对比

#### 条件判断
```php
// PHP
if ($x > 0) {
    echo "Positive";
} elseif ($x < 0) {
    echo "Negative";
} else {
    echo "Zero";
}

$result = $x > 0 ? "Yes" : "No";
```

```python
# Python
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

result = "Yes" if x > 0 else "No"
```

#### 循环
```php
// PHP
foreach ($items as $item) {
    echo $item;
}

foreach ($dict as $key => $value) {
    echo "$key: $value";
}

for ($i = 0; $i < 10; $i++) {
    echo $i;
}

while ($x < 10) {
    $x++;
}
```

```python
# Python
for item in items:
    print(item)

for key, value in dict.items():
    print(f"{key}: {value}")

for i in range(10):
    print(i)

while x < 10:
    x += 1

# Python 特色：列表推导式
squares = [x**2 for x in range(10)]
filtered = [x for x in items if x > 0]
```

### 4. 函数对比

```php
// PHP
function greet($name, $greeting = "Hello") {
    return "$greeting, $name!";
}

// 可变参数
function sum(...$numbers) {
    return array_sum($numbers);
}

// 匿名函数
$multiply = function($a, $b) {
    return $a * $b;
};
```

```python
# Python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# 可变参数
def sum_numbers(*numbers):
    return sum(numbers)

# Lambda 表达式
multiply = lambda a, b: a * b

# 关键字参数
def create_user(name, age=18, city="Unknown"):
    return {'name': name, 'age': age, 'city': city}

user = create_user(name="Alice", city="NYC")  # 可以跳过默认参数
```

### 5. 面向对象对比

```php
// PHP
class User {
    private $name;
    protected $age;
    public $email;
    
    public function __construct($name) {
        $this->name = $name;
    }
    
    public function getName() {
        return $this->name;
    }
    
    public static function create($name) {
        return new self($name);
    }
}

class Admin extends User {
    public function getRole() {
        return "admin";
    }
}

$user = new User("Alice");
echo $user->getName();
```

```python
# Python
class User:
    def __init__(self, name):
        self._name = name      # 约定：单下划线为"受保护"
        self.__secret = "xyz"  # 双下划线为"私有"（名称改写）
        self.email = None
    
    def get_name(self):
        return self._name
    
    @property
    def name(self):
        """属性装饰器，可以像访问属性一样调用"""
        return self._name
    
    @staticmethod
    def create(name):
        return User(name)
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['name'])

class Admin(User):
    def get_role(self):
        return "admin"

user = User("Alice")
print(user.get_name())
print(user.name)  # 使用 @property
```

### 6. 错误处理对比

```php
// PHP
try {
    throw new Exception("Error message");
} catch (Exception $e) {
    echo $e->getMessage();
} finally {
    echo "Cleanup";
}
```

```python
# Python
try:
    raise Exception("Error message")
except Exception as e:
    print(str(e))
except ValueError:  # 可以捕获特定异常
    print("Value error")
else:  # 没有异常时执行
    print("No error")
finally:
    print("Cleanup")

# Context manager (类似 PHP 的 try-finally)
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭
```

---

## 快速学习路径

### 第一周：核心基础
**目标：掌握语法差异，能写简单脚本**

1. **Day 1-2：基础语法** ✅ 已有文档
   - 阅读：`00-docs/python_data_types.markdown`
   - 阅读：`00-docs/python_functions_classes_oop.markdown`
   - 练习：改写 5 个常用的 PHP 工具函数到 Python

2. **Day 3-4：数据结构实战**
   - 列表、字典、集合的深入使用
   - 练习：实现一个简单的数据清洗脚本
   - 对比：PHP 数组 vs Python 列表/字典

3. **Day 5-7：文件和模块**
   - 文件读写（对比 PHP 的 file_get_contents）
   - 模块系统（对比 require/include）
   - JSON/CSV 处理
   - **实战项目**：CSV 数据处理工具

### 第二周：进阶特性
**目标：理解 Python 特色，提升开发效率**

1. **Day 8-10：函数式编程特性**
   - 列表推导式、生成器表达式
   - map、filter、reduce
   - 装饰器（类似 PHP 的 Attributes）
   - **实战项目**：日志装饰器系统

2. **Day 11-12：异步编程** ✅ 已有模块
   - 目录：`01-asyncio/`
   - 对比：PHP 8 Fibers vs Python asyncio
   - 练习：并发 HTTP 请求

3. **Day 13-14：命令行工具** ✅ 已有模块
   - 目录：`05-typer/`
   - 对比：Symfony Console vs Typer
   - **实战项目**：开发一个 CLI 工具

### 第三周：Web 开发
**目标：能用 Python 开发 Web 应用**

1. **Day 15-17：FastAPI** ✅ 已有项目
   - 目录：`03-fastapi/`
   - 对比：Laravel Routes vs FastAPI
   - 特点：自动文档、类型验证、高性能
   - **实战项目**：RESTful API 开发

2. **Day 18-19：数据库操作**
   - SQLAlchemy ORM（类似 Eloquent）
   - 迁移系统（类似 Laravel Migrations）

3. **Day 20-21：队列和异步任务** ✅ 已有模块
   - 目录：`07-queue/`
   - RabbitMQ 实战
   - 对比：Laravel Queue vs Python Celery

### 第四周：实战与生态
**目标：独立开发完整项目**

1. **Day 22-24：爬虫和自动化** ✅ 已有项目
   - 目录：`08-zaubacorp/`（爬虫实战）
   - BeautifulSoup、Selenium
   - 数据采集和处理

2. **Day 25-26：测试**
   - pytest（对比 PHPUnit）
   - 单元测试、集成测试
   - Mock 和 Fixture

3. **Day 27-28：性能优化**
   - 目录：`04-rusty_req/`（高性能请求）
   - Profiling 工具
   - 多进程/多线程

4. **Day 29-30：综合项目**
   - 开发一个完整的 Web 应用
   - 包含：API、数据库、队列、定时任务

---

## 关键差异点

### 1. 最重要的思维转变

#### ✨ 缩进即语法
```python
# Python - 缩进决定代码块
def example():
    if True:
        print("Indented")  # 必须缩进
    print("Still in function")
print("Outside function")
```

**注意**：不要混用 Tab 和空格！统一使用 4 个空格。

#### ✨ 一切皆对象
```python
# 在 Python 中，连函数都是对象
def greet():
    return "Hello"

# 可以赋值
my_func = greet
print(my_func())  # "Hello"

# 可以作为参数传递
def execute(func):
    return func()

result = execute(greet)
```

#### ✨ Duck Typing（鸭子类型）
```python
# PHP 需要严格的类型检查
# Python 关注的是"能不能做"而不是"是什么类型"

class Duck:
    def quack(self):
        return "Quack!"

class Person:
    def quack(self):
        return "I'm imitating a duck!"

def make_it_quack(thing):
    # 不关心 thing 是什么类型，只要它有 quack 方法
    print(thing.quack())

make_it_quack(Duck())    # OK
make_it_quack(Person())  # 也 OK
```

### 2. 没有的 PHP 特性及替代方案

| PHP 特性 | Python 替代方案 |
|----------|----------------|
| `$_GET`, `$_POST` | FastAPI: `request.query_params`, `request.form()` |
| `$_SESSION` | Flask-Session 或 FastAPI 的 session middleware |
| `isset()` | `if var is not None:` 或 `hasattr(obj, 'attr')` |
| `empty()` | `if not var:` |
| `array_map()` | `map()` 或列表推导式 `[f(x) for x in list]` |
| `array_filter()` | `filter()` 或 `[x for x in list if condition]` |
| `count()` | `len()` |
| `in_array()` | `item in list` |
| `implode()` / `explode()` | `str.join()` / `str.split()` |
| `json_encode()` / `json_decode()` | `json.dumps()` / `json.loads()` |
| Composer | pip / Poetry / uv |
| PHPDoc | Type hints + docstring |

### 3. Python 独有的强大特性

#### 列表推导式
```python
# PHP
$squares = array_map(fn($x) => $x * $x, range(1, 10));

# Python - 更简洁
squares = [x**2 for x in range(1, 11)]

# 带条件
even_squares = [x**2 for x in range(1, 11) if x % 2 == 0]

# 字典推导式
word_lengths = {word: len(word) for word in ['hello', 'world']}
```

#### 上下文管理器
```python
# 自动管理资源
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭，即使发生异常

# 数据库连接
with get_db_connection() as conn:
    conn.execute("SELECT * FROM users")
# 连接自动关闭
```

#### 装饰器
```python
# 类似 PHP 的 Attributes，但更强大
def log_execution(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_execution
def process_data(data):
    return data * 2

# 等同于：process_data = log_execution(process_data)
```

#### 生成器（节省内存）
```python
# PHP - 必须生成完整数组
function get_numbers() {
    $arr = [];
    for ($i = 0; $i < 1000000; $i++) {
        $arr[] = $i;
    }
    return $arr;  // 占用大量内存
}

# Python - 按需生成
def get_numbers():
    for i in range(1000000):
        yield i  # 只在需要时生成下一个值

# 使用
for num in get_numbers():
    if num > 10:
        break  # 不会生成所有 100 万个数字
```

#### Multiple Inheritance (多重继承)
```python
class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")

class CacheMixin:
    def cache_set(self, key, value):
        self._cache[key] = value

class User(LoggerMixin, CacheMixin):
    def __init__(self):
        self._cache = {}

user = User()
user.log("User created")
user.cache_set("key", "value")
```

---

## 实战项目建议

### 初级项目（1-2天）
1. **CSV 处理工具**
   - 读取、过滤、转换 CSV 文件
   - 输出统计报告

2. **文件批量重命名工具**
   - 使用 `os` 和 `pathlib` 模块
   - 支持正则表达式匹配

3. **简单的 CLI 计算器**
   - 使用 `typer` 或 `argparse`
   - 支持加减乘除

### 中级项目（3-5天）
1. **RESTful API 服务** ✅ 可参考 `03-fastapi/`
   - FastAPI + SQLAlchemy
   - JWT 认证
   - CRUD 操作

2. **网页数据采集器** ✅ 可参考 `08-zaubacorp/`
   - requests + BeautifulSoup
   - 数据导出到 Excel
   - 错误重试机制

3. **定时任务调度器**
   - APScheduler
   - 任务持久化
   - 邮件通知

### 高级项目（1-2周）
1. **全栈 Web 应用**
   - FastAPI 后端
   - 前端框架对接
   - WebSocket 实时通信
   - Redis 缓存
   - Celery 异步任务

2. **分布式爬虫系统**
   - Scrapy 框架
   - RabbitMQ 任务队列 ✅ 参考 `07-queue/`
   - MongoDB 存储
   - 反爬虫策略

3. **数据分析平台**
   - Dash 可视化 ✅ 参考 `02-dash-apps/`
   - Pandas 数据处理
   - 交互式图表
   - 定时报告生成

---

## 常见陷阱

### 1. 可变默认参数
```python
# ❌ 错误 - 默认参数在函数定义时只创建一次
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - 不是期望的 [2]!

# ✅ 正确
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. 循环中的闭包
```python
# ❌ 错误
functions = []
for i in range(3):
    functions.append(lambda: i)  # 都引用同一个 i

print([f() for f in functions])  # [2, 2, 2]

# ✅ 正确
functions = []
for i in range(3):
    functions.append(lambda x=i: x)  # 立即绑定

print([f() for f in functions])  # [0, 1, 2]
```

### 3. 可变对象作为类属性
```python
# ❌ 错误
class MyClass:
    items = []  # 类属性，所有实例共享

obj1 = MyClass()
obj2 = MyClass()
obj1.items.append(1)
print(obj2.items)  # [1] - 意外共享!

# ✅ 正确
class MyClass:
    def __init__(self):
        self.items = []  # 实例属性，每个实例独立
```

### 4. 整数缓存
```python
# 小整数（-5 到 256）被缓存
a = 256
b = 256
print(a is b)  # True

c = 257
d = 257
print(c is d)  # False (在交互式环境中)

# 教训：比较值用 ==，比较身份用 is
# is 主要用于 None、True、False
```

### 5. 浮点数精度
```python
# ❌ 问题
print(0.1 + 0.2 == 0.3)  # False!

# ✅ 解决方案 1：使用 decimal
from decimal import Decimal
print(Decimal('0.1') + Decimal('0.2') == Decimal('0.3'))  # True

# ✅ 解决方案 2：容差比较
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
```

### 6. 字符串不可变
```python
# ❌ 低效
result = ""
for i in range(1000):
    result += str(i)  # 每次创建新字符串

# ✅ 高效
result = "".join(str(i) for i in range(1000))
```

### 7. 忘记 self
```python
# ❌ 错误
class MyClass:
    def method(self):
        name = "test"  # 局部变量

    def other_method(self):
        print(name)  # NameError!

# ✅ 正确
class MyClass:
    def method(self):
        self.name = "test"  # 实例属性

    def other_method(self):
        print(self.name)  # OK
```

---

## 推荐资源

### 官方文档
- [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/)
- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
- [SQLAlchemy 文档](https://www.sqlalchemy.org/)

### 书籍推荐
- 《Fluent Python》（流畅的Python）- 进阶必读
- 《Python Cookbook》- 实用技巧集合
- 《Effective Python》- 最佳实践

### 在线资源
- Real Python (realpython.com) - 高质量教程
- Python Weekly - 每周精选
- Talk Python Podcast - 播客

### 练习平台
- LeetCode - 算法练习
- HackerRank - Python 专项
- Codewars - 趣味挑战

---

## 学习检查清单

### 第一周
- [ ] 能不看文档写出基本的类和函数
- [ ] 理解列表推导式和字典推导式
- [ ] 掌握文件读写和异常处理
- [ ] 完成一个 CSV 处理项目

### 第二周
- [ ] 理解装饰器和生成器
- [ ] 能写出异步代码（async/await）
- [ ] 掌握常用标准库（os, sys, pathlib, json）
- [ ] 开发一个 CLI 工具

### 第三周
- [ ] 能用 FastAPI 开发 RESTful API
- [ ] 理解 SQLAlchemy ORM
- [ ] 掌握 RabbitMQ 队列使用
- [ ] 完成一个 Web API 项目

### 第四周
- [ ] 能独立开发爬虫
- [ ] 理解多线程和多进程
- [ ] 掌握测试框架（pytest）
- [ ] 完成一个综合项目

---

## 快速参考

### PHP vs Python 函数速查

```python
# 数组操作
array_push($arr, $item)      → arr.append(item)
array_pop($arr)              → arr.pop()
count($arr)                  → len(arr)
in_array($needle, $arr)      → needle in arr
array_keys($arr)             → list(dict.keys())
array_values($arr)           → list(dict.values())
array_merge($a1, $a2)        → a1 + a2  或  [*a1, *a2]
sort($arr)                   → arr.sort()
array_map($fn, $arr)         → [fn(x) for x in arr]
array_filter($arr, $fn)      → [x for x in arr if fn(x)]
array_reduce($arr, $fn)      → functools.reduce(fn, arr)

# 字符串操作
strlen($str)                 → len(str)
strpos($str, $sub)           → str.find(sub)
substr($str, $start, $len)   → str[start:start+len]
strtolower($str)             → str.lower()
strtoupper($str)             → str.upper()
trim($str)                   → str.strip()
explode($sep, $str)          → str.split(sep)
implode($sep, $arr)          → sep.join(arr)
str_replace($old, $new, $s)  → s.replace(old, new)

# 文件操作
file_get_contents($file)     → open(file).read()
file_put_contents($f, $d)    → open(f, 'w').write(d)
file_exists($path)           → os.path.exists(path)
is_dir($path)                → os.path.isdir(path)
mkdir($path)                 → os.mkdir(path)
unlink($file)                → os.remove(file)

# JSON
json_encode($data)           → json.dumps(data)
json_decode($json, true)     → json.loads(json)

# 时间
time()                       → time.time()
date('Y-m-d H:i:s')          → datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

---

## 结语

作为 PHP 开发者，你已经有了：
- ✅ 编程基础和算法思维
- ✅ Web 开发经验
- ✅ 数据库和 ORM 概念
- ✅ MVC 架构理解

现在只需要：
1. **适应语法差异**（1-2周）
2. **理解 Python 特色**（2-3周）
3. **实战项目积累**（持续）

**建议**：不要追求完美，边学边做，遇到问题就查文档和 Stack Overflow。Python 社区非常活跃，大部分问题都能找到答案。

**记住**：Python 的哲学是 "There should be one-- and preferably only one --obvious way to do it."（应该有一种，最好只有一种明显的方法来做某事）

祝学习顺利！🚀
