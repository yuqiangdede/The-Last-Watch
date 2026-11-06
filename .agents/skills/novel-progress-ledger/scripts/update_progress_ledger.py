#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按项目实际文件与可信审核记录构建四阶段创作进度台账。

只更新 05-写作计划/创作阶段进度.md 和 .csv；绝不修改正文、简写、
章节规划总表、正文终审记录及作者人工复核进度。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

CN = "一二三四五六七八九十"
VOLUMES = [f"第{ch}卷" for ch in CN[:9]] + ["第十卷"] + [
    "第十一卷", "第十二卷", "第十三卷", "第十四卷", "第十五卷",
    "第十六卷", "第十七卷", "第十八卷", "第十九卷", "第二十卷",
]
STAGES = ("卷纲", "章纲", "简写", "正文")
STATUS = {"通过", "不通过", "待复核", "待核实"}
ROOT_PLAN = "05-写作计划/章节规划总表.md"
REVIEW_REGISTER = "08-审稿/章节最终审核总表.csv"
EVENTS_FILE = "05-写作计划/阶段审核记录.json"
AUTHOR_CONFIRMATIONS_FILE = "05-写作计划/创作阶段状态确认.json"
MD_FILE = "05-写作计划/创作阶段进度.md"
CSV_FILE = "05-写作计划/创作阶段进度.csv"


def digest(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def read_events(root: Path) -> list[dict]:
    file = root / EVENTS_FILE
    if not file.exists():
        return []
    payload = json.loads(file.read_text(encoding="utf-8"))
    return payload.get("reviews", [])


def read_author_confirmations(root: Path) -> dict[int, dict]:
    """作者确认是流程完成状态，不得冒充含分数/报告/版本hash的专业审稿证据。"""
    file = root / AUTHOR_CONFIRMATIONS_FILE
    if not file.is_file():
        return {}
    payload = json.loads(file.read_text(encoding="utf-8"))
    confirmations = {}
    for key, stages in payload.get("volumes", {}).items():
        vol = int(key)
        if not 1 <= vol <= 20:
            raise ValueError(f"作者确认卷号非法：{vol}")
        if any(s not in STAGES for s in stages):
            raise ValueError(f"作者确认包含未知阶段：{vol}")
        confirmations[vol] = stages
    return confirmations


def stage_file(root: Path, volume: int, stage: str, unit: str, files: dict) -> Path | None:
    if stage == "卷纲":
        return root / "03-剧情/卷大纲.md"
    if stage == "章纲":
        return root / files["chapter_outline"]
    if stage == "简写":
        return root / files.get("brief", "") if files.get("brief") else None
    if stage == "正文":
        return root / files.get("prose", "") if files.get("prose") else None
    return None


def revision(events: list[dict], root: Path, volume: int, stage: str,
             unit: str, file: Path | None) -> dict | None:
    candidates = [e for e in events if e["volume"] == volume and
                  e["stage"] == stage and e["unit"] == ("卷" if stage == "卷纲" else unit)]
    if not candidates:
        return None
    latest = sorted(candidates, key=lambda e: e["reviewed_at"])[-1]
    report = root / latest.get("report", "")
    if not latest.get("report") or not report.is_file():
        return None
    if not file or not file.is_file():
        return None
    if latest.get("source_sha256") != digest(file):
        return dict(latest, stale=True)
    return latest


def parse_index(root: Path) -> dict[int, list[dict]]:
    """从只读生成索引获取1—6卷当前章位；不使用已暂停的旧卷章号。"""
    result = {i: [] for i in range(1, 21)}
    file = root / ROOT_PLAN
    if not file.is_file():
        return result
    vol = 0
    for line in file.read_text(encoding="utf-8").splitlines():
        m = re.match(r"## 第([一二三四五六七八九十]+)卷", line)
        if m:
            vol = next((i for i, name in enumerate(VOLUMES, 1)
                        if name.startswith("第" + m.group(1) + "卷")), 0)
        if vol not in range(1, 7) or not line.startswith("| 第"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not cells[1].startswith("第"):
            continue
        chapter, title, hint = cells[1], cells[2], cells[-1]
        num = re.search(r"第(\d{3})章", chapter)
        inter = re.search(r"第(\d+)章后插章", chapter)
        if num and not inter:
            unit = f"第{int(num.group(1)):03d}章"
            kind = "编号章"
        elif inter:
            unit = f"插章{int(inter.group(1))}"
            kind = "插章"
        else:
            continue
        result[vol].append(dict(unit=unit, kind=kind, title=title, hint=hint))
    return result


def current_outline(root: Path, vol: int) -> str:
    newer = f"03-剧情/章大纲/第{vol:02d}卷-新版.md"
    old = f"03-剧情/章大纲/第{vol:02d}卷.md"
    if vol in (7, 8, 9, 10) and (root / newer).is_file():
        return newer
    return old


def planned_new(root: Path, vol: int, outline: str) -> list[dict]:
    file = root / outline
    if not file.is_file() or vol < 7 or vol > 10 or "-新版" not in outline:
        return []
    content = file.read_text(encoding="utf-8")
    section = content.split("## 逐章章纲", 1)[-1].split("\n## ", 1)[0]
    result = []
    for line in section.splitlines():
        m = re.match(r"(\d+)\.\s+\*\*(.+?)\*\*", line)
        if m:
            result.append(dict(unit=f"卷内{int(m.group(1)):03d}章",
                               kind="暂定章", title=m.group(2), hint="design_pending_review"))
    return result


def planned_new_interludes(root: Path, vol: int) -> list[dict]:
    """新第七至十卷的插章章纲单独保存在新版插章设计稿，不能漏算。"""
    rel = "03-剧情/第七至十卷-新版第三方有限视角插章.md"
    file = root / rel
    if not file.is_file():
        return []
    tokens = {7: "七", 8: "八", 9: "九", 10: "十"}
    result = []
    for line in file.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([七八九十])卷(\d{3})后\s*\|\s*【([^】]+)】《([^》]+)》", line)
        if m and m.group(1) == tokens[vol]:
            result.append(dict(unit="插章" + m.group(2), kind="插章",
                               title=m.group(3) + "·" + m.group(4),
                               hint="design_pending_review",
                               chapter_outline=rel))
    return result


def find_artifacts(root: Path, vol: int, unit: str) -> dict:
    cn_vol = VOLUMES[vol - 1]
    brief_dir = root / f"05-写作计划/章节简写/第{vol:02d}卷"
    prose_dir = root / "06-正文" / cn_vol
    matches = []
    if re.fullmatch(r"第\d{3}章", unit) or re.fullmatch(r"卷内\d{3}章", unit):
        base = "第" + unit.removeprefix("卷内") if unit.startswith("卷内") else unit
        matches = sorted(brief_dir.glob(base + "*-简写.md"))
        prose = prose_dir / (base + ".md")
        prose_matches = [prose] if prose.is_file() else sorted(prose_dir.glob(base + "-*.md"))
    elif unit.startswith("插章"):
        number = unit.removeprefix("插章")
        matches = sorted(brief_dir.glob("插章" + number + "*-简写.md"))
        prose_matches = sorted(prose_dir.glob("插章" + number + "*md"))
        # 插046、插章46等历史命名也要精准匹配；不能错连其它章节。
        prose_matches += sorted(prose_dir.glob(f"插{int(number):03d}-*.md"))
        prose_matches = [p for p in prose_matches if p.is_file()]
    else:
        prose_matches = []
    return {
        "brief": matches[0].relative_to(root).as_posix() if matches else "",
        "prose": prose_matches[0].relative_to(root).as_posix() if prose_matches else "",
    }


def prose_reviews(root: Path) -> dict[str, dict]:
    file = root / REVIEW_REGISTER
    if not file.is_file():
        return {}
    result = {}
    with file.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            path = row.get("正文MD路径", "")
            report = row.get("审核报告", "")
            if not path or not report or not (root / report).is_file():
                continue
            old = result.get(path)
            if old is None or row.get("日期", "") >= old.get("日期", ""):
                result[path] = row
    return result


def audit_label(review: dict | None) -> str:
    if not review:
        return "未审"
    if review.get("stale"):
        return "需复审(源稿已改)"
    score = review.get("score", "")
    return "已审:" + str(review["result"]) + (f"({score}分)" if score != "" else "")


def state(exists: bool, audit: dict | None, author: dict | None = None,
          official: dict | None = None) -> str:
    """写作、审核分别计数；作者声明与实际有报告的审查结论明确区分。"""
    author = author or {}
    written = ("已写" if exists else
               ("已写（作者确认；稿件待核）" if author.get("written") is True else "未写"))
    if audit:
        reviewed = audit_label(audit)
    elif official:
        score = official.get("最终总分", "")
        reviewed = "有终审登记（" + (str(score) + "分；" if score else "") + "当前版本待核）"
    elif author.get("reviewed") is True:
        reviewed = "已审（作者确认；报告待关联）"
    elif author.get("reviewed") is False:
        reviewed = "待审（作者确认）"
    else:
        reviewed = "未审"
    return written + "／" + reviewed


def latest_review(staged: list[tuple[str, dict | None]], csv_row: dict | None) -> str:
    candidates = [(r["reviewed_at"], st + ":" + audit_label(r))
                  for st, r in staged if r]
    if csv_row:
        score = csv_row.get("最终总分") or "未记录"
        lit = csv_row.get("文学质量") or "待核实"
        ai = csv_row.get("AI专项") or "待核实"
        eng = csv_row.get("工程") or "未验收"
        candidates.append((csv_row.get("日期", ""),
                           f"正文:{score}分；文学{lit}；AI味{ai}；工程{eng}（原记录，版本待核）"))
    return sorted(candidates)[-1][1] if candidates else "无正式审核记录"


def build(root: Path) -> tuple[str, str]:
    events = read_events(root)
    authors = read_author_confirmations(root)
    plans = parse_index(root)
    finals = prose_reviews(root)
    for vol in range(7, 11):
        outline = current_outline(root, vol)
        plans[vol] = planned_new(root, vol, outline) + planned_new_interludes(root, vol)
    rows = []
    stats = []
    vol_text = (root / "03-剧情/卷大纲.md").read_text(encoding="utf-8") if (root / "03-剧情/卷大纲.md").exists() else ""
    for vol in range(1, 21):
        outline = current_outline(root, vol)
        outline_file = root / outline
        volume_file = root / "03-剧情/卷大纲.md"
        volume_exists = bool(vol_text and f"| {VOLUMES[vol-1]} |" in vol_text)
        vol_audit = revision(events, root, vol, "卷纲", "卷", volume_file)
        author = authors.get(vol, {})
        chapters = plans[vol]
        counters = {stage: [0, 0] for stage in STAGES}
        if volume_exists or author.get("卷纲", {}).get("written") is True:
            counters["卷纲"][0] = 1
        if ((vol_audit and not vol_audit.get("stale")) or
                author.get("卷纲", {}).get("reviewed") is True):
            counters["卷纲"][1] = 1
        for chapter in chapters:
            unit = chapter["unit"]
            artifacts = find_artifacts(root, vol, unit)
            files = dict(chapter_outline=chapter.get('chapter_outline', outline), **artifacts)
            stage_exists = {
                "卷纲": volume_exists,
                "章纲": (root / files["chapter_outline"]).is_file(),
                "简写": bool(files["brief"]),
                "正文": bool(files["prose"]),
            }
            existing = finals.get(files["prose"]) if files["prose"] else None
            reviews = {}
            for stage in STAGES:
                file = stage_file(root, vol, stage, unit, files)
                reviews[stage] = revision(events, root, vol, stage, unit, file)
                if stage != "卷纲":
                    claim = author.get(stage, {})
                    if stage_exists[stage] or claim.get("written") is True:
                        counters[stage][0] += 1
                    if (claim.get("reviewed") is True or
                            (reviews[stage] and not reviews[stage].get("stale")) or
                            (stage == "正文" and existing and claim.get("reviewed") is not False)):
                        counters[stage][1] += 1
            last = latest_review(list(reviews.items()), existing)
            if vol <= 4 and author:
                last = (last + "；" if last != "无正式审核记录" else "") + "四阶段审核均已完成（作者确认；未关联的分数及报告待核）"
            elif vol == 5 and author:
                last = (last + "；" if last != "无正式审核记录" else "") + "卷纲、章纲已审；简写、正文待审（作者确认）"
            rows.append({
                "卷": VOLUMES[vol-1], "篇目": unit, "类型": chapter["kind"],
                "标题": chapter["title"],
                **{stage: state(stage_exists[stage], reviews[stage],
                                 author.get(stage, {}), existing if stage == "正文" else None)
                   for stage in STAGES},
                "最新审核结果": last,
                "章纲路径": files["chapter_outline"], "简写路径": files["brief"],
                "正文路径": files["prose"],
                "终审报告": (existing or {}).get("审核报告", ""),
            })
        stats.append((vol, volume_exists, vol_audit, counters, len(chapters), outline))
    title = (json.loads((root / "novel.project.json").read_text(encoding="utf-8"))
             .get("title", "小说") if (root / "novel.project.json").exists() else "小说")
    lines = [
        f"# 《{title}》四阶段创作进度台账（自动生成）",
        "",
        "> 本表由现行章纲、稿件、实际审核报告、历史正文终审CSV及作者明确确认的流程状态生成；禁止手改。",
        "> 作者确认“审核完成”只证明流程状态，**不等于取得正式报告、具体成绩或本次版本复审通过**；未知结论、分数和源稿路径不补造。",
        "> 旧章纲停用不计新章，未分章卷仅显示卷级进度；作者人工复核进度表独立且绝不自动修改。",
        "",
        "## 一、20卷总览",
        "",
        "| 卷 | 有效篇目数 | 卷纲(写/审) | 章纲(写/审) | 简写(写/审) | 正文(写/审) | 章纲版本 |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for vol, has_vol, vol_audit, cnt, n, outline in stats:
        lines.append(f"| {VOLUMES[vol-1]} | {n if n else '未定'} | "
                     f"{cnt['卷纲'][0]}/{cnt['卷纲'][1]} | "
                     + " | ".join(f"{cnt[s][0]}/{cnt[s][1]}" for s in ("章纲", "简写", "正文"))
                     + f" | {outline if (root / outline).exists() else '缺失'} |")
    lines += [
        "", "## 二、逐章明细", "",
        "说明：每阶段「已写／未审」「已写／已审:结论(分数)」分别表示生产与质量审核；",
        "有源稿而旧审核源版本不一致时标「需复审」。本页只索引，不替代正式审稿报告。",
        "",
        "| 卷 | 篇目 | 标题 | 卷纲 | 章纲 | 简写 | 正文 | 最新审核结果 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        def esc(value):
            return str(value).replace("|", "／").replace("\n", " ")
        page_row = dict(row)
        target = row["正文路径"] or row["简写路径"] or row["章纲路径"]
        if target:
            page_row["篇目"] = f"[{row['篇目']}](../{target})"
        lines.append("| " + " | ".join(esc(page_row[c]) for c in (
            "卷", "篇目", "标题", "卷纲", "章纲", "简写", "正文", "最新审核结果")) + " |")
    lines += ["", "## 三、数据与使用", "",
              f"- 最新逐章清单：{CSV_FILE}；真实审稿报告事件：{EVENTS_FILE}；作者流程状态确认：{AUTHOR_CONFIRMATIONS_FILE}。",
              f"- 正文终审来源：{REVIEW_REGISTER}（含正式报告路径和旧版本说明）。",
              "- 有效审核需真实报告文件和受审稿源的SHA256；修改源稿不抹旧分数，但自动提示需复审。",
              "- 更新：python .agents/skills/novel-progress-ledger/scripts/update_progress_ledger.py --project-dir .",
              "- 校验：同命令加 --check。每次完成写作、审核、阶段跨越或章纲重排后必须更新。",
              "- 未启动的卷可有卷纲而没有具体篇目；不能为填表补造章数与编号。",
              ""]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else [
        "卷", "篇目", "类型", "标题", *STAGES, "最新审核结果",
        "章纲路径", "简写路径", "正文路径", "终审报告"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "\n".join(lines), stream.getvalue()


def record(root: Path, args: argparse.Namespace) -> None:
    if args.stage not in STAGES or args.result not in STATUS:
        raise ValueError("阶段或审核结论无效")
    if not 1 <= args.volume <= 20:
        raise ValueError("卷号应为1—20")
    unit = "卷" if args.stage == "卷纲" else args.unit
    if not unit:
        raise ValueError("非卷纲审核必须提供 --unit")
    if not args.report or Path(args.report).is_absolute() or ".." in Path(args.report).parts:
        raise ValueError("审核报告应为仓库内相对路径")
    report = root / args.report
    if not report.is_file():
        raise ValueError("正式审核报告不存在，不能登记已审")
    plan = parse_index(root)
    if args.volume in range(7, 11):
        plan[args.volume] = planned_new(root, args.volume, current_outline(root, args.volume)) + planned_new_interludes(root, args.volume)
    chapter = next((c for c in plan[args.volume] if c["unit"] == unit), None)
    if args.stage != "卷纲" and chapter is None:
        raise ValueError("现行章纲里找不到篇目标识，检查卷号/编号/新版章纲")
    artifacts = find_artifacts(root, args.volume, unit)
    files = dict(chapter_outline=(chapter or {}).get('chapter_outline', current_outline(root, args.volume)), **artifacts)
    file = stage_file(root, args.volume, args.stage, unit, files)
    if not file or not file.is_file():
        raise ValueError("受审核源稿文件不存在，不能登记已审")
    if args.score is not None and not (0 <= args.score <= 100):
        raise ValueError("评分必须处于0—100")
    events = read_events(root)
    events.append({
        "volume": args.volume, "unit": unit, "stage": args.stage,
        "result": args.result, "score": args.score if args.score is not None else "",
        "report": args.report, "source": file.relative_to(root).as_posix(),
        "source_sha256": digest(file),
        "reviewed_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    })
    (root / EVENTS_FILE).write_text(
        json.dumps({"schema_version": 1, "reviews": events}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--check", action="store_true", help="校验表格与源文件一致；不写入")
    parser.add_argument("--record-review", action="store_true", help="登记本轮有报告的有效审核并刷新")
    parser.add_argument("--volume", type=int)
    parser.add_argument("--unit", help="如 第144章、插章149、卷内001章")
    parser.add_argument("--stage", choices=STAGES)
    parser.add_argument("--result", choices=sorted(STATUS))
    parser.add_argument("--score", type=float)
    parser.add_argument("--report", help="本轮实际审核报告的仓库相对路径")
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    if args.check and args.record_review:
        parser.error("--check 与 --record-review 不可同时使用")
    if args.record_review:
        if args.volume is None or not args.stage or not args.result:
            parser.error("--record-review 需要 --volume/--stage/--result/--report")
        record(root, args)
    markdown, machine_csv = build(root)
    expected = {MD_FILE: markdown, CSV_FILE: machine_csv}
    if args.check:
        out_of_date = [p for p, body in expected.items()
                       if not (root / p).exists() or
                       (root / p).read_text(encoding="utf-8") != body]
        if out_of_date:
            print("FAIL 台账未同步：" + ", ".join(out_of_date))
            return 1
        print("PASS 四阶段进度台账与当前证据同步")
        return 0
    for rel, body in expected.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body, encoding="utf-8")
    print(f"已刷新：{MD_FILE}、{CSV_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
