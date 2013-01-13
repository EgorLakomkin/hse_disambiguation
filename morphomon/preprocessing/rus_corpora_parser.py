# -*- coding: utf-8 -*-
import codecs
import xml.parsers.expat
#парсер для НКРЯ в наш формат
#код позаимстован отсюда:

class RNCFileParser:
    def __init__(self,codepage):
        self._parser = xml.parsers.expat.ParserCreate(codepage)
        self._parser.StartElementHandler = self.start_element
        self._parser.EndElementHandler = self.end_element
        self._parser.CharacterDataHandler = self.char_data
        self._word_began_flag = False

    def start_element(self, name, attr):
        if name == 'ana':
            self._info = attr
        if name == 'w':
            self._word_began_flag = True

    def end_element(self, name):
        if name == 'se':
            self.out_f.write('\r\n')
            self._sentence = []
            self._wordforms = []
            self._cdata = ''
        elif name == 'w':
            lemmas_str = []
            for lemma in self._wordforms:
                lex = lemma['lex']
                gram = lemma['gr']
                lemma_str = u"{0}={1}".format( lex, ','.join(gram.split(' ') ) )
                lemmas_str.append( lemma_str )

            wf = self._cdata
            wf = wf.replace('`', '').strip()

            result_str = u"{0}\t{1}\r\n".format(wf,'\t'.join(lemmas_str))
            if len(result_str)>1:
                self.out_f.write(result_str)

            self._wordforms = []
            self._cdata = ''
            self._word_began_flag = False
        elif name == 'ana':
            self._wordforms.append( self._info )

    def char_data(self, content):
        if self._word_began_flag:
            self._cdata += content

    def read(self, input_file, output_file):
        self.input_f = open(input_file, 'r')
        self.out_f =  codecs.open( output_file, 'w', 'utf-8' )

        self._sentences = []
        self._sentence = []
        self._cdata = ''
        self._info = ''
        self._wordforms = []
        self._parser.ParseFile(self.input_f)

        self.input_f.close()
        self.out_f.close()

def process_ruscorpora_file( file, outfile ):
    rnc_parser = RNCFileParser("cp1251")
    rnc_parser.read(file, outfile)

if __name__ == "__main__":
    in_file_test = "/home/egor/rnc.xml"
    out_file = "/home/egor/rnc.txt"
    process_ruscorpora_file(in_file_test, out_file)
