import csv
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm


IN_FILE_PATH = '../data/data-1.tsv'
PROMPT_FILE_PATH = 'prompts/template.md'
OUT_FILE_PATH = 'results/data-1.tsv'
OUT_FIELDS = ['#Reference', '#Target', '#Matching', 'Reasoning', 'Error']
LLM_MODEL = 'gpt-4o-mini'
TEMPERATURE = 0.0


def extract_response_values(
    response: str
) -> tuple[int | None, int | None, int | None, str, str]:
    vals = response.split('\t')
    n = len(vals)
    if n < 4:
        msg = f'Expected 4 tab-separated values: {response}'
        return None, None, None, '', msg
    vals = vals[:4]
    try:
        n_ref_claims, n_target_claims, n_matching_claims = map(int, vals[:3])
    except ValueError:
        msg = f'Non-int value: {response}'
        return None, None, None, vals[3], msg
    if any([n_ref_claims < 1, n_target_claims < 1, n_matching_claims < 1, n_matching_claims > n_ref_claims, n_matching_claims > n_target_claims]):
        msg = f'Invalid int values: {n_ref_claims}\t{n_target_claims}\t{n_matching_claims}'
        return None, None, None, vals[3], msg
    return n_ref_claims, n_target_claims, n_matching_claims, vals[3], ''


class OpenAIAnswerEvaluator:
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
    in_file_path: str | Path,
    out_file_path: str | Path,
) -> None:
    evaluator = OpenAIAnswerEvaluator(PROMPT_FILE_PATH)
    with open(in_file_path, encoding='utf-8') as f:
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


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', type=str, default=IN_FILE_PATH)
    parser.add_argument('-o', '--out-file', type=str, default=OUT_FILE_PATH)
    args = parser.parse_args()
    evaluate_and_write(
        in_file_path=args.in_file,
        out_file_path=args.out_file,
    )
