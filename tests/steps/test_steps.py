from graphrag_eval import (
    compare_steps_outputs,
    match_group_by_output,
    collect_possible_matches_by_name_and_status,
    get_steps_matches
)
from graphrag_eval.steps import evaluate_steps


sparkle_expected_step = {
    "name": "sparql_query",
    "args": {
        "query": "\nPREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>\nPREFIX cim: <https://cim.ucaiug.io/ns#>\nPREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nselect distinct ?transformer ?transformerName\nwhere {\n    bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)\n\n    ?transformer a cim:PowerTransformer ;\n      cim:Equipment.EquipmentContainer ?substation ;\n      cim:IdentifiedObject.name ?transformerName .\n}\n"
    },
    "output": "{\"head\": {\"vars\": [\"transformer\", \"transformerName\"]}, \"results\": {\"bindings\": [{\"transformer\": {\"type\": \"uri\", \"value\": \"urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f\"}, \"transformerName\": {\"type\": \"literal\", \"value\": \"OSLO    T2\"}}, {\"transformer\": {\"type\": \"uri\", \"value\": \"urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f\"}, \"transformerName\": {\"type\": \"literal\", \"value\": \"OSLO    T1\"}}]}}",
    "output_media_type": "application/sparql-results+json",
    "required_columns": ["transformer", "transformerName"],
    "ordered": False,
}
sparkle_actual_step = {
    "name": "sparql_query",
    "args": {
        "query": "SELECT ?transformer ?transformerName WHERE {\n  ?transformer a cim:PowerTransformer ;\n               cim:Equipment.EquipmentContainer <urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> ;\n               cim:IdentifiedObject.name ?transformerName .\n}"
    },
    "id": "call_3b3zHJnBXwYYSg04BiFGAAgO",
    "status": "success",
    "output": "{\n  \"head\": {\n    \"vars\": [\n      \"transformer\",\n      \"transformerName\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"transformer\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"transformerName\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO    T2\"\n        }\n      },\n      {\n        \"transformer\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"transformerName\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO    T1\"\n        }\n      }\n    ]\n  }\n}"
}
influx_expected_step = {
    "name": "influx_query",
    "args": {
        "query": """
        from(bucket: "example_bucket")
|> range(start: -1h)
|> filter(fn: (r) => r._measurement == "temperature_data")
|> filter(fn: (r) => r.sensor == "sensor1")"""
    },
    "output": "{\"results\": [{\"series\": [{\"name\": \"temperature_data\", \"tags\": {\"sensor\": \"sensor1\", \"location\": \"warehouse\"}, \"columns\": [\"time\", \"_value\", \"_field\", \"_measurement\"], \"values\": [[\"2025-05-22T12:00:00Z\", 22.5, \"temperature\", \"temperature_data\"], [\"2025-05-22T12:05:00Z\", 22.7, \"temperature\", \"temperature_data\"], [\"2025-05-22T12:10:00Z\", 22.9, \"temperature\", \"temperature_data\"]]}]}]}",
    "output_media_type": "application/json",
}
influx_actual_step = {
    "name": "influx_query",
    "args": {
        "query": """
        from(bucket: "example_bucket")
|> range(start: -1h)
|> filter(fn: (r) => r._measurement == "temperature_data")
|> filter(fn: (r) => r.sensor == "sensor1")"""
    },
    "id": "call_3b3zHJnBXwYYSg04BiFGAAgO",
    "status": "success",
    "output": "{\"results\": [{\"series\": [{\"name\": \"temperature_data\", \"tags\": {\"sensor\": \"sensor1\", \"location\": \"warehouse\"}, \"values\": [[\"2025-05-22T12:00:00Z\", 22.5, \"temperature\", \"temperature_data\"], [\"2025-05-22T12:05:00Z\", 22.7, \"temperature\", \"temperature_data\"], [\"2025-05-22T12:10:00Z\", 22.9, \"temperature\", \"temperature_data\"]], \"columns\": [\"time\", \"_value\", \"_field\", \"_measurement\"]}]}]}"
}
calculation_expected_step = {
    "name": "calculation",
    "args": {
        "x": 5, "y": 10
    },
    "output": 15,
}
calculation_actual_step = {
    "name": "calculation",
    "args": {
        "y": 6, "x": 10
    },
    "id": "call_4",
    "status": "success",
    "output": 16
}
concatenation_expected_step = {
    "name": "concatenation",
    "args": {
        "x": "5", "y": "10"
    },
    "output": "510",
}
concatenation_actual_step = {
    "name": "concatenation",
    "args": {
        "x": "10", "y": "5"
    },
    "id": "call_4",
    "status": "success",
    "output": "105",
}
retrieval_expected_step = {
    "name": "retrieval",
    "args": {
        "question": "Why is the sky blue?",
        "k": 5
    },
    "output": [1, 3, 5, 7, 9],
}
retrieval_actual_step = {
    "name": "retrieval",
    "args": {
        "question": "Why is the sky blue?",
        "k": 5
    },
    "id": "call_4",
    "status": "success",
    "output": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
}
retrieval_error_step = {
    "name": "retrieval",
    "args": {
        "question": "Why is the sky blue?",
        "k": 5
    },
    "id": "call_4",
    "status": "error",
    "error": "oops",
}


def test_compare_outputs_sparql_results():
    assert compare_steps_outputs(sparkle_expected_step, sparkle_actual_step) == 1.0


def test_compare_outputs_json():
    assert compare_steps_outputs(influx_expected_step, influx_actual_step) == 1.0


def test_compare_outputs_numbers():
    assert compare_steps_outputs(calculation_expected_step, calculation_expected_step) == 1.0
    assert compare_steps_outputs(calculation_expected_step, calculation_actual_step) == 0.0


def test_compare_outputs_strings():
    assert compare_steps_outputs(concatenation_expected_step, concatenation_expected_step) == 1.0
    assert compare_steps_outputs(concatenation_expected_step, concatenation_actual_step) == 0.0


def test_retrieval_evaluation():
    assert compare_steps_outputs(retrieval_expected_step, retrieval_expected_step) == 1.0
    assert compare_steps_outputs(retrieval_expected_step, retrieval_actual_step) == 0.6


def test_match_group_by_output():
    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1"},
            {"name": "step_a", "output": "result_a_2"},
        ],
        [
            {"name": "step_b", "output": "result_b"},
        ]
    ]
    actual_steps = [
        {"name": "step_a", "output": "result_a_1"},
        {"name": "step_b", "output": "result_b"},
    ]
    matches = match_group_by_output(expected_steps, -1, actual_steps, {"step_b": [1]})
    assert matches == [(-1, 0, 1, 1.0)]

    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1"},
            {"name": "step_a", "output": "result_a_2"},
        ],
        [
            {"name": "step_b", "output": "result_b"},
            {"name": "step_b", "output": "result_b"},
        ]
    ]
    actual_steps = [
        {"name": "step_a", "output": "result_a"},
        {"name": "step_b", "output": "result_b"},
    ]
    matches = match_group_by_output(expected_steps, -1, actual_steps, {"step_b": [1]})
    assert matches == [(-1, 0, 1, 1.0)]

    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1"},
            {"name": "step_a", "output": "result_a_2"},
        ],
        [
            {"name": "step_b", "output": "result_b_1"},
            {"name": "step_b", "output": "result_b_2"},
        ]
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_2"},
        {"name": "step_a", "output": "result_a"},
        {"name": "step_b", "output": "result_b_1"},
    ]
    matches = match_group_by_output(expected_steps, -1, actual_steps, {"step_b": [0, 2]})
    assert matches == [(-1, 0, 2, 1.0), (-1, 1, 0, 1.0)]


def test_collect_possible_matches_by_name():
    expected_steps = [
        {"name": "step_b", "output": "result_b_1", "status": "success"},
        {"name": "step_b", "output": "result_b_2", "status": "success"},
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_2", "status": "success"},
        {"name": "step_a", "output": "result_a", "status": "success"},
        {"name": "step_b", "output": "result_b_1", "status": "success"},
    ]
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 2) == {"step_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, len(actual_steps)) == {
        "step_b": [0, 2]}

    expected_steps = [
        {"name": "step_b", "output": "result_b_1", "status": "success"},
        {"name": "step_b", "output": "result_b_2", "status": "success"},
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_2", "status": "success"},
        {"name": "step_b", "error": "error", "status": "error"},
        {"name": "step_a", "output": "result_a", "status": "success"},
        {"name": "step_b", "output": "result_b_1", "status": "success"},
    ]
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 0) == {}
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 1) == {"step_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 2) == {"step_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 3) == {"step_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_steps, actual_steps, 4) == {"step_b": [0, 3]}


def test_get_steps_matches():
    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_1", "status": "success"},
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_2", "status": "success"},
        {"name": "step_b", "error": "error", "status": "error"},
        {"name": "step_a", "output": "result_a", "status": "success"},
        {"name": "step_b", "output": "result_b_1", "status": "success"},
    ]
    matches = get_steps_matches(expected_steps, actual_steps)
    assert matches == [(-1, 0, 3, 1.0), (-1, 1, 0, 1.0)]


def test_evaluate_steps_groups():
    expected_groups = [
        [sparkle_expected_step],
        [retrieval_expected_step],
    ]
    actual_steps = [retrieval_actual_step, sparkle_actual_step]
    assert evaluate_steps(expected_groups, actual_steps) == 0.6
    assert evaluate_steps(expected_groups, [retrieval_actual_step]) == 0.6
    assert evaluate_steps(expected_groups, [sparkle_actual_step]) == 0.0
    assert evaluate_steps(expected_groups, list(reversed(actual_steps))) == 0.6
    assert evaluate_steps(expected_groups, [calculation_actual_step]) == 0.0
    assert evaluate_steps(expected_groups, [retrieval_error_step]) == 0.0
    assert evaluate_steps(expected_groups, []) == 0.0


def test_evaluate_steps_last_group():
    expected_groups = [
        [sparkle_expected_step, retrieval_expected_step]
    ]
    actual_steps = [retrieval_actual_step, sparkle_actual_step]
    assert evaluate_steps(expected_groups, actual_steps) == 0.8
    assert evaluate_steps(expected_groups, [retrieval_actual_step]) == 0.3
    assert evaluate_steps(expected_groups, [sparkle_actual_step]) == 0.5
    assert evaluate_steps(expected_groups, list(reversed(actual_steps))) == 0.8
    assert evaluate_steps(expected_groups, [calculation_actual_step]) == 0.0
    assert evaluate_steps(expected_groups, [retrieval_error_step]) == 0.0
    assert evaluate_steps(expected_groups, []) == 0.0
