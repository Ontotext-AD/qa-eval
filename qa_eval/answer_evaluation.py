import csv
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm


DATA_FILE_PATH = '../data/knowledge-hub/data.tsv'
PROMPT_FILE_PATH = 'prompts/template.md'
OUT_FILE_PATH = 'results/knowledge-hub.tsv'
OUT_FIELDS = ['#T', '#P', '#TP', 'Reasoning', 'Error']
LLM_MODEL = 'gpt-4o-mini'
TEMPERATURE = 0.0


def call_llm(openai_client: OpenAI, prompt: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip('\n')
    except Exception as e:
        return str(e).replace('\n', '    ')


def extract_response_values(response: str) -> tuple[str, str, str, str, str]:
    vals = response.split('\t')
    n = len(vals)
    if n < 4:
        msg = f'Expected 4 tab-separated values: {response}'
        return '', '', '', '', msg
    vals = vals[:4]
    try:
        t, p, tp = map(int, vals[:3])
    except ValueError:
        msg = f'Non-int value: {response}'
        return '', '', '', vals[3], msg
    if any([t < 1, p < 1, tp < 1, tp > t, tp > p]):
        msg = f'Invalid int values: {t}\t{p}\t{tp}'
        return '', '', '', vals[3], msg
    return vals[0], vals[1], vals[2], vals[3], ''


def evaluate_answers(
    prompt_file_path: str | Path,
    data_file_path: str | Path,
    out_file_path: str | Path,
) -> None:
    openai_client = OpenAI()
    with open(prompt_file_path, encoding='utf-8') as f:
        prompt_template = f.read()
    with open(data_file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    print(f'Writing results to {out_file_path}')
    Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file_path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(OUT_FIELDS) + '\n')
        for row in tqdm(rows):
            prompt = prompt_template.format(
                question=row['Question'],
                reference_answer=row['Reference answer'],
                candidate_answer=row['Actual answer'],
            )
            response_str = call_llm(openai_client, prompt)
            vals = extract_response_values(response_str)
            f.write('\t'.join(vals) + '\n')
            f.flush()


def main():
    evaluate_answers(PROMPT_FILE_PATH, DATA_FILE_PATH, OUT_FILE_PATH)


if __name__ == '__main__':
    main()
