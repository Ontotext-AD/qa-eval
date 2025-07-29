import sys
from pathlib import Path

import pandas
from openai import OpenAI
from tqdm import tqdm


DATA_FILE_PATH = '../data/paws/validation.tsv'
PROMPT_FILE_PATH = 'prompts/template.md'
OUT_FILE_PATH = 'results/knowledge-hub.tsv'
OUT_FIELDS = ['#T', '#P', '#TP', 'LLM reasoning']
LLM_MODEL = 'gpt-4o-mini'
TEMPERATURE = 0.0


def call_llm(client, prompt) -> str:
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip('\n')
    except Exception as e:
        return str(e).replace('\n', '    ')


def evaluate_answers():
    client = OpenAI()
    with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    references = pandas.read_table(DATA_FILE_PATH)
    Path(OUT_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    print(f'Writing results to {OUT_FILE_PATH}')
    with open(OUT_FILE_PATH, 'w', encoding='utf-8') as out_f:
        out_f.write('\t'.join(OUT_FIELDS) + '\n')
        for i, row in tqdm(references.iterrows()):
            prompt = prompt_template.format(
                question=row['Question'],
                reference_answer=row['Reference answer'],
                candidate_answer=row['Actual answer'],
            )
            llm_output = call_llm(client, prompt)
            out_f.write(llm_output + '\n')
            out_f.flush()
            print('.', end='')
            sys.stdout.flush()


if __name__ == '__main__':
    evaluate_answers()
