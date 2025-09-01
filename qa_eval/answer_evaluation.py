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



def extract_response_values(response: str) -> tuple[int | None, int | None, int | None, str, str]:
    vals = response.split('\t')
    n = len(vals)
    if n < 4:
        msg = f'Expected 4 tab-separated values: {response}'
        return None, None, None, '', msg
    vals = vals[:4]
    try:
        t, p, tp = map(int, vals[:3])
    except ValueError:
        msg = f'Non-int value: {response}'
        return None, None, None, vals[3], msg
    if any([t < 1, p < 1, tp < 1, tp > t, tp > p]):
        msg = f'Invalid int values: {t}\t{p}\t{tp}'
        return None, None, None, vals[3], msg
    return t, p, tp, vals[3], ''


class AnswerOpenAIEvaluator:
    def __init__(
        self,
        prompt_file_path: str | Path = PROMPT_FILE_PATH,
        temperature : float = TEMPERATURE
    ):
        with open(prompt_file_path, encoding='utf-8') as f:
            self.prompt_template = f.read()
        self.openai_client = OpenAI()
        self.temperature = temperature

    def call_llm(self, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip('\n')
        except Exception as e:
            return str(e).replace('\n', '    ')

    def evaluate_answer(
        self,
        question: str,
        reference_answer: str,
        actual_answer: str
    ):
        prompt = self.prompt_template.format(
            question=question,
            reference_answer=reference_answer,
            candidate_answer=actual_answer,
        )
        response_str = self.call_llm(prompt)
        return extract_response_values(response_str)


def evaluate_and_write(
    prompt_file_path: str | Path,
    data_file_path: str | Path,
    out_file_path: str | Path,
) -> None:
    evaluator = AnswerOpenAIEvaluator(prompt_file_path)
    with open(data_file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = [row for row in reader]
    print(f'Writing results to {out_file_path}')
    Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(OUT_FIELDS)
        for row in tqdm(rows):
            vals = evaluator.evaluate_answer(
                row['Question'],
                row['Reference answer'],
                row['Actual answer']
            )
            writer.writerow(vals)
            f.flush()


if __name__ == '__main__':
    evaluate_and_write(PROMPT_FILE_PATH, DATA_FILE_PATH, OUT_FILE_PATH)
