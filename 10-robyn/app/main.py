import os
import logging
import sys
import uuid
import json
from robyn import Robyn, jsonify, Request, Response, serve_file
from robyn.templating import JinjaTemplate
from pathlib import Path
from datetime import datetime
from app.database import init_db, check_db_health
from app.routes import users, items
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sentry_sdk
import subprocess

class JsonFormatter(logging.Formatter):
    def format(self, record):
        from datetime import datetime as dt
        data = {
            "timestamp": dt.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for k in ("request_id", "method", "path", "status", "duration"):
            v = getattr(record, k, None)
            if v is not None:
                data[k] = v
        return json.dumps(data, ensure_ascii=False)


def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    sql_level = os.getenv("SQLALCHEMY_LOG_LEVEL", "WARNING").upper()
    root = logging.getLogger()
    root.handlers = []
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, level, logging.INFO))
    logging.getLogger("sqlalchemy.engine").setLevel(getattr(logging, sql_level, logging.WARNING))


setup_logging()

app = Robyn(__file__)

# 初始化模板引擎
template = JinjaTemplate(Path(__file__).parent.parent / "templates")

# 监控指标
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "HTTP request latency", ["path"])


# 中间件：全局请求日志
@app.before_request
async def log_request(request: Request):
    request.start_time = datetime.now()
    request.request_id = str(uuid.uuid4())
    logging.info("request_start", extra={"request_id": request.request_id, "method": request.method, "path": request.path})
    return None


# 中间件：全局响应处理
@app.after_request
async def add_response_headers(request: Request, response: Response):
    # 添加响应头
    response.headers["X-Powered-By"] = "Robyn"
    response.headers["X-Process-Time"] = str(
        (datetime.now() - getattr(request, "start_time", datetime.now())).total_seconds()
    )
    if hasattr(request, "request_id"):
        response.headers["X-Request-ID"] = request.request_id

    # 安全与CORS
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Access-Control-Allow-Origin"] = os.getenv("CORS_ALLOW_ORIGIN", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    # 确保响应有正确的Content-Type
    # 检查响应体类型
    body = getattr(response, 'body', None) or getattr(response, 'description', '')
    
    # 检查路径，API 路径通常返回 JSON
    is_api_path = request.path.startswith('/api/') or request.path in ['/health', '/openapi.json']
    
    # 如果已经设置了 Content-Type，不覆盖
    if response.headers.get("Content-Type"):
        pass  # 保持已设置的 Content-Type
    elif isinstance(body, (dict, list)):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    elif isinstance(body, str):
        body_stripped = body.strip()
        # 检查是否是 JSON 字符串
        if body_stripped.startswith('{') or body_stripped.startswith('['):
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        elif "<html" in body.lower() or "<!doctype" in body.lower():
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        elif is_api_path:
            # API 路径默认返回 JSON
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        else:
            response.headers["Content-Type"] = "text/plain; charset=utf-8"
    elif request.path == "/metrics":
        response.headers["Content-Type"] = CONTENT_TYPE_LATEST
    elif is_api_path:
        # API 路径默认返回 JSON
        response.headers["Content-Type"] = "application/json; charset=utf-8"

    # CORS 白名单
    origin = request.headers.get("origin") or request.headers.get("Origin")
    allow_list = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]
    if "*" in allow_list:
        response.headers["Access-Control-Allow-Origin"] = "*"
    elif origin and origin in allow_list:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    # 指标记录
    try:
        status = getattr(response, "status_code", 200)
        REQUEST_COUNT.labels(method=request.method, path=request.path, status=str(status)).inc()
        if hasattr(request, "start_time"):
            d = (datetime.now() - request.start_time).total_seconds()
            REQUEST_LATENCY.labels(path=request.path).observe(d)
            logging.info("request_end", extra={"request_id": getattr(request, "request_id", None), "method": request.method, "path": request.path, "status": status, "duration": d})
    except Exception:
        pass

    return response


# 健康检查端点
@app.get("/health")
async def health_check(request: Request):
    db_health = await check_db_health()
    return jsonify({
        "status": "healthy" if db_health else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_health,
        "service": "robyn-postgres-api",
        "version": "1.0.0"
    })


# Prometheus 指标端点
@app.get("/metrics")
async def metrics(request: Request):
    return generate_latest().decode("utf-8")


# 根路由
@app.get("/")
async def home(request: Request):
    return template.render_template(
        "index.html",
        {"title": "Robyn + PostgreSQL API", "message": "Welcome!"}
    )


# OpenAPI JSON 规范
async def openapi_json(request: Request):
    import json
    openapi_path = Path(__file__).parent / "openapi.json"
    if openapi_path.exists():
        with open(openapi_path, "r", encoding="utf-8") as f:
            openapi_spec = json.load(f)
        return jsonify(openapi_spec)
    return jsonify({"error": "OpenAPI spec not found"}), 404


# Swagger UI 文档页面
async def swagger_ui(request: Request):
    # 直接读取 HTML 文件内容并返回
    swagger_html_path = Path(__file__).parent.parent / "templates" / "swagger.html"
    if swagger_html_path.exists():
        with open(swagger_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        # Robyn 可以直接返回字符串，通过中间件设置 Content-Type
        response = Response(
            status_code=200,
            description=html_content,
            headers={"Content-Type": "text/html; charset=utf-8"}
        )
        return response
    return jsonify({"error": "Swagger UI template not found"}), 404


# 旧版 API 文档（JSON 格式，保留兼容性）
@app.get("/api-docs")
async def api_docs(request: Request):
    docs = {
        "endpoints": {
            "auth": {
                "POST /api/auth/register": "Register new user",
                "POST /api/auth/login": "Login user"
            },
            "users": {
                "GET /api/users/": "List users",
                "GET /api/users/{id}": "Get user by ID",
                "POST /api/users/": "Create user",
                "PUT /api/users/{id}": "Update user",
                "DELETE /api/users/{id}": "Delete user"
            },
            "items": {
                "GET /api/items/": "List items",
                "GET /api/items/{id}": "Get item by ID",
                "POST /api/items/": "Create item",
                "PUT /api/items/{id}": "Update item",
                "DELETE /api/items/{id}": "Delete item",
                "GET /api/items/search": "Search items with filters"
            }
        }
    }
    return jsonify(docs)


# 静态文件服务
@app.get("/static/*path")
async def serve_static(request: Request):
    path = request.path_params["path"]
    static_path = Path(__file__).parent.parent / "static" / path

    if static_path.exists() and static_path.is_file():
        return serve_file(str(static_path))
    return jsonify({"error": "File not found"}), 404


# 注册路由
# 注意：Robyn当前版本没有内置的include_router，需要手动注册路由
app.add_route("GET", "/docs", swagger_ui)
app.add_route("GET", "/openapi.json", openapi_json)

# CORS 预检通用处理
@app.options("/*path")
async def cors_preflight(request: Request):
    origin = request.headers.get("origin") or request.headers.get("Origin")
    allow_list = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]
    
    response = Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*" if "*" in allow_list or not origin else (origin if origin in allow_list else "*"),
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS,PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "3600",
            "Access-Control-Allow-Credentials": "true"
        },
        description=""
    )
    return response

# 用户路由
app.add_route("GET", "/api/users/me", users.read_users_me)
app.add_route("POST", "/api/users/", users.create_user)
app.add_route("GET", "/api/users/", users.read_users)
app.add_route("GET", "/api/users/:user_id", users.read_user)
app.add_route("PUT", "/api/users/:user_id", users.update_user)
app.add_route("DELETE", "/api/users/:user_id", users.delete_user)
app.add_route("POST", "/api/auth/register", users.register)
app.add_route("POST", "/api/auth/login", users.login)

# 项目路由
app.add_route("GET", "/api/items/", items.read_items)
app.add_route("POST", "/api/items/", items.create_item)
app.add_route("GET", "/api/items/:item_id", items.read_item)
app.add_route("PUT", "/api/items/:item_id", items.update_item)
app.add_route("DELETE", "/api/items/:item_id", items.delete_item)
app.add_route("GET", "/api/items/search", items.search_items)


# 启动时初始化数据库
@app.startup_handler
async def startup():
    logging.info("Starting Robyn PostgreSQL API...")
    logging.info("Initializing database...")
    # Sentry
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(dsn=dsn, traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")))
    # Alembic 迁移
    if os.getenv("APPLY_MIGRATIONS", "false").lower() == "true":
        try:
            logging.info("Applying Alembic migrations...")
            subprocess.check_call(["alembic", "upgrade", "head"])
            logging.info("Alembic migrations applied")
        except Exception as e:
            logging.error(f"Alembic migration failed: {e}")
    init_db()
    logging.info("Database initialized successfully")
    logging.info("Server is ready!")


@app.shutdown_handler
async def shutdown():
    logging.info("Shutting down Robyn PostgreSQL API...")
    logging.info("Goodbye!")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 4))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    setup_logging()

    logging.info(f"Server starting on http://{host}:{port}")
    logging.info(f"Workers: {workers}")
    logging.info(f"Debug mode: {debug}")

    app.start(host=host, port=port)
