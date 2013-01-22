# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys
from morphomon.utils import TokenRecord, N_rnc_pos, get_corpus_files, N_default, N_rnc_default_tags, N_rnc_positional_microsubset
import settings

__author__ = 'egor'


garbage_tags = [ 'init', 'abbr', 'ciph', 'bastard' ]

def M_strict_mathcher(algo_token, gold_token, N = N_default ):
    #no lemma comparison
    algo_gram = N(algo_token.gram)
    gold_gram =  N(gold_token.gram)
    if  algo_gram == gold_gram and algo_token.word == gold_token.word:
        return 1.0
    #print u"Algo output word-form : {0}, gram {1}".format( algo_token.word, algo_gram )
    #print u"Gold output word-form : {0}, gram {1}".format( gold_token.word, gold_gram)
    #print "================================================================="
    return 0.0

def P_dump_filter(token):
    return 1


def P_no_garbage(token):
    gram = token.gram
    for garbage_tag in garbage_tags:
        if garbage_tag in gram:
            return 0
    return 1
def calculate_precision(file_algo_name, file_gold_standart_name, file_ambi_name, M, N, P):
    """
    Params :
    file_algo - файл, который получился в результате алгоритма
    file_ambi - файл, который получился в результате работы морф.анализатора (с неснятой омонимией)
    file_gold_standart - файл, в котором содержится золотой стандарт
    """
    print >>sys.stderr, "Processing file {0}".format( file_gold_standart_name )
    algo_f = codecs.open( file_algo_name, 'r', 'utf-8' )
    gold_f = codecs.open( file_gold_standart_name, 'r', 'utf-8' )
    ambi_f = codecs.open( file_ambi_name, 'r', 'utf-8' )


    token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'
    correct_known = 0.0
    correct_unknown = 0.0
    max_value_known = 0.0
    max_value_unknown = 0.0

    #предполагается, что два файла имеют одинаковый формат и одинаковую длину
    for line_gold in gold_f:

        line_algo = algo_f.readline().strip()
        line_ambi = ambi_f.readline().strip()
        line_gold = line_gold.strip()

        if len(line_gold) == 0:
            continue


        algo_token_info = re.match(token_pattern, line_algo)
        gold_token_info = re.match(token_pattern, line_gold )

        try:
            gold_token_record = TokenRecord(word = gold_token_info.group('token_name').lower(), lemma = gold_token_info.group('token_lemma').lower(), gram = N (gold_token_info.group('token_gram').lower()) )
            algo_token_record = TokenRecord(word = algo_token_info.group('token_name').lower(), lemma = algo_token_info.group('token_lemma').lower(), gram = N (algo_token_info.group('token_gram').lower()) )
        except Exception as e:
            print e

        if gold_token_record.word!= algo_token_record.word:
            #пропускаем все предложение где не совпали словоформы
            skip_line = algo_f.readline().strip()
            while len(skip_line)>0:
                skip_line = algo_f.readline().strip()

            skip_line = ambi_f.readline().strip()
            while len(skip_line)>0:
                skip_line = ambi_f.readline().strip()

            skip_line = gold_f.readline().strip()
            while len(skip_line)>0:
                skip_line = gold_f.readline().strip()
            continue

        #if '-' in gold_token_record.word and '-' not in algo_token_record.word:
        # algo_f.readline()
        # continue


        if P(gold_token_record) > 0 and P(algo_token_record) > 0:
            m = re.search('bastard', line_ambi)
            if m != None:
                correct_unknown += M( algo_token_record, gold_token_record, N=N)
                max_value_unknown += 1.0
            else:
                correct_known += M( algo_token_record, gold_token_record, N=N)
                max_value_known += 1.0

    return correct_unknown, correct_known, max_value_unknown, max_value_known

def calculate_dir_precision(algo_dir, gold_dir, ambi_dir, M , N, P):
    gold_files = get_corpus_files(gold_dir)

    num = 0
    total = 0
    total_unknown = 0
    total_known = 0
    total_correct = 0
    total_correct_unknown = 0
    total_correct_known = 0
    for gold_file in gold_files:
        algo_file = os.path.join( algo_dir, os.path.basename( gold_file ) )
        ambi_file = os.path.join( ambi_dir, os.path.basename( gold_file ) )
        cur_correct_unknown, cur_correct_known, cur_total_unknown, cur_total_known = calculate_precision( file_algo_name= algo_file, file_gold_standart_name= gold_file, file_ambi_name = ambi_file, M=M , N=N, P=P )
        total_unknown += cur_total_unknown
        total_known += cur_total_known
        total = total_unknown + total_known
        total_correct_unknown += cur_correct_unknown
        total_correct_known += cur_correct_known
        total_correct = total_correct_unknown + total_correct_known

        print "percent correct (total)", int(float(total_correct)/total*100)
        print "percent correct (known words)", int(float(total_correct_known)/total_known*100)
        print "percent correct (unknown words)", int(float(total_correct_unknown)/total_unknown*100)

        num+=1
        print "{0} file processed. {1}%".format(gold_file, num/(len(gold_files)+0.0)*100 )

if __name__=="__main__":
    print calculate_dir_precision(gold_dir=  r"/home/egor/disamb_test/test_gold/",algo_dir=r"/home/egor/disamb_test/hmm_full_tags_output",
        ambi_dir= r"/home/egor/disamb_test/mystem_txt", M =M_strict_mathcher,  N = N_rnc_positional_microsubset, P = P_no_garbage )
