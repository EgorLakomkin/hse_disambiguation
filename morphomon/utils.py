# -*- coding: utf-8 -*-
import codecs
from collections import namedtuple
import os
import pickle
import re
from sys import stderr


def get_word_ending(word, enging_length = 3):
    ending = word[-enging_length:]
    return ending.lower()

TokenRecord = namedtuple('TokenRecord', 'word, lemma, gram')
#паттерн токена для корпуса со снятой омонимией
token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'

EOS_TOKEN = TokenRecord(word='',lemma='',gram='EOS')


pymorphy_coverter = dict()
pymorphy_coverter[u'с'] = "s"
pymorphy_coverter[u'п'] = "a"
pymorphy_coverter[u'г'] = "v"
pymorphy_coverter[u'мс'] = "s-pro"
pymorphy_coverter[u'причастие'] = "v"
pymorphy_coverter[u'деепричастие'] = "v"
pymorphy_coverter[u'инфинитив'] = "v"
pymorphy_coverter[u'мс-предк'] = "praedic-pro"
pymorphy_coverter[u'мс-п'] = "a-pro"
pymorphy_coverter[u'числ'] = "num"
pymorphy_coverter[u'числ-п'] = "a-num"
pymorphy_coverter[u'н'] = "adv"
pymorphy_coverter[u'предк'] = "praedic"
pymorphy_coverter[u'предл'] = "pr"
pymorphy_coverter[u'союз'] = "conj"
pymorphy_coverter[u'межд'] = "intj"
pymorphy_coverter[u'част'] = "part"
pymorphy_coverter[u'вводн'] = "parenth"
pymorphy_coverter[u'кр_прил'] = "a"
pymorphy_coverter[u'кр_причастие'] = "v"

def N_pymorphy_tagset_POS(tagset):
    token_grams = tagset.split(',')
    gram_class = token_grams[0].lower()
    try:
        return pymorphy_coverter[gram_class]
    except:
        pass


def N_ruscorpora_tagset(tagset):
    token_grams = tagset.split(',')
    token_grams = [tag for gram_tag in token_grams for tag in gram_tag.split('=')]
    token_grams[0] = mystem_rnc_pos_convert( token_grams[0] )
    return ','.join(token_grams)

def N_mystem_tagset(tagset):
    #
    token_grams = tagset.split(',')
    return token_grams[0]

def N_default(tagset):
    """
    Возвращаем неизмененный тагсет
    """
    return tagset


def mystem_rnc_pos_convert(pos_tag):
    if pos_tag == 'spro':
        return 's-pro'
    if pos_tag == 'advpro':
        return 'adv-pro'
    if pos_tag == 'apro':
        return 'a-pro'
    if pos_tag == 'anum':
        return 'a-num'
    return pos_tag


def N_rnc_pos(tag_set):
    """
    Возвращаем первый тег - тег отвечающий за часть речи во всех системах
    """
    token_grams = N_ruscorpora_tagset(tag_set.lower())
    token_grams = token_grams.split(',')
    token_grams[0] = mystem_rnc_pos_convert( token_grams[0] )
    if token_grams[0] in pos_tag:
        return token_grams[0]
    else:
        return 's'


def N_rnc_default_tags(tag_set):
    """
    Возвращаем первый тег - тег отвечающий за часть речи во всех системах
    """
    token_grams = N_ruscorpora_tagset(tag_set.lower())
    token_grams = token_grams.split(',')
    pos_tag = mystem_rnc_pos_convert( token_grams[0] )
    gram_tags = filter( lambda x : x in default_tags, token_grams[1:] )
    return ','.join( [pos_tag] + gram_tags )


pos_tag = ['s-pro','adv-pro','a-pro','s','a','num','a-num','v','adv', 'praedic','parenth', 'praedic-pro', 'pr','conj','part', 'intj']
gender_tags = ['m','f','n','m-f']
anim_tags = ['anim','inan']
number_tags = ['sg','pl']
case_tags = ['nom','gen','gen2','dat','dat2', 'acc','acc2', 'ins','loc','loc2', 'voc', 'adnum']
form_tags = ['brev','plen']
degree_tags = ['comp','comp2','supr']
type = ['pf','ipf']
pereh_tags = ['intr', 'tran']
zalog_tags = ['act','pass', 'med']
verb_form = ['inf','partcp', 'ger']
naklon_tags = ['indic', 'imper','imper2']
time_tags = ['praet','praes','fut']
person_tags = [ '1p','2p','3p' ]
other_tags = ['persn', 'patrn','famn', 'zoon', '0']
disamb_tag_set = [ 'anom', 'distort', 'ciph', 'init', 'abbr', 'nonlex' ]
no_doc_tagset = ['obsc']
pos_tagset = [ pos_tag ]


full_tag_set = [pos_tag, gender_tags,anim_tags, number_tags, case_tags, form_tags, degree_tags,
                type, pereh_tags, zalog_tags, verb_form, naklon_tags, time_tags, person_tags, other_tags, disamb_tag_set,no_doc_tagset ]

full_tag_set_str = ['pos', 'gender','amim', 'number', 'case', 'form', 'degree',
                'type', 'perehod', 'zalog', 'verb_form', 'naklon', 'time', 'person', 'other', 'rnc_disamb','not_in_docs' ]


used_micro_tag_subset = [ pos_tag, gender_tags, number_tags, case_tags, person_tags, disamb_tag_set ]

def find_matching_pos(tag, tag_set = full_tag_set, used_tagset = full_tag_set):
    for index, possible_tag_lst in enumerate(tag_set):
        if possible_tag_lst in used_tagset:
            if tag in possible_tag_lst:
                return index
    return None
    #raise Exception("no matching tag : {0}".format(tag) )

def N_rnc_positional_microsubset(tag_set, used_tagset = used_micro_tag_subset):
    token_grams = N_ruscorpora_tagset(tag_set.lower())
    token_grams = token_grams.split(',')
    result_tag_set_lst = ['' for i in range(len(full_tag_set))]
    for tag in token_grams:
        index = find_matching_pos( tag = tag, tag_set= full_tag_set, used_tagset = used_tagset )
        if index is not None:
            result_tag_set_lst[ index ] = tag
    return ','.join( result_tag_set_lst )


def N_rnc_positional(tag_set, used_tagset = full_tag_set):
    token_grams = N_ruscorpora_tagset(tag_set.lower())
    token_grams = token_grams.split(',')
    result_tag_set_lst = ['' for i in range(len(full_tag_set))]
    for tag in token_grams:
        index = find_matching_pos( tag = tag, tag_set= full_tag_set, used_tagset = used_tagset )
        if index is not None:
            result_tag_set_lst[ index ] = tag
    return ','.join( result_tag_set_lst )


def is_corpus_line_match_out_format(line):
    if re.match(token_pattern, line):
        return True
    return False

def parse_token(line, N_filter_func=N_default):
    tokens = set()

    if len(line) ==0:
        #
        return [ EOS_TOKEN ]

    if line == '.':
        return [ EOS_TOKEN ]

    tab_split = line.split('\t')
    wf = tab_split[0]
    lemmas = tab_split[1:]
    for lemma in lemmas:
        equal_idx = lemma.find('=')
        cur_lemma = lemma[:equal_idx]
        gram = N_filter_func(lemma[equal_idx + 1:])
        x = TokenRecord(word = wf, lemma = cur_lemma, gram = gram )
        tokens.add(x)

    return list(tokens)

def get_corpus_gram_tags(corpus_file):
    gram_set = set()
    for token_lst in get_tokens_from_file(corpus_file):
        for token in token_lst:
            token_grams = token.gram.split(',')
            for token_gram in token_grams:
                gram_set.add(token_gram)
    return gram_set

def get_corpus_files(corpus_path, pattern="*.*"):
    import os
    from glob import glob

    files = []
    start_dir = corpus_path

    for dir,_,_ in os.walk(start_dir):
        files.extend(glob(os.path.join(dir,pattern)))
    return files

def get_tokens_from_file(corpus_file,N_filter_func=N_default):
    corpus =  codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\r\n')
    for token in data:
        if not token:
            #здесь нашало нового предложения
            #выкидываем токен EOS
            yield [ EOS_TOKEN ]
        else:
            yield  parse_token(token,N_filter_func = N_filter_func)

def get_tokens_from_directory(corpus_dir, file_pattern = "*.*", N_filter_func = N_default):
    files = get_corpus_files(corpus_dir, pattern = file_pattern )
    for file in files:
        for token in get_tokens_from_file(file,N_filter_func=N_filter_func ):
            yield token


def dump_object(filename, object):
    file = open(filename,'wb')
    pickle.dump(object, file)
    file.close()

def load_object(filename):
    file = open(filename,'rb')
    obj = pickle.load(file)
    file.close()
    return obj

def remove_ambiguity_dir( corpus_dir, output_dir, algo ):
    corpus_files = get_corpus_files(corpus_dir)

    num = 0
    for input_file_name in corpus_files:
       print "Starting file", input_file_name


       out_file = os.path.join( output_dir, os.path.basename( input_file_name ) )

       if os.path.exists( out_file ):
           num +=1
           continue


       algo.remove_ambiguity_file( input_file_name, out_file )

       num+=1
       print "{0} file processed. {1}%".format(input_file_name, num/(len(corpus_files)+0.0)*100 )

def pymorphy_info_token_record_converter(word, pymorphy_info, N_processor):
    lst = []
    for info in pymorphy_info:
        gram = info['class'] + ',' + info['info']
        lst.append( TokenRecord(word = word, lemma = info['norm'], gram = N_processor(gram) ) )
    return lst

def get_diff_between_tokens(token1, token2):
    token1_pos_gram = N_rnc_positional(token1.gram)
    token2_pos_gram = N_rnc_positional(token2.gram)

    token2_arr = token2_pos_gram.split(',')
    lst_errors = []
    for idx,gram in  enumerate( token1_pos_gram.split(',') ):
        if gram != token2_arr[idx]:
            lst_errors.append( full_tag_set_str[idx] )
    return lst_errors

if __name__ == "__main__":
    print N_rnc_positional("A=pl,tran=partCp,f", used_tagset = used_micro_tag_subset)