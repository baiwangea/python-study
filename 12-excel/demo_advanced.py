"""
高级示例 - 展示更多高级用法

包括：
- 批量请求
- 参数验证
- 错误处理
- 自定义请求头
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from excel_api_client.config.excel_reader import ExcelConfigReader
from excel_api_client.api.client import APIClient, APIRequestError
from excel_api_client.utils.logger import get_logger


def demo_batch_requests():
    """批量请求示例"""
    print("\n【批量请求示例】")
    print("-" * 50)

    config_path = project_root / 'data' / 'api_config.xlsx'
    
    with ExcelConfigReader(str(config_path)) as reader:
        config = reader.read_all()

    logger = get_logger(config.log_config)

    with APIClient(config) as client:
        # 批量获取多个用户
        user_ids = [1, 2, 3, 4, 5]
        results = []

        for uid in user_ids:
            try:
                response = client.get(
                    endpoint_name='获取用户详情',
                    path_params={'id': uid}
                )
                results.append({
                    'id': uid,
                    'success': response.success,
                    'name': response.get('name', 'Unknown'),
                    'duration': response.duration_ms
                })
            except APIRequestError as e:
                results.append({
                    'id': uid,
                    'success': False,
                    'error': str(e)
                })

        # 打印结果汇总
        success_count = sum(1 for r in results if r.get('success'))
        print(f"   批量请求完成: {success_count}/{len(user_ids)} 成功")
        for r in results:
            if r.get('success'):
                print(f"      ✅ ID={r['id']}: {r['name']} ({r['duration']:.2f}ms)")
            else:
                print(f"      ❌ ID={r['id']}: {r.get('error', 'Unknown error')}")


def demo_custom_headers():
    """自定义请求头示例"""
    print("\n【自定义请求头示例】")
    print("-" * 50)

    config_path = project_root / 'data' / 'api_config.xlsx'
    
    with ExcelConfigReader(str(config_path)) as reader:
        config = reader.read_all()

    logger = get_logger(config.log_config)

    with APIClient(config) as client:
        # 添加自定义请求头
        extra_headers = {
            'X-Request-ID': 'custom-request-001',
            'X-Client-Version': '1.0.0',
        }

        try:
            response = client.get(
                endpoint_name='获取用户列表',
                query_params={'limit': 3},
                extra_headers=extra_headers
            )
            print(f"   ✅ 请求成功，状态码: {response.status_code}")
            print(f"   📋 自定义请求头已发送: {list(extra_headers.keys())}")
        except APIRequestError as e:
            print(f"   ❌ 请求失败: {e}")


def demo_error_handling():
    """错误处理示例"""
    print("\n【错误处理示例】")
    print("-" * 50)

    config_path = project_root / 'data' / 'api_config.xlsx'
    
    with ExcelConfigReader(str(config_path)) as reader:
        config = reader.read_all()

    logger = get_logger(config.log_config)

    with APIClient(config) as client:
        # 示例1: 缺少必需参数
        print("   测试1: 缺少必需参数")
        try:
            # 创建用户时缺少必需的 name 和 email
            response = client.post(
                endpoint_name='创建用户',
                body_params={}  # 空参数
            )
        except ValueError as e:
            print(f"      ⚠️  参数验证失败: {e}")
        except Exception as e:
            print(f"      ❌ 其他错误: {e}")

        # 示例2: 请求不存在的端点
        print("   测试2: 请求不存在的端点")
        try:
            response = client.get(endpoint_name='不存在的接口')
        except ValueError as e:
            print(f"      ⚠️  端点不存在: {e}")
        except Exception as e:
            print(f"      ❌ 其他错误: {e}")


def demo_config_inspection():
    """配置查看示例"""
    print("\n【配置查看示例】")
    print("-" * 50)

    config_path = project_root / 'data' / 'api_config.xlsx'
    
    with ExcelConfigReader(str(config_path)) as reader:
        config = reader.read_all()

    print(f"   当前环境: {config.current_environment}")
    print(f"   API端点数量: {len(config.endpoints)}")
    print(f"   参数配置数量: {len(config.parameters)}")
    print(f"   认证配置数量: {len(config.auth_configs)}")
    print()

    print("   📋 已启用的API端点:")
    for ep in config.endpoints:
        status = "✅ 启用" if ep.enabled else "❌ 禁用"
        print(f"      - {ep.name} [{ep.method.value}] {status}")
        print(f"        URL: {ep.full_url}")
        print(f"        超时: {ep.timeout}s | 重试: {ep.retry_count}次")
        if ep.description:
            print(f"        说明: {ep.description}")
        print()

    print("   🔐 认证配置:")
    for auth in config.auth_configs:
        print(f"      - 环境: {auth.environment} | 类型: {auth.auth_type.value}")
        if auth.expire_time:
            print(f"        过期时间: {auth.expire_time}")
        print()

    print("   ⚙️  环境配置:")
    for env in config.env_configs:
        value = env.get_value(config.current_environment)
        print(f"      - {env.key}: {value}")


if __name__ == '__main__':
    print("=" * 70)
    print("  Excel API Client - 高级用法示例")
    print("=" * 70)

    demo_config_inspection()
    demo_batch_requests()
    demo_custom_headers()
    demo_error_handling()

    print("\n" + "=" * 70)
    print("  ✅ 高级示例执行完毕")
    print("=" * 70)
