from pathlib import Path

import jsonlines
import yaml

from qa_eval import (
    answer_evaluation,
    compute_aggregates,
    run_evaluation,
)


def test_run_evaluation_and_compute_aggregates(monkeypatch, tmp_path):
    def get_chat_responses(path: Path) -> dict:
        responses = dict()
        with jsonlines.open(path, "r") as reader:
            for obj in reader:
                responses[obj["question_id"]] = obj
        return responses

    sample_reference_standard = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_reference_standard_corpus_1.yaml").read_text(encoding="utf-8")
    )
    sample_chat_responses_path = Path(__file__).parent.parent / "tests" / "test_data" / "sample_chat_responses_1.jsonl"

    # Define mock call_llm()
    mock_call_llm = lambda *_: "2\t2\t2\treason"
    
    # Assign mocks
    monkeypatch.setattr(answer_evaluation, "OpenAI", lambda: None)
    monkeypatch.setattr(answer_evaluation.OpenAIAnswerEvaluator, "call_llm", mock_call_llm)
    
    # Run
    evaluation_results = run_evaluation(sample_reference_standard, get_chat_responses(sample_chat_responses_path))
    aggregates = compute_aggregates(evaluation_results)
    expected_evaluation_results = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_evaluation_per_question_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates


def test_run_evaluation_and_compute_aggregates_all_errors():
    def get_chat_responses(path: Path) -> dict:
        responses = dict()
        with jsonlines.open(path, "r") as reader:
            for obj in reader:
                responses[obj["question_id"]] = obj
        return responses

    sample_reference_standard = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_reference_standard_corpus_1.yaml").read_text(encoding="utf-8")
    )
    sample_chat_responses_path = Path(__file__).parent / "test_data" / "sample_chat_responses_2.jsonl"

    evaluation_results = run_evaluation(sample_reference_standard, get_chat_responses(sample_chat_responses_path))
    aggregates = compute_aggregates(evaluation_results)
    expected_evaluation_results = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_evaluation_per_question_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "sample_evaluation_summary_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
