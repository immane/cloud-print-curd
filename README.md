Cloud Print — Backend

项目概览
- 名称: cloud-print-backend
- 描述: 一个用 FastAPI 实现的云打印服务后端，包含文件存储（S3/MinIO）、MySQL 数据库、Redis 缓存/任务队列（dramatiq）等组件。
- 语言/工具: Python >= 3.12, FastAPI, SQLAlchemy (async), Alembic, Dramatiq, Uvicorn

仓库结构（重要部分）
- src/backend/: 后端代码与构建文件
  - src/: Python package 源码（src.app）
  - Dockerfile, docker-compose.yml, pyproject.toml
  - .env.example

快速开始（本地开发）
1. 推荐创建虚拟环境并安装依赖:
   python -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install -e src

2. 复制环境变量示例并修改:
   cp src/backend/.env.example .env
   编辑 .env（尤其是数据库、Redis、S3/MinIO 凭据、JWT 密钥）

3. 运行数据库与依赖服务（本地或使用 docker-compose）:
   docker compose -f src/backend/docker-compose.yml up -d

4. 运行应用（开发）:
   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

容器 / 生产运行
1. 使用 Dockerfile 构建镜像（在 src/backend 目录下）:
   docker build -t cloud-print-backend src/backend

2. 使用 docker-compose 启动（已包含 mysql/redis/minio）:
   docker compose -f src/backend/docker-compose.yml up --build

环境变量（关键）
- 请复制 src/backend/.env.example 并在生产中确保以下项被正确设置:
  - DATABASE_URL / DATABASE_URL_SYNC
  - REDIS_URL
  - STORAGE_PROVIDER / STORAGE_ENDPOINT / STORAGE_ACCESS_KEY / STORAGE_SECRET_KEY
  - JWT_SECRET
  - SENTRY_DSN (可选)

开发辅助脚本
- src/backend/scripts/create_admin.py: 用来创建或更新管理员账号（见脚本内帮助）

数据库迁移
- 使用 Alembic (alembic.ini 与 alembic/ 目录已存在)。示例:
  alembic upgrade head

测试
- 可在 dev 依赖中安装 pytest 等工具。示例:
  pip install -e .[dev]
  pytest

贡献与代码风格
- 本项目建议使用 ruff / mypy 做静态检查（dev 依赖中包含）。
- 提交前请确保没有敏感信息（JWT 密钥、数据库密码）被提交到仓库。

许可证
- 仓库主许可证: MIT，见 `LICENSE`。
- 许可证说明与子项目继承关系: 见 `LICENSES.md`。

联系人
- 若需帮助或想贡献，请在仓库中打开 issue。
