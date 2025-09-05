# Modern FastAPI Project Structure

这是一个现代化的FastAPI项目结构示例，遵循了最佳实践和项目组织规范。

## 项目结构

```
fastapi/
├── app/                  # 主应用目录
│   ├── __init__.py
│   ├── main.py           # 应用入口点
│   ├── api/              # API路由定义
│   │   ├── __init__.py
│   │   ├── deps.py       # 依赖项定义
│   │   └── v1/           # API v1版本
│   │       ├── __init__.py
│   │       ├── api.py    # v1路由整合
│   │       └── endpoints/ # 各个具体路由处理
│   │           ├── __init__.py
│   │           └── items.py
│   ├── core/             # 核心配置和功能
│   │   ├── __init__.py
│   │   ├── config.py     # 配置文件
│   │   ├── database.py   # 数据库连接
│   │   └── init_db.py    # 数据库初始化
│   ├── models/           # 数据库模型
│   │   ├── __init__.py
│   │   └── item.py
│   ├── schemas/          # Pydantic模型/序列化
│   │   ├── __init__.py
│   │   └── item.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       └── helper.py
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── conftest.py       # pytest配置
│   └── test_items.py     # 测试用例
├── requirements.txt      # 依赖列表
└── README.md             # 项目说明
```

## 主要特点

1. **分层架构**：清晰分离了路由、业务逻辑、数据模型和配置
2. **版本控制**：API具有版本控制（v1）
3. **依赖注入**：使用FastAPI的依赖注入系统
4. **Pydantic验证**：使用Pydantic进行请求和响应数据验证
5. **SQLAlchemy ORM**：使用SQLAlchemy作为数据库ORM
6. **测试配置**：包含pytest测试配置和示例测试

## 安装依赖

```bash
pip install -r requirements.txt
```

## 初始化数据库

在首次运行应用之前，需要创建数据库表：

在项目根目录下运行：
```bash
python -m app.core.init_db
```

或者在Unix/Linux/MacOS系统中：
```bash
python app/core/init_db.py
```

## 运行应用

```bash
uvicorn app.main:app --reload
```

访问 `http://127.0.0.1:8000` 查看API根路径
访问 `http://127.0.0.1:8000/docs` 查看自动生成的API文档

## 运行测试

```bash
pytest
```

## 目录结构说明

- `app/main.py`: 应用程序入口点，创建FastAPI实例并注册路由
- `app/api/v1/api.py`: API路由整合点，将各个子路由整合到一起
- `app/api/v1/endpoints/`: 具体的API端点实现
- `app/schemas/`: Pydantic模型，用于请求和响应数据验证
- `app/models/`: SQLAlchemy数据模型
- `app/core/`: 核心功能，如数据库连接、配置等
- `app/api/deps.py`: 依赖项定义，如数据库会话