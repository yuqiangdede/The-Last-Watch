#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单章机械性预扫描：字数/候选套话。只提供证据候选，不判定是否由 AI 生成。
用法: python3 .agents/skills/novel-quality-review/scripts/scan_chapter.py 06-正文/第一卷/第001章.md [--json]
"""
import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "全知模板句": r"他不知道的是|她不知道的是|殊不知|命运的齿轮",
    "总结式顿悟": r"这一刻.{0,9}(终于|才)?明白|终于懂得了|这一刻.{0,9}意识到",
    "假对比/升华": r"不仅是.{0,24}更是|不只是.{0,24}更是|看似.{0,24}实则",
    "机械断章": r"危险正在悄然逼近|然而.{0,20}意想不到|一场更大的风暴",
    "高频修饰词": r"瞬间|冰冷|死死|狂暴|狠狠",
}

def is_han(ch: str) -> bool:
    cp = ord(ch)
    return 0x3400 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF or 0x20000 <= cp <= 0x3134F

def prose_lines(text: str):
    """保留原始行号；跳过 Markdown 标题与代码围栏，其他非空正文行参与统计。"""
    inside_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(">>>"):  # 防止某些文稿插入转储标记
            continue
        if stripped.startswith("~~~") or stripped.startswith("```"):
            inside_fence = not inside_fence
            continue
        if inside_fence or not stripped or re.match(r"^#{1,6}\s", stripped):
            continue
        # Markdown 场景分隔符不算正文
        if stripped in ("---", "***", "___"):
            continue
        yield line_no, line

def scan(path: Path):
    lines = list(prose_lines(path.read_text(encoding="utf-8-sig")))
    prose = "".join(line for _, line in lines)
    hits = []
    for label, pattern in PATTERNS.items():
        for line_no, line in lines:
            for match in re.finditer(pattern, line):
                left, right = max(0, match.start() - 24), min(len(line), match.end() + 24)
                hits.append({"type": label, "line": line_no, "match": match.group(),
                             "context": line[left:right].strip()})
    hits.sort(key=lambda x: (x["line"], x["type"]))
    han_count = sum(is_han(ch) for ch in prose)
    visible_count = sum(not ch.isspace() for ch in prose)
    return {
        "file": str(path), "han_characters": han_count,
        "non_whitespace_characters": visible_count,
        "length_rule": "4000-5000 汉字（仅本项目第一至四卷自动启用）",
        "length_status": "BLOCKED" if "06-正文" in path.parts and any(
            part in ("第一卷", "第二卷", "第三卷", "第四卷") for part in path.parts
        ) and not 4000 <= han_count <= 5000 else "NOT_BLOCKED_BY_LENGTH",
        "potential_patterns": hits,
        "disclaimer": "候选文本模式只供人工上下文审查，不是AI生成识别或质量判定",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="+", help="章节 Markdown 路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式")
    args = parser.parse_args()
    data = [scan(p) for p in args.files]
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for item in data:
            print(f"{item['file']}: 汉字={item['han_characters']} "
                  f"非空白字符={item['non_whitespace_characters']} "
                  f"篇幅={item['length_status']} 候选表达={len(item['potential_patterns'])}处")
            for hit in item["potential_patterns"][:30]:
                print(f"  L{hit['line']} [{hit['type']}] {hit['context']}")
            if len(item["potential_patterns"]) > 30:
                print("  ...更多命中使用 --json 查看")
        print("提示：以上不是AI作者鉴定；未命中也不等于不存在问题。")

if __name__ == "__main__":
    main()
