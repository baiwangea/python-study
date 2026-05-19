#!/bin/bash

# 启动脚本

# 设置环境变量
export DATABASE_URL="postgresql://postgres:password@localhost:5432/robyn_db"
export DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:password@localhost:5432/robyn_db"
export DEBUG="True"
export HOST="0.0.0.0"
export PORT="8000"
export WORKERS="4"

# 检查PostgreSQL是否运行
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Starting PostgreSQL..."
    # 这里可以添加启动PostgreSQL的命令
fi

# 激活虚拟环境（如果有）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "
from app.database import init_db
init_db()
print('Database initialized')
"

# 启动应用
echo "Starting Robyn server on http://localhost:8000"
python app/main.py