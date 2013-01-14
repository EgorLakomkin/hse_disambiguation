# -*- coding: utf-8 -*-
from morphomon.algorithm.hmm_disambig import HMMAlgorithm
from morphomon.pymorphy_utils import get_morph_info

__author__ = 'egor'

from morphomon.utils import get_word_ending,N_rnc_pos,dump_object, load_object, parse_token, get_tokens_from_file,N_ruscorpora_tagset,N_rnc_pos, pymorphy_info_token_record_converter, N_pymorphy_tagset_POS, EOS_TOKEN


if __name__=="__main__":
    #B = load_object(filename="/home/egor/B_POS_rnc.dat")
    #A = load_object(filename="/home/egor/A_POS_rnc.dat")
    #p = load_object(filename="/home/egor/p_POS_rnc.dat")

    #gram_pr = set()
    #for key in B:
    #    for ending in B[key]:
    #        gram_pr.add(key)


    #X = set([ending for gram in B for ending in B[gram]])

    #Y = set([gram for gram in gram_pr])

    B = load_object(filename="/home/egor/B_POS_rnc.dat")
    A = load_object(filename="/home/egor/A_POS_rnc.dat")
    p = load_object(filename="/home/egor/p_POS_rnc.dat")

    hmm_algo = HMMAlgorithm( B= B , A = A , p = p, corpus_file= None )


    gold_standart = get_tokens_from_file( corpus_file = "/home/egor/rnc.txt", N_filter_func = N_rnc_pos )

    sentence = []
    gold_sentence = []
    pos_ambiguity_flag = False
    total_words = 0.0
    score_words = 0.0
    total_sentences = 0
    score_sentences = 0

    for token in gold_standart:
        gold_token = token[0]

        if gold_token.gram == EOS_TOKEN.gram:


            print "Анализ омонимичного предложения"
            print ' '.join( tup[0] for tup in sentence )

            print "Снимаем омонимию"
            no_ambig =  hmm_algo.remove_ambiguity(sentence)


            cor_words = 0
            for token_idx, token in enumerate(no_ambig):
                print token[0], token[1]
                if unicode(token[1]) == gold_sentence[token_idx][1]:
                    score_words += 1.0
                    cor_words +=1
                else:
                    print r"////////////////////////////////////////////"
                    print "Несовпадение в грам признаках"
                    print "Слово", gold_sentence[token_idx][0], "алгоритм - ", token[1], " в НКРЯ : ", gold_sentence[token_idx][1]
                    print "То что выдавал pymorphy"
                    token = sentence[ token_idx ][1]
                    for tok in token:
                        print "Грам признак", tok.gram
                    print r"////////////////////////////////////////////"
                total_words += 1.0
            print "+++++++++++++++++++++++++++++"
            for gold in gold_sentence:
                print gold[0], gold[1]

            if pos_ambiguity_flag:
                if cor_words == len(gold_sentence):
                    score_sentences +=1
                total_sentences +=1
            if (total_sentences!=0):
                print "Правильно была распознана омонимия в ", (float(score_sentences)/ total_sentences) * 100 , "% предложений"
            print "Правильно была распознана омонимия в ", (score_words/ total_words) * 100 , "% слов"
            print "*************************"



            sentence = []
            gold_sentence = []
            pos_ambiguity_flag = False
            continue

        gold_token_word = gold_token.word
        gold_token_lemma = gold_token.lemma
        gold_token_gram = gold_token.gram

        pymorphy_info = get_morph_info( gold_token_word )

        test_token_records = pymorphy_info_token_record_converter(gold_token_word, pymorphy_info, N_processor = N_pymorphy_tagset_POS)

        pos_amb = set()
        for token_record in test_token_records:
            pos_amb.add( token_record.gram )

        if len( pos_amb ) > 1:
            pos_ambiguity_flag = True

        sentence.append( (gold_token_word, test_token_records) )
        gold_sentence.append( (gold_token_word,gold_token_gram ) )


