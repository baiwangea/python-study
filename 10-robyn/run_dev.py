#!/usr/bin/env python3
"""
开发环境启动脚本
"""
import os
import sys
from pathlib import Path

# 设置环境变量
os.environ["DATABASE_URL"] = "postgresql://postgres:123456@localhost:5432/robyn_db"
os.environ["DATABASE_URL_ASYNC"] = "postgresql+asyncpg://postgres:123456@localhost:5432/robyn_db"
os.environ["DEBUG"] = "True"
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8000"
os.environ["WORKERS"] = "2"  # 开发环境使用较少worker
os.environ["SECRET_KEY"] = "dev-secret-key-change-in-production"

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 检查数据库连接
try:
    from app.database import check_db_health
    import asyncio

    health = asyncio.run(check_db_health())
    if not health:
        print("❌ Database connection failed!")
        print("Please make sure PostgreSQL is running:")
        print("  brew services start postgresql  # macOS")
        print("  sudo service postgresql start   # Linux")
        sys.exit(1)
    else:
        print("✅ Database connection successful")
except Exception as e:
    print(f"⚠️  Database check error: {e}")
    print("Continuing anyway...")

# 初始化数据库
try:
    from app.database import init_db

    init_db()
    print("✅ Database tables created/verified")
except Exception as e:
    print(f"⚠️  Database initialization error: {e}")

# 导入并运行主应用
from app.main import app

if __name__ == "__main__":
    print("\n🚀 Starting Robyn development server...")
    print(f"📡 http://localhost:8000")
    print(f"📊 Health check: http://localhost:8000/health")
    print(f"📚 API docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")

    # 启动服务器（开发模式使用较少worker）
    app.start(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 2))
    )