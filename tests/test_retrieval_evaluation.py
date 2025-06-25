import math

from ttyg_evaluation.retrieval_evaluation import recall_at_k, average_precision


def test_recall_at_k() -> None:
    relevant_items = {1, 3, 5, 7, 9}
    retrieved_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    k_value = 5
    r_at_k = recall_at_k(relevant_items, retrieved_items, k_value)

    assert math.isclose(r_at_k, 0.6)


def test_average_precision() -> None:
    relevant_q1 = {1, 2, 5, 8}
    retrieved_q1 = [1, 3, 2, 4, 5, 6, 7, 8]

    ap_score = average_precision(relevant_q1, retrieved_q1)

    assert math.isclose(ap_score, 0.6916666666666667)
