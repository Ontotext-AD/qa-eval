import math

from graphrag_eval.steps.retrieval import recall_at_k, average_precision


def test_recall_at_k() -> None:
    relevant_items = {1, 3, 5, 7, 9}
    retrieved_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    r = recall_at_k(relevant_items, retrieved_items, 5)
    assert math.isclose(r, 0.6)


def test_average_precision() -> None:
    relevant_items = {1, 2, 5, 8}
    retrieved_items = [1, 3, 2, 4, 5, 6, 7, 8]
    p = average_precision(relevant_items, retrieved_items)
    assert math.isclose(p, 0.6916666666666667)
