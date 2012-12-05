# -*- coding: utf-8 -*-
from lxml import etree

__author__ = 'egor'
import lxml.html
import codecs


def get_token_str_rep(token_el):
    #формат
    #токен\tлемма1=список грамм признаков\tлемма2=
    token_text = token_el.attrib['text']

    #зачем нужен v элемент?

    lemmas = token_el.findall(".//l")

    lemma_lst = []
    for lemma in lemmas:
        lemma_text = lemma.attrib["t"]
        gram_lst = []
        for gram in lemma.iter("g"):
            gram_t = gram.attrib['v']
            gram_lst.append( gram_t )

        lemma_str = u"{0}={1}".format( lemma_text, ','.join(gram_lst) )
        lemma_lst.append( lemma_str )

    result_str = u"{0}\t{1}\r\n".format(token_text,'\t'.join(lemma_lst))
    return result_str


def process_open_corpora_file( file, outfile ):
    out_f =  codecs.open( outfile, 'w', 'utf-8' )
    with open(file, 'r') as f:
        try:
            content = f.read()
            document = lxml.html.document_fromstring( content )

            tokens = document.xpath("//tokens")
            for token_list in tokens:
                #проходим по всем токенам
                for el in token_list.iter("token"):
                    out_f.write(get_token_str_rep( el ))
                out_f.write('\r\n')

        except Exception as e:
            raise Exception("Dom parsing exception %s" % (e))

if __name__=="__main__":
    import settings

    process_open_corpora_file( settings.CORPUS_DATA_ROOT + 'annot.opcorpora.no_ambig.xml', settings.CORPUS_DATA_ROOT + 'processed_opencorpora.txt' )