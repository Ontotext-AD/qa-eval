import json
from collections import defaultdict
from statistics import mean, median
from typing import Any

from .steps import get_steps_matches


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


def run_evaluation(
        gsc_templates: list[dict],
        chat_responses: dict,
) -> list[dict]:
    evaluation_results = []
    for template in gsc_templates:
        template_id = template["template_id"]
        actual_steps_count_total, actual_steps_error_total = defaultdict(int), defaultdict(int)
        for question in template["questions"]:
            actual_results = chat_responses[question["id"]]
            reference_steps = question["reference_steps"]
            if "error" in actual_results:
                evaluation_results.append({
                    "template_id": template_id,
                    "question_id": actual_results["question_id"],
                    "question_text": question["question_text"],
                    "reference_steps": reference_steps,
                    "status": "error",
                    "error": actual_results["error"],
                })
                continue

            actual_steps = actual_results["steps"]
            score = evaluate_steps(reference_steps, actual_steps)

            for step in actual_steps:
                actual_steps_count_total[step["name"]] += 1
                if step["status"] == "error":
                    actual_steps_error_total[step["name"]] += 1

            evaluation_results.append({
                "status": "success",
                "template_id": template_id,
                "question_id": actual_results["question_id"],
                "question_text": question["question_text"],
                "reference_steps": reference_steps,
                "actual_answer": actual_results["actual_answer"],
                "actual_steps": actual_steps,
                "answer_score": score,
                "input_tokens": actual_results["input_tokens"],
                "output_tokens": actual_results["output_tokens"],
                "total_tokens": actual_results["total_tokens"],
                "elapsed_sec": actual_results["elapsed_sec"],
            })
    return evaluation_results


def stats_for_series(values: list) -> dict[str, float]:
    return {
        "sum": sum(values),
        "mean": mean(values) if values else 0,
        "median": median(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
    }


def compute_aggregations(samples: list[dict]) -> dict:
    data_series = ["answer_score", "input_tokens", "output_tokens", "total_tokens", "elapsed_sec"]

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

        for series in data_series:
            results_per_template[template_id][series].append(sample[series])

        seen = set()
        for step in sample["actual_steps"]:
            name = step["name"]
            steps_summary_per_template[template_id]["total"][name] += 1
            if step["status"] == "error":
                steps_summary_per_template[template_id]["errors"][name] += 1
            if name not in seen:
                seen.add(name)
                steps_summary_per_template[template_id]["once_per_sample"][name] += 1

            if step["status"] != "error":
                try:
                    res = json.loads(step["output"])
                    if "results" in res and "bindings" in res["results"]:
                        if not res["results"]["bindings"]:
                            steps_summary_per_template[template_id]["empty_results"][name] += 1
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
        for series in data_series:
            template_summary.update({
                series: stats_for_series(results_per_template[template_id][series]),
            })

        summary["per_template"][template_id] = template_summary

    summary["micro"] = {
        "number_of_error_samples": sum(
            [values["error"] for values in number_of_samples_per_template_by_status.values()]),
        "number_of_success_samples": sum(
            [values["success"] for values in number_of_samples_per_template_by_status.values()]),
    }
    for series in data_series:
        summary["micro"].update({
            series: stats_for_series([i for values in results_per_template.values() for i in values[series]]),
        })

    summary["macro"] = {}
    for series in data_series:
        means = [values[series]["mean"] for template_id, values in summary["per_template"].items()]
        summary["macro"].update({
            series: {
                "mean": mean(means) if means else 0
            }
        })

    return summary
