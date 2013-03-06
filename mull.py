# -*- coding: utf-8 -*-

import os, random, shutil, codecs


def mull(gold, mystem, experiments_path, experiment_name):
    def absent_files(list1, list2, list1_name, list2_name):
        absent = []
        for name in list1:
            if name not in list2:
                print name, 'not in', list2_name
                absent.append(name)
        for name in list2:
            if name not in list1:
                print name, 'not in', list1_name
                absent.append(name)
        return absent

    def generate_numbers(length):
        x = range(0, length)
        num_of_folds = 5
        folds = []
        while num_of_folds > 1:
            fold = []
            num_in_fold = length / 5
            while num_in_fold > 0:
                num_f = random.choice(range(0, len(x)))
                fold.append(x[num_f])
                del x[num_f]
                num_in_fold -= 1
            folds.append(fold)
            num_of_folds -= 1
        # если есть остаток от деления, то все "лишние" файлы уходят в последний fold
        last_fold = x
        folds.append(last_fold)
        return folds

    def balance_sizes(common_part):
        x = range(0, len(common_part))
        gold_size = 0
        for file in common_part:
            size = os.path.getsize(gold + '/' + file)
            gold_size += size
        fold_size = gold_size / 5
        num_of_folds = 5
        folds = []
        while num_of_folds > 1:
            cur_fold_size = 0
            fold = []
            while cur_fold_size < fold_size:
                num_f = random.choice(range(0, len(x)))
                num_in_list = x[num_f]
                filename = common_part[num_in_list]
                size_f = os.path.getsize(gold + '/' + filename)
                cur_fold_size += size_f
                fold.append(x[num_f])
                del x[num_f]
            folds.append(fold)
            num_of_folds -= 1
        last_fold = x
        folds.append(last_fold)
        return folds
            
    namelist_gold = os.listdir(gold)
    namelist_mystem = os.listdir(mystem)

    absent = absent_files(namelist_gold, namelist_mystem, 'Gold', 'Mystem')
    common_part = []
    for name in namelist_gold:
        if name not in absent:
            common_part.append(name)

    #folds = generate_numbers(len(common_part))
    folds = balance_sizes(common_part)

    new_experiment_path = os.path.join(experiments_path, experiment_name )

    if os.path.exists(new_experiment_path) != True:
        os.mkdir(new_experiment_path)
        os.mkdir( os.path.join(new_experiment_path,'folds' ))

    for fold_id in range(0, 5):

        fold_dir = os.path.join( new_experiment_path, 'folds', str(fold_id) )
        if os.path.exists(fold_dir) != True:
            os.mkdir(fold_dir)

        test_file_name = os.path.join( fold_dir, 'test.txt' )
        train_file_name = os.path.join( fold_dir, 'train.txt' )

        list_of_test_files = codecs.open(test_file_name, 'w', 'utf-8')
        list_of_train_files = codecs.open(train_file_name, 'w', 'utf-8')
        for num in folds[fold_id]:
            test_file_name = common_part[num]
            list_of_test_files.write(mystem + '/' + test_file_name + '\r\n')
        for j in range(0, 5):
            if j != fold_id:
                for element in folds[j]:
                    train_file_name = common_part[element]
                    list_of_train_files.write(gold + '/' + train_file_name + '\r\n')
        list_of_test_files.close()
        list_of_train_files.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fold', help="fold directory", required = True)
    parser.add_argument('-g', '--gold', help="gold directory", required = True)
    parser.add_argument('-m', '--mystem', help="mystem directory", required = True)
    parser.add_argument('-e', '--experiment_name', help="mystem directory", required = True)

    args = parser.parse_args()

    mull(experiments_path= args.fold, gold = args.gold, mystem = args.mystem, experiment_name = args.experiment_name)

