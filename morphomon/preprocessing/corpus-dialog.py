import codecs, re

f1 = codecs.open('rueval-tagged.txt', 'r', 'utf-8')
f2 = codecs.open('rueval-our-version.txt', 'w', 'utf-8')

for line in f1:
    m = re.search(u'([А-я]+?[-]?[А-я]*?)\t(.*?)\t(.*?)\t(.*?)\t', line)
    m1 = re.search(u'[\.?!]', line)
    if m != None:
        stroka_new = m.group(1)+'\t'+m.group(2)+'='+m.group(3)+','+m.group(4)+'\r\n'
        f2.write(stroka_new)
    elif m1 != None:
        f2.write(u'\r\n')

f1.close()
f2.close()
