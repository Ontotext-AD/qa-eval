from collections import Counter
from typing import Union
import itertools
import math


def truncate(number, decimals=0):
    """
    Truncates a float to a certain number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places must be zero or a positive integer.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0**decimals
    return math.trunc(number * factor) / factor


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


def parse_dict2table(
    reference_vars: Union[list[str], tuple[str, ...]],
    reference_var_to_values: dict[str, list],
) -> list[str]:
    result = []
    num_rows = len(reference_var_to_values[reference_vars[0]])
    for row_idx in range(num_rows):
        row = []
        for reference_var in reference_vars:
            val = reference_var_to_values[reference_var][row_idx]
            if isinstance(val, float):
                val = truncate(val, 5)
            if isinstance(val, int):
                val = float(val)
            val = str(val)
            row.append(val)
        result.append("".join(row))
    return result


def compare_values(
    reference_vars: list[str],
    reference_var_to_values: dict[str, list],
    actual_vars: Union[list[str], tuple[str, ...]],
    actual_var_to_values: dict[str, list],
    results_are_ordered: bool,
) -> bool:

    if len(reference_vars) > len(actual_vars):
        return False
    if len(reference_vars) < len(actual_vars):
        for combination in itertools.combinations(actual_vars, len(reference_vars)):
            if compare_values(
                reference_vars,
                reference_var_to_values,
                combination,
                actual_var_to_values,
                results_are_ordered,
            ):
                return True
        return False

    table = parse_dict2table(reference_vars, reference_var_to_values)
    for permutation in itertools.permutations(actual_vars):
        actual_table = parse_dict2table(permutation, actual_var_to_values)
        if (results_are_ordered and table == actual_table) or (
            not results_are_ordered and Counter(table) == Counter(actual_table)
        ):
            return True

    return False


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
    actual_vars: list[str] = actual_sparql_result["head"].get("vars", [])

    if (not actual_bindings) and (not reference_bindings):
        return float(len(actual_vars) >= len(required_vars))
    elif (not actual_bindings) or (not reference_bindings):
        return 0.0
    if len(required_vars) > len(actual_vars):
        return 0.0
    if len(required_vars) == 0:
        return 1.0

    reference_var_to_values: dict[str, list] = get_var_to_values(
        required_vars, reference_bindings
    )
    actual_var_to_values: dict[str, list] = get_var_to_values(
        actual_vars, actual_bindings
    )

    return float(
        compare_values(
            required_vars,
            reference_var_to_values,
            actual_vars,
            actual_var_to_values,
            results_are_ordered,
        )
    )
