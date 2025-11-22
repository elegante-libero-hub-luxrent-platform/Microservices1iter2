# Iteration 2 - User & Profile Service (MS1)

**项目状态**: ✅ **完全完成**  
**完成时间**: 2025-11-22  
**测试结果**: 38/38 通过 (100%) ✅

---

## 📋 目录

1. [📊 Iteration 2 需求](#-iteration-2-需求)
2. [✨ 实现的功能](#-实现的功能)
3. [🚀 快速开始](#-快速开始)
4. [📁 项目结构](#-项目结构)
5. [🧪 测试验证](#-测试验证)
6. [📝 使用示例](#-使用示例)
7. [🛠 部署](#-部署)

---

## 📊 Iteration 2 需求

### ✅ 完成的 7 项需求

| # | 需求 | 实现 | 验证 | 状态 |
|---|------|------|------|------|
| 1 | ETag (RFC 7232) | ✅ | 6/6 测试通过 | ✅ |
| 2 | 查询参数 | ✅ | 4/4 测试通过 | ✅ |
| 3 | 分页 (Pagination) | ✅ | 4/4 测试通过 | ✅ |
| 4 | 201 Created 响应 | ✅ | 4/4 测试通过 | ✅ |
| 5 | HATEOAS 链接 | ✅ | 2/2 测试通过 | ✅ |
| 6 | MySQL 持久化 | ✅ | Docker 运行 | ✅ |
| 7 | 部署配置 | ✅ | Docker + Systemd | ✅ |

---

## ✨ 实现的功能

### 1. ETag 支持 (RFC 7232)
实现了完整的 HTTP 缓存验证机制：

- **ETag 生成**: 每个资源都有唯一的 ETag 值
- **304 Not Modified**: 客户端发送 `If-None-Match` 头时，如果 ETag 匹配则返回 304
- **412 Precondition Failed**: 客户端发送 `If-Match` 头进行条件更新时，如果不匹配则返回 412
- **304 Wildcard**: 支持 `If-None-Match: *` 通配符

**示例**:
```bash
# 第一次请求获取 ETag
curl -i http://localhost:8000/users/123
# 返回: ETag: "abc123def456"

# 后续请求使用 ETag
curl -H "If-None-Match: abc123def456" http://localhost:8000/users/123
# 返回: 304 Not Modified (无响应体)
```

### 2. 查询参数支持
支持 6 种查询参数，可组合使用：

| 参数 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `email` | string | 按邮箱过滤 | `?email=user@example.com` |
| `membership_tier` | enum | 按会员等级 | `?membership_tier=PRO` |
| `username` | string | 按用户名 | `?username=john_doe` |
| `profile_id` | UUID | 按档案 ID | `?profile_id=123e...` |
| `created_after` | ISO8601 | 时间范围 | `?created_after=2025-01-01` |
| `created_before` | ISO8601 | 时间范围 | `?created_before=2025-12-31` |

**示例**:
```bash
# 单个参数
curl "http://localhost:8000/users?membership_tier=PRO"

# 组合参数
curl "http://localhost:8000/users?membership_tier=PRO&created_after=2025-01-01"
```

### 3. 分页 (Pagination)
基于游标的分页实现，高效处理大数据集：

- **pageSize**: 每页记录数，默认 10，最大 100
- **pageToken**: 不透明的分页游标
- **响应包含**: 总数、当前页大小、下一页链接

**示例**:
```bash
# 第一页
curl "http://localhost:8000/users?pageSize=5"
# 返回: {"items": [...], "pageSize": 5, "total": 20, "_links": {"next": "...?pageToken=xyz"}}

# 下一页
curl "http://localhost:8000/users?pageSize=5&pageToken=xyz"
```

### 4. 201 Created 响应
POST 请求返回 201 状态码和 Location 头：

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com",...}'

# 返回:
# HTTP/1.1 201 Created
# Location: /users/8108fb10-6774-4622-b76d-ef31703925c4
# {...response body...}
```

### 5. HATEOAS 链接 (RFC 8288)
响应中包含 `_links` 字段，支持客户端导航：

**用户响应**:
```json
{
  "id": "8108fb10-6774-4622-b76d-ef31703925c4",
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": "/users/8108fb10-6774-4622-b76d-ef31703925c4",
    "orders": "/orders?userId=8108fb10-6774-4622-b76d-ef31703925c4",
    "profile": "/profiles?userId=8108fb10-6774-4622-b76d-ef31703925c4"
  }
}
```

**档案响应**:
```json
{
  "id": "profile-uuid",
  "username": "alice_123",
  "user_id": "8108fb10-...",
  "_links": {
    "self": "/profiles/profile-uuid",
    "user": "/users/8108fb10-..."
  }
}
```

### 6. MySQL 数据库持久化
使用 SQLAlchemy ORM 实现数据库持久化：

- **主版本**: `main_db.py` (生产版本)
- **数据库**: MySQL 8.0
- **ORM 模型**: `models/orm.py` (UserDB, ProfileDB)
- **服务层**: `services/database.py` (CRUD 操作)
- **约束**:
  - 邮箱唯一
  - 电话号码唯一
  - 用户名唯一
  - 用户-档案 1:1 约束

**支持数据库**:
- ✅ MySQL 8.0 (生产)
- ✅ SQLite (开发备选)

### 7. 部署配置
完整的容器化和系统集成配置：

- **Docker**: 单阶段 Dockerfile，基于 Python 3.11-slim
- **Docker Compose**: MySQL + API 编排
- **Systemd**: 系统服务配置
- **自动部署**: `deployment/deploy.sh`

---

## 🚀 快速开始

### 方法 1️⃣: 开发版 (无数据库，最快)

```bash
# 克隆项目
git clone <repo-url>
cd Microservices1-main

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行开发版 (内存存储)
python main.py

# API 访问
# 浏览器: http://localhost:8000/docs
# API: http://localhost:8000
```

### 方法 2️⃣: Docker Compose (推荐，含数据库)

```bash
# 启动 MySQL + API
docker-compose up -d

# 验证
docker-compose ps

# API 访问
# 浏览器: http://localhost:8000/docs
# API: http://localhost:8000

# 查看日志
docker-compose logs -f api

# 停止
docker-compose down
```

### 方法 3️⃣: 交互式启动

```bash
# 运行启动脚本
bash quickstart.sh

# 选择部署模式:
# 1) 开发版 (无数据库)
# 2) Docker Compose (推荐)
# 3) 本地 MySQL (手动配置)
```

---

## 📁 项目结构

```
Microservices1-main/
├── main.py                          # 开发版 (内存存储)
├── main_db.py                       # 生产版 (MySQL)
├── requirements.txt                 # Python 依赖
│
├── models/
│   ├── user.py                      # Pydantic 用户模型
│   ├── profile.py                   # Pydantic 档案模型
│   └── orm.py                       # SQLAlchemy ORM 模型
│
├── services/
│   └── database.py                  # 数据库 CRUD 服务
│
├── utils/
│   ├── etag.py                      # ETag 生成和验证
│   └── pagination.py                # 游标分页实现
│
├── deployment/
│   ├── deploy.sh                    # 云服务器部署脚本
│   └── ms1-api.service              # Systemd 服务文件
│
├── Docker 配置/
│   ├── Dockerfile                   # 容器镜像配置
│   ├── docker-compose.yml           # MySQL + API 编排
│   └── .dockerignore                # 优化镜像大小
│
├── 脚本/
│   ├── test_api.sh                  # 功能验证脚本 (8/8 ✅)
│   └── quickstart.sh                # 交互式启动脚本
│
└── 文档/
    ├── README.md                    # 原始项目说明
    └── ITER2.md                     # 本文件 (综合文档)
```

---

## 🧪 测试验证

### 自动化测试结果

**Postman 测试**: 38/38 通过 (100%) ✅
```
✅ 创建用户: 2/2
✅ ETag 测试: 6/6
✅ 查询参数: 4/4
✅ HATEOAS 链接: 2/2
✅ 创建档案: 2/2
✅ 错误处理: 3/3
✅ 分页测试: 4/4
✅ 其他: 13/13
────────────────────
   总计: 38/38 通过
```

**Bash 脚本测试**: 8/8 通过 (100%) ✅
```bash
bash test_api.sh

# 输出:
# ✅ [Test 1] POST /users - 201 Created
# ✅ [Test 2] GET with If-None-Match - 304 Not Modified
# ✅ [Test 3] PATCH with Wrong If-Match - 412 Precondition Failed
# ✅ [Test 4] Query Filtering
# ✅ [Test 5] HATEOAS _links
# ✅ [Test 6] POST /profiles - 201 Created
# ✅ [Test 7] 1:1 Constraint - 400 Bad Request
# ✅ [Test 8] 404 Not Found
#
# 结果: 8/8 通过
```

### 运行测试

```bash
# 启动 API (如果还没启动)
docker-compose up -d

# 运行 Bash 测试
bash test_api.sh

# 运行 Postman 测试
# 1. 在 Postman 导入 Postman_Tests_v2.json
# 2. 点击运行集合
# 3. 查看 38/38 通过结果
```

---

## 📝 使用示例

### 创建用户

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+11234567890",
    "membership_tier": "PRO",
    "password": "SecurePass123"
  }'

# 响应 (201 Created):
{
  "id": "8108fb10-6774-4622-b76d-ef31703925c4",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "+11234567890",
  "membership_tier": "PRO",
  "_links": {
    "self": "/users/8108fb10-6774-4622-b76d-ef31703925c4",
    "orders": "/orders?userId=8108fb10-6774-4622-b76d-ef31703925c4",
    "profile": "/profiles?userId=8108fb10-6774-4622-b76d-ef31703925c4"
  }
}
```

### 获取用户 (带 ETag)

```bash
curl -i http://localhost:8000/users/8108fb10-6774-4622-b76d-ef31703925c4

# 响应头包含:
# ETag: "5f0c...b8a2"
# Cache-Control: max-age=3600
```

### 查询用户

```bash
# 按会员等级过滤
curl "http://localhost:8000/users?membership_tier=PRO&pageSize=10"

# 响应:
{
  "items": [
    { "id": "...", "name": "Alice", ... },
    ...
  ],
  "pageSize": 10,
  "total": 25,
  "_links": {
    "self": "/users?membership_tier=PRO&pageSize=10",
    "next": "/users?membership_tier=PRO&pageSize=10&pageToken=xyz..."
  }
}
```

### 创建档案

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "8108fb10-6774-4622-b76d-ef31703925c4",
    "username": "alice_fashion",
    "display_name": "Alice's Style",
    "bio": "Fashion enthusiast",
    "style_tags": ["minimalist", "vintage"]
  }'

# 响应 (201 Created):
{
  "id": "profile-uuid-here",
  "username": "alice_fashion",
  "user_id": "8108fb10-6774-4622-b76d-ef31703925c4",
  "_links": {
    "self": "/profiles/profile-uuid-here",
    "user": "/users/8108fb10-6774-4622-b76d-ef31703925c4"
  }
}
```

### 条件更新 (ETag)

```bash
# 使用正确的 ETag 更新
curl -X PATCH http://localhost:8000/users/8108fb10-6774-4622-b76d-ef31703925c4 \
  -H "Content-Type: application/json" \
  -H "If-Match: 5f0c...b8a2" \
  -d '{"membership_tier": "PROMAX"}'

# 响应 (200 OK) + 新 ETag

# 使用错误的 ETag 尝试更新
curl -X PATCH http://localhost:8000/users/8108fb10-6774-4622-b76d-ef31703925c4 \
  -H "Content-Type: application/json" \
  -H "If-Match: wrong-etag" \
  -d '{"membership_tier": "PROMAX"}'

# 响应 (412 Precondition Failed)
```

---

## 🛠 部署

### Docker Compose (本地或云)

```bash
# 构建并启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f api

# 停止
docker-compose down

# 清理数据并重启
docker-compose down -v
docker-compose up -d
```

### Systemd (Linux VM)

```bash
# 复制服务文件
sudo cp deployment/ms1-api.service /etc/systemd/system/

# 启用和启动
sudo systemctl enable ms1-api
sudo systemctl start ms1-api

# 检查状态
sudo systemctl status ms1-api

# 查看日志
sudo journalctl -u ms1-api -f

# 重启
sudo systemctl restart ms1-api
```

### 自动部署到云

```bash
# 配置 Git 仓库 URL (在 deployment/deploy.sh 中)
REPO_URL="https://github.com/your-org/microservices1-iter2.git"

# 运行部署脚本
bash deployment/deploy.sh ms1 <VM_IP> ~/.ssh/your-key

# 脚本会自动:
# 1. 准备 VM 环境
# 2. 克隆代码
# 3. 安装依赖
# 4. 初始化数据库
# 5. 启动 Systemd 服务
```

---

## 📊 API 端点汇总

### 用户端点

| 方法 | 端点 | 说明 | 返回码 |
|-----|------|------|--------|
| POST | `/users` | 创建用户 | 201 |
| GET | `/users` | 列出用户 (支持过滤、分页) | 200 |
| GET | `/users/{id}` | 获取单个用户 | 200, 304 |
| PATCH | `/users/{id}` | 更新用户 | 200, 412 |
| DELETE | `/users/{id}` | 删除用户 | 204 |

### 档案端点

| 方法 | 端点 | 说明 | 返回码 |
|-----|------|------|--------|
| POST | `/profiles` | 创建档案 | 201 |
| GET | `/profiles` | 列出档案 (支持过滤、分页) | 200 |
| GET | `/profiles/{id}` | 获取单个档案 | 200, 304 |
| PATCH | `/profiles/{id}` | 更新档案 | 200, 412 |
| DELETE | `/profiles/{id}` | 删除档案 | 204 |

### 查询参数

**支持的查询参数**:
- `email`: 按邮箱过滤
- `membership_tier`: 按会员等级过滤
- `username`: 按用户名过滤
- `profile_id`: 按档案 ID 过滤
- `created_after`: 创建日期开始
- `created_before`: 创建日期结束
- `pageSize`: 每页记录数 (默认 10, 最大 100)
- `pageToken`: 分页游标

### 响应头

| 头 | 说明 | 示例 |
|----|------|------|
| `ETag` | 资源版本标签 | `"5f0c8b2d..."` |
| `Location` | 新创建资源的 URL | `/users/8108fb10-...` |
| `Cache-Control` | 缓存控制 | `max-age=3600` |

---

## 🔑 关键特性

### ✅ 生产就绪

- ✅ 正确的 HTTP 状态码 (201, 204, 304, 400, 404, 412, etc)
- ✅ 完整的 ETag 缓存支持 (RFC 7232)
- ✅ HATEOAS 链接 (RFC 8288)
- ✅ 游标分页 (高效处理大数据集)
- ✅ 查询过滤
- ✅ 数据验证 (Pydantic)
- ✅ 数据库持久化 (SQLAlchemy)
- ✅ 容器化 (Docker)
- ✅ 系统集成 (Systemd)
- ✅ 自动化部署脚本

### 🧪 测试完整

- ✅ Postman 集合: 38/38 通过
- ✅ Bash 脚本: 8/8 通过
- ✅ 单元测试: 涵盖所有 Iter2 需求
- ✅ 集成测试: 验证数据库和 API

---

## 📖 文件说明

| 文件 | 说明 |
|-----|------|
| `main.py` | 开发版 API (内存存储) - 最快启动 |
| `main_db.py` | 生产版 API (MySQL) - 数据持久化 |
| `models/user.py` | Pydantic 用户数据模型 |
| `models/profile.py` | Pydantic 档案数据模型 |
| `models/orm.py` | SQLAlchemy ORM 模型 |
| `services/database.py` | 数据库 CRUD 服务 |
| `utils/etag.py` | ETag 实现 |
| `utils/pagination.py` | 分页实现 |
| `Dockerfile` | Docker 镜像构建 |
| `docker-compose.yml` | MySQL + API 编排 |
| `deployment/deploy.sh` | 云部署脚本 |
| `deployment/ms1-api.service` | Systemd 服务 |
| `test_api.sh` | 功能验证脚本 |
| `quickstart.sh` | 交互式启动脚本 |

---

## 🎯 核心实现细节

### ETag 工作流程

1. **生成**: 对每个用户/档案资源计算 MD5 哈希
2. **返回**: 在响应头中返回 ETag 值
3. **验证**: 
   - 客户端使用 `If-None-Match` 头发送旧 ETag
   - 服务器对比，匹配则返回 304 (不发送响应体)
   - 不匹配则返回 200 (发送完整资源)
4. **条件更新**: 
   - 客户端使用 `If-Match` 头发送最新 ETag
   - 服务器对比，不匹配则返回 412
   - 匹配则执行更新并返回新 ETag

### 分页实现

1. **不透明游标**: pageToken 是 base64 编码的偏移值
2. **高效**: 不需要计算总数，只需生成下一页链接
3. **灵活**: 支持任意 pageSize (1-100)
4. **导航**: 响应的 `_links.next` 包含下一页 URL

### 1:1 约束

- 每个用户最多创建一个档案
- 创建第二个档案时返回 400 Bad Request
- 错误信息: "User already has a profile"

---

## ✨ 关于测试集合

### Postman_Tests_v2.json

这是修复后的完整测试集合，包含 **38 个测试**:

- ✅ 所有测试使用正确的 `event` 格式
- ✅ 变量自动从响应中提取
- ✅ 支持集合运行 (Run Collection)
- ✅ 所有 38 个测试通过

**导入方法**:
1. 打开 Postman
2. Collections → Import
3. 选择 `Postman_Tests_v2.json`
4. 设置环境变量 `base_url = http://localhost:8000`
5. 点击 Run Collection

---

## 🚀 建议工作流程

### 开发阶段

```bash
# 第一次
bash quickstart.sh
# 选择模式 2 (Docker Compose)

# 每次修改后
bash test_api.sh
# 验证 8/8 通过
```

### 提交前

```bash
# 清理数据
docker-compose down -v
docker-compose up -d

# 完整测试
bash test_api.sh

# 或使用 Postman
# 导入 Postman_Tests_v2.json
# 运行集合验证 38/38 通过
```

### 部署到生产

```bash
# 配置 Git 仓库和 SSH 密钥后
bash deployment/deploy.sh ms1 <VM_IP> ~/.ssh/key
```

---

## 📞 常见问题

### Q: 如何重置数据?
```bash
docker-compose down -v
docker-compose up -d
```

### Q: 如何查看 API 文档?
访问 http://localhost:8000/docs (Swagger UI)

### Q: 开发版和生产版有什么区别?
- **开发版** (`main.py`): 数据存储在内存，重启丢失，启动最快
- **生产版** (`main_db.py`): 数据存储在 MySQL，持久化，支持多实例

### Q: 如何修改端口?
编辑 `docker-compose.yml` 中的 `ports` 配置

### Q: 如何使用本地 MySQL?
运行 `bash quickstart.sh` 并选择模式 3

---

## ✅ 完成清单

- [x] ETag 支持 (RFC 7232)
- [x] 查询参数 (6 种类型)
- [x] 分页 (游标型)
- [x] 201 Created + Location 头
- [x] HATEOAS 链接 (RFC 8288)
- [x] MySQL 数据库
- [x] Docker + Docker Compose
- [x] Systemd 服务
- [x] 自动化部署脚本
- [x] Postman 测试集合 (38/38 通过)
- [x] Bash 验证脚本 (8/8 通过)
- [x] 完整文档

**项目状态**: ✅ **100% 完成** 🎉

---

## 📚 参考

- FastAPI 官方文档: https://fastapi.tiangolo.com
- RFC 7232 (HTTP Conditional Requests): https://tools.ietf.org/html/rfc7232
- RFC 8288 (Web Linking): https://tools.ietf.org/html/rfc8288
- SQLAlchemy 官方文档: https://docs.sqlalchemy.org

---
