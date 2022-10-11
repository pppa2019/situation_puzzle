import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--sample_num", type=int, default=3)
with open('puzzles.json', 'r') as f:
    dataset = json.load(f)
task_definition = "I am a chatbot that can answer questions from users."
text_pair_list = []
for item_dict in dataset.values():
    for senario, answer in zip(item_dict['senario'], item_dict['answer']):
        # if text_pair_list.__len__()==0:
        #     text = 'Q: '+senario+' '+item_dict['question']+'\t'+'A: '+answer
        # else:
        text = 'Q: '+senario+' '+item_dict['question']+'\t'+'A: '
        text_pair_list.append(text)

with open('prompts.txt', 'w') as f:
    example = "Q: A man is found dead outside a large building with a hole in him. How could this be?"+'\t'+"A: The man was struck by an object thrown from the roof of the Empire State Building.  Originally I had the object being a penny, but several people suggested that a penny probably wouldn't be enough to penetrate someone's skull.  Something aerodynamic and heavier, like a dart, was suggested, but I don't know how much mass would be required."
    for prompt in text_pair_list[:20]:
        f.write(task_definition+'\t\t'+example+'\t'+prompt+'\n')