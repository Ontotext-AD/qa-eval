from .steps import evaluate_steps


def add_steps_evaluation(reference: dict, target: dict, eval_result: dict):
    act_steps = target["steps"]
    eval_result["actual_steps"] = act_steps
    if "reference_steps" in reference:
        ref_steps = reference["reference_steps"]
        steps_score = evaluate_steps(ref_steps, act_steps)
        eval_result["steps_score"] = steps_score


def run_evaluation(
        qa_dataset: list[dict],
        responses_dict: dict,
) -> list[dict]:
    # Output metrics are not nested, for simpler aggregation
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
            if "reference_answer" in question:
                eval_result["reference_answer"] = question["reference_answer"]
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
                from qa_eval.answer_evaluation import OpenAIAnswerEvaluator
                if not answer_evaluator:
                    answer_evaluator = OpenAIAnswerEvaluator()
                eval_result.update(
                    answer_evaluator.get_evaluation_result_dict(
                        question,
                        actual_result,
                    )
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
