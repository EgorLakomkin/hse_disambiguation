# -*- coding: utf-8 -*-
import os
import sys
from morphomon.algorithm.mmem_disambig import MMEMAlgorithm
from morphomon.eval import M_strict_mathcher, P_no_garbage, calculate_dir_precision
from morphomon.utils import N_rnc_modified_positional_microsubset, N_rnc_pos


def runner( **kwarg):
    """
    Example of runner for training MEMM new pos
    """
    action = kwarg['action']
    experiment_dir = kwarg['experiment_dir']
    fold = kwarg['fold']
    experiment_name = kwarg['experiment_name']
    model_filename =  os.path.abspath(os.path.join(experiment_dir,'folds',str(fold),  'model_{0}.dat'.format( fold )))

    if action == "train":
        print "Train experiment {0}".format(experiment_name)
        #обучаем модель для конкретного фолда
        train_file_list = kwarg['train_file_list']
        memm_algo = MMEMAlgorithm( N_filter_func = N_rnc_modified_positional_microsubset)
        ambiguity_dir = None
        if 'ambiguity_dir' in kwarg:
            ambiguity_dir = kwarg['ambiguity_dir']


        memm_algo.train_model_file_list(corpus_filelist = train_file_list, ambiguity_dir=ambiguity_dir)
        memm_algo.save_model( model_filename )
        print "MEMM model has been trained and saved to file {0}".format(model_filename)
    elif action == "load_model":
        print "Load model {0}".format(experiment_name)

        model_filename = os.path.abspath(os.path.join(experiment_dir,model_filename))
        if not os.path.exists( model_filename ):
            print >>sys.stderr, "Model has not been trained for experiment {0} for fold {1}".format(experiment_name, fold )
            exit(-1)
        memm_algo = MMEMAlgorithm( N_filter_func = N_rnc_modified_positional_microsubset)
        memm_algo.load_model( model_filename )
        print "Loaded MEMM model from file {0}".format( model_filename )
        return memm_algo
    elif action == "eval":
        print "Eval model results for experiment {0} fold {1}".format( experiment_name, fold )
        gold_dir = kwarg['gold']
        fold_dir = os.path.join(experiment_dir, 'folds', fold )

        errors_filename =  os.path.join( fold_dir, 'errors.txt' )
        ambiguity_dir = kwarg['ambiguity_dir']
        algo_dir = os.path.join( fold_dir, 'test_result' )

        return calculate_dir_precision( algo_dir = algo_dir, gold_dir = gold_dir,ambi_dir=ambiguity_dir, M=M_strict_mathcher,
        N=N_rnc_modified_positional_microsubset, P = P_no_garbage, errors_context_filename=errors_filename)