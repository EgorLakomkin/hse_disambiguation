import re
import codecs

#токен\tлемма1=список грамм признаков\tлемма2=                                


m = u'(<w>.*?</w>)'
m1 = u'<ana lex="(.*?)" gr="(.*?)"></ana>'
m2 = u'.*</ana>(.*)</w>'
n = u'</se>'

f = codecs.open('rueval.xml', 'r','cp1251')
o = codecs.open('rueval_mystem.txt', 'w', 'utf-8')
data = f.readlines()

for i in range(0,len(data)):
    s = re.search(m,data[i])
    s1 = re.search (n, data [i])
    if s != None:
        s2 = re.search(m2, s.group(1))
        if s2 != None:
            o.write(s2.group(1) + u'\t')
        s3 = re.findall(m1, s.group(1))
        if s3 != None:
            for j in range(0,len(s3)):
                para = s3[j]
                lemma = para[0]
                gram = para[1]
                string = lemma + '=' + gram + '\t'
                o.write(string)
        o.write('\r\n')

    if s1 != None:
        o.write('\r\n')
                            
f.close()
o.close()

