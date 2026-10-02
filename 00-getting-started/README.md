# 快速开始 - PHP 开发者的 Python 第一课

## 🎯 目标
5分钟快速体验 Python，对比 PHP 理解核心差异。

## 📁 文件说明
- `hello_python.py` - 核心语法对比示例
- `practice_exercises.py` - 练习题（待完成）

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

## 📚 接下来做什么？

### 新手路径
1. ✅ 运行 `hello_python.py` 
2. 📖 阅读 `00-docs/php_python_cheatsheet.md`（速查表）
3. 📖 阅读 `00-docs/php_to_python_guide.md`（完整指南）
4. 📅 跟随 `00-docs/30_day_learning_plan.md`（30天计划）

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

## 🎓 练习题

完成 `practice_exercises.py` 中的练习：

1. **变量和类型转换**
   - 字符串转整数
   - 列表操作
   - 字典操作

2. **控制流**
   - FizzBuzz 问题
   - 循环遍历

3. **函数**
   - 计算器函数
   - 可变参数

4. **类**
   - 创建一个简单的类
   - 使用继承

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
