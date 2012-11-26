from morphomon.preprocessing.syntagrus import process_syntagrus_file

import settings

process_syntagrus_file( settings.CORPUS_DATA_ROOT + 'Anketa.tgt', settings.CORPUS_DATA_ROOT + 'processed_anketa.txt' )