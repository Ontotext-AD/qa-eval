import copy

from qa_eval import (
    get_var_to_values,
    compare_sparql_results,
    get_permutation_indices,
)


def test_get_var_to_values():
    bindings = []
    result = get_var_to_values(["s"], bindings)
    assert result == {"s": []}

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}},
    ]
    result = get_var_to_values(["x"], bindings)
    assert result == {"x": ["http://example.com/Person/1", "http://example.com/Person/2"]}

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}, "y": {"type": "literal", "value": "A"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {"x": ["http://example.com/Person/1", "http://example.com/Person/2"], "y": ["A", "B"]}

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}, "y": {"type": "literal", "value": "A"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {"x": ["http://example.com/Person/2", "http://example.com/Person/1"], "y": ["B", "A"]}

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {"x": ["http://example.com/Person/2", "http://example.com/Person/1"], "y": ["B", None]}

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/3"}, "y": {"type": "literal", "value": "A"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/5"}, "y": {"type": "literal", "value": "A"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {
        "x": [
            "http://example.com/Person/2",
            "http://example.com/Person/1",
            "http://example.com/Person/3",
            "http://example.com/Person/6",
            "http://example.com/Person/5",
        ],
        "y": ["B", None, "A", None, "A"]
    }

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}, "y": {"type": "literal", "value": "B"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/3"}, "y": {"type": "literal", "value": "A"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/5"}, "y": {"type": "literal", "value": "A"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {
        "x": [
            "http://example.com/Person/2",
            "http://example.com/Person/1",
            "http://example.com/Person/3",
            "http://example.com/Person/6",
            "http://example.com/Person/5",
        ],
        "y": [None, "B", "A", None, "A"]
    }

    bindings = [
        {"x": {"type": "uri", "value": "http://example.com/Person/2"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/3"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
        {"x": {"type": "uri", "value": "http://example.com/Person/5"}},
    ]
    result = get_var_to_values(["x", "y"], bindings)
    assert result == {
        "x": [
            "http://example.com/Person/2",
            "http://example.com/Person/1",
            "http://example.com/Person/3",
            "http://example.com/Person/6",
            "http://example.com/Person/5",
        ],
        "y": [None, None, None, None, None]
    }


def test_compare_empty_sparql_results() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": []}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["personName", "person"]) == False

    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": []}
    }
    actual_sparql_results = {
        "head": {"vars": ["x", "y"]},
        "results": {"bindings": []}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["personName", "person"]) == True

    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": []}
    }
    actual_sparql_results = {
        "head": {"vars": ["x", "y", "z"]},
        "results": {"bindings": []}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["personName", "person"]) == True

    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": []}
    }
    actual_sparql_results = {
        "head": {"vars": ["x"]},
        "results": {"bindings": []}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["personName", "person"]) == False

    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": []}
    }
    actual_sparql_results = {
        "head": {"vars": ["x"]},
        "results": {"bindings": []}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person"]) == True


def test_compare_sparql_results_ask() -> None:
    expected_sparql_results = {"head": {}, "boolean": True}
    actual_sparql_results = {"head": {}, "boolean": True}
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, []) == True

    expected_sparql_results = {"head": {}, "boolean": False}
    actual_sparql_results = {"head": {}, "boolean": True}
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, []) == False

    expected_sparql_results = {"head": {}, "boolean": True}
    actual_sparql_results = {"head": {}, "boolean": False}
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, []) == False

    expected_sparql_results = {"head": {}, "boolean": False}
    actual_sparql_results = {"head": {}, "boolean": False}
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, []) == True


def test_compare_sparql_results_exactly_the_same_results_as_expected() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    actual_sparql_results = copy.deepcopy(expected_sparql_results)

    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person", "personName"]) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, ["person", "personName"], results_are_ordered=True
    ) == True

    required_columns = ["personName"]
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, required_columns) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, required_columns, results_are_ordered=True
    ) == True

    required_columns = []
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, required_columns) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, required_columns, results_are_ordered=True
    ) == True


def test_compare_sparql_results_same_results_as_expected_but_variables_are_renamed() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["x", "y"]},
        "results": {"bindings": [
            {
                "x": {"type": "uri", "value": "http://example.com/Person/1"},
                "y": {"type": "literal", "value": "Alice"}
            },
            {
                "x": {"type": "uri", "value": "http://example.com/Person/2"},
                "y": {"type": "literal", "value": "Bob"}
            }
        ]}
    }

    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person", "personName"]) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, ["person", "personName"], results_are_ordered=True
    ) == True

    required_columns = ["personName"]
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, required_columns) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, required_columns, results_are_ordered=True
    ) == True

    required_columns = []
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, required_columns) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, required_columns, results_are_ordered=True
    ) == True


def test_compare_sparql_results_equals_one_binding() -> None:
    expected_sparql_results = {
        "head": {"vars": ["average_person_age"]},
        "results": {"bindings": [
            {
                "average_person_age": {
                    "type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#decimal", "value": "35"
                },
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["avg"]},
        "results": {"bindings": [
            {
                "avg": {
                    "type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#decimal", "value": "35"
                },
            }
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["average_person_age"]) == True


def test_compare_sparql_results_not_equals() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person", "personName"]) == False
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, ["person", "personName"], results_are_ordered=True
    ) == False


def test_compare_sparql_results_different_order() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["person", "personName"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"}
            }
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person", "personName"]) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results, ["person", "personName"], results_are_ordered=True
    ) == False


def test_compare_sparql_results_different_order_optional_columns() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person", "personName", "personAge"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personName": {"type": "literal", "value": "Alice"},
                "personAge": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "30"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personName": {"type": "literal", "value": "Bob"},
                "personAge": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "35"}
            }
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["person", "personAge", "gender"]},
        "results": {"bindings": [
            {
                "person": {"type": "uri", "value": "http://example.com/Person/2"},
                "personAge": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "35"},
                "gender": {"type": "literal", "value": "male"}
            },
            {
                "person": {"type": "uri", "value": "http://example.com/Person/1"},
                "personAge": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "30"},
                "gender": {"type": "literal", "value": "female"}
            }
        ]}
    }
    required_columns = ["person", "personAge"]
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, required_columns) == True
    assert compare_sparql_results(
        expected_sparql_results, actual_sparql_results,
        required_columns, results_are_ordered=True
    ) == False


def test_compare_sparql_results_empty_binding_values() -> None:
    expected_sparql_results = {
        "head": {"vars": ["x", "y"]},
        "results": {"bindings": [
            {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/3"}, "y": {"type": "literal", "value": "A"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/5"}, "y": {"type": "literal", "value": "A"}},
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["c", "p"]},
        "results": {"bindings": [
            {"c": {"type": "uri", "value": "http://example.com/Person/2"}},
            {"c": {"type": "uri", "value": "http://example.com/Person/1"}, "p": {"type": "literal", "value": "B"}},
            {"c": {"type": "uri", "value": "http://example.com/Person/3"}, "p": {"type": "literal", "value": "A"}},
            {"c": {"type": "uri", "value": "http://example.com/Person/6"}},
            {"c": {"type": "uri", "value": "http://example.com/Person/5"}, "p": {"type": "literal", "value": "A"}},
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["x", "y"]) == False

    expected_sparql_results = {
        "head": {"vars": ["x", "y"]},
        "results": {"bindings": [
            {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/3"}, "y": {"type": "literal", "value": "A"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/5"}, "y": {"type": "literal", "value": "A"}},
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["x", "y"]},
        "results": {"bindings": [
            {"x": {"type": "uri", "value": "http://example.com/Person/2"}, "y": {"type": "literal", "value": "B"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/1"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/3"}, "y": {"type": "literal", "value": "A"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/6"}},
            {"x": {"type": "uri", "value": "http://example.com/Person/5"}, "y": {"type": "literal", "value": "A"}},
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["x", "y"]) == True


def test_compare_sparql_results_additional_column() -> None:
    expected_sparql_results = {
        "head": {"vars": ["person"]},
        "results": {"bindings": [
            {"person": {"type": "uri", "value": "http://example.com/Person/2"}},
            {"person": {"type": "uri", "value": "http://example.com/Person/3"}},
        ]}
    }
    actual_sparql_results = {
        "head": {"vars": ["p", "n"]},
        "results": {"bindings": [
            {
                "p": {"type": "uri", "value": "http://example.com/Person/3"},
                "n": {"type": "literal", "value": "Alice"}
            },
            {
                "p": {"type": "uri", "value": "http://example.com/Person/2"},
                "n": {"type": "literal", "value": "Bob"}
            },
        ]}
    }
    assert compare_sparql_results(expected_sparql_results, actual_sparql_results, ["person"]) == True


def test_get_permutation_indices() -> None:
    assert get_permutation_indices([1], []) == []
    assert get_permutation_indices([], [1]) == []

    assert get_permutation_indices([1, 2, 3], [1]) == []
    assert get_permutation_indices([1, 2, 3], [1, 2]) == []

    assert get_permutation_indices([1, 2, 3], [1, 2, 3]) == [0, 1, 2]
    assert get_permutation_indices([1, 2, 3], [1, 3, 2]) == [0, 2, 1]
    assert get_permutation_indices([1, 2, 3], [2, 1, 3]) == [1, 0, 2]
    assert get_permutation_indices([1, 2, 3], [2, 3, 1]) == [1, 2, 0]
    assert get_permutation_indices([1, 2, 3], [3, 1, 2]) == [2, 0, 1]
    assert get_permutation_indices([1, 2, 3], [3, 2, 1]) == [2, 1, 0]

    assert get_permutation_indices([1, 1, 2, 3], [3, 1, 2, 2]) == []
    assert get_permutation_indices([1, 1, 2, 3], [3, 1, 2, 1]) == [3, 0, 2, 1]

    assert get_permutation_indices([1, None, "3"], ["3", 1, None]) == [2, 0, 1]
