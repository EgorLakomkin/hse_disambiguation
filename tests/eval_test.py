from morphomon.eval import calculate_precision

__author__ = 'egor'

import settings

print calculate_precision(settings.CORPUS_DATA_ROOT + 'processed_opencorpora.txt', settings.CORPUS_DATA_ROOT + 'processed_opencorpora_test.txt')