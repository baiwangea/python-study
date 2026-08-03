"""
请求构建器 - 根据Excel配置构建HTTP请求

负责：
- 参数收集和验证
- URL路径参数替换
- Query参数组装
- 请求体构建
- 请求头组装
"""

import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from excel_api_client.models.api_config import (
    APIEndpoint, APIParameter, ClientConfig, ParamLocation
)
from excel_api_client.utils.logger import get_logger


logger = get_logger()


class RequestBuilder:
    """HTTP请求构建器"""

    def __init__(self, config: ClientConfig):
        """
        初始化请求构建器
        
        Args:
            config: 客户端配置对象
        """
        self.config = config

    def build_request(self, endpoint_name: str, 
                      path_params: Optional[Dict[str, Any]] = None,
                      query_params: Optional[Dict[str, Any]] = None,
                      body_params: Optional[Dict[str, Any]] = None,
                      extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        构建完整的请求信息
        
        Args:
            endpoint_name: 端点名称
            path_params: 路径参数
            query_params: URL查询参数
            body_params: 请求体参数
            extra_headers: 额外请求头
            
        Returns:
            包含完整请求信息的字典
        """
        endpoint = self.config.get_endpoint(endpoint_name)
        if not endpoint:
            raise ValueError(f"未找到端点配置: {endpoint_name}")

        if not endpoint.enabled:
            raise RuntimeError(f"端点 '{endpoint_name}' 已禁用")

        # 获取该端点的所有参数定义
        param_definitions = self.config.get_parameters_for_endpoint(endpoint_name)

        # 构建URL
        url = self._build_url(endpoint, path_params, param_definitions)

        # 构建请求头
        headers = self._build_headers(endpoint, extra_headers)

        # 构建查询参数
        final_query = self._build_query_params(param_definitions, query_params)
        if final_query:
            url = f"{url}?{urlencode(final_query)}"

        # 构建请求体
        body = self._build_body(param_definitions, body_params)

        request_info = {
            'method': endpoint.method.value,
            'url': url,
            'headers': headers,
            'timeout': endpoint.timeout,
            'retry_count': endpoint.retry_count,
        }

        if body is not None:
            request_info['body'] = body

        logger.logger.debug(f"请求构建完成: {endpoint.method.value} {url}")
        return request_info

    def _build_url(self, endpoint: APIEndpoint, 
                   path_params: Optional[Dict[str, Any]],
                   param_definitions: List[APIParameter]) -> str:
        """构建完整URL，替换路径参数"""
        url = endpoint.full_url

        # 查找路径参数
        path_param_defs = [p for p in param_definitions 
                          if p.location == ParamLocation.PATH]

        for param_def in path_param_defs:
            param_name = param_def.name
            placeholder = f"{{{param_name}}}"

            if placeholder in url:
                value = path_params.get(param_name) if path_params else None
                if value is None:
                    if param_def.required:
                        raise ValueError(f"缺少必需的路径参数: {param_name}")
                    value = param_def.default_value or ''
                
                url = url.replace(placeholder, str(value))

        return url

    def _build_headers(self, endpoint: APIEndpoint,
                       extra_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'ExcelAPIClient/1.0',
        }

        # 添加认证头
        auth_config = self.config.get_auth_config()
        if auth_config:
            auth_headers = auth_config.get_auth_header()
            headers.update(auth_headers)

        # 添加额外请求头
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _build_query_params(self, param_definitions: List[APIParameter],
                            provided_params: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """构建查询参数"""
        query_defs = [p for p in param_definitions 
                     if p.location == ParamLocation.QUERY]
        
        result = {}
        for param_def in query_defs:
            value = provided_params.get(param_def.name) if provided_params else None
            
            if value is None:
                value = param_def.default_value
            
            if value is not None:
                casted = param_def.cast_value(value)
                result[param_def.name] = str(casted)
            elif param_def.required:
                raise ValueError(f"缺少必需的查询参数: {param_def.name}")

        return result

    def _build_body(self, param_definitions: List[APIParameter],
                    provided_params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """构建请求体"""
        body_defs = [p for p in param_definitions 
                    if p.location == ParamLocation.BODY]
        
        if not body_defs:
            return None

        result = {}
        for param_def in body_defs:
            value = provided_params.get(param_def.name) if provided_params else None
            
            if value is None:
                value = param_def.default_value
            
            if value is not None:
                casted = param_def.cast_value(value)
                result[param_def.name] = casted
            elif param_def.required:
                raise ValueError(f"缺少必需的请求体参数: {param_def.name}")

        return result if result else None

    def validate_params(self, endpoint_name: str,
                        path_params: Optional[Dict[str, Any]] = None,
                        query_params: Optional[Dict[str, Any]] = None,
                        body_params: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        验证参数是否满足要求
        
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        param_definitions = self.config.get_parameters_for_endpoint(endpoint_name)

        for param_def in param_definitions:
            if not param_def.required:
                continue

            value = None
            if param_def.location == ParamLocation.PATH:
                value = path_params.get(param_def.name) if path_params else None
            elif param_def.location == ParamLocation.QUERY:
                value = query_params.get(param_def.name) if query_params else None
            elif param_def.location == ParamLocation.BODY:
                value = body_params.get(param_def.name) if body_params else None

            if value is None and param_def.default_value is None:
                errors.append(f"缺少必需参数 [{param_def.location.value}] {param_def.name}")

        return errors
