# -*- coding: utf-8 -*-
from morphomon.algorithm.naive import get_tokens
import settings

def get_ending(word):
    ending = word[-3:]
    return ending

def calculate_A(corpus_file):
    tokens = get_tokens(corpus_file)

    A_matrix = {}
    #ключ - окончание слова, значение - словарь с грамматическими формамими : грам.форма => кол-во раз встреч в корпусе

    for token in tokens:
        word_form = token.word
        gram = token.gram
        ending = get_ending(word_form)
        if ending not in A_matrix:
            A_matrix[ending] = {}

        if gram not in A_matrix[ending]:
            A_matrix[ending][gram] = 1
        else:
            A_matrix[ending][gram] += 1

    return A_matrix



A_matrix = calculate_A(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')
for key in A_matrix:
    for gram_form in A_matrix[key]:
        print "Окончание",key,"грам форма", gram_form,A_matrix[key][gram_form]
