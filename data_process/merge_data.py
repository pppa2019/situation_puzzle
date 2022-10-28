import json
data_path1 = "situation-data/puzzles.json"
data_path2 = "docx_puzzles.json"
data1 = json.load(open(data_path1, 'r'))
data2 = json.load(open(data_path2, 'r'))
all_data = []
item_schema = {
    "puzzle": None,
    "question_list": [],
    "answer_list":[],
    "final_answer":None
}
for item in data1.values():
    unified_item = item_schema.copy()
    unified_item["puzzle"] = item["senario"][0].strip() + ' ' + item["question"]
    unified_item["final_answer"] = item["answer"]
    all_data.append(unified_item)
for item in data2.values():
    unified_item = item_schema.copy()
    unified_item["puzzle"] = item["puzzle"]
    unified_item["question_list"] = item["question_list"]
    unified_item["answer_list"] = item["answer_list"]
    unified_item["final_answer"] = item["final answer"]
    all_data.append(unified_item)
with open('situation-data/merge_data.json', 'w') as f:
    json.dump(all_data, f)
