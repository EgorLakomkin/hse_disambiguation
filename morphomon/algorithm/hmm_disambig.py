# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
from morphomon.algorithm.statistics import calculate_B, calculate_A, train_A_corpus, train_B_corpus
from morphomon.utils import get_word_ending, TokenRecord, N_default, load_object, get_tokens_from_file, EOS_TOKEN, N_rnc_pos
import settings

__author__ = 'egor'


class HMMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, A = None , B = None, p = None , corpus_dir = None , N_filter_func = N_default):
        self.filter_func = N_filter_func
        if corpus_dir:
            self.B = train_B_corpus(corpus_dir = corpus_dir,N_filter_func = N_filter_func)
            self.A,self.p = train_A_corpus(corpus_dir = corpus_dir,N_filter_func  = N_filter_func)

        else:
            self.B = B
            self.A = A
            self.p = p

        gram_pr = set()
        for key in self.B:
            for ending in self.B[key]:
                gram_pr.add(key)

        self.X = set([ending for gram in self.B for ending in self.B[gram]])

        self.Y = set([gram for gram in gram_pr])


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

        prev_states = [(None, 'start')]
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

    B = load_object(filename="/home/egor/B_POS_rnc.dat")
    A = load_object(filename="/home/egor/A_POS_rnc.dat")
    p = load_object(filename="/home/egor/p_POS_rnc.dat")
    hmm_algo = HMMAlgorithm( B = B, A = A, p = p,N_filter_func = N_rnc_pos )
    hmm_algo.remove_ambiguity_file('/home/egor/rnc_test/_itartass2_2139_2_ambig.txt','/home/egor/rnc_test/_itartass2_2139_2_no_ambig.txt')
