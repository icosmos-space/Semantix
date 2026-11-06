# Semantix MVP 验收场景

在 Studio → ChatBI 中（建议开启 `use_demo_rows`），按顺序验证以下三组提示词。

## 1. 语义在线率

**提示词**

```text
查询各项目最近 7 天的设备在线率。
```

**期望**

- 返回 Markdown 表格（项目 / 在线率）
- 含 `GPT-Vis` 柱状图围栏
- 含只读 SQL 代码块

## 2. Functional 告警

前置：系统集成导入 OpenAPI，确认 Overlay 只读后发布 `get_device_alarms`；或在能力中心注册同名 Functional 能力并发布。

**提示词**

```text
查询设备 tacey_002 最近一天的告警。
```

**期望**

- Planner 走 Functional 单步
- 回答中出现 `tacey_002` 与告警字段（demo 下含 `A-1001`）

## 3. 混合：低在线率设备 → 告警

**提示词**

```text
找出最近 7 天在线率最低的 5 台设备，并查询它们最近的告警情况。
```

**期望**

- 回答标题含「混合查询计划」
- Step 1：列出 5 台设备（含 `tacey_002` / `tacey_005`）
- Step 2：按设备汇总告警表
- `execution_summary.status == hybrid`，`steps` 长度为 2

## 可选种子

```bash
uv run python scripts/seed_mvp_demo.py
```
