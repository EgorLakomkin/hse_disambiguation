# -*- coding: utf-8 -*-
import os
import sys
from morphomon.algorithm.mmem_disambig import MMEMAlgorithm, default_compute_features
from morphomon.utils import dump_object, N_rnc_pos, load_object, remove_directory_content, remove_ambiguity_file_list, N_rnc_modified_pos
from morphomon.eval import M_strict_mathcher, P_no_garbage, calculate_dir_precision
from morphomon.utils import *

PREPS = ['за','путём','вво','позади','со','близ','от','после','включая','ввиду','помимо','из-за','против','до','наперекор','для','насчёт',
         'перд','ко','кончая','вслед','возле','вне','вопреки','перед','передо','над','посреди','наподобие','а-ля','внутри','благодаря','кроме',
         'изо','вследствие','без','через','вдоль','спустя','безо','среди','вместо','прежде','по','при','о','у','вблизи','обо','к','подобно',
         'во','про','вроде','из','касательно','меж','проо','ради','на','из-под','под','относительно','сверху','мимо','посредством','согласно',
         'вокруг','между','ото','накануне','сквозь','в','об','около','сверх','с','минус','средь']



def compute_features(sentence , i, prev_label, analysises, labels):
	
	default_features = default_compute_features(sentence, i, prev_label, analysises, labels)
	if analysises is not None:
            for analysis in analysises:
                yield "has_analysis={0}".format( analysis )

        if len(sentence[i]) <= 3:
            yield "is={0}".format(sentence[i].encode('utf-8'))

        n = len( sentence )
        for k in xrange(max(0, i - 2), min(n, i + 3)):
            if sentence[k].encode('utf-8') in PREPS:
                yield "has preposition {0} at {1}".format(sentence[k].encode('utf-8'), k)


        #совпадение по числу.падежу, роду
        if labels:
            for k in xrange( max(0, i -2 ), i ):
		if get_gender( labels[k] ) == get_gender( labels[i] ) and get_gender( labels[i] ):
                    yield "has same gender at pos {0}".format( k - i)
                if get_case( labels[k] ) == get_case( labels[i] ) and get_case( labels[i] ):
                    yield "has same case at pos {0}".format( k - i)
                if get_number( labels[k] ) == get_number( labels[i] ) and get_number( labels[i] ):
                    yield "has same number at pos {0}".format( k - i)


def runner(action=None, fold=None, experiment_name=None,experiment_dir=None, **kwarg):

    """
    Example of runner for training MEMM new pos
    """
    model_filename =  os.path.abspath(os.path.join(experiment_dir,'folds',str(fold),  'model_{0}.dat'.format( fold )))

    if action == "train":
        print "Train experiment {0}".format(experiment_name)
        #обучаем модель для конкретного фолда
        train_file_list = kwarg['train_file_list']
        memm_algo = MMEMAlgorithm(compute_features=compute_features, N_filter_func = N_rnc_modified_pos)
        ambiguity_dir = None
        if 'ambiguity_dir' in kwarg:
            ambiguity_dir = kwarg['ambiguity_dir']


        memm_algo.train_model_file_list(corpus_filelist = train_file_list, ambiguity_dir=ambiguity_dir)
        memm_algo.save_model( model_filename )
        print "MEMM model has been trained and saved to file {0}".format(model_filename)
    if action == "load_model":
        print "Load model {0}".format(experiment_name)

        model_filename = os.path.abspath(os.path.join(experiment_dir,model_filename))
        if not os.path.exists( model_filename ):
            print >>sys.stderr, "Model has not been trained for experiment {0} for fold {1}".format(experiment_name, fold )
            exit(-1)
        memm_algo = MMEMAlgorithm( N_filter_func = N_rnc_modified_pos)
        memm_algo.load_model( model_filename )
        print "Loaded MEMM model from file {0}".format( model_filename )
        return memm_algo
    elif action == "eval":
	return {'M' : M_strict_mathcher,'N' : N_rnc_pos, 'P' : P_no_garbage}
