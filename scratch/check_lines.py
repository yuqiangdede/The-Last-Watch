with open('06-正文/第四卷/第106章.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines[105:125], 106):
    print(f'{i}: {line.strip()}')

