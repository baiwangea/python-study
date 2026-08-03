"""
Excel API Client - 基于Excel配置的API请求客户端

通过读取Excel配置文件来管理API接口、参数、认证和环境配置，
实现结构化的第三方接口请求和日志记录。
"""

__version__ = '1.0.0'
__author__ = 'API Client Team'

from excel_api_client.config.excel_reader import ExcelConfigReader
from excel_api_client.api.client import APIClient
from excel_api_client.utils.logger import get_logger

__all__ = [
    'ExcelConfigReader',
    'APIClient',
    'get_logger',
]
