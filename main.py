# lateral thinking puzzles
# Date: 2022.10.x
# version: 1
import time
import os
import json
import argparse
from utils.convert_prompt import *
from utils.metrics import *
from models.get_response import *
def load_data(data_path):
	with open(data_path, 'r') as f:
		data = json.load(f)
	return data


if __name__=="__main__":
	parse = argparse.ArgumentParser()
	parse.add_argument('--sample_num', type=int, default=1, help="the sample number to be infer")
	parse.add_argument('--max_turn', type=int, default=5)
	parse.add_argument('--with_hint', action='store_true')
	parse.add_argument('--threshold', type=float, default=0.5)
	parse.add_argument('--model', type=str, default="Electra")


	args = parse.parse_args()

	model_func_dict = {
		"GPT-3": get_response_from_GPT3,
		"T5": get_response_from_t5,
		"Blender": get_response_from_Blender,
		"Electra": get_response_from_electra
	}
	get_response = model_func_dict[args.model]

	dataset = load_data("situation-data/merge_data.json")
	# dataset = list(dataset.values())
	
	for item in dataset[:args.sample_num]:
		turn_count = 0
		while turn_count < args.max_turn:
			question_generation_prompt = convert_to_question_generation_prefix(item)
			generated_question = get_response(question_generation_prompt)
			
			if 'gen_question_list' not in item:
				item["gen_question_list"] = [generated_question]
			else:
				item['gen_question_list'].append(generated_question)
			answer_generation_prompt = convert_to_answer_generation_prefix(item)
			generated_answer = get_response(answer_generation_prompt)
			if 'gen_answer_list' not in item:
				item["gen_answer_list"] = [generated_answer]
			else:
				item["gen_answer_list"].append(generated_answer)
			solution_generation_prompt = convert_to_solution_generation_prefix(item)
			generated_solution = get_response(solution_generation_prompt)
			print(f"turn_{turn_count+1}: ", generated_solution)
			if 'solution_history' not in item:
				item["solution_history"] = [generated_solution]
			else:
				item["solution_history"].append(generated_solution)
			jaccard_score = Jaccard_similarity(generated_solution, item['final_answer'][0])
			if jaccard_score>args.threshold:
				break
			turn_count += 1
	time_stamp = time.strftime("%m-%d_%H:%M:%S")
	with open(f'output/infer_output_{time_stamp}.json', 'w') as f:
		json.dump(dataset[:args.sample_num], f)