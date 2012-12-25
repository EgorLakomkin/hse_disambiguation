# -*- coding: utf-8 -*-
from collections import defaultdict
from math import log
from morphomon.utils import get_tokens_from_corpora, get_word_ending, EOS_TOKEN


def calculate_A(corpus_file):
    """
    Возвращаем матрицу переходов состояний A и начальный вектор распределения p
    """
    tokens = get_tokens_from_corpora(corpus_file)

    A = defaultdict(lambda: defaultdict(float))
    p = defaultdict(float)
    prev_token = EOS_TOKEN
    for token in tokens:

        if len(token) > 1:
            raise Exception("You cannot train on corpus with ambiguity")

        token = token[0]

        if token.gram == EOS_TOKEN.gram:
            prev_token = token
            continue

        gram = token.gram

        if prev_token.gram != EOS_TOKEN.gram:
            A[prev_token.gram][gram] += 1
        else:
            p[gram] +=1

        prev_token = token




    #преобразование вероятности в логарифм
    #lop p = log (k / n) = log k - log n
    for prev_token in A:
        log_n = log(sum([A[prev_token][next_token] for next_token in A[prev_token]]))
        for next_token in A[prev_token]:
            A[prev_token][next_token] = log(A[prev_token][next_token]) - log_n
    #преобразуем вероятности начального распределения
    log_n_p = log(sum([p[gram] for gram in p]))
    for gram in p:
        p[gram] = log(p[gram]) - log_n_p

    for prev_token in A:
        A[prev_token].default_factory = lambda : float('-10000')

    A.default_factory = lambda: defaultdict(lambda : float('-10000'))
    p.default_factory = lambda : float('-10000')
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
        if token.gram != EOS_TOKEN.gram:
            ending = get_word_ending(word_form,enging_length=3)
            B[gram][ending] += 1

    #преобразование вероятности в логарифм
    #lop p = log (k / n) = log k - log n
    for gram in B:
        log_n = log(sum([B[gram][ending] for ending in B[gram]]))
        for ending in B[gram]:
            B[gram][ending] = log(B[gram][ending]) - log_n

    for gram in B:
        B[gram].default_factory = lambda : float('-10000')

    B.default_factory = lambda: defaultdict(lambda : float('-10000'))
    return B



