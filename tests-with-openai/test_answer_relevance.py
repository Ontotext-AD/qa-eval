from qa_eval import answer_relevance


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
    eval_result_dict = answer_relevance.get_relevance_dict(
        "Why is the sky blue?", 
        "Because of the oxygen in the air"
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
    eval_result_dict = answer_relevance.get_relevance_dict(
        "Why is the sky blue?", 
        "Because of the oxygen in the air"
    )
    assert eval_result_dict == {
        "answer_relevance_error": "details"
    }
