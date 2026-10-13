# 快速开始 - PHP 开发者的 Python 第一课

## 🎯 目标
5分钟快速体验 Python，对比 PHP 理解核心差异。

## 📁 文件说明
- `hello_python.py` - 核心语法对比示例（直接运行看输出）
- `practice_exercises.py` - 13 道练习题 + **自动判分器**，实现一题跑一次即可自查

## 🚀 快速开始

### 1. 检查 Python 环境
```bash
python3 --version
# 应该显示 Python 3.x.x
```

### 2. 运行第一个程序
```bash
cd 00-getting-started
python3 hello_python.py
```

### 3. 理解输出
程序会演示：
- ✅ 变量和数据类型
- ✅ 函数定义
- ✅ 列表推导式
- ✅ 类和对象
- ✅ 装饰器
- ✅ 生成器

### 4. 做练习并自动判分
```bash
python3 practice_exercises.py
```
把每个函数里的 `raise NotImplementedError` 换成你的实现，**每改一题就跑一次**，
判分器会打印 `✓ 通过 / ✗ 结果不符 / · 未实现`。全部 13 题绿了再看文末的参考答案。

## 📚 接下来做什么？

### 新手路径
1. ✅ 运行 `hello_python.py`
2. ✍️ 做完 `practice_exercises.py`（13 题，跑一次就知道过没过）
3. 📖 阅读 `00-docs/php_python_cheatsheet.md`（速查表）
4. 📖 阅读 `00-docs/php_to_python_guide.md`（完整指南）
5. 📅 跟随 `00-docs/30_day_learning_plan.md`（30天计划）

### 快速实战
直接跳到现有项目：
- `01-asyncio/` - 异步编程
- `03-fastapi/` - Web API 开发
- `05-typer/` - CLI 工具
- `07-queue/` - 消息队列
- `08-zaubacorp/` - 爬虫实战

## 💡 学习建议

### 从 PHP 到 Python 的思维转变

#### 1. 缩进即语法
```python
# Python - 缩进决定代码块
if True:
    print("Indented")
print("Outside")
```

#### 2. 一切皆对象
```python
# 函数也是对象
def greet():
    return "Hello"

my_func = greet  # 可以赋值
```

#### 3. 鸭子类型
```python
# 不关心类型，关心行为
def make_sound(animal):
    animal.sound()  # 只要有 sound() 方法即可
```

### PHP vs Python 核心对照

| PHP | Python | 说明 |
|-----|--------|------|
| `$var = 10;` | `var = 10` | 变量 |
| `echo $var;` | `print(var)` | 输出 |
| `$arr = [1, 2];` | `arr = [1, 2]` | 列表 |
| `$dict = ['a' => 1];` | `dict = {'a': 1}` | 字典 |
| `if ($x) { }` | `if x:` | 条件 |
| `function fn() { }` | `def fn():` | 函数 |
| `class User { }` | `class User:` | 类 |
| `null` | `None` | 空值 |
| `true` / `false` | `True` / `False` | 布尔 |

## 🎓 练习题（`practice_exercises.py`，13 题）

| # | 题目 | 考点 | PHP 里你熟悉的写法 |
|---|------|------|-------------------|
| 1.1 | `parse_csv_numbers` | split + 列表推导式 | `array_map('intval', explode())` |
| 1.2 | `sum_csv_numbers` | 内置聚合 | `array_sum()` |
| 1.3 | `safe_get` | 嵌套字典、`*args`、关键字默认值 | 多级 `??` |
| 1.4 | `merge_defaults` | `{**a, **b}` 与「不可修改入参」 | `$config += $defaults` |
| 2.1 | `fizzbuzz` | 控制流、f-string | 经典 if/elseif |
| 2.2 | `group_by` | `defaultdict`、传函数作参数 | `array_reduce` / Laravel `groupBy` |
| 2.3 | `top_n` | `sorted(key=)` 元组排序 | `usort` 自定义比较 |
| 3.1 | `calculator` | `*numbers` 可变参数、`reduce` | 可变参数 + 分发 |
| 3.2 | `apply_if` | 一等函数、短路 | early return 链 |
| 3.3 | `memoize` | **手写装饰器** + `functools.wraps` | 闭包缓存 / 静态变量 |
| 4.1 | `Counter` | `__str__` / `__eq__` / `NotImplemented` | `__toString` |
| 4.2 | `Account` | `@property`、`@classmethod`、自定义异常 | 构造器 + 静态方法 |
| 4.3 | `Animal/Dog/Cat` | 继承与多态 | `abstract class` / `interface` |

判分器只调用公开函数、不检查写法，一题可以有多种解法。

## 📖 参考资源

### 官方文档
- [Python 官方教程（中文）](https://docs.python.org/zh-cn/3/tutorial/)
- [Python 标准库](https://docs.python.org/zh-cn/3/library/)

### 推荐阅读
- `00-docs/python_data_types.markdown` - 数据类型详解
- `00-docs/python_functions_classes_oop.markdown` - 函数和OOP

### 互动学习
- [Python Tutor](http://pythontutor.com/) - 可视化代码执行
- [LeetCode](https://leetcode.com/) - 算法练习

## ❓ 常见问题

### Q: Python 2 还是 Python 3？
A: 一定用 Python 3.9+，Python 2 已经停止维护。

### Q: 需要 IDE 吗？
A: 推荐 VS Code + Python 扩展，或 PyCharm。

### Q: 如何管理依赖？
A: 使用 `conda` 或 `venv` 创建虚拟环境。

### Q: 缩进用 Tab 还是空格？
A: 统一使用 4 个空格，不要混用。

### Q: 如何调试？
A: 使用 `print()` 或 IDE 的断点调试功能。

## 🚧 下一步

完成这个快速入门后：

1. **第一周**: 基础语法（Day 1-7）
   - 数据类型和控制流
   - 函数和类
   - 文件操作

2. **第二周**: 进阶特性（Day 8-14）
   - 异步编程
   - CLI 工具
   - 装饰器和生成器

3. **第三周**: Web 开发（Day 15-21）
   - FastAPI
   - 数据库
   - 消息队列

4. **第四周**: 实战项目（Day 22-30）
   - 爬虫
   - 综合应用

## 📞 获取帮助

- 查看项目 README.md
- 阅读各目录的 README
- 搜索 Stack Overflow
- 查看官方文档

---

**准备好了吗？运行 `hello_python.py` 开始你的 Python 之旅！** 🚀
