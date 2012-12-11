import codecs, re, os
from subprocess import Popen

corpora = ['processed_anketa.txt', 'processed_opencorpora.txt', 'processed_fiction.txt']
for i in corpora:
    f = codecs.open(i, 'r', 'utf-8')
    fOut = codecs.open('./lemmer/texts/clean/' + i[10:], 'w', 'utf-8')
    fOut.write('<?xml version="1.0" '
                'encoding="utf-8"?>\r\n'
                '<html><body>\r\n')
    for line in f:
        m = re.search(u'([А-яЁё]+?[-]?[А-яЁё]*?)\t', line)
        if m != None:
            stroka = m.group(1) + u'\r\n'
            fOut.write(stroka)
    fOut.write('</body>\r\n</html>')
    fOut.close()

    do_bat_path = os.path.abspath('./lemmer/processing')
    p = Popen(do_bat_path + '/do.bat', cwd=do_bat_path)
    stdout, stderr = p.communicate()

    f.close()

