#!/usr/bin/env python3
"""
RabbitMQ工具模块
提供连接参数配置和连接管理功能
"""
import pika

# 建议：在生产环境中，用户名和密码等敏感信息应通过环境变量加载，而不是硬编码。
RABBITMQ_PARAMS_DICT = {
    'host': 'localhost',
    'port': 5672,
    'credentials': pika.PlainCredentials("root", "123456"),
    'virtual_host': "/",
    'heartbeat': 30,
}

def get_connection_parameters() -> pika.ConnectionParameters:
    """
    从配置中获取并返回一个 pika.ConnectionParameters 对象。
    
    Returns:
        pika.ConnectionParameters: RabbitMQ连接参数对象
    """
    return pika.ConnectionParameters(**RABBITMQ_PARAMS_DICT)

def get_connection():
    """
    获取RabbitMQ连接对象
    
    Returns:
        pika.BlockingConnection: RabbitMQ连接对象
    """
    params = get_connection_parameters()
    return pika.BlockingConnection(params)