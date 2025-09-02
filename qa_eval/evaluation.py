import json
from collections import defaultdict
from statistics import mean, median
from typing import Any

from .steps import get_steps_matches


def compute_recall_precision_f1(
    n_pos: int | None,
    n_pred_pos: int | None,
    n_true_pos: int | None,
) -> tuple[float | None, float | None, float | None]:
    recall = None
    precision = None
    f1 = None
    if n_true_pos is not None and n_pos:
        recall = n_true_pos / n_pos
    if n_true_pos is not None and n_pred_pos:
        precision = n_true_pos / n_pred_pos
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    return recall, precision, f1


def evaluate_steps(
    reference_steps_groups: list[list[dict]],
    actual_steps: list[dict]
) -> float:
    matches = get_steps_matches(reference_steps_groups, actual_steps)
    matches_by_group = defaultdict(list)
    scores_by_group = defaultdict(float)
    for ref_group_idx, ref_match_idx, actual_idx, score in matches:
        matches_by_group[ref_group_idx].append(ref_match_idx)
        scores_by_group[ref_group_idx] += score
        reference_steps_groups[ref_group_idx][ref_match_idx]["matches"] \
            = actual_steps[actual_idx]["id"]
    group_ix = -1  # For now, consider only the last reference group of steps
    return scores_by_group[group_ix] / len(reference_steps_groups[group_ix])


def add_steps_evaluation(question: dict, actual_result: dict, eval_result: dict):
    act_steps = actual_result["steps"]
    eval_result["actual_steps"] = act_steps
    if "reference_steps" in question:
        ref_steps = question["reference_steps"]
        steps_score = evaluate_steps(ref_steps, act_steps)
        eval_result["steps_score"] = steps_score


def add_answer_evaluation(
    question: dict,
    actual_result: dict,
    answer_evaluator: 'AnswerEvaluator',
    eval_result: dict
):
    # Nested output would be cleaner:
    # ```yaml
    # answer_eval:
    #     n_pos: ...
    #     n_pred_pos: ...
    #     n_true_pos: ...
    # ```
    # but would complicate aggregation
    eval_result["reference_answer"] = question["reference_answer"]
    num_ref_claims, num_actual_claims, num_matching_claims, reason, error = \
    answer_evaluator.evaluate_answer(
        question["question_text"],
        question["reference_answer"],
        actual_result["actual_answer"],
    )
    if error:
        eval_result["answer_eval_error"] = error
    else:
        eval_result.update({
            "answer_num_ref_claims": num_ref_claims,
            "answer_num_actual_claims": num_actual_claims,
            "answer_num_matching_claims": num_matching_claims,
            "answer_eval_reason": reason,
        })
        recall, precision, f1 = compute_recall_precision_f1(
            num_ref_claims, num_actual_claims, num_matching_claims
        )
        if recall is not None:
            eval_result["answer_recall"] = recall
        if precision is not None:
            eval_result["answer_precision"] = precision
        if f1 is not None:
            eval_result["answer_f1"] = f1


def run_evaluation(
        qa_dataset: list[dict],
        responses_dict: dict,
) -> list[dict]:
    answer_evaluator = None
    evaluation_results = []
    for template in qa_dataset:
        template_id = template["template_id"]
        for question in template["questions"]:
            actual_result = responses_dict[question["id"]]
            eval_result = {
                "template_id": template_id,
                "question_id": actual_result["question_id"],
                "question_text": question["question_text"],
            }
            if "reference_steps" in question:
                eval_result["reference_steps"] = question["reference_steps"]
            if "error" in actual_result:
                eval_result.update({
                    "status": "error",
                    "error": actual_result["error"],
                })
                evaluation_results.append(eval_result)
                continue
            eval_result["status"] = "success"
            if "reference_answer" in question:
                from qa_eval.answer_evaluation import AnswerOpenAIEvaluator
                if not answer_evaluator:
                    answer_evaluator = AnswerOpenAIEvaluator()
                add_answer_evaluation(
                    question,
                    actual_result,
                    answer_evaluator,
                    eval_result
                )
            if "steps" in actual_result:
                add_steps_evaluation(question, actual_result, eval_result)
            eval_result.update({
                "actual_answer": actual_result["actual_answer"],
                "input_tokens": actual_result["input_tokens"],
                "output_tokens": actual_result["output_tokens"],
                "total_tokens": actual_result["total_tokens"],
                "elapsed_sec": actual_result["elapsed_sec"],
            })
            evaluation_results.append(eval_result)
    return evaluation_results


def stats_for_series(values: list) -> dict[str, float]:
    return {
        "sum": sum(values),
        "mean": mean(values) if values else 0,
        "median": median(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
    }


def compute_aggregates(samples: list[dict]) -> dict:
    metrics = [
        "answer_recall",
        "answer_precision",
        "answer_f1",
        "steps_score",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "elapsed_sec"
    ]
    protected_metrics = [
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "elapsed_sec"
    ]
    results_per_template = defaultdict(lambda: defaultdict(list))
    number_of_samples_per_template_by_status = defaultdict(lambda: defaultdict(int))
    steps_summary_per_template = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    templates_ids = set()
    for sample in samples:
        template_id = sample["template_id"]
        templates_ids.add(template_id)

        if "error" in sample:
            number_of_samples_per_template_by_status[template_id]["error"] += 1
            continue

        number_of_samples_per_template_by_status[template_id]["success"] += 1

        for metric in metrics:
            value = sample.get(metric)
            if value is not None:
                results_per_template[template_id][metric].append(value)

        seen = set()
        for step in sample["actual_steps"]:
            name = step["name"]
            template_steps_summary = steps_summary_per_template[template_id]
            template_steps_summary["total"][name] += 1
            if step["status"] == "error":
                template_steps_summary["errors"][name] += 1
            if name not in seen:
                seen.add(name)
                template_steps_summary["once_per_sample"][name] += 1

            if step["status"] != "error":
                try:
                    res = json.loads(step["output"])
                    if "results" in res and "bindings" in res["results"]:
                        if not res["results"]["bindings"]:
                            template_steps_summary["empty_results"][name] += 1
                except json.decoder.JSONDecodeError:
                    pass

    summary = {"per_template": {}}

    for template_id in templates_ids:

        template_summary: dict[str, Any] = {
            "number_of_error_samples": number_of_samples_per_template_by_status[template_id]["error"],
            "number_of_success_samples": number_of_samples_per_template_by_status[template_id]["success"],
            "steps": {
                k1: {k2: v2 for k2, v2 in v1.items()}
                for k1, v1 in steps_summary_per_template[template_id].items()
            },
        }
        for metric in metrics:
            results_for_template = results_per_template[template_id]
            series = results_for_template.get(metric, [])
            if series or metric in protected_metrics:
                template_summary[metric] = stats_for_series(series)

        summary["per_template"][template_id] = template_summary

    summary["micro"] = {
        "number_of_error_samples": sum(
            [values["error"] for values in number_of_samples_per_template_by_status.values()]),
        "number_of_success_samples": sum(
            [values["success"] for values in number_of_samples_per_template_by_status.values()]),
    }
    for metric in metrics:
        series = [
            i
            for values in results_per_template.values()
            for i in values[metric]
            if values.get(metric) is not None
        ]
        if series or metric in protected_metrics:
            summary["micro"][metric] = stats_for_series(series)

    summary["macro"] = {}
    for metric in metrics:
        means = [
            values[metric]["mean"]
            for template_id, values in summary["per_template"].items()
            if values.get(metric) is not None
        ]
        if means or metric in protected_metrics:
            summary["macro"][metric] = {"mean": mean(means) if means else 0}

    return summary
