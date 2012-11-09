# -*- coding: utf-8 -*-
from morphomon.algorithm.naive import NaiveAlgorithm, TokenRecord

__author__ = 'egor'
import settings

naive_algo = NaiveAlgorithm(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_opencorpora.txt')

print naive_algo.get_token_freq( TokenRecord(word=u'в', lemma=u'в', gram = u'PREP') )
print naive_algo.remove_ambiguity( [TokenRecord(word=u'в', lemma=u'в', gram = u'PREP')] )