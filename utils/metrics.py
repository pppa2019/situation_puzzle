import torch
import numpy as np
def bleu_score(refs, cand):
    pass

def rouge_score(ref, cand):
    pass

def question_evaluate(refs, cand):
    pass


def question_unsupervise_evaluate(puzzle, cand):
    pass


def final_answer_evaluate(refs, cand):
    pass


def Jaccard_similarity(infer_sent, ref):
	infer_sent_list = infer_sent.split(' ')
	ref_list = ref.split(' ')
	infer_sent_set = set(infer_sent_list)
	ref_set = set(ref_list)
	union_set = infer_sent_set.union(ref_set)
	intersetion_set = infer_sent_set.intersection(ref_set)
	jaccard_score = float(len(intersetion_set)/len(union_set))
	return jaccard_score