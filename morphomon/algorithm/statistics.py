# -*- coding: utf-8 -*-
from morphomon.utils import get_tokens_from_corpora, get_word_ending
import settings



def calculate_A(corpus_file):
    tokens = get_tokens_from_corpora(corpus_file)

    A_matrix = {}

    prev_token = None
    for token in tokens:
        gram = token.gram
        if prev_token:
            if prev_token.gram not in  A_matrix:
                A_matrix[prev_token.gram] = {}
            if gram not in A_matrix[prev_token.gram]:
                A_matrix[prev_token.gram][gram] = 1
            else:
                A_matrix[prev_token.gram][gram] += 1
        prev_token = token
    return A_matrix

def calculate_B(corpus_file):
    tokens = get_tokens_from_corpora(corpus_file)

    B_matrix = {}
    #ключ - окончание слова, значение - словарь с грамматическими формамими : грам.форма => кол-во раз встреч в корпусе

    for token in tokens:
        word_form = token.word
        gram = token.gram
        ending = get_word_ending(word_form,enging_length=4)
        if ending not in B_matrix:
            B_matrix[ending] = {}

        if gram not in B_matrix[ending]:
            B_matrix[ending][gram] = 1
        else:
            B_matrix[ending][gram] += 1

    return B_matrix


if __name__=="__main__":
    B_matrix = calculate_B(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')
    A_matrix = calculate_A(corpus_file = settings.CORPUS_DATA_ROOT + 'processed_anketa.txt')

    gram_pr = set()
    for key in B_matrix:
        for gram_form in B_matrix[key]:
            gram_pr.add(gram_form)
            print "Окончание",key,"грам форма", gram_form,B_matrix[key][gram_form]

    print "Размерность множества окончаний", len(B_matrix)
    print "Размерность множества грам. признаков", len(gram_pr)

    for a_i in A_matrix:
        for a_j in A_matrix[a_i]:
            print a_i,a_j, A_matrix[a_i][a_j]