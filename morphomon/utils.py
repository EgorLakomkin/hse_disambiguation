# -*- coding: utf-8 -*-
import codecs
from collections import namedtuple
import os
import re


def get_word_ending(word, enging_length = 3):
    ending = word[-enging_length:]
    return ending

TokenRecord = namedtuple('TokenRecord', 'word, lemma, gram')
#паттерн токена для корпуса со снятой омонимией
token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'

def parse_token(line):
    tokens = []
    m = re.search(u'(.*?)\t', line)
    if m != None:
        m1 = re.findall(u'\t(.*?)=([A-zА-яёЁ0-9,=\-]+)\t?', line)
        if m1 != None:
            for i in m1:
                x = TokenRecord(word = m.group(1).lower(), lemma = i[0].lower(), gram = (i[1].lower()))
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

def get_tokens_from_corpora(corpus_file):
    corpus =  codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\r\n')
    for token in data:
        if not token:
            #здесь нашало нового предложения
            #выкидываем токен EOS
            yield [TokenRecord(word='\n', lemma='\n', gram = 'EOS')]
        else:
            yield  parse_token(token)
