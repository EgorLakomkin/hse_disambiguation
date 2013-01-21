# -*- coding: utf-8 -*-
__author__ = 'egor'
from morphomon.algorithm.naive import NaiveAlgorithm
from morphomon.utils import TokenRecord
import settings

naive_algo = NaiveAlgorithm(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_opencorpora.txt')

print naive_algo.get_token_freq( TokenRecord(word=u'в', lemma=u'в', gram = u'PREP') )
print naive_algo.remove_ambiguity_sentence( [TokenRecord(word=u'этом', lemma=u'это', gram = u'NPRO,neut,sing,loct'),
                                    TokenRecord(word=u'этом', lemma=u'этот', gram = u'ADJF,Apro,masc,sing,loct')] )
naive_algo.find_ambiguity_words()