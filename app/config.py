"""配置模块

从环境变量读取配置，便于在不同环境（开发、测试、生产）间切换。
"""

import os
from functools import lru_cache


class Settings:
    """应用配置类

    通过环境变量注入配置，避免硬编码，符合 12-factor App 规范。
    """

    # 应用基础信息
    APP_NAME: str = "User Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库配置：默认使用 SQLite，生产环境可通过 DATABASE_URL 切换
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./user_service.db"  # 默认使用本地 SQLite 文件
    )

    # API 前缀
    API_PREFIX: str = "/users"

    # 测试模式：使用内存数据库
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    # SQLite 特殊处理：允许跨线程访问（FastAPI 多线程场景需要）
    @property
    def DATABASE_CONNECT_ARGS(self) -> dict:
        if self.DATABASE_URL.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例

    使用 lru_cache 缓存，避免重复读取环境变量。
    测试时可通过 `get_settings.cache_clear()` 重置缓存。
    """
    return Settings()
