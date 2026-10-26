#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从正文 Markdown 生成逐章 TXT 阅读版与分卷合订本（仅标准库）。"""
import argparse
import re
from pathlib import Path

CHAPTER = re.compile(r"^第(\d+)章(?:[-_ ].*)?\.md$")
SCENE = re.compile(r"^(?:\*\s*\*\s*\*+|-{3,}|_{3,})$")

def order(path):
    return int(CHAPTER.match(path.name).group(1)), path.name

def inline(text):
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    for p in [r"\x60([^\x60]*)\x60", r"\*\*([^*]+)\*\*", r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"__([^_]+)__", r"~~([^~]+)~~"]:
        text = re.sub(p, r"\1", text)
    return text.strip()

def chapter_txt(markdown, fallback):
    title, body, seen = fallback, [], False
    for line in markdown.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").split("\n"):
        value = line.strip()
        if not value:
            continue
        if SCENE.fullmatch(value):
            if body and body[-1] != "":
                body.append("")
            continue
        h = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", value)
        if h:
            value = h.group(1).strip()
            if not seen and re.match(r"^第\d+章", value):
                title, seen = inline(value), True
                continue
        body.append("\u3000\u3000" + inline(value))
    while body and body[-1] == "":
        body.pop()
    return title + "\n\n" + "\n".join(body) + "\n"

def write(path, text, check):
    old = path.read_text(encoding="utf-8-sig") if path.is_file() else None
    if old == text:
        return True
    if check:
        print("不同步:", path)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("生成:", path)
    return True

def main():
    p = argparse.ArgumentParser(description="同步/校验小说 TXT 阅读副本")
    p.add_argument("--project-dir", default=".")
    p.add_argument("--source", default=None, help="Markdown 正文目录")
    p.add_argument("--output", default=None, help="TXT 输出目录")
    p.add_argument("--book-title", default=None)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--chapter", help="同步指定章节与对应合订本")
    mode.add_argument("--all", action="store_true", help="同步所有章节（默认）")
    p.add_argument("--check", action="store_true", help="只校验，不写入")
    a = p.parse_args()
    root = Path(a.project_dir).resolve()
    src = (root / (a.source or ("06-正文" if (root / "06-正文").is_dir() else "正文"))).resolve()
    out = (root / a.output).resolve() if a.output else src.with_name(src.name + "-TXT")
    if not src.is_dir():
        p.error("正文目录不存在: " + str(src))
    if src == out or src in out.parents or out in src.parents:
        p.error("输出目录不能与源目录重叠")
    chapters = sorted([f for f in src.rglob("*.md") if CHAPTER.fullmatch(f.name)], key=lambda f: (str(f.parent.relative_to(src)), order(f)))
    if not chapters:
        p.error("没有找到 Markdown 章节")
    if a.chapter:
        selected = (root / a.chapter).resolve()
        if selected not in chapters:
            p.error("指定章节不在正文目录中: " + str(selected))
        volumes, selected_files = {selected.parent}, {selected}
    else:
        volumes, selected_files = {f.parent for f in chapters}, set(chapters)
    readme = root / "README.md"
    match = re.search(r"《([^》\n]+)》", readme.read_text(encoding="utf-8-sig")) if readme.is_file() else None
    book = a.book_title or (match.group(1) if match else root.name)
    ok = True
    for volume in sorted(volumes):
        members = sorted([f for f in chapters if f.parent == volume], key=order)
        relative = volume.relative_to(src)
        texts = []
        for md in members:
            content = chapter_txt(md.read_text(encoding="utf-8-sig"), md.stem)
            texts.append(content.rstrip("\n"))
            if md in selected_files:
                ok = write(out / relative / (md.stem + ".txt"), content, a.check) and ok
        label = volume.name if relative != Path(".") else "正文"
        combined = "《" + book + "》\n" + label + "\n\n" + "\n\n".join(texts) + "\n"
        ok = write(out / relative / ("《" + book + "》" + label + ".txt"), combined, a.check) and ok
        if not a.chapter:
            names = {f.stem + ".txt" for f in members}
            folder = out / relative
            if folder.is_dir():
                for stale in folder.glob("第*章*.txt"):
                    if re.match(r"^第\d+章", stale.name) and stale.name not in names:
                        if a.check:
                            print("过期副本:", stale)
                            ok = False
                        else:
                            stale.unlink()
    if ok:
        print("TXT 同步校验通过：%d 章，%d 卷" % (len(selected_files), len(volumes)))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
