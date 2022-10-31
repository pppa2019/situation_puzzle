from unittest import result
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
from time import sleep

def get_response_from_GPT3(prompt):
    result = ""
    count = 0
    print(prompt)
    while result=="" and count <1:
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
        print(response.get('choices')[0]['text'].strip().split("\n"))
        result = response.get('choices')[0]['text'].strip().split("\n")[0]
        count += 1
        sleep(5)
        # if result == "":
        #     print('Connetion failed! Sleep for 15 sec...')
        #     sleep(15)
    return result


def get_response_from_t5(prompt):
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    tokenizer = T5Tokenizer.from_pretrained("/data/chenyijie/pretrained/t5-small")
    model = T5ForConditionalGeneration.from_pretrained("/data/chenyijie/pretrained/t5-small")  
    # inference
    input_ids = tokenizer(
        prompt, return_tensors="pt"
    ).input_ids  # Batch size 1
    outputs = model.generate(input_ids, top_p=0.7)
    decoded_ouputs = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(decoded_ouputs)
    return decoded_ouputs.split("\n")[0]

def get_response_from_Blender(prompt):
    from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
    mname = "facebook/blenderbot-3B"
    model = BlenderbotForConditionalGeneration.from_pretrained(mname)
    tokenizer = BlenderbotTokenizer.from_pretrained(mname)
    model.save_pretrained('/data/chenyijie/pretrained/blenderbot-3B')
    tokenizer.save_pretrained('/data/chenyijie/pretrained/blenderbot-3B')
    prompt = prompt.replace('\n', '</s>')
    inputs = tokenizer([prompt], return_tensors="pt")
    try:
        reply_ids = model.generate(**inputs)
    except:
        import ipdb;ipdb.set_trace()
    print(tokenizer.batch_decode(reply_ids))
    import ipdb;ipdb.set_trace()

def get_response_from_electra(prompt):
    from transformers import pipeline

    fill_mask = pipeline(
        "fill-mask",
        model="google/electra-large-generator",
        tokenizer="google/electra-large-generator"
    )

    
    outputs = fill_mask(f"HuggingFace is creating a {fill_mask.tokenizer.mask_token} that the community uses to solve NLP tasks.")
    return outputs[0]['sequence']
    # import ipdb;ipdb.set_trace()
