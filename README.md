# exploring lateral thinking ability of GPT-3 on situation puzzle

# how to run?
Step 1: prepare data folder 'situation-data', including json dataset and annotated KG files folder.
Step2:
Put your openai API_KEY into run_openai.sh, and confirm your experiment setting in this file, then
```bash
    bash run_pipeline.sh [sample_num]
```
In order to avoid lossing data, you can simply run
```bash
    bash split_run.sh
```
Step 2:
To generate KG, write you setting in run_eval_kg.sh. In addition, evaluation_kg.py is for KG automatically generation; evaluate_lmqg.py is for text-based metrics; evaluation_graph_score.py is for graph-based metrics