with open('.agents/skills/chinese-novelist/scripts/scan_ai_tone.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'REPEAT_WORDS' in l:
        for j in range(max(0, i-2), min(len(lines), i+15)):
            print(f'{j}: {lines[j]}')
        break
