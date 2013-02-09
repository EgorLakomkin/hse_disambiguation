# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
import multiprocessing
import os
from random import shuffle
import sys
import math
from morphomon.algorithm.hmm_disambig import HMMAlgorithm
from morphomon.algorithm.mmem_disambig import MMEMAlgorithm
from morphomon.algorithm.naive import NaiveAlgorithm
from morphomon.utils import N_rnc_pos, get_corpus_files, get_diff_between_tokens, parse_token, EOS_TOKEN, split_seq, remove_directory_content, flatten, remove_ambiguity_file_list, get_dirs_from_config, tag_set_name_N

__author__ = 'egor'


garbage_tags = [ 'init', 'abbr', 'ciph', 'nonlex' ]

class ALGONAMES:
    BASELINE = 'baseline'
    HMM = 'hmm'
    MEMM = 'memm'

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
    upper_bound_known = 0.0
    upper_bound_unknown = 0.0


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
                if 'bastard' in line_ambi:
                    upper_bound_unknown += 1.0
                else:
                    upper_bound_known += 1.0


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
    return correct_unknown, correct_known, max_value_unknown, max_value_known,errors, upper_bound_unknown, upper_bound_known


def calculate_dir_precision(algo_dir, gold_dir, ambi_dir, M , N, P, errors_context_filename, errors_statistics_filename):

    algo_files = get_corpus_files(algo_dir)

    num = 0
    total_unknown = 0
    total_known = 0
    total_correct_unknown = 0
    total_correct_known = 0
    total_upperbound_known = 0
    total_upperbound_unknown = 0

    total_error_stats = defaultdict(float)
    for algo_file in algo_files:
        print "Evaluating file {0}".format( algo_file )
        ambi_file = os.path.join( ambi_dir, os.path.basename( algo_file ) )
        gold_file = os.path.join( gold_dir, os.path.basename( algo_file ) )

        if os.path.exists( algo_file ) and os.path.exists( gold_file ):
            cur_correct_unknown, cur_correct_known, cur_total_unknown, cur_total_known,errors, cur_upper_bound_unknown,cur_upper_bound_known  = calculate_precision( file_algo_name= algo_file, file_gold_standart_name= gold_file,
                file_ambi_name = ambi_file, M=M , N=N, P=P,
                errors_context_filename = errors_context_filename,
                errors_statistics_filename = errors_statistics_filename )
            total_unknown += cur_total_unknown
            total_known += cur_total_known
            total = total_unknown + total_known
            total_correct_unknown += cur_correct_unknown
            total_correct_known += cur_correct_known
            total_correct = total_correct_unknown + total_correct_known
            total_upperbound_known += cur_upper_bound_known
            total_upperbound_unknown += cur_upper_bound_unknown

            for k,v in errors.iteritems():
                total_error_stats[k] += v

            print "percent correct (total)", int(float(total_correct)/total*100)
            print "percent correct (known words)", int(float(total_correct_known)/total_known*100)

            print "percent (upper bound words)", int(float(total_upperbound_unknown + total_upperbound_known)/total*100)


            if total_unknown:
                print "percent correct (unknown words)", int(float(total_correct_unknown)/total_unknown*100)

            total_errors = sum([v for v in total_error_stats.values() ])
            for k,v in total_error_stats.iteritems():
                print "error count in {0} is {1}".format( k,v*100.0/total_errors )

            num+=1
            print "{0} file processed. {1}%".format(gold_file, num/(len(algo_files)+0.0)*100 )
    return total_correct_known, total_correct_unknown, total_known, total_unknown, total_upperbound_known, total_upperbound_unknown


_NAIVE_CV_GLOBALS = None

def cross_validate_inner(i):
    corpus_dir, algo_dir, morph_analysis_dir, N_func, error_dir, num_iters, corpus_files, splits, algo_name = _NAIVE_CV_GLOBALS

    remove_directory_content(algo_dir)
    print "Starting {0} fold".format( i )
    train_fold_corpus_files = flatten(splits[j] for j in range(num_iters) if i != j)
    test_corpus_files = flatten(splits[j] for j in range(num_iters) if i == j)

    morph_analysis_files = [ os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) for test_file in test_corpus_files if os.path.exists( os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) )]
    algo = None
    if algo_name == ALGONAMES.BASELINE:
        algo = NaiveAlgorithm(N_func=N_func)
        algo.train_from_filelist( train_fold_corpus_files )
    elif algo_name == ALGONAMES.HMM:
        algo = HMMAlgorithm(N_filter_func=N_func)
        algo.train_model_from_filelist(corpus_files =  train_fold_corpus_files )
    elif algo_name == ALGONAMES.MEMM:
        algo = MMEMAlgorithm(N_filter_func=N_func)
        algo.train_model_file_list(corpus_filelist =  train_fold_corpus_files, ambiguity_dir = morph_analysis_dir )
    if algo is None:
        raise Exception("Not supported algorithm {0}".format( algo_name ))

    print "Finished training. Starting testing phase!"
    remove_ambiguity_file_list(ambig_filelist=morph_analysis_files, output_dir= algo_dir, algo = algo )
    print "Finished working of algo. Starting measuring phase"
    total_correct_known, total_correct_unknown, total_known, total_unknown, upper_bound_known,upper_bound_unknown  = calculate_dir_precision( algo_dir = algo_dir, ambi_dir= morph_analysis_dir, gold_dir =  corpus_dir, M = M_strict_mathcher, N =  N_func, P = P_no_garbage,
        errors_context_filename = os.path.join(error_dir, "naive_errors_context_{0}.txt".format( i )),
        errors_statistics_filename = os.path.join(error_dir, "naive_errors_statistics_{0}.txt".format( i )) )

    return (total_correct_known, total_correct_unknown, total_known, total_unknown, upper_bound_known,upper_bound_unknown )


def cross_validate(num_iters, algo_name, corpus_dir, algo_dir, morph_analysis_dir, N_func, error_dir):
    global _NAIVE_CV_GLOBALS

    corpus_files = get_corpus_files(corpus_dir)
    shuffle(corpus_files)
    splits = split_seq(corpus_files, num_iters)

    _NAIVE_CV_GLOBALS = [ corpus_dir, algo_dir, morph_analysis_dir, N_func, error_dir, num_iters, corpus_files, splits, algo_name ]

    pool = multiprocessing.Pool()
    results = pool.map(cross_validate_inner, range(num_iters))
    pool.close()
    pool.join()

    def summary(seq):
        q, s, n = 0.0, 0.0, 0.0
        for x in seq:
            q += x * x
            s += x
            n += 1.0
        avg = s / n
        dev = q / n - avg ** 2
        return avg, dev

    prec         = list( (tck + tcu) / (tk + tu) for tck, tcu, tk, tu, _, _ in results )
    known_prec   = list( tck / tk                for tck, tcu, tk, tu, _, _ in results )
    unknown_prec = list( tcu / tu                for tck, tcu, tk, tu, _, _ in results )

    ub_known     = list( ubk / tk for tck, tcu, tk, tu, ubk, ubu in results )
    ub_unknown   = list( ubu / tu for tck, tcu, tk, tu, ubk, ubu in results )

    print "RESULT:         total precision: {0:.4f}% +- {1:.4f}%".format(*summary(prec))
    print "RESULT:      by-known precision: {0:.4f}% +- {1:.4f}%".format(*summary(known_prec))
    print "RESULT:    by-unknown precision: {0:.4f}% +- {1:.4f}%".format(*summary(unknown_prec))
    print "RESULT:   upper bound by knowns: {0:.4f}% +- {1:.4f}%".format(*summary(ub_known))
    print "RESULT: upper bound by unknowns: {0:.4f}% +- {1:.4f}%".format(*summary(ub_unknown))
    print "RESULT: " # Just a separator.
    print "RESULT: Finished {0} algorithm with {1} tagset".format( algo_name, N_func )
    print "RESULT: Raw: " + repr(results)

if __name__=="__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', '--config')
    parser.add_argument('-err', '--error')
    parser.add_argument('-alg','--algorithm')
    parser.add_argument('-gold_dir','--gold_dir')
    parser.add_argument('-algo_dir','--algo_dir')
    parser.add_argument('-morph_dir','--morph_dir')
    parser.add_argument('-tag_type','--tag_type')
    parser.add_argument('-num_iters','--num_iters')

    args = parser.parse_args()

    gold_dir, ambig_dir, algo_dir = args.gold_dir, args.morph_dir, args.algo_dir
    tag_type = args.tag_type
    num_iters = int(args.num_iters)

    algo_name = args.algorithm
    cross_validate(num_iters = num_iters, algo_name= algo_name, corpus_dir = gold_dir,
        algo_dir= algo_dir, morph_analysis_dir= ambig_dir, N_func = tag_set_name_N.get( tag_type ), error_dir = args.error)