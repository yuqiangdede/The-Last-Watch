with open('07-创作记忆/当前写作进度.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.startswith("- **当前撰写章节**：第四卷第111章"):
        new_lines.append("- **当前撰写章节**：第四卷第112章《第二声号角》已完成并归档。\n")
        new_lines.append("- **本次交付**：\n")
        new_lines.append("  - 正文：`06-正文/第四卷/第112章.md`（4017汉字，处于 3000-6000 字区间）；\n")
        new_lines.append("  - 审稿：`08-审稿/第112章-去AI味四关报告.md`（G0-G4 四关 PASS，0 block 0 warn 纯净大满贯）、`08-审稿/第112章-综合质检报告.md`（综合评分 99.5/100，✅ APPROVED）；\n")
        new_lines.append("  - 纯文本阅读版：`06-正文-TXT/第四卷/第030章 第二声号角.txt` 及《崖边戍卒》第四卷.txt 合订本已同步导出。\n")
        new_lines.append("- **最新战局与人物动态**：\n")
        new_lines.append("  - 敌精锐山地突击步兵吹响双响铜号发起波浪强攻，中路以组合钛铝防弹盾与发烟罐推进，两翼沿垂直绝壁攀岩包抄；\n")
        new_lines.append("  - 林霰带伤狙杀攀岩组与敌狙击手，小年冷静击落贴近石堡投弹的敌兵并输送弹药，陈渡贴地反弹手雷破盾并刺刀见红将敌士官长推落悬崖，老霍单手重机枪封死石梁入口；\n")
        new_lines.append("  - 小队击退敌步兵集团冲锋，弹药基本见底；陈渡在石壁刻下第三道凹痕（已坚守六小时），身后两万边民全线通过最险峡管区向西南深山纵深疏散。\n")
        new_lines.append("- **已完成第四卷章节（共 30 章，累计 116,112 汉字 · 达成全书卷内三十章里程碑）**：\n")
        skip = True
        continue
    if skip:
        if line.strip().startswith("- [第083章]"):
            skip = False
            new_lines.append(line)
        continue
    if line.strip().startswith("- [第111章]"):
        new_lines.append(line)
        new_lines.append("  - [第112章](../06-正文/第四卷/第112章.md)：4017汉字。\n")
        continue
    if line.strip().startswith("- **下步承接**：第112章"):
        new_lines.append("- **下步承接**：第113章《石缝里的雪水》（午后短暂间隙，四人清点仅剩无几的残存弹药，搜集敌尸物资补给；老霍融化积雪煮水润喉，小年检视严恪骨灰红封条；敌第二波次重装喷火兵与迫击炮混合纵队在山下集结，决战杀局悄然压境）。\n")
        continue
    new_lines.append(line)

with open('07-创作记忆/当前写作进度.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('UPDATED_PROGRESS_112_OK')
