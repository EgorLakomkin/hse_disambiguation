# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
import os
import re
import sys
from morphomon.utils import TokenRecord, N_rnc_pos, get_corpus_files, N_default, N_rnc_positional_microsubset, get_diff_between_tokens, parse_token, EOS_TOKEN
import settings

__author__ = 'egor'


garbage_tags = [ 'init', 'abbr', 'ciph', 'nonlex' ]

def M_strict_mathcher(algo_token, gold_token):
    #no lemma comparison
    algo_gram = algo_token.gram
    gold_gram =  gold_token.gram
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


def prettify_gram(gram):
    return ','.join( [tag for tag in gram.split(',') if len(tag) > 0 ] )

def calculate_precision(file_algo_name, file_gold_standart_name, file_ambi_name, M, N, P, errors_context_filename, errors_statistics_filename):
    """
    Params :
    file_algo - файл, который получился в результате алгоритма
    file_ambi - файл, который получился в результате работы морф.анализатора (с неснятой омонимией)
    file_gold_standart - файл, в котором содержится золотой стандарт
    """
    algo_f = codecs.open( file_algo_name, 'r', 'utf-8' )
    gold_f = codecs.open( file_gold_standart_name, 'r', 'utf-8' )
    ambi_f = codecs.open( file_ambi_name, 'r', 'utf-8' )

    error_context_f = open( errors_context_filename,'a+' )
    error_stat_f = open( errors_statistics_filename,'a+' )

    correct_known = 0.0
    correct_unknown = 0.0
    max_value_known = 0.0
    max_value_unknown = 0.0
    upper_bound = 0.0

    errors = defaultdict( float )

    context = []
    #предполагается, что два файла имеют одинаковый формат и одинаковую длину
    for line_gold in gold_f:

        line_algo = algo_f.readline().strip()
        line_ambi = ambi_f.readline().strip()
        line_gold = line_gold.strip()



        gold_token_record = parse_token( line_gold, N_filter_func=N)[0]
        algo_token_record = parse_token( line_algo, N_filter_func=N)[0]
        ambig_token_records = parse_token( line_ambi, N_filter_func=N)

        ERROR = 1
        OK = 0
        EOS = -1

        if gold_token_record.word!= algo_token_record.word:
            print >>sys.stderr, u"Gold and algo files does not match. Gold line : {0} \nAlgo line  : {1}".format( line_gold,line_algo  )
            #пропускаем все предложение где есть слова с съехавшими не совпали словоформы

            try:
                skip_line = gold_f.readline().strip()
                while len(skip_line)>0:
                    skip_line = gold_f.readline().strip()
                skip_line = gold_f.readline().strip()
                gold_token = parse_token( skip_line, N_filter_func=N)[0]

                skip_line = ambi_f.readline().strip()
                ambi_token = parse_token( skip_line, N_filter_func=N)
                while ambi_token[0].word != gold_token.word:
                    skip_line = ambi_f.next().strip()
                    ambi_token = parse_token( skip_line, N_filter_func=N)

                skip_line = algo_f.readline().strip()
                algo_f_token = parse_token( skip_line, N_filter_func=N)[0]

                while algo_f_token.word != gold_token.word:
                    skip_line = algo_f.readline().strip()
                    algo_f_token = parse_token( skip_line, N_filter_func=N)[0]

                gold_token_record = gold_token
                algo_token_record = algo_f_token
                ambig_token_records = ambi_token
            except StopIteration:
                continue




        if gold_token_record == EOS_TOKEN:
            context.append( (None, None, EOS) )
            continue



        if P(gold_token_record) > 0:
            result_m = M( algo_token_record, gold_token_record)

            if result_m < 1.0:
                context.append( (gold_token_record, algo_token_record, ERROR) )
            else:
                context.append( (gold_token_record, algo_token_record, OK) )

            if 'bastard' in line_ambi:

                correct_unknown += result_m
                max_value_unknown += 1.0
            else:
                max_value_known += 1.0
                correct_known += result_m

            diff = get_diff_between_tokens( gold_token_record, algo_token_record )
            for error in diff:
                errors[ error[0] ] += 1

            #считаем верхнюю границу
            results_ambig = sum([  M( ambig_token, gold_token_record) for ambig_token in ambig_token_records ])
            if results_ambig > 0.0:
                upper_bound += 1.0
            else:
                pass

        else:
            context.append( (gold_token_record, algo_token_record, OK) )

    for i,data in enumerate(context):
        gold_token = data[0]
        algo_token = data[1]
        outcome = data[2]

        prev_data = context[i - 1] if i > 0 and context[i - 1][2] != EOS else None

        next_data = context[ i + 1] if i < len( context ) - 1 and context[i + 1][2] != EOS else None

        if outcome == ERROR:
            error_context_f.write("{0}\t{1}\t{2}\r\n".format( prev_data[0].word.encode('utf-8') if prev_data else '', gold_token.word.encode('utf-8'),   next_data[0].word.encode('utf-8') if next_data else '' ) )
            error_context_f.write("{0}\t{1}\t{2}\r\n".format( prettify_gram(prev_data[0].gram).encode('utf-8') if prev_data else '', prettify_gram(gold_token.gram).encode('utf-8'),   prettify_gram(next_data[0].gram).encode('utf-8') if next_data else '' ) )
            error_context_f.write("{0}\t{1}\t{2}\r\n".format( prettify_gram(prev_data[1].gram).encode('utf-8') if prev_data else '', prettify_gram(algo_token.gram).encode('utf-8'),  prettify_gram(next_data[1].gram).encode('utf-8') if next_data else '' ) )

            token_diff = get_diff_between_tokens( gold_token, algo_token )
            token_diff_error_pos_names = [err[0]  for err in token_diff ]
            token_diff_error_ids = [err[1]  for err in token_diff ]

            gold_tk = gold_token.gram.split(',')
            algo_tk = algo_token.gram.split(',')
            if 'pos' in token_diff_error_pos_names:
                error_context_f.write("\t{0} -> {1}\t\r\n".format( gold_tk[0], algo_tk[0] ))
                error_context_f.write("\tpos\t\r\n")
            else:
                error_context_f.write("\t{0} -> {1}\t\r\n".format( ','.join( [gold_tk[idx] for idx in token_diff_error_ids]  ),  ','.join( [algo_tk[idx] for idx in token_diff_error_ids] )))
                error_context_f.write("\t{0}\t\r\n".format( ','.join( token_diff_error_pos_names  )))
            error_context_f.write("\r\n")
    #процессим контексты
    error_context_f.close()
    error_stat_f.close()

    algo_f.close()
    gold_f.close()
    ambi_f.close()
    return correct_unknown, correct_known, max_value_unknown, max_value_known,errors, upper_bound


def calculate_dir_precision(algo_dir, gold_dir, ambi_dir, M , N, P, errors_context_filename, errors_statistics_filename):

    algo_files = get_corpus_files(algo_dir)

    num = 0
    total_unknown = 0
    total_known = 0
    total_correct_unknown = 0
    total_correct_known = 0
    total_upperbound = 0
    total_error_stats = defaultdict(float)
    for algo_file in algo_files:
        print "Evaluating file {0}".format( algo_file )
        ambi_file = os.path.join( ambi_dir, os.path.basename( algo_file ) )
        gold_file = os.path.join( gold_dir, os.path.basename( algo_file ) )

        if os.path.exists( algo_file ) and os.path.exists( gold_file ):
            cur_correct_unknown, cur_correct_known, cur_total_unknown, cur_total_known,errors, cur_upper_bound = calculate_precision( file_algo_name= algo_file, file_gold_standart_name= gold_file,
                file_ambi_name = ambi_file, M=M , N=N, P=P,
                errors_context_filename = errors_context_filename,
                errors_statistics_filename = errors_statistics_filename )
            total_unknown += cur_total_unknown
            total_known += cur_total_known
            total = total_unknown + total_known
            total_correct_unknown += cur_correct_unknown
            total_correct_known += cur_correct_known
            total_correct = total_correct_unknown + total_correct_known
            total_upperbound += cur_upper_bound

            for k,v in errors.iteritems():
                total_error_stats[k] += v

            print "percent correct (total)", int(float(total_correct)/total*100)
            print "percent correct (known words)", int(float(total_correct_known)/total_known*100)

            print "percent (upper bound words)", int(float(total_upperbound)/total*100)


            if total_unknown:
                print "percent correct (unknown words)", int(float(total_correct_unknown)/total_unknown*100)

            total_errors = sum([v for v in total_error_stats.values() ])
            for k,v in total_error_stats.iteritems():
                print "error count in {0} is {1}".format( k,v*100.0/total_errors )

            num+=1
            print "{0} file processed. {1}%".format(gold_file, num/(len(algo_files)+0.0)*100 )
    return total_correct_known, total_correct_unknown, total_known, total_unknown, total_upperbound

if __name__=="__main__":
    print calculate_dir_precision(gold_dir=  r"/home/egor/disamb_test/gold/",algo_dir=r"/home/egor/disamb_test/test_hmm_base_tags",
        ambi_dir= r"/home/egor/disamb_test/test_ambig", M =M_strict_mathcher,  N =  N_rnc_positional_microsubset, P = P_no_garbage,
        errors_context_filename = r"/home/egor/disamb_test/hmm_errors_context.txt",
        errors_statistics_filename = r"/home/egor/disamb_test/hmm_errors_statistics.txt")
