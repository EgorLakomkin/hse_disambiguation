# -*- coding: utf-8 -*-
import os
import sys
import traceback
from morphomon.algorithm.mmem_disambig import MMEMAlgorithm
from morphomon.eval import M_strict_mathcher, P_no_garbage, calculate_dir_precision
from morphomon.utils import create_dir, load_object, remove_directory_content, remove_ambiguity_file_list, N_rnc_pos, N_rnc_modified_pos

FOLDS_DIRNAME = 'folds'
TEST_FILENAME = 'test.txt'
RUNPY_FILENAME = 'run'
TEST_DIR = 'test'
TRAIN_DIR = 'train'
TRAIN_FILENAME = 'train.txt'

from maxent import MaxentModel


def bull(action, experiment_name, experiment_path, fold, gold = None, morph_analysis = None):
    experiment_dir = os.path.join( experiment_path, experiment_name  )


    sys.path.append( os.path.abspath(experiment_path) )
    mod_run_py = '.'.join( [experiment_name, RUNPY_FILENAME ] )

    try:
        # Import the module
        mod = __import__(mod_run_py, globals(), locals(), ['*'])
    except ImportError:
        # Log error
        print >>sys.stderr, "Failed to run.py module from experiment {0}. {1}".format(experiment_name,traceback.format_exc())
    print "Loaded run.py for experiment {0}".format( experiment_name )

    params = {
        'action' : action,
        'experiment_dir' : experiment_dir
    }
    if action == 'train':
        fold_dir = os.path.join(experiment_dir, FOLDS_DIRNAME, fold )

        train_files_source_dir = os.path.join(experiment_dir, TRAIN_DIR)
        fold_train_file = os.path.join( fold_dir, TRAIN_FILENAME )
        params['fold'] = fold
        params['train_file_list'] = [os.path.abspath(os.path.join(train_files_source_dir,line.strip())) for line in open(fold_train_file, 'r').readlines()]
        if morph_analysis:
            params['ambiguity_dir'] = morph_analysis
        mod.runner( **params )

    elif action == 'test':
        fold_dir = os.path.join(experiment_dir, FOLDS_DIRNAME, fold )

        test_files_source_dir = os.path.join(experiment_dir, TEST_DIR)
        fold_test_file = os.path.join( fold_dir, TEST_FILENAME )
        test_files= [os.path.abspath(os.path.join(test_files_source_dir,line.strip())) for line in open(fold_test_file, 'r').readlines()]

        result_dir =  os.path.join( fold_dir, 'test_result' )
        create_dir( result_dir )

        model_filename = 'model_{0}.dat'.format( fold )
        model_filename = os.path.abspath(os.path.join(experiment_dir,model_filename))
        if not os.path.exists( model_filename ):
            print >>sys.stderr, "Model has not been trained for experiment {0} for fold {1}".format(experiment_name, fold )

        hmm_algo = MMEMAlgorithm(N_filter_func=N_rnc_modified_pos)
        hmm_algo.load_model( model_filename )
        remove_directory_content( result_dir )
        remove_ambiguity_file_list( ambig_filelist = test_files, output_dir=result_dir, algo=hmm_algo)
        print "Finished removing ambiguity for experiment {0} for fold {1}".format(experiment_name, fold )
    elif action == 'eval':
        #результат работы алгоритма в конкретном фолде
        fold_dir = os.path.join(experiment_dir, FOLDS_DIRNAME, fold )

        errors_filename =  os.path.join( fold_dir, 'errors.txt' )

        algo_dir = os.path.join( fold_dir, 'test_result' )

        test_files_source_dir = os.path.join(experiment_dir, TEST_DIR)

        calculate_dir_precision( algo_dir = algo_dir, gold_dir = gold,ambi_dir=test_files_source_dir, M=M_strict_mathcher,
        N=N_rnc_pos, P = P_no_garbage, errors_context_filename=errors_filename)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', help="test/train/eval")
    parser.add_argument('-e', '--experiment_name', help="Name of the experiment")
    parser.add_argument('-p', '--experiment_path', help="Path to the experiment")
    parser.add_argument('-f', '--fold', help="fold number")
    parser.add_argument('-g', '--gold', help="gold directory")
    parser.add_argument('-m', '--ambiguity_dir', help="morph analysis output directory")


    args = parser.parse_args()

    if not args.action:
        print >>sys.stderr, "You did not specify action you want to make!"
        exit(-1)
    if not args.experiment_name:
        print >>sys.stderr, "You did not specify experiment name"
        exit()
    if not args.experiment_path:
        print >>sys.stderr, "You did not specify experiment path"
        exit()

    if (args.action in ['train','test'])  and not args.fold:
        print >>sys.stderr, "You did not specify fold for {0} action".format( args.action )
        exit()

    if args.action == 'eval' and not args.gold:
        print >>sys.stderr, "You did not specify gold directory"
        exit()

    bull(action=args.action, experiment_name=args.experiment_name,
         experiment_path=args.experiment_path, fold = args.fold, gold = args.gold, morph_analysis = args.ambiguity_dir)

