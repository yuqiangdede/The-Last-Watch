#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由当前项目的分卷章纲生成章节规划索引，不限定卷数、书名和题材。

用法: python .agents/skills/chinese-novelist/scripts/build_chapter_index.py --project-dir . [--check]
"""
import argparse
import json
import re
from pathlib import Path

NUMERALS = [
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
]

HEADER = """# 《{title}》章节规划总表（自动生成索引）

> **只读生成文件，严禁手改。** 逐章规划来源：当前项目的分卷章纲。
> 工作流：卷大纲 → 章大纲 → 简写 → 正文。
> 更新命令：python .agents/skills/chinese-novelist/scripts/build_chapter_index.py --project-dir .
> 检查漂移：同一命令附加 --check。

| 卷号 | 章号 / 插章位置 | 标题 | 核心事件 / 概要 | 推进目标 | 状态 |
| --- | --- | --- | --- | --- | --- |"""


def project_title(root: Path) -> str:
    config = root / "novel.project.json"
    if config.is_file():
        try:
            info = json.loads(config.read_text(encoding="utf-8"))
            value = info.get("title")
            if isinstance(value, str) and value.strip():
                return value.strip()
        except (OSError, ValueError):
            pass
    return root.name


def volume_files(folder: Path):
    result = []
    for path in folder.glob("第*卷.md"):
        m = re.fullmatch(r"第(\d+)卷\.md", path.name)
        if m:
            result.append((int(m.group(1)), path))
    return sorted(result, key=lambda item: item[0])


def build(root: Path) -> str:
    folder = root / "05-写作计划" / "章大纲"
    volumes = volume_files(folder)
    if not volumes:
        raise ValueError(f"未找到分卷章纲：{folder}")
    out = [HEADER.format(title=project_title(root))]
    seen = set()
    for i, path in volumes:
        numeral = NUMERALS[i - 1] if 1 <= i <= len(NUMERALS) else str(i)
        content = path.read_text(encoding="utf-8")
        title = re.search(r"^# .*?：(.+)$", content, re.M)
        if not title:
            raise ValueError(f"卷文件缺少标题：{path}")
        count_match = re.search(r"^- 编号章节数：(\d+|待定)", content, re.M)
        expected = int(count_match.group(1)) if count_match and count_match.group(1).isdigit() else None
        rows = []
        for line in content.splitlines():
            if not re.match(r"^\| 第\d+章(?:后插章（不编号）)? \|", line):
                continue
            cols = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(cols) not in (4, 5):
                raise ValueError(f"字段数量错误：{path}: {line}")
            if len(cols) == 4:
                number, name, brief, status = cols
                goal = "—"
            else:
                number, name, brief, goal, status = cols
            if re.fullmatch(r"第\d+章", number):
                n = int(re.search(r"\d+", number).group())
                if n in seen:
                    raise ValueError(f"重复章节号：{n}")
                seen.add(n)
            rows.append((number, name, brief, goal, status))
        numbered = sum(bool(re.fullmatch(r"第\d+章", r[0])) for r in rows)
        if expected is not None and numbered != expected:
            raise ValueError(f"第{i:02d}卷章数不一致：声明{expected}，实际{numbered}")
        out.append(f"\n## 第{numeral}卷：{title.group(1)}（{expected if expected is not None else '章数待定'}）")
        if not rows:
            out.append("\n> 尚未拆章；等待作者确认卷纲和章节安排。")
        else:
            out.append("")
            out.extend("| 第" + numeral + "卷 | " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", default=".")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    root = Path(args.project_dir).resolve()
    target = root / "05-写作计划" / "章节规划总表.md"
    generated = build(root)
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != generated:
            raise SystemExit("章节索引漂移：请执行生成命令后复核")
        print("章节规划总表与当前项目分卷章纲一致")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated, encoding="utf-8")
        print(f"已生成：{target}")


if __name__ == "__main__":
    main()
