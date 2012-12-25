# -*- coding: utf-8 -*-
import codecs
import re
from morphomon.utils import TokenRecord
import settings

__author__ = 'egor'



def M_strict_mathcher(algo_token, gold_token ):
    if algo_token.gram == gold_token.gram and algo_token.lemma == gold_token.lemma and algo_token.word == gold_token.word:
        return 1.0
    return 0.0

def P_dump_filter(token):
    return 1


def calculate_precision(file_algo_name, file_gold_standart_name, M, P):
    """
    Params :
    fila_algo - файл, который получился в результате алгоритма
    file_gold_standart - файл, в котором содержится золотой стандарт
    """
    algo_f =  codecs.open( file_algo_name, 'r', 'utf-8' )
    gold_f = codecs.open( file_gold_standart_name, 'r', 'utf-8' )

    algo_f_tokens = algo_f.read().split('\n')
    gold_f_tokens = gold_f.read().split('\n')

    #фильтруем признаки конца предложения
    algo_f_tokens = [token for token in algo_f_tokens if len(token)>0]
    gold_f_tokens = [token for token in gold_f_tokens if len(token)>0]


    token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'
    correct = 0.0
    max_value = 0.0
    #предполагается, что два файла имеют одинаковый формат и одинаковую длину
    for token_index in range( len( algo_f_tokens ) ):


        algo_token_info = re.match(token_pattern, algo_f_tokens[token_index] )
        gold_token_info = re.match(token_pattern, gold_f_tokens[token_index] )

        algo_token_record = TokenRecord(word =algo_token_info.group('token_name'), lemma = algo_token_info.group('token_lemma'), gram = algo_token_info.group('token_gram') )

        gold_token_record = TokenRecord(word =gold_token_info.group('token_name'), lemma = gold_token_info.group('token_lemma'), gram = gold_token_info.group('token_gram') )

        if P(gold_token_record) > 0:
            correct += M(algo_token_record,gold_token_record)
            max_value += 1.0

    return float(correct) / max_value

if __name__=="__main__":
    print calculate_precision(settings.CORPUS_DATA_ROOT + 'processed_opencorpora.txt', settings.CORPUS_DATA_ROOT + 'processed_opencorpora_test.txt', M = M_strict_mathcher, P = P_dump_filter )