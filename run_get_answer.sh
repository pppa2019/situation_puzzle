export OPENAI_API_KEY=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

python golden_Q_test.py\
    --sample_num $1\
    --max_turn 4\
    --with_hint\
    --model GPT-3-davinci-003