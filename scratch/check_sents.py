with open('06-正文/第四卷/第111章.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sents = [s.strip() for s in re.split(r'[。！？\n]+', text) if len(s.strip()) > 5]
for i in range(12):
    c = sents[i].count('，')
    print(f'{i}: (逗号={c}, 长度={len(sents[i])}) {sents[i]}')
