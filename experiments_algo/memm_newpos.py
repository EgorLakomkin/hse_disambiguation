# -*- coding: utf-8 -*-
import os
from morphomon.algorithm.mmem_disambig import MMEMAlgorithm
from morphomon.utils import dump_object, N_rnc_pos, load_object, remove_directory_content, remove_ambiguity_file_list, N_rnc_modified_pos


def runner( **kwarg):
    """
    Example of runner for training HMM
    """
    action = kwarg['action']
    experiment_dir = kwarg['experiment_dir']
    fold = kwarg['fold']
    ambiguity_dir = kwarg['ambiguity_dir']
    model_filename = 'model_{0}.dat'.format( fold )

    if action == "train":
        #обучаем модель для конкретного фолда
        train_file_list = kwarg['train_file_list']
        memm_algo = MMEMAlgorithm( N_filter_func = N_rnc_modified_pos)
        memm_algo.train_model_file_list(corpus_filelist = train_file_list, ambiguity_dir=ambiguity_dir)
        model_filename =  os.path.abspath(os.path.join(experiment_dir,model_filename))
        memm_algo.save_model( model_filename )
        print "Memm model has been trained and saved to file {0}".format(model_filename)