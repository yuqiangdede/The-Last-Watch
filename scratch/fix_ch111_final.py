with open('06-正文/第四卷/第111章.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 替换狂暴
text = text.replace('狂暴气浪将两人凌空掀出马道边缘', '翻卷气浪将两人凌空掀出马道边缘')
text = text.replace('爆炸引发的狂暴冲击波像一记重拳', '暴烈的冲击波似重锤砸落')
text = text.replace('狂暴的气浪甚至卷上了三号岩嘴', '倒灌的热浪甚至卷上了三号岩嘴')
text = text.replace('狂暴的巨响自石坎底部爆发。', '沉闷的巨响自石坎底部爆发。')

# 替换开头同构句子
old_passage = '''鹰嘴梁顶端那团殉爆火光刚刚暗下，谷底深处便传来一阵教人牙酸的金属绞扭动静。

三十吨往上的重型钢铁履带正以极低转速强行碾过碎石路面，传出一阵沉闷粗粝的碾压声。履带齿与花岗岩石板反复磨挫，整条断脊岩石梁的岩脉深处都在随之发出低频震颤。'''

new_passage = '''鹰嘴梁顶端那团殉爆火光刚刚暗下，深谷底部就钻出一阵教人牙酸的金属绞扭声。

那是三十吨往上的重履带正以极低转速啃过碎石。沉闷粗粝的碾压动静里，履带齿反复刮蹭花岗岩石板，震得整条断脊岩石梁的深处岩脉嗡嗡发颤。'''

text = text.replace(old_passage, new_passage)

with open('06-正文/第四卷/第111章.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('FIXED_REPEAT_AND_HOMO_OK')
