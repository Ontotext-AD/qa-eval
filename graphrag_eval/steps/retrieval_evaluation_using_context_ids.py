from typing import Iterable


def recall_at_k(relevant_ids: list, retrieved_ids: list, k: int = 10) -> float:
    """
    Calculates Recall@k.

    Args:
        relevant_ids (list): A list of ground truth relevant document IDs.
        retrieved_ids (list): A list of retrieved document IDs, ordered by rank.
        k (int): The cutoff for the retrieval list.

    Returns:
        float: The Recall@k score.
    """
    retrieved_at_k = retrieved_ids[:k]
    relevant_at_k = relevant_ids[:k]
    true_positives = len(set(relevant_at_k).intersection(set(retrieved_at_k)))
    total_relevant = len(relevant_at_k)
    if total_relevant == 0:
        return 0.0
    return true_positives / total_relevant


def average_precision(relevant_ids: Iterable, retrieved_ids: Iterable) -> float:
    """
    Calculates Average Precision (AP) for a single query.

    Args:
        relevant_ids (Iterable): A set of ground truth relevant document IDs.
        retrieved_ids (Iterable): A list of retrieved document IDs, ordered by rank.

    Returns:
        float: The Average Precision score.
    """
    relevant_set = set(relevant_ids)
    hits = 0
    sum_of_precisions = 0.0

    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_set:
            hits += 1
            precision_at_k = hits / (i + 1)
            sum_of_precisions += precision_at_k

    total_relevant = len(relevant_set)
    if total_relevant == 0:
        return 0.0

    return sum_of_precisions / total_relevant
