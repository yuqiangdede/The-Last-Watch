with open('.agents/skills/chinese-novelist/scripts/scan_ai_tone.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'G0-04' in l and i > 120:
        for j in range(max(0, i-5), min(len(lines), i+30)):
            print(f'{j}: {lines[j]}')
        break
