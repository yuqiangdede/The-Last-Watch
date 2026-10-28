---
name: webnovel-writer-bridge
description: 项目内以 webnovel-writer v8 流程组织正文备料、起草、八维审读、分项修改与候选事实核对；继续执行 chinese-novelist 的世界观、人物、四关与双格式质量门禁。
---

# Webnovel Writer v8 正文适配入口

**触发**：用户要求使用 webnovel-writer 写正文／复审／续写，或者 chinese-novelist 完成「概要设定＋约500字简写」用户审核后进入详写。

先阅读仓库 AGENTS.md、../chinese-novelist/SKILL.md，再读 ../chinese-novelist/references/flows/webnovel-writer-v8-adapter.md。所有细节以适配协议为准，本入口不创建第二套重复规则。

严格执行：核对审批与人物档案 → 十段来源备料 → 单章候选起草（子 Agent 可用才真的派）→ v8 八维审读 → 现有 G1—G4 + 独立 AI 味反方与一致性校验 → 分项改稿复审 → 候选事实对账 → 权威 MD 与 TXT 交付。

离线备料：python .agents/skills/chinese-novelist/scripts/make_webnovel_write_pack.py --project-dir . --chapter 40 --volume 第三卷。正式稿不可包含草稿元数据和候选事实。独立插章无字数限制。

采用 v8 Scriptor 8.3.2 的工作方法，**不表示已安装其 DSH 运行时**。未发现真实可用的 novel_* 工具时不得伪造调用结果，也不擅自迁移本书目录或重写既有正文。
