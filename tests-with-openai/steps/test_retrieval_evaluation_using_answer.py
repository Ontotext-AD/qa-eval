from pytest import approx

from qa_eval.steps.retrieval_evaluation_using_answer import (
    RagasResponseContextPrecisionEvaluator,
    RagasResponseContextRecallEvaluator,
    get_retrieval_evaluation_dict,
)


def test_get_retrieval_evaluation_dict_using_reference_answer_success(monkeypatch):
    recall_result = {
        "status": "processed",
        "score": 0.9,
        "passed": None,
        "label": None,
        "details": None,
        "cost": {
            "currency": "USD",
            "amount": 0.0007,
        }
    }
    precision_result = {
        "status": "processed",
        "score": 0.6,
        "passed": None,
        "label": None,
        "details": None,
        "cost": {
            "currency": "USD",
            "amount": 0.0003,
        }
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        'evaluate',
        lambda *_: {"response_context_recall": [recall_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        'evaluate',
        lambda *_: {"response_context_precision": [precision_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert approx(eval_result_dict) == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision": 0.6,
        "retrieval_answer_precision_cost": 0.0003,
        "retrieval_answer_f1": 0.72,
        "retrieval_answer_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_using_reference_answer_recall_success_precision_error(monkeypatch):
    success_result = {
        "status": "processed",
        "score": 0.9,
        "passed": None,
        "label": None,
        "details": "details",
        "cost": {
            "currency": "USD",
            "amount": 0.0007,
        }
    }
    error_result = {
        "status": "error",
        "details": "details",
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: {"response_context_recall": [success_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: {"response_context_precision": [error_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision_error": "details"
    }


def test_get_retrieval_evaluation_dict_using_reference_answer_both_errors(monkeypatch):
    error_result = {
        "status": "error",
        "details": "details",
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: {"response_context_recall": [error_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: {"response_context_precision": [error_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "details",
        "retrieval_answer_precision_error": "details",
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_success(monkeypatch):
    recall_result = {
        "status": "processed",
        "score": 0.9,
        "passed": None,
        "label": None,
        "details": None,
        "cost": {
            "currency": "USD",
            "amount": 0.0007,
        }
    }
    precision_result = {
        "status": "processed",
        "score": 0.6,
        "passed": None,
        "label": None,
        "details": None,
        "cost": {
            "currency": "USD",
            "amount": 0.0003,
        }
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        'evaluate',
        lambda *_: {"response_context_recall": [recall_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        'evaluate',
        lambda *_: {"response_context_precision": [precision_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert approx(eval_result_dict) == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision": 0.6,
        "retrieval_answer_precision_cost": 0.0003,
        "retrieval_answer_f1": 0.72,
        "retrieval_answer_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_recall_success_precision_error(monkeypatch):
    success_result = {
        "status": "processed",
        "score": 0.9,
        "passed": None,
        "label": None,
        "details": "details",
        "cost": {
            "currency": "USD",
            "amount": 0.0007,
        }
    }
    error_result = {
        "status": "error",
        "details": "details",
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: {"response_context_recall": [success_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: {"response_context_precision": [error_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_recall_cost": 0.0007,
        "retrieval_answer_precision_error": "details"
    }


def test_get_retrieval_evaluation_dict_using_actual_answer_both_errors(monkeypatch):
    error_result = {
        "status": "error",
        "details": "details",
    }
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: {"response_context_recall": [error_result]}
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: {"response_context_precision": [error_result]}
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_answer="Because of the oxygen in the air",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "details",
        "retrieval_answer_precision_error": "details",
    }


def test_get_retrieval_evaluation_dict_using_no_answers():
    eval_result_dict = get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        actual_contexts=["Oxygen turns the sky blue"],
    )
    assert eval_result_dict == {}
