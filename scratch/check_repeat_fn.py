with open('.agents/skills/chinese-novelist/scripts/scan_ai_tone.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'def check_repeat_words' in l:
        for j in range(i, min(len(lines), i+30)):
            print(f'{j}: {lines[j]}')
        break
