# 冷门徒步路线水源标记

记录冷门徒步路线上的水源与休息点，方便行前查阅与途中参考。

## 技术栈

| 层级 | 技术 | 端口 |
|------|------|------|
| 前端 | Vue 3 + PrimeVue + Vue Router + axios | **7101** |
| 后端 | Flask + SQLite (`data/hiking.db`) | **7000** |

## 首次安装

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 前端

```bash
cd frontend
npm install
```

## 启动

**终端 1 — 后端（一条命令）：**

```bash
cd backend; .venv\Scripts\python app.py
```

> macOS / Linux：`cd backend; .venv/bin/python app.py`

首次启动会自动创建 `data/hiking.db` 并写入种子数据（2 条路线，各 3 个标记点）。

**终端 2 — 前端：**

```bash
cd frontend; npm run dev
```

浏览器访问：<http://localhost:7101>

## 功能（MVP）

- **路线列表**：查看、新建、编辑、删除路线（名称、难度）
- **路线详情**：DataTable 展示标记点（类型：水源/休息、坐标文字、备注），支持增删改

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/routes` | 路线列表 |
| POST | `/api/routes` | 新建路线 |
| GET | `/api/routes/:id` | 路线详情 |
| PUT | `/api/routes/:id` | 更新路线 |
| DELETE | `/api/routes/:id` | 删除路线 |
| GET | `/api/routes/:id/markers` | 标记点列表 |
| POST | `/api/routes/:id/markers` | 新建标记点 |
| PUT | `/api/markers/:id` | 更新标记点 |
| DELETE | `/api/markers/:id` | 删除标记点 |

## 种子数据

| 路线 | 难度 | 标记点 |
|------|------|--------|
| 雨崩冰湖线 | 困难 | 2 水源 + 1 休息 |
| 格聂C线 | 极难 | 2 水源 + 1 休息 |
