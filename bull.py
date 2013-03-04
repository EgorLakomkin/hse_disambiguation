# -*- coding: utf-8 -*-
import os
import sys
import traceback
from morphomon.utils import create_dir

FOLDS_DIRNAME = 'folds'
TEST_FILENAME = 'test.txt'
RUNPY_FILENAME = 'run'
TEST_DIR = 'test'
TRAIN_DIR = 'train'
TRAIN_FILENAME = 'train.txt'

def bull(action, experiment_name, experiment_path, fold):
    experiment_dir = os.path.join( experiment_path, experiment_name  )
    fold_dir = os.path.join(experiment_dir, FOLDS_DIRNAME, fold )


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
        train_files_source_dir = os.path.join(experiment_dir, TRAIN_DIR)
        fold_train_file = os.path.join( fold_dir, TRAIN_FILENAME )
        params['fold'] = fold
        params['train_file_list'] = [os.path.abspath(os.path.join(train_files_source_dir,line.strip())) for line in open(fold_train_file, 'r').readlines()]
    elif action == 'test':
        test_files_source_dir = os.path.join(experiment_dir, TEST_DIR)
        fold_test_file = os.path.join( fold_dir, TEST_FILENAME )
        params['fold'] = fold
        params['test_file_list'] = [os.path.abspath(os.path.join(test_files_source_dir,line.strip())) for line in open(fold_test_file, 'r').readlines()]

        result_dir =  os.path.join( fold_dir, 'test_result' )
        create_dir( result_dir )
        params['result_dir'] =result_dir

    mod.runner( **params )




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', help="test/train/eval")
    parser.add_argument('-e', '--experiment_name', help="Name of the experiment")
    parser.add_argument('-p', '--experiment_path', help="Path to the experiment")
    parser.add_argument('-f', '--fold', help="fold number")

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

    if not args.fold:
        print >>sys.stderr, "You did not specify fold"
        exit()

    bull(action=args.action, experiment_name=args.experiment_name,
         experiment_path=args.experiment_path, fold = args.fold)

