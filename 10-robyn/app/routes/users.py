from robyn import jsonify, Request, Response
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.crud import AuthService
import json



# 依赖注入数据库会话
def get_db_session(request: Request) -> Session:
    return next(get_db())


# 用户路由
async def read_users_me(request: Request):
    # 这里应该从JWT token中获取用户信息
    # 简化示例：直接返回测试用户
    return jsonify({"username": "testuser", "email": "test@example.com"})


async def create_user(request: Request):
    db = get_db_session(request)
    try:
        user_data = json.loads(request.body)
        user_create = schemas.UserCreate(**user_data)

        # 检查用户是否已存在
        db_user = crud.UserCRUD.get_user_by_email(db, email=user_create.email)
        if db_user:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=jsonify({"error": "Email already registered"})
            )

        # 创建用户
        user = crud.UserCRUD.create_user(db=db, user=user_create)
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=jsonify({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "message": "User created successfully"
            })
        )
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": str(e)})
        )


async def read_users(request: Request):
    db = get_db_session(request)
    skip = int(request.query_params.get("skip", "0") or "0")
    limit = int(request.query_params.get("limit", "100") or "100")

    users = crud.UserCRUD.get_users(db, skip=skip, limit=limit)
    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active
            }
            for user in users
        ]
    })


async def read_user(request: Request):
    db = get_db_session(request)
    user_id = int(request.path_params["user_id"])

    user = crud.UserCRUD.get_user(db, user_id=user_id)
    if user is None:
        return Response(
            status_code=404,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": "User not found"})
        )

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    })


async def update_user(request: Request):
    db = get_db_session(request)
    user_id = int(request.path_params["user_id"])

    try:
        update_data = json.loads(request.body)
        user_update = schemas.UserUpdate(**update_data)

        user = crud.UserCRUD.update_user(db, user_id, user_update)
        if not user:
            return Response(
                status_code=404,
                description=jsonify({"error": "User not found"})
            )

        return jsonify({
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": str(e)})
        )


async def delete_user(request: Request):
    db = get_db_session(request)
    user_id = int(request.path_params["user_id"])

    success = crud.UserCRUD.delete_user(db, user_id)
    if not success:
        return Response(
            status_code=404,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": "User not found"})
        )

    return jsonify({"message": "User deleted successfully"})


# 认证路由
async def register(request: Request):
    db = get_db_session(request)
    try:
        # 处理请求体，可能是字符串或字节
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        elif not isinstance(body, str):
            body = str(body)
        
        # 如果 body 为空，返回错误
        if not body or body.strip() == '':
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=jsonify({"error": "Request body is required"})
            )
        
        user_data = json.loads(body)
        user_create = schemas.UserCreate(**user_data)

        # 检查邮箱是否已注册
        db_user = crud.UserCRUD.get_user_by_email(db, email=user_create.email)
        if db_user:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=jsonify({"error": "Email already registered"})
            )

        # 检查用户名是否已存在
        db_user_by_username = crud.UserCRUD.get_user_by_username(db, username=user_create.username)
        if db_user_by_username:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=jsonify({"error": "Username already taken"})
            )

        # 创建用户
        user = crud.UserCRUD.create_user(db, user_create)

        # 创建访问令牌
        access_token = AuthService.create_access_token(
            data={"sub": user.username}
        )

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            description=jsonify({
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })
        )
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
            description=jsonify({"error": str(e)})
        )


async def login(request: Request):
    db = get_db_session(request)
    try:
        credentials = json.loads(request.body)
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=jsonify({"error": "Username and password required"})
            )

        # 验证用户
        user = crud.UserCRUD.authenticate_user(db, username, password)
        if not user:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json; charset=utf-8"},
                description=jsonify({"error": "Invalid credentials"})
            )

        # 创建访问令牌
        access_token = AuthService.create_access_token(
            data={"sub": user.username}
        )

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            description=jsonify({
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })
        )
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json; charset=utf-8"},
            description=jsonify({"error": str(e)})
        )
