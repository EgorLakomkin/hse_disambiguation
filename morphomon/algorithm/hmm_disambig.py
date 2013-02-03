# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
from morphomon.algorithm.statistics import calculate_B, calculate_A, train_A_corpus, train_B_corpus
from morphomon.utils import get_word_ending, TokenRecord, N_default, load_object, get_tokens_from_file, EOS_TOKEN, N_rnc_pos, remove_ambiguity_dir,  dump_object, N_rnc_positional_microsubset, N_rnc_positional

__author__ = 'egor'


class HMMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, A = None , B = None, p = None , N_filter_func = N_default):
        self.filter_func = N_filter_func
        if A and B and p:
            self.B = B
            self.A = A
            self.p = p
            self.init()

    def init(self):
        gram_pr = set()
        for key in self.B:
            for ending in self.B[key]:
                gram_pr.add(key)

        self.X = set([ending for gram in self.B for ending in self.B[gram]])

        self.Y = set([gram for gram in gram_pr])

    def train_model(self, corpus_dir,N_filter_func = N_default ):
        self.B = train_B_corpus(corpus_dir = corpus_dir,N_filter_func = N_filter_func)
        self.A,self.p = train_A_corpus(corpus_dir = corpus_dir,N_filter_func  = N_filter_func)
        self.filter_func = N_filter_func
        self.init()


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
        #формат входящих данных
        #список tuple из словоформы и списка ее вариантов разбора
        #формат исходящих данных
        #список tuple

        phi = defaultdict(lambda: defaultdict(float))

        backtrace = defaultdict(lambda: defaultdict(str))
        path = []

        all_states = ['start'] + list(self.Y)
        for state in all_states:
            phi[-1][state] = 0.0
            self.A['start'][state] = self.p[state]

        prev_states = [ 'start' ]
        #проходим все наблюдения
        for i,obs in enumerate(variants):

            current_word_form = obs[0]
            current_word_form_ending = get_word_ending(current_word_form)
            list_of_possible_grams = [token_record.gram for token_record in obs[1]]
            #перебираем все возможные следующие состояния
            for state in list_of_possible_grams:
                max_prob = float('-inf')
                source_state = None
                #находим максимальный путь до состояния Y
                for prev_state in prev_states:
                    prob = phi[i-1][prev_state] + self.A[prev_state][ state ] + self.B[ state ][current_word_form_ending]
                    if prob > max_prob:
                        max_prob = prob
                        source_state = prev_state
                        #записываем max P(x1..xi,y1..i)
                phi[i][state] = max_prob
                backtrace[i][state] = source_state

            prev_states = list_of_possible_grams

        #начинаем back_trace

        last_state = None
        max_prob = float('-inf')

        #ищем максимальное состояние
        for key in phi[len(variants) - 1]:
            prob = phi[len(variants) - 1][key]
            if prob > max_prob:
                max_prob = prob
                last_state = key

        it_state = last_state
        path.append(last_state)
        #проходим с конца и записываем в путь предыдущие состояния
        for index in reversed(range(1,len(variants))):
            path.append( backtrace[index][it_state] )
            it_state = backtrace[index][it_state]

        word_forms = [x[0] for x in variants]

        return zip(word_forms,path[::-1])



if __name__=="__main__":


    hmm_algo = HMMAlgorithm()
    hmm_algo.train_model( corpus_dir= "/home/egor/disamb_test/gold/" , N_filter_func= N_rnc_positional_microsubset)
    dump_object( r"/home/egor/disamb_test/hmm_base.dat",  hmm_algo )
    #hmm_algo = load_object( r"/home/egor/disamb_test/hmm_positional.dat"  )
    remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/test_ambig",output_dir = r"/home/egor/disamb_test/hmm_full_tags_output", algo = hmm_algo )
