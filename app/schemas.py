"""Pydantic 数据模型（Schema）

用于请求体校验和响应序列化。Pydantic v2 风格。
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """用户基础字段（创建和更新共用）"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: str | None = Field(None, max_length=120, description="全名")


class UserCreate(UserBase):
    """创建用户请求体"""

    pass


class UserUpdate(BaseModel):
    """更新用户请求体

    所有字段可选，支持部分更新（PATCH 语义）。
    """

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=120)


class UserResponse(UserBase):
    """用户响应体

    包含数据库生成的字段（id、created_at）。
    """

    id: int
    created_at: datetime

    # Pydantic v2：允许从 ORM 对象读取属性
    model_config = ConfigDict(from_attributes=True)
