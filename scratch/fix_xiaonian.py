with open('06-正文/第四卷/第112章.md', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''开枪的是小年。

年轻的医务兵双手托着卡宾枪的护木，后背顶着石壁，脸色苍白得没有一丝血色，但那双平日里总带着一丝温和腼腆的眼眸中，此刻竟泛着前所未有的坚毅与决绝。'''

replacement = '''开枪的是小年。

年轻医务兵双手托着卡宾枪护木，后背紧抵石壁，面色虽因严寒透着惨白，眼神却沉静如铁。'''

if target in text:
    text = text.replace(target, replacement)
    with open('06-正文/第四卷/第112章.md', 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESSFULLY_REPLACED_XIAONIAN')
else:
    print('TARGET_NOT_FOUND')
