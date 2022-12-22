export CUDA_VISIBLE_DEVICES=4
paths=(
    # 'output/golden_davinci-003/GQA_davinci-003_full-dataset.json'
    # 'output/davinci-003-KG/infer_output_s277_GPT-3-davinci-003_t4.json'
    # 'output/davinci-003-KG-shuffle/infer_output_s277_GPT-3-davinci-003_t4.json'
    # 'output/davinci-003-shuffle-lt-setting/infer_output_s277_GPT-3-davinci-003_t4.json'
    # 'output/No_QA_003/infer_output_noQA_s277_GPT-3-davinci-003_t4.json'
    'output/davinci-003-lt-setting/infer_output_s277_GPT-3-davinci-003_t4.json'
)

# TODO: Golden那份结果不能用来直接比较，应当统一成一样的example才可以。

# file_path=output/davinci-003-shuffle-lt-setting/infer_output_s277_GPT-3-davinci-003_t4.json
for file_path in ${paths[@]}
do
    echo $file_path
    # python evaluation_kg.py  --eval_file_path $file_path --is_golden --use_amr_kg
    # python evaluation_kg.py  --eval_file_path $file_path --is_golden
    # python evaluation_kg.py  --eval_file_path $file_path --use_amr_kg
    # python evaluation_kg.py  --eval_file_path $file_path
    python evaluation_lmqg.py --eval_file_path $file_path
    python evaluate_graph_score.py --eval_file_path $file_path
done
