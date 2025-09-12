from collections import Counter, defaultdict


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


def is_permutation(list1: list, list2: list, permutation: list[int]) -> bool:
    for i, j in enumerate(permutation):
        if list1[i] != list2[j]:
            return False

    return True


def compare_unordered_results(
    reference_values: list[str],
    actual_values: list[str],
    permutation: list[int],
) -> tuple[bool, list[int]]:
    if permutation:
        if is_permutation(actual_values, reference_values, permutation):
            return True, permutation
    else:
        permutation_indices = get_permutation_indices(reference_values, actual_values)
        if permutation_indices:
            return True, permutation_indices
    return False, permutation


def compare_columns(
    reference_values: list[str],
    actual_values: list,
    results_are_ordered: bool,
    permutation: list[int],
) -> tuple[bool, list[int]]:
    """Compares a list of actual values against a reference list.

    This function supports both order-sensitive and order-insensitive
    comparisons. For an unordered comparison, it can either find a new
    permutation or verify a pre-existing one.

    Args:
        reference_values: The list of expected values.
        actual_values: The list of values to be checked.
        results_are_ordered: If True, performs a direct element-wise
            comparison. If False, checks if `actual_values` is a
            permutation of `reference_values`.
        permutation: An optional list of indices. For unordered checks,
            if provided, it's used to verify a specific permutation.

    Returns:
        A tuple containing:
            - bool: True if the lists match (either directly or as a
              permutation)
            - list[int]: The list of permutation indices. If an unordered
              match is found, ordering is not required, this list maps the indices of
              `reference_values` to `actual_values`.
    """
    if not results_are_ordered:
        return compare_unordered_results(reference_values, actual_values, permutation)
    if reference_values == actual_values:
        return True, permutation
    return False, permutation


def compare_values(
    reference_vars: list[str],
    reference_var_to_values: dict[str, list],
    actual_vars: list[str],
    actual_var_to_values: dict[str, list],
    required_vars: list[str],
    results_are_ordered: bool,
) -> bool:
    permutation = []
    mapped_or_skipped_reference_vars = set()
    mapped_actual_vars = set()
    for reference_var in reference_vars:
        reference_values = reference_var_to_values[reference_var]
        for actual_var in actual_vars:
            if actual_var in mapped_actual_vars:
                continue
            is_new_mapping, permutation = compare_columns(
                reference_values,
                actual_var_to_values[actual_var],
                results_are_ordered,
                permutation,
            )
            if is_new_mapping:
                mapped_or_skipped_reference_vars.add(reference_var)
                mapped_actual_vars.add(actual_var)
                break

        if reference_var not in mapped_or_skipped_reference_vars:
            if reference_var in required_vars:
                return False
            # optional, we can skip it
            mapped_or_skipped_reference_vars.add(reference_var)

    return len(mapped_or_skipped_reference_vars) == len(reference_vars)


def compare_sparql_results(
    reference_sparql_result: dict,
    actual_sparql_result: dict,
    required_vars: list[str],
    results_are_ordered: bool = False,
) -> float:
    # DESCRIBE results
    if isinstance(actual_sparql_result, str):
        return 0.0

    # ASK
    if "boolean" in reference_sparql_result:
        return float(
            "boolean" in actual_sparql_result
            and reference_sparql_result["boolean"] == actual_sparql_result["boolean"]
        )

    reference_bindings: list[dict] = reference_sparql_result["results"]["bindings"]
    actual_bindings: list[dict] = actual_sparql_result.get("results", dict()).get(
        "bindings", []
    )
    reference_vars: list[str] = reference_sparql_result["head"]["vars"]
    actual_vars: list[str] = actual_sparql_result["head"].get("vars", [])

    if (not actual_bindings) and (not reference_bindings):
        return float(len(actual_vars) >= len(required_vars))
    elif (not actual_bindings) or (not reference_bindings):
        return 0.0

    # re-order the vars, so that required come first
    reference_vars = required_vars + [
        var for var in reference_vars if var not in required_vars
    ]

    reference_var_to_values: dict[str, list] = get_var_to_values(
        reference_vars, reference_bindings
    )
    actual_var_to_values: dict[str, list] = get_var_to_values(
        actual_vars, actual_bindings
    )

    return compare_values(
        reference_vars,
        reference_var_to_values,
        actual_vars,
        actual_var_to_values,
        required_vars,
        results_are_ordered,
    )
