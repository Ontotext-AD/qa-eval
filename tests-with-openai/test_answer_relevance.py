from qa_eval import answer_relevance
from langevals_ragas.response_relevancy import RagasResponseRelevancyEvaluator



def test_get_relevance_dict_eval_success(monkeypatch):
    monkeypatch.setattr(
        answer_relevance, 
        'langevals.evaluate', 
        lambda *_: {
            "ragas_answer_relevancy": [
                {
                    "status": "processed",
                    "score": 0.0,
                    "passed": None,
                    "label": None,
                    "details": "details",
                    "cost": {
                        "currency": "USD",
                        "amount": 0.0007093499999999999
                    }                            
                }
            ]
        }
    )
    question_dict = {
        "question": "Why is the sky blue?",
        "reference_answer": "Because of the scattering of sunlight by the atmosphere."
    }
    response_dict = {
        "response": "Because of the oxygen in the air."
    }
    eval_result_dict = answer_relevance.get_relevance_dict(
        question_dict, 
        response_dict
    )
    assert eval_result_dict == {
        "answer_relevance": 0.9,
        "cost": 0.0007093499999999999,
    }


def test_get_relevance_dict_eval_error(monkeypatch):
    monkeypatch.setattr(
        answer_relevance, 
        'langevals.evaluate', 
        lambda *_: {
            "ragas_answer_relevancy": [
                {
                    "status": "error",
                    "details": "details",
                }
            ]
        }
    )
    question_dict = {
        "question": "Why is the sky blue?",
        "reference_answer": "Because of the scattering of sunlight by the atmosphere."
    }
    response_dict = {
        "response": "Because of the oxygen in the air."
    }
    eval_result_dict = answer_relevance.get_relevance_dict(
        question_dict, 
        response_dict
    )
    assert eval_result_dict == {
        "answer_relevance_error": "details"
    }
