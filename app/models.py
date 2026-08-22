"""SQLAlchemy 模型定义

定义数据库表结构。模型与表一一对应，通过 Base.metadata 管理迁移。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    """用户表模型

    字段：
        id          主键，自增
        username    用户名，唯一，建立索引便于查询
        email       邮箱，唯一
        full_name   全名，可为空
        created_at  创建时间，默认 UTC 当前时间
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username!r}, email={self.email!r})>"
