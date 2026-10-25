# 深度审稿使用说明

> 本目录保存传统写后质检与独立深度审稿。新报告统一使用 [novel-quality-review Skill](../.agents/skills/novel-quality-review/SKILL.md)。

## 运行方式

在支持项目 Skill 的编码 Agent 中请求：
- 「使用 novel-quality-review 审查第一卷第001—005章，standard 模式；先审查、不要改正文。」
- 「深度检查第四章地形/情报来源、战术合理性和AI式表达，按统一模板输出。」
- 「按上版深度质检报告复审第四章，保留问题 ID，给出评分变化与未修复问题。」

如果 Agent 没有自动识别 Skill，直接让它读取 `.agents/skills/novel-quality-review/SKILL.md` 并按步骤执行。

机械预检（需要 Python 3 标准库，不需要安装依赖）：

```bash
python3 .agents/skills/novel-quality-review/scripts/scan_chapter.py 06-正文/第一卷/第001章.md
python3 .agents/skills/novel-quality-review/scripts/scan_chapter.py 06-正文/第一卷/第001章.md --json
python3 -m unittest discover -s .agents/skills/novel-quality-review/scripts -p 'test_*.py'
```

**机械扫描不会审稿**，只能提供字数与待人工核验的候选表达；逻辑矛盾、AI式痕迹程度、人物与网文吸引力需要完整阅读并引用原文。

## 报告管理

- 正常单章深度报告：`第XXX章-深度质检报告.md`
- 多章：`第XXX-YYY章-综合质检报告.md`
- 修改后的复审：文件名追加 `-复审YYYYMMDD.md`
- 旧 `第XXX章-质检报告.md` 原样保留，作为原稿自检历史记录。

完整评分定义：[评分卡](../.agents/skills/novel-quality-review/references/scoring.md)；统一格式：[报告模板](../.agents/skills/novel-quality-review/references/report-template.md)；检查项：[检查矩阵](../.agents/skills/novel-quality-review/references/checklist.md)。
