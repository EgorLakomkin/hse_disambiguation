# -*- coding: utf-8 -*-
import codecs
from morphomon.preprocessing.rus_corpora_parser import get_ruscorpora_content
from morphomon.utils import get_corpus_files

__author__ = 'egor'

#создание одного большого файла нкря в нашем формате


if __name__ == "__main__":
    corpus_dir = "/home/umka/distr/ruscorpora"
    corpus_files = get_corpus_files(corpus_dir)

    out_file_rnc =  codecs.open( "/home/umka/rnc.txt", 'w', 'utf-8' )
    num = 0
    for rnc_file in corpus_files:
	try:
		file_rnc_content = get_ruscorpora_content(rnc_file)
		out_file_rnc.write(file_rnc_content)
		num+=1
		print "{0} file processed. {1}%".format(rnc_file, num/(len(corpus_files)+0.0)*100 )
	except Exception as e:
		print "Exception occured in file {0}".format(rnc_file)
		print e
    out_file_rnc.close()
