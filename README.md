# 小说Agent

AI 驱动的在线小说创作助手，支持多 Agent 协作、LLM 自由配置、流式输出。

## 功能特性

- **多 Agent 协作** — 规划 / 写作 / 审查 / 角色 四大 Agent 分工协作
- **LLM 自由配置** — 支持 OpenAI / Anthropic / Ollama / 任何 OpenAI 兼容 API
- **Agent-模型绑定** — 不同 Agent 可绑定不同模型（如规划用 GPT-4o，写作用本地 Qwen）
- **对话式创作** — 工作台式交互，SSE 流式实时输出
- **项目管理** — 大纲 / 角色 / 世界观 / 章节全流程管理
- **API Key 加密** — 后端 AES 加密存储，前端掩码显示
- **双存储模式** — 本地开发用 JSON 文件，服务器部署用 MongoDB

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + 原生 CSS |
| 后端 | Python + FastAPI |
| 数据库 | MongoDB（生产）/ JSON 文件（开发） |
| LLM 调用 | httpx（OpenAI 兼容协议） |
| 流式输出 | SSE (Server-Sent Events) |

## 项目结构

```
novel-agent/
├── client/                     # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用封装
│   │   ├── components/         # 公共组件
│   │   ├── composables/        # 组合式函数
│   │   ├── router/             # 路由配置
│   │   ├── styles/             # 全局样式
│   │   └── views/              # 页面视图
│   └── vite.config.js
│
├── server/                     # Python 后端
│   ├── core/
│   │   ├── config.py           # 全局配置
│   │   ├── crypto.py           # 加密工具
│   │   ├── llm_router.py       # LLM 统一路由
│   │   ├── oid.py              # ID 兼容层
│   │   └── workflow.py         # Agent 工作流 + Prompt
│   ├── db/
│   │   ├── mongo.py            # 数据库层（自动降级）
│   │   └── json_store.py       # JSON 文件存储
│   ├── models/schemas.py       # 数据模型
│   ├── routes/                 # API 路由
│   └── main.py                 # FastAPI 入口
│
└── .gitignore
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.11
- MongoDB（可选，不装则自动使用 JSON 文件存储）

### 1. 安装依赖

```bash
# 前端
cd client
npm install

# 后端
cd server
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `server/.env` 并修改：

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=novel_agent
ENCRYPTION_KEY=替换为你的32字节密钥
CORS_ORIGINS=http://localhost:5173
```

### 3. 启动服务

```bash
# 后端（端口 8000）
cd server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 不使用 MongoDB 时：
$env:USE_MONGO="false"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端（端口 5173）
cd client
npm run dev
```

### 4. 访问应用

浏览器打开 http://localhost:5173

## 使用流程

1. **配置 LLM** — 进入「LLM配置」页面，添加你的模型（如 OpenAI API）
2. **绑定 Agent** — 为规划/写作/审查/角色 Agent 分别绑定模型
3. **创建项目** — 在首页新建小说项目
4. **设定世界观** — 填写地理、历史、魔法体系等设定
5. **创建角色** — 添加角色信息（性格、背景、说话风格）
6. **编写大纲** — 规划情节走向和章节安排
7. **开始创作** — 在工作台选择 Agent，对话式生成内容

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/health | 健康检查 |
| GET | /api/llm/providers | 获取模型列表 |
| POST | /api/llm/providers | 添加模型 |
| PUT | /api/llm/providers/:id | 更新模型 |
| DELETE | /api/llm/providers/:id | 删除模型 |
| POST | /api/llm/test | 测试模型连接 |
| GET | /api/llm/bindings | 获取 Agent 绑定 |
| PUT | /api/llm/bindings | 更新 Agent 绑定 |
| GET | /api/projects | 项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/:id | 项目详情 |
| PUT | /api/projects/:id | 更新项目 |
| DELETE | /api/projects/:id | 删除项目 |
| GET | /api/projects/:id/outline | 获取大纲 |
| PUT | /api/projects/:id/outline | 更新大纲 |
| GET | /api/projects/:id/characters | 角色列表 |
| POST | /api/projects/:id/characters | 创建角色 |
| PUT | /api/projects/:id/characters/:cid | 更新角色 |
| DELETE | /api/projects/:id/characters/:cid | 删除角色 |
| GET | /api/projects/:id/worldview | 获取世界观 |
| PUT | /api/projects/:id/worldview | 更新世界观 |
| GET | /api/projects/:id/chapters | 章节列表 |
| POST | /api/projects/:id/chapters | 创建章节 |
| PUT | /api/projects/:id/chapters/:cid | 更新章节 |
| DELETE | /api/projects/:id/chapters/:cid | 删除章节 |
| POST | /api/chat/:projectId | 对话式创作（SSE 流式） |

## 支持的 LLM

| 类型 | 说明 | API 地址示例 |
|------|------|-------------|
| OpenAI | GPT-4o / GPT-4 等 | https://api.openai.com/v1 |
| Anthropic | Claude 系列 | https://api.anthropic.com |
| Ollama | 本地模型（Qwen/DeepSeek 等） | http://localhost:11434 |
| Custom | 任何 OpenAI 兼容 API | 自定义 |

## Agent 说明

| Agent | 功能 | Prompt 策略 |
|-------|------|------------|
| 🧠 规划 Agent | 故事大纲、情节走向、冲突设计 | 结合世界观+角色+前文生成规划建议 |
| ✍️ 写作 Agent | 章节内容生成、场景描写 | 保持与前文一致性，角色对话符合性格 |
| 🔍 审查 Agent | 一致性检查、质量评估 | 五维度打分：角色/逻辑/质量/节奏/一致性 |
| 🎭 角色 Agent | 角色设计、性格完善 | 输出姓名/性格/背景/外貌/说话风格/弧线 |

## 服务器部署

```bash
# 使用 MongoDB
export MONGO_URI=mongodb://your-mongo-host:27017
export MONGO_DB=novel_agent
export ENCRYPTION_KEY=your-32-byte-secret-key
export CORS_ORIGINS=https://your-domain.com

# 启动后端
cd server
uvicorn main:app --host 0.0.0.0 --port 8000

# 构建前端
cd client
npm run build
# 将 dist/ 目录部署到 Nginx 或其他静态服务器
```

## License

MIT
