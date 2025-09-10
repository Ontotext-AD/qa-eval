from langevals_ragas.response_relevancy import (
    RagasResponseRelevancyEvaluator,
    RagasResponseRelevancyEntry
)


def get_relevance_dict(
    question_text: str, 
    actual_answer: str, 
    model_name : str = 'openai/gpt-4o-mini', 
    max_tokens: int = 65_536
) -> dict:
    settings_dict = {
        'model': model_name,
        'max_tokens': max_tokens
    }
    entry = RagasResponseRelevancyEntry(
        input=question_text,
        output=actual_answer
    )
    evaluator = RagasResponseRelevancyEvaluator(settings=settings_dict)
    _result_dict = evaluator.evaluate(entry)["ragas_answer_relevancy"][0]
    if _result_dict["status"] == "processed":
        return {
            "answer_relevance": _result_dict["score"],
            "answer_relevance_cost": _result_dict["cost"]["amount"]
        }
    else:
        return {
            "answer_relevance_error": _result_dict["details"]
        }
