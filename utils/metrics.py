import torch
import sys
import scipy.spatial.distance as dist
sys.path.append('.')
import numpy as np
from amr2brat import convert_sent2EventGraph
def bert_similarity(list1, list2):
	from sklearn.metrics.pairwise import cosine_similarity
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

	#Compute embedding for both lists
	embedding_1= model.encode(list1, convert_to_tensor=True)
	embedding_2 = model.encode(list2, convert_to_tensor=True)
	return  cosine_similarity(embedding_1.cpu(), embedding_2.cpu())


def dat_score(sent_list):
	distances = []
	length = len(sent_list)
	assert length>=2

	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
	sent_embed = model.encode(sent_list, convert_to_tensor=True).cpu()

	for i in range(length):
		for j in range(i+1, length):
			distances.append(dist.cosine(sent_embed[i], sent_embed[j]))
	return np.mean(distances)

def solution_dat(solution, question_list):
	distances = []
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
	sent_embed = model.encode([solution]+question_list, convert_to_tensor=True).cpu()
	for i in range(1, len(question_list)+1):
		distances.append(dist.cosine(sent_embed[0], sent_embed[i]))
	return np.mean(distances)

def question_evaluate(golden_kg, q_text):
	span_dict, relation_dict, event_dict = convert_sent2EventGraph(q_text)
	return


def final_answer_evaluate(golden_kg, solution):
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

if __name__=="__main__":
	print(bert_similarity(['killed[SEP]women'], ['Alice[SEP]murder[SEP]her sister']))
	print(dat_score(['killed[SEP]women', 'Alice[SEP]murder[SEP]her sister']))
	print(dat_score(['killed[SEP]men', 'killed[SEP]women', 'Alice[SEP]murder[SEP]her sister']))
	import ipdb;ipdb.set_trace()