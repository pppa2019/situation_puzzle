export OPENAI_API_KEY=[API_KEY]
python main.py\
    --sample_num $1\
    --max_turn 4\
    --with_hint\
    --golden_QA\
    --model GPT-3-davinci-003