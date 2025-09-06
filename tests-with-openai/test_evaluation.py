from pathlib import Path

import jsonlines
import yaml

from qa_eval import (
    answer_evaluation,
    compute_aggregates,
    evaluate_steps,
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
    mock_call_llm = lambda *_: '2\t2\t2\treason'
    
    # Assign mocks
    monkeypatch.setattr(answer_evaluation, 'OpenAI', lambda: None)
    monkeypatch.setattr(answer_evaluation.OpenAIAnswerEvaluator, 'call_llm', mock_call_llm)
    
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


def test_get_steps_matches():
    expected_calls = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_calls = [
        {"name": "step_a", "output": "result_a_1", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_b", "error": "error", "status": "error", "id": "3"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "4"},
        {"name": "step_b", "error": "error", "status": "error", "id": "5"},
    ]
    assert evaluate_steps(expected_calls, actual_calls) == 0
    assert "matches" not in expected_calls[-1][0]

    expected_calls = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_calls = [
        {"name": "step_a", "output": "result_a_1", "status": "success", "id": "1"},
        {"name": "step_b", "output": "result_b_2", "status": "success", "id": "2"},
        {"name": "step_b", "error": "error", "status": "error", "id": "3"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "4"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "5"},
    ]
    assert evaluate_steps(expected_calls, actual_calls) == 1
    assert expected_calls[-1][0]["matches"] == "2"

    expected_calls = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_1", "status": "success"},
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_calls = [
        {"name": "step_b", "output": "result_b_2", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "3"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "4"},
    ]
    assert evaluate_steps(expected_calls, actual_calls) == 1
    assert expected_calls[-1][0]["matches"] == "4"
    assert expected_calls[-1][1]["matches"] == "1"

    expected_calls = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_1", "status": "success"},
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_calls = [
        {"name": "step_b", "output": "result_b_24", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "3"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "4"},
    ]
    assert evaluate_steps(expected_calls, actual_calls) == 0.5
    assert expected_calls[-1][0]["matches"] == "4"
    assert "matches" not in expected_calls[-1][1]


def test_evaluate_steps_expected_select_actual_ask():
    expected_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "expected_steps_1.yaml").read_text(encoding="utf-8")
    )
    actual_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "actual_steps_1.yaml").read_text(encoding="utf-8")
    )
    assert evaluate_steps(expected_calls, actual_calls) == 0
    assert "matches" not in expected_calls[-1][0]

    expected_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "expected_steps_2.yaml").read_text(encoding="utf-8")
    )
    actual_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "actual_steps_2.yaml").read_text(encoding="utf-8")
    )
    assert evaluate_steps(expected_calls, actual_calls) == 0
    assert "matches" not in expected_calls[-1][0]


def test_evaluate_steps_expected_select_actual_describe():
    expected_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "expected_steps_3.yaml").read_text(encoding="utf-8")
    )
    actual_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "actual_steps_3.yaml").read_text(encoding="utf-8")
    )
    assert evaluate_steps(expected_calls, actual_calls) == 0
    assert "matches" not in expected_calls[-1][0]


def test_evaluate_steps_expected_select_actual_ask_and_then_select():
    expected_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "expected_steps_4.yaml").read_text(encoding="utf-8")
    )
    actual_calls = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "actual_steps_4.yaml").read_text(encoding="utf-8")
    )
    assert evaluate_steps(expected_calls, actual_calls) == 1
    assert "matches" in expected_calls[-1][0]
    assert expected_calls[-1][0]["matches"] == "call_3qJK186HZj1twnr6x976slHN"
