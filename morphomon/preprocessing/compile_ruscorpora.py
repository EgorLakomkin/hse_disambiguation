# -*- coding: utf-8 -*-
import codecs
import os
from morphomon.preprocessing.rus_corpora_parser import process_ruscorpora_file
from morphomon.utils import get_corpus_files

__author__ = 'egor'


def process_ruscorpora(ruscorpora_dir, processed_dir):

    corpus_files = get_corpus_files(ruscorpora_dir)
    print "Processing {0} files".format( len(corpus_files) )
    num = 0
    for rnc_file_name in corpus_files:
        print "Starting file", rnc_file_name

        out_file_name = os.path.join( processed_dir, os.path.basename( rnc_file_name ).replace('.xml', '_{0}.txt'.format( num ) ) )

        if os.path.exists( out_file_name ):
            num +=1
            continue


        process_ruscorpora_file( rnc_file_name, out_file_name )
        num+=1
        print "{0} file processed. {1}%".format(rnc_file_name, num/(len(corpus_files)+0.0)*100 )



if __name__ == "__main__":
    process_ruscorpora( '/home/egor/test/mystem_xml', '/home/egor/test/mystem_txt' )