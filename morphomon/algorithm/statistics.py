# -*- coding: utf-8 -*-
from collections import defaultdict
from math import log
from morphomon.utils import get_tokens_from_corpora, get_word_ending
import settings
from tests.egor_viterbi import get_viterbi_probability, get_viterbi_path


def calculate_A(corpus_file):
    """
    Возвращаем матрицу переходов состояний A и начальный вектор распределения p
    """
    tokens = get_tokens_from_corpora(corpus_file)

    A = defaultdict(lambda: defaultdict(float))
    p = defaultdict(float)
    prev_token = None
    for token in tokens:

        if len(token) > 1:
            raise Exception("You cannot train on corpus with ambiguity")

        token = token[0]

        gram = token.gram
        if token.gram !='EOS' and prev_token:
            A[prev_token.gram][gram] += 1
            prev_token = token
        else:
            if gram !='EOS' and not prev_token:
                p[gram] +=1
                prev_token = token
            else:
                prev_token = None

    #преобразование вероятности в логарифм
    #lop p = log (k / n) = log k - log n
    for prev_token in A:
        log_n = log(sum([A[prev_token][next_token] for next_token in A[prev_token]]))
        for next_token in A[prev_token]:
            A[prev_token][next_token] = log(A[prev_token][next_token]) - log_n


    #преобразуем вероятности начального распределения
    for gram in A:
        if gram not in p:
            p[gram] = 0.000001

    log_n_p = log(sum([p[gram] for gram in A]))
    for gram in A:
        p[gram] = log(p[gram]) - log_n_p

    return A,p

def calculate_B(corpus_file):
    """
    Считаем матрицу наблюдений B
    """
    tokens = get_tokens_from_corpora(corpus_file)

    B = defaultdict(lambda: defaultdict(float))
    #ключ - окончание слова, значение - словарь с грамматическими формамими : грам.форма => кол-во раз встреч в корпусе

    for token in tokens:

        if len(token) > 1:
            raise Exception("You cannot train on corpus with ambiguity")

        token = token[0]

        word_form = token.word
        gram = token.gram
        if gram != 'EOS':
            ending = get_word_ending(word_form,enging_length=3)
            B[gram][ending] += 1

    #преобразование вероятности в логарифм
    #lop p = log (k / n) = log k - log n
    for gram in B:
        log_n = log(sum([B[gram][ending] for ending in B[gram]]))
        for ending in B[gram]:
            B[gram][ending] = log(B[gram][ending]) - log_n
    return B


if __name__=="__main__":
    B = calculate_B(corpus_file = "/home/umka/rnc.txt")
    A,p = calculate_A(corpus_file = "/home/umka/rnc.txt")
    for initial in p:
        print initial, p[initial]
    gram_pr = set()
    for key in B:
        for ending in B[key]:
            gram_pr.add(key)

    for gram in A:
        for ending in B:
            if gram not in B[ending]:
                B[ending][gram] = float('-inf')



    X = set([ending for gram in B for ending in B[gram]])

    Y = set([gram for gram in gram_pr])

    #препроцессинг матрицы A
    for prev_state in Y:
        for next_state in Y:
            if next_state not in A[prev_state]:
                A[prev_state][next_state] = float('-inf')

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
