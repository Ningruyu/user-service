"""单元测试

直接测试 crud.py 中的函数，使用独立的测试数据库会话。
不经过 HTTP 层，验证数据访问逻辑的正确性。
"""

import pytest

from app import crud, schemas
from app.models import User


class TestCreateUser:
    """创建用户测试"""

    def test_create_user_success(self, db_session):
        """测试成功创建用户"""
        user_in = schemas.UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice Smith",
        )
        user = crud.create_user(db_session, user_in)

        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.full_name == "Alice Smith"
        assert user.created_at is not None

    def test_create_user_minimal_fields(self, db_session):
        """测试只传必填字段（full_name 为空）"""
        user_in = schemas.UserCreate(
            username="bob",
            email="bob@example.com",
        )
        user = crud.create_user(db_session, user_in)

        assert user.full_name is None
        assert user.username == "bob"


class TestGetUser:
    """查询用户测试"""

    def test_get_user_by_id(self, db_session):
        """测试按 ID 查询存在的用户"""
        user_in = schemas.UserCreate(
            username="charlie",
            email="charlie@example.com",
        )
        created = crud.create_user(db_session, user_in)

        found = crud.get_user(db_session, created.id)
        assert found is not None
        assert found.id == created.id
        assert found.username == "charlie"

    def test_get_user_not_found(self, db_session):
        """测试查询不存在的用户返回 None"""
        found = crud.get_user(db_session, 9999)
        assert found is None

    def test_get_user_by_username(self, db_session):
        """测试按用户名查询"""
        user_in = schemas.UserCreate(
            username="dave",
            email="dave@example.com",
        )
        crud.create_user(db_session, user_in)

        found = crud.get_user_by_username(db_session, "dave")
        assert found is not None
        assert found.email == "dave@example.com"

    def test_get_user_by_email(self, db_session):
        """测试按邮箱查询"""
        user_in = schemas.UserCreate(
            username="eve",
            email="eve@example.com",
        )
        crud.create_user(db_session, user_in)

        found = crud.get_user_by_email(db_session, "eve@example.com")
        assert found is not None
        assert found.username == "eve"


class TestListUsers:
    """用户列表测试"""

    def test_list_users_pagination(self, db_session):
        """测试分页查询"""
        # 创建 5 个用户
        for i in range(5):
            crud.create_user(
                db_session,
                schemas.UserCreate(
                    username=f"user{i}",
                    email=f"user{i}@example.com",
                ),
            )

        # 第一页：跳过 0，取 3
        page1 = crud.get_users(db_session, skip=0, limit=3)
        assert len(page1) == 3

        # 第二页：跳过 3，取 3（只剩 2 个）
        page2 = crud.get_users(db_session, skip=3, limit=3)
        assert len(page2) == 2

    def test_list_users_empty(self, db_session):
        """测试空列表"""
        users = crud.get_users(db_session, skip=0, limit=10)
        assert users == []


class TestUpdateUser:
    """更新用户测试"""

    def test_update_user_partial(self, db_session):
        """测试部分更新（仅更新 full_name）"""
        user_in = schemas.UserCreate(
            username="frank",
            email="frank@example.com",
            full_name="Old Name",
        )
        user = crud.create_user(db_session, user_in)

        update_data = {"full_name": "New Name"}
        updated = crud.update_user(db_session, user, update_data)

        assert updated.full_name == "New Name"
        assert updated.username == "frank"  # 未被更新
        assert updated.email == "frank@example.com"

    def test_update_user_full(self, db_session):
        """测试完整更新"""
        user_in = schemas.UserCreate(
            username="grace",
            email="grace@example.com",
        )
        user = crud.create_user(db_session, user_in)

        update_data = {
            "username": "grace2",
            "email": "grace2@example.com",
            "full_name": "Grace Lee",
        }
        updated = crud.update_user(db_session, user, update_data)

        assert updated.username == "grace2"
        assert updated.email == "grace2@example.com"
        assert updated.full_name == "Grace Lee"


class TestDeleteUser:
    """删除用户测试"""

    def test_delete_user_success(self, db_session):
        """测试删除用户后查询返回 None"""
        user_in = schemas.UserCreate(
            username="henry",
            email="henry@example.com",
        )
        user = crud.create_user(db_session, user_in)
        user_id = user.id

        crud.delete_user(db_session, user)

        assert crud.get_user(db_session, user_id) is None

    def test_delete_user_count_changes(self, db_session):
        """测试删除后用户列表数量减少"""
        user_in = schemas.UserCreate(
            username="ivy",
            email="ivy@example.com",
        )
        user = crud.create_user(db_session, user_in)

        assert len(crud.get_users(db_session)) == 1
        crud.delete_user(db_session, user)
        assert len(crud.get_users(db_session)) == 0
