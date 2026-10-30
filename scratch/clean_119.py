import re

path = r'C:\Users\yuqiang2\Documents\小说\测试小说\chinese-novelist\20261025-崖边戍卒\06-正文\第四卷\第119章.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

def replace_quotes(s):
    res = []
    in_quote = False
    for ch in s:
        if ch == '"':
            if not in_quote:
                res.append('“')
                in_quote = True
            else:
                res.append('”')
                in_quote = False
        else:
            res.append(ch)
    return ''.join(res)

text = replace_quotes(text)

# Replace unnecessary dashes
text = text.replace('轰——！', '轰！')
text = text.replace('嗵嗵嗵嗵——！', '嗵嗵嗵嗵！')
text = text.replace('呜——啾——！！', '呜——啾！')
text = text.replace('嗒、嗒嗒、嗒——', '嗒、嗒嗒、嗒……')
text = text.replace('噪声底层隐约混杂着某种极其遥远、断断续续的人声碎片——但那不是回执，更像是其他某个频段上溢漏过来的嘈杂通话', '噪声底层隐约混杂着某种极其遥远、断断续续的人声碎片，但那不是回执，更像是其他某个频段上溢漏过来的嘈杂通话')
text = text.replace('从前天后半夜老霍第一次发现战术校时频段被自己人压制，到刚才接战报告拍出去石沉大海——三次开机，三次无回。', '从前天后半夜老霍第一次发现战术校时频段被自己人压制，到刚才接战报告拍出去石沉大海，三次开机，三次无回。')
text = text.replace('不是够他求援——援军不会来。', '不是够他求援，援军不会来。')
text = text.replace('是够严恪的骨灰棺、够杜衡的签章令和够他们四个人的军籍，在将来的某一天，被人从故纸堆里翻出来时，上面写着的不是“擅离职守”或“弃阵逃亡”。', '是够严恪的骨灰棺、杜衡的签章令与他们四个人的军籍，在将来的某一天被人从故纸堆里翻出时，上面写的不是“擅离职守”或“弃阵逃亡”。')
text = text.replace('他在对面用手摇电话回了三个长音——收到、收到、收到！', '他在对面用手摇电话回了三个长音：收到、收到、收到！')
text = text.replace('“这条虚线是我们的底线后撤路——从石堡沿碎石斜坡向南，穿过峡谷拐角的暗沟，翻过乱石坡进入黑风沟松林。”', '“这条虚线是我们的底线后撤路：从石堡沿碎石斜坡向南，穿过峡谷拐角的暗沟，翻过乱石坡进入黑风沟松林。”')
text = text.replace('三道暗火青烟已经升起，边民全部通过——撤位判据中的人群线已经满足。', '三道暗火青烟已经升起，边民全部通过，撤位判据中的人群线已经满足。')
text = text.replace('划过天幕的弧线压得极扁——', '划过天幕的弧线压得极扁。')
text = text.replace('没有被破片击中，只有左肩被一块弹起的石块砸出一道钝痛。', '身上没有被破片直接咬中，唯独左肩被震飞的岩石硬生生砸出一阵发闷的钝痛。')
text = text.replace('按每分钟三十米的山地散兵跃进速度，还有不到九分钟。', '山地散兵跃进按每分钟三十米估算，敌前锋抵达只剩不到九分钟。')
text = text.replace('依旧严格依照弘毅野战通信条令，格式精短到极致：', '依旧按照弘毅野战通信条令，格式压到了最短：')
text = text.replace('的迫击炮阵地突然', '的迫击炮阵地蓦地')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Success!')

