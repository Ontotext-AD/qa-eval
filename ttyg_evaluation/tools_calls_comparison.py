import json
from _collections import defaultdict

from .sparql_results_comparison import compare_sparql_results


def compare_tools_outputs(
        reference: dict,
        actual: dict
) -> bool:
    if "output_media_type" in reference:
        if reference["output_media_type"] in {"application/sparql-results+json", "application/json"}:
            reference_output = json.loads(reference["output"])
            actual_output = json.loads(actual["output"])
            if reference["output_media_type"] == "application/sparql-results+json":
                return compare_sparql_results(
                    reference_output,
                    actual_output,
                    reference["required_columns"],
                    reference.get("ordered", False),
                )
            else:
                return reference_output == actual_output
    return reference["output"] == actual["output"]


def match_group_by_output(
        reference_calls: list[list[dict]],
        group_idx: int,
        actual_calls: list[dict],
        candidates_by_name: dict[str, list[int]],
) -> list[tuple[tuple[int, int], int]]:
    used_actual_indices = set()
    matches = []

    reference_group = reference_calls[group_idx]
    for reference_idx, reference_tool in enumerate(reference_group):
        name = reference_tool["name"]
        candidates = reversed(candidates_by_name.get(name, []))
        for actual_idx in candidates:
            if actual_idx in used_actual_indices:
                continue
            actual_tool = actual_calls[actual_idx]
            if compare_tools_outputs(reference_tool, actual_tool):
                matches.append(((group_idx, reference_idx), actual_idx))
                used_actual_indices.add(actual_idx)
                break
    return matches


def collect_possible_matches_by_name_and_status(
        group: list[dict],
        actual_calls: list[dict],
        search_upto: int,
) -> dict[str, list[int]]:
    group_by_name = defaultdict(list)

    for j in range(search_upto):
        name = actual_calls[j]["name"]
        if actual_calls[j]["status"] == "success":
            group_by_name[name].append(j)

    reference_names = {item["name"] for item in group}
    return {name: group_by_name[name] for name in reference_names if name in group_by_name}


def get_tools_calls_matches(
        reference_calls: list[list[dict]],
        actual_calls: list[dict],
) -> list[tuple[tuple[int, int], int]]:
    # when we have autocomplete
    # matches = []
    # search_upto = len(actual_calls)
    # for group_idx in reversed(range(len(reference_calls))):
    #     group = reference_calls[group_idx]
    #     candidates = collect_possible_matches_by_name(group, actual_calls, search_upto)
    #
    #     matched = match_group_by_output(reference_calls, group_idx, actual_calls, candidates)
    #     if len(matched) == len(group):
    #         # update search_upto to just before the highest matched actual index
    #         matches.extend(matched)
    #         search_upto = min(j for (_, j) in matched)
    #     elif len(matched) < len(group):
    #         matches.extend(matched)
    #         break # a call is not matched and missing, abort
    #     else:
    #         break  # a call is not matched and missing, abort
    # return matches

    # for now, we have only the last tool(s)
    last_group = reference_calls[-1]
    candidates = collect_possible_matches_by_name_and_status(last_group, actual_calls, len(actual_calls))
    return match_group_by_output(reference_calls, -1, actual_calls, candidates)
