# -*- coding: utf-8 -*-
from morphomon.algorithm.statistics import calculate_B, calculate_A
from morphomon.utils import get_word_ending,N_rnc_pos,dump_object, load_object
import settings
from exercises.egor_viterbi import get_viterbi_path, get_viterbi_probability


if __name__=="__main__":
    B = calculate_B(corpus_file = '/home/egor/rnc.txt',N_filter_func=N_rnc_pos)
    A,p = calculate_A(corpus_file = '/home/egor/rnc.txt',N_filter_func=N_rnc_pos)
    dump_object(filename="/home/egor/B_POS_rnc.dat",object = B)
    dump_object(filename="/home/egor/A_POS_rnc.dat",object = A)
    dump_object(filename="/home/egor/p_POS_rnc.dat",object = p)
    #B = load_object(filename="/home/egor/B_POS_rnc.dat")
    #A = load_object(filename="/home/egor/A_POS_rnc.dat")
    #p = load_object(filename="/home/egor/p_POS_rnc.dat")

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
