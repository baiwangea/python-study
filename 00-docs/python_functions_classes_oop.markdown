# Python 函数、类与面向对象编程实战指南

本文档基于 Python 基础知识，聚焦函数、类和面向对象编程（OOP）的详细说明与实战示例。内容包括定义、常用操作、实战代码及注意事项。假设读者有基本 Python 知识（如数据类型）。所有示例均可在 Python 3.x 中运行。

## 1. 函数（Functions）
函数是可重用代码块，用于封装逻辑。Python 函数支持位置参数、关键字参数、默认值、可变参数等。

### 1.1 函数定义与调用
- **定义**：使用 `def` 关键字。
- **参数**：
  - 位置参数：按顺序传递。
  - 关键字参数：指定参数名。
  - 默认参数：提供默认值。
  - 可变位置参数：`*args`（元组）。
  - 可变关键字参数：`**kwargs`（字典）。
- **返回**：使用 `return`，可返回多个值（实际为元组）。
- **文档字符串**：三引号描述函数。
- **注解**：类型提示，如 `def func(a: int) -> str:`。

- **示例**：
  ```python
  def greet(name: str, greeting: str = "Hello") -> str:
      """返回问候语。"""
      return f"{greeting}, {name}!"

  print(greet("Alice"))  # Hello, Alice!
  print(greet("Bob", greeting="Hi"))  # Hi, Bob!
  ```

### 1.2 可变参数
- **`*args`**：收集位置参数为元组。
- **`**kwargs`**：收集关键字参数为字典。

- **示例**：
  ```python
  def sum_numbers(*args: int) -> int:
      return sum(args)

  print(sum_numbers(1, 2, 3))  # 6

  def print_info(**kwargs):
      for key, value in kwargs.items():
          print(f"{key}: {value}")

  print_info(name="Alice", age=30)
  # name: Alice
  # age: 30
  ```

### 1.3 Lambda 函数
- 匿名函数，用于简单表达式。
- 语法：`lambda 参数: 表达式`。

- **示例**：
  ```python
  add = lambda x, y: x + y
  print(add(2, 3))  # 5

  # 与 sorted 使用
  points = [(1, 2), (3, 1), (5, 0)]
  sorted_points = sorted(points, key=lambda p: p[1])
  print(sorted_points)  # [(5, 0), (3, 1), (1, 2)]
  ```

### 1.4 装饰器（Decorators）
- 函数的函数，用于修改函数行为（如计时、日志）。
- 使用 `@decorator` 语法。

- **示例**：
  ```python
  import time

  def timer(func):
      def wrapper(*args, **kwargs):
          start = time.time()
          result = func(*args, **kwargs)
          end = time.time()
          print(f"执行时间: {end - start:.4f} 秒")
          return result
      return wrapper

  @timer
  def slow_add(a, b):
      time.sleep(1)
      return a + b

  print(slow_add(1, 2))  # 执行时间: 1.0001 秒 \n 3
  ```

### 1.5 递归函数
- 函数调用自身。
- 注意基线条件，避免无限递归。

- **示例**：
  ```python
  def factorial(n: int) -> int:
      if n <= 1:
          return 1
      return n * factorial(n - 1)

  print(factorial(5))  # 120
  ```

### 1.6 函数实战：计算器程序
- **实战代码**：
  ```python
  def calculator(operation: str, *args: float) -> float:
      """简单计算器。"""
      if operation == "add":
          return sum(args)
      elif operation == "mul":
          result = 1
          for num in args:
              result *= num
          return result
      elif operation == "div":
          if len(args) < 2:
              raise ValueError("至少两个参数")
          result = args[0]
          for num in args[1:]:
              if num == 0:
                  raise ZeroDivisionError("不能除以零")
              result /= num
          return result
      else:
          raise ValueError("无效操作")

  try:
      print(calculator("add", 1, 2, 3))  # 6
      print(calculator("mul", 2, 3, 4))  # 24
      print(calculator("div", 10, 2, 1))  # 5.0
  except (ValueError, ZeroDivisionError) as e:
      print(f"错误: {e}")
  ```

### 1.7 函数注意事项
- **作用域**：局部变量优先，`global`/`nonlocal` 修改全局/封闭变量。
- **纯函数**：无副作用，提高可测试性。
- **性能**：递归深度限 1000，避免栈溢出。
- **类型提示**：使用 `typing` 模块提升可读性。

## 2. 类（Classes）
类是自定义类型，用于封装数据和行为。

### 2.1 类定义与实例化
- **定义**：使用 `class` 关键字。
- **初始化**：`__init__` 方法。
- **属性**：实例属性（self.var）、类属性（Class.var）。
- **方法**：实例方法（带 self）、类方法（@classmethod）、静态方法（@staticmethod）。

- **示例**：
  ```python
  class Person:
      species = "Human"  # 类属性

      def __init__(self, name: str, age: int):
          self.name = name  # 实例属性
          self.age = age

      def greet(self) -> str:
          return f"Hello, I'm {self.name}."

  p = Person("Alice", 30)
  print(p.greet())  # Hello, I'm Alice.
  print(Person.species)  # Human
  ```

### 2.2 类方法与静态方法
- **类方法**：操作类属性，参数 cls。
- **静态方法**：不依赖实例/类，工具函数。

- **示例**：
  ```python
  class MathUtils:
      @classmethod
      def from_list(cls, numbers: list):
          obj = cls()
          obj.numbers = numbers
          return obj

      @staticmethod
      def add(a, b):
          return a + b

  mu = MathUtils.from_list([1, 2])
  print(mu.numbers)  # [1, 2]
  print(MathUtils.add(3, 4))  # 7
  ```

### 2.3 属性访问控制
- **私有属性**：`__var`（名称混淆）。
- **属性装饰器**：@property（getter）、@var.setter。

- **示例**：
  ```python
  class Circle:
      def __init__(self, radius: float):
          self.__radius = radius

      @property
      def radius(self) -> float:
          return self.__radius

      @radius.setter
      def radius(self, value: float):
          if value < 0:
              raise ValueError("半径不能负")
          self.__radius = value

      @property
      def area(self) -> float:
          return 3.14 * self.__radius ** 2

  c = Circle(5)
  print(c.area)  # 78.5
  c.radius = 10
  print(c.area)  # 314.0
  ```

### 2.4 特殊方法（Magic Methods）
- `__str__`：字符串表示。
- `__repr__`：调试表示。
- `__len__`：长度。
- `__getitem__`：索引访问。

- **示例**：
  ```python
  class Book:
      def __init__(self, title: str):
          self.title = title

      def __str__(self) -> str:
          return f"Book: {self.title}"

      def __repr__(self) -> str:
          return f"Book('{self.title}')"

  b = Book("Python Guide")
  print(str(b))  # Book: Python Guide
  print(repr(b))  # Book('Python Guide')
  ```

### 2.5 类实战：银行账户系统
- **实战代码**：
  ```python
  class Account:
      def __init__(self, owner: str, balance: float = 0.0):
          self.owner = owner
          self.__balance = balance

      def deposit(self, amount: float):
          if amount > 0:
              self.__balance += amount
          else:
              raise ValueError("存款金额必须正")

      def withdraw(self, amount: float):
          if 0 < amount <= self.__balance:
              self.__balance -= amount
          else:
              raise ValueError("无效取款")

      @property
      def balance(self) -> float:
          return self.__balance

  acc = Account("Alice", 100)
  acc.deposit(50)
  acc.withdraw(30)
  print(acc.balance)  # 120.0
  ```

## 3. 面向对象编程（OOP）
OOP 核心：封装、继承、多态、抽象。

### 3.1 封装（Encapsulation）
- 隐藏内部实现，使用私有属性/方法。

- **示例**：上述 Circle 类使用 `__radius` 和 property 封装。

### 3.2 继承（Inheritance）
- 子类继承父类属性/方法。
- 使用 `super()` 调用父类方法。
- 多继承：支持，但注意 MRO（方法解析顺序）。

- **示例**：
  ```python
  class Animal:
      def __init__(self, name: str):
          self.name = name

      def speak(self) -> str:
          return "未知声音"

  class Dog(Animal):
      def speak(self) -> str:
          return "汪汪!"

  class Cat(Animal):
      def speak(self) -> str:
          return "喵喵!"

  d = Dog("Buddy")
  print(d.speak())  # 汪汪!
  ```

### 3.3 多态（Polymorphism）
- 相同方法，不同类不同行为。

- **示例**：
  ```python
  animals = [Dog("Buddy"), Cat("Whiskers")]
  for animal in animals:
      print(animal.speak())
  # 汪汪!
  # 喵喵!
  ```

### 3.4 抽象类与接口
- 使用 `abc` 模块定义抽象基类（ABC）。

- **示例**：
  ```python
  from abc import ABC, abstractmethod

  class Shape(ABC):
      @abstractmethod
      def area(self) -> float:
          pass

  class Rectangle(Shape):
      def __init__(self, width: float, height: float):
          self.width = width
          self.height = height

      def area(self) -> float:
          return self.width * self.height

  r = Rectangle(4, 5)
  print(r.area())  # 20
  ```

### 3.5 OOP 实战：图形编辑器
- **实战代码**：
  ```python
  from abc import ABC, abstractmethod

  class Shape(ABC):
      @abstractmethod
      def draw(self) -> str:
          pass

      @abstractmethod
      def area(self) -> float:
          pass

  class Circle(Shape):
      def __init__(self, radius: float):
          self.radius = radius

      def draw(self) -> str:
          return "绘制圆形"

      def area(self) -> float:
          return 3.14 * self.radius ** 2

  class Square(Shape):
      def __init__(self, side: float):
          self.side = side

      def draw(self) -> str:
          return "绘制正方形"

      def area(self) -> float:
          return self.side ** 2

  shapes = [Circle(5), Square(4)]
  for shape in shapes:
      print(shape.draw(), "- 面积:", shape.area())
  # 绘制圆形 - 面积: 78.5
  # 绘制正方形 - 面积: 16
  ```

## 4. 注意事项与最佳实践
- **函数**：保持单一责任，避免全局变量。
- **类**：使用 PascalCase 命名，方法 snake_case。
- **OOP**：优先组合而非继承（Composition over Inheritance）。
- **异常处理**：在实战中捕获特定异常。
- **测试**：使用 unittest 或 pytest 测试函数/类。
- **性能**：类方法调用稍慢于函数，必要时优化。

如果需要更多示例或特定主题深入，请提供反馈！