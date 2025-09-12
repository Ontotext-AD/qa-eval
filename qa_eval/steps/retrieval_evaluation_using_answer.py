from langevals_ragas.response_context_recall import (
    RagasResponseContextRecallEntry,
    RagasResponseContextRecallEvaluator,
)
from langevals_ragas.response_context_precision import (
    RagasResponseContextPrecisionEvaluator,
    RagasResponseContextPrecisionEntry
)


def _construct_result_dict(
    langevals_result_dict: dict,
    answer_type: str,
    metric: str
) -> dict:
    if langevals_result_dict["status"] == "processed":
        return {
            f"retrieval_{answer_type}_{metric}": langevals_result_dict["score"],
            f"retrieval_{answer_type}_{metric}_cost": langevals_result_dict["cost"]["amount"]
        }
    else:
        return {
            f"retrieval_{answer_type}_{metric}_error": langevals_result_dict["details"]
        }


def get_f1_dict(
    input_dict: dict,
    answer_type: str
) -> dict:
    recall = input_dict.get(f"retrieval_{answer_type}_recall")
    precision = input_dict.get(f"retrieval_{answer_type}_precision")
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
        recall_cost = input_dict[f"retrieval_{answer_type}_recall_cost"]
        precision_cost = input_dict[f"retrieval_{answer_type}_precision_cost"]
        return {
            f"retrieval_{answer_type}_f1": f1,
            f"retrieval_{answer_type}_f1_cost": recall_cost + precision_cost
        }
    return {}


def get_retrieval_evaluation_dict(
    question_text: str,
    actual_contexts: list[str],
    reference_answer: str | None = None,
    actual_answer: str | None = None,
    model_name : str = "openai/gpt-4o-mini",
    max_tokens : int = 65_536
) -> dict:
    if reference_answer:
        answer_type = "reference_answer"
    elif actual_answer:
        answer_type = "actual_answer"
    else:
        return {}
    settings_dict = {
        "model": model_name,
        "max_tokens": max_tokens
    }
    entry = RagasResponseContextPrecisionEntry(
        input=question_text,
        expected_output=reference_answer,
        output=actual_answer,
        contexts=actual_contexts
    )
    result = {}
    evaluator = RagasResponseContextRecallEvaluator(settings=settings_dict)
    _result = evaluator.evaluate(entry)["response_context_recall"][0]
    result.update(_construct_result_dict(_result, answer_type, "recall"))
    evaluator = RagasResponseContextPrecisionEvaluator(settings=settings_dict)
    _result = evaluator.evaluate(entry)["response_context_precision"][0]
    result.update(_construct_result_dict(_result, answer_type, "precision"))
    result.update(get_f1_dict(result, answer_type))
    return result
