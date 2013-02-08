# -*- coding: utf-8 -*-
import codecs
from collections import namedtuple
import os
import pickle
import re
import sys
import multiprocessing


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


def N_ruscorpora_tagset_base_preprocess(tagset):
    token_grams = tagset.split(',')
    token_grams = [tag for gram_tag in token_grams for tag in gram_tag.split('=')]
    if 'adv' in token_grams and 'praedic' in token_grams:
        token_grams.remove('praedic')
    if 'adv' in token_grams and 'parenth' in token_grams:
        token_grams.remove('parenth')
    if 'gen2' in token_grams:
        token_grams.remove('gen2')
        token_grams.append('gen')

    if 'loc2' in token_grams:
        token_grams.remove('loc2')
        token_grams.append('loc')

    if 'dat2' in token_grams:
        token_grams.remove('dat2')

    if 'acc2' in token_grams:
        token_grams.remove('acc2')
        token_grams.append('nom')

    if 'voc' in token_grams:
        token_grams.remove('voc')

    if 'adnum' in token_grams:
        token_grams.remove('adnum')
        token_grams.append('gen')


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

    if pos_tag == 'praedic':
        return 'adv'

    if pos_tag == 'parenth':
        return 'adv'

    if pos_tag == 'praedic-pro':
        return 'adv'

    return pos_tag


def N_rnc_pos(tag_set):
    """
    Возвращаем первый тег - тег отвечающий за часть речи во всех системах
    """
    token_grams = N_ruscorpora_tagset_base_preprocess(tag_set.lower())
    token_grams = token_grams.split(',')
    token_grams[0] = mystem_rnc_pos_convert( token_grams[0] )
    if token_grams[0] in pos_tag:
        return token_grams[0]
    else:
        print >>sys.stderr, u"No pos tag was found in tagset : {0}. Treat as S".format( tag_set )
        return 's'



pos_tag = ['s-pro','adv-pro','a-pro','s','a','num','a-num','v','adv', 'praedic','parenth', 'praedic-pro', 'pr','conj','part', 'intj','abrev','vger','vpartcp']
gender_tags = ['m','f','n']
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
disamb_tag_set = [ 'anom', 'distort', 'ciph', 'init', 'abbr', 'nonlex', 'bastard']
no_doc_tagset = ['obsc']
pos_tagset = [ pos_tag ]


full_tag_set = [pos_tag, gender_tags,anim_tags, number_tags, case_tags, form_tags, degree_tags,
                type, pereh_tags, zalog_tags, verb_form, naklon_tags, time_tags, person_tags, other_tags, disamb_tag_set,no_doc_tagset ]

full_tag_set_str = ['pos', 'gender','amim', 'number', 'case', 'form', 'degree',
                'type', 'perehod', 'zalog', 'verb_form', 'naklon', 'time', 'person', 'other', 'rnc_disamb','not_in_docs' ]

filter_tags = ['norm','bastard']

used_micro_tag_subset = [ pos_tag, gender_tags, number_tags, case_tags, person_tags,time_tags, naklon_tags ]
used_modified_tag_subset = [ pos_tag, gender_tags, number_tags, case_tags, person_tags,time_tags, naklon_tags ]

def get_pos(positiona_tag_set):
    tag_set = positiona_tag_set.split(',')
    return tag_set[0] if len(tag_set)>0 and len(tag_set[0]) > 0 else None

def get_gender(positiona_tag_set):
    tag_set = positiona_tag_set.split(',')
    return tag_set[1] if len(tag_set)>1 and len(tag_set[1]) > 0 else None

def get_case(positiona_tag_set):
    tag_set = positiona_tag_set.split(',')
    return tag_set[4] if len(tag_set) > 5 and len(tag_set[4]) > 0 else None

def get_number(positiona_tag_set):
    tag_set = positiona_tag_set.split(',')
    return tag_set[3] if len(tag_set) > 4 and len(tag_set[3]) > 0 else None

def find_matching_pos(tag, tag_set = full_tag_set, used_tagset = full_tag_set):
    for index, possible_tag_lst in enumerate(tag_set):
        if possible_tag_lst in used_tagset:
            if tag in possible_tag_lst:
                return index

    #for debug purpose only
    for possible_tag_lst in tag_set:
        if tag in possible_tag_lst:
            return None
    print >>sys.stderr, u"Cannot find position for tag - {0}".format( tag )
    #raise Exception("no matching tag : {0}".format(tag) )

def N_rnc_positional_microsubset(tag_set):
    return N_rnc_positional( tag_set = tag_set, used_tagset = used_micro_tag_subset )

def N_rnc_positional_modified_pos(tag_set):
    tag_set = N_ruscorpora_tagset_base_preprocess(tag_set.lower())
    if 'a,' in tag_set and 'brev' in tag_set:
        tag_set = tag_set.replace('brev', '')
        tag_set = tag_set.replace('a,', 'abrev,',1)
    elif 'v,' in tag_set and 'partcp' in tag_set:
        tag_set = tag_set.replace('partcp', '')
        tag_set = tag_set.replace('v,', 'vpartcp,',1)
    elif 'v,' in tag_set and 'ger' in tag_set:
        tag_set = tag_set.replace('ger', '')
        tag_set = tag_set.replace('v,', 'vger,',1)
    return N_rnc_pos(tag_set)

def N_rnc_positional_modified_tagset(tag_set):
    tag_set = N_ruscorpora_tagset_base_preprocess(tag_set.lower())
    if 'a,' in tag_set and 'brev' in tag_set:
        tag_set = tag_set.replace('brev', '')
        tag_set = tag_set.replace('a,', 'abrev,',1)
    elif 'v,' in tag_set and 'partcp' in tag_set:
        tag_set = tag_set.replace('partcp', '')
        tag_set = tag_set.replace('v,', 'vpartcp,',1)
    elif 'v,' in tag_set and 'ger' in tag_set:
        tag_set = tag_set.replace('ger', '')
        tag_set = tag_set.replace('v,', 'vger,',1)
    return N_rnc_positional( tag_set = tag_set, used_tagset = used_micro_tag_subset )


def N_rnc_positional(tag_set, used_tagset = full_tag_set):


    token_grams = N_ruscorpora_tagset_base_preprocess(tag_set.lower())
    token_grams = [token for token in token_grams.split(',') if len(token) > 0 and token not in filter_tags]
    result_tag_set_lst = ['' for i in range(len(full_tag_set))]
    for tag in token_grams:
        if len(tag) == 0:
            print >>sys.stderr, "Error tagset : {0}".format( tag_set )
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
    corpus.close()

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

def remove_directory_content(folder):
    import os
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e

_RA_GLOBALS = None

def remove_ambiguity_file_list_inner(ambig_file):
    output_dir, algo = _RA_GLOBALS

    print "Starting removing ambiguity for file", ambig_file
    out_file = os.path.join( output_dir, os.path.basename( ambig_file ) )

    if os.path.exists( out_file ):
        print "Skipping file {0}".format( ambig_file )
        return False

    algo.remove_ambiguity_file( ambig_file, out_file )
    print "Finishing removing ambiguity for file", ambig_file
    return True

def remove_ambiguity_file_list(ambig_filelist, output_dir, algo):
    global _RA_GLOBALS
    _RA_GLOBALS = [ output_dir, algo ]
    pool = multiprocessing.Pool()
    n = pool.map(remove_ambiguity_file_list_inner, ambig_filelist)
    n = sum(1 for x in n if x)
    print "Processed {0} files out of {1}".format(n, len(ambig_filelist))

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
            lst_errors.append( (full_tag_set_str[idx], idx) )
    return lst_errors

def get_corpora_preps(corpus_dir):
    preps = set()
    for token in get_tokens_from_directory(corpus_dir, N_filter_func = N_rnc_pos):
        if 'pr' == token[0].gram:
            preps.add( '\'' + token[0].word.lower() + '\'')
    #preps = [prep.encode('utf-8') for prep in preps]
    return preps

def get_corpora_pluratives(corpus_dir):
    pluratives = set()
    for token in get_tokens_from_directory(corpus_dir, N_filter_func = N_rnc_positional_modified_tagset):
        token_gram = token[0].gram

        token_gender = get_gender( token_gram )
        token_number = get_number( token_gram )
        if token_number == 'pl' and token_gender is None and get_pos( token_gram ) == 's':
            pluratives.add( token[0].lemma.lower() )
    #preps = [prep.encode('utf-8') for prep in preps]
    return pluratives

if __name__ == "__main__":    
    pluratives = get_corpora_pluratives(corpus_dir= r"/home/egor/disamb_test/gold/" )
    
