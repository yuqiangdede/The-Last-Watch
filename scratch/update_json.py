import json

path = r'c:\Users\yuqiang2\Documents\小说\测试小说\chinese-novelist\20261025-崖边戍卒\02-写作计划.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = []
for ch in data.get('chapters', []):
    if ch.get('chapterNumber') in [115, 116, 117, 118, 119]:
        ch['status'] = 'completed'
        updated.append(ch.get('chapterNumber'))

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Updated chapters to completed:', updated)

