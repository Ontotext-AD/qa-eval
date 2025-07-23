import csv
import json
import sys
from io import StringIO
from pathlib import Path

from openai import OpenAI


DATA_FILE_PATH = '../data/knowledge-hub.tsv'
OUT_FILE_PATH = 'results/knowledge-hub.tsv'
PROMPT_FILE_PATH = 'prompts/template.md'
#OUT_FIELDS = ['#T', '#P', '#TP', 'LLM reasoning']
OUT_FIELDS = ['Reference claims', 'Actual claims', '#T', '#P', '#TP']
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


def _format_list(vals) -> str:
    out_f = StringIO()
    for i, v in enumerate(vals):
        if i > 0:
            out_f.write('\n')
        cleaned = v.strip().replace('"', '\\"')
        out_f.write(f'{1 + i}: {cleaned}')
    return out_f.getvalue()


def format_table_row(llm_output) -> tuple[str, str, str, str, str]:
    try:
        out_vals = json.loads(llm_output)
    except json.JSONDecodeError as e:
        print(llm_output)
        raise e
    return (
        _format_list(out_vals['v1']),
        _format_list(out_vals['v2']),
        out_vals['v3'],
        out_vals['v4'],
        out_vals['v5']
    )


def evaluate_answers():
    client = OpenAI()
    with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    with open(DATA_FILE_PATH, encoding='utf-8') as in_f:
        reader = csv.DictReader(in_f, delimiter='\t')
        Path(OUT_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        print(f'Writing results to {OUT_FILE_PATH}')
        with open(OUT_FILE_PATH, 'w', encoding='utf-8') as out_f:
            writer = csv.writer(out_f, delimiter='\t')
            writer.writerow(OUT_FIELDS)
            for row in reader:
                prompt = prompt_template.format(
                    question=row['Question'],
                    reference_answer=row['Reference answer'],
                    candidate_answer=row['Actual answer'],
                )
                llm_output = call_llm(client, prompt)
                writer.writerow(format_table_row(llm_output))
                out_f.flush()
                print('.', end='')
                sys.stdout.flush()
        print()


if __name__ == '__main__':
    evaluate_answers()
