"""
数据模型定义 - API配置相关的数据类
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from enum import Enum


class HTTPMethod(Enum):
    """HTTP请求方法枚举"""
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'


class AuthType(Enum):
    """认证类型枚举"""
    BEARER = 'Bearer'
    API_KEY = 'APIKey'
    BASIC = 'Basic'
    OAUTH2 = 'OAuth2'
    NONE = 'None'


class ParamLocation(Enum):
    """参数位置枚举"""
    QUERY = 'query'
    BODY = 'body'
    HEADER = 'header'
    PATH = 'path'


@dataclass
class APIEndpoint:
    """API端点配置模型"""
    name: str                          # 接口名称
    method: HTTPMethod                 # 请求方法
    base_url: str                      # 基础URL
    path: str                          # 接口路径
    timeout: int = 10                  # 超时时间(秒)
    retry_count: int = 3               # 重试次数
    enabled: bool = True               # 是否启用
    description: str = ''              # 备注说明

    @property
    def full_url(self) -> str:
        """获取完整URL"""
        base = self.base_url.rstrip('/')
        path = self.path.lstrip('/')
        return f"{base}/{path}"

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.method, str):
            self.method = HTTPMethod(self.method.upper())
        if isinstance(self.enabled, str):
            self.enabled = self.enabled in ('是', 'yes', 'true', 'True', '1')
        self.timeout = int(self.timeout) if self.timeout else 10
        self.retry_count = int(self.retry_count) if self.retry_count else 0


@dataclass
class APIParameter:
    """API参数配置模型"""
    name: str                          # 参数名称
    endpoint_name: str                 # 所属接口名称
    location: ParamLocation          # 参数位置
    param_type: str = 'string'         # 参数类型
    default_value: Optional[str] = None  # 默认值
    required: bool = False           # 是否必填
    description: str = ''            # 参数说明

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.location, str):
            self.location = ParamLocation(self.location.lower())
        if isinstance(self.required, str):
            self.required = self.required in ('是', 'yes', 'true', 'True', '1')

    def cast_value(self, value: Any) -> Any:
        """将值转换为参数类型"""
        if value is None:
            return None
        type_map = {
            'int': int,
            'float': float,
            'bool': lambda x: str(x).lower() in ('true', '1', 'yes', '是'),
            'string': str,
            'list': lambda x: x if isinstance(x, list) else [x],
        }
        caster = type_map.get(self.param_type.lower(), str)
        try:
            return caster(value)
        except (ValueError, TypeError):
            return value


@dataclass
class AuthConfig:
    """认证配置模型"""
    environment: str                   # 环境名称
    auth_type: AuthType                # 认证类型
    token: str = ''                    # Token/Key
    username: str = ''                 # 用户名(Basic认证)
    password: str = ''                 # 密码(Basic认证)
    expire_time: Optional[str] = None  # 过期时间
    refresh_url: str = ''              # 刷新URL
    description: str = ''              # 备注

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.auth_type, str):
            auth_map = {
                'bearer': AuthType.BEARER,
                'apikey': AuthType.API_KEY,
                'basic': AuthType.BASIC,
                'oauth2': AuthType.OAUTH2,
                'none': AuthType.NONE,
            }
            self.auth_type = auth_map.get(self.auth_type.lower(), AuthType.BEARER)

    def get_auth_header(self) -> Dict[str, str]:
        """获取认证请求头"""
        if self.auth_type == AuthType.BEARER:
            return {'Authorization': f'Bearer {self.token}'}
        elif self.auth_type == AuthType.API_KEY:
            return {'X-API-Key': self.token}
        elif self.auth_type == AuthType.BASIC:
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {'Authorization': f'Basic {credentials}'}
        return {}


@dataclass
class EnvironmentConfig:
    """环境配置模型"""
    key: str                           # 配置项名称
    current_env: str                   # 当前环境
    dev_value: str = ''                # 开发环境值
    test_value: str = ''               # 测试环境值
    staging_value: str = ''            # 预发布环境值
    prod_value: str = ''               # 生产环境值
    description: str = ''            # 配置说明

    def get_value(self, env: Optional[str] = None) -> str:
        """获取指定环境的配置值"""
        target = env or self.current_env
        env_map = {
            'dev': self.dev_value,
            'test': self.test_value,
            'staging': self.staging_value,
            'prod': self.prod_value,
        }
        return env_map.get(target, self.dev_value)


@dataclass
class LogConfig:
    """日志配置模型"""
    log_dir: str = 'logs'              # 日志目录
    log_file: str = 'api_client.log'   # 主日志文件
    error_file: str = 'api_errors.log' # 错误日志文件
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    console_output: bool = True        # 控制台输出
    max_file_size_mb: int = 10         # 文件最大大小
    backup_count: int = 30             # 保留文件数
    log_request: bool = True           # 记录请求
    log_response: bool = True          # 记录响应
    excel_log_enabled: bool = True     # 是否写入Excel日志工作表
    excel_log_file: str = 'data/api_config.xlsx'  # Excel日志文件路径
    excel_log_sheet: str = '请求响应日志'  # Excel日志工作表名称

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.console_output, str):
            self.console_output = self.console_output in ('是', 'yes', 'true', 'True', '1')
        if isinstance(self.log_request, str):
            self.log_request = self.log_request in ('是', 'yes', 'true', 'True', '1')
        if isinstance(self.log_response, str):
            self.log_response = self.log_response in ('是', 'yes', 'true', 'True', '1')
        if isinstance(self.excel_log_enabled, str):
            self.excel_log_enabled = self.excel_log_enabled in ('是', 'yes', 'true', 'True', '1')
        self.max_file_size_mb = int(self.max_file_size_mb) if self.max_file_size_mb else 10
        self.backup_count = int(self.backup_count) if self.backup_count else 30

    def to_dict(self) -> Dict[str, Any]:
        """返回可比较的配置字典"""
        return asdict(self)


@dataclass
class ClientConfig:
    """客户端完整配置模型"""
    endpoints: List[APIEndpoint] = field(default_factory=list)
    parameters: List[APIParameter] = field(default_factory=list)
    auth_configs: List[AuthConfig] = field(default_factory=list)
    env_configs: List[EnvironmentConfig] = field(default_factory=list)
    log_config: LogConfig = field(default_factory=LogConfig)
    current_environment: str = 'dev'

    def get_endpoint(self, name: str) -> Optional[APIEndpoint]:
        """根据名称获取端点配置"""
        for ep in self.endpoints:
            if ep.name == name:
                return ep
        return None

    def get_parameters_for_endpoint(self, endpoint_name: str) -> List[APIParameter]:
        """获取指定端点的所有参数"""
        return [p for p in self.parameters if p.endpoint_name == endpoint_name]

    def get_auth_config(self, env: Optional[str] = None) -> Optional[AuthConfig]:
        """获取指定环境的认证配置"""
        target = env or self.current_environment
        for auth in self.auth_configs:
            if auth.environment == target:
                return auth
        return None

    def get_env_value(self, key: str, env: Optional[str] = None) -> str:
        """获取环境配置值"""
        target = env or self.current_environment
        for cfg in self.env_configs:
            if cfg.key == key:
                return cfg.get_value(target)
        return ''
