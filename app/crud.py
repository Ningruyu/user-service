"""数据访问层（CRUD 操作）

将数据库操作封装为独立函数，便于单元测试和复用。
路由层通过调用这些函数完成业务逻辑，实现关注点分离。
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    """根据 ID 查询单个用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        User 对象或 None（未找到）
    """
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    """根据用户名查询用户（用于校验唯一性）"""
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> User | None:
    """根据邮箱查询用户（用于校验唯一性）"""
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    """分页查询用户列表

    Args:
        db: 数据库会话
        skip: 跳过的记录数（偏移量）
        limit: 返回的最大记录数（默认 20，上限 100）

    Returns:
        User 列表
    """
    # 防止过大 limit 拖慢查询
    limit = min(limit, 100)
    stmt = select(User).offset(skip).limit(limit).order_by(User.id)
    return list(db.execute(stmt).scalars().all())


def create_user(db: Session, user_in: UserCreate) -> User:
    """创建用户

    Args:
        db: 数据库会话
        user_in: 创建用户的 Pydantic 模型

    Returns:
        创建后的 User 对象（包含 id 和 created_at）
    """
    # 将 Pydantic 模型转为字典，避免手动逐字段赋值
    user_data = user_in.model_dump()
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # 刷新以获取数据库生成的 id、created_at
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate | dict[str, Any]) -> User:
    """更新用户（支持部分更新）

    Args:
        db: 数据库会话
        db_user: 已存在的 User 对象
        user_in: 更新数据（Pydantic 模型或字典）

    Returns:
        更新后的 User 对象
    """
    # 兼容 Pydantic 模型和字典两种输入
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        # exclude_unset=True：只取用户实际传入的字段，避免覆盖为 None
        update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    """删除用户"""
    db.delete(db_user)
    db.commit()
