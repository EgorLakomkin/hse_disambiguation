#!/bin/bash

N=5
R=/home/egor.lakomkin/
T=$(date +%Y%m%d_%H%M)

export PYTHONPATH=${R}/hse_disambiguation/

function run() {
  local algo=$1
  local tags=$2

  echo "*** Starting algorithm '$1' on '$2' at $(date)"

  python morphomon/eval.py \
    --num_iters=$N \
    --err ${R}/errors/ \
    --gold_dir=${R}/data/rnc_gold/ \
    --morph_dir=${R}/data/mystem_txt/ \
    --algorithm=$algo \
    --algo_dir=${R}/$algo/ \
    --tag_type=$tags

  echo "*** Finishing algorithm '$1' on '$2' at $(date)"
}

for a in baseline hmm memm ; do
for b in pos base_tags new_pos new_base_tags ; do
  cout=${R}/logs/run_${T}_${a}_${b}.stdout.txt
  cerr=${R}/logs/run_${T}_${a}_${b}.stderr.txt

  ( run $a $b | tee $cout ) 3>&1 1>&2 2>&3 | tee $cerr &
done
wait
done
wait
