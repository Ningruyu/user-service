"""FastAPI 应用入口

创建应用实例、注册路由、配置 CORS 和启动事件。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router as user_router
from app.config import get_settings
from app.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    启动时：创建数据库表（开发/测试用，生产环境应使用 Alembic 迁移）
    关闭时：清理资源
    """
    # 仅在非测试模式下自动建表，避免污染测试 fixture 的初始化逻辑
    if not settings.TESTING:
        Base.metadata.create_all(bind=engine)
    yield
    # 关闭时的清理逻辑可在此添加


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="用户管理 RESTful API - 用于演示 Jenkins CI/CD 流程",
    lifespan=lifespan,
)

# 注册用户管理路由，统一前缀 /users
app.include_router(user_router, prefix=settings.API_PREFIX, tags=["用户管理"])


@app.get("/", tags=["健康检查"])
def root() -> dict:
    """根路径：返回服务基本信息，可用于健康检查"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["健康检查"])
def health() -> dict:
    """健康检查端点：供 Docker / Kubernetes 探针使用"""
    return {"status": "healthy"}
