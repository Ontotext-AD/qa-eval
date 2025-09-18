from pprint import pprint

from qa_eval.steps.retrieval_evaluation_using_answer import (
    get_retrieval_evaluation_dict
)


result_dict = get_retrieval_evaluation_dict(
    question_text="Why is the sky blue?",
    reference_answer="Because of Rayleigh scattering.",
    actual_contexts=[
        {
            "id": "http://example.com/resource/doc/1",
            "text": "Rayleigh discovered that shorter wavelengths are scattered more than long wavelengths."
        },
        {
            "id": "http://example.com/resource/doc/2",
            "text": "Gases scatter sunlight"
        }
    ]
)
pprint(result_dict)
assert "retrieval_answer_recall" in result_dict
assert "retrieval_answer_recall_reason" in result_dict
assert "retrieval_answer_recall_cost" in result_dict
assert "retrieval_answer_precision" in result_dict
assert "retrieval_answer_precision_reason" in result_dict
assert "retrieval_answer_precision_cost" in result_dict
assert "retrieval_answer_f1" in result_dict
assert "retrieval_answer_f1_cost" in result_dict
