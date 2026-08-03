"""
装饰器模块 - 提供API请求相关的装饰器
"""

import functools
import time
from typing import Callable, Any

from excel_api_client.utils.logger import get_logger


logger = get_logger()


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                     exceptions: tuple = (Exception,)):
    """
    失败重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 每次重试间隔(秒)
        exceptions: 需要捕获的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.log_retry(attempt, max_retries, e)
                        time.sleep(delay * attempt)  # 指数退避
                    else:
                        logger.log_error(e, f"重试 {max_retries} 次后仍然失败")
                        raise
            raise last_exception
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """记录函数执行时间的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            logger.logger.debug(f"{func.__name__} 执行耗时: {elapsed:.2f}ms")
    return wrapper


def validate_params(required_params: list):
    """
    参数验证装饰器
    
    Args:
        required_params: 必需参数列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            missing = [p for p in required_params if p not in kwargs or kwargs[p] is None]
            if missing:
                raise ValueError(f"缺少必需参数: {', '.join(missing)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
