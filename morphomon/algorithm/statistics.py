# -*- coding: utf-8 -*-
from collections import defaultdict
from math import log
from morphomon.utils import get_tokens_from_file, get_word_ending, EOS_TOKEN, N_default, get_corpus_files
from random import choice

def default_float():
    return defaultdict(float)

def default_min_float():
    return defaultdict( return_min_float )

def return_min_float():
    return float('-10000')


def train_A_corpus(corpus_dir, N_filter_func = N_default):
    corpus_files = get_corpus_files( corpus_dir )
    A = defaultdict(default_float)
    p = defaultdict(float)
    for file in corpus_files:
        print "Train A matrix on {0} file".format( file )
        calculate_A(A,p,file, N_filter_func )
    A,p = normalize_A_matrix(A,p)
    return A,p

def train_B_corpus(corpus_dir, N_filter_func = N_default):
    corpus_files = get_corpus_files( corpus_dir )
    B = defaultdict(default_float)
    for file in corpus_files:
        print "Train B matrix on {0} file".format( file )
        calculate_B(B,file, N_filter_func )
    B = normalize_B(B)
    return B

def calculate_A(A,p, corpus_file,N_filter_func=N_default):
    """
    Возвращаем матрицу переходов состояний A и начальный вектор распределения p
    """
    tokens = get_tokens_from_file(corpus_file,N_filter_func )

    if A is None:
        A = defaultdict(default_float)
        p = defaultdict(float)

    prev_token = EOS_TOKEN
    for token in tokens:

        if len(token) > 1:
            pass
            #print "Ambiguity in corpus"
            #print "Pick random token"
            #raise Exception("You cannot train on corpus with ambiguity")

        token = choice(token)

        if token.gram == EOS_TOKEN.gram:
            prev_token = token
            continue

        gram = token.gram

        if prev_token.gram != EOS_TOKEN.gram:
            A[prev_token.gram][gram] += 1
        else:
            p[gram] +=1

        prev_token = token

    return A,p


def normalize_A_matrix(A,p):
    for prev_token in A:
        log_n = log(sum([A[prev_token][next_token] for next_token in A[prev_token]]))
        for next_token in A[prev_token]:
            A[prev_token][next_token] = log(A[prev_token][next_token]) - log_n
        #преобразуем вероятности начального распределения
    log_n_p = log(sum([p[gram] for gram in p]))
    for gram in p:
        p[gram] = log(p[gram]) - log_n_p

    for prev_token in A:
        A[prev_token].default_factory = return_min_float

    A.default_factory = default_min_float
    p.default_factory = return_min_float
    return A,p


def calculate_B(B, corpus_file,N_filter_func=N_default):
    """
    Считаем матрицу наблюдений B
    """
    tokens = get_tokens_from_file(corpus_file,N_filter_func)
    if B is None:
        B = defaultdict(default_float)
    #ключ - окончание слова, значение - словарь с грамматическими формамими : грам.форма => кол-во раз встреч в корпусе

    for token in tokens:

        if len(token) > 1:
            pass
            #print "Ambiguity in corpus"
            #print "Pick random token"
            #raise Exception("You cannot train on corpus with ambiguity")

        token = choice(token)

        word_form = token.word
        gram = token.gram
        if token.gram != EOS_TOKEN.gram:
            ending = get_word_ending(word_form,enging_length=3)
            B[gram][ending] += 1

    return B


def normalize_B(B):
    for gram in B:
        log_n = log(sum([B[gram][ending] for ending in B[gram]]))
        for ending in B[gram]:
            B[gram][ending] = log(B[gram][ending]) - log_n

    for gram in B:
        B[gram].default_factory = return_min_float

    B.default_factory = default_min_float
    return B
