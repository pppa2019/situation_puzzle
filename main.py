# lateral thinking puzzles
# Date: 2022.10.x
# version: 1
import time
import os
import json
from random import shuffle
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
	parse.add_argument('--example_only_first_turn', action='store_true')
	parse.add_argument('--with_hint', action='store_true')
	parse.add_argument('--threshold', type=float, default=0.5)
	parse.add_argument('--model', type=str, default="Electra")
	parse.add_argument('--without_QA', action='store_true')
	parse.add_argument('--KGQA', action='store_true')
	parse.add_argument('--shuffle', action='store_true')
	parse.add_argument('--golden_QA', action='store_true')


	args = parse.parse_args()

	model_func_dict = {
		"GPT-3-davinci-003": get_response_from_GPT3,
		"t5-small": get_response_from_t5,
		"t5-base": get_response_from_t5,
		"t5-large": get_response_from_t5,
		"Blender": get_response_from_Blender,
		"GPT-2": get_response_from_gpt2_large
	}
	get_response = model_func_dict[args.model]
	dataset = load_data("situation-data/lateral_data.json")
	# check cache and reload
	# import ipdb;ipdb.set_trace()
	output_caches = os.listdir('output')
	reload_filename = ''
	max_sample_num = 0
	for file in output_caches:
		if args.model in file and (file[-5:]=='.json') and ('_infer' not in file) and ("_golden" not in file) and ('log' not in file):
			cache_s_num = int(file.split('_s')[-1].split('_')[0])
			if cache_s_num > max_sample_num:
				reload_filename = file
				max_sample_num = cache_s_num
	if reload_filename != '':
		with open(f'output/{reload_filename}', 'r') as f:
			cache_data = json.load(f)
		begin_len = max_sample_num
		dataset[:begin_len] = cache_data
	else:
		begin_len = 0
	# dataset = list(dataset.values())
	with_hint = args.with_hint
	if args.model=="GPT-3" or args.model=='GPT-3-davinci-003' and not args.without_QA and not args.golden_QA:
		valid_answer = ["Yes", 'No', 'Irrelevant', "Yes.", 'No.', 'Irrelevant.']
		if reload_filename == '':
			request_logs = []
		else:
			request_logs = json.load(open("output/"+reload_filename.replace('infer_output', 'infer_log'), 'r'))
		for index, item in zip(range(begin_len, begin_len+args.sample_num), dataset[begin_len:begin_len+args.sample_num]):
			turn_count = 0
			log_item = {
				'gen_question_list': [],
				'gen_question_logs':[],
				'gen_answer_list': [],
				'gen_answer_logs':[],
				'solution_history': [],
				'solution_his_logs': []
			}
			while turn_count < args.max_turn:
				if 'gen_question_list' in item and len(item['gen_question_list'])>1:
					qa_pairs = [(q, a) for q, a in zip(item['gen_question_list'], item['gen_answer_list'])]
					# import ipdb;ipdb.set_trace()
					shuffle(qa_pairs)
					item['gen_question_list'] = [q for q, a in qa_pairs]
					item['gen_answer_list'] = [a for q, a in qa_pairs]
				question_generation_prompt = convert_to_question_generation_prefix(item)
				generated_question, gen_ques_log = get_response(question_generation_prompt)
				
				if 'gen_question_list' not in item:
					item["gen_question_list"] = [generated_question]
					log_item['gen_question_list'] = [generated_question]
					log_item['gen_question_logs'] = [gen_ques_log]
				else:
					item['gen_question_list'].append(generated_question)
					log_item['gen_question_list'].append(generated_question)
					log_item['gen_question_logs'].append(gen_ques_log)

				answer_generation_prompt = convert_to_answer_generation_prefix(item)
				if not args.KGQA:
					generated_answer, gen_ans_log = get_response(answer_generation_prompt)
					if generated_answer in valid_answer:
						if 'gen_answer_list' not in item:
							item["gen_answer_list"] = [generated_answer]
							log_item['gen_answer_list'] = [generated_answer]
							log_item['gen_answer_logs'] = [gen_ans_log]
						else:
							item["gen_answer_list"].append(generated_answer)
							log_item['gen_answer_list'].append(generated_answer)
							log_item['gen_answer_logs'].append(gen_ans_log)
					else:
						item['gen_question_list'].pop(-1)
						log_item['gen_question_list'].pop(-1)
						log_item['gen_question_logs'].pop(-1)
						continue
				else:
					path_template = 'situation-data/KG_annotation/{}.ann'
					generated_answer = get_response_from_KG(
						path_template.format(f'{index+1}.puzzle'),
						path_template.format(f'{index+1}.truth'),
						item["gen_question_list"][-1]
						)
					if 'gen_answer_list' not in item:
						item["gen_answer_list"] = [generated_answer]
					else:
						item["gen_answer_list"].append(generated_answer)
				
				solution_generation_prompt = convert_to_solution_generation_prefix(item, with_hint)
				generated_solution, gen_solution_log = get_response(solution_generation_prompt)
				print(f"turn_{turn_count+1}: ", generated_solution)
				if 'solution_history' not in item:
					item["solution_history"] = [generated_solution]
					log_item['solution_his_logs'] = [gen_solution_log]
					log_item['solution_history'] = [generated_solution]
				else:
					item["solution_history"].append(generated_solution)
					log_item['solution_history'].append(generated_solution)
					log_item['solution_his_logs'].append(gen_solution_log)
				jaccard_score = Jaccard_similarity(generated_solution, item['final_answer'][0])
				request_logs.append(log_item)
				if jaccard_score>args.threshold:
					break
				turn_count += 1
		with open(f'output/infer_log_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
			json.dump(request_logs, f)
	else:
		if reload_filename == '':
				request_logs = []
		else:
			request_logs = json.load(open("output/"+reload_filename.replace('infer_output', 'infer_log'), 'r'))
		for item in dataset[begin_len:begin_len+args.sample_num]:
			
			if "t5-" in args.model:
				gen_solution = get_response(item['puzzle'], args.model)
			elif 'GPT-3' in args.model and args.without_QA:
				task_description = "I am an intelligent bot that can play lateral thinking puzzles with user. Give me the puzzle and I will try to answer you."
				gen_solution, log = get_response(task_description + "\nQuestion: "+item['puzzle']+"\n Answer: ")
				request_logs.append(log)
			elif 'GPT-3' in args.model and args.golden_QA:
				if len(item['question_list'])>0:
					# import ipdb;ipdb.set_trace()
					prompt = convert_to_solution_generation_prefix(item, with_hint=True, golden_history=True)
					gen_solution, log = get_response(prompt)
					request_logs.append(log)
				else:
					continue
			else:
				gen_solution = get_response("Question: "+item['puzzle']+" Answer: ")
			item["solution_history"] = [gen_solution]
		if 'GPT-3' in args.model and args.without_QA:
			with open(f'output/infer_log_noQA_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
				json.dump(request_logs, f)
		if 'GPT-3' in args.model and args.golden_QA:
			with open(f'output/infer_log_GQA_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
				json.dump(request_logs, f)
	# time_stamp = time.strftime("%m-%d_%H:%M:%S")
	if args.without_QA:
		with open(f'output/infer_output_noQA_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
			json.dump(dataset[:args.sample_num+begin_len], f)
	elif args.golden_QA:
		with open(f'output/infer_output_GQA_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
			json.dump(dataset[:args.sample_num+begin_len], f)
	else:
		with open(f'output/infer_output_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
			json.dump(dataset[:args.sample_num+begin_len], f)