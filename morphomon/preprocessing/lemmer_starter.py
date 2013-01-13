import codecs, re, os
from subprocess import Popen

corpora = ['rnc.txt']

for i in corpora:
    f = codecs.open(i, 'r', 'utf-8')
    fOut = codecs.open('./lemmer/texts/clean/' + i, 'w', 'utf-8')
    fOut.write('<?xml version="1.0" '
                'encoding="utf-8"?>\r\n'
                '<html><body>\r\n')
    for line in f:
        m = re.search(u'(.*?)\t', line)
        m1 = re.search(u'^\r\n', line)
        if m != None:
            x = re.sub(u'<', u'', m.group(1), flags = re.U)
            x = re.sub(u'>', u'', x, flags = re.U)
            x = re.sub(u'&', u'', x, flags = re.U)
            stroka = x + u'\r\n'
            fOut.write(stroka)
        if m1 != None:
            fOut.write('.' + '\r\n')
    fOut.write('</body>\r\n</html>')
    fOut.close()

do_bat_path = os.path.abspath('./lemmer/processing')
p = Popen(do_bat_path + '/do.bat', cwd=do_bat_path)
stdout, stderr = p.communicate()

f.close()



