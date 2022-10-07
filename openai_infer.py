import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
# task_definition = "I am a chatbot that can answer questions from users."
# example_q = "Q: A man is found dead outside a large building with a hole in him. How could this be?"
# example_a = "A: The man was struck by an object thrown from the roof of the Empire State Building.  Originally I had the object being a penny, but several people suggested that a penny probably wouldn't be enough to penetrate someone's skull.  Something aerodynamic and heavier, like a dart, was suggested, but I don't know how much mass would be required."
# test_q = 'Q: A body is discovered in a park in Chicago in the middle of summer. How could this be?'
with open('prompts.txt', 'r') as f:
  prompt_list = f.readlines()

result_list = []
for prompt in prompt_list:
  prompt = prompt.replace('\t', '\n').strip()
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
  result = response.get('choices')[0]['text']
  print(result)
  result_list.append({'question':prompt.split('Q: ')[-1][:-4], 'result': result})
  # import ipdb;ipdb.set_trace()

with open('output.json', 'w') as f:
  json.dump(result_list, f)