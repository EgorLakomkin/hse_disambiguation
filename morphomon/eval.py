# -*- coding: utf-8 -*-
import codecs
import re
from morphomon.utils import TokenRecord, N_rnc_pos
import settings

__author__ = 'egor'


garbage_tags = [ 'init', 'abbr', 'ciph' ]

def M_strict_mathcher(algo_token, gold_token ):
    if algo_token.gram == gold_token.gram and algo_token.lemma == gold_token.lemma and algo_token.word == gold_token.word:
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

        algo_token_record = TokenRecord(word = algo_token_info.group('token_name'), lemma = algo_token_info.group('token_lemma'), gram = N( algo_token_info.group('token_gram') ) )
        algo_words.add( algo_token_record.word )
        gold_token_record = TokenRecord(word = gold_token_info.group('token_name'), lemma = gold_token_info.group('token_lemma'), gram = N( gold_token_info.group('token_gram') ) )
        gold_words.add( gold_token_record.word )



        if P(gold_token_record) > 0:
            correct += M( algo_token_record, gold_token_record)
            max_value += 1.0

    return correct,max_value

def calculate_dir_precision(algo_dir, gold_dir, M , N, P):
    pass


if __name__=="__main__":
    print calculate_precision('/home/egor/rnc_mystem.txt', '/home/egor/rnc.txt',M =M_strict_mathcher,  N = N_rnc_pos, P = P_no_garbage )