from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from passlib.context import CryptContext
import bcrypt as bcrypt_lib
import json
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import models, schemas
from app.database import get_asyncpg_pool

# 密码哈希
# 延迟初始化以避免 passlib 初始化时的 bcrypt 检测问题
_pwd_context = None

def get_pwd_context():
    """获取密码上下文，延迟初始化"""
    global _pwd_context
    if _pwd_context is None:
        try:
            _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception:
            # 如果初始化失败，使用直接 bcrypt
            _pwd_context = None
    return _pwd_context

def hash_password(password: str) -> str:
    """哈希密码，自动处理 72 字节限制"""
    password_truncated = _truncate_password(password)
    try:
        pwd_ctx = get_pwd_context()
        if pwd_ctx:
            return pwd_ctx.hash(password_truncated)
    except Exception:
        pass
    # 直接使用 bcrypt
    password_bytes = password_truncated.encode('utf-8')
    salt = bcrypt_lib.gensalt()
    return bcrypt_lib.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    password_truncated = _truncate_password(password)
    try:
        pwd_ctx = get_pwd_context()
        if pwd_ctx:
            return pwd_ctx.verify(password_truncated, hashed)
    except Exception:
        pass
    # 直接使用 bcrypt
    password_bytes = password_truncated.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt_lib.checkpw(password_bytes, hashed_bytes)

def _truncate_password(password: str) -> str:
    """截断密码到 72 字节（bcrypt 限制）"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        # 确保不截断 UTF-8 字符的中间字节
        while len(password_bytes) > 0 and (password_bytes[-1] & 0xC0) == 0x80:
            password_bytes = password_bytes[:-1]
        return password_bytes.decode('utf-8', errors='ignore')
    return password


# 用户CRUD
class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        # bcrypt 限制密码最大 72 字节，自动处理
        hashed_password = hash_password(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.add(models.AuditLog(action="CREATE", table_name="users", record_id=db_user.id, new_values=json.dumps({"username": db_user.username, "email": db_user.email})))
        db.commit()
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
        db_user = UserCRUD.get_user(db, user_id)
        if not db_user:
            return None

        old = {"email": db_user.email, "full_name": db_user.full_name, "is_active": db_user.is_active}
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        db.add(models.AuditLog(action="UPDATE", table_name="users", record_id=db_user.id, old_values=json.dumps(old), new_values=json.dumps(update_data)))
        db.commit()
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        db_user = UserCRUD.get_user(db, user_id)
        if db_user:
            old = {"username": db_user.username, "email": db_user.email}
            db.delete(db_user)
            db.commit()
            db.add(models.AuditLog(action="DELETE", table_name="users", record_id=user_id, old_values=json.dumps(old)))
            db.commit()
            return True
        return False

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            return False
        # bcrypt 限制密码最大 72 字节，自动处理
        if not verify_password(password, user.hashed_password):
            return False
        db.add(models.AuditLog(action="LOGIN", table_name="users", record_id=user.id, new_values=json.dumps({"username": username})))
        db.commit()
        return user


# 异步用户CRUD
class AsyncUserCRUD:
    @staticmethod
    async def get_user_by_email_async(session: AsyncSession, email: str):
        from sqlalchemy import select
        stmt = select(models.User).where(models.User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user_async(session: AsyncSession, user_data: dict):
        user = models.User(**user_data)
        session.add(user)
        await session.flush()
        return user


# 项目CRUD
class ItemCRUD:
    @staticmethod
    def get_item(db: Session, item_id: int):
        return db.query(models.Item).filter(models.Item.id == item_id).first()

    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Item).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Item).filter(
            models.Item.owner_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
        db_item = models.Item(**item.model_dump(), owner_id=user_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.add(models.AuditLog(action="CREATE", table_name="items", record_id=db_item.id, new_values=json.dumps({"title": db_item.title, "owner_id": db_item.owner_id})))
        db.commit()
        return db_item

    @staticmethod
    def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate):
        db_item = ItemCRUD.get_item(db, item_id)
        if not db_item:
            return None

        old = {"title": db_item.title, "description": db_item.description, "price": str(db_item.price)}
        update_data = item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        db.commit()
        db.refresh(db_item)
        db.add(models.AuditLog(action="UPDATE", table_name="items", record_id=db_item.id, old_values=json.dumps(old), new_values=json.dumps(update_data)))
        db.commit()
        return db_item

    @staticmethod
    def delete_item(db: Session, item_id: int):
        db_item = ItemCRUD.get_item(db, item_id)
        if db_item:
            old = {"title": db_item.title, "owner_id": db_item.owner_id}
            db.delete(db_item)
            db.commit()
            db.add(models.AuditLog(action="DELETE", table_name="items", record_id=item_id, old_values=json.dumps(old)))
            db.commit()
            return True
        return False

    @staticmethod
    def search_items(db: Session, filters: schemas.ItemFilterParams):
        query = db.query(models.Item)

        # 价格过滤
        if filters.min_price is not None:
            query = query.filter(models.Item.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.filter(models.Item.price <= filters.max_price)

        # 搜索
        if filters.search:
            query = query.filter(
                or_(
                    models.Item.title.ilike(f"%{filters.search}%"),
                    models.Item.description.ilike(f"%{filters.search}%")
                )
            )

        # 排序
        if filters.sort_by:
            if filters.sort_by == "price":
                order_by = models.Item.price
            elif filters.sort_by == "title":
                order_by = models.Item.title
            elif filters.sort_by == "created_at":
                order_by = models.Item.created_at
            else:
                order_by = models.Item.created_at

            if filters.sort_order == "desc":
                order_by = desc(order_by)
            else:
                order_by = asc(order_by)

            query = query.order_by(order_by)
        else:
            query = query.order_by(desc(models.Item.created_at))

        # 计算总数
        total = query.count()

        # 分页
        items = query.offset((filters.page - 1) * filters.size).limit(filters.size).all()

        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "size": filters.size,
            "pages": (total + filters.size - 1) // filters.size
        }


# 原生SQL查询（asyncpg）
class NativeQuery:
    @staticmethod
    async def get_user_stats(user_id: int):
        pool = await get_asyncpg_pool()
        async with pool.acquire() as conn:
            # 执行原生SQL
            row = await conn.fetchrow("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    COUNT(i.id) as items_count,
                    COALESCE(SUM(i.price), 0) as total_value,
                    MAX(i.created_at) as latest_item_date
                FROM users u
                LEFT JOIN items i ON u.id = i.owner_id
                WHERE u.id = $1
                GROUP BY u.id
            """, user_id)

            if row:
                return dict(row)
            return None

    @staticmethod
    async def bulk_insert_users(users_data: List[Dict]):
        pool = await get_asyncpg_pool()
        async with pool.acquire() as conn:
            # 批量插入
            await conn.executemany("""
                INSERT INTO users (username, email, hashed_password, full_name)
                VALUES ($1, $2, $3, $4)
            """, [
                (u["username"], u["email"], u["password"], u.get("full_name"))
                for u in users_data
            ])


# JWT认证
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
