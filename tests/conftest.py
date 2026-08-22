"""pytest 公共 fixtures

提供测试数据库、测试客户端等共享资源。
通过 fixtures 隔离测试环境，避免污染开发数据库。
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 必须在导入 app 之前设置环境变量，确保使用内存数据库
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="function")
def db_session():
    """每个测试函数使用独立的内存数据库会话

    scope="function" 保证每个测试互不影响，提升测试隔离性。
    使用 StaticPool 保证内存数据库在整个会话期间不被释放。
    """
    # 创建内存数据库 engine，使用 StaticPool 共享同一连接
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 建表
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI 测试客户端

    覆盖 get_db 依赖，使其返回测试会话而非生产会话。
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # 会话由 db_session fixture 负责关闭

    # 替换依赖：让路由使用测试数据库会话
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """示例用户数据，供多个测试复用"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
    }


@pytest.fixture
def created_user(client, sample_user_data):
    """创建一个用户并返回，供需要前置用户的测试使用"""
    response = client.post("/users/", json=sample_user_data)
    assert response.status_code == 201
    return response.json()
