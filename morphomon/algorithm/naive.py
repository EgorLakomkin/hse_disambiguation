# -*- coding: utf-8 -*-
from morphomon.utils import get_tokens_from_corpora


__author__ = 'egor'





class NaiveAlgorithm(object):
    #реализация наивного алгоритма
    def __init__(self, corpus_file):
        self.corpus_dict = {}
        for token in get_tokens_from_corpora( corpus_file ):
            if token.word not in self.corpus_dict:
                self.corpus_dict[token.word] = {}
            if token.lemma not in self.corpus_dict[token.word]:
                self.corpus_dict[token.word][token.lemma] = {}
            if token.gram not in self.corpus_dict[token.word][token.lemma]:
                self.corpus_dict[token.word][token.lemma][token.gram] = 1
            else:
                self.corpus_dict[token.word][token.lemma][token.gram] += 1

    def find_ambiguity_words(self):
        for word in self.corpus_dict:
            if len( self.corpus_dict[word] ) > 1:
                print "ambiguity word %s" % ( word )

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