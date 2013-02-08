# -*- coding: utf-8 -*-
import codecs
from collections import defaultdict
import os
from random import shuffle
import math
from morphomon.algorithm.statistics import calculate_B, calculate_A, train_A_corpus, train_B_corpus, train_A_corpus_lst_files, train_B_lst_files
from morphomon.eval import calculate_dir_precision, P_no_garbage, M_strict_mathcher
from morphomon.utils import get_word_ending, TokenRecord, N_default, load_object, get_tokens_from_file, EOS_TOKEN, N_rnc_pos, remove_ambiguity_dir,  dump_object, N_rnc_positional_microsubset, N_rnc_positional, remove_ambiguity_file_list, remove_directory_content, get_corpus_files, N_rnc_positional_modified_tagset

__author__ = 'egor'


class HMMAlgorithm(object):

    #реализация алгоритма на основе HMM
    def __init__(self, A = None , B = None, p = None , N_filter_func = N_default):
        self.filter_func = N_filter_func
        if A and B and p:
            self.B = B
            self.A = A
            self.p = p
            self.init()

    def init(self):
        gram_pr = set()
        for key in self.B:
            for ending in self.B[key]:
                gram_pr.add(key)

        self.X = set([ending for gram in self.B for ending in self.B[gram]])

        self.Y = set([gram for gram in gram_pr])

    def train_model_from_filelist(self, corpus_files):
        self.B = train_B_lst_files(corpus_lst_files = corpus_files,N_filter_func = self.filter_func)
        self.A,self.p = train_A_corpus_lst_files(corpus_lst_files = corpus_files,N_filter_func  = self.filter_func)

        self.init()

    def train_model(self, corpus_dir ):
        self.B = train_B_corpus(corpus_dir = corpus_dir,N_filter_func = self.filter_func)
        self.A,self.p = train_A_corpus(corpus_dir = corpus_dir,N_filter_func  = self.filter_func)

        self.init()


    def remove_ambiguity_file(self, file, outfile):
        out_f =  codecs.open( outfile, 'w', 'utf-8' )
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if len(token) == 1 and token[0] == EOS_TOKEN:
                no_ambig_tokens = self.remove_ambiguity( sentence )
                for no_ambig_token in no_ambig_tokens:
                    out_f.write( u"{0}\t{1}={2}\r\n".format(no_ambig_token[0], 'nolemma', no_ambig_token[1] ) )
                out_f.write('\r\n')
                sentence = []
                continue

            sentence.append( (token[0].word, token) )
        out_f.close()

    def remove_ambiguity_dir(self, dir):
        pass

    def remove_ambiguity(self, variants):
        #формат входящих данных
        #список tuple из словоформы и списка ее вариантов разбора
        #формат исходящих данных
        #список tuple

        phi = defaultdict(lambda: defaultdict(float))

        backtrace = defaultdict(lambda: defaultdict(str))
        path = []

        all_states = ['start'] + list(self.Y)
        for state in all_states:
            phi[-1][state] = 0.0
            self.A['start'][state] = self.p[state]

        prev_states = [ 'start' ]
        #проходим все наблюдения
        for i,obs in enumerate(variants):

            current_word_form = obs[0]
            current_word_form_ending = get_word_ending(current_word_form)
            list_of_possible_grams = [token_record.gram for token_record in obs[1]]
            #перебираем все возможные следующие состояния
            for state in list_of_possible_grams:
                max_prob = float('-inf')
                source_state = None
                #находим максимальный путь до состояния Y
                for prev_state in prev_states:
                    prob = phi[i-1][prev_state] + self.A[prev_state][ state ] + self.B[ state ][current_word_form_ending]
                    if prob > max_prob:
                        max_prob = prob
                        source_state = prev_state
                        #записываем max P(x1..xi,y1..i)
                phi[i][state] = max_prob
                backtrace[i][state] = source_state

            prev_states = list_of_possible_grams

        #начинаем back_trace

        last_state = None
        max_prob = float('-inf')

        #ищем максимальное состояние
        for key in phi[len(variants) - 1]:
            prob = phi[len(variants) - 1][key]
            if prob > max_prob:
                max_prob = prob
                last_state = key

        it_state = last_state
        path.append(last_state)
        #проходим с конца и записываем в путь предыдущие состояния
        for index in reversed(range(1,len(variants))):
            path.append( backtrace[index][it_state] )
            it_state = backtrace[index][it_state]

        word_forms = [x[0] for x in variants]

        return zip(word_forms,path[::-1])

def hmm_cross_validate(corpus_dir, algo_dir, morph_analysis_dir, N_func):

    corpus_files = get_corpus_files(corpus_dir)

    results = []
    num_iters = 1
    for i in range(1,num_iters + 1):
        shuffle( corpus_files )
        remove_directory_content(algo_dir)
        print "Starting {0} fold".format( i )
        train_fold_corpus_files = corpus_files[:len(corpus_files)*4/5]
        test_corpus_files = corpus_files[len(corpus_files)*4/5:]
        hmm_algo = HMMAlgorithm(N_filter_func=N_func)
        hmm_algo.train_model_from_filelist(corpus_files =  train_fold_corpus_files )
        print "Finished training. Starting testing phase!"
        morph_analysis_files = [ os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) for test_file in test_corpus_files if os.path.exists( os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) )]
        remove_ambiguity_file_list(ambig_filelist=morph_analysis_files, output_dir= algo_dir, algo =hmm_algo )
        print "Finished working of algo. Starting measuring phase"
        total_correct_known, total_correct_unknown, total_known, total_unknown, upper_bound  = calculate_dir_precision( algo_dir = algo_dir, ambi_dir= morph_analysis_dir, gold_dir =  corpus_dir, M = M_strict_mathcher, N =  N_func, P = P_no_garbage,
            errors_context_filename = r"/home/egor/disamb_test/hmm_errors_context_{0}.txt".format( i ),
            errors_statistics_filename = r"/home/egor/disamb_test/hmm_errors_statistics_{0}.txt".format( i ))
        results.append((total_correct_known, total_correct_unknown, total_known, total_unknown, upper_bound  ) )

    avg_prec = sum([(result[0]+result[1])*100.0/(result[2] + result[3]) for result in results])  / len( results )
    std_dev = math.sqrt( sum([ ((result[0]+result[1])*100.0/(result[2] + result[3])- avg_prec)* ((result[0]+result[1])*100.0/(result[2] + result[3]) - avg_prec) for result in results ] )  / num_iters )

    avg_known_prec = sum([result[0]*100.0/result[2] for result in results])  / len( results )
    avg_unknown_prec = sum([result[1]*100.0/result[3] for result in results])  / len( results )
    std_dev_known = math.sqrt( sum([ (result[0]*100.0/result[2]- avg_known_prec)* (result[0]*100.0/result[2] - avg_known_prec) for result in results ] )  / num_iters )
    std_dev_unknown = math.sqrt( sum([ (result[1]*100.0/result[3]- avg_unknown_prec)* (result[1]*100.0/result[3] - avg_unknown_prec) for result in results ] )  / num_iters )
    avg_upper_bound = sum([result[4]*100.0/(result[2]+result[3]) for result in results])  / len( results )

    stdev_upper_bound = math.sqrt( sum([ (result[4]*100.0/(result[2]+result[3]) - avg_upper_bound)* (result[4]*100.0/(result[2]+result[3]) - avg_upper_bound )  for result in results ]  )  / num_iters )

    print "Total Average precision  : {0}%".format( avg_prec )
    print "Total StdDev  : {0}%".format( std_dev)

    print "Average precision known : {0}%".format( avg_known_prec )
    print "StdDev known : {0}%".format( std_dev_known )

    print "Average precision unknown : {0}%".format( avg_unknown_prec )
    print "StdDev unknown : {0}%".format( std_dev_unknown )
    print "Average upper bound : {0}%".format( avg_upper_bound )

    print "StdDev upperbound : {0}%".format( stdev_upper_bound )

    print results

if __name__=="__main__":


    #hmm_algo = HMMAlgorithm()
    #hmm_algo.train_model( corpus_dir= "/home/egor/disamb_test/gold/" , N_filter_func= N_rnc_positional_microsubset)
    #dump_object( r"/home/egor/disamb_test/hmm_base_tags.dat",  hmm_algo )
    #hmm_algo = load_object( r"/home/egor/disamb_test/hmm_base_tags.dat"  )
    #remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/test_ambig",output_dir = r"/home/egor/disamb_test/test_hmm_base_tags", algo = hmm_algo )

    import ConfigParser

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', '--config')
    args = parser.parse_args()
    config = ConfigParser.RawConfigParser()
    config.read( args.config )

    gold_dir = config.get( "dir", "gold_dir" )
    ambig_dir = config.get( "dir", "morph_analysis_dir" )
    algo_dir = config.get( "dir", "algo_dir" )

    hmm_cross_validate( corpus_dir = gold_dir, algo_dir= algo_dir,
        morph_analysis_dir=ambig_dir, N_func = N_rnc_pos )