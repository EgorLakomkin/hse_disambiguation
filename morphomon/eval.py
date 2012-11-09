# -*- coding: utf-8 -*-
import codecs
import re

__author__ = 'egor'




def calculate_precision(file_algo_name, file_gold_standart_name):
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
    correct = 0
    #предполагается, что два файла имеют одинаковый формат и одинаковую длину
    for token_index in range( len( algo_f_tokens ) ):

        algo_token_info = re.match(token_pattern, algo_f_tokens[token_index] )
        gold_token_info = re.match(token_pattern, gold_f_tokens[token_index] )

        if algo_token_info.group('token_name') == gold_token_info.group('token_name'):
            if algo_token_info.group('token_lemma') == gold_token_info.group('token_lemma'):
                #тупое и наивное сравнение грамм признаков
                #TODO
                if algo_token_info.group('token_gram') == gold_token_info.group('token_gram'):
                    correct +=1


    return float(correct) / len(algo_f_tokens)