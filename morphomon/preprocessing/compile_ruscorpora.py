# -*- coding: utf-8 -*-
import codecs
import os
from morphomon.preprocessing.rus_corpora_parser import process_ruscorpora_file
from morphomon.utils import get_corpus_files

__author__ = 'egor'

#создание одного большого файла нкря в нашем формате


def process_ruscorpora(ruscorpora_dir, processed_dir):

    corpus_files = get_corpus_files(ruscorpora_dir)

    num = 0
    for rnc_file_name in corpus_files:
        print "Starting file", rnc_file_name
        rnc_file = open( rnc_file_name, 'r' )

        out_file = os.path.join( processed_dir, os.path.basename( rnc_file_name ).replace('.xhtml', '_{0}.txt'.format( num ) ) )

        if os.path.exists( out_file ):
            num +=1
            continue

        out_file_rnc =  codecs.open( out_file, 'w', 'utf-8' )

        process_ruscorpora_file( rnc_file, out_file_rnc )
        num+=1
        print "{0} file processed. {1}%".format(rnc_file, num/(len(corpus_files)+0.0)*100 )

        out_file_rnc.close()


if __name__ == "__main__":
    process_ruscorpora( '/home/egor/ruscorpora', '/home/egor/processed_ruscorpora' )