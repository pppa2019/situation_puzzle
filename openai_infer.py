import os
from unittest import result
import openai
import json
import argparse

openai.api_key = os.getenv("OPENAI_API_KEY")
example_data = {
	"puzzle":"A man walks into a bar and asks the bartender for a drink of water. The bartender pulls out a qun, points it at the man and cocks it. The man pauses before saying \"Thank you\"and leaving. What happened?",
	"solution":"The man had the hiccups. The bartender realized this and chose instead to cure the hiccups by frightening the man with the gun.",
	"question_list":[
		"Could the bartender hear him?",
		"Did the man ask for water in an offensive way?"
	],
	"answer_list": [
		"Yes",
		"No"
	]
}

def load_data(data_path):
	with open(data_path, 'r') as f:
		data = json.load(f)
	return data

def convert_to_question_generation_prefix(item_dict):
	task_description = "I am an intelligent bot that can play situation puzzles with user. A puzzle is given first, and the user begin to ask a \"yes/no\" question to ensure details."
	result_prefix = task_description+'\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['senario'][0]+' '+item_dict['question']+'\n'
	if "question_list" in item_dict:
		for question, answer in zip(item['question_list'], item['answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Question: "
	return result_prefix


def convert_to_answer_generation_prefix(item_dict):
	task_description = "I am an intelligent bot that can play as judge in situation puzzles with user. A puzzle is given first, and the user begin to ask a \"yes/no\" question to ensure details, and I will give \"Yes/No/Irrelevent\" as answer to questions."
	result_prefix = task_description+'\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Solution: "+example_data["solution"]
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['senario'][0]+' '+item_dict['question']+'\n'
	if "question_list" in item_dict and "answer_list" in item_dict:
		for question, answer in zip(item['question_list'], item['answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Question: "+item['question_list'][-1]+'\n'
	result_prefix += "Answer: "
	return result_prefix

def convert_to_hint_generation_prefix(item_dict):
	pass

def convert_to_solution_generation_prefix(item_dict):
	task_description = "I am an intelligent bot that can play situation puzzles with user. A puzzle is given first, and the user begin to ask \"yes/no\" question to ensure details, then I will give the question a\"yes/no/irrelevent\" answer. Finally user try to give solution for the puzzle."
	result_prefix = task_description+'\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['senario'][0]+' '+item_dict['question']+'\n'
	if "question_list" in item_dict and "answer_list" in item_dict:
		for question, answer in zip(item['question_list'], item['answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Solution: "
	return result_prefix

def Jaccard_similarity(infer_sent, ref):
	infer_sent_list = infer_sent.split(' ')
	ref_list = ref.split(' ')
	infer_sent_set = set(infer_sent_list)
	ref_set = set(ref_list)
	union_set = infer_sent_set.union(ref_set)
	intersetion_set = infer_sent_set.intersection(ref_set)
	jaccard_score = float(len(intersetion_set)/len(union_set))
	return jaccard_score


def get_response(prompt):
	response = openai.Completion.create(
		model="text-davinci-002",
		prompt=prompt,
		temperature=0.7,
		max_tokens=100,
		top_p=1,
		frequency_penalty=0.0,
		presence_penalty=0.0,
		stop=["\n\n"]
		)
	return response.get('choices')[0]['text'].split("\n")[0]

if __name__=="__main__":
	parse = argparse.ArgumentParser()
	parse.add_argument('--sample_num', type=int, default=1, help="the sample number to be infer")
	parse.add_argument('--max_turn', type=int, default=5)
	parse.add_argument('--with_hint', action='store_true')
	args = parse.parse_args()

	dataset = load_data("situation-data/puzzles.json")
	dataset = list(dataset.values())
	
	for item in dataset[:args.sample_num]:
		turn_count = 0
		while turn_count < args.max_turn:
			question_generation_prompt = convert_to_question_generation_prefix(item)
			# import ipdb;ipdb.set_trace()
			generated_question = get_response(question_generation_prompt)
			
			if 'question_list' not in item:
				item["question_list"] = [generated_question]
			else:
				item['question_list'].append(generated_question)
			answer_generation_prompt = convert_to_answer_generation_prefix(item)
			generated_answer = get_response(answer_generation_prompt)
			if 'answer_list' not in item:
				item["answer_list"] = [generated_answer]
			else:
				item["answer_list"].append(generated_answer)
			solution_generation_prompt = convert_to_solution_generation_prefix(item)
			generated_solution = get_response(solution_generation_prompt)
			print(f"turn_{turn_count+1}: ", generated_solution)
			if 'solution_history' not in item:
				item["solution_history"] = [generated_solution]
			else:
				item["solution_history"].append(generated_solution)
			jaccard_score = Jaccard_similarity(generated_solution, item['answer'][0])
			if jaccard_score>0.5:
				break
			turn_count += 1
	with open('output/infer_output.json', 'w') as f:
		json.dump(dataset[:args.sample_num], f)