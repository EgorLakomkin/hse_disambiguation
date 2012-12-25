# -*- coding: utf-8 -*-
from morphomon.algorithm.statistics import calculate_B, calculate_A
from morphomon.utils import get_word_ending
import settings
from exercises.egor_viterbi import get_viterbi_path, get_viterbi_probability


if __name__=="__main__":
    B = calculate_B(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')
    A,p = calculate_A(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')


    gram_pr = set()
    for key in B:
        for ending in B[key]:
            gram_pr.add(key)


    X = set([ending for gram in B for ending in B[gram]])

    Y = set([gram for gram in gram_pr])


    print "Размерность множества окончаний", len(X)
    print "Размерность множества грам. признаков", len(Y)

    while True:
        sentence = raw_input("Введите предложение :")
        sentence = sentence.decode('utf-8')
        print "Вы ввели : ", sentence
        sentence_obserable = [get_word_ending(word,enging_length=3) for word in sentence.split(' ')]
        print "Наблюдаемые состояния : ", ' '.join(sentence_obserable)
        print ' '.join(get_viterbi_path(sentence_obserable,X,Y,A,B,p))
        print get_viterbi_probability(sentence_obserable,X,Y,A,B,p)