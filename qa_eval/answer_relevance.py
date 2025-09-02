import pandas
import langevals
from langevals_core.base_evaluator import LLMEvaluatorSettings
from langevals_legacy.ragas_lib.common import RagasSettings as LegacyRagasSettins
from langevals_legacy.ragas_answer_relevancy import RagasAnswerRelevancyEvaluator as LegacyAnswerRelevancyEvaluator


MODEL = 'openai/gpt-4o-mini'
MAX_TOKENS = 65_536


def compute_answer_relevance(question_text: str, actual_answer: str, model: str = MODEL, max_tokens: int = MAX_TOKENS) -> dict:
    settings_dict = {
        'model': model,
        'max_tokens': max_tokens
    }
    legacy_settings = LegacyRagasSettins(**settings_dict)
    evaluators = [LegacyAnswerRelevancyEvaluator(settings=legacy_settings)]
    ds = pandas.DataFrame({'input': [question_text], 'output': [actual_answer]})
    eval_result = langevals.evaluate(ds, evaluators, max_evaluations_in_parallel=1)
    result_dict = eval_result.to_list()
    result_dict = result_dict["ragas_answer_relevancy"]
    del result_dict["passed"]
    del result_dict["label"]
    result_dict["cost"] = result_dict["cost"]["amount"]
    return result_dict
