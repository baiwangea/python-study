# PHP ↔ Python 速查表

## 目录
- [变量和类型](#变量和类型)
- [运算符](#运算符)
- [字符串](#字符串)
- [数组列表](#数组列表)
- [控制流](#控制流)
- [函数](#函数)
- [类和对象](#类和对象)
- [文件操作](#文件操作)
- [HTTP和网络](#http和网络)
- [常用库函数](#常用库函数)

---

## 变量和类型

| PHP | Python | 说明 |
|-----|--------|------|
| `$name = "John";` | `name = "John"` | 变量声明 |
| `define('PI', 3.14);` | `PI = 3.14` | 常量 |
| `const MAX = 100;` | `MAX = 100` | 类常量 |
| `$num = 42;` | `num = 42` | 整数 |
| `$price = 9.99;` | `price = 9.99` | 浮点数 |
| `$flag = true;` | `flag = True` | 布尔值（注意大小写）|
| `$empty = null;` | `empty = None` | 空值 |
| `is_null($var)` | `var is None` | 检查空值 |
| `isset($var)` | `'var' in locals()` 或 `hasattr(obj, 'var')` | 检查变量是否存在 |
| `empty($var)` | `not var` | 检查空值 |
| `gettype($var)` | `type(var)` | 获取类型 |
| `is_int($var)` | `isinstance(var, int)` | 类型检查 |
| `(int)$var` | `int(var)` | 类型转换 |

---

## 运算符

| PHP | Python | 说明 |
|-----|--------|------|
| `$a . $b` | `a + b` | 字符串拼接 |
| `$a == $b` | `a == b` | 相等比较 |
| `$a === $b` | `a is b` (仅对象) | 严格相等 |
| `$a <> $b` | `a != b` | 不等于 |
| `$a and $b` | `a and b` | 逻辑与 |
| `$a or $b` | `a or b` | 逻辑或 |
| `!$a` | `not a` | 逻辑非 |
| `$a ? $b : $c` | `b if a else c` | 三元运算符 |
| `$a ?? $b` | `a if a is not None else b` | 空值合并 |
| `$a++` | `a += 1` | 自增（Python 没有 ++）|
| `$a .= $b` | `a += b` | 字符串追加 |
| `**` | `**` | 幂运算（两者相同）|

---

## 字符串

| PHP | Python | 说明 |
|-----|--------|------|
| `"Hello $name"` | `f"Hello {name}"` | 字符串插值 |
| `'Single quote'` | `'Single quote'` | 单引号字符串 |
| `"Double quote"` | `"Double quote"` | 双引号字符串 |
| `<<<EOT\n...\nEOT` | `"""..."""` | 多行字符串 |
| `strlen($str)` | `len(str)` | 字符串长度 |
| `strtolower($str)` | `str.lower()` | 转小写 |
| `strtoupper($str)` | `str.upper()` | 转大写 |
| `ucfirst($str)` | `str.capitalize()` | 首字母大写 |
| `trim($str)` | `str.strip()` | 去除两端空格 |
| `ltrim($str)` | `str.lstrip()` | 去除左边空格 |
| `rtrim($str)` | `str.rstrip()` | 去除右边空格 |
| `substr($str, 0, 5)` | `str[0:5]` | 截取子串 |
| `strpos($str, $sub)` | `str.find(sub)` | 查找子串位置 |
| `str_replace($old, $new, $str)` | `str.replace(old, new)` | 替换字符串 |
| `explode($sep, $str)` | `str.split(sep)` | 分割字符串 |
| `implode($sep, $arr)` | `sep.join(arr)` | 连接数组为字符串 |
| `str_repeat($str, 3)` | `str * 3` | 重复字符串 |
| `str_contains($str, $sub)` | `sub in str` | 检查包含 |
| `str_starts_with($str, $prefix)` | `str.startswith(prefix)` | 检查前缀 |
| `str_ends_with($str, $suffix)` | `str.endswith(suffix)` | 检查后缀 |
| `sprintf("%s: %d", $name, $age)` | `f"{name}: {age}"` | 格式化字符串 |
| `printf("Hello %s", $name)` | `print(f"Hello {name}")` | 格式化输出 |

**字符串格式化对比：**
```php
// PHP
sprintf("Name: %s, Age: %d", $name, $age);
sprintf("Price: %.2f", $price);
```
```python
# Python 方式 1: f-string (推荐)
f"Name: {name}, Age: {age}"
f"Price: {price:.2f}"

# 方式 2: format()
"Name: {}, Age: {}".format(name, age)
"Price: {:.2f}".format(price)

# 方式 3: % 运算符（旧式）
"Name: %s, Age: %d" % (name, age)
```

---

## 数组/列表

| PHP | Python | 说明 |
|-----|--------|------|
| `$arr = [1, 2, 3];` | `arr = [1, 2, 3]` | 索引数组/列表 |
| `$dict = ['a' => 1, 'b' => 2];` | `dict = {'a': 1, 'b': 2}` | 关联数组/字典 |
| `$arr[] = 4;` | `arr.append(4)` | 添加元素 |
| `array_push($arr, 4, 5)` | `arr.extend([4, 5])` | 添加多个元素 |
| `array_pop($arr)` | `arr.pop()` | 弹出最后元素 |
| `array_shift($arr)` | `arr.pop(0)` | 移除第一个元素 |
| `array_unshift($arr, 0)` | `arr.insert(0, 0)` | 在开头插入 |
| `count($arr)` | `len(arr)` | 数组长度 |
| `in_array($val, $arr)` | `val in arr` | 检查元素存在 |
| `array_key_exists($key, $arr)` | `key in dict` | 检查键存在 |
| `array_keys($arr)` | `list(dict.keys())` | 获取所有键 |
| `array_values($arr)` | `list(dict.values())` | 获取所有值 |
| `array_merge($a1, $a2)` | `a1 + a2` 或 `[*a1, *a2]` | 合并数组 |
| `array_slice($arr, 1, 3)` | `arr[1:4]` | 数组切片 |
| `sort($arr)` | `arr.sort()` | 排序（原地）|
| `rsort($arr)` | `arr.sort(reverse=True)` | 逆序排序 |
| `asort($arr)` | `sorted(dict.items(), key=lambda x: x[1])` | 按值排序 |
| `ksort($arr)` | `dict(sorted(dict.items()))` | 按键排序 |
| `array_reverse($arr)` | `arr[::-1]` 或 `list(reversed(arr))` | 反转数组 |
| `array_unique($arr)` | `list(set(arr))` | 去重 |
| `array_sum($arr)` | `sum(arr)` | 求和 |
| `max($arr)` | `max(arr)` | 最大值 |
| `min($arr)` | `min(arr)` | 最小值 |
| `range(1, 10)` | `list(range(1, 11))` | 生成范围 |

**高级操作对比：**
```php
// PHP - array_map
array_map(fn($x) => $x * 2, $arr);
// PHP - array_filter
array_filter($arr, fn($x) => $x > 0);
// PHP - array_reduce
array_reduce($arr, fn($carry, $x) => $carry + $x, 0);
```
```python
# Python - map (推荐用列表推导)
list(map(lambda x: x * 2, arr))
[x * 2 for x in arr]  # 推荐

# Python - filter
list(filter(lambda x: x > 0, arr))
[x for x in arr if x > 0]  # 推荐

# Python - reduce
from functools import reduce
reduce(lambda carry, x: carry + x, arr, 0)
sum(arr)  # 对于求和，直接用 sum()
```

---

## 控制流

### 条件语句
```php
// PHP
if ($x > 0) {
    echo "Positive";
} elseif ($x < 0) {
    echo "Negative";
} else {
    echo "Zero";
}

switch ($x) {
    case 1:
        echo "One";
        break;
    case 2:
        echo "Two";
        break;
    default:
        echo "Other";
}
```
```python
# Python
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

# Python 3.10+ match-case
match x:
    case 1:
        print("One")
    case 2:
        print("Two")
    case _:
        print("Other")

# 或使用字典
actions = {
    1: "One",
    2: "Two"
}
print(actions.get(x, "Other"))
```

### 循环
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

do {
    $x++;
} while ($x < 10);
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

# Python 没有 do-while，可以这样模拟
while True:
    x += 1
    if x >= 10:
        break

# 带索引的循环
for index, item in enumerate(items):
    print(f"{index}: {item}")

# 同时遍历多个列表
for a, b in zip(list1, list2):
    print(a, b)
```

---

## 函数

```php
// PHP
function greet($name, $greeting = "Hello") {
    return "$greeting, $name!";
}

// 类型提示 (PHP 7+)
function add(int $a, int $b): int {
    return $a + $b;
}

// 可变参数
function sum(...$numbers) {
    return array_sum($numbers);
}

// 匿名函数
$multiply = function($a, $b) {
    return $a * $b;
};

// 箭头函数 (PHP 7.4+)
$square = fn($x) => $x * $x;

// 引用传递
function increment(&$x) {
    $x++;
}
```
```python
# Python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# 类型提示 (Python 3.5+)
def add(a: int, b: int) -> int:
    return a + b

# 可变参数
def sum_numbers(*numbers):
    return sum(numbers)

# 关键字参数
def create_user(name, age=18, **kwargs):
    return {'name': name, 'age': age, **kwargs}

# Lambda 表达式
multiply = lambda a, b: a * b

square = lambda x: x ** 2

# Python 没有引用传递，但可以返回新值或修改可变对象
def increment(x):
    return x + 1

# 对于可变对象（如列表）
def append_item(lst, item):
    lst.append(item)  # 直接修改列表
```

**函数装饰器对比：**
```php
// PHP 8+ Attributes
#[Route("/api/users")]
function getUsers() {
    // ...
}
```
```python
# Python 装饰器
@app.route("/api/users")
def get_users():
    # ...

# 自定义装饰器
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
```

---

## 类和对象

```php
// PHP
class User {
    private $name;
    protected $age;
    public $email;
    
    public function __construct($name, $age = 18) {
        $this->name = $name;
        $this->age = $age;
    }
    
    public function getName() {
        return $this->name;
    }
    
    public function setName($name) {
        $this->name = $name;
    }
    
    public static function create($name) {
        return new self($name);
    }
    
    private function privateMethod() {
        // ...
    }
}

class Admin extends User {
    public function getRole() {
        return "admin";
    }
}

// 使用
$user = new User("Alice", 25);
echo $user->getName();
$user->email = "alice@example.com";

$admin = User::create("Bob");
```
```python
# Python
class User:
    def __init__(self, name, age=18):
        self._name = name        # 约定：受保护
        self.__secret = "xyz"    # 名称改写：私有
        self.email = None        # 公开
    
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
    
    # 属性装饰器（推荐）
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @staticmethod
    def create(name):
        return User(name)
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data.get('age', 18))
    
    def _private_method(self):
        # 约定：私有方法
        pass

class Admin(User):
    def get_role(self):
        return "admin"

# 使用
user = User("Alice", 25)
print(user.get_name())
print(user.name)  # 使用 @property
user.name = "Alice Smith"  # 使用 @setter
user.email = "alice@example.com"

admin = User.create("Bob")
admin2 = User.from_dict({'name': 'Charlie', 'age': 30})
```

**魔术方法对比：**
| PHP | Python | 说明 |
|-----|--------|------|
| `__construct()` | `__init__()` | 构造函数 |
| `__destruct()` | `__del__()` | 析构函数 |
| `__toString()` | `__str__()`, `__repr__()` | 字符串表示 |
| `__get($name)` | `__getattr__(name)` | 动态获取属性 |
| `__set($name, $value)` | `__setattr__(name, value)` | 动态设置属性 |
| `__call($name, $args)` | `__getattr__(name)` + callable | 动态调用方法 |
| `__clone()` | `__copy__()`, `__deepcopy__()` | 克隆对象 |
| `__invoke()` | `__call__()` | 对象作为函数调用 |

---

## 文件操作

| PHP | Python | 说明 |
|-----|--------|------|
| `file_get_contents($file)` | `open(file).read()` | 读取整个文件 |
| `file_put_contents($f, $data)` | `open(f, 'w').write(data)` | 写入文件 |
| `file($file)` | `open(file).readlines()` | 按行读取 |
| `fopen($file, 'r')` | `open(file, 'r')` | 打开文件 |
| `fclose($handle)` | `file.close()` | 关闭文件 |
| `fgets($handle)` | `file.readline()` | 读取一行 |
| `feof($handle)` | 迭代器自动处理 | 检查文件末尾 |
| `file_exists($path)` | `os.path.exists(path)` | 检查文件存在 |
| `is_file($path)` | `os.path.isfile(path)` | 是否是文件 |
| `is_dir($path)` | `os.path.isdir(path)` | 是否是目录 |
| `mkdir($dir)` | `os.mkdir(dir)` | 创建目录 |
| `rmdir($dir)` | `os.rmdir(dir)` | 删除目录 |
| `unlink($file)` | `os.remove(file)` | 删除文件 |
| `rename($old, $new)` | `os.rename(old, new)` | 重命名 |
| `copy($src, $dst)` | `shutil.copy(src, dst)` | 复制文件 |
| `scandir($dir)` | `os.listdir(dir)` | 列出目录 |
| `basename($path)` | `os.path.basename(path)` | 获取文件名 |
| `dirname($path)` | `os.path.dirname(path)` | 获取目录名 |
| `pathinfo($path)` | `os.path.splitext(path)` | 路径信息 |
| `glob("*.txt")` | `glob.glob("*.txt")` | 文件名匹配 |

**文件操作最佳实践：**
```php
// PHP
$handle = fopen("file.txt", "r");
try {
    while (($line = fgets($handle)) !== false) {
        echo $line;
    }
} finally {
    fclose($handle);
}
```
```python
# Python - 推荐使用 with 语句（自动关闭）
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# 读取整个文件
with open("file.txt", "r") as f:
    content = f.read()

# 写入文件
with open("file.txt", "w") as f:
    f.write("Hello, World!")

# 追加文件
with open("file.txt", "a") as f:
    f.write("Appended text\n")

# 二进制模式
with open("image.png", "rb") as f:
    data = f.read()
```

---

## HTTP 和网络

```php
// PHP - cURL
$ch = curl_init("https://api.example.com/users");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

// PHP - file_get_contents
$data = file_get_contents("https://api.example.com/users");

// PHP - Guzzle (推荐)
$client = new \GuzzleHttp\Client();
$response = $client->get('https://api.example.com/users');
$body = $response->getBody();
```
```python
# Python - requests (最常用)
import requests

# GET 请求
response = requests.get("https://api.example.com/users")
data = response.json()

# POST 请求
response = requests.post(
    "https://api.example.com/users",
    json={"name": "Alice"},
    headers={"Authorization": "Bearer token"}
)

# 带参数
response = requests.get(
    "https://api.example.com/users",
    params={"page": 1, "limit": 10}
)

# Python - httpx (支持异步)
import httpx

# 同步
response = httpx.get("https://api.example.com/users")

# 异步
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
```

---

## 常用库函数

### 日期和时间
| PHP | Python | 说明 |
|-----|--------|------|
| `time()` | `time.time()` | 当前时间戳 |
| `date('Y-m-d')` | `datetime.now().strftime('%Y-%m-%d')` | 格式化日期 |
| `strtotime($str)` | `datetime.strptime(str, fmt).timestamp()` | 解析日期 |
| `mktime()` | `datetime(y, m, d).timestamp()` | 创建时间戳 |
| `sleep(3)` | `time.sleep(3)` | 休眠 |

```python
# Python datetime 模块
from datetime import datetime, timedelta

# 当前时间
now = datetime.now()
print(now.strftime('%Y-%m-%d %H:%M:%S'))

# 时间计算
tomorrow = now + timedelta(days=1)
week_ago = now - timedelta(weeks=1)

# 解析字符串
dt = datetime.strptime('2024-01-01', '%Y-%m-%d')
```

### JSON
| PHP | Python | 说明 |
|-----|--------|------|
| `json_encode($data)` | `json.dumps(data)` | 编码 JSON |
| `json_decode($json, true)` | `json.loads(json)` | 解码 JSON |
| `json_last_error()` | try/except | 错误处理 |

```python
import json

# 编码
data = {'name': 'Alice', 'age': 25}
json_str = json.dumps(data)
json_pretty = json.dumps(data, indent=2)

# 解码
parsed = json.loads(json_str)

# 文件操作
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

with open('data.json', 'r') as f:
    loaded = json.load(f)
```

### 数学
| PHP | Python | 说明 |
|-----|--------|------|
| `abs($x)` | `abs(x)` | 绝对值 |
| `ceil($x)` | `math.ceil(x)` | 向上取整 |
| `floor($x)` | `math.floor(x)` | 向下取整 |
| `round($x)` | `round(x)` | 四舍五入 |
| `pow($x, $y)` | `x ** y` 或 `pow(x, y)` | 幂运算 |
| `sqrt($x)` | `math.sqrt(x)` | 平方根 |
| `rand($min, $max)` | `random.randint(min, max)` | 随机整数 |
| `mt_rand()` | `random.random()` | 随机浮点数 |
| `pi()` | `math.pi` | 圆周率 |

### 正则表达式
| PHP | Python | 说明 |
|-----|--------|------|
| `preg_match($pattern, $str)` | `re.search(pattern, str)` | 查找匹配 |
| `preg_match_all($pattern, $str, $m)` | `re.findall(pattern, str)` | 查找所有 |
| `preg_replace($pattern, $repl, $str)` | `re.sub(pattern, repl, str)` | 替换 |
| `preg_split($pattern, $str)` | `re.split(pattern, str)` | 分割 |

```python
import re

# 查找
match = re.search(r'\d+', 'Price: 123')
if match:
    print(match.group())  # '123'

# 查找所有
numbers = re.findall(r'\d+', 'a1b2c3')  # ['1', '2', '3']

# 替换
result = re.sub(r'\d+', 'X', 'a1b2c3')  # 'aXbXcX'

# 分割
parts = re.split(r'\s+', 'a  b    c')  # ['a', 'b', 'c']
```

---

## 快速记忆技巧

1. **变量名**：PHP 的 `$` 前缀在 Python 中直接去掉
2. **字符串拼接**：`.` → `+` 或 f-string
3. **数组**：`$arr[]` → `arr.append()`
4. **关联数组**：`['key' => 'value']` → `{'key': 'value'}`
5. **代码块**：花括号 `{}` → 冒号 `:` + 缩进
6. **对象访问**：`->` → `.`
7. **静态调用**：`::` → `.`
8. **类型**：`null` → `None`, `true/false` → `True/False`
9. **打印**：`echo`/`print` → `print()`
10. **长度计数**：`count()`/`strlen()` → `len()`

---

## 实用代码片段

### 读取配置文件
```php
// PHP
$config = parse_ini_file('config.ini');
// 或
$config = json_decode(file_get_contents('config.json'), true);
```
```python
# Python - INI
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
value = config['section']['key']

# Python - JSON
import json
with open('config.json') as f:
    config = json.load(f)

# Python - YAML (需要 pyyaml)
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Python - .env (需要 python-dotenv)
from dotenv import load_dotenv
import os
load_dotenv()
db_host = os.getenv('DB_HOST')
```

### 数据库操作
```php
// PHP - PDO
$pdo = new PDO("mysql:host=localhost;dbname=test", $user, $pass);
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$id]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
```
```python
# Python - sqlite3
import sqlite3
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
user = cursor.fetchone()
conn.close()

# Python - SQLAlchemy (ORM, 类似 Eloquent)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=engine)
session = Session()

user = session.query(User).filter_by(id=1).first()
```

### 发送邮件
```php
// PHP
mail($to, $subject, $message, $headers);

// 或使用 PHPMailer
$mail = new PHPMailer();
$mail->setFrom('from@example.com');
$mail->addAddress('to@example.com');
$mail->Subject = 'Subject';
$mail->Body = 'Message';
$mail->send();
```
```python
# Python - smtplib
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['From'] = 'from@example.com'
msg['To'] = 'to@example.com'
msg['Subject'] = 'Subject'
msg.set_content('Message')

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login('user', 'pass')
    smtp.send_message(msg)
```

---

这份速查表涵盖了从 PHP 到 Python 最常用的语法对照。建议打印或保存，随时参考！
