example_data = {
	"puzzle":"A man walks into a bar and asks the bartender for a drink of water. The bartender pulls out a qun, points it at the man and cocks it. The man pauses before saying \"Thank you\"and leaving. What happened?",
	"final_answer":"The man had the hiccups. The bartender realized this and chose instead to cure the hiccups by frightening the man with the gun.",
	"question_list":[
		"Could the bartender hear him?",
		"Did the man ask for water in an offensive way?"
	],
	"answer_list": [
		"Yes",
		"No"
	]
}

def convert_to_question_generation_prefix(item_dict):
	task_description = "I am an intelligent bot that can play situation puzzles with user. A puzzle is given first, and the user begin to ask a \"yes/no\" question to ensure details."
	result_prefix = task_description+'\n\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['puzzle']+'\n'
	if "gen_question_list" in item_dict:
		for question, answer in zip(item_dict['gen_question_list'], item_dict['gen_answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Question: "
	return result_prefix


def convert_to_answer_generation_prefix(item_dict):
	# task_description = "I am an intelligent bot that can play as judge in situation puzzles with user. A puzzle is given first, and the user begin to ask a \"yes/no\" question to ensure details, and I will give \"Yes/No/Irrelevent\" as answer to questions."
	task_description = "I can answer the question with only yes or no or irrelevant with the \"truth\". "
	result_prefix = task_description+'\n\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Solution: "+example_data["final_answer"]
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['puzzle']+'\n'
	if "gen_question_list" in item_dict and "gen_answer_list" in item_dict:
		for question, answer in zip(item_dict['gen_question_list'], item_dict['gen_answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Question: "+item_dict['gen_question_list'][-1]+'\n'
	result_prefix += "Answer: "
	return result_prefix

def convert_to_hint_generation_prefix(item_dict):
	pass

def convert_to_solution_generation_prefix(item_dict):
	# task_description = "I am an intelligent bot that can play situation puzzles with user. A puzzle is given first, and the user begin to ask \"yes/no\" question to ensure details, then I will give the question a\"yes/no/irrelevent\" answer. Finally user try to give solution for the puzzle."
	task_description = "I can generate a logical answer to the question based on the puzzle, the follow up questions and the follow up answers. "
	result_prefix = task_description+'\n\n'+"Puzzle: "+example_data['puzzle']+'\n'
	result_prefix += "Question: "+example_data["question_list"][0]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][0]+'\n'
	result_prefix += "Question: "+example_data["question_list"][1]+'\n'
	result_prefix += "Answer: "+example_data["answer_list"][1]+'\n'
	result_prefix += '\n'
	result_prefix += "Puzzle:"+item_dict['puzzle']+'\n'
	if "gen_question_list" in item_dict and "gen_answer_list" in item_dict:
		for question, answer in zip(item_dict['gen_question_list'], item_dict['gen_answer_list']):
			result_prefix += "Question: "+question+'\n'
			result_prefix += "Answer: "+answer+'\n'
	result_prefix += "Solution: "
	return result_prefix