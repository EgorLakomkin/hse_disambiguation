# -*- coding: utf-8 -*-
import codecs
import os
from random import choice

__author__ = 'egor'
from morphomon.utils import EOS_TOKEN, get_word_ending, get_tokens_from_directory, dump_object, N_default, N_rnc_pos, get_tokens_from_file, load_object, get_corpus_files, remove_ambiguity_dir
from collections import defaultdict


def default_float():
    return defaultdict( float )

class NaiveAlgorithm(object):
    #реализация наивного алгоритма
    def __init__(self, corpus_dir, N_func = N_default):
        self.corpus_dict = defaultdict( default_float )
        self.filter_func = N_func
        for token in get_tokens_from_directory( corpus_dir, N_filter_func = self.filter_func ):
            if token != [EOS_TOKEN]:
                if len(token) > 1:
                   print "Ambiguity in corpus"
                   print "Pick random token"
                token = choice(token)
                token_word = token.word
                token_word_ending = get_word_ending( token_word )
                token_gram = token.gram
                self.corpus_dict[ token_word_ending ][token_gram]+=1

    def find_ambiguity_words(self):
        for word in self.corpus_dict:
            if len( self.corpus_dict[word] ) > 1:
                print "ambiguity word %s" % ( word )

    def get_token_freq(self, token):
        pass


    def remove_ambiguity_sentence(self, variants):
        #на вход приходит

        for variant in variants:
            word = variant[0]
            token_variants = variant[1]
            for token in token_variants:
                max_variant_val = -1
                max_variant = None
                val = self.corpus_dict[  get_word_ending(word)  ][token.gram]
                if val > max_variant_val:
                    max_variant = token
            yield (max_variant.word, max_variant.gram)

    def remove_ambiguity_file(self, file, outfile):
        out_f =  codecs.open( outfile, 'w', 'utf-8' )
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if len(token) == 1 and token[0] == EOS_TOKEN:
                no_ambig_tokens = self.remove_ambiguity_sentence( sentence )
                for no_ambig_token in no_ambig_tokens:
                    out_f.write( u"{0}\t{1}={2}\r\n".format(no_ambig_token[0], 'nolemma', no_ambig_token[1] ) )
                out_f.write('\r\n')
                sentence = []
                continue

            sentence.append( (token[0].word, token) )
        out_f.close()



if __name__ == "__main__":

    #naive_algo = NaiveAlgorithm( corpus_dir = r"C:\disamb_test\gold", N_func= N_rnc_pos )
    #dump_object( r"C:\disamb_test\naive.dat" , naive_algo  )
    naive_algo = load_object( r"C:\disamb_test\naive.dat" )
    #naive_algo.remove_ambiguity_file(r"C:\disamb_test\mystem_txt\_rbk2_2140.txt", r"C:\disamb_test\algo_output\_rbk2_2140.txt" )
    remove_ambiguity_dir(corpus_dir = r"C:\disamb_test\mystem_txt",output_dir = r"C:\disamb_test\naive_output", algo = naive_algo )