# -*- coding: utf-8 -*-
from morphomon.utils import get_corpus_gram_tags, get_tokens_from_file

def find_word_by_tag(corpus_file, tag):
    #for token in get_tokens_from_corpora(corpus_file):
    pass

if __name__ == "__main__":
    test_mystem_file = "/home/egor/rnc_mystem.txt"
    test_ruscorpora_file = "/home/egor/rnc.txt"
    mystem_gram = get_corpus_gram_tags(test_mystem_file)
    ruscorpora_gram = get_corpus_gram_tags(test_ruscorpora_file)

    #тривиальный препроцессинг
    ruscorpora_gram = set([tag for gram_tag in ruscorpora_gram for tag in gram_tag.split('=')])

    #ruscorpora_gram = set([tag.replace('-','') for tag in ruscorpora_gram])

    intersection = set.intersection(mystem_gram,ruscorpora_gram)

    mystem_ruscorpora = mystem_gram - ruscorpora_gram
    ruscorpora_mystem = ruscorpora_gram - mystem_gram



    print "Кол-во тегов mystem ", len(mystem_gram)
    print "Кол-во тегов НКРЯ",len(ruscorpora_gram)
    print "Кол-во совпавших тегов",len(intersection)
    print "Кол-во тегов которые есть в mystem и нет в НКРЯ", len(mystem_ruscorpora)
    for tag in mystem_ruscorpora:
        print tag
    print "Кол-во тегов которые есть в НКРЯ и нет в mystem", len(ruscorpora_mystem)
    for tag in ruscorpora_mystem:
        print tag