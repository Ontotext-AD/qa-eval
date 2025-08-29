import builtins
import io
from pathlib import Path

from qa_eval import answer_evaluation


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
