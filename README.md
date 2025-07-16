<p align="center">
  <img alt="Graphwise Logo" src=".github/Graphwise_Logo.jpg">
</p>

# Talk to Your Graph (TTYG) Evaluation

TTYG Evaluation is a Python module for evaluating whether LLM agents correctly orchestrate and invoke available
tools to answer user questions, based on a gold-standard corpus of tool call expectations.

## License

Apache-2.0 License. See [LICENSE](LICENSE) file for details.

## Installation

```bash
pip install ttyg-evaluation
```

## Maintainers

Developed and maintained by [Graphwise](https://graphwise.ai/).
For issues or feature requests, please open [a GitHub issue](https://github.com/Ontotext-AD/ttyg-evaluation/issues).

## Usage

To use this module you must provide a gold standard corpus that defines questions and expected tool calls for each question.

### Gold Standard Format

A gold standard corpus is a list of templates. Each template contains:

- `template_id` – Unique template identifier
- `questions` – A list of questions derived from this template, where each includes:
  - `id` – Unique question identifier
  - `question_text` – The natural language query passed to the LLM
  - `reference_steps` – A list of expected steps / tool calls grouped by *level*.
The assumption is that the final answer to the question is derived from the outputs of the tools, which are called last (last level).

Each tool call includes:

- `name` – The tool being called (e.g., `sparql_query`)
- `args` – Arguments passed to the tool (e.g., SPARQL query)
- `output` – The expected output from the tool
- `output_media_type` – (optional, missing or one of `application/sparql-results+json`, `application/json`) - Indicates how the output of a tool must be processed
- `ordered` – (optional, defaults to `false`) - only applicable for SPARQL query results, whether the order of the results matters.
`false` means that the results are not ordered, hence for comparison we can re-order them.
`true` means the results order matters and in order to match the order must be preserved.
- `required_columns`– (optional) - required only for SPARQL query results; list of binding names, which are required for SPARQL query results to match

#### Example Corpus

The example corpus below illustrates a minimal but realistic gold standard, showing two templates with associated questions and tool calls.

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  questions:
  - id: c10bbc8dce98a4b8832d125134a16153
    question_text: List all transformers within Substation OSLO
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?transformer ?transformerName
            where {
                bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)

                ?transformer a cim:PowerTransformer ;
                  cim:Equipment.EquipmentContainer ?substation ;
                  cim:IdentifiedObject.name ?transformerName .
            }
        output: '{"head": {"vars": ["transformer", "transformerName"]}, "results":
          {"bindings": [{"transformer": {"type": "uri", "value": "urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "OSLO    T2"}}, {"transformer":
          {"type": "uri", "value": "urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "OSLO    T1"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - transformer
          - transformerName
  - id: 8bbea9a10876a04ad77a82fd2aedee40
    question_text: List all transformers within Substation STAVANGER
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?transformer ?transformerName
            where {
                bind(<urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f> as ?substation)

                ?transformer a cim:PowerTransformer ;
                  cim:Equipment.EquipmentContainer ?substation ;
                  cim:IdentifiedObject.name ?transformerName .
            }
        output: '{"head": {"vars": ["transformer", "transformerName"]}, "results":
          {"bindings": [{"transformer": {"type": "uri", "value": "urn:uuid:f1769e0c-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "STAVANGET1"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - transformer
          - transformerName
- template_id: list_all_substations_within_bidding_zone_REGION
  questions:
  - id: d566b1e9da418ac83e520a66cc7af4d7
    question_text: List all substations within bidding zone NO2 SGR
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?substation ?substationName
            where {
                bind(<urn:uuid:f176965f-9aeb-11e5-91da-b8763fd99c5f> as ?region)

                ?substation a cim:Substation ;
                  cim:Substation.Region ?region ;
                  cim:IdentifiedObject.name ?substationName .
            }
        output: '{"head": {"vars": ["substation", "substationName"]}, "results": {"bindings":
          [{"substation": {"type": "uri", "value": "urn:uuid:f1769670-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "ARENDAL"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176968e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "BLAFALLI"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "STAVANGER"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769676-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KRISTIA_HVDC"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KVILLDAL"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176966a-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SANDEFJORD"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176965a-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KRISTIANSAND"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176967c-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "FEDA_HVDC"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - substation
          - substationName
        ordered: false
  - id: 03d4283773b4387114342518176b128b
    question_text: List all substations within bidding zone NO1 SGR
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?substation ?substationName
            where {
                bind(<urn:uuid:f1769609-9aeb-11e5-91da-b8763fd99c5f> as ?region)

                ?substation a cim:Substation ;
                  cim:Substation.Region ?region ;
                  cim:IdentifiedObject.name ?substationName .
            }
        output: '{"head": {"vars": ["substation", "substationName"]}, "results": {"bindings":
          [{"substation": {"type": "uri", "value": "urn:uuid:f176960e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "HALDEN"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176961e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KONGSBERG"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769642-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SYLLING"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "OSLO"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176964e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "ASKER"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769648-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SYSLE"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769654-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SKIEN"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769604-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "TRETTEN"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - substation
          - substationName
        ordered: false
```

The module is agnostic to the specific LLM agent implementation and model; it depends solely on the format of the response.
Below is a sample response from the LLM agent for a single question:

```json
{
    "question_id": "f91fc938d606e5f6089912bebfaf114b",
    "input_tokens": 298028,
    "output_tokens": 725,
    "total_tokens": 298753,
    "elapsed_sec": 46.48961806297302,
    "actual_steps": [
        {
            "name": "autocomplete_search",
            "args": {
                "query": "STAVANGER",
                "result_class": "cim:Substation"
            },
            "id": "call_7amIsfEGelOnVZ1DWtgtc0hc",
            "status": "success",
            "output": "{\n  \"head\": {\n    \"vars\": [\n      \"iri\",\n      \"name\",\n      \"rank\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"iri\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"name\": {\n          \"type\": \"literal\",\n          \"value\": \"STAVANGER\"\n        },\n        \"rank\": {\n          \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\",\n          \"type\": \"literal\",\n          \"value\": \"0.00976\"\n        }\n      }\n    ]\n  }\n}"
        },
        {
            "name": "sparql_query",
            "args": {
                "query": "SELECT DISTINCT ?substation2 ?substation2Name ?line ?lineName WHERE {\n  # Substation STAVANGER\n  BIND(urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f AS ?substation1) .\n\n  # Find lines connected to STAVANGER\n  ?line a cim:Line ;\n        cimex:connectedThroughPart ?substation1, ?substation2 ;\n        cim:IdentifiedObject.name ?lineName .\n\n  # Ensure the connected substation is different from STAVANGER\n  ?substation2 a cim:Substation ;\n               cim:IdentifiedObject.name ?substation2Name .\n  FILTER(?substation1 != ?substation2)\n}"
            },
            "id": "call_DbMkZ8kv3qkf49wNNdREkpRN",
            "status": "error",
            "error": "Error: ValueError('The following prefixes are undefined: urn')\n Please fix your mistakes."
        },
        {
            "name": "sparql_query",
            "args": {
                "query": "SELECT DISTINCT ?substation2 ?substation2Name ?line ?lineName WHERE {\n  # Substation STAVANGER\n  BIND(<urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f> AS ?substation1) .\n\n  # Find lines connected to STAVANGER\n  ?line a cim:Line ;\n        cimex:connectedThroughPart ?substation1, ?substation2 ;\n        cim:IdentifiedObject.name ?lineName .\n\n  # Ensure the connected substation is different from STAVANGER\n  ?substation2 a cim:Substation ;\n               cim:IdentifiedObject.name ?substation2Name .\n  FILTER(?substation1 != ?substation2)\n}"
            },
            "id": "call_Qm1mzX7g5q9SVPrR2QzEMTp3",
            "status": "success",
            "output": "{\n  \"head\": {\n    \"vars\": [\n      \"substation2\",\n      \"substation2Name\",\n      \"line\",\n      \"lineName\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176965a-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KRISTIANSAND\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:47332c85-17a4-7a41-abd5-2b92e4b800ed\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 300KRISTIAN-STAVANGE\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769614-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"DAGALI\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769648-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SYSLE\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176962a-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"AURLAND\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769624-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SIMA\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769642-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SYLLING\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      }\n    ]\n  }\n}"
        }
    ],
    "actual_answer": "The substations connected to the substation \"STAVANGER\" via AC or DC lines are:\n\n1. **KRISTIANSAND** via line \"LC 300KRISTIAN-STAVANGE\"\n2. **DAGALI** via line \"LC 420DAGALI-HAGAFOSS\"\n3. **KVILLDAL** via lines:\n   - \"LC 420DAGALI-HAGAFOSS\"\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420AURLAND-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n4. **HAGAFOSS** via lines:\n   - \"LC 420DAGALI-HAGAFOSS\"\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420AURLAND-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n5. **OSLO** via lines:\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n6. **SYSLE** via line \"LC 420SYSLE-HAGAFOSS\"\n7. **AURLAND** via line \"LC 420AURLAND-HAGAFOSS\"\n8. **SIMA** via line \"LC 420AURLAND-HAGAFOSS\"\n9. **SYLLING** via line \"LC 420SYLLING-HAGAFOSS\""
}
```

If an error occurs, the expected response format is:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "error": "Error message",
    "status": "error"
}
```

Sample code:

```python
from ttyg_evaluation import run_evaluation, compute_aggregations

sample_gold_standard: list[dict] = [] # read your corpus
chat_responses: dict = {} # call your implementation to get the response
evaluation_results = run_evaluation(sample_gold_standard, chat_responses)
aggregates = compute_aggregations(evaluation_results)
```

`evaluation_results` is a list in which for each question from the gold standard corpus we have for example

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  question_id: c10bbc8dce98a4b8832d125134a16153
  question_text: List all transformers within Substation OSLO
  reference_steps:
  - - name: sparql_query
      args:
        query: |2

          PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
          PREFIX cim: <https://cim.ucaiug.io/ns#>
          PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
          PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
          select distinct ?transformer ?transformerName
          where {
              bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)

              ?transformer a cim:PowerTransformer ;
                cim:Equipment.EquipmentContainer ?substation ;
                cim:IdentifiedObject.name ?transformerName .
          }
      output: '{"head": {"vars": ["transformer", "transformerName"]}, "results": {"bindings":
        [{"transformer": {"type": "uri", "value": "urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f"},
        "transformerName": {"type": "literal", "value": "OSLO    T2"}}, {"transformer":
        {"type": "uri", "value": "urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f"},
        "transformerName": {"type": "literal", "value": "OSLO    T1"}}]}}'
      output_media_type: application/sparql-results+json
      required_columns:
        - transformer
        - transformerName
      matches: call_3b3zHJnBXwYYSg04BiFGAAgO
  actual_answer: |-
    The following transformers are located within the Substation OSLO:

    1. **OSLO T2** (IRI: `urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f`)
    2. **OSLO T1** (IRI: `urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f`)
  actual_steps:
  - name: autocomplete_search
    args:
      query: OSLO
      result_class: cim:Substation
    id: call_3wIrBHIsInzAWzo8qwwYAkDD
    status: success
    output: |-
      {
        "head": {
          "vars": [
            "iri",
            "name",
            "rank"
          ]
        },
        "results": {
          "bindings": [
            {
              "iri": {
                "type": "uri",
                "value": "urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f"
              },
              "name": {
                "type": "literal",
                "value": "OSLO"
              },
              "rank": {
                "datatype": "http://www.w3.org/2001/XMLSchema#float",
                "type": "literal",
                "value": "0.01185"
              }
            }
          ]
        }
      }
  - name: sparql_query
    args:
      query: |-
        SELECT ?transformer ?transformerName WHERE {
          ?transformer a cim:PowerTransformer ;
                       cim:Equipment.EquipmentContainer <urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> ;
                       cim:IdentifiedObject.name ?transformerName .
        }
    id: call_3b3zHJnBXwYYSg04BiFGAAgO
    status: success
    output: |-
      {
        "head": {
          "vars": [
            "transformer",
            "transformerName"
          ]
        },
        "results": {
          "bindings": [
            {
              "transformer": {
                "type": "uri",
                "value": "urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f"
              },
              "transformerName": {
                "type": "literal",
                "value": "OSLO    T2"
              }
            },
            {
              "transformer": {
                "type": "uri",
                "value": "urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f"
              },
              "transformerName": {
                "type": "literal",
                "value": "OSLO    T1"
              }
            }
          ]
        }
      }
  answer_score: 1
  input_tokens: 221339
  output_tokens: 212
  total_tokens: 221551
  elapsed_sec: 6.601679801940918
```

- `template_id` - the template id
- `question_id` - the question id
- `question_text` - the natural language query
- `reference_steps` - the expected tools calls as in the gold standard
- `actual_answer` - the LLM natural language answer
- `actual_steps` - the actual tools calls by the LLM agent
- `answer_score` - a real number between 0 and 1. It's calculated by comparing the results of the last tools calls, which are expected.
If there is no match in the actual tools calls, then the score will be `0`.
Otherwise, it's calculated as the number of the matched tools calls on the last step divided by the total tools calls from the last step.
- `input_tokens` - input tokens usage
- `output_tokens` - output tokens usage
- `total_tokens` - total tokens usage
- `elapsed_sec` - elapsed seconds

The `aggregates` object provides aggregated evaluation metrics.
Aggregations are computed both per-template and overall, using micro and macro averaging strategies.
These aggregations support analysis of agent quality, token efficiency, and execution performance.
Aggregations include:

- `per_template` - a dictionary where each key is a template identifier. For each template, the following statistics are reported:
  - `number_of_error_samples` - number of questions for this template, which resulted in error response
  - `number_of_success_samples` - number of questions for this template, which resulted in successful response
  - `input_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `input_tokens` of all successful questions for this template
  - `output_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `output_tokens` of all successful questions for this template
  - `total_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `total_tokens` of all successful questions for this template
  - `elapsed_sec` - `sum`, `mean`, `median`, `min` and `max` statistics for `elapsed_sec` of all successful questions for this template
  - `answer_score` - `sum`, `mean`, `median`, `min` and `max` statistics for `answer_score` of all successful questions for this template
  - `tools_calls` - statistics for the `tools_calls` for of all successful questions for this template. Includes:
    - `total_calls` - for each tool how many times it was called
    - `once_per_sample` - how many times each tool was called, but counted only once per question
    - `empty_results` - how many times the tool was called, but it returned empty results
    - `error_calls` - how many times the tool was called and this resulted in error
- `micro` - micro gives overall aggregate statistics across questions, treating each equally. It includes:
  - `number_of_error_samples` - total number of questions, which resulted in error response
  - `number_of_success_samples` - total number of questions, which resulted in successful response
  - `input_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `input_tokens` of all successful questions
  - `output_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `output_tokens` of all successful questions
  - `total_tokens` - `sum`, `mean`, `median`, `min` and `max` statistics for `total_tokens` of all successful questions
  - `elapsed_sec` - `sum`, `mean`, `median`, `min` and `max` statistics for `elapsed_sec` of all successful questions
  - `answer_score` - `sum`, `mean`, `median`, `min` and `max` statistics for `answer_score` of all successful questions
- `macro` - macro gives averages across templates, i.e., it computes the mean of each metric per template, then averages those means. It includes:
  - `input_tokens` - `mean` for `input_tokens`
  - `output_tokens` - `mean` for `output_tokens`
  - `total_tokens` - `mean` for `total_tokens`
  - `elapsed_sec` - `mean` for `elapsed_sec`
  - `answer_score` - `mean` for `answer_score`

Example aggregations:

```yaml
per_template:
  list_all_transformers_within_Substation_SUBSTATION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    tools_calls:
      total_calls:
        autocomplete_search: 10
        sparql_query: 8
      once_per_sample:
        autocomplete_search: 10
        sparql_query: 8
      empty_results:
        autocomplete_search: 2
    answer_score:
      sum: 8
      mean: 0.8
      median: 1
      min: 0
      max: 1
    input_tokens:
      sum: 2064559
      mean: 206455.9
      median: 221263.5
      min: 147171
      max: 221339
    output_tokens:
      sum: 1555
      mean: 155.5
      median: 177
      min: 46
      max: 212
    total_tokens:
      sum: 2066114
      mean: 206611.4
      median: 221439.5
      min: 147217
      max: 221551
    elapsed_sec:
      sum: 259.2278094291687
      mean: 25.92278094291687
      median: 9.677194952964783
      min: 5.529741525650024
      max: 55.4010910987854
  list_all_substations_within_bidding_zone_REGION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    tools_calls:
      total_calls:
        autocomplete_search: 10
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 10
    answer_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1471880
      mean: 147188
      median: 147188
      min: 147188
      max: 147188
    output_tokens:
      sum: 571
      mean: 57.1
      median: 57
      min: 56
      max: 61
    total_tokens:
      sum: 1472451
      mean: 147245.1
      median: 147245
      min: 147244
      max: 147249
    elapsed_sec:
      sum: 185.5483124256134
      mean: 18.55483124256134
      median: 8.886059165000916
      min: 2.8653159141540527
      max: 47.51542258262634
  list_all_substations_that_are_connected_via_an_ac_line_or_a_dc_line_to_substation_named_SUBSTATION:
    number_of_error_samples: 1
    number_of_success_samples: 9
    tools_calls:
      total_calls:
        autocomplete_search: 9
        sparql_query: 17
      once_per_sample:
        autocomplete_search: 9
        sparql_query: 9
      error_calls:
        sparql_query: 8
    answer_score:
      sum: 9
      mean: 1
      median: 1
      min: 1
      max: 1
    input_tokens:
      sum: 2601595
      mean: 289066.1111111111
      median: 297059
      min: 222528
      max: 298028
    output_tokens:
      sum: 6066
      mean: 674
      median: 700
      min: 363
      max: 805
    total_tokens:
      sum: 2607661
      mean: 289740.1111111111
      median: 297759
      min: 222891
      max: 298787
    elapsed_sec:
      sum: 354.82168316841125
      mean: 39.42463146315681
      median: 41.88556528091431
      min: 26.418761014938354
      max: 52.42662525177002
  list_all_ac_lines_that_traverse_bidding_zones_REGION1_and_REGION2:
    number_of_error_samples: 0
    number_of_success_samples: 10
    tools_calls:
      total_calls:
        autocomplete_search: 20
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 20
    answer_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1472540
      mean: 147254
      median: 147254
      min: 147254
      max: 147254
    output_tokens:
      sum: 1052
      mean: 105.2
      median: 105
      min: 105
      max: 107
    total_tokens:
      sum: 1473592
      mean: 147359.2
      median: 147359
      min: 147359
      max: 147361
    elapsed_sec:
      sum: 197.44370341300964
      mean: 19.744370341300964
      median: 18.030158162117004
      min: 15.56333041191101
      max: 26.422670125961304
micro:
  number_of_error_samples: 1
  number_of_success_samples: 39
  answer_score:
    sum: 17
    mean: 0.4358974358974359
    median: 0
    min: 0
    max: 1
  input_tokens:
    sum: 7610574
    mean: 195142.92307692306
    median: 147254
    min: 147171
    max: 298028
  output_tokens:
    sum: 9244
    mean: 237.02564102564102
    median: 105
    min: 46
    max: 805
  total_tokens:
    sum: 7619818
    mean: 195379.94871794872
    median: 147359
    min: 147217
    max: 298787
  elapsed_sec:
    sum: 997.041508436203
    mean: 25.565166882979565
    median: 18.32871961593628
    min: 2.8653159141540527
    max: 55.4010910987854
macro:
  answer_score:
    mean: 0.45
  input_tokens:
    mean: 197491.0027777778
  output_tokens:
    mean: 247.95
  total_tokens:
    mean: 197738.9527777778
  elapsed_sec:
    mean: 25.911653497483996
```
