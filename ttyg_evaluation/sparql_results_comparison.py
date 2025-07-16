from collections import Counter


def get_var_to_values(
        vars_: list[str],
        bindings: list[dict],
) -> dict[str, list]:
    var_to_values = dict()
    for var in vars_:
        var_to_values[var] = []
        for binding in bindings:
            if var in binding:
                var_to_values[var].append(binding[var]["value"])
            else:
                var_to_values[var].append(None)
    return dict(var_to_values)


def get_permutation_indices(list1: list, list2: list) -> list:
    if len(list1) != len(list2) or Counter(list1) != Counter(list2):
        return []

    indices = []
    used = [False] * len(list1)

    for item2 in list2:
        for i in range(len(list1)):
            if not used[i] and list1[i] == item2:
                indices.append(i)
                used[i] = True
                break

    return indices


def compare_sparql_results(
        reference_sparql_result: dict,
        actual_sparql_result: dict,
        required_vars: list[str],
        results_are_ordered: bool = False,
) -> bool:
    # DESCRIBE results
    if isinstance(actual_sparql_result, str):
        return False

    # ASK
    if "boolean" in reference_sparql_result:
        return "boolean" in actual_sparql_result and \
            reference_sparql_result["boolean"] == actual_sparql_result["boolean"]

    reference_bindings: list[dict] = reference_sparql_result["results"]["bindings"]
    actual_bindings: list[dict] = actual_sparql_result.get("results", dict()).get("bindings", [])
    reference_vars: list[str] = reference_sparql_result["head"]["vars"]
    actual_vars: list[str] = actual_sparql_result["head"].get("vars", [])

    if (not actual_bindings) and (not reference_bindings):
        return len(actual_vars) >= len(required_vars)
    elif (not actual_bindings) or (not reference_bindings):
        return False

    # re-order the vars, so that required come first
    reference_vars = required_vars + [var for var in reference_vars if var not in required_vars]

    reference_var_to_values: dict[str, list] = get_var_to_values(reference_vars, reference_bindings)
    actual_var_to_values: dict[str, list] = get_var_to_values(actual_vars, actual_bindings)

    permutation = []
    mapped_or_skipped_reference_vars, mapped_actual_vars = set(), set()
    for reference_var in reference_vars:
        reference_values = reference_var_to_values[reference_var]
        for actual_var in actual_vars:
            if actual_var not in mapped_actual_vars:
                actual_values = actual_var_to_values[actual_var]
                if not results_are_ordered:
                    permutation_indices = get_permutation_indices(reference_values, actual_values)
                    if permutation_indices:
                        if permutation:
                            if permutation_indices == permutation:
                                mapped_or_skipped_reference_vars.add(reference_var)
                                mapped_actual_vars.add(actual_var)
                                break
                        else:
                            permutation = permutation_indices
                            mapped_or_skipped_reference_vars.add(reference_var)
                            mapped_actual_vars.add(actual_var)
                            break
                elif reference_values == actual_values:
                    mapped_or_skipped_reference_vars.add(reference_var)
                    mapped_actual_vars.add(actual_var)
                    break
        if reference_var not in mapped_or_skipped_reference_vars:
            if reference_var in required_vars:
                return False
            # optional, we can skip it
            mapped_or_skipped_reference_vars.add(reference_var)

    return len(mapped_or_skipped_reference_vars) == len(reference_vars)
