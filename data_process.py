import json
import re
answer_path = 'situation-data/answers.txt'
question_id_mapper = [r'[1-2].[0-9a-z]{1,3}\.', r'[1-2].[0-9a-z]{1,3}\...Variant:']
answer_id_mapper = [r'[1-2].[0-9a-z]{1,3}.answer:', r'[1-2].[0-9a-z]{1,3}.variant answer:']
source_pattern = r'\(\)'
qa_pair = {}
with open(answer_path, 'r') as f:
    lines = f.readlines()
    line_id = 0
    lines_count = len(lines)
    text = []
    question_mode = True
    while line_id < lines_count:

        line = lines[line_id].strip()
        if len(line)>0:
            text.append(line)
        else:
            if question_mode:
                question = ' '.join(text)
                text = []
                question_mode = False
            elif not question_mode:
                answer = ' '.join(text)
                text = []
                qa_pair[question] = answer
                question_mode = True
                # import ipdb;ipdb.set_trace()
            while(len(lines[line_id+1].strip())==0):
                line_id += 1
        line_id += 1
    with open('puzzles.json', 'w') as f:
        json.dump(qa_pair, f)
    import ipdb;ipdb.set_trace()