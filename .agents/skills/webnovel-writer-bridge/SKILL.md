---
name: webnovel-writer-bridge
description: 项目内以 webnovel-writer v8 流程组织正文备料、起草、八维审读、分项修改与候选事实核对；继续执行 chinese-novelist 的世界观、人物、四关与双格式质量门禁。
---

# Webnovel Writer v8 正文适配入口

**触发**：用户要求使用 webnovel-writer 写正文／复审／续写，或者 chinese-novelist 完成「概要设定＋约500字简写」用户审核后进入详写。

先阅读仓库 AGENTS.md、../chinese-novelist/SKILL.md，再读 ../chinese-novelist/references/flows/webnovel-writer-v8-adapter.md。所有细节以适配协议为准，本入口不创建第二套重复规则。

**改稿前置条件**：详写初稿之外的任何分项修订，逐项执行 [改稿净收益评估门禁](../chinese-novelist/references/guides/change-benefit-gate.md)：记录原文价值、收益与潜在副作用；只有收益明确大于损害才改，否则保留原稿或寻找更小替代方案。P0/P1 硬伤未解决不能交付 PASS；改后复验负收益须回滚。禁止为满足八维审读或 AI 味扫描而强行磨平人物与叙事。

严格执行：核对审批与人物档案 → 十段来源备料 → 单章候选起草（子 Agent 可用才真的派）→ v8 八维审读 → 现有 G1—G4 + 独立 AI 味反方与一致性校验 → 分项改稿复审 → 候选事实对账 → 权威 MD 与 TXT 交付。

离线备料：python .agents/skills/chinese-novelist/scripts/make_webnovel_write_pack.py --project-dir . --chapter 39 --volume 第二卷。正式稿不可包含草稿元数据和候选事实。独立插章无字数限制。

采用 v8 Scriptor 8.3.2 的工作方法，**不表示已安装其 DSH 运行时**。未发现真实可用的 novel_* 工具时不得伪造调用结果，也不擅自迁移本书目录或重写既有正文。

## 八能力适配与可执行入口（2026-10-29）

这是工作流等价适配，不等于原版命令已注册或原生 Scriptor novel_* 服务已安装；调用前须确认真实可用工具。统一工具脚本：`../chinese-novelist/scripts/novel_workbench.py`（Python 标准库）。

| 用户意图 | 本仓执行 | 限制 |
|---|---|---|
| webnovel-init | chinese-novelist 的分阶段初始化及 init_novel_workspace.py | 已有项目不得重置 |
| webnovel-plan | 本书总纲/分卷纲/任务卡/时间线，用户审批后写回 | 不自动覆盖已定剧情 |
| webnovel-write | 十段备料→获批简写→单章多版本草稿→八维审读→净收益改稿→事实核对→MD/TXT | 原生 novel_* 不可用时不得冒充 |
| webnovel-review | 简写专属七维或正文八维+原七维+G1—G4+反方 | 简写不检测字句 AI 味 |
| webnovel-query | 工作台 query 检索人物、伏笔、状态、正文等并输出路径行号 | 关键词查询不是数据库/图谱语义查询 |
| webnovel-learn | 工作台 learn 提取有原文来源和 SHA256 的学习候选 | 作者确认前绝不合并到文风权威源 |
| webnovel-dashboard | 工作台 dashboard 生成只读 HTML 文件目录和卷计数 | 暂无追读力计算/实体关系图 |
| webnovel-doctor | 工作台 doctor 检测必需目录、JSON 语法、TXT 缺失 | RAG、依赖、原生服务与语义一致性未检测 |

Windows PowerShell 示例：

```powershell
python .agents/skills/chinese-novelist/scripts/novel_workbench.py --project-dir . query "林霰" --scope 人物 --limit 30
python .agents/skills/chinese-novelist/scripts/novel_workbench.py --project-dir . doctor
python .agents/skills/chinese-novelist/scripts/novel_workbench.py --project-dir . dashboard --output .novel-work/dashboard/index.html
python .agents/skills/chinese-novelist/scripts/novel_workbench.py --project-dir . learn --source "06-正文/第一卷/第001章.md" --excerpt "从实际正文复制的原文" --finding "有效叙事手法" --usage "适用范围与反例"
```

query 命中仅是检索证据，须区分正文事实、人物证言和未来规划；doctor 为 BLOCKED 时中止交付，并结合 `export_reading_txt.py --all --check` 和原一致性质检；learn 仅输出 `07-创作记忆/学习候选/` 的候选 JSON，不自动训练或覆盖规则；dashboard 输出固定在 `.novel-work/`，不修改权威数据。任何 write/review 仍需作者逐章简写审批、角色小传、对抗审稿、净收益评估与 MD/TXT 双格式一致性检查。

## 场景自然度专项（webnovel-write / webnovel-review 同步生效）

执行 [第023章案例：场景真实感与 AI 式结构审查](../chinese-novelist/references/guides/scene-naturalness-review.md)。写前检查人物所知与行动阻力，写中控制动作-眼神-心理三联/说明式对白/场景清单，审后查过度工整的情节模板、专业技术与数量守恒、情感锚点误删；朱雀值不能当生成概率或过关线；简写只审剧情结构。所有改动仍须净收益为正。
