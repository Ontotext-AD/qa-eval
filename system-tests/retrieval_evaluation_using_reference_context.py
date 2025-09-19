from pprint import pprint

from qa_eval.steps.retrieval_evaluation_using_context_texts import (
    get_retrieval_evaluation_dict
)


result_dict = get_retrieval_evaluation_dict(
    reference_contexts=[
        {
            "id": "http://example.com/resource/doc/1",
            "text": "Rayleigh discovered that shorter wavelengths are scattered more than long wavelengths."
        },
        {
            "id": "http://example.com/resource/doc/2",
            "text": "Gases scatter sunlight"
        }
    ],
    actual_contexts=[
        {
            "id": "http://example.com/resource/doc/3",
            "text": "In Rayleigh scattering, shorter wavelengths are scattered more"
        },
        {
            "id": "http://example.com/resource/doc/4",
            "text": "The sun shines onto the atmosphere. The atmosphere contains various gases."
        }
    ]
)
pprint(result_dict)
assert "retrieval_recall" in result_dict
#assert "retrieval_recall_reason" in result_dict
#assert "retrieval_recall_cost" in result_dict
assert "retrieval_precision" in result_dict
#assert "retrieval_precision_reason" in result_dict
#assert "retrieval_precision_cost" in result_dict
assert "retrieval_f1" in result_dict
#assert "retrieval_f1_cost" in result_dict
