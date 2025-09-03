import builtins
import io

from qa_eval import answer_evaluation
from qa_eval.answer_evaluation import extract_response_values


def test_extract_response_values_expected_case():
    response = '2\t3\t1\tsome reason'
    result = extract_response_values(response)
    assert result == (2, 3, 1, 'some reason', '')


def test_extract_response_values_invalid_values():
    response = '0\t1\t1\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 0\t1\t1')

    response = '1\t0\t1\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 1\t0\t1')

    response = '1\t2\t-1\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 1\t2\t-1')

    response = '1\t3\t2\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 1\t3\t2')

    response = '3\t1\t2\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 3\t1\t2')

    response = '3\t1\t2\tsome reason'
    result = extract_response_values(response)
    assert result == (None, None, None, 'some reason', 'Invalid int values: 3\t1\t2')


def test_extract_response_values_non_int():
    response = '2\t2\tx\thello'
    result = answer_evaluation.extract_response_values(response)
    assert result == (None, None, None, 'hello', 'Non-int value: 2\t2\tx\thello')


def test_extract_response_values_too_few_values():
    response = '2\t2\thello'
    result = answer_evaluation.extract_response_values(response)
    # fewer than 4 values → error
    assert result == (None, None, None, '', 'Expected 4 tab-separated values: 2\t2\thello')


def test_extract_response_values_too_many_values():
    response = '2\t2\t2\thello\textra'
    result = answer_evaluation.extract_response_values(response)
    # only first 4 should be taken
    assert result == (2, 2, 2, 'hello', '')


def test_evaluate_answers(monkeypatch, tmp_path):
    mock_prompt_content = 'Prompt with {question} {reference_answer} {candidate_answer}'
    mock_input_content = 'Question\tReference answer\tActual answer\nQ1\tRef\tAns\n'

    prompt_file_path = 'prompt_file_path'
    in_file_path = 'in_file_path'
    out_file_path = tmp_path / 'out_file_name'

    # Mock open()
    real_open = builtins.open

    def mock_open(path, *args, **kwargs):
        if path == prompt_file_path:
            return io.StringIO(mock_prompt_content)
        elif path == in_file_path:
            return io.StringIO(mock_input_content)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', mock_open)

    # Mock OpenAI(), call_llm() and tqdm()
    monkeypatch.setattr(answer_evaluation, 'OpenAI', lambda: None)
    monkeypatch.setattr(answer_evaluation.OpenAIAnswerEvaluator, 'call_llm', lambda *_: '2\t2\t2\thello')
    monkeypatch.setattr(answer_evaluation, 'tqdm', lambda x: x)

    # Run
    answer_evaluation.evaluate_and_write(in_file_path, out_file_path)

    # Verify output file content
    written = out_file_path.read_text().splitlines()
    assert written[0].split('\t') == answer_evaluation.OUT_FIELDS
    assert written[1].split('\t') == ['2', '2', '2', 'hello', '']
