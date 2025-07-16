from ttyg_evaluation import (
    compare_tools_outputs,
    match_group_by_output,
    collect_possible_matches_by_name_and_status,
    get_tools_calls_matches
)


def test_compare_outputs_sparql_results():
    expected_tool = {
        "name": "sparql_query",
        "args": {
            "query": "\nPREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>\nPREFIX cim: <https://cim.ucaiug.io/ns#>\nPREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nselect distinct ?transformer ?transformerName\nwhere {\n    bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)\n\n    ?transformer a cim:PowerTransformer ;\n      cim:Equipment.EquipmentContainer ?substation ;\n      cim:IdentifiedObject.name ?transformerName .\n}\n"
        },
        "output": "{\"head\": {\"vars\": [\"transformer\", \"transformerName\"]}, \"results\": {\"bindings\": [{\"transformer\": {\"type\": \"uri\", \"value\": \"urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f\"}, \"transformerName\": {\"type\": \"literal\", \"value\": \"OSLO    T2\"}}, {\"transformer\": {\"type\": \"uri\", \"value\": \"urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f\"}, \"transformerName\": {\"type\": \"literal\", \"value\": \"OSLO    T1\"}}]}}",
        "output_media_type": "application/sparql-results+json",
        "required_columns": ["transformer", "transformerName"],
        "ordered": False,
    }
    actual_tool = {
        "name": "sparql_query",
        "args": {
            "query": "SELECT ?transformer ?transformerName WHERE {\n  ?transformer a cim:PowerTransformer ;\n               cim:Equipment.EquipmentContainer <urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> ;\n               cim:IdentifiedObject.name ?transformerName .\n}"
        },
        "id": "call_3b3zHJnBXwYYSg04BiFGAAgO",
        "status": "success",
        "output": "{\n  \"head\": {\n    \"vars\": [\n      \"transformer\",\n      \"transformerName\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"transformer\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"transformerName\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO    T2\"\n        }\n      },\n      {\n        \"transformer\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"transformerName\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO    T1\"\n        }\n      }\n    ]\n  }\n}"
    }

    assert compare_tools_outputs(expected_tool, actual_tool) == True


def test_compare_outputs_json():
    expected_tool = {
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
    actual_tool = {
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

    assert compare_tools_outputs(expected_tool, actual_tool) == True


def test_compare_outputs_numbers():
    expected_tool = {
        "name": "calculator",
        "args": {
            "x": 5, "y": 10
        },
        "output": 15,
    }
    actual_tool = {
        "name": "calculator",
        "args": {
            "y": 5, "x": 10
        },
        "id": "call_4",
        "status": "success",
        "output": 15
    }
    assert compare_tools_outputs(expected_tool, actual_tool) == True

    expected_tool = {
        "name": "calculator",
        "args": {
            "x": 5, "y": 10
        },
        "output": 15,
    }
    actual_tool = {
        "name": "calculator",
        "args": {
            "y": 6, "x": 10
        },
        "id": "call_4",
        "status": "success",
        "output": 16
    }
    assert compare_tools_outputs(expected_tool, actual_tool) == False


def test_compare_outputs_strings():
    expected_tool = {
        "name": "concatenate",
        "args": {
            "x": "5", "y": "10"
        },
        "output": "510",
    }
    actual_tool = {
        "name": "concatenate",
        "args": {
            "x": "5", "y": "10"
        },
        "id": "call_4",
        "status": "success",
        "output": "510",
    }
    assert compare_tools_outputs(expected_tool, actual_tool) == True

    expected_tool = {
        "name": "concatenate",
        "args": {
            "x": "5", "y": "10"
        },
        "output": "510",
    }
    actual_tool = {
        "name": "concatenate",
        "args": {
            "x": "10", "y": "5"
        },
        "id": "call_4",
        "status": "success",
        "output": "105",
    }
    assert compare_tools_outputs(expected_tool, actual_tool) == False


def test_match_group_by_output():
    expected_calls = [
        [
            {"name": "tool_a", "output": "result_a_1"},
            {"name": "tool_a", "output": "result_a_2"},
        ],
        [
            {"name": "tool_b", "output": "result_b"},
        ]
    ]
    actual_calls = [
        {"name": "tool_a", "output": "result_a_1"},
        {"name": "tool_b", "output": "result_b"},
    ]
    assert match_group_by_output(expected_calls, -1, actual_calls, {"tool_b": [1]}) == [((-1, 0), 1)]

    expected_calls = [
        [
            {"name": "tool_a", "output": "result_a_1"},
            {"name": "tool_a", "output": "result_a_2"},
        ],
        [
            {"name": "tool_b", "output": "result_b"},
            {"name": "tool_b", "output": "result_b"},
        ]
    ]
    actual_calls = [
        {"name": "tool_a", "output": "result_a"},
        {"name": "tool_b", "output": "result_b"},
    ]
    assert match_group_by_output(expected_calls, -1, actual_calls, {"tool_b": [1]}) == [((-1, 0), 1)]

    expected_calls = [
        [
            {"name": "tool_a", "output": "result_a_1"},
            {"name": "tool_a", "output": "result_a_2"},
        ],
        [
            {"name": "tool_b", "output": "result_b_1"},
            {"name": "tool_b", "output": "result_b_2"},
        ]
    ]
    actual_calls = [
        {"name": "tool_b", "output": "result_b_2"},
        {"name": "tool_a", "output": "result_a"},
        {"name": "tool_b", "output": "result_b_1"},
    ]
    assert match_group_by_output(expected_calls, -1, actual_calls, {"tool_b": [0, 2]}) == [
        ((-1, 0), 2), ((-1, 1), 0)
    ]


def test_collect_possible_matches_by_name():
    expected_calls = [
        {"name": "tool_b", "output": "result_b_1", "status": "success"},
        {"name": "tool_b", "output": "result_b_2", "status": "success"},
    ]
    actual_calls = [
        {"name": "tool_b", "output": "result_b_2", "status": "success"},
        {"name": "tool_a", "output": "result_a", "status": "success"},
        {"name": "tool_b", "output": "result_b_1", "status": "success"},
    ]
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 2) == {"tool_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, len(actual_calls)) == {
        "tool_b": [0, 2]}

    expected_calls = [
        {"name": "tool_b", "output": "result_b_1", "status": "success"},
        {"name": "tool_b", "output": "result_b_2", "status": "success"},
    ]
    actual_calls = [
        {"name": "tool_b", "output": "result_b_2", "status": "success"},
        {"name": "tool_b", "error": "error", "status": "error"},
        {"name": "tool_a", "output": "result_a", "status": "success"},
        {"name": "tool_b", "output": "result_b_1", "status": "success"},
    ]
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 0) == {}
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 1) == {"tool_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 2) == {"tool_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 3) == {"tool_b": [0]}
    assert collect_possible_matches_by_name_and_status(expected_calls, actual_calls, 4) == {"tool_b": [0, 3]}


def test_get_tools_calls_matches():
    expected_calls = [
        [
            {"name": "tool_a", "output": "result_a_1", "status": "success"},
            {"name": "tool_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "tool_b", "output": "result_b_1", "status": "success"},
            {"name": "tool_b", "output": "result_b_2", "status": "success"},
        ]
    ]
    actual_calls = [
        {"name": "tool_b", "output": "result_b_2", "status": "success"},
        {"name": "tool_b", "error": "error", "status": "error"},
        {"name": "tool_a", "output": "result_a", "status": "success"},
        {"name": "tool_b", "output": "result_b_1", "status": "success"},
    ]

    assert get_tools_calls_matches(expected_calls, actual_calls) == [((-1, 0), 3), ((-1, 1), 0)]
