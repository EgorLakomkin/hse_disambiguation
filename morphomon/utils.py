# -*- coding: utf-8 -*-
import codecs
from collections import namedtuple
import pickle
import re


def get_word_ending(word, enging_length = 3):
    ending = word[-enging_length:]
    return ending

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

def N_rnc_pos(tag_set):
    """
    Возвращаем первый тег - тег отвечающий за часть речи во всех системах
    """
    token_grams = N_ruscorpora_tagset(tag_set)
    token_grams = token_grams.split(',')
    return token_grams[0]

def parse_token(line, N_filter_func=N_default):
    tokens = []
    m = re.search(u'(.*?)\t', line)
    if m != None:
        m1 = re.findall(u'\t(.*?)=([A-zА-яёЁ0-9,=\-]+)\t?', line)
        if m1 != None:
            for i in m1:
                x = TokenRecord(word = m.group(1).lower(), lemma = i[0].lower(), gram = N_filter_func( i[1].lower() ) )
                tokens.append(x)
    return tokens

def get_corpus_gram_tags(corpus_file):
    gram_set = set()
    for token_lst in get_tokens_from_corpora(corpus_file):
        for token in token_lst:
            token_grams = token.gram.split(',')
            for token_gram in token_grams:
                gram_set.add(token_gram)
    return gram_set

def get_corpus_files(corpus_path, pattern="*.xhtml"):
    import os
    from glob import glob

    files = []
    start_dir = corpus_path

    for dir,_,_ in os.walk(start_dir):
        files.extend(glob(os.path.join(dir,pattern)))
    return files

def get_tokens_from_corpora(corpus_file,N_filter_func=N_default):
    corpus =  codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\r\n')
    for token in data:
        if not token:
            #здесь нашало нового предложения
            #выкидываем токен EOS
            yield [TokenRecord(word='\n', lemma='\n', gram = 'EOS')]
        else:
            yield  parse_token(token,N_filter_func = N_filter_func)


def dump_object(filename, object):
    file = open(filename,'wb')
    pickle.dump(object, file)
    file.close()

def load_object(filename):
    file = open(filename,'rb')
    obj = pickle.load(file)
    file.close()
    return obj

def pymorphy_info_token_record_converter(word, pymorphy_info, N_processor):
    lst = []
    for info in pymorphy_info:
        gram = info['class'] + ',' + info['info']
        lst.append( TokenRecord(word = word, lemma = info['norm'], gram = N_processor(gram) ) )
    return lst

if __name__ == "__main__":
    print N_ruscorpora_tagset("A=pl,tran=partcp,f,sg")