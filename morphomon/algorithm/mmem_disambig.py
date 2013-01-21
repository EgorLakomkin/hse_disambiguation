# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
from morphomon.utils import N_rnc_pos, dump_object, get_tokens_from_file, EOS_TOKEN
from maxent import MaxentModel

__author__ = 'egor'


class MMEMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, N_filter_func = N_default):
        self.filter_func = N_filter_func
        self.me = MaxentModel()

    def init(self):
        pass

    def compute_features( self, sentence ,  i):
        if i > 0:
            yield "previous-tag={0}".format(   sentence[i - 1].gram  )
        if i > 1:
            yield "previous-previous-tag={0}".format(   sentence[i - 2].gram  )

    def train_model(self, corpus_dir,N_filter_func = N_default ):
        self.me.begin_add_event()
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if token[0] == EOS_TOKEN:
                for i,token in enumerate( sentence ):
                    word_features = list( self.compute_features( sentence, i ) )
                    self.me.add_event(word_features, token.gram )
                sentence = []
                continue

            sentence.append( token )

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


    memm_algo = MMEMAlgorithm()
    memm_algo.train_model( corpus_dir= "/home/egor/disamb_test/test_gold/" , N_filter_func= N_rnc_pos)
    memm.save_model( r"/home/egor/disamb_test/memm_positional.dat", )
    #hmm_algo = load_object( r"/home/egor/disamb_test/hmm_positional.dat"  )
    #remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/mystem_txt",output_dir = r"/home/egor/disamb_test/hmm_full_tags_output", algo = hmm_algo )
