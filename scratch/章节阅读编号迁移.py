from pathlib import Path
import json
import re
import shutil
from datetime import datetime

root = Path.cwd()
volumes = {'第一卷': (1, 20), '第二卷': (21, 39), '第三卷': (40, 82), '第四卷': (83, 143)}
changes = []
for volume, (start, end) in volumes.items():
    for path in (root / '06-正文' / volume).glob('第*章.md'):
        match = re.fullmatch(r'第(\d+)章\.md', path.name)
        if not match:
            continue
        number = int(match.group(1))
        if not start <= number <= end:
            raise ValueError(f'超出卷范围: {path}')
        text = path.read_text(encoding='utf-8-sig')
        heading = re.match(r'^(#\s+第)(\d+)(章)', text)
        if not heading:
            print(f'正文缺少标题，暂不改写: {path}')
            continue
        if int(heading.group(2)) not in (number, number - start + 1):
            raise ValueError(f'标题与原编号不一致: {path}')
        updated = text[:heading.start(2)] + f'{number-start+1:03d}' + text[heading.end(2):]
        if text != updated:
            changes.append((path, updated))

plan_path = root / '02-写作计划.json'
plan = json.loads(plan_path.read_text(encoding='utf-8-sig'))
for chapter in plan.get('chapters', []):
    vol = chapter.get('volume')
    n = chapter.get('chapterNumber')
    if vol not in volumes or not isinstance(n, int):
        continue
    start, end = volumes[vol]
    if not start <= n <= end:
        raise ValueError(f'计划章号与分卷不符: {vol} {n}')
    local = n - start + 1
    chapter['volumeChapterNumber'] = local
    if isinstance(chapter.get('title'), str):
        chapter['title'] = re.sub(r'^第\d+章', f'第{local:03d}章', chapter['title'])

backup = root / 'scratch' / ('章节编号迁移备份-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
shutil.copy2(plan_path, backup / plan_path.name)
shutil.copytree(root / '06-正文-TXT', backup / '06-正文-TXT')
for path, text in changes:
    original = backup / path.relative_to(root)
    original.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, original)
    path.write_text(text, encoding='utf-8', newline='\n')
plan['chapterNumbering'] = {'reader': '每卷从001开始，volumeChapterNumber为卷内章号', 'chapterNumber': '保留原全书连续编号作为内部唯一定位号；引用须注明卷名与编号体系'}
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(f'更新正文标题 {len(changes)} 章；计划记录 {len(plan.get("chapters", []))} 章；备份：{backup}')
