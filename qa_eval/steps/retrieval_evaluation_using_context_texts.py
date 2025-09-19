from langevals_ragas.context_precision import (
    RagasContextPrecisionEntry,
    RagasContextPrecisionEvaluator,
)
from langevals_ragas.context_recall import (
    RagasContextRecallEntry,
    RagasContextRecallEvaluator,
)


def _evaluate(
    entry: RagasContextRecallEntry | RagasContextPrecisionEntry,
    evauator: RagasContextRecallEvaluator | RagasContextPrecisionEvaluator,
    metric: str
) -> dict:
    try:
        result = evauator.evaluate(entry)
        if result.status == "processed":
            return {
                f"retrieval_{metric}": result.score,
                f"retrieval_{metric}_reason": result.details,
                f"retrieval_{metric}_cost": result.cost.amount
            }
        else:
            return {
                f"retrieval_{metric}_error": result.details,
            }
    except Exception as e:
        return {
            f"retrieval_{metric}_error": str(e),
        }

def get_f1_dict(
    input_dict: dict,
) -> dict:
    recall = input_dict.get("retrieval_recall")
    precision = input_dict.get("retrieval_precision")
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
        recall_cost = input_dict["retrieval_recall_cost"]
        precision_cost = input_dict["retrieval_precision_cost"]
        return {
            "retrieval_f1": f1,
            "retrieval_f1_cost": recall_cost + precision_cost
        }
    return {}


def get_retrieval_evaluation_dict(
    reference_contexts: list[dict[str, str]],
    actual_contexts: list[dict[str, str]],
    model_name : str = "openai/gpt-4o-mini",
    max_tokens : int = 65_536
) -> dict:
    settings_dict = {
        "model": model_name,
        "max_tokens": max_tokens
    }
    entry = RagasContextRecallEntry(
        expected_contexts=[a["text"] for a in reference_contexts],
        contexts=[a["text"] for a in actual_contexts]
    )
    result = {}
    evaluator = RagasContextRecallEvaluator(settings=settings_dict)
    result.update(_evaluate(entry, evaluator, "recall"))
    evaluator = RagasContextPrecisionEvaluator(settings=settings_dict)
    result.update(_evaluate(entry, evaluator, "precision"))
    result.update(get_f1_dict(result))
    return result
