# Robyn + PostgreSQL API

一个使用 Robyn 构建的高性能 REST API，集成 PostgreSQL、SQLAlchemy、asyncpg，支持容器化部署与健康检查。

## 功能概览
- 用户与项目 CRUD（`/api/users`, `/api/items`）
- 条件搜索与分页（`/api/items/search`）
- 健康检查（`/health`）
- 模板与静态资源（`/`, `/static/*`）
- 结构化日志与安全响应头

## 快速开始（Docker）
- 启动：`docker-compose up -d --build`
- 健康检查：`curl http://localhost:8000/health`
- 访问：`http://localhost:8000/`
- 停止：`docker-compose down`

说明：容器启动包含 Postgres（持久化卷）、应用（健康检查），不依赖宿主 Python 版本。

## 本地开发（可选）
- 推荐 Python 3.11 环境（3.13 会导致 uvloop/robyn 构建失败）
- 安装依赖：
  - `python -m pip install -r requirements/development.txt`
  - `python -m pip install -r requirements.txt`
- 启动开发服务：`python run_dev.py`

> 无数据库时可用 `docker-compose` 启动 Postgres，或修改 `.env` 指向本地数据库。

## 环境变量
- 数据库：`DATABASE_URL`、`DATABASE_URL_ASYNC`
- 应用：`DEBUG`、`SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`
- 服务器：`HOST`、`PORT`
- CORS：`CORS_ALLOW_ORIGINS`（逗号分隔，默认 `*`，生产建议限定域名）
- 监控：`SENTRY_DSN`、`SENTRY_TRACES_SAMPLE_RATE`

示例参考 `.env.example`

## API 文档
- **Swagger UI**: `http://localhost:8000/docs` - 交互式 API 文档，支持在线测试
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - OpenAPI 3.0 规范文件
- **简单文档**: `http://localhost:8000/api-docs` - JSON 格式的端点列表

## 主要端点
- `GET /health` 健康检查
- `GET /` 首页模板
- `GET /docs` Swagger UI 文档（推荐）
- 用户
  - `POST /api/users/` 创建用户
  - `GET /api/users/` 列表
  - `GET /api/users/{id}` 详情
  - `PUT /api/users/{id}` 更新
  - `DELETE /api/users/{id}` 删除
  - `POST /api/auth/register` 注册并返回令牌
  - `POST /api/auth/login` 登录并返回令牌
- 项目
  - `POST /api/items/` 创建
  - `GET /api/items/` 列表
  - `GET /api/items/{id}` 详情
  - `PUT /api/items/{id}` 更新
  - `DELETE /api/items/{id}` 删除
  - `GET /api/items/search` 条件查询（分页、排序、搜索）

## 示例请求
- 创建用户：
  ```bash
  curl -X POST http://localhost:8000/api/users/ \
    -H 'Content-Type: application/json' \
    -d '{"username":"testuser","email":"test@example.com","password":"testpassword123"}'
  ```
- 创建项目：
  ```bash
  curl -X POST http://localhost:8000/api/items/ \
    -H 'Content-Type: application/json' \
    -d '{"title":"Test Item","price":"19.99","owner_id":1}'
  ```

## 测试与质量
- 运行测试：
  - 宿主机：`pytest -q`（需本地安装依赖，3.11 推荐）
  - 容器内：`docker exec -it 10-robyn-app-1 sh -lc "python -m pip install pytest && python -m pytest -q"`
- 代码检查：`flake8 app`
- 预提交钩子：`pre-commit install`，执行 `pre-commit run --all-files`

## 迁移与数据库版本管理（Alembic）
- 初始迁移已生成并注册：`alembic/versions/20251204_000001_init.py`
- 常用命令：
  - 升级到最新：`alembic upgrade head`
  - 生成新迁移（自动扫描模型变更）：`alembic revision --autogenerate -m "desc"`
  - 回滚一步：`alembic downgrade -1`
  - 查看当前版本：`alembic current`
- Docker 场景：
  - 进入容器执行：`docker exec -it 10-robyn-app-1 sh -lc "alembic upgrade head"`
- 说明：生产环境建议使用 Alembic 管理变更，避免 `create_all` 直接改表结构。

## 监控与告警
- Prometheus：暴露 `GET /metrics`，默认导出请求计数与延迟直方图。
- Sentry：设置 `SENTRY_DSN` 环境变量启用；`SENTRY_TRACES_SAMPLE_RATE` 控制性能采样（默认 0）。
- 指标示例：
  ```bash
  curl http://localhost:8000/metrics | head -n 20
  ```

## 日志与排查
- 输出：标准输出采用 JSON 结构化日志，便于采集与检索。
- 请求关联：每次请求都会生成 `X-Request-ID` 并写入日志与响应头，便于端到端排查。
- 响应耗时：日志包含 `duration` 字段（秒）。
- SQL 日志：通过 `SQLALCHEMY_LOG_LEVEL` 控制 `sqlalchemy.engine` 输出级别（默认 `WARNING`）。
- 环境变量：
  - `LOG_LEVEL`（默认 `INFO`）
  - `SQLALCHEMY_LOG_LEVEL`（默认 `WARNING`）
- 示例：
  ```json
  {"timestamp":"2025-12-04T13:05:22.84","level":"INFO","message":"request_end","request_id":"...","method":"GET","path":"/api/items","status":200,"duration":0.012}
  ```

## CORS 白名单与预检
- 配置：`CORS_ALLOW_ORIGINS="https://a.com,https://b.com"`
- 预检：已实现通用 `OPTIONS /*` 处理（返回 204）；响应头包含 `Access-Control-*`。
- 注意：默认允许 `*`，生产请按域名白名单收敛。

## CI 与 Git 工作流
- CI（GitHub Actions）：`.github/workflows/ci.yml`
  - 启动 Postgres 服务（健康检查）、安装依赖、运行 `flake8` 与 `pytest`
  - 默认 Python 3.11，环境变量通过 job `env` 注入
- Git 工作流建议：
  - 分支：`main`（发布）、`develop`（集成）、`feature/*`、`bugfix/*`、`hotfix/*`
  - 提交信息：使用动词开头，如 `feat: add items search api`
  - PR：附检查结果、影响范围与回滚方案

## 部署说明
- 使用 `docker-compose` 在生产部署：
  - 设置 `DEBUG=False`、强壮的 `SECRET_KEY`
  - 限定 `CORS_ALLOW_ORIGINS`
  - 数据库使用持久化卷与远程备份
  - 健康检查已内置（Dockerfile 与 docker-compose 配置）
- 运行时检查：
  - 应用健康：`/health` 返回 `status` 与数据库连通性
  - 指标健康：`/metrics` 可被 Prometheus 抓取

## 代码位置
- 启动与路由注册：`app/main.py:150–175`
- 健康检查与指标：`app/main.py:79–95`
- CORS 与安全响应头：`app/main.py:40–63`
- 用户接口：`app/routes/users.py:18–27`
- 项目接口：`app/routes/items.py:15–23`

## 常见问题
- 宿主机 Python 3.13 安装 `robyn/uvloop` 失败：建议使用 Docker 或 Python 3.11。
- 测试在容器内缺少 `pytest`：在容器中安装 `python -m pip install pytest` 后运行。
- `requests` 未安装：已添加到 `requirements.txt`，容器重建即可。

## 维护约定与更新清单
- 改动约束：凡涉及下列任一改动，请同步更新本 README 并在 PR 中说明。
- 更新清单：
  - 环境变量新增或语义变化（如 `CORS_ALLOW_ORIGINS`、`SENTRY_DSN`、`APPLY_MIGRATIONS`）
  - 新增/变更 API 端点或响应格式
  - 迁移策略变化（Alembic 命令、自动迁移开关、版本命名规范）
  - CI 流程变化（测试命令、数据库服务、Python 版本）
  - 部署容器参数变化（健康检查、端口映射、卷、网络）
  - 监控指标变化（新增指标、暴露端点路径、抓取频率建议）
  - 安全与跨域策略变化（响应头、预检处理、来源白名单）
- PR 要求：
  - 附变更说明与影响面；如涉及数据结构，附迁移步骤
  - 本地或容器内运行 `flake8 app` 与最小化测试
  - 若 CI 失败，须修复后再合并
