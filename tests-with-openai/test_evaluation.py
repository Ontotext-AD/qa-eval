from pathlib import Path

import jsonlines
import yaml
from langevals_ragas.lib.common import RagasResult, Money

from qa_eval import (
    answer_correctness,
    answer_relevance,
    compute_aggregates,
    run_evaluation,
)
from qa_eval.steps import retrieval_evaluation_using_context_texts


def test_run_evaluation_and_compute_aggregates(monkeypatch):
    def get_chat_responses(path: Path) -> dict:
        responses = dict()
        with jsonlines.open(path, "r") as reader:
            for obj in reader:
                responses[obj["question_id"]] = obj
        return responses

    sample_reference_standard = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "reference_standard_corpus_1.yaml").read_text(encoding="utf-8")
    )
    sample_chat_responses_path = Path(__file__).parent / "test_data" / "chat_responses_1.jsonl"
    monkeypatch.setattr(
        answer_relevance.RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="relevance reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        retrieval_evaluation_using_context_texts.RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        retrieval_evaluation_using_context_texts.RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="precision reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        answer_correctness.AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\treason"
    )

    # Run
    evaluation_results = run_evaluation(sample_reference_standard, get_chat_responses(sample_chat_responses_path))
    aggregates = compute_aggregates(evaluation_results)
    expected_evaluation_results = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates


def test_run_evaluation_and_compute_aggregates_no_actual_steps(monkeypatch):
    def get_chat_responses(path: Path) -> dict:
        responses = dict()
        with jsonlines.open(path, "r") as reader:
            for obj in reader:
                responses[obj["question_id"]] = obj
        return responses

    sample_reference_standard = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "reference_standard_corpus_1.yaml").read_text(encoding="utf-8")
    )
    sample_chat_responses_path = Path(__file__).parent / "test_data" / "chat_responses_3.jsonl"

    monkeypatch.setattr(
        answer_relevance.RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        answer_correctness.AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\treason"
    )

    # Run
    evaluation_results = run_evaluation(sample_reference_standard, get_chat_responses(sample_chat_responses_path))
    aggregates = compute_aggregates(evaluation_results)
    expected_evaluation_results = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_3.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_summary_3.yaml").read_text(encoding="utf-8")
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
        (Path(__file__).parent / "test_data" / "reference_standard_corpus_1.yaml").read_text(encoding="utf-8")
    )
    sample_chat_responses_path = Path(__file__).parent / "test_data" / "chat_responses_2.jsonl"

    evaluation_results = run_evaluation(sample_reference_standard, get_chat_responses(sample_chat_responses_path))
    aggregates = compute_aggregates(evaluation_results)
    expected_evaluation_results = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (Path(__file__).parent / "test_data" / "evaluation_summary_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
