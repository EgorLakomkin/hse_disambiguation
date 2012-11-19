import codecs, re

f1 = codecs.open('rueval_2010_goldstandard_tagged.txt', 'r', 'utf-8')
f2 = codecs.open('rueval-our-version.txt', 'w', 'utf-8')

brev = 0
for line in f1:
    m = re.search(u'([А-яЁё]+?[-]?[А-яЁё]*?)\t(.*?)\t(.*?)\t(.*?)\t', line)
    m1 = re.search(u'[\.?!]', line)
    m2 = re.search(u'.*abbrev.*', line)
    if m1 != None:
        if brev != 1:
            f2.write(u'\n')
    if m2 != None:
        brev = 1
    else:
        brev = 0
    if m != None:
        stroka_new = m.group(1)+'\t'+m.group(2)+'='+m.group(3)+','+m.group(4)+'\n'
        f2.write(stroka_new)
        
f1.close()
f2.close()
