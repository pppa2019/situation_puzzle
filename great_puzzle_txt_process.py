
import json
import re
lines = open('./situation-data/Lateral_Thinking_Puzzles.txt', 'r').readlines()
puzzle_dict = {}

# idea_item = {
#     "puzzle name": {
#         "puzzle": "xxx",
#         "question list": [],
#         "answer list": [],
#         "final answer": "xxx"
#     }
# }
idx = 0
def jump_noise(idx):
    while len(lines[idx])<=2:
        idx += 1
    return idx
    
total_paras = len(lines)
pattern = r"[1-9].[0-9]{1,2}"
while idx < total_paras:
    text = lines[idx]
    if re.match(pattern, text):
        text = re.sub(pattern, '', text)
        text = text.strip()
        if text not in puzzle_dict:
            puzzle_dict[text] = {'puzzle': lines[idx+1]}
            idx += 1
        elif 'question_list' not in puzzle_dict[text]:
            puzzle_dict[text]['question_list'] = []
            puzzle_dict[text]['answer_list'] = []
            idx = jump_noise(idx)
            while "Q:" in lines[idx+1]:
                puzzle_dict[text]["question_list"].append(lines[idx+1].split("Q: ")[-1])
                puzzle_dict[text]['answer_list'].append(lines[idx+2].split("A: ")[-1])
                idx += 2
        elif 'final answer' not in puzzle_dict[text]:
            puzzle_dict[text]['final answer'] = lines[idx+1]
            idx += 1
            
    idx += 1
with open('docx_puzzles.json', 'w') as f:
    json.dump(puzzle_dict, f)
