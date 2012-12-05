# -*- coding: utf-8 -*-
from naive import NaiveAlgorithm
from collections import namedtuple
#from morphomon.utils import TokenRecord
import codecs, re

__author__ = 'egor'
#import settings

f_raw = 'fiction_mystem.txt'
f_disamb = codecs.open('test_naive.txt', 'w', 'utf-8')

naive_algo = NaiveAlgorithm(corpus_file = 'processed_fiction.txt')

def parse_token(line):
    tokens = []
    TokenRecord = namedtuple('TokenRecord', 'word, lemma, gram')
    m = re.search(u'([А-яЁЁ]+[-]?[А-яЁЁ]*?)', line)
    if m != None:
        m1 = re.findall(u'([А-яЁЁ]+[-]?[А-яЁЁ]*?)=([A-z0123,]*)', line)
        if m1 != None:
            for i in m1:
                x = TokenRecord(word = m.group(1), lemma = i[0], gram = i[1])
                tokens.append(x)
    return tokens

def get_tokens_from_corpora(corpus_file):
    corpus = codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\r\n')
    for token in data:
        token = token.strip()
        if len(token) > 0:
            yield parse_token(token)


#print naive_algo.get_token_freq( TokenRecord(word=u'в', lemma=u'в', gram = u'PR,') )
#for i in get_tokens_from_corpora(f_raw):
#    print naive_algo.remove_ambiguity(i)
#naive_algo.find_ambiguity_words()

for token in get_tokens_from_corpora(f_raw):
    print naive_algo.remove_ambiguity(token)

f_raw.close()
f_disamb.close()
