# -*- coding: utf-8 -*-
import codecs
from collections import namedtuple
import re


def get_word_ending(word, enging_length = 3):
    ending = word[-enging_length:]
    return ending

TokenRecord = namedtuple('TokenRecord', 'word, lemma, gram')
#паттерн токена для корпуса со снятой омонимией
token_pattern = ur'^(?P<token_name>.*?)\t(?P<token_lemma>.*?)=(?P<token_gram>.*)$'

def parse_token(line):
    match = re.match(token_pattern, line)
    return TokenRecord(word = match.group('token_name'), lemma = match.group('token_lemma'),
        gram = match.group('token_gram'))

def get_tokens_from_corpora(corpus_file):
    corpus =  codecs.open( corpus_file, 'r', 'utf-8' )
    data = corpus.read().split('\n')
    for token in data:
        token = token.strip()
        if len(token) > 0:
            yield parse_token(token)
