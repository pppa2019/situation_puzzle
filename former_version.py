import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

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