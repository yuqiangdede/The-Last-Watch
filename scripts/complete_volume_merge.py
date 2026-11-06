#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合卷完成后的可重复工程校正。文件名：scripts/complete_volume_merge.py

只更改简写元信息、已写正文首行章号、TXT阅读合订本和生成型进度台账；
不重写人物台词、叙事正文，不伪造质量评分或重置历史审核。
用法：
 python scripts/complete_volume_merge.py --apply
 python scripts/complete_volume_merge.py --check
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS = ROOT / "05-写作计划/章节简写"
PROSE = ROOT / "06-正文/第七卷-海路尽头"
TXT = ROOT / "06-正文-TXT/第七卷-海路尽头"
STAMP = "2026-11-06 17:30:00 +08:00"
INSERTS = {6, 13, 19, 27}


def expected_brief(path: Path, volume: int) -> str:
    source = path.read_text(encoding="utf-8")
    m = re.match(r"第(\d{3})章-简写\.md$", path.name)
    inter = re.match(r"插章(\d{3})-", path.name)
    if not m and not inter:
        return source
    number = int((m or inter).group(1))
    if m:
        title = source.splitlines()[0]
        title = re.sub(
            r"^# 第[七八九十]+卷第\d{3}章",
            f"# 第{'七' if volume == 7 else '八'}卷第{number:03d}章",
            title,
        )
        source = title + "\n" + "\n".join(source.split("\n")[1:])
    else:
        source = re.sub(
            r"^# (插章[^\n]*?)｜第[七八九十]+卷第\d{3}章后",
            lambda x: f"# {x.group(1)}｜第{'七' if volume == 7 else '八'}卷第{number:03d}章后",
            source,
            count=1,
            flags=re.MULTILINE,
        )
    source = re.sub(r"最后修订时间：[^\n]+", "最后修订时间：" + STAMP, source, count=1)
    lines = source.splitlines()
    marker = f"> 合卷校验状态：现行第{volume}卷第{number:03d}章{'后插章' if inter else ''}，历史评分保留但合卷版待重新审核；不得以旧卷原审核通过替代现行门禁。"
    if marker not in lines:
        first = next((i for i, line in enumerate(lines) if "最后修订时间：" in line), 0)
        lines.insert(first + 1, marker)
    source = "\n".join(lines)
    if not source.endswith("\n"):
        source += "\n"
    return source


def expected_prose(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    n = int(path.stem[1:4])
    if not 234 <= n <= 247:
        return source
    return re.sub(r"^# 第\d{3}章", f"# 第{n:03d}章", source, count=1)


def make_txt() -> dict[Path, str]:
    if not TXT.exists():
        raise FileNotFoundError(TXT)
    heading = "《崖边戍卒》\n第七卷-海路尽头\n\n"
    before: list[str] = []
    after: list[str] = []
    for n in range(1, 31):
        matches = sorted(TXT.glob(f"第{n:03d}章 *.txt"))
        if len(matches) != 1:
            raise ValueError(f"第七卷卷内{n:03d}章TXT缺失或重名：{len(matches)}")
        file = matches[0]
        title = file.stem
        content = file.read_text(encoding="utf-8-sig").strip()
        unit = f"{title}\n\n{content}\n\n"
        chunk = before if n <= 16 else after
        chunk.append(unit)
        if n in INSERTS:
            ins = sorted(TXT.glob(f"插章{n:03d}-*.txt"))
            if len(ins) != 1:
                raise ValueError(f"第七卷第{n:03d}章后插章缺失或重名：{len(ins)}")
            ins_name = ins[0].stem
            ins_body = ins[0].read_text(encoding="utf-8-sig").strip()
            chunk.append(f"{ins_name}\n\n{ins_body}\n\n")
    first = heading + "".join(before).rstrip() + "\n"
    second = heading + "".join(after).rstrip() + "\n"
    combined = heading + "".join(before + after).rstrip() + "\n"
    return {
        TXT / "《崖边戍卒》第七卷-海路尽头-上段001-016.txt": first,
        TXT / "《崖边戍卒》第七卷-海路尽头-下段017-030.txt": second,
        TXT / "《崖边戍卒》第七卷-海路尽头.txt": combined,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--apply", action="store_true", help="执行校正并重新生成进度台账")
    group.add_argument("--check", action="store_true", help="只读校验；出现差异则退出非零")
    args = parser.parse_args()
    expected: dict[Path, str] = {}
    for volume in (7, 8):
        directory = BRIEFS / f"第{volume:02d}卷"
        main_briefs = sorted(directory.glob("第???章-简写.md"))
        inserts = sorted(directory.glob("插章???-*-简写.md"))
        if len(main_briefs) != (30 if volume == 7 else 28) or len(inserts) != 4:
            raise ValueError(f"第{volume}卷简写数量错误：{len(main_briefs)}+{len(inserts)}")
        for file in main_briefs + inserts:
            expected[file] = expected_brief(file, volume)
    prose = sorted(PROSE.glob("第???.md"))
    insert_prose = sorted(PROSE.glob("插章*.md"))
    if len(prose) != 30 or len(insert_prose) != 4:
        raise ValueError(f"合卷第七卷正文数量错误：{len(prose)}+{len(insert_prose)}")
    for file in prose:
        expected[file] = expected_prose(file)
    expected.update(make_txt())

    changed = []
    for path, content in expected.items():
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing == content:
            continue
        changed.append(path)
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"校验文件{len(expected)}个，发现差异{len(changed)}个")
    if args.check and changed:
        for file in changed[:25]:
            print("需更新:", file.relative_to(ROOT))
        return 1
    ledger = ROOT / ".agents/skills/novel-progress-ledger/scripts/update_progress_ledger.py"
    if ledger.is_file():
        command = [sys.executable, str(ledger), "--project-dir", str(ROOT)]
        if args.check:
            command.append("--check")
        result = subprocess.run(command, check=False, cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
