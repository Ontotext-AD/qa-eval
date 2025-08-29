import builtins
import io
from pathlib import Path

from qa_eval import answer_evaluation
from qa_eval.answer_evaluation import extract_response_values


def test_extract_response_values_expected_case():
    response = '2\t3\t1\tsome reasoning'
    result = extract_response_values(response)
    assert result == ('2', '3', '1', 'some reasoning', '')


def test_extract_response_values_five_values():
    response = '2\t2\t2\thello\textra'
    result = answer_evaluation.extract_response_values(response)
    # only first 4 should be taken
    assert result == ('2', '2', '2', 'hello', '')


def test_extract_response_values_invalid_values():
    response = '1\t1\t2\tsome reasoning'
    result = extract_response_values(response)
    assert result == ('', '', '', 'some reasoning', 'Invalid int values: 1\t1\t2')


def test_extract_response_values_non_int():
    response = '2\t2\tx\thello'
    result = answer_evaluation.extract_response_values(response)
    # t and p parse as ints, tp fails → error
    assert result == ('', '', '', 'hello', 'Non-int value: 2\t2\tx\thello')


def test_extract_response_values_too_few_values():
    response = '2\t2\thello'
    result = answer_evaluation.extract_response_values(response)
    # fewer than 4 values → error
    assert result == ('', '', '', '', 'Expected 4 tab-separated values: 2\t2\thello')


def test_evaluate_answers(monkeypatch, tmp_path):
    mock_prompt_content = 'Prompt with {question} {reference_answer} {candidate_answer}'
    mock_input_content = 'Question\tReference answer\tActual answer\nQ1\tRef\tAns\n'

    # Redirect OUT_FILE_PATH to a temporary file
    out_file_name = tmp_path / Path(answer_evaluation.OUT_FILE_PATH).name
    monkeypatch.setattr(answer_evaluation, 'OUT_FILE_PATH', str(out_file_name))

    real_open = builtins.open

    def mock_open(path, *args, **kwargs):
        if path == answer_evaluation.PROMPT_FILE_PATH:
            return io.StringIO(mock_prompt_content)
        elif path == answer_evaluation.DATA_FILE_PATH:
            return io.StringIO(mock_input_content)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', mock_open)

    # Mock call_llm and tqdm
    monkeypatch.setattr(answer_evaluation, 'call_llm', lambda *_: '2\t2\t2\thello')
    monkeypatch.setattr(answer_evaluation, 'tqdm', lambda x: x)

    # Run
    answer_evaluation.evaluate_answers()

    # Verify output file content
    written = out_file_name.read_text().splitlines()
    assert written[0].split('\t') == answer_evaluation.OUT_FIELDS
    assert written[1].split('\t') == ['2', '2', '2', 'hello', '']
