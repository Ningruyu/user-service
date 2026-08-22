"""数据库连接和会话管理

提供 SQLAlchemy engine 和 SessionLocal，以及依赖注入函数 get_db。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

# 创建 engine：根据 DATABASE_URL 自动适配（SQLite / PostgreSQL 等）
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=settings.DATABASE_CONNECT_ARGS,
    echo=settings.DEBUG,  # 开发模式下打印 SQL 日志
)

# 会话工厂：每个请求创建一个独立会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明式基类：所有模型继承自 Base
Base = declarative_base()


def get_db():
    """FastAPI 依赖：提供一个数据库会话并在请求结束后关闭

    使用方式：
        @app.get("/users/")
        def list_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
