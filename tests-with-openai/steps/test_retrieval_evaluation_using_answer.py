from collections import namedtuple

from langevals_ragas.lib.common import RagasResult, Money
from pytest import approx

from qa_eval.steps.retrieval_evaluation_using_answer import (
    RagasResponseContextPrecisionEvaluator,
    RagasResponseContextRecallEvaluator,
    get_retrieval_evaluation_dict,
)


def test_get_retrieval_evaluation_dict_using_reference_answer_success(monkeypatch):
    recall_result = RagasResult(
        status="processed",
        score=0.9,
        details="recall reason",
        cost=Money(currency="USD", amount=0.0007)
    )
    precision_result = RagasResult(
        status="processed",
        score=0.6,
        details="precision reason",
        cost=Money(currency="USD", amount=0.0003)
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        'evaluate',
        lambda *_: recall_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        'evaluate',
        lambda *_: precision_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert approx(eval_result_dict) == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_reason": "recall reason",
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision": 0.6,
        "retrieval_answer_precision_reason": "precision reason",
        "retrieval_answer_precision_cost": 0.0003,
        "retrieval_answer_f1": 0.72,
        "retrieval_answer_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_using_reference_answer_recall_success_precision_error(monkeypatch):
    success_result = RagasResult(
        status="processed",
        score=0.9,
        details="recall reason",
        cost=Money(
            currency="USD",
            amount=0.0007,
        )
    )
    error_result = namedtuple(
        "RagasResult",
        ["status", "score", "details", "cost"],
        defaults=[None, None, None, None]
    )(
        status="error",
        details="details",
        cost=Money(
            currency="USD",
            amount=0.0003,
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: success_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_reason": "recall reason",
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision_error": "details"
    }


def test_get_retrieval_evaluation_dict_using_reference_answer_both_errors(monkeypatch):
    error_result = namedtuple(
        "RagasResult",
        ["status", "score", "details", "cost"],
        defaults=[None, None, None, None]
    )(
        status="error",
        details="details",
        cost=Money(
            currency="USD",
            amount=0.0003,
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "details",
        "retrieval_answer_precision_error": "details",
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_success(monkeypatch):
    recall_result = RagasResult(
        status="processed",
        score=0.9,
        details="recall reason",
        cost=Money(currency="USD", amount=0.0007)
    )
    precision_result = RagasResult(
        status="processed",
        score=0.6,
        details="precision reason",
        cost=Money(currency="USD", amount=0.0003)
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        'evaluate',
        lambda *_: recall_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        'evaluate',
        lambda *_: precision_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert approx(eval_result_dict) == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_reason": "recall reason",
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision": 0.6,
        "retrieval_answer_precision_reason": "precision reason",
        "retrieval_answer_precision_cost": 0.0003,
        "retrieval_answer_f1": 0.72,
        "retrieval_answer_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_recall_success_precision_error(monkeypatch):
    success_result = RagasResult(
        status="processed",
        score=0.9,
        details="recall reason",
        cost=Money(
            currency="USD",
            amount=0.0007,
        )
    )
    error_result = namedtuple(
        "RagasResult",
        ["status", "score", "details", "cost"],
        defaults=[None, None, None, None]
    )(
        status="error",
        details="details",
        cost=Money(
            currency="USD",
            amount=0.0003,
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: success_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_reason": "recall reason",
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision_error": "details"
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_both_errors(monkeypatch):
    error_result = namedtuple(
        "RagasResult",
        ["status", "score", "details", "cost"],
        defaults=[None, None, None, None]
    )(
        status="error",
        details="details",
        cost=Money(
            currency="USD",
            amount=0.0003,
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: error_result
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "details",
        "retrieval_answer_precision_error": "details",
    }


def test_get_retrieval_evaluation_dict_using_no_answers():
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_contexts=[{"id": "1", "text": "Oxygen turns the sky blue"}],
    )
    assert eval_result_dict == {}
