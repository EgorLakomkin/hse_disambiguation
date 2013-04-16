# -*- coding: utf-8 -*-
import os
import sys
from morphomon.algorithm.hmm_disambig import HMMAlgorithm
from morphomon.eval import M_strict_mathcher, P_no_garbage, calculate_dir_precision
from morphomon.utils import N_rnc_modified_pos, dump_object, load_object


def runner(action=None, fold=None, experiment_name=None,experiment_dir=None, **kwarg):

    """
    Example of runner for training MEMM new pos
    """
    model_filename =  os.path.abspath(os.path.join(experiment_dir,'folds',str(fold),  'model_{0}.dat'.format( fold )))

    if action == "train":
        print "Train experiment {0}".format(experiment_name)
        #обучаем модель для конкретного фолда
        train_file_list = kwarg['train_file_list']
        hmm_algo = HMMAlgorithm( N_filter_func = N_rnc_modified_pos)


        hmm_algo.train_model_from_filelist(corpus_files = train_file_list)
        dump_object(filename =  model_filename, object=  hmm_algo)
        print "MEMM model has been trained and saved to file {0}".format(model_filename)
    elif action == "load_model":
        print "Load model {0}".format(experiment_name)

        model_filename = os.path.abspath(os.path.join(experiment_dir,model_filename))
        if not os.path.exists( model_filename ):
            print >>sys.stderr, "Model has not been trained for experiment {0} for fold {1}".format(experiment_name, fold )
            exit(-1)
        hmm_algo = load_object( model_filename )
        print "Loaded HMM model from file {0}".format( model_filename )
        return hmm_algo
    elif action == "eval":
	return {'M' : M_strict_mathcher,'N' : N_rnc_pos, 'P' : P_no_garbage}
