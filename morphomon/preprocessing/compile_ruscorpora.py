# -*- coding: utf-8 -*-
import os
from morphomon.preprocessing.rus_corpora_parser import process_ruscorpora_file
from morphomon.utils import get_corpus_files

__author__ = 'egor'

#создание одного большого файла нкря в нашем формате


def process_ruscorpora(ruscorpora_dir, processed_dir, extension = "xml"):

    corpus_files = get_corpus_files(ruscorpora_dir)

    num = 0
    for rnc_file_name in corpus_files:
        print "Starting file", rnc_file_name


        out_file = os.path.join( processed_dir, os.path.basename( rnc_file_name ).replace('.{0}'.format(extension), '.txt' ) )

        if os.path.exists( out_file ):
            num +=1
            continue


        process_ruscorpora_file( rnc_file_name, out_file )
        num+=1
        print "{0} file processed. {1}%".format(rnc_file_name, num/(len(corpus_files)+0.0)*100 )




if __name__ == "__main__":
    process_ruscorpora( 'C:\\disamb_test\\mystem_xml', 'C:\\disamb_test\\mystem_txt' )