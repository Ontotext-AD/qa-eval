from langevals_ragas.response_context_recall import (
    RagasResponseContextRecallEntry,
    RagasResponseContextRecallEvaluator,
)
from langevals_ragas.response_context_precision import (
    RagasResponseContextPrecisionEntry,
    RagasResponseContextPrecisionEvaluator,
)


def _evaluate(
    evaluator: RagasResponseContextRecallEvaluator | RagasResponseContextPrecisionEvaluator,
    entry: RagasResponseContextRecallEntry | RagasResponseContextPrecisionEntry,
    metric: str
) -> dict[str, float | str]:
    try:
        result = evaluator.evaluate(entry)
        if result.status == "processed":
            return {
                f"retrieval_answer_{metric}": result.score,
                f"retrieval_answer_{metric}_cost": result.cost.amount,
                f"retrieval_answer_{metric}_reason": result.details
            }
        else:
            return {
                f"retrieval_answer_{metric}_error": result.details
            }
    except Exception as e:
        return {
            f"retrieval_answer_{metric}_error": str(e)
        }


def get_f1_dict(
    input_dict: dict,
) -> dict:
    recall = input_dict.get("retrieval_answer_recall")
    precision = input_dict.get("retrieval_answer_precision")
    if recall is not None and precision is not None:
        if recall == 0.0 and precision == 0.0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)
        recall_cost = input_dict["retrieval_answer_recall_cost"]
        precision_cost = input_dict["retrieval_answer_precision_cost"]
        return {
            "retrieval_answer_f1": f1,
            "retrieval_answer_f1_cost": recall_cost + precision_cost
        }
    return {}


def get_retrieval_evaluation_dict(
    question_text: str,
    actual_contexts: list[dict[str, str]],
    reference_answer: str | None = None,
    actual_answer: str | None = None,
    model_name : str = "openai/gpt-4o-mini",
    max_tokens : int = 65_536
) -> dict:
    if not reference_answer and not actual_answer:
        return {}
    settings_dict = {
        "model": model_name,
        "max_tokens": max_tokens
    }
    entry = RagasResponseContextPrecisionEntry(
        input=question_text,
        expected_output=reference_answer,
        output=actual_answer,
        contexts=[a["text"] for a in actual_contexts]
    )
    result = {}
    evaluator = RagasResponseContextRecallEvaluator(settings=settings_dict)
    result.update(_evaluate(evaluator, entry, "recall"))
    evaluator = RagasResponseContextPrecisionEvaluator(settings=settings_dict)
    result.update(_evaluate(evaluator, entry, "precision"))
    result.update(get_f1_dict(result))
    return result
