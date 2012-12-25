# -*- coding: utf-8 -*-
from collections import defaultdict
from morphomon.algorithm.statistics import calculate_B, calculate_A
from morphomon.utils import get_word_ending, TokenRecord
import settings

__author__ = 'egor'


class HMMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, corpus_file):

        self.B = calculate_B(corpus_file = corpus_file)
        self.A,self.p = calculate_A(corpus_file = corpus_file)

        gram_pr = set()
        for key in self.B:
            for ending in self.B[key]:
                gram_pr.add(key)


        self.X = set([ending for gram in self.B for ending in self.B[gram]])

        self.Y = set([gram for gram in gram_pr])

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

        prev_states = ['start']
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
                    prob = phi[i-1][prev_state] + self.A[prev_state][state] + self.B[state][current_word_form_ending]
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
        return zip(word_forms,path[::-1]) # Посчитать max_y P(y|x)

if __name__=="__main__":

    hmm_algo = HMMAlgorithm( corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt' )


    variants = [('мама',[TokenRecord(word=u'в', lemma=u'в', gram = u'PREP'),TokenRecord(word=u'мама', lemma=u'мама', gram = u's,ед,жен,им,од')  ]),
                ('мыла',[TokenRecord(word=u'в', lemma=u'в', gram = u'v,несов,изъяв,прош,ед,муж'),TokenRecord(word=u'мыла', lemma=u'мыть', gram = u'v,несов,изъяв,прош,ед,жен')  ]),
                ('раму',[TokenRecord(word=u'в', lemma=u'в', gram = u'PREP'),TokenRecord(word=u'раму', lemma=u'рама', gram = u's,ед,жен,вин,од')  ])]

    no_ambig =  hmm_algo.remove_ambiguity(variants)
    for token in no_ambig:
        print "Словоформа",token[0],"грам признак",token[1]