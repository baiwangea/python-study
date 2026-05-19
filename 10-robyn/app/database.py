import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator
import asyncpg
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 同步数据库配置（用于普通操作）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/robyn_db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 异步数据库配置（用于高性能异步操作）
ASYNC_DATABASE_URL = os.getenv("DATABASE_URL_ASYNC", "postgresql+asyncpg://postgres:password@localhost:5432/robyn_db")
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 获取同步数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 获取异步数据库会话
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 直接asyncpg连接（用于高性能原生SQL查询）
async def get_asyncpg_pool():
    dsn = os.getenv("DATABASE_URL_ASYNC", ASYNC_DATABASE_URL)
    pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=int(os.getenv("PG_MIN_SIZE", "10")),
        max_size=int(os.getenv("PG_MAX_SIZE", "20")),
        command_timeout=int(os.getenv("PG_COMMAND_TIMEOUT", "60"))
    )
    return pool

# 数据库健康检查
async def check_db_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

# 初始化数据库
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

# 清空测试数据
def clear_test_data():
    from app.models import User, Item
    db = SessionLocal()
    try:
        db.query(Item).delete()
        db.query(User).delete()
        db.commit()
        print("Test data cleared")
    except Exception as e:
        db.rollback()
        print(f"Error clearing test data: {e}")
    finally:
        db.close()
