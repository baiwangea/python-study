# Python 常见数据类型处理与转化

## 1. 常见数据类型
Python 的常见数据类型包括：
- **数值类型**：`int`（整数）、`float`（浮点数）、`complex`（复数）
- **字符串**：`str`
- **序列类型**：`list`（列表）、`tuple`（元组）、`range`
- **映射类型**：`dict`（字典）
- **集合类型**：`set`（集合）、`frozenset`（不可变集合）
- **布尔类型**：`bool`（True/False）
- **NoneType**：`None`

## 2. 各数据类型的常见操作

### 2.1 数值类型（int, float, complex）
数值类型用于表示数字，支持算术运算。`int` 无大小限制，`float` 为双精度浮点，`complex` 为复数。

- **创建**：
  - `int`：`a = 10`, `a = 0b1010`（二进制），`a = 0o12`（八进制），`a = 0xA`（十六进制）
  - `float`：`b = 3.14`, `b = 1.2e3`（科学计数法）
  - `complex`：`c = 1 + 2j`, `c = complex(1, 2)`
  - 空值：数值类型无空，但可为 0 或 0.0

- **算术运算**：
  - `+`, `-`, `*`, `/`（真除法），`//`（整除），`%`（取模），`**`（幂）
  - 对于 `complex`，支持所有运算

- **比较运算**：
  - `>`, `<`, `==`, `!=`, `>=`, `<=`（`complex` 不支持大小比较）

- **位运算（仅 int）**：
  - `&`（与），`|`（或），`^`（异或），`~`（取反），`<<`（左移），`>>`（右移）

- **内置函数与方法**：
  - `abs(x)`：绝对值（对于 complex，返回模）
  - `round(x, n)`：四舍五入
  - `divmod(a, b)`：返回 (商, 余数)
  - `pow(a, b, mod)`：a^b % mod
  - `int.bit_length()`：二进制位数
  - `float.is_integer()`：是否整数
  - `complex.real`, `complex.imag`：实部/虚部

- **成员检查与转换**：
  - `isinstance(x, (int, float, complex))`
  - 隐式转换：int + float → float

- **性能与注意**：
  - int 支持任意大数，但运算慢于 float
  - float 有精度问题（如 0.1 + 0.2 != 0.3）

- **示例**：
  ```python
  # 创建
  a = 10  # int
  b = 3.14  # float
  c = 1 + 2j  # complex

  # 算术
  print(a + b)  # 13.14
  print(a // 3)  # 3
  print(a % 3)  # 1
  print(a ** 2)  # 100
  print(c * c)  # (-3+4j)

  # 位运算
  print(bin(a))  # '0b1010'
  print(a & 3)  # 2
  print(a << 1)  # 20

  # 内置函数
  print(abs(-5))  # 5
  print(round(3.14159, 2))  # 3.14
  print(divmod(10, 3))  # (3, 1)
  print(pow(2, 3, 5))  # 3
  print(a.bit_length())  # 4
  print(b.is_integer())  # False
  print(c.real)  # 1.0

  # 精度问题
  print(0.1 + 0.2 == 0.3)  # False
  from decimal import Decimal
  print(Decimal('0.1') + Decimal('0.2') == Decimal('0.3'))  # True
  ```

### 2.2 字符串（str）
字符串是不可变的序列类型，用于表示文本，支持 Unicode。

- **创建**：
  - 单引号：`s = 'hello'`
  - 双引号：`s = "hello"`
  - 三引号：`s = """多行\n字符串"""`
  - 原始字符串：`s = r'C:\path'`（不转义）
  - 格式字符串：`s = f'value: {var}'`
  - 字节字符串：`b = b'bytes'`（但 str 是 Unicode）
  - 空字符串：`s = ''`

- **访问**：
  - 索引：`s[i]`（正负）
  - 切片：`s[i:j:k]`

- **拼接与重复**：
  - `+`：拼接
  - `*`：重复

- **常用方法**：
  - 大小写：`s.lower()`, `s.upper()`, `s.capitalize()`, `s.title()`, `s.swapcase()`
  - 去除空白：`s.strip()`, `s.lstrip()`, `s.rstrip()`
  - 替换：`s.replace(old, new, count)`
  - 分割：`s.split(sep, maxsplit)`, `s.rsplit()`, `s.partition(sep)`
  - 拼接：`sep.join(iterable)`
  - 查找：`s.find(sub)`, `s.rfind()`, `s.index(sub)`, `s.rindex()`
  - 检查：`s.startswith(prefix)`, `s.endswith(suffix)`, `s.isdigit()`, `s.isalpha()`, `s.isalnum()`, `s.isspace()`
  - 格式化：`s.format(**kwargs)`, f-strings, `%` 运算符
  - 编码：`s.encode('utf-8')`, `bytes.decode('utf-8')`

- **成员检查**：
  - `sub in s`

- **不可变性**：
  - 修改需创建新字符串

- **性能**：
  - 字符串拼接用 join() 高效

- **示例**：
  ```python
  # 创建
  s = "Hello, World!"
  multi = """Line1\nLine2"""
  raw = r"\n not escaped"
  fstr = f"Pi: {3.14:.2f}"  # 'Pi: 3.14'

  # 访问
  print(s[0])  # 'H'
  print(s[-1])  # '!'
  print(s[0:5])  # 'Hello'

  # 拼接
  print(s + "!!")  # 'Hello, World!!!'
  print(s * 2)  # 'Hello, World!Hello, World!'

  # 方法
  print(s.lower())  # 'hello, world!'
  print(s.strip("!"))  # 'Hello, World'
  print(s.replace("World", "Python"))  # 'Hello, Python!'
  print(s.split(", "))  # ['Hello', 'World!']
  print(", ".join(['a', 'b']))  # 'a, b'
  print(s.find("World"))  # 7
  print(s.startswith("Hello"))  # True
  print("123".isdigit())  # True
  print(s.format())  # 'Hello, World!'
  print("Name: {}".format("Alice"))  # 'Name: Alice'
  print("Age: %d" % 25)  # 'Age: 25'

  # 检查
  print("ell" in s)  # True

  # 编码
  encoded = s.encode('utf-8')
  print(encoded.decode('utf-8'))  # 'Hello, World!'
  ```

### 2.3 列表（list）
列表是可变的序列类型，支持异构元素。

- **创建**：
  - `lst = [1, 2, 3]`
  - 列表推导式：`lst = [x**2 for x in range(5)]`
  - 空列表：`lst = []`

- **访问**：
  - 索引：`lst[i]`（正负）
  - 切片：`lst[i:j:k]`（返回新列表）

- **修改**：
  - `lst[i] = x`
  - `lst[i:j] = iterable`（替换切片）

- **添加**：
  - `lst.append(x)`
  - `lst.extend(iterable)`
  - `lst.insert(i, x)`
  - `lst += iterable`

- **删除**：
  - `lst.pop(i)`（默认末尾）
  - `lst.remove(x)`（移除第一个匹配）
  - `del lst[i]`, `del lst[i:j]`
  - `lst.clear()`

- **排序与反转**：
  - `lst.sort(key=None, reverse=False)`（原地）
  - `sorted(lst)`（返回新列表）
  - `lst.reverse()`（原地反转）
  - `reversed(lst)`（返回迭代器）

- **查询与统计**：
  - `lst.count(x)`
  - `lst.index(x, start, end)`
  - `len(lst)`

- **成员检查**：
  - `x in lst`

- **复制**：
  - 浅拷贝：`lst.copy()`, `list(lst)`, `lst[:]`
  - 深拷贝：`import copy; copy.deepcopy(lst)`

- **性能**：
  - 追加/弹出 O(1)，插入/删除 O(n)

- **示例**：
  ```python
  # 创建
  lst = [1, 2, 3]
  comp = [x for x in range(5) if x % 2 == 0]  # [0, 2, 4]
  empty = []

  # 访问
  print(lst[1])  # 2
  print(lst[-1])  # 3
  print(lst[1:])  # [2, 3]

  # 修改
  lst[0] = 10  # [10, 2, 3]
  lst[1:3] = [20, 30]  # [10, 20, 30]

  # 添加
  lst.append(4)  # [10, 20, 30, 4]
  lst.extend([5, 6])  # [10, 20, 30, 4, 5, 6]
  lst.insert(0, 0)  # [0, 10, 20, 30, 4, 5, 6]

  # 删除
  lst.pop()  # [0, 10, 20, 30, 4, 5]
  lst.remove(10)  # [0, 20, 30, 4, 5]
  del lst[0]  # [20, 30, 4, 5]
  lst.clear()  # []

  # 排序
  lst = [3, 1, 2]
  lst.sort()  # [1, 2, 3]
  print(sorted([3, 1, 2], reverse=True))  # [3, 2, 1]
  lst.reverse()  # [3, 2, 1]

  # 查询
  print([1, 2, 1].count(1))  # 2
  print([1, 2, 3].index(2))  # 1
  print(len(lst))  # 3
  print(2 in lst)  # True

  # 复制
  lst2 = lst.copy()  # 浅拷贝
  import copy
  deep = copy.deepcopy([[1]])  # 深拷贝
  ```

### 2.4 元组（tuple）
元组是不可变的序列类型，适合存储固定数据、作为字典键或函数返回值。

- **创建**：
  - 语法：`tup = (1, 2, 3)` 或 `tup = 1, 2, 3`（省略括号）
  - 单元素元组：`tup = (1,)`（需加逗号）
  - 空元组：`tup = ()`

- **访问**：
  - 索引：`tup[i]`（支持正负索引）
  - 切片：`tup[i:j:k]`（支持步长）

- **拼接与重复**：
  - 拼接：`tup1 + tup2`
  - 重复：`tup * n`

- **查询与统计**：
  - `tup.count(x)`：统计元素 x 出现次数
  - `tup.index(x, start, end)`：查找 x 的索引（可指定范围）
  - `len(tup)`：返回元组长度

- **成员检查**：
  - `x in tup`：检查元素是否存在
  - `x not in tup`

- **解包**：
  - 解包赋值：`a, b = tup`
  - 使用 `*` 收集剩余元素：`a, *rest = tup`
  - 嵌套解包：`a, (b, c) = (1, (2, 3))`

- **比较**：
  - 支持 `==`, `!=`, `<`, `>`, `<=`, `>=`，按元素逐个比较

- **内置函数**：
  - `min(tup)`：最小值
  - `max(tup)`：最大值
  - `sum(tup)`：求和（仅限数值元素）
  - `sorted(tup)`：返回排序后的列表

- **不可变性**：
  - 元组不可修改，但若元素是可变对象（如列表），其内部内容可变

- **作为字典键**：
  - 因不可变性，元组可作为 `dict` 键或 `set` 元素

- **性能优势**：
  - 比列表占用内存少，访问速度更快

- **示例**：
  ```python
  # 创建
  tup = (1, 2, 3)
  single = (1,)  # 单元素元组
  empty = ()     # 空元组

  # 访问
  print(tup[0])  # 1
  print(tup[-1])  # 3
  print(tup[1:3])  # (2, 3)

  # 拼接与重复
  print(tup + (4, 5))  # (1, 2, 3, 4, 5)
  print(tup * 2)  # (1, 2, 3, 1, 2, 3)

  # 查询
  print(tup.count(2))  # 1
  print(tup.index(3))  # 2
  print(len(tup))  # 3
  print(2 in tup)  # True

  # 解包
  a, b, c = tup
  print(a, b, c)  # 1 2 3
  x, *rest = (1, 2, 3, 4)
  print(rest)  # [2, 3, 4]

  # 内置函数
  print(min(tup))  # 1
  print(sorted(tup, reverse=True))  # [3, 2, 1]

  # 作为字典键
  d = {(1, 2): "value"}
  print(d[(1, 2)])  # value

  # 嵌套元组
  nested = (1, (2, 3))
  x, (y, z) = nested
  print(x, y, z)  # 1 2 3

  # 可变元素
  tup_with_list = (1, [2, 3])
  tup_with_list[1].append(4)  # (1, [2, 3, 4])
  ```

### 2.5 字典（dict）
字典是可变的映射类型，使用键值对存储，支持哈希键。

- **创建**：
  - `d = {'a': 1, 'b': 2}`
  - 字典推导式：`d = {k: v**2 for k, v in zip(['a', 'b'], [1, 2])}`
  - 从序列：`dict([('a', 1), ('b', 2)])`
  - 空字典：`d = {}`

- **访问**：
  - `d[key]`（不存在抛 KeyError）
  - `d.get(key, default)`（不存在返回 default）
  - `d.setdefault(key, default)`（不存在设置并返回）

- **添加/修改**：
  - `d[key] = value`
  - `d.update(other_dict or iterable)`

- **删除**：
  - `del d[key]`
  - `d.pop(key, default)`（返回并删除）
  - `d.popitem()`（返回并删除最后一对）
  - `d.clear()`

- **遍历**：
  - `d.keys()`：键视图
  - `d.values()`：值视图
  - `d.items()`：键值对视图
  - `for k in d: ...`（遍历键）

- **查询**：
  - `key in d`
  - `len(d)`

- **复制**：
  - 浅拷贝：`d.copy()`
  - 深拷贝：`copy.deepcopy(d)`

- **有序性**：
  - Python 3.7+，插入有序

- **性能**：
  - 平均 O(1) 访问/插入/删除

- **示例**：
  ```python
  # 创建
  d = {'a': 1, 'b': 2}
  comp = {k: v for k, v in [('c', 3)]}  # {'c': 3}
  from_seq = dict([('d', 4)])  # {'d': 4}
  empty = {}

  # 访问
  print(d['a'])  # 1
  print(d.get('c', 0))  # 0
  print(d.setdefault('e', 5))  # 5, d={'a':1,'b':2,'e':5}

  # 添加/修改
  d['f'] = 6  # {'a':1,'b':2,'e':5,'f':6}
  d.update({'g':7})  # 添加

  # 删除
  del d['a']  # {'b':2,'e':5,'f':6,'g':7}
  print(d.pop('b', 0))  # 2
  print(d.popitem())  # ('g', 7)
  d.clear()  # {}

  # 遍历
  d = {'x':10, 'y':20}
  print(list(d.keys()))  # ['x', 'y']
  print(list(d.values()))  # [10, 20]
  print(list(d.items()))  # [('x',10), ('y',20)]
  for k, v in d.items(): print(k, v)  # x 10 \n y 20

  # 查询
  print('x' in d)  # True
  print(len(d))  # 2

  # 复制
  d2 = d.copy()
  ```

### 2.6 集合（set, frozenset）
集合是无序的、可变的独特元素集合；frozenset 不可变。

- **创建**：
  - `s = {1, 2, 3}`（注意 {} 是空字典）
  - 从序列：`set([1, 2, 2])` → {1,2}
  - 空集合：`s = set()`
  - frozenset：`fs = frozenset([1, 2])`

- **添加**：
  - `s.add(x)`
  - `s.update(iterable)`

- **删除**：
  - `s.remove(x)`（不存在抛 KeyError）
  - `s.discard(x)`（不存在无操作）
  - `s.pop()`（随机移除）
  - `s.clear()`

- **集合运算**：
  - 并集：`s1 | s2`, `s.union(other)`
  - 交集：`s1 & s2`, `s.intersection(other)`
  - 差集：`s1 - s2`, `s.difference(other)`
  - 对称差：`s1 ^ s2`, `s.symmetric_difference(other)`
  - 更新运算：`s |= other`, `&=` 等

- **检查**：
  - 子集：`s.issubset(other)`, `s <= other`
  - 超集：`s.issuperset(other)`, `s >= other`
  - 不相交：`s.isdisjoint(other)`

- **查询**：
  - `x in s`
  - `len(s)`

- **frozenset**：
  - 不可变，可作为键

- **性能**：
  - O(1) 成员检查

- **示例**：
  ```python
  # 创建
  s = {1, 2, 3}
  from_list = set([1, 2, 2])  # {1, 2}
  empty = set()
  fs = frozenset([1, 2])

  # 添加
  s.add(4)  # {1, 2, 3, 4}
  s.update([5, 6])  # {1,2,3,4,5,6}

  # 删除
  s.remove(1)  # {2,3,4,5,6}
  s.discard(7)  # 无操作
  s.pop()  # 随机移除，如 {3,4,5,6}
  s.clear()  # set()

  # 运算
  s1 = {1, 2, 3}
  s2 = {2, 4}
  print(s1 | s2)  # {1,2,3,4}
  print(s1 & s2)  # {2}
  print(s1 - s2)  # {1,3}
  print(s1 ^ s2)  # {1,3,4}
  s1 |= s2  # {1,2,3,4}

  # 检查
  print({1,2} <= {1,2,3})  # True
  print({1,2}.issuperset({1}))  # True
  print({1}.isdisjoint({2}))  # True

  # 查询
  print(2 in s1)  # True
  print(len(s1))  # 4

  # frozenset 作为键
  d = {fs: "value"}
  print(d[fs])  # value
  ```

### 2.7 布尔类型（bool）
布尔是 int 的子类，True=1, False=0，用于逻辑判断。

- **创建**：
  - `b = True`, `b = False`
  - 从表达式：`b = 1 > 0`

- **逻辑运算**：
  - `and`, `or`, `not`
  - 短路求值：and 从左到右，or 类似

- **转换**：
  - `bool(x)`：空/0/空容器 → False，其他 → True

- **比较**：
  - 支持所有比较运算符

- **作为数值**：
  - `True + 1` → 2

- **示例**：
  ```python
  # 创建
  t = True
  f = False
  expr = (5 > 3)  # True

  # 逻辑
  print(t and f)  # False
  print(t or f)  # True
  print(not t)  # False
  print(True and "a" or "b")  # 'a' (短路)

  # 转换
  print(bool(0))  # False
  print(bool(""))  # False
  print(bool([]))  # False
  print(bool(1))  # True
  print(bool("a"))  # True
  print(bool([0]))  # True

  # 作为数值
  print(True + False)  # 1
  print(True * 2)  # 2
  ```

### 2.8 NoneType
None 表示空值，常用于默认或缺失值。

- **创建**：
  - `x = None`

- **检查**：
  - `x is None`, `x is not None`（推荐用 is）

- **比较**：
  - `None == None` → True，但用 is 更好

- **作为默认**：
  - 函数参数默认值

- **示例**：
  ```python
  x = None
  print(x is None)  # True
  print(x == None)  # True (但不推荐)

  def func(arg=None):
      if arg is None:
          print("No arg")
  func()  # No arg
  ```

## 3. 数据类型转化
| 目标类型 | 转换方法       | 示例                              |
|----------|----------------|-----------------------------------|
| int      | `int(x)`      | `int("123")` → 123              |
| float    | `float(x)`    | `float("3.14")` → 3.14          |
| str      | `str(x)`      | `str(123)` → "123"              |
| list     | `list(x)`     | `list("abc")` → ['a', 'b', 'c'] |
| tuple    | `tuple(x)`    | `tuple([1, 2])` → (1, 2)        |
| set      | `set(x)`      | `set([1, 2, 2])` → {1, 2}       |
| dict     | `dict(x)`     | `dict([('a', 1)])` → {'a': 1}   |
| bool     | `bool(x)`     | `bool(0)` → False               |

## 4. 常见场景与技巧
- **字符串与列表**：
  ```python
  s = "a,b,c"
  lst = s.split(",")  # ['a', 'b', 'c']
  s2 = ",".join(lst)  # "a,b,c"
  ```
- **列表与集合去重**：
  ```python
  lst = [1, 2, 2, 3]
  unique = list(set(lst))  # [1, 2, 3]
  ```
- **字典与列表**：
  ```python
  d = {'a': 1, 'b': 2}
  items = list(d.items())  # [('a', 1), ('b', 2)]
  ```
- **元组解包与函数**：
  ```python
  def get_point(): return (1, 2)
  x, y = get_point()  # x=1, y=2
  ```
- **数值与字符串格式化**：
  ```python
  num = 3.14159
  print(f"{num:.2f}")  # 3.14
  ```
- **集合运算示例**：
  ```python
  odds = {1, 3, 5}
  evens = {2, 4, 6}
  print(odds.union(evens))  # {1,2,3,4,5,6}
  ```

## 5. 注意事项
- **可变性**：列表、字典、集合可变；字符串、元组、frozenset 不可变。
- **性能**：集合/字典 O(1) 查询；列表 O(n)。
- **类型检查**：用 `isinstance(x, type)` 或 `type(x)`。
- **异常处理**：
  ```python
  try:
      num = int("abc")
  except ValueError:
      print("Invalid conversion")
  ```
- **内存**：不可变类型更高效于频繁访问。