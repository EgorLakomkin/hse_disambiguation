# -*- coding: utf-8 -*-
from collections import defaultdict
from morphomon.utils import get_tokens_from_corpora, get_word_ending
import settings



def calculate_A(corpus_file):
    """
    Возвращаем матрицу переходов состояний A и начальный вектор распределения p
    """
    tokens = get_tokens_from_corpora(corpus_file)

    A = defaultdict(lambda: defaultdict(float))
    p = defaultdict(float)
    prev_token = None
    for token in tokens:
        gram = token.gram
        if prev_token:
            A[prev_token.gram][gram] += 1
        else:
            p[gram] +=1

        prev_token = token
    return A,p

def calculate_B(corpus_file):
    """
    Считаем матрицу наблюдений B
    """
    tokens = get_tokens_from_corpora(corpus_file)

    B = defaultdict(lambda: defaultdict(float))
    #ключ - окончание слова, значение - словарь с грамматическими формамими : грам.форма => кол-во раз встреч в корпусе

    for token in tokens:
        word_form = token.word
        gram = token.gram
        ending = get_word_ending(word_form,enging_length=4)
        B[gram][ending] += 1

    return B


if __name__=="__main__":
    B_matrix = calculate_B(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')
    A_matrix,p = calculate_A(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')

    gram_pr = set()
    for key in B_matrix:
        for ending in B_matrix[key]:
            gram_pr.add(key)
            print "Окончание",ending,"грам форма", key,B_matrix[key][ending]

    print "Размерность множества окончаний", len(B_matrix)
    print "Размерность множества грам. признаков", len(gram_pr)

    for a_i in A_matrix:
        for a_j in A_matrix[a_i]:
            print a_i,a_j, A_matrix[a_i][a_j]