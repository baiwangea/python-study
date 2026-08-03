"""
API客户端 - 执行HTTP请求的核心模块

功能：
- 基于配置发送HTTP请求
- 自动重试机制
- 请求/响应日志记录
- 错误处理和异常转换
"""

import json
import time
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from excel_api_client.models.api_config import ClientConfig, APIEndpoint
from excel_api_client.api.request_builder import RequestBuilder
from excel_api_client.utils.logger import get_logger
from excel_api_client.utils.decorators import retry_on_failure, log_execution_time


logger = get_logger()


class APIResponse:
    """API响应包装类"""

    def __init__(self, status_code: int, headers: Dict[str, str],
                 body: Any, duration_ms: float, raw_response: requests.Response):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.duration_ms = duration_ms
        self.raw_response = raw_response
        self.success = 200 <= status_code < 300

    def __repr__(self) -> str:
        return f"APIResponse(status={self.status_code}, success={self.success}, duration={self.duration_ms:.2f}ms)"

    def get(self, key: str, default: Any = None) -> Any:
        """从响应体中获取字段值（响应体为字典时）"""
        if isinstance(self.body, dict):
            return self.body.get(key, default)
        return default

    def raise_for_status(self) -> None:
        """状态码非2xx时抛出异常"""
        if not self.success:
            raise APIRequestError(
                f"请求失败: HTTP {self.status_code} | 响应: {self.body}"
            )


class APIRequestError(Exception):
    """API请求异常"""
    pass


class APIClient:
    """API HTTP客户端"""

    def __init__(self, config: ClientConfig):
        """
        初始化API客户端
        
        Args:
            config: 客户端配置对象
        """
        self.config = config
        self.request_builder = RequestBuilder(config)
        self.session = self._create_session()
        logger.logger.info("API客户端初始化完成")

    def _create_session(self) -> requests.Session:
        """创建配置好的requests会话"""
        session = requests.Session()

        # 配置重试策略
        max_retries = int(self.config.get_env_value('MAX_RETRIES') or 3)
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 配置代理
        proxy_url = self.config.get_env_value('PROXY_URL')
        if proxy_url:
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url,
            }
            logger.logger.info(f"已配置代理: {proxy_url}")

        # SSL验证
        ssl_verify = self.config.get_env_value('ENABLE_SSL_VERIFY')
        session.verify = ssl_verify in ('是', 'yes', 'true', 'True', '1')

        return session

    def request(self, endpoint_name: str,
                path_params: Optional[Dict[str, Any]] = None,
                query_params: Optional[Dict[str, Any]] = None,
                body_params: Optional[Dict[str, Any]] = None,
                extra_headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        发送API请求
        
        Args:
            endpoint_name: 端点名称（对应Excel中的接口名称）
            path_params: 路径参数
            query_params: 查询参数
            body_params: 请求体参数
            extra_headers: 额外请求头
            
        Returns:
            APIResponse对象
        """
        # 构建请求
        request_info = self.request_builder.build_request(
            endpoint_name=endpoint_name,
            path_params=path_params,
            query_params=query_params,
            body_params=body_params,
            extra_headers=extra_headers
        )

        # 记录请求日志
        logger.log_request(
            method=request_info['method'],
            url=request_info['url'],
            headers=request_info['headers'],
            params=query_params,
            body=request_info.get('body')
        )

        # 执行请求
        start_time = time.perf_counter()
        try:
            response = self._execute_request(request_info)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # 解析响应
            api_response = self._parse_response(response, duration_ms)

            # 记录响应日志
            logger.log_response(
                status_code=api_response.status_code,
                response_headers=dict(response.headers),
                response_body=api_response.body,
                duration_ms=duration_ms
            )

            return api_response

        except requests.exceptions.RequestException as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.log_error(e, f"请求失败 [{endpoint_name}] 耗时: {duration_ms:.2f}ms")
            raise APIRequestError(f"请求执行失败: {str(e)}") from e

    def _execute_request(self, request_info: Dict[str, Any]) -> requests.Response:
        """执行HTTP请求"""
        method = request_info['method']
        url = request_info['url']
        headers = request_info['headers']
        timeout = request_info['timeout']
        body = request_info.get('body')

        kwargs = {
            'headers': headers,
            'timeout': timeout,
        }

        if body is not None:
            kwargs['json'] = body

        return self.session.request(method, url, **kwargs)

    def _parse_response(self, response: requests.Response, duration_ms: float) -> APIResponse:
        """解析HTTP响应"""
        try:
            body = response.json()
        except (json.JSONDecodeError, ValueError):
            body = response.text

        return APIResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=body,
            duration_ms=duration_ms,
            raw_response=response
        )

    # ========== 便捷方法 ==========

    def get(self, endpoint_name: str, 
            path_params: Optional[Dict[str, Any]] = None,
            query_params: Optional[Dict[str, Any]] = None,
            **kwargs) -> APIResponse:
        """发送GET请求"""
        return self.request(endpoint_name, path_params, query_params, None, **kwargs)

    def post(self, endpoint_name: str,
             path_params: Optional[Dict[str, Any]] = None,
             body_params: Optional[Dict[str, Any]] = None,
             **kwargs) -> APIResponse:
        """发送POST请求"""
        return self.request(endpoint_name, path_params, None, body_params, **kwargs)

    def put(self, endpoint_name: str,
            path_params: Optional[Dict[str, Any]] = None,
            body_params: Optional[Dict[str, Any]] = None,
            **kwargs) -> APIResponse:
        """发送PUT请求"""
        return self.request(endpoint_name, path_params, None, body_params, **kwargs)

    def delete(self, endpoint_name: str,
               path_params: Optional[Dict[str, Any]] = None,
               **kwargs) -> APIResponse:
        """发送DELETE请求"""
        return self.request(endpoint_name, path_params, None, None, **kwargs)

    def close(self) -> None:
        """关闭会话"""
        self.session.close()
        logger.logger.info("API客户端会话已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False
