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
        responses_dict: dict,
) -> list[dict]:
    answer_evaluator = None
    evaluation_results = []
    for template in gsc_templates:
        template_id = template["template_id"]
        #actual_steps_count_total, actual_steps_error_total = defaultdict(int), defaultdict(int)
        for question in template["questions"]:
            actual_result = responses_dict[question["id"]]
            reference_steps = question["reference_steps"]
            eval_result = {
                "template_id": template_id,
                "question_id": actual_result["question_id"],
                "question_text": question["question_text"],
                "reference_steps": reference_steps,
            }
            if "error" in actual_result:
                eval_result.update({
                    "status": "error",
                    "error": actual_result["error"],
                })
                evaluation_results.append(eval_result)
                continue

            eval_result.update({
                "status": "success",
                "actual_steps": actual_result["steps"],
                "actual_answer": actual_result["actual_answer"],
                "input_tokens": actual_result["input_tokens"],
                "output_tokens": actual_result["output_tokens"],
                "total_tokens": actual_result["total_tokens"],
                "elapsed_sec": actual_result["elapsed_sec"],
            })
            if "reference_answer" in question:
                from qa_eval.answer_evaluation import AnswerOpenAIEvaluator

                eval_result["reference_answer"] = question["reference_answer"]
                if not answer_evaluator:
                    answer_evaluator = AnswerOpenAIEvaluator()
                t, p, tp, reason, error = answer_evaluator.evaluate_answer(
                    question["question_text"],
                    question["reference_answer"],
                    actual_result["actual_answer"],
                )
                if error:
                    eval_result["answer_eval_error"] = error
                else:
                    eval_result.update({
                        # Nested output would be much cleaner:
                        # ```yaml
                        # answer_eval:
                        #     t: 0
                        #     ....
                        # ```
                        # but would complicated aggregation
                        "answer_eval_t": t,
                        "answer_eval_p": p,
                        "answer_eval_tp": tp,
                        "answer_eval_reason": reason,
                    })
                    recall = t / tp if t is not None and tp else None
                    precision = p / tp if p is not None and tp else None
                    if recall is not None and precision is not None and recall + precision > 0:
                        f1 = 2 * recall * precision / (recall + precision)
                    else:
                        f1 = None
                    if recall is not None:
                        eval_result["answer_eval_recall"] = recall
                    if precision is not None:
                        eval_result["answer_eval_precision"] = precision
                    if f1 is not None:
                        eval_result["answer_eval_f1"] = f1

            steps_score = evaluate_steps(reference_steps, actual_result["steps"])
            eval_result["steps_score"] = steps_score
            evaluation_results.append(eval_result)
            # for step in eval_result["steps"]:
            #     actual_steps_count_total[step["name"]] += 1
            #     if step["status"] == "error":
            #         actual_steps_error_total[step["name"]] += 1
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
    metrics = [
        "answer_eval_recall",
        "answer_eval_precision",
        "answer_eval_f1",
        "steps_score",
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
        for metric in metrics:
            results_for_template = results_per_template[template_id]
            series = results_for_template.get(metric, [])
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
        summary["micro"][metric] = stats_for_series(series)

    summary["macro"] = {}
    for metric in metrics:
        means = [
            values[metric]["mean"]
            for template_id, values in summary["per_template"].items()
            if values.get(metric) is not None
        ]
        summary["macro"][metric] = {"mean": mean(means) if means else 0}

    return summary
