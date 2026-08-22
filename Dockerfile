# ============================================
# 多阶段构建 Dockerfile
# 第一阶段（builder）：安装依赖到虚拟环境
# 第二阶段（runtime）：仅复制运行时所需文件，减小镜像体积
# ============================================

# ---------- 第一阶段：构建依赖 ----------
FROM python:3.10-slim AS builder

# 设置工作目录
WORKDIR /build

# 升级 pip 并安装依赖到 /install 目录（便于后续复制）
# 使用 --prefix 将依赖安装到独立目录，避免复制时带入系统包
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- 第二阶段：运行时镜像 ----------
FROM python:3.10-slim AS runtime

# 设置环境变量，优化 Python 运行时
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # 应用配置：使用容器内 SQLite 文件
    DATABASE_URL=sqlite:///./user_service.db

# 安装必要的系统依赖（sqlite3 用于健康检查）
# 注意：安装后清理 apt 缓存以减小镜像体积
RUN apt-get update \
    && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户运行应用（安全最佳实践）
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从 builder 阶段复制已安装的 Python 依赖
COPY --from=builder /install /usr/local

# 复制应用代码
COPY --chown=appuser:appuser . /app

# 切换到非 root 用户
USER appuser

# 暴露应用端口
EXPOSE 8000

# 健康检查：每 30 秒检查一次 /health 端点
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# 启动命令：使用 uvicorn 运行 FastAPI 应用
# --host 0.0.0.0 监听所有网络接口
# --port 8000 监听端口
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
