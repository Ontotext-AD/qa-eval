from .steps import get_steps_evaluation_result_dict


def run_evaluation(
        qa_dataset: list[dict],
        responses_dict: dict,
) -> list[dict]:
    # Output metrics are not nested, for simpler aggregation
    answer_correctess_evaluator = None
    evaluation_results = []
    for template in qa_dataset:
        template_id = template["template_id"]
        for question in template["questions"]:
            actual_result = responses_dict[question["id"]]
            eval_result = {
                "template_id": template_id,
                "question_id": actual_result["question_id"],
                "question_text": question["question_text"]
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
            if "actual_answer" in actual_result:
                eval_result["actual_answer"] = actual_result["actual_answer"]
                from graphrag_eval import answer_relevance
                eval_result.update(
                    answer_relevance.get_relevance_dict(
                        question["question_text"],
                        actual_result["actual_answer"],
                    )
                )
            if "reference_answer" in question and "actual_answer" in actual_result:
                from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
                if not answer_correctess_evaluator:
                    answer_correctess_evaluator = AnswerCorrectnessEvaluator()
                eval_result.update(
                    answer_correctess_evaluator.get_correctness_dict(
                        question,
                        actual_result,
                    )
                )
            if "steps" in actual_result:
                eval_result.update(
                    get_steps_evaluation_result_dict(question, actual_result)
                )
            eval_result.update({
                "input_tokens": actual_result["input_tokens"],
                "output_tokens": actual_result["output_tokens"],
                "total_tokens": actual_result["total_tokens"],
                "elapsed_sec": actual_result["elapsed_sec"],
            })
            evaluation_results.append(eval_result)
    return evaluation_results
