"""
主程序入口 - 演示如何使用Excel配置的API客户端

功能：
1. 从Excel读取所有配置
2. 初始化日志系统
3. 创建API客户端
4. 执行示例请求
5. 展示完整的工作流程
"""

import sys
import os
from pathlib import Path

# 确保可以导入本地包
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from excel_api_client.config.excel_reader import ExcelConfigReader
from excel_api_client.api.client import APIClient
from excel_api_client.utils.logger import get_logger


def main():
    """主函数"""
    print("=" * 70)
    print("  Excel API Client - 基于Excel配置的API请求客户端")
    print("=" * 70)
    print()

    # 配置文件路径
    config_path = project_root / 'data' / 'api_config.xlsx'
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("   请先运行 generate_excel.py 生成配置文件")
        return 1

    print(f"📄 配置文件: {config_path}")
    print()

    # 第一步：读取Excel配置
    print("【步骤1】读取Excel配置...")
    with ExcelConfigReader(str(config_path)) as reader:
        config = reader.read_all()
    print("   ✅ 配置读取完成")
    print()

    # 第二步：初始化日志（使用配置中的日志设置）
    print("【步骤2】初始化日志系统...")
    logger = get_logger(config.log_config)
    print(f"   ✅ 日志目录: {config.log_config.log_dir}")
    print(f"   ✅ 日志文件: {config.log_config.log_file}")
    print()

    # 第三步：创建API客户端
    print("【步骤3】创建API客户端...")
    with APIClient(config) as client:
        print("   ✅ API客户端已创建")
        print()

        # 第四步：执行示例请求
        print("【步骤4】执行示例请求...")
        print()

        # 示例1: 获取用户列表
        print("   📡 请求1: 获取用户列表 (GET /users)")
        try:
            response = client.get(
                endpoint_name='获取用户列表',
                query_params={'page': 1, 'limit': 5}
            )
            print(f"      ✅ 状态码: {response.status_code}")
            print(f"      ✅ 耗时: {response.duration_ms:.2f}ms")
            if isinstance(response.body, list):
                print(f"      ✅ 返回 {len(response.body)} 条数据")
                if response.body:
                    print(f"      📋 第一条: {response.body[0].get('name', 'N/A')}")
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
        print()

        # 示例2: 获取用户详情
        print("   📡 请求2: 获取用户详情 (GET /users/1)")
        try:
            response = client.get(
                endpoint_name='获取用户详情',
                path_params={'id': 1}
            )
            print(f"      ✅ 状态码: {response.status_code}")
            print(f"      ✅ 耗时: {response.duration_ms:.2f}ms")
            if isinstance(response.body, dict):
                print(f"      📋 用户: {response.body.get('name', 'N/A')}")
                print(f"      📧 邮箱: {response.body.get('email', 'N/A')}")
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
        print()

        # 示例3: 创建用户
        print("   📡 请求3: 创建用户 (POST /users)")
        try:
            response = client.post(
                endpoint_name='创建用户',
                body_params={
                    'name': '张三',
                    'email': 'zhangsan@example.com',
                    'phone': '13800138000'
                }
            )
            print(f"      ✅ 状态码: {response.status_code}")
            print(f"      ✅ 耗时: {response.duration_ms:.2f}ms")
            if isinstance(response.body, dict):
                print(f"      📋 创建成功，ID: {response.body.get('id', 'N/A')}")
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
        print()

        # 示例4: 更新用户
        print("   📡 请求4: 更新用户 (PUT /users/1)")
        try:
            response = client.put(
                endpoint_name='更新用户',
                path_params={'id': 1},
                body_params={
                    'name': '李四',
                    'email': 'lisi@example.com'
                }
            )
            print(f"      ✅ 状态码: {response.status_code}")
            print(f"      ✅ 耗时: {response.duration_ms:.2f}ms")
            if isinstance(response.body, dict):
                print(f"      📋 更新成功")
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
        print()

        # 示例5: 获取文章列表
        print("   📡 请求5: 获取文章列表 (GET /posts)")
        try:
            response = client.get(
                endpoint_name='获取文章列表'
            )
            print(f"      ✅ 状态码: {response.status_code}")
            print(f"      ✅ 耗时: {response.duration_ms:.2f}ms")
            if isinstance(response.body, list):
                print(f"      ✅ 返回 {len(response.body)} 条数据")
        except Exception as e:
            print(f"      ❌ 请求失败: {e}")
        print()

    # 完成
    print("=" * 70)
    print("  ✅ 所有请求执行完毕")
    print(f"  📁 日志文件位置: {project_root / config.log_config.log_dir}")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
