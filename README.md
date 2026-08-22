# User Service

一个用于学习 Jenkins CI/CD 的轻量级企业级示例项目。模拟用户管理 RESTful API 服务，采用分层架构，结构清晰，适合演示持续集成和持续部署流程。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.9+ |
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据校验 | Pydantic v2 |
| 数据库 | SQLite（开发/测试） |
| 测试框架 | pytest + httpx |
| 覆盖率 | pytest-cov |
| 代码检查 | flake8 |
| 容器化 | Docker（多阶段构建） |
| CI/CD | Jenkins（声明式 Pipeline） |

## 项目结构

```
user-service/
├── app/                        # 应用代码
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py              # 配置类（读取环境变量）
│   ├── database.py            # 数据库连接和会话管理
│   ├── models.py              # SQLAlchemy 模型定义
│   ├── schemas.py             # Pydantic 数据模型
│   ├── crud.py                # 数据访问层（CRUD 操作）
│   └── api/
│       ├── __init__.py
│       └── routes.py          # API 路由定义
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── test_unit.py           # 单元测试（CRUD 函数）
│   └── test_api.py            # 集成测试（HTTP 接口）
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖（含测试工具）
├── pytest.ini                  # pytest 配置
├── Dockerfile                  # 多阶段构建
├── .dockerignore
├── .flake8                    # flake8 配置
├── .gitignore
├── Jenkinsfile                # 声明式 Pipeline
└── README.md
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/users/` | 创建用户 |
| `GET` | `/users/{user_id}` | 获取单个用户 |
| `GET` | `/users/` | 获取用户列表（支持分页 `skip`、`limit`） |
| `PUT` | `/users/{user_id}` | 更新用户（支持部分更新） |
| `DELETE` | `/users/{user_id}` | 删除用户 |
| `GET` | `/` | 根路径信息 |
| `GET` | `/health` | 健康检查 |

### 用户模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键，自增 |
| `username` | string | 用户名，唯一 |
| `email` | string | 邮箱，唯一 |
| `full_name` | string | 全名，可选 |
| `created_at` | datetime | 创建时间 |

## 本地运行

### 1. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装开发依赖（包含测试工具）
pip install -r requirements-dev.txt
```

### 2. 运行应用

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload

# 或指定端口
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问以下地址：

- API 文档（Swagger UI）：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

### 3. 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite:///./user_service.db` | 数据库连接字符串 |
| `DEBUG` | `false` | 调试模式（打印 SQL） |
| `TESTING` | `false` | 测试模式（影响建表逻辑） |

```bash
# 示例：使用内存数据库
export DATABASE_URL="sqlite:///:memory:"

# 示例：开启调试模式
export DEBUG=true
```

## 运行测试

### 运行所有测试

```bash
# 自动生成 JUnit XML 和覆盖率报告
pytest
```

报告文件：
- `results.xml` - JUnit 测试报告
- `coverage.xml` - Cobertura 覆盖率报告
- `htmlcov/` - HTML 覆盖率报告

### 分别运行单元测试和集成测试

```bash
# 仅单元测试（测试 CRUD 函数）
pytest tests/test_unit.py -v

# 仅集成测试（测试 API 接口）
pytest tests/test_api.py -v
```

### 运行代码检查

```bash
# flake8 代码风格检查
flake8 app tests
```

## Docker 构建与运行

### 构建镜像

```bash
# 构建并打标签
docker build -t user-service:latest .

# 查看镜像大小
docker images user-service
```

### 运行容器

```bash
# 运行容器，端口映射 8000:8000
docker run -d \
    --name user-service \
    -p 8000:8000 \
    user-service:latest

# 查看日志
docker logs -f user-service

# 健康检查
curl http://localhost:8000/health
```

### 停止和清理

```bash
# 停止容器
docker stop user-service

# 删除容器
docker rm user-service
```

## Jenkins Pipeline 配置

### 所需 Jenkins 插件

在配置 Pipeline 前，请确保 Jenkins 已安装以下插件：

| 插件 | 用途 |
|------|------|
| [Pipeline](https://plugins.jenkins.io/workflow-aggregator/) | 声明式 Pipeline 支持 |
| [JUnit Plugin](https://plugins.jenkins.io/junit/) | 展示测试报告 |
| [Cobertura Plugin](https://plugins.jenkins.io/cobertura/) | 展示覆盖率报告 |
| [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/) | 在 Pipeline 中使用 Docker |
| [HTML Publisher Plugin](https://plugins.jenkins.io/htmlpublisher/) | 发布 HTML 覆盖率报告 |
| [Warnings Next Generation](https://plugins.jenkins.io/warnings-ng/)（可选） | 展示 flake8 报告 |

### 创建 Pipeline 任务

1. **新建任务**：Jenkins 首页 → 新建任务 → 选择 "Pipeline"

2. **配置源码管理**：
   - 选择 "Pipeline script from SCM"
   - SCM 选择 "Git"
   - Repository URL 填入你的 Git 仓库地址（替换 Jenkinsfile 中的占位符）
   - 指定分支（如 `*/main`）

3. **配置凭证**：

   **Docker Hub 凭证**：
   - 进入 Jenkins → 凭证 → 系统 → 全局凭证
   - 添加凭证 → 类型选 "Username with password"
   - Username: Docker Hub 用户名
   - Password: Docker Hub 密码或 Access Token
   - ID: `docker-hub-credentials`

4. **修改镜像名称**：
   编辑 `Jenkinsfile`，将 `IMAGE_NAME` 改为你的 Docker Hub 仓库地址：
   ```groovy
   environment {
       IMAGE_NAME = 'your-dockerhub-username/user-service'
   }
   ```

5. **构建触发器**（可选）：
   - 可配置轮询 SCM（如 `H/5 * * * *` 每 5 分钟检查一次）
   - 或配置 Webhook 推送触发

### Pipeline 阶段说明

```
Checkout → Setup → Code Quality → Unit Test → Integration Test
        → Coverage → Build Docker Image → Push Docker Image → Deploy to Test
```

| 阶段 | 说明 |
|------|------|
| Checkout | 从 Git 拉取代码 |
| Setup | 创建虚拟环境并安装依赖 |
| Code Quality | 运行 flake8 检查代码风格 |
| Unit Test | 运行单元测试（`test_unit.py`） |
| Integration Test | 运行集成测试（`test_api.py`） |
| Coverage | 生成覆盖率报告 |
| Build Docker Image | 构建 Docker 镜像（仅 main 分支） |
| Push Docker Image | 推送到 Docker Hub（仅 main 分支） |
| Deploy to Test | 运行容器部署到测试环境（仅 main 分支） |

### 查看构建结果

构建完成后，可在 Jenkins 构建页面查看：

- **Test Result**：测试用例通过/失败情况
- **Coverage Report**：代码覆盖率趋势
- **Cobertura Coverage Report**：覆盖率详情
- **构建产物**：下载 `results.xml`、`coverage.xml` 等报告

## 系统要求

- 内存：≥ 2GB（构建和测试）
- Docker：≥ 20.10
- Python：≥ 3.9
- Jenkins：≥ 2.400（推荐 LTS 版本）

## 开发指南

### 添加新 API 端点

1. 在 `app/schemas.py` 添加请求/响应模型
2. 在 `app/crud.py` 添加数据访问函数
3. 在 `app/api/routes.py` 添加路由
4. 在 `tests/test_unit.py` 添加单元测试
5. 在 `tests/test_api.py` 添加集成测试

### 代码风格

- 使用 `flake8` 检查代码风格，配置见 `.flake8`
- 行长度限制 120 字符
- 使用类型注解（Python 3.9+ 风格）

## License

MIT
