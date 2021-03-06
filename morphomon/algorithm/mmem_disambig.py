# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
import math
import os
import maxent
import sys
from morphomon.utils import *
from maxent import MaxentModel

__author__ = 'egor'


def default_compute_features( sentence , i, prev_label, analysises, labels):
        if prev_label is not None:
            yield "previous-tag={0}".format(   prev_label )

        word_form = sentence[i]
        word_ending = get_word_ending( word_form, ending_length= 3 )
        yield "word-ending={0}".format( word_ending.encode('utf-8') )


class MMEMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self,compute_features, N_filter_func = N_default):
        self.filter_func = N_filter_func
        self.me = MaxentModel()
        self.num_train_iters = 2000
	self.compute_features = compute_features

    def load_memm_model(self, filename):
        self.me.load( filename  )

    def init(self):
        pass

    


    def train_model_file_list(self, corpus_filelist, ambiguity_dir ):
        self.me.begin_add_event()

        for corpus_file in corpus_filelist:
            print "Training on file {0}".format( corpus_file )
            sentence = []
            morph_analys_file = os.path.join( ambiguity_dir, os.path.basename( corpus_file ) )

            morph_analys_tokens = get_tokens_from_file(morph_analys_file, N_filter_func = self.filter_func ) if os.path.exists( morph_analys_file ) else None
            if morph_analys_tokens:
                print "Using mystem features on file {0}".format( morph_analys_file )

            gold_tokens = get_tokens_from_file(corpus_file, N_filter_func = self.filter_func )
            for corpus_token in gold_tokens:

                morph_analys_token = morph_analys_tokens.next() if morph_analys_tokens else None


                gold_token_word = corpus_token[0].word
                morph_analys_token_word = morph_analys_token[0].word if morph_analys_token else None
                if morph_analys_token_word:
                    if gold_token_word != morph_analys_token_word:
                        '''
                        if ('-' in gold_token_word and '-' not in morph_analys_token_word) or ('\'' in gold_token_word and '\'' not in morph_analys_token_word):
                            morph_analys_token = morph_analys_tokens.next()
                        if ('.' in gold_token_word):
                            cnt_dots = '.'.count( gold_token_word )
                            for i in xrange( 0, cnt_dots ):
                                morph_analys_token = morph_analys_tokens.next()
                        '''
                        print >>sys.stderr, u"Start skipping sentence. Gold token wordform {0} morph token wordform {1}".format( gold_token_word, morph_analys_token_word )

                        sentence = []
                        try:
                            next_gold = gold_tokens.next()
                            while( next_gold !=  [EOS_TOKEN] ):
                                next_gold = gold_tokens.next()

                            next_gold = gold_tokens.next()
                            next_morph = morph_analys_tokens.next()
                            while( next_morph[0].word != next_gold[0].word ):
                                next_morph = morph_analys_tokens.next()

                        except StopIteration:
                            break



                if corpus_token[0] == EOS_TOKEN and len(sentence) > 0:
                    words = [token[0].word for token in sentence]
                    labels = [token[0].gram for token in sentence]
                    for i,token_info in enumerate( sentence ):
                        gold_token = token_info[0]
                        morph_analysises = [token.gram for token in token_info[1]] if token_info[1] and morph_analys_token else None

                        if token_info[1] is not None:
                            if gold_token.word != token_info[1][0].word:
                                print >>sys.stderr, u"Cannot match gold token and morph analysis token\n gold token : {0}     morph analysis token : {1}".format( gold_token.word, token_info[1][0].word )
                                morph_analysises = None

                        word_features = list( self.compute_features( sentence = words, i = i , prev_label= labels[ i - 1 ] if i >0 else None, analysises = morph_analysises, labels = labels) )
                        gold_token_gram = gold_token.gram.encode('utf-8')
                        self.me.add_event(word_features, gold_token_gram )
                    sentence = []
                else:
                    sentence.append( (corpus_token[0], morph_analys_token)  )


        self.me.end_add_event()
        maxent.set_verbose(1)
        self.me.train( self.num_train_iters, 'lbfgs', 0.0 )
        maxent.set_verbose(0)

    def train_model(self, corpus_dir, ambiguity_dir ):
        self.me.begin_add_event()
        #self.B = train_B_corpus(corpus_dir = corpus_dir,N_filter_func = N_filter_func)
        sentence = []

        corpus_files = get_corpus_files(corpus_dir)
        for corpus_file in corpus_files:

            morph_analys_file = os.path.join( ambiguity_dir, os.path.basename( corpus_file ) )
            morph_analys_tokens = get_tokens_from_file(morph_analys_file, N_filter_func = self.filter_func )

            for corpus_token in get_tokens_from_file(corpus_file, N_filter_func = self.filter_func ):

                morph_analys_token = morph_analys_tokens.next()
                if corpus_token[0] == EOS_TOKEN:
                    words = [token[0].word for token in sentence]
                    labels = [token[0].gram for token in sentence]
                    for i,token_info in enumerate( sentence ):
                        gold_token = token_info[0]
                        morph_analysises = [token.gram for token in token_info[1]]
                        if gold_token.word != token_info[1][0].word:
                            print >>sys.stderr, u"Cannot match gold token and morph analysis token\n gold token : {0}     morph analysis token : {1}".format( gold_token.word, token_info[1][0].word )
                            morph_analysises = None
                        word_features = list( self.compute_features( sentence = words, i = i , prev_label= labels[ i - 1 ] if i >0 else None, analysises = morph_analysises, labels = labels) )
                        gold_token_gram = gold_token.gram.encode('utf-8')
                        self.me.add_event(word_features, gold_token_gram )
                    sentence = []
                else:
                    sentence.append( (corpus_token[0], morph_analys_token)  )

        self.me.end_add_event()
        maxent.set_verbose(1)
        self.me.train( 50, 'lbfgs', 0.0 )
        maxent.set_verbose(0)

    def load_model(self, memm_filename):
        self.me.load( memm_filename )

    def save_model(self, memm_filename):
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
        viterbi_layers[0] = self.me.eval_all(list(self.compute_features(sentence=words, i = 0 , prev_label= None, analysises = analysises[0], labels = None ) ) )

        filtered_viterbi_layer = dict( (k, v) for k, v in viterbi_layers[0] if k in analysises[0] )
        viterbi_layer_0_prob = sum( [v for v in filtered_viterbi_layer.values() ]  )
        viterbi_layers[0] = dict( (k, math.log(v/viterbi_layer_0_prob) ) for k, v in filtered_viterbi_layer.items() )


        viterbi_backpointers[0] = dict( (k, None) for k, v in viterbi_layers[0].iteritems() )

        # Compute intermediate layers.
        for i in xrange(1, len(words)):
            viterbi_layers[i] = defaultdict(lambda: float("-inf"))
            viterbi_backpointers[i] = defaultdict(lambda: None)
            for prev_label, prev_logprob in viterbi_layers[i - 1].iteritems():
                features = self.compute_features(sentence=words,i= i, prev_label= prev_label, analysises = analysises[i], labels = None)
                features = list(features)
                distribution =  self.me.eval_all(features)
                distribution = dict( (label, prob) for label, prob in  distribution if label in analysises[i])

                distribution_sum = sum( [v for v in distribution.values() ]  )
                distribution = dict( (k, v/ distribution_sum) for k, v in distribution.items() )
                for label, prob in distribution.items():
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

        return zip(words,path)

