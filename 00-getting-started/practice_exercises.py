#!/usr/bin/env python3
"""
PHP 开发者的 Python 练习题

用法：
    1. 逐个把函数体里的 `raise NotImplementedError` 替换成你的实现
    2. 随时运行 `python3 practice_exercises.py` 查看判分结果
    3. 全绿后再看文末的「参考答案」区块

判分器只调用公开函数，不检查写法，一题可以有多种解法。
"""

# ============================================
# 第 1 组：变量与数据类型
# ============================================


def parse_csv_numbers(text):
    """把 "1,2,3,4,5" 这样的字符串转成整数列表。

    PHP:  array_map('intval', explode(',', $text))
    期望: parse_csv_numbers("1,2,3") == [1, 2, 3]
    """
    raise NotImplementedError


def sum_csv_numbers(text):
    """接上一题：把逗号分隔的数字字符串求和。

    PHP:  array_sum(array_map('intval', explode(',', $text)))
    期望: sum_csv_numbers("1,2,3,4,5") == 15
    """
    raise NotImplementedError


def safe_get(data, *keys, default=None):
    """安全读取嵌套字典，路径不存在时返回 default。

    PHP:  $data['user']['profile']['name'] ?? 'unknown'
          （PHP 里多级 ?? 要写三遍，Python 用循环或 functools.reduce）
    期望: safe_get({"a": {"b": 1}}, "a", "b") == 1
          safe_get({"a": {"b": 1}}, "a", "x", default=-1) == -1
    """
    raise NotImplementedError


def merge_defaults(config, defaults):
    """用 defaults 补齐 config 里缺失的键，但不能修改 defaults 本身。

    PHP:  $config += $defaults
    期望: merge_defaults({"a": 1}, {"a": 9, "b": 2}) == {"a": 1, "b": 2}
    提示: 字典合并有 `{**a, **b}` 和 `dict | dict` 两种写法，注意谁覆盖谁。
    """
    raise NotImplementedError


# ============================================
# 第 2 组：控制流
# ============================================


def fizzbuzz(n):
    """返回 1..n 的 FizzBuzz 字符串列表。

    规则：3 的倍数 "Fizz"，5 的倍数 "Buzz"，同时是 3 和 5 的倍数 "FizzBuzz"，
          其它是数字本身的字符串。
    期望: fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
    提示: 先判断 15，或者用 f-string 拼接后判空。
    """
    raise NotImplementedError


def group_by(items, key_func):
    """把列表按 key_func 的返回值分组。

    PHP:  array_reduce() 手工攒，或 Laravel 的 ->groupBy()
    期望: group_by([1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}
    提示: collections.defaultdict(list) 可以省掉「键不存在先初始化」这一步。
    """
    raise NotImplementedError


def top_n(scores, n):
    """按分值降序返回前 n 个学生姓名，分值相同按姓名字典序。

    期望: top_n({"a": 90, "b": 95, "c": 90}, 2) == ["b", "a"]
    提示: sorted() 的 key 可以是返回元组的 lambda，reverse=True 时次级排序也会反向，
          必要时对姓名取反或用两次排序。
    """
    raise NotImplementedError


# ============================================
# 第 3 组：函数
# ============================================


def calculator(op, *numbers):
    """可变参数计算器："+" 求和，"*" 求积，"-" 从左到右减，"/" 从左到右除。

    期望: calculator("+", 1, 2, 3) == 6
          calculator("*", 2, 3, 4) == 24
          calculator("-", 10, 3) == 7
    提示: math.fsum / functools.reduce 都能用；未知 op 抛 ValueError。
    """
    raise NotImplementedError


def apply_if(value, *conditions):
    """依次套用条件函数，第一个为真的条件决定结果（类似 PHP 的 early return 链）。

    期望: apply_if(10, lambda v: v > 100 and "大", lambda v: v > 5 and "中") == "中"
    说明: 条件函数返回假值就跳过，返回真值则直接返回该值。
    """
    raise NotImplementedError


def memoize(func):
    """实现一个带缓存的装饰器（不用 functools）。

    PHP:  静态变量缓存，或框架里的 memoize helper
    期望: 被装饰函数对同一参数只真正计算一次
    提示: 装饰器要保留原函数名（functools.wraps），缓存 key 用 (args, kwargs)。
    """
    raise NotImplementedError


# ============================================
# 第 4 组：类与面向对象
# ============================================


class Counter:
    """线程无关的简单计数器。

    要求:
      - __init__(start=0) 设置初始值
      - increment() 加一并返回新值
      - reset() 归零
      - __str__() 返回 f"Counter({value})"
      - __eq__() 让两个 Counter 按 value 比较
    期望: c = Counter(5) -> str(c) == "Counter(5)"
          c.increment() == 6 且之后 str(c) == "Counter(6)"
    提示: __eq__ 返回 NotImplemented 让 Python 走默认比较，而不是返回 False。
    """

    def __init__(self, start=0):
        raise NotImplementedError


class Account:
    """银行账户：余额不可直接改写，只能通过 deposit / withdraw。

    要求:
      - balance 属性用私有约定（_balance）
      - withdraw 金额超过余额时抛 ValueError("insufficient funds")
      - 提供 classmethod from_cents(cents) 构造（100 分 = 1 元）
    期望: Account(10).withdraw(20) 抛 ValueError
    提示: @property 返回副本可以防止外部篡改。
    """

    def __init__(self, balance=0):
        raise NotImplementedError


class Animal:
    """基类，子类实现 sound()。

    要求:
      - Animal.sound() 抛 NotImplementedError
      - speak() 返回 f"{self.__class__.__name__} says {self.sound()}"
      - 定义 Dog("Woof") 和 Cat("Meow") 两个子类
    期望: Dog().speak() == "Dog says Woof"
    提示: 这就是「鸭子类型」+ 多态，PHP 用 interface + abstract class 表达同一件事。
    """

    def sound(self):
        raise NotImplementedError


# ============================================
# 判分器
# ============================================

PENDING = object()


class InsufficientFunds(ValueError):
    """Account.withdraw 使用的异常类型（判分器只要求它是 ValueError 的子类）"""


EXERCISES = [
    ("1.1 parse_csv_numbers", lambda: _call("parse_csv_numbers", "7,8,9") == [7, 8, 9]),
    ("1.2 sum_csv_numbers", lambda: _call("sum_csv_numbers", "1,2,3,4,5") == 15),
    ("1.3 safe_get", lambda: _check_safe_get()),
    ("1.4 merge_defaults", lambda: _check_merge_defaults()),
    ("2.1 fizzbuzz", lambda: _call("fizzbuzz", 15)[-1] == "FizzBuzz"
                              and _call("fizzbuzz", 5) == ["1", "2", "Fizz", "4", "Buzz"]),
    ("2.2 group_by", lambda: _call("group_by", [1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}),
    ("2.3 top_n", lambda: _call("top_n", {"a": 90, "b": 95, "c": 90}, 2) == ["b", "a"]),
    ("3.1 calculator", lambda: _check_calculator()),
    ("3.2 apply_if", lambda: _call("apply_if", 10, lambda v: v > 100 and "大",
                                   lambda v: v > 5 and "中") == "中"),
    ("3.3 memoize", lambda: _check_memoize()),
    ("4.1 Counter", lambda: _check_counter()),
    ("4.2 Account", lambda: _check_account()),
    ("4.3 Animal/Dog/Cat", lambda: _check_animal()),
]


def _call(name, *args, **kwargs):
    """按名字调用当前模块里的练习函数；未实现时 NotImplementedError 直接冒泡，由 verify 判为「未实现」"""
    return globals()[name](*args, **kwargs)


def _check_safe_get():
    data = {"user": {"profile": {"name": "Alice"}}}
    if _call("safe_get", data, "user", "profile", "name") != "Alice":
        return False
    return _call("safe_get", data, "user", "missing", default="unknown") == "unknown"


def _check_merge_defaults():
    defaults = {"a": 9, "b": 2}
    result = _call("merge_defaults", {"a": 1}, defaults)
    return result == {"a": 1, "b": 2} and defaults == {"a": 9, "b": 2}


def _check_calculator():
    return (_call("calculator", "+", 1, 2, 3) == 6
            and _call("calculator", "*", 2, 3, 4) == 24
            and _call("calculator", "-", 10, 3) == 7)


def _check_memoize():
    calls = []

    @globals()["memoize"]
    def slow_add(a, b):
        calls.append((a, b))
        return a + b

    if slow_add(1, 2) != 3 or slow_add(1, 2) != 3:
        return False
    return len(calls) == 1


def _check_counter():
    counter = globals()["Counter"](5)
    if str(counter) != "Counter(5)":
        return False
    if counter.increment() != 6:
        return False
    if str(counter) != "Counter(6)":
        return False
    counter.reset()
    return counter == globals()["Counter"](0)


def _check_account():
    account = globals()["Account"](10)
    try:
        account.withdraw(20)
        return False
    except ValueError:
        pass
    account.deposit(5)
    built = globals()["Account"].from_cents(1050)
    return account.balance == 15 and built.balance == 10.5


def _check_animal():
    dog = globals().get("Dog")
    cat = globals().get("Cat")
    if dog is None or cat is None:
        raise NotImplementedError("请先定义 Dog / Cat 子类")
    return dog().speak() == "Dog says Woof" and cat().speak() == "Cat says Meow"


def verify():
    print("=" * 60)
    print("练习题判分结果")
    print("=" * 60)

    passed = 0
    for title, check in EXERCISES:
        try:
            ok = check()
        except NotImplementedError:
            ok = PENDING
        except Exception as exc:
            print(f"  ✗ {title:<24} 运行报错: {type(exc).__name__}: {exc}")
            continue

        if ok is PENDING:
            print(f"  · {title:<24} 未实现")
        elif ok:
            print(f"  ✓ {title:<24} 通过")
            passed += 1
        else:
            print(f"  ✗ {title:<24} 结果不符")

    print("-" * 60)
    print(f"  通过 {passed}/{len(EXERCISES)}")
    if passed < len(EXERCISES):
        print("  继续加油：从上到下依次实现，每改一题就跑一次本文件")
    else:
        print("  全部通过！下一步去 00-docs/30_day_learning_plan.md 的 Day 4")
    return passed


if __name__ == "__main__":
    verify()


# ============================================
# 参考答案（先自己写完再看）
# ============================================
#
# def parse_csv_numbers(text):
#     return [int(x) for x in text.split(",")]
#
# def sum_csv_numbers(text):
#     return sum(parse_csv_numbers(text))
#
# def safe_get(data, *keys, default=None):
#     current = data
#     for key in keys:
#         if not isinstance(current, dict) or key not in current:
#             return default
#         current = current[key]
#     return current
#
# def merge_defaults(config, defaults):
#     return {**defaults, **config}          # config 在后，优先级更高
#
# def fizzbuzz(n):
#     out = []
#     for i in range(1, n + 1):
#         s = ("Fizz" if i % 3 == 0 else "") + ("Buzz" if i % 5 == 0 else "")
#         out.append(s or str(i))
#     return out
#
# def group_by(items, key_func):
#     from collections import defaultdict
#     grouped = defaultdict(list)
#     for item in items:
#         grouped[key_func(item)].append(item)
#     return dict(grouped)
#
# def top_n(scores, n):
#     ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
#     return [name for name, _ in ranked[:n]]
#
# def calculator(op, *numbers):
#     from functools import reduce
#     import operator
#     ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}
#     if op not in ops:
#         raise ValueError(f"未知运算符: {op}")
#     return reduce(ops[op], numbers)
#
# def apply_if(value, *conditions):
#     for condition in conditions:
#         result = condition(value)
#         if result:
#             return result
#     return None
#
# def memoize(func):
#     import functools
#     cache = {}
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         key = (args, tuple(sorted(kwargs.items())))
#         if key not in cache:
#             cache[key] = func(*args, **kwargs)
#         return cache[key]
#     return wrapper
#
# class Counter:
#     def __init__(self, start=0):
#         self.value = start
#     def increment(self):
#         self.value += 1
#         return self.value
#     def reset(self):
#         self.value = 0
#     def __str__(self):
#         return f"Counter({self.value})"
#     def __eq__(self, other):
#         if not isinstance(other, Counter):
#             return NotImplemented
#         return self.value == other.value
#
# class Account:
#     def __init__(self, balance=0):
#         self._balance = balance
#     @property
#     def balance(self):
#         return self._balance
#     def deposit(self, amount):
#         self._balance += amount
#         return self._balance
#     def withdraw(self, amount):
#         if amount > self._balance:
#             raise ValueError("insufficient funds")
#         self._balance -= amount
#         return self._balance
#     @classmethod
#     def from_cents(cls, cents):
#         return cls(cents / 100)
#
# class Animal:
#     def speak(self):                      # 补在基类里，子类自动继承
#         return f"{self.__class__.__name__} says {self.sound()}"
#
# class Dog(Animal):
#     def sound(self):
#         return "Woof"
#
# class Cat(Animal):
#     def sound(self):
#         return "Meow"
