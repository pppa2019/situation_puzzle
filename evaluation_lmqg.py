import os
os.environ["NUM_WORKERS"] = "1"
os.environ['CUDA_VISIBLE_DEVICES'] = '7'
from typing import DefaultDict
from lmqg.automatic_evaluation_tool.bleu.bleu import Bleu
from lmqg.automatic_evaluation_tool.rouge import Rouge
from lmqg.automatic_evaluation_tool.bertscore import BERTScore
from lmqg.automatic_evaluation_tool.moverscore import MoverScore
import argparse
import json
import csv
from bleurt import score
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--eval_file_path', type=str, default="output/davinci-003-lt-setting/infer_output_s277_GPT-3-davinci-003_t4.json")
args = parser.parse_args()

raw_data = json.load(open(args.eval_file_path))
solution_ref = DefaultDict()
solution_hypo = DefaultDict()
question_ref = DefaultDict()
question_hypo = DefaultDict()
for item in raw_data:
    try:
        solution_ref[f"solution_{len(solution_ref)}"] = [item["final_answer"].encode()]
    except:
        solution_ref[f"solution_{len(solution_ref)}"] = [item["final_answer"][0].encode()]
    solution_hypo[f"solution_{len(solution_hypo)}"] = [item['solution_history'][-1].encode()]
    # import ipdb;ipdb.set_trace()
    if 'gen_question_list' in item:
        for gen_question in item['gen_question_list']:
            # for ref_question in item['question_list']:
            if len(item['question_list'])!=0:
                # question_ref[f"question_{len(question_ref)}"] = [ref_question.encode() for ref_question in item['question_list']]
                question_ref[f"question_{len(question_ref)}"] = [item['question_list'][0].encode()]
                question_hypo[f"question_{len(question_hypo)}"] = [gen_question.encode()]

# import ipdb;ipdb.set_trace()
output_csv_name = args.eval_file_path.replace('.json', '_metric.csv')
f = open(output_csv_name, 'w')
csv_writer = csv.writer(f, delimiter=',')
csv_writer.writerow(["metric", "solution_score", "question_score"])
for scorer, method in [(Bleu(4), ["Bleu-1", "Bleu-2", "Bleu-3", "Bleu-4"])]:
    puzzle_score, puzzle_scores = scorer.compute_score(solution_ref, solution_hypo)
    if len(question_ref.keys())>0:
        question_score, question_scores = scorer.compute_score(question_ref, question_hypo)
    if isinstance(puzzle_score, list):
        if len(question_ref.keys())>0:
            for m, ps, qs in zip(method, puzzle_score, question_score):
                csv_writer.writerow([m, ps, qs])
        else:
            for m, ps in zip(method, puzzle_score):
                csv_writer.writerow([m, ps])
    else:
        if len(question_ref.keys())>0:
            csv_writer.writerow([method, puzzle_score, question_score])
        else:
            csv_writer.writerow([method, puzzle_score])
    if len(question_ref.keys())>0:
        print(f"{method}  puzzle:{puzzle_score} question:{question_score}")
    else:
        print(f"{method}  puzzle:{puzzle_score}")

scorer = score.BleurtScorer()
bleurt_solution_score = scorer.score(
    references=[sent[0] for sent in solution_ref.values()], 
    candidates=[sent[0] for sent in solution_hypo.values()]
    )

bleurt_question_score = scorer.score(
    references=[sent[0] for sent in question_ref.values()], 
    candidates=[sent[0] for sent in question_hypo.values()]
    )

csv_writer.writerow(['BLEURT', np.mean(bleurt_solution_score), np.mean(bleurt_question_score)])