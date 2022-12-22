from unittest import result
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
from time import sleep

def get_response_from_GPT3(prompt):
    result = ""
    count = 0
    print(prompt)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        logprobs=5,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=None
    )
    print(response.get('choices')[0]['text'].strip().split("\n"))
    result = response.get('choices')[0]['text'].strip().split("\n")[0]
    request_log = response.get('choices')[0]
    count += 1
    # if result == '':
    #     import ipdb;ipdb.set_trace()
    sleep(5)
    # if result == "":
    #     print('Connetion failed! Sleep for 15 sec...')
    #     sleep(15)
    return result, request_log


def get_response_from_KG(puzzle_kg_path, solution_kg_path, question):
    ''' 
        TODO:
        - parse question to event graph
        - fuzzy match to judge if there is event or entity overlap
    '''
    import sys
    sys.path.append('.')
    from utils import load_kg_from_ann
    from amr2brat import convert_sent2EventGraph
    def abstract_entity_event(span_dict):
        entity_list = []
        event_list = []
        for _, value in span_dict.items():
            if value[0]=='Head_End':
                entity_list.append(value[-1])
            elif value[0]=='Event':
                event_list.append(value[-1])
        return entity_list, event_list
    
    def abstract_event_triple(span_dict, event_dict):
        event_triple_list = []
        for value in event_dict.values():
            event_triple_list.append('\t'.join([span_dict[span_id.split(':')[-1]][-1] for span_id in value]))
        return event_triple_list
    
    pz_span_dict, _, pz_event_dict = load_kg_from_ann(puzzle_kg_path)
    sl_span_dict, _, sl_event_dict = load_kg_from_ann(solution_kg_path)
    q_span_dict, _, q_event_dict = convert_sent2EventGraph(question)

    pz_entity, pz_event = abstract_entity_event(pz_span_dict)
    sl_entity, sl_event = abstract_entity_event(sl_span_dict)
    q_entity, q_event = abstract_entity_event(q_span_dict)
    pz_event_triples = abstract_event_triple(pz_span_dict, pz_event_dict)
    sl_event_triples = abstract_event_triple(pz_span_dict, pz_event_dict)
    q_event_triples = abstract_event_triple(q_span_dict, q_event_dict)


    if len(pz_event+sl_event)==0 and len(set(q_entity).intersection(set(pz_entity+sl_entity)))>0:
        return 'Yes'
    
    if len(set(q_entity).intersection(set(pz_entity+sl_entity)))>0:
        if len(set(q_event_triples).intersection(set(pz_event_triples+sl_event_triples)))>0:
            return 'Yes'
        return 'No'
    
    return "Irrelevant"

def get_response_from_t5(prompt, name):
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    tokenizer = T5Tokenizer.from_pretrained(f"/data/chenyijie/pretrained/{name}")
    model = T5ForConditionalGeneration.from_pretrained(f"/data/chenyijie/pretrained/{name}")  
    # inference
    input_ids = tokenizer(
        prompt, return_tensors="pt"
    ).input_ids  # Batch size 1
    outputs = model.generate(input_ids, top_p=0.7, min_length=8, max_length=128)
    decoded_ouputs = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(decoded_ouputs)
    return decoded_ouputs.split("\n")[0]

def get_response_from_Blender(prompt):
    from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
    mname = "/data/chenyijie/pretrained/blenderbot-3B"
    model = BlenderbotForConditionalGeneration.from_pretrained(mname)
    tokenizer = BlenderbotTokenizer.from_pretrained(mname)
    prompt = prompt.replace('\n', '</s>')
    inputs = tokenizer([prompt], return_tensors="pt")
    try:
        reply_ids = model.generate(**inputs)
    except:
        import ipdb;ipdb.set_trace()
    result = tokenizer.batch_decode(reply_ids)[0].replace('<s>', ' ').replace('</s>', ' ').strip()
    print(result)
    return result


def get_response_from_gpt2_large(prompt):
    from transformers import pipeline, set_seed
    generator = pipeline('text-generation', model='gpt2-large')
    set_seed(42)
    result = generator(prompt, max_length=768, num_return_sequences=1)
    print(result[0]['generated_text'].split('Answer: ')[-1].split('\n')[-1])
    return result[0]['generated_text'].split('Answer: ')[-1].split('\n')[-1]


if __name__ == '__main__':
    get_response_from_KG('situation-data/KG_annotation/22.puzzle.ann', 'situation-data/KG_annotation/22.truth.ann', 'Did the man close windows by himself?')
