# 审稿与设定核查：事实核验参考

> 本文仅提供时空、人物、设定与工程检查的例子。**正式正文评分、AI味37项、P级、修改闭环统一执行 [review-core.md](review-core.md)**；规划和简写执行 [outline-review.md](outline-review.md)。不得把历史“四维硬拦截”、旧双重润色流程或示例脚本作为额外质量门禁。

## 一、事实核查要点

1. **时间线与年龄**：核对正文明确出现的日期、季节、人物出生/去世时点、已发生事件和角色知情；年龄计算须考虑是否过生日。未设明确日期的故事不强制写出年月日。
2. **时空与物理条件**：关注路程、交通方式、行动耗时、伤病恢复、温度与物态、装备能力、资源供给等。先核项目世界规则和实际环境，查证矛盾及反证，不以单一经验强判超自然或科幻设定。
3. **人物与因果**：核对人物小传、能力限制、目标、关系、所知情报及实际选择；人物发生有铺垫的改变或信息误判不自动视为人设崩塌。
4. **语言与视角**：如涉及公文腔、翻译腔、冗余否定、重复解释或声音同质化，按 [37项原表](ai-style-37-checks.md) 及 [自然表达指南](chinese-natural-expression.md) 同轮裁决，不能要求调用未安装的外部润色工具。
5. **问题严重性**：只对确证且实质破坏故事成立的P0/P1按核心协议判文学阻断；无足够证据记待核实，脚本告警仅作候选。

## 二、可选工程扫描

在项目配置启用、脚本可用且当前权限允许时，可运行对应检查；**运行前应确认参数与章节目录**，不在本通用指南硬编码“每章3000—5000字”或固定字数下限。

```bash
# 从项目实际配置核对路径与参数后使用
python .agents/skills/chinese-novelist/scripts/verify_chapter_consistency.py <chapter-path> --project-dir <project-root>
python .agents/skills/chinese-novelist/scripts/scan_chapter.py <chapter-path>
```

运行结果属于工程或候选检测，不能等同语义审稿；未运行就明确写未运行。正式验收与必要副本同步按 [phase4-validation.md](../flows/phase4-validation.md) 执行。

## 三、唯一评分与报告入口

正式正文：[review-core.md](review-core.md)、[chapter-review-default.md](chapter-review-default.md)；非正文：[outline-review.md](outline-review.md)。[旧评分卡](novel-review-scoring.md) 与 [旧报告模板](novel-review-template.md) 仅留作历史格式参考，不能覆盖现行量表及通过条件。
