# 《崖边戍卒》TXT 阅读版

本目录是从 06-正文/ 内的 Markdown 自动导出的纯文本副本，不是写作源稿。

- 第一卷/第001章 寒风七折岩.txt：单章 TXT，章节名称直接写在文件名上，正文内容不包含标题；保留自然段，段首两个全角空格，普通段间没有多余空行。
- 第一卷/《崖边戍卒》第一卷.txt：第一卷已写章节合订本，按数字章号顺序排列。
- 每次写作或修订正文后运行：python .agents/skills/chinese-novelist/scripts/export_reading_txt.py --project-dir . --all
- 交付前运行：python .agents/skills/chinese-novelist/scripts/export_reading_txt.py --project-dir . --all --check
- 后续修订只编辑 06-正文/ 的 .md 文件，不直接编辑 TXT。

2026-10-29：作者确认前两卷正文定稿；第一、二卷单章与合订本均已对照 Markdown 校验同步，插章按其所处章节后收录。


## 2026-11-06 新第七卷合并版阅读源

- 新第七卷《海路尽头》含30个编号章和4篇插章（原第七卷16章＋原第八卷14章）；逐篇TXT已移入 `第七卷-海路尽头/`。
- 两份由旧合订本迁移的上／下段TXT尚有旧版封面与卷内章名，不能冒称已重新生成完整合订。运行 `python scripts/complete_volume_merge.py --apply` 后会生成全30章合订文件，运行 `--check` 只读验证。
