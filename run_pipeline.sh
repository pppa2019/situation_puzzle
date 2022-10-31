export OPENAI_API_KEY=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
model=$1
python main.py\
    --sample_num 3\
    --max_turn 1\
    --model $model