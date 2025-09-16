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
    try:
        result = evaluator.evaluate(entry)
        if result.status == "processed":
            return {
                "answer_relevance": result.score,
                "answer_relevance_cost": result.cost.amount,
                "answer_relevance_reason": result.details,
            }
        else:
            return {
                "answer_relevance_error": result.details
            }
    except Exception as e:
        return {
            "answer_relevance_error": str(e),
        }
