from collections import namedtuple
from pytest import approx

from langevals_ragas.lib.common import RagasResult, Money

from qa_eval.steps.retrieval_evaluation_using_context_texts import (
    RagasContextPrecisionEvaluator,
    RagasContextRecallEvaluator,
    get_retrieval_evaluation_dict,
)


context_1_dict = {
    "id": "1",
    "text": "Oxygen turns the sky blue"
}


def test_get_retrieval_evaluation_dict_success(monkeypatch):
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.6,
            details="precision reason",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert approx(eval_result_dict) == {
        "retrieval_recall": 0.9,
        "retrieval_recall_reason": "recall reason",
        "retrieval_recall_cost": 0.0007,
        "retrieval_precision": 0.6,
        "retrieval_precision_reason": "precision reason",
        "retrieval_precision_cost": 0.0003,
        "retrieval_f1": 0.72,
        "retrieval_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_recall_success_precision_error(monkeypatch):
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="precision error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert eval_result_dict == {
        "retrieval_recall": 0.9,
        "retrieval_recall_reason": "recall reason",
        "retrieval_recall_cost": 0.0007,
        "retrieval_precision_error": "precision error"
    }


def test_get_retrieval_evaluation_dict_both_errors(monkeypatch):
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="recall error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="precision error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert eval_result_dict == {
        "retrieval_recall_error": "recall error",
        "retrieval_precision_error": "precision error",
    }
