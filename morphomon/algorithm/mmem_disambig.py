# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
from morphomon.utils import N_rnc_pos, dump_object, get_tokens_from_file, EOS_TOKEN, get_tokens_from_directory, N_default, load_object, remove_ambiguity_dir
from maxent import MaxentModel

__author__ = 'egor'


class MMEMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, N_filter_func = N_default):
        self.filter_func = N_filter_func
        self.me = MaxentModel()

    def load_memm_model(self, filename):
        self.me.load( filename  )

    def init(self):
        pass

    def compute_features( self, sentence ,  i):
        if i > 0:
            yield "previous-tag={0}".format(   sentence[i - 1].gram  )
        if i == 0:
            yield "first-tag=True"

    def train_model(self, corpus_dir ):
        self.me.begin_add_event()
        sentence = []
        for token in get_tokens_from_directory(corpus_dir = corpus_dir, N_filter_func= self.filter_func):
            if token[0] == EOS_TOKEN:
                for i,token in enumerate( sentence ):
                    word_features = list( self.compute_features( sentence, i ) )
                    token_gram = token.gram
                    token_gram = token_gram.encode('utf-8')
                    self.me.add_event(word_features, token_gram )
                sentence = []
                continue

            sentence.append( token[0] )

        self.me.end_add_event()
        self.me.train()


    def save_model(self, filename):
        self.me.save( filename )

    def remove_ambiguity_file(self, file, outfile):
        out_f =  codecs.open( outfile, 'w', 'utf-8' )
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if len(token) == 1 and token[0] == EOS_TOKEN:
                no_ambig_tokens = self.remove_ambiguity( sentence )
                for no_ambig_token in no_ambig_tokens:
                    out_f.write( u"{0}\t{1}={2}\r\n".format(no_ambig_token[0], 'nolemma', no_ambig_token[1] ) )
                out_f.write('\r\n')
                sentence = []
                continue

            sentence.append( (token[0].word, token) )
        out_f.close()

    def remove_ambiguity_dir(self, dir):
        pass

    def remove_ambiguity(self, variants):
        pass



if __name__=="__main__":


    #memm_algo = MMEMAlgorithm(N_filter_func= N_rnc_pos)
    #memm_algo.train_model( corpus_dir= "/home/egor/disamb_test/test_gold/" , )
    #memm_algo.save_model( r"/home/egor/disamb_test/memm_pos.dat" )
    memm_algo = MMEMAlgorithm(N_filter_func= N_rnc_pos)
    memm_algo.load_memm_model( r"/home/egor/disamb_test/memm_pos.dat"  )
    remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/mystem_txt",output_dir = r"/home/egor/disamb_test/memm_pos", algo = memm_algo )
