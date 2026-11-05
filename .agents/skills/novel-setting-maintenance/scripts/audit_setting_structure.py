#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小说设定工程：只读巡检材料覆盖、分卷章纲结构、旧路径及关键词证据。

本脚本只提供确定性候选，不会宣称完成剧情/人物/世界观的语义审阅。
用法：python .agents/skills/novel-setting-maintenance/scripts/audit_setting_structure.py --project-dir . --expected-volumes 20 --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SOURCE_DIRS = ("01-世界观", "02-人物", "03-剧情", "04-文风", "05-写作计划", "07-创作记忆")
SOURCE_EXTENSIONS = {".md", ".json", ".yaml", ".yml"}
ROOT_CONTEXT = ("AGENTS.md", "README.md", "novel.project.json", "02-写作计划.json", "03-文风基准.md", "99-章节摘要.md")
PROTECTED_DIRS = ("06-正文", "06-正文-TXT", "09-归档")
BRIEF_PREFIX = "05-写作计划/章节简写/"
INDEX_FILE = "05-写作计划/章节规划总表.md"
OUTLINE_DIR = "03-剧情/章大纲"
VOLUME_NAV = "03-剧情/卷大纲.md"
MAIN_OUTLINE = "03-剧情/全书主线.md"
OLD_PATH = re.compile(r"05-写作计划/(?:卷大纲\.md|章大纲/第\d{1,2}卷\.md)")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CHAPTER_OLD = re.compile(r"^\|\s*第(\d+)章\s*\|")
CHAPTER_NEW = re.compile(r"^\|\s*\*\*(\d{3})\s*/\s*\d{3}\*\*\s*\|")
COUNT = re.compile(r"^[-*]\s*编号章节数\s*[:：]\s*(.+)$", re.M)
NUMBER = re.compile(r"(?:共|拟定|确定|预计|^|\*\*)\s*(\d+)\s*(?:个|章|篇|\*\*)?")
REVISION_TIME = re.compile(r"最后修订时间\s*[:：]\s*(.+)")


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def editable(rel: str) -> bool:
    if rel == INDEX_FILE or rel == "07-创作记忆/作者人工复核进度.md":
        return False
    if rel == "05-写作计划/章节简写" or rel.startswith(BRIEF_PREFIX):
        return False
    return not any(rel == p or rel.startswith(p + "/") for p in PROTECTED_DIRS)


def locate_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirname in SOURCE_DIRS:
        folder = root / dirname
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS and editable(relative(path, root)):
                files.append(path)
    files.extend(root / item for item in ROOT_CONTEXT if (root / item).is_file())
    return sorted(set(files))


def classify(rel: str) -> str:
    if rel.startswith(OUTLINE_DIR + "/"):
        return "chapter_outline"
    if rel == VOLUME_NAV:
        return "volume_navigation"
    if rel == MAIN_OUTLINE:
        return "book_outline"
    if rel.startswith("03-剧情/"):
        return "volume_detail_or_plot"
    if rel.startswith("02-人物/"):
        return "character"
    if rel.startswith("01-世界观/"):
        return "world"
    if rel.startswith("07-创作记忆/"):
        return "dynamic_memory"
    if rel.startswith("05-写作计划/"):
        return "plan_or_task"
    if "/" not in rel:
        return "project_context"
    return "story_rules"


def parse_chapters(content: str) -> tuple[list[tuple[int, int]], list[int]]:
    rows = []
    for line_no, line in enumerate(content.splitlines(), 1):
        match = CHAPTER_OLD.match(line) or CHAPTER_NEW.match(line)
        if match:
            rows.append((int(match.group(1)), line_no))
    seen: set[int] = set()
    duplicates: list[int] = []
    for number, _ in rows:
        if number in seen:
            duplicates.append(number)
        seen.add(number)
    return rows, duplicates


def planned_count(content: str) -> int | None:
    match = COUNT.search(content)
    if not match:
        return None
    # 不把“另5篇插章”误判成常规章节数。
    text = match.group(1).replace("**", "")
    exact = re.fullmatch(r"\s*(\d+)\s*", text)
    if exact:
        return int(exact.group(1))
    count = re.search(r"(?:共|拟定|已确定|计划)?\s*(\d+)\s*个?编号", text)
    if count:
        return int(count.group(1))
    count = re.search(r"(?:共|拟定|已确定|计划)?\s*(\d+)\s*(?:个|篇)?常规章", text)
    if count:
        return int(count.group(1))
    count = re.search(r"(?:共|拟定|已确定|计划)?\s*(\d+)\s*章", text)
    if count:
        return int(count.group(1))
    return None


def link_targets(root: Path, path: Path, text: str):
    """内部相对 .md 链接仅作为待核线索；模板、示例和旧记录可能合法。"""
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in LINK.finditer(line):
            raw = match.group(1).split("#", 1)[0].split("?", 1)[0]
            if not raw.lower().endswith(".md") or "://" in raw or raw.startswith("#"):
                continue
            target = (path.parent / raw).resolve()
            if not target.is_relative_to(root):
                yield {"line": line_no, "target": raw, "reason": "链接超出项目根目录"}
            elif not target.is_file():
                yield {"line": line_no, "target": raw, "reason": "目标不存在（可能是历史说明）"}


def scan(root: Path, expected_volumes: int | None = None, terms: list[str] | None = None) -> dict:
    root = root.resolve()
    terms = [x for x in (terms or []) if x.strip()]
    files = locate_source_files(root)
    issues: list[dict] = []
    inventory: list[dict] = []
    evidence: dict[str, list[dict]] = defaultdict(list)
    volume_records: list[dict] = []
    nav_path = root / VOLUME_NAV
    nav_text = nav_path.read_text(encoding="utf-8") if nav_path.is_file() else ""
    nav_numbers = {int(m) for m in re.findall(r"章大纲/第(\d{1,2})卷\.md", nav_text)}
    found_volumes = {int(m.group(1)): p for p in (root / OUTLINE_DIR).glob("第*卷.md")
                     if (m := re.fullmatch(r"第(\d+)卷\.md", p.name))} if (root / OUTLINE_DIR).is_dir() else {}
    if expected_volumes is not None:
        target_volumes = set(range(1, expected_volumes + 1))
    else:
        target_volumes = nav_numbers | set(found_volumes)
    if not nav_path.is_file():
        issues.append({"severity": "error", "code": "MISSING_VOLUME_NAV", "path": VOLUME_NAV, "message": "缺失卷纲导航"})
    if not (root / MAIN_OUTLINE).is_file():
        issues.append({"severity": "error", "code": "MISSING_BOOK_OUTLINE", "path": MAIN_OUTLINE, "message": "缺失全书主线"})
    for vol in sorted(target_volumes):
        path = found_volumes.get(vol)
        expected_path = f"{OUTLINE_DIR}/第{vol:02d}卷.md"
        if path is None:
            issues.append({"severity": "error", "code": "MISSING_CHAPTER_OUTLINE", "path": expected_path,
                           "volume": vol, "message": "章纲不存在；不能声称已覆盖该卷"})
            volume_records.append({"volume": vol, "path": expected_path, "status": "missing"})
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append({"severity": "error", "code": "UNREADABLE", "path": relative(path, root), "message": str(exc)})
            volume_records.append({"volume": vol, "path": relative(path, root), "status": "unreadable"})
            continue
        rows, duplicates = parse_chapters(content)
        expected = planned_count(content)
        for number in duplicates:
            issues.append({"severity": "error", "code": "DUPLICATE_CHAPTER", "path": relative(path, root),
                           "volume": vol, "message": f"重复编号章节：{number}"})
        if expected is not None and rows and len(rows) != expected:
            issues.append({"severity": "error", "code": "CHAPTER_COUNT_MISMATCH", "path": relative(path, root),
                           "volume": vol, "message": f"声明{expected}章，表格识别{len(rows)}章；需核对章纲格式"})
        if not rows:
            issues.append({"severity": "info", "code": "PLANNED_NOT_SPLIT", "path": relative(path, root),
                           "volume": vol, "message": f"未识别逐章表格；声明章数为{expected if expected is not None else '待定'}，该卷不算已完成逐章审阅"})
        if nav_numbers and vol not in nav_numbers:
            issues.append({"severity": "candidate", "code": "MISSING_NAV_LINK", "path": VOLUME_NAV,
                           "volume": vol, "message": "卷纲导航未链接此卷章纲"})
        volume_records.append({"volume": vol, "path": relative(path, root), "status": "read",
                               "declared_count": expected, "recognized_chapters": len(rows),
                               "chapter_ids": [n for n, _ in rows]})

    for path in files:
        rel = relative(path, root)
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append({"severity": "error", "code": "UNREADABLE", "path": rel, "message": str(exc)})
            continue
        match = REVISION_TIME.search(content)
        inventory.append({"path": rel, "type": classify(rel),
                          "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                          "last_revision_label": match.group(1).strip() if match else None})
        if not match and rel.startswith(("01-世界观/", "02-人物/", "03-剧情/")):
            issues.append({"severity": "candidate", "code": "MISSING_REVISION_LABEL", "path": rel,
                           "message": "未发现最后修订时间；不能猜测历史修改时间"})
        for line_no, line in enumerate(content.splitlines(), 1):
            if OLD_PATH.search(line):
                issues.append({"severity": "candidate", "code": "LEGACY_OUTLINE_PATH", "path": rel,
                               "line": line_no, "excerpt": line[:180], "message": "旧章纲/卷纲路径；需区分历史记录与当前引用"})
            for term in terms:
                if term in line:
                    evidence[term].append({"path": rel, "line": line_no, "excerpt": line[:240]})
        for broken in link_targets(root, path, content):
            issues.append({"severity": "candidate", "code": "UNRESOLVED_MD_LINK", "path": rel,
                           "line": broken["line"], "message": broken["reason"], "target": broken["target"]})
    for term in terms:
        evidence.setdefault(term, [])
    return {
        "schema_version": 1,
        "mode": "deterministic_read_only_candidates; not_semantic_review",
        "project_root": str(root),
        "expected_volumes": sorted(target_volumes),
        "volume_coverage": volume_records,
        "inventory": inventory,
        "inventory_count": len(inventory),
        "summary": {"errors": sum(i["severity"] == "error" for i in issues),
                    "candidates": sum(i["severity"] == "candidate" for i in issues),
                    "info": sum(i["severity"] == "info" for i in issues),
                    "volumes_read": sum(v["status"] == "read" for v in volume_records),
                    "volumes_with_chapters": sum(v.get("recognized_chapters", 0) > 0 for v in volume_records),
                    "volumes_unexpanded": sum(v["status"] == "read" and v.get("recognized_chapters", 0) == 0 for v in volume_records),
                    "chapter_rows_recognized": sum(v.get("recognized_chapters", 0) for v in volume_records)},
        "issues": issues,
        "term_evidence": dict(evidence),
        "limits": ["仅检查结构、路径与指定关键词证据；所有语义冲突须由Agent实读裁决",
                   "不会修改正文、TXT、章节简写、规划或设定原文件",
                   "无法读取的文件与不能识别的章纲格式必须显式报告，不能按已扫描通过处理"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--expected-volumes", type=int, default=None,
                        help="强制覆盖1..N卷；《崖边戍卒》应传入20")
    parser.add_argument("--term", action="append", default=[], help="需逐文件定位的设定/角色/势力关键词；可重复")
    parser.add_argument("--output", help="保存JSON报告（只允许可写的审稿报告路径，不写正文/简写）")
    parser.add_argument("--check", action="store_true", help="发现确定性结构错误时退出码为2")
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    if args.expected_volumes is not None and args.expected_volumes < 1:
        parser.error("--expected-volumes 必须大于0")
    if not root.is_dir():
        parser.error("项目根目录不存在")
    result = scan(root, args.expected_volumes, args.term)
    if args.output:
        target = Path(args.output)
        if not target.is_absolute():
            target = root / target
        target = target.resolve()
        if not target.is_relative_to(root / "08-审稿"):
            parser.error("--output 仅允许写入项目的 08-审稿/ 内，避免覆盖设定/正文/简写")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"已写只读巡检结果：{target}", file=sys.stderr)
    print(json.dumps({"mode": result["mode"], "summary": result["summary"],
                      "volume_coverage": [{k: v for k, v in row.items() if k != "chapter_ids"}
                                          for row in result["volume_coverage"]],
                      "issue_count": len(result["issues"]), "report_saved": bool(args.output)},
                     ensure_ascii=False, indent=2))
    return 2 if args.check and result["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
