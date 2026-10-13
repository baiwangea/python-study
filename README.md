# Python 学习手册 - 总目录

本手册旨在系统性学习 Python 各类常用库，覆盖 **入门 → 进阶 → 精通** 的完整路径。
每个库都会包含：
- **入门**：核心概念 & 基本用法
- **进阶**：常见模式 & 性能优化
- **精通**：源码机制 & 项目实战 Demo

> 下面的清单是**学习目标**，不是完成度声明。已落地的内容以「📂 目录索引」为准。

---

## 📂 目录索引（当前实际内容）

| 目录 | 内容 | 状态 |
|------|------|------|
| `00-docs/` | PHP→Python 指南、速查表、30 天计划、并发完全指南、数据类型、函数与 OOP、conda、git 规范 | ✅ 完整 |
| `00-getting-started/` | `hello_python.py` 语法对照 + `practice_exercises.py` 13 题自动判分 | ✅ 完整 |
| `01-asyncio/` | `test.py` 入门片段 + 421 行 README 讲解 | 🟡 代码偏少 |
| `02-dash-apps/` | Plotly Dash 仪表盘 | 🟡 单文件示例 |
| `03-fastapi/` | 分层骨架：core / models / schemas / api/v1 / tests | 🟡 结构完整、实现偏薄 |
| `04-rusty_req/` | rusty_req（Rust 加速的 requests 替代）4 个测试 | 🟡 单点验证 |
| `05-typer/` | Typer CLI | 🔴 仅 10 行片段 |
| `06-telegram_bot/` | Excel 读数据 → Telegram 推送 | ✅ 可运行 |
| `07-queue/` | RabbitMQ：基础 / 延迟交换机 / TTL + DLX 死信 | ✅ 完整 |
| `08-zaubacorp/` | 真实爬虫：断点续爬 + Excel 产出 | ✅ 完整 |
| `09-works/` | 占位 | 🔴 空 |
| `10-robyn/` | **工程化范本**：Robyn + SQLAlchemy + Alembic + Docker + CI + pytest + pre-commit | ✅ 最完整 |
| `11-crc/` | CRC 校验小工具 | 🟡 单文件 |
| `12-excel/` | Excel 驱动的 API 客户端（config/models/api/utils 分层 + 装饰器 + 日志） | ✅ 完整 |
| `13-concurrency/` | 多线程 / 多进程 / 异步 8 个递进示例 + 竞态条件演示 | ✅ 完整 |

**新手推荐顺序**：`00-getting-started` → `00-docs` 三份必读 → `13-concurrency` → `03-fastapi` → `10-robyn` → `12-excel`

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
- [Python 并发编程完全指南](00-docs/python_concurrency_guide.md)（配 `13-concurrency/` 代码）
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

## 🛠 环境准备

仓库**没有根级依赖清单**，每个编号目录自带 `requirements.txt`，按需安装：

```bash
# 方式 A：venv（标准库 + 单目录依赖，推荐）
cd 13-concurrency
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 06_asyncio_advanced.py

# 方式 B：conda（详见 00-docs/conda_env_manual.md）
conda create -n python-study python=3.13 && conda activate python-study
```

已验证可跑的目录：`00-getting-started`、`13-concurrency`（仅标准库；`06`/`07` 需要 `aiohttp`、`requests`）。
本机若无 conda，用 venv 即可，两条路径文档里都给了。

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
- ✅ asyncio（异步编程）→ `01-asyncio/`、`13-concurrency/05、06`
- ✅ threading（多线程）→ `13-concurrency/01、02、race_condition_*`
- ✅ multiprocessing（多进程）→ `13-concurrency/03、04`
- ✅ concurrent.futures（任务调度）→ `13-concurrency/02、04、08`
- ⬜ socket（底层网络编程）

### 文件与 IO
- ✅ os（操作系统接口）→ `13-concurrency/08`（原子写 + fsync）
- ⬜ sys（Python 运行时环境）
- ✅ pathlib（现代路径操作）→ `13-concurrency/08`
- ⬜ shutil（文件操作）
- ⬜ io（流操作）
- ✅ logging（日志系统）→ `13-concurrency/08` 场景 3、`12-excel/utils/logger.py`

### 数据处理
- ✅ json（JSON 编解码）→ `13-concurrency/06`（checkpoint / JSONL）
- ⬜ csv（CSV 文件处理）
- ⬜ pickle（对象序列化）→ 仅在 `13-concurrency/04` 第 9 节讲限制
- ⬜ re（正则表达式）
- ⬜ datetime（日期时间）
- ✅ collections（数据结构扩展）→ `13-concurrency/08`、`00-getting-started` 练习 2.2

### 网络编程
- ⬜ socket（底层网络编程）
- ⬜ http.server（内置 HTTP 服务器）→ `13-concurrency/06` 用作离线被测服务
- ✅ urllib（网络请求）→ `13-concurrency/06` 服务端解析
- ⬜ ssl（安全加密）

---

## 二、数据科学与数值计算
- ⬜ NumPy（数组与矩阵计算）
- ⬜ Pandas（数据分析）
- 🟡 Matplotlib / Seaborn（数据可视化）→ `02-dash-apps/` 走的是 Plotly 路线
- ⬜ SciPy（科学计算）

---

## 三、Web 开发
- ⬜ Flask（轻量级 Web 框架）
- ✅ FastAPI（高性能 Web 框架）→ `03-fastapi/`
- ✅ Robyn（Rust 异步框架）→ `10-robyn/`（本仓库工程化最完整的样例）
- ✅ Requests / httpx / aiohttp / rusty_req → `04-rusty_req/`、`07`、`13-concurrency/06、07`
- ⬜ Django（全栈框架，扩展学习）

---

## 四、数据库操作
- ✅ sqlite3（内置轻量数据库）→ `03-fastapi/test.db`
- ✅ SQLAlchemy（ORM 框架）→ `03-fastapi/app/core`、`10-robyn/app`
- 🟡 pymysql / psycopg2（MySQL/Postgres 驱动）→ `10-robyn/` 走 PostgreSQL + Alembic

---

## 五、爬虫与自动化
- ✅ 实战爬虫 → `08-zaubacorp/`（断点续爬 + Excel 落盘）
- ⬜ BeautifulSoup（HTML 解析）
- ⬜ lxml（高性能解析）
- ⬜ Scrapy（爬虫框架）
- ⬜ Selenium / Playwright（浏览器自动化）
- ✅ Telegram 自动化推送 → `06-telegram_bot/`
- ✅ 消息队列（RabbitMQ）→ `07-queue/`

---

## 六、机器学习与 AI
- ⬜ scikit-learn（机器学习算法库）
- ⬜ TensorFlow / PyTorch（深度学习框架）
- ⬜ transformers（NLP 预训练模型）

---

## 七、测试与工具
- ✅ unittest / pytest（单元测试框架）→ `03-fastapi/tests`、`10-robyn/tests`
- ✅ argparse / click / typer（命令行工具）→ `05-typer/`
- ✅ typing（类型注解）→ `12-excel/`、`10-robyn/app/schemas`
- ✅ Excel 处理（openpyxl）→ `12-excel/`
- ✅ 工程化（Docker / CI / pre-commit / Alembic 迁移）→ `10-robyn/`

---

# 学习路径建议
1. **基础打牢**：标准库（文件、IO、网络、并发）
2. **进阶拓展**：数据科学 & Web 开发
3. **实战项目**：数据库、爬虫、自动化
4. **高阶提升**：机器学习 & AI
5. **工程化能力**：测试、工具、最佳实践

> 标 ⬜ 的条目是待补清单，按上面的路径顺序补齐即可；标 ✅ 的条目都有可直接运行的代码。

---
