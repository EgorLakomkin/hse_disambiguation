# -*- coding: utf-8 -*-
import codecs
import xml.parsers.expat
#парсер для НКРЯ в наш формат
#код позаимстован отсюда:
#https://github.com/irokez/Pyrus/blob/master/src/rnc.py
class Reader:
    def __init__(self,codepage):
        self._parser = xml.parsers.expat.ParserCreate(codepage)
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
            self._sentence.append(  (self._cdata, self._wordforms)  )
            self._wordforms = []
            self._cdata = ''
        elif name == 'ana':
            self._wordforms.append( self._info )

    def char_data(self, content):
        self._cdata += content

    def read(self, filename, ):
        f = open( filename, 'r' )


        self._sentences = []
        self._sentence = []
        self._cdata = ''
        self._info = ''
        self._wordforms = []
        self._parser.ParseFile(f)

        return self._sentences

def get_ruscorpora_content( file ):
    #возврашаем строку в нашем формате
    try:
        return_str = ""
        sentences = Reader("cp1251" ).read( file)
        for sentence in sentences:
            for words in sentence:
                word_form = words[0]
                word_form = word_form.replace('`', '').strip()

                lemmas = words[1]
                lemmas_str = []
                for lemma in lemmas:
                    lex = lemma['lex']
                    gram = lemma['gr']
                    lemma_str = u"{0}={1}".format( lex, ','.join(gram.split(' ') ) )
                    lemmas_str.append( lemma_str )

                result_str = u"{0}\t{1}\r\n".format(word_form,'\t'.join(lemmas_str))
                return_str += result_str
            return_str +='\r\n'
        return_str+='\r\n'
    except Exception as e:
        raise Exception("Dom parsing exception %s" % (e))
    return return_str


class RNCFileParser:
    def __init__(self,codepage):
        self._parser = xml.parsers.expat.ParserCreate(codepage)
        self._parser.StartElementHandler = self.start_element
        self._parser.EndElementHandler = self.end_element
        self._parser.CharacterDataHandler = self.char_data


    def start_element(self, name, attr):
        if name == 'ana':
            self._info = attr

    def end_element(self, name):
        if name == 'se':
            self.out_f.write('\r\n')
            self._sentence = []
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
        elif name == 'ana':
            self._wordforms.append( self._info )

    def char_data(self, content):
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
    in_file_test = "/home/egor/test.xml"
    out_file = "/home/egor/fiction.txt"
    process_ruscorpora_file(in_file_test, out_file)
    #print get_ruscorpora_content("/home/egor/fiction.xml")