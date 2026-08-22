"""集成测试

通过 FastAPI TestClient 发送 HTTP 请求，验证 API 端点的完整行为。
覆盖成功路径、错误处理、边界条件。
"""

import pytest


class TestCreateUserAPI:
    """POST /users/ 创建用户接口测试"""

    def test_create_user_success(self, client, sample_user_data):
        """测试成功创建用户返回 201"""
        response = client.post("/users/", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_username(self, client, created_user, sample_user_data):
        """测试重复用户名返回 409"""
        # 修改邮箱避免邮箱冲突，仅触发用户名冲突
        payload = {**sample_user_data, "email": "another@example.com"}
        response = client.post("/users/", json=payload)

        assert response.status_code == 409
        assert "用户名已被占用" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, created_user, sample_user_data):
        """测试重复邮箱返回 409"""
        payload = {**sample_user_data, "username": "anotheruser"}
        response = client.post("/users/", json=payload)

        assert response.status_code == 409
        assert "邮箱已被注册" in response.json()["detail"]

    def test_create_user_invalid_email(self, client, sample_user_data):
        """测试非法邮箱格式返回 422"""
        payload = {**sample_user_data, "email": "not-an-email"}
        response = client.post("/users/", json=payload)

        assert response.status_code == 422

    def test_create_user_missing_required_field(self, client):
        """测试缺少必填字段返回 422"""
        response = client.post("/users/", json={"email": "test@example.com"})

        assert response.status_code == 422


class TestGetUserAPI:
    """GET /users/{user_id} 获取用户接口测试"""

    def test_get_user_success(self, client, created_user):
        """测试获取存在的用户"""
        response = client.get(f"/users/{created_user['id']}")

        assert response.status_code == 200
        assert response.json() == created_user

    def test_get_user_not_found(self, client):
        """测试获取不存在的用户返回 404"""
        response = client.get("/users/9999")

        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]


class TestListUsersAPI:
    """GET /users/ 用户列表接口测试"""

    def test_list_users_empty(self, client):
        """测试空列表"""
        response = client.get("/users/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_with_data(self, client):
        """测试返回多个用户"""
        # 创建 3 个用户
        for i in range(3):
            client.post(
                "/users/",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                },
            )

        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_users_pagination(self, client):
        """测试分页参数"""
        for i in range(5):
            client.post(
                "/users/",
                json={
                    "username": f"page_user{i}",
                    "email": f"page_user{i}@example.com",
                },
            )

        # 测试 skip 和 limit
        response = client.get("/users/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_users_invalid_limit(self, client):
        """测试超出范围的 limit 返回 422"""
        response = client.get("/users/?limit=200")
        assert response.status_code == 422


class TestUpdateUserAPI:
    """PUT /users/{user_id} 更新用户接口测试"""

    def test_update_user_success(self, client, created_user):
        """测试成功更新用户"""
        payload = {"full_name": "Updated Name"}
        response = client.put(f"/users/{created_user['id']}", json=payload)

        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"
        assert response.json()["username"] == created_user["username"]

    def test_update_user_not_found(self, client):
        """测试更新不存在的用户返回 404"""
        response = client.put("/users/9999", json={"full_name": "X"})

        assert response.status_code == 404

    def test_update_user_conflict_username(self, client):
        """测试更新为已存在的用户名返回 409"""
        # 创建两个用户
        user1 = client.post(
            "/users/",
            json={"username": "first", "email": "first@example.com"},
        ).json()
        client.post(
            "/users/",
            json={"username": "second", "email": "second@example.com"},
        )

        # 将第二个用户的用户名改为第一个的
        response = client.put(f"/users/{user1['id']}", json={"username": "second"})

        assert response.status_code == 409


class TestDeleteUserAPI:
    """DELETE /users/{user_id} 删除用户接口测试"""

    def test_delete_user_success(self, client, created_user):
        """测试成功删除用户"""
        response = client.delete(f"/users/{created_user['id']}")

        assert response.status_code == 204
        # 验证删除后无法再获取
        get_response = client.get(f"/users/{created_user['id']}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        """测试删除不存在的用户返回 404"""
        response = client.delete("/users/9999")

        assert response.status_code == 404


class TestHealthCheck:
    """健康检查端点测试"""

    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    def test_health(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
