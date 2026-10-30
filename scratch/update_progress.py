with open('07-创作记忆/当前写作进度.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.startswith("- **当前撰写章节**：第四卷第109章"):
        new_lines.append("- **当前撰写章节**：第四卷第110章《悬崖上的迫击炮》已完成并归档。\n")
        new_lines.append("- **本次交付**：\n")
        new_lines.append("  - 正文：`06-正文/第四卷/第110章.md`（3647汉字，处于 3000-6000 字区间）；\n")
        new_lines.append("  - 审稿：`08-审稿/第110章-去AI味四关报告.md`（G0-G4 四关 PASS，0 block 0 warn 纯净大满贯）、`08-审稿/第110章-综合质检报告.md`（综合评分 99.5/100，✅ APPROVED）；\n")
        new_lines.append("  - 纯文本阅读版：`06-正文-TXT/第四卷/第110章 悬崖上的迫击炮.txt` 及《崖边戍卒》第四卷.txt 合订本已同步导出。\n")
        new_lines.append("- **最新战局与人物动态**：\n")
        new_lines.append("  - 敌一百二十毫米重迫击炮群覆盖轰击断脊岩，石堡坍塌，老霍耳膜震裂，陈渡将严恪骨灰转移至死角；\n")
        new_lines.append("  - 林霰侦破敌炮兵在鹰嘴梁的猫眼激光逆反射，老霍以六零炮白磷发烟弹凌空测风，林霰千米外穿透敌潜望镜引爆电池组殉爆，全歼敌炮兵观察所，迫使敌重迫击炮群沉寂；\n")
        new_lines.append("  - 陈渡在石壁刻下第一道坚守凹痕，四人抢出宝贵的喘息整备时间。\n")
        new_lines.append("- **已完成第四卷章节（共 28 章，累计 107,521 汉字）**：\n")
        skip = True
        continue
    if skip:
        if line.strip().startswith("- [第083章]"):
            skip = False
            new_lines.append(line)
        continue
    if line.strip().startswith("- [第109章]"):
        new_lines.append(line)
        new_lines.append("  - [第110章](../06-正文/第四卷/第110章.md)：3647汉字。\n")
        continue
    if line.strip().startswith("- **下步承接**：第110章"):
        new_lines.append("- **下步承接**：第111章《炸不塌的石梁》（敌重型装甲工兵车抵近第一道石坎实施爆破清障与架桥作业；陈渡与老霍利用迫击炮盲区与反斜面实施反制，双方在两米八的石梁前沿展开焦土拉锯战）。\n")
        continue
    new_lines.append(line)

with open('07-创作记忆/当前写作进度.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('UPDATED_PROGRESS_110_OK')
