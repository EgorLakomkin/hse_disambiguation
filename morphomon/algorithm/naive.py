# -*- coding: utf-8 -*-
from collections import namedtuple
import codecs
import re

__author__ = 'egor'



TokenRecord = namedtuple('TokenRecord', 'word, lemma, gram')
#паттерн токена для корпуса со снятой омонимией
token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'

def parse_token(line):
    match = re.match(token_pattern, line)
    return TokenRecord(word = match.group('token_name'), lemma = match.group('token_lemma'),
                                    gram = match.group('token_gram'))

def get_tokens(corpus_file):
    corpus =  codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\n')
    for token in data:
        if len(token) > 0:
            yield parse_token(token)

class NaiveAlgorithm(object):
    #реализация наивного алгоритма
    def __init__(self, corpus_file):
        self.corpus_dict = {}
        for token in get_tokens( corpus_file ):
            if token.word not in self.corpus_dict:
                self.corpus_dict[token.word] = {}
            if token.lemma not in self.corpus_dict[token.word]:
                self.corpus_dict[token.word][token.lemma] = {}
            if token.gram not in self.corpus_dict[token.word][token.lemma]:
                self.corpus_dict[token.word][token.lemma][token.gram] = 1
            else:
                self.corpus_dict[token.word][token.lemma][token.gram] += 1


    def get_token_freq(self, token):
        if token.word in self.corpus_dict:
            return self.corpus_dict[token.word][token.lemma][token.gram]
        return 0

    def remove_ambiguity(self, variants):
        #на вход приходит
        max_variant_val = -1
        max_variant = None
        for variant in variants:
            val = self.corpus_dict[variant.word][variant.lemma][variant.gram]
            if val > max_variant_val:
                max_variant = variant
        return max_variant