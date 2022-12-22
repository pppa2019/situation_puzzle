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
	}
	get_response = model_func_dict[args.model]
	dataset = load_data("situation-data/lateral_data.json")
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
	with_hint = args.with_hint
	if args.model=="GPT-3" or args.model=='GPT-3-davinci-003' and not args.without_QA:
		if reload_filename == '':
			request_logs = []
		else:
			request_logs = json.load(open("output/"+reload_filename.replace('infer_output', 'infer_log'), 'r'))
		for index, item in zip(range(begin_len, begin_len+args.sample_num), dataset[begin_len:begin_len+args.sample_num]):
			turn_count = 0
			log_item = {
				'gen_answer_list': [],
				'gen_answer_logs':[],
			}
			if len(item['question_list'])==0:
				continue
			else:
				for i in range(len(item['question_list'])):
					question_list = item['question_list'][:i+1]
					answer_list = item['answer_list'][:i]
					answer_prefix = convert_to_answer_prefix(item, question_list, answer_list)
					print(answer_prefix)
					if args.KGQA:
						# import ipdb;ipdb.set_trace()
						path_template = 'situation-data/KG_annotation/{}.ann'
						answer = get_response_from_KG(
							path_template.format(f'{index+1}.puzzle'),
							path_template.format(f'{index+1}.truth'),
							item["question_list"][i]
						)
					answer, log = get_response(answer_prefix)
					if 'golden_q_answer_list' not in item:
						item['golden_q_answer_list'] = [answer]
					else:
						item['golden_q_answer_list' ].append(answer)
					if not args.KGQA:
						request_logs.append(log)
		with open(f'output/infer_output_s{args.sample_num+begin_len}_{args.model}_t{args.max_turn}.json', 'w') as f:
			json.dump(request_logs, f)
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