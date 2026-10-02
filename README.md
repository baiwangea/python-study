# Python 学习手册 - 总目录

本手册旨在系统性学习 Python 各类常用库，覆盖 **入门 → 进阶 → 精通** 的完整路径。  
每个库都会包含：
- **入门**：核心概念 & 基本用法  
- **进阶**：常见模式 & 性能优化  
- **精通**：源码机制 & 项目实战 Demo  

---

## 🚀 PHP 开发者快速上手指南

如果你是**十年 PHP 开发者**，想要快速掌握 Python，请从这里开始：

### 必读文档
1. **[PHP → Python 快速上手指南](00-docs/php_to_python_guide.md)** ⭐
   - PHP 和 Python 语法对比
   - 关键差异点详解
   - 思维方式转换
   - 常见陷阱避坑

2. **[PHP ↔ Python 速查表](00-docs/php_python_cheatsheet.md)** ⭐
   - 语法快速对照
   - 函数映射表
   - 代码片段对比
   - 随时查阅参考

3. **[30天学习计划](00-docs/30_day_learning_plan.md)** ⭐
   - 结构化学习路径
   - 每日任务清单
   - 实战项目指导
   - 循序渐进掌握

### 基础参考文档
- [Python 数据类型详解](00-docs/python_data_types.markdown)
- [Python 函数与面向对象](00-docs/python_functions_classes_oop.markdown)
- [Git 提交规范](00-docs/git-commit-guidelines.md)
- [Conda 环境管理](00-docs/conda_env_manual.md)

### 推荐学习顺序
```
第1周  → 基础语法 + 数据结构 + 文件操作
第2周  → 异步编程 + CLI工具 + 函数式编程
第3周  → FastAPI Web开发 + 数据库 + 队列
第4周  → 爬虫实战 + 性能优化 + 综合项目
```

---

## 零、Conda 常用操作
- **创建环境**: `conda create -n <env_name> python=3.x`
- **激活环境**: `conda activate <env_name>`
- **退出环境**: `conda deactivate`
- **查看所有环境**: `conda env list`
- **安装包**: `conda install <package_name>`
- **查看已安装的包**: `conda list`
- **删除环境**: `conda env remove -n <env_name>`

---

## 一、标准库部分
### 并发与异步
- asyncio（异步编程）
- threading（多线程）
- multiprocessing（多进程）
- concurrent.futures（任务调度）

### 文件与 IO
- os（操作系统接口）
- sys（Python 运行时环境）
- pathlib（现代路径操作）
- shutil（文件操作）
- io（流操作）
- logging（日志系统）

### 数据处理
- json（JSON 编解码）
- csv（CSV 文件处理）
- pickle（对象序列化）
- re（正则表达式）
- datetime（日期时间）
- collections（数据结构扩展）

### 网络编程
- socket（底层网络编程）
- http.server（内置 HTTP 服务器）
- urllib（网络请求）
- ssl（安全加密）

---

## 二、数据科学与数值计算
- NumPy（数组与矩阵计算）
- Pandas（数据分析）
- Matplotlib / Seaborn（数据可视化）
- SciPy（科学计算）

---

## 三、Web 开发
- Flask（轻量级 Web 框架）
- FastAPI（高性能 Web 框架）
- Requests / httpx（HTTP 客户端）
- Django（全栈框架，扩展学习）

---

## 四、数据库操作
- sqlite3（内置轻量数据库）
- SQLAlchemy（ORM 框架）
- pymysql / psycopg2（MySQL/Postgres 驱动）

---

## 五、爬虫与自动化
- BeautifulSoup（HTML 解析）
- lxml（高性能解析）
- Scrapy（爬虫框架）
- Selenium / Playwright（浏览器自动化）

---

## 六、机器学习与 AI
- scikit-learn（机器学习算法库）
- TensorFlow / PyTorch（深度学习框架）
- transformers（NLP 预训练模型）

---

## 七、测试与工具
- unittest / pytest（单元测试框架）
- argparse / click（命令行工具）
- typing（类型注解）

---

# 学习路径建议
1. **基础打牢**：标准库（文件、IO、网络、并发）  
2. **进阶拓展**：数据科学 & Web 开发  
3. **实战项目**：数据库、爬虫、自动化  
4. **高阶提升**：机器学习 & AI  
5. **工程化能力**：测试、工具、最佳实践  

---
