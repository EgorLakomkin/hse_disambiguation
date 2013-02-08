# -*- coding: utf-8 -*-
import codecs
import os
from random import choice, shuffle
import sys
from morphomon.eval import calculate_dir_precision, M_strict_mathcher, P_no_garbage

__author__ = 'egor'
from morphomon.utils import EOS_TOKEN, get_word_ending, get_tokens_from_directory, dump_object, N_default, N_rnc_pos, get_tokens_from_file, load_object, get_corpus_files, remove_ambiguity_dir,  N_rnc_positional_microsubset, remove_directory_content, remove_ambiguity_file_list, N_rnc_positional_modified_tagset
from collections import defaultdict


def default_float():
    return defaultdict( float )

class NaiveAlgorithm(object):
    #реализация наивного алгоритма
    def __init__(self, corpus_dir = None, N_func = N_default):
        self.corpus_dict = defaultdict( default_float )
        self.filter_func = N_func
        if corpus_dir is not None:
            for token in get_tokens_from_directory( corpus_dir, N_filter_func = self.filter_func ):
                if token != [EOS_TOKEN]:
                    if len(token) > 1:
                       print "Ambiguity in corpus"
                       print "Pick random token"
                    token = choice(token)
                    token_word = token.word
                    token_word_ending = get_word_ending( token_word )
                    token_gram = token.gram
                    self.corpus_dict[ token_word_ending ][token_gram]+=1

    def train_from_filelist(self, file_list):
        self.corpus_dict = defaultdict( default_float )
        for file in file_list:
            print >>sys.stderr, "Baseline algo train on file {0}".format( file )
            for token in get_tokens_from_file(file, N_filter_func = self.filter_func):
                if token != [EOS_TOKEN]:
                    if len(token) > 1:
                        print "Ambiguity in corpus"
                        print "Pick random token"
                    token = choice(token)
                    token_word = token.word
                    token_word_ending = get_word_ending( token_word )
                    token_gram = token.gram
                    self.corpus_dict[ token_word_ending ][token_gram]+=1

    def find_ambiguity_words(self):
        for word in self.corpus_dict:
            if len( self.corpus_dict[word] ) > 1:
                print "ambiguity word %s" % ( word )

    def get_token_freq(self, token):
        pass


    def remove_ambiguity_sentence(self, variants):
        #на вход приходит

        for variant in variants:
            word = variant[0]
            token_variants = variant[1]
            for token in token_variants:
                max_variant_val = -1
                max_variant = None
                val = self.corpus_dict[  get_word_ending(word)  ][token.gram]
                if val > max_variant_val:
                    max_variant = token
            yield (max_variant.word, max_variant.gram)

    def remove_ambiguity_file(self, file, outfile):
        out_f =  codecs.open( outfile, 'w', 'utf-8' )
        sentence = []
        for token in get_tokens_from_file(file, N_filter_func= self.filter_func):
            if len(token) == 1 and token[0] == EOS_TOKEN:
                no_ambig_tokens = self.remove_ambiguity_sentence( sentence )
                for no_ambig_token in no_ambig_tokens:
                    out_f.write( u"{0}\t{1}={2}\r\n".format(no_ambig_token[0], 'nolemma', no_ambig_token[1] ) )
                out_f.write('\r\n')
                sentence = []
                continue

            sentence.append( (token[0].word, token) )
        out_f.close()


def naive_cross_validate(corpus_dir, algo_dir, morph_analysis_dir, N_func):

    corpus_files = get_corpus_files(corpus_dir)

    results = []
    for i in range(1,5):
        shuffle( corpus_files )
        remove_directory_content(algo_dir)
        print "Starting {0} fold".format( i )
        train_fold_corpus_files = corpus_files[:len(corpus_files)*4/5]
        test_corpus_files = corpus_files[len(corpus_files)*4/5:]
        naive_algo = NaiveAlgorithm(N_func=N_func)
        naive_algo.train_from_filelist( train_fold_corpus_files )
        print "Finished training. Starting testing phase!"
        morph_analysis_files = [ os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) for test_file in test_corpus_files if os.path.exists( os.path.join( morph_analysis_dir, os.path.basename( test_file ) ) )]
        remove_ambiguity_file_list(ambig_filelist=morph_analysis_files, output_dir= algo_dir, algo =naive_algo )
        print "Finished working of algo. Starting measuring phase"
        total_correct_known, total_correct_unknown, total_known, total_unknown = calculate_dir_precision( algo_dir = algo_dir, ambi_dir= morph_analysis_dir, gold_dir =  corpus_dir, M = M_strict_mathcher, N =  N_func, P = P_no_garbage,
            errors_context_filename = r"/home/egor/disamb_test/naive_errors_context_{0}.txt".format( i ),
            errors_statistics_filename = r"/home/egor/disamb_test/naive_errors_statistics_{0}.txt".format( i ))
        results.append((total_correct_known, total_correct_unknown, total_known, total_unknown ) )
    avg_known_prec = sum([result[0] for result in results]) * 100.0 / sum([result[2] for result in results])
    avg_unknown_prec = sum([result[1] for result in results]) * 100.0 / sum([result[3] for result in results])
    print "Average precision known : {0}%".format( avg_known_prec )
    print "Average precision unknown : {0}%".format( avg_unknown_prec )
    print results

if __name__ == "__main__":

    #naive_algo = NaiveAlgorithm( corpus_dir = "/home/egor/disamb_test/gold/", N_func= N_rnc_positional_microsubset )
    #dump_object( r"/home/egor/disamb_test/naive_positional_full.dat" , naive_algo  )
    #naive_algo = load_object( r"/home/egor/disamb_test/naive_positional_full.dat" )
    #naive_algo.remove_ambiguity_file(r"C:\disamb_test\mystem_txt\_rbk2_2140.txt", r"C:\disamb_test\algo_output\_rbk2_2140.txt" )
    #remove_ambiguity_dir(corpus_dir = r"/home/egor/disamb_test/mystem_txt",output_dir = r"/home/egor/disamb_test/naive_full_tag_output", algo = naive_algo )
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


    naive_cross_validate( corpus_dir =gold_dir, algo_dir= ambig_dir, morph_analysis_dir= algo_dir, N_func = N_rnc_pos )