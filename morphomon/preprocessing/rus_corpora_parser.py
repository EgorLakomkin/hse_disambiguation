# -*- coding: utf-8 -*-
import codecs
import xml.parsers.expat
#парсер для НКРЯ в наш формат
#код позаимстован отсюда:
#https://github.com/irokez/Pyrus/blob/master/src/rnc.py
class Reader:
    def __init__(self):
        self._parser = xml.parsers.expat.ParserCreate('UTF-8')
        self._parser.StartElementHandler = self.start_element
        self._parser.EndElementHandler = self.end_element
        self._parser.CharacterDataHandler = self.char_data

    def start_element(self, name, attr):
        if name == 'ana':
            self._info = attr

    def end_element(self, name):
        if name == 'se':
            self._sentences.append(self._sentence)
            self._sentence = []
        elif name == 'w':
            self._sentence.append((self._cdata, self._info))
        elif name == 'ana':
            self._cdata = ''

    def char_data(self, content):
        self._cdata += content

    def read(self, filename, codepage):
        f = codecs.open( filename, 'r', codepage )
        content = f.read().encode('utf-8')
        f.close()

        self._sentences = []
        self._sentence = []
        self._cdata = ''
        self._info = ''

        self._parser.Parse(content)

        return self._sentences

def get_ruscorpora_content( file ):
    #возврашаем строку в нашем формате
    try:
        sentences = Reader().read( file, "cp1251" )
        return_str = ""
        for sentence in sentences:
            for word in sentence:
                accent = word[0].index('`') + 1 if '`' in word[0] else 0
                word_form = word[0].replace('`', '')
                lemma = word[1]['lex']
                gram = word[1]['gr']
                lemma_str = u"{0}={1}".format( lemma, ','.join(gram.split(' ') ) )
                word_form_str = u"{0}\t{1}\r\n".format(word_form,lemma_str)
                return_str += word_form_str
            return_str+='\r\n'
        return_str+='\r\n'
        return return_str

    except Exception as e:
        raise Exception("Dom parsing exception %s" % (e))

def process_ruscorpora_file( file, outfile ):
    out_f =  codecs.open( outfile, 'w', 'utf-8' )
    try:
        sentences = Reader().read( file, "cp1251" )
        for sentence in sentences:
            for word in sentence:
                accent = word[0].index('`') + 1 if '`' in word[0] else 0
                word_form = word[0].replace('`', '')
                lemma = word[1]['lex']
                gram = word[1]['gr']
                lemma_str = u"{0}={1}".format( lemma, ','.join(gram.split(' ') ) )
                result_str = u"{0}\t{1}\r\n".format(word_form,lemma_str)
                out_f.write(result_str)
            out_f.write('\r\n')

    except Exception as e:
        raise Exception("Dom parsing exception %s" % (e))

if __name__ == "__main__":
    in_file_test = "/home/umka/distr/ruscorpora/post1950/anecdota/gostin.xhtml"
    out_file = "/home/umka/gostin_test.txt"
    process_ruscorpora_file(in_file_test, out_file)