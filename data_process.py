import json
import re
from typing import DefaultDict

answer_path = 'situation-data/answers.txt'
question_id_mapper = [r'[1-2].[0-9a-z]{1,3}\.\s\s', r'[1-2].[0-9a-z]{1,3}\.\s\sVariant:\s']
answer_id_mapper = [r'[1-2].[0-9a-z]{1,3}.answer:\s\s', r'[1-2].[0-9a-z]{1,3}\svariant answer:\s\s']
pure_id_pattern = r'[1-2].[0-9]{1,3}'
source_pattern = r'\(.{0,30}\)'
answer_source_pattern = r'\([fF]rom.{0,30}\)'
def dict_template():
    return {
        "senario": [],
        "answer": [],
        "question": "How could this be?"
    }
qa_pair = DefaultDict(dict_template)
with open(answer_path, 'r') as f:
    lines = f.readlines()
    line_id = 0
    lines_count = len(lines)
    text = []
    id = None
    while line_id < lines_count:
        line = lines[line_id].strip()
        full_text = None
        if len(line)>0:
            text.append(line)
                
        else:
            full_text = ' '.join(text)
            for pattern in question_id_mapper:
                map_result = re.match(pattern, full_text)
                if map_result:
                    id = map_result.group()
                    question_mode = True
            for pattern in answer_id_mapper:
                map_result = re.match(pattern, full_text)
                if map_result:
                    id = map_result.group()
                    question_mode = False
            pure_id = re.match(pure_id_pattern, id).group()
            if pure_id=='2.34':
                import ipdb;ipdb.set_trace()
            if question_mode:
                question = full_text.split(id)[-1]
                question = re.sub(source_pattern, '', question)
                text = []
                qa_pair[pure_id]['senario'].append(question)
            elif not question_mode:
                answer = full_text.split(id)[-1]
                answer = re.sub(answer_source_pattern, '', answer)
                text = []
                qa_pair[pure_id]['answer'].append(answer)
                # qa_pair[question] = answer
                # import ipdb;ipdb.set_trace()
            full_text = None
            while(len(lines[line_id+1].strip())==0):
                line_id += 1
        line_id += 1
    with open('puzzles.json', 'w') as f:
        json.dump(qa_pair, f)
