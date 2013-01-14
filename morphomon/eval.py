# -*- coding: utf-8 -*-
import codecs
import re
from morphomon.utils import TokenRecord, N_rnc_pos
import settings

__author__ = 'egor'


garbage_tags = [ 'init', 'abbr', 'ciph', 'bastard' ]

def M_strict_mathcher(algo_token, gold_token ):
    #no lemma comparison
    if algo_token.gram == gold_token.gram  and algo_token.word == gold_token.word:
        return 1.0
    return 0.0

def P_dump_filter(token):
    return 1


def P_no_garbage(token):
    gram = token.gram
    for garbage_tag in garbage_tags:
        if garbage_tag in gram:
            return 0
    return 1

def calculate_precision(file_algo_name, file_gold_standart_name,M, N, P):
    """
    Params :
    fila_algo - файл, который получился в результате алгоритма
    file_gold_standart - файл, в котором содержится золотой стандарт
    """
    algo_f =  codecs.open( file_algo_name, 'r', 'utf-8' )
    gold_f = codecs.open( file_gold_standart_name, 'r', 'utf-8' )


    algo_words = set()
    gold_words =set()

    token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'
    correct = 0.0
    max_value = 0.0
    #предполагается, что два файла имеют одинаковый формат и одинаковую длину
    for line_gold in gold_f:

        line_algo = algo_f.readline().strip()
        line_gold = line_gold.strip()

        if len(line_gold) == 0:
            continue

        algo_token_info = re.match(token_pattern, line_algo)
        gold_token_info = re.match(token_pattern, line_gold )


        gold_token_record = TokenRecord(word = gold_token_info.group('token_name').lower(), lemma = gold_token_info.group('token_lemma').lower(), gram = N( gold_token_info.group('token_gram').lower() ) )
        algo_token_record = TokenRecord(word = algo_token_info.group('token_name').lower(), lemma = algo_token_info.group('token_lemma').lower(), gram = N( algo_token_info.group('token_gram').lower() ) )

        if '-' in gold_token_record.word and '-' not in algo_token_record.word:
            algo_f.readline()
            continue


        if P(gold_token_record) > 0 and P(algo_token_record) > 0:
            correct += M( algo_token_record, gold_token_record)
            max_value += 1.0

    return float(correct) / max_value

if __name__=="__main__":
    print calculate_precision('/home/egor/rnc_test/_itartass2_2139_2_no_ambig.txt', '/home/egor/rnc_test/_itartass2_2139.txt',M =M_strict_mathcher,  N = N_rnc_pos, P = P_no_garbage )