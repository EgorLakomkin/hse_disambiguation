# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
import math
from morphomon.algorithm.statistics import train_B_corpus
from morphomon.utils import N_rnc_pos, dump_object, get_tokens_from_file, EOS_TOKEN, get_tokens_from_directory, N_default, load_object, remove_ambiguity_dir, get_word_ending
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

    def compute_features( self, sentence , i, prev_label, analysises):
        if prev_label is not None:
            yield "previous-tag={0}".format(   prev_label )

        word_form = sentence[i]
        word_ending = get_word_ending( word_form, enging_length = 3 )
        yield "word-ending={0}".format( word_ending.encode('utf-8') )

        if analysises is not None:
            for analysis in analysises:
                yield "has_analysis={0}".format( analysis )

    def train_model(self, corpus_dir ):
        self.me.begin_add_event()
        #self.B = train_B_corpus(corpus_dir = corpus_dir,N_filter_func = N_filter_func)
        sentence = []
        for token in get_tokens_from_directory(corpus_dir = corpus_dir, N_filter_func= self.filter_func):
            if token[0] == EOS_TOKEN:
                words = [token.word for token in sentence]
                labels = [token.gram for token in sentence]
                for i,token in enumerate( sentence ):

                    word_features = list( self.compute_features( sentence = words, i = i , prev_label= labels[ i - 1 ] if i >0 else None, analysises = None) )
                    token_gram = token.gram
                    token_gram = token_gram.encode('utf-8')
                    self.me.add_event(word_features, token_gram )
                sentence = []
                continue

            sentence.append( token[0] )

        self.me.end_add_event()
        self.me.train()


    def save_model(self, memm_filename, B_stat_filename):
        self.me.save( memm_filename )
        #dump_object( B_stat_filename, self.B )

    def remove_ambiguity_file(self, file, outfile):
        out_f =  codecs.open( outfile, 'w', 'utf-8' )
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if len(token) == 1 and token[0] == EOS_TOKEN:
                if len(sentence)>0:
                    no_ambig_tokens = self.remove_ambiguity( sentence )
                    for no_ambig_token in no_ambig_tokens:
                        out_f.write( u"{0}\t{1}={2}\r\n".format(no_ambig_token[0], 'nolemma', no_ambig_token[1] ) )
                    out_f.write('\r\n')
                    sentence = []
                    continue
                else:
                    sentence = []
                    continue

            sentence.append( (token[0].word, token) )
        out_f.close()

    def remove_ambiguity_dir(self, dir):
        pass

    def remove_ambiguity(self, variants):
        """
        Структура variants = [ (word_form, [tokens ]), (...) , (  ) ]
        """
        words = [variant[0]  for variant in variants]
        analysises = [[token.gram for token in variant[1]]  for variant in variants ]

        viterbi_layers = [ None for i in xrange(len(words)) ]

        viterbi_backpointers = [ None for i in xrange(len(words) + 1) ]

        # Compute first layer directly.
        viterbi_layers[0] = self.me.eval_all(list(self.compute_features(sentence=words, i = 0 , prev_label= None, analysises = analysises[0] ) ) )
        if len(viterbi_layers[0]) ==0 :
            pass
        filtered_viterbi_layer = dict( (k, v) for k, v in viterbi_layers[0] if k in analysises[0] )
        if len(filtered_viterbi_layer) ==0 :
            pass
        viterbi_layer_0_prob = sum( [v for v in filtered_viterbi_layer.values() ]  )
        viterbi_layers[0] = dict( (k, math.log(v/viterbi_layer_0_prob) ) for k, v in filtered_viterbi_layer.items() )


        viterbi_backpointers[0] = dict( (k, None) for k, v in viterbi_layers[0].iteritems() )

        # Compute intermediate layers.
        for i in xrange(1, len(words)):
            viterbi_layers[i] = defaultdict(lambda: float("-inf"))
            viterbi_backpointers[i] = defaultdict(lambda: None)
            for prev_label, prev_logprob in viterbi_layers[i - 1].iteritems():
                features = self.compute_features(sentence=words,i= i, prev_label= prev_label, analysises = analysises[i])
                features = list(features)
                for label, prob in self.me.eval_all(features):
                    logprob = math.log(prob)
                    if prev_logprob + logprob > viterbi_layers[i][label]:
                        viterbi_layers[i][label] = prev_logprob + logprob
                        viterbi_backpointers[i][label] = prev_label

        # Most probable endpoint.
        max_logprob = float("-inf")
        max_label = None
        for label, logprob in viterbi_layers[len(words) - 1].iteritems():
            if logprob > max_logprob:
                max_logprob = logprob
                max_label = label

        # Most probable sequence.
        path = []
        label = max_label
        for i in reversed(xrange(len(words))):
            path.insert(0, label)
            try:
                label = viterbi_backpointers[i][label]
            except KeyError:
                pass

        return zip(words,path[::-1])

if __name__=="__main__":


    #memm_algo = MMEMAlgorithm(N_filter_func= N_rnc_pos)
    #memm_algo.train_model( corpus_dir= "/home/egor/disamb_test/gold/" , )
    #memm_algo.save_model(memm_filename =  r"/home/egor/disamb_test/memm_pos.dat", B_stat_filename = r"/home/egor/disamb_test/B_stat_pos.dat" )
    memm_algo = MMEMAlgorithm(N_filter_func= N_rnc_pos)
    memm_algo.load_memm_model( r"/home/egor/disamb_test/memm_pos.dat"  )
    remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/mystem_txt",output_dir = r"/home/egor/disamb_test/memm_pos", algo = memm_algo )
