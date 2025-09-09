import langevals
import pandas
from langevals_ragas.response_relevancy import RagasResponseRelevancyEvaluator


def get_relevance_dict(
    question_dict, 
    actual_answer_dict: dict, 
    model_name : str = 'openai/gpt-4o-mini', 
    max_tokens: int = 65_536
) -> dict:
    settings_dict = {
        'model': model_name,
        'max_tokens': max_tokens
    }
    ds = pandas.DataFrame(
        {
            "input": question_dict["question"],
            "output": actual_answer_dict["answer"]
        }
    )
    evaluator = RagasResponseRelevancyEvaluator(settings=settings_dict)
    _result_dict = langevals.evaluate(ds, [evaluator]).to_list()
    if _result_dict["status"] == "processed":
        return {
            "answer_relevance": _result_dict["score"],
            "answer_relevance_cost": _result_dict["cost"]["amount"]
        }
    else:
        return {
            "answer_relevance_error": _result_dict["details"]
        }
