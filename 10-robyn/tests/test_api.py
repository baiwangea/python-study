import pytest
import os
import time
import subprocess
import requests
import json


@pytest.fixture(scope="module", autouse=True)
def wait_server_ready():
    for _ in range(60):
        try:
            r = requests.get("http://localhost:8000/health", timeout=1)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.5)


def test_health_check():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_create_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = requests.post("http://localhost:8000/api/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == user_data["username"]


def test_get_users():
    response = requests.get("http://localhost:8000/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data


def test_create_and_get_item():
    # 先创建用户
    user_data = {
        "username": "itemuser",
        "email": "item@example.com",
        "password": "itempassword123"
    }
    user_response = requests.post("http://localhost:8000/api/users/", json=user_data)
    user_id = user_response.json()["id"]

    # 创建项目
    item_data = {
        "title": "Test Item",
        "description": "Test Description",
        "price": "19.99",
        "owner_id": user_id
    }
    item_response = requests.post("http://localhost:8000/api/items/", json=item_data)
    assert item_response.status_code == 201

    # 获取项目
    item_id = item_response.json()["id"]
    get_response = requests.get(f"http://localhost:8000/api/items/{item_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == item_data["title"]


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__])
