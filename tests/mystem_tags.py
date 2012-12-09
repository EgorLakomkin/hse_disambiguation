# -*- coding: utf-8 -*-
from morphomon.utils import get_corpus_gram_tags


if __name__ == "__main__":
    test_mystem_file = "/home/umka/Dropbox/hse_disabmig/data/mystem/txt/fiction_mystem.txt"
    test_ruscorpora_file = "/home/umka/Dropbox/hse_disabmig/data/processed/processed_fiction.txt"
    mystem_gram = get_corpus_gram_tags(test_mystem_file)
    ruscorpora_gram = get_corpus_gram_tags(test_ruscorpora_file)

    #тривиальный препроцессинг
    ruscorpora_gram = set([tag for gram_tag in ruscorpora_gram for tag in gram_tag.split('=')])
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