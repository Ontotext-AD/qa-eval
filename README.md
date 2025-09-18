<p align="center">
  <img alt="Graphwise Logo" src=".github/Graphwise_Logo.jpg">
</p>

# QA Evaluation

This is a Python module for assessing the quality of question-answering systems such as ones based on LLM agents, based on a set of questions and reference answers for them. This includes evaluating the final answer and the steps used
to reach the answer (such as orchestrated and executed steps), compared to the given reference steps.

## License

Apache-2.0 License. See [LICENSE](LICENSE) file for details.

## Installation

To evaluate only steps:
```bash
pip install qa-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
qa-eval = "*"
```

To evaluate answer relevance and answer correctness:

```bash
pip install 'qa-eval[openai]'
```

or add the following dependency in your `pyproject.toml` file:
```toml
qa-eval = {version = "*", extras = ["openai"]}
```

## Maintainers

Developed and maintained by [Graphwise](https://graphwise.ai/).
For issues or feature requests, please open [a GitHub issue](https://github.com/Ontotext-AD/qa-eval/issues).

## Command Line Use

To evaluate only correctness of final answers (system responses), you can clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
1. Execute `poetry install --with openai`
1. Execute `OPENAI_API_KEY=<your_api_key> poetry run answer-correctness -i <input_file.tsv> -o <output_file.tsv>`

We plan to improve CLI support in future releases.

## Use as a Library

To evaluate answers and/or steps:
1. Install this package: section [Install](#Installation)
1. Format the corpus of questions and reference answers and/or steps: section [Reference Q&A Corpus](#reference-qa-corpus)
1. Format the answers and/or steps you want to evaluate: section [Evaluation Target Corpus](#Evaluation-Target-Corpus)
1. To evaluate answer relevance:
    1. Include `actual_answer` in the target data to evaluate
    1. Set environment vairabe `OPENAI_API_KEY` appropriately
1. To evaluate answer correctness:
    1. Include `reference_answer` in the reference corpus and `actual_answer` in the target data to evaluate
    1. Set environment variable `OPENAI_API_KEY` appropriately
1. To evaluate steps:
    1. Include `reference_steps` in the reference corpus and `actual_steps` in target data to evaluate
1. Call the evaluation function with the reference corpus and target corpus: section [Example Usage Code](#Example-Usage-Code)
1. Call the aggregation function with the evaluation results

Answer evaluation (correctness and relevance) uses the LLM `openai/gpt-4o-mini`.

### Reference Q&A Corpus

A reference corpus is a list of templates, each of which contains:

- `template_id`: Unique template identifier
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier
  - `question_text`: The natural language query passed to the LLM
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution, where all steps in a group can be executed in any order relative to each other, but after all steps in the previous group and before all steps in the next group.
  - `reference_answer`: (optional) The expected answer to the question

The assumption is that the final answer to the question is derived from the outputs of the steps, which are executed last (last level).

Each step includes:

- `name`: The type of step being performed (e.g., `sparql_query`)
- `args`: Arguments of the step (e.g., arguments to a tool used in the step, such as a SPARQL query)
- `output`: (optional) The expected output from the step. Optional for steps whose `name` is `"retrieval"`
- `output_media_type`: (optional, missing or one of `application/sparql-results+json`, `application/json`) Indicates how the output of a step must be processed
- `ordered`: (optional, defaults to `false`) For SPARQL query results, whether results order matters. `true` means that the actual result rows must be ordered as the reference result; `false` means that result rows are matched as a set.
- `required_columns`: (optional) - required only for SPARQL query results; list of binding names, which are required for SPARQL query results to match

#### Example Reference Corpus

The example corpus below illustrates a minimal but realistic Q&A dataset, showing two templates with associated questions and steps.

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  questions:
  - id: c10bbc8dce98a4b8832d125134a16153
    question_text: List all transformers within Substation OSLO
    reference_answer: OSLO T1, OSLO T2
    reference_steps:
    - - name: retrieval
        args:
          query: transformers Substation OSLO
          k: 2
      - name: sparql_query
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
    reference_answer: STAVANGET1
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
    reference_answer: ARENDAL, BLAFALLI, STAVANGER, KRISTIA_HVDC, KVILLDAL, SANDEFJORD, KRISTIANSAND, FEDA_HVDC
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
    reference_answer: HALDEN, KONGSBERG, SYLLING, OSLO, ASKER, SYSLE, SKIEN, TRETTEN
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

### Evaluation Target Corpus

Below is an example response from the question-answering system for a single question (unless there is an error in answering: see [Example Target Input on Error](#example-target-input-on-error) below):

```json
{
    "question_id": "f91fc938d606e5f6089912bebfaf114b",
    "input_tokens": 298028,
    "output_tokens": 725,
    "total_tokens": 298753,
    "elapsed_sec": 46.48961806297302,
    "actual_steps": [
        {
          "name": "retrieval",
          "args": {
            "query": "transformers Substation OSLO",
            "k": 2
          },
          "id": "call_3",
          "status": "success",
          "output": "[\n  {\n    \"id\": 1,\n    \"text\": \"Transformer OSLO T1 is in Substation Oslo.\"\n  },\n  {\n    \"id\": 2,\n    \"text\": \"Transformer OSLO T2 is in Substation Oslo.\"\n  }\n]"
        },
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

#### Example Target Input on Error

If an error occurs during generating a response to a question, the expected target input for evaluation is:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "error": "Error message",
    "status": "error"
}
```

### Example Usage Code

```python
from qa_eval import run_evaluation, compute_aggregates

reference_qas: list[dict] = [] # read your corpus
chat_responses: dict = {} # call your implementation to get the response
evaluation_results = run_evaluation(reference_qas, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of statistics for each question, as in section [Example Evaluation Results](#example-evaluation-results). The format is explained in section [Output Keys](#output-keys)

If your chat responses contain actual answers, set your environment variable `OPENAI_API_KEY` before running the code above.

### Example Evaluation Results

The output is a list of statistics for each question from the reference Q&A dataset. Here is an example of statistics for one question:

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  question_id: c10bbc8dce98a4b8832d125134a16153
  question_text: List all transformers within Substation OSLO
  reference_answer: OSLO T1, OSLO T2
  reference_steps:
  - - name: retrieval
      args:
        query: transformers Substation OSLO
        k: 2
    - name: sparql_query
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
  status: success
  actual_answer: |-
    The following transformers are located within the Substation OSLO:
    1. **OSLO T2** (IRI: `urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f`)
    2. **OSLO T1** (IRI: `urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f`)
  answer_reference_claims_count: 2
  answer_actual_claims_count: 2
  answer_matching_claims_count: 2
  answer_correctness_reason: The candidate answer contains exactly the transformers listed in the reference answer, asked in the question
  answer_recall: 1.0
  answer_precision: 1.0
  answer_f1: 1.0
  answer_relevance: 0.9
  answer_relevance_cost: 0.0007
  actual_steps:
  - name: retrieval
    id: call_3
    args:
      query: transformers Substation OSLO
      k: 2
    status: success
    output: |-
      [
        {
          "id": "1",
          "text": "Transformer OSLO T1 is in Substation Oslo."
        },
        {
          "id": "2",
          "text": "Transformer OSLO T2 is in Substation Oslo."
        }
      ]
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
  steps_score: 1
  input_tokens: 221339
  output_tokens: 212
  total_tokens: 221551
  elapsed_sec: 6.601679801940918
```

### Output Keys

- `template_id`: the template id
- `question_id`: the question id
- `question_text`: the natural language query
- `reference_steps`: (optional) copy of the expected steps in the Q&A dataset, if specified there
- `reference_answer`: (optional) copy of the expected answer in the Q&A dataset, if specified there
- `status`: "success" or "error", indicating whether the evaluation succeeded
- `actual_answer`: (optional) copy of the response text in the evaluation target, if specified there
- `answer_reference_claims_count`: (optional) number of claims extracted from the reference answer, if a reference answer and actual answer are available
- `answer_actual_claims_count`: (optional) number of claims extracted from the answer being evaluated, if a reference answer and actual answer are available
- `answer_matching_claims_count`: (optional) number of matching claims between the reference answer and the actual answer, if a reference answer and actual answer are available
- `answer_recall`: (optional) `answer_matching_claims_count / answer_reference_claims_count`
- `answer_precision`: (optional) `answer_matching_claims_count / answer_actual_claims_count`
- `answer_correctness_reason`: (optional) LLM reasoning in extracting and matching claims from the reference answer and the actual answer
- `answer_eval_error`: (optional) error message if answer evaluation failed
- `answer_f1`: (optional) Harmonic mean of `answer_recall` and `answer_precision`
- `answer_relevance`: (optional) The value representing how relevant is the actual answer to the question, computed using [RAGAS answer relevance](https://docs.ragas.io/en/v0.3.3/concepts/metrics/available_metrics/answer_relevance/)
- `answer_relevance_error`: (optional) error message if answer relevance evaluation failed
- `answer_relevance_cost`: The LLM use cost of computing `answer_relevance`, in US dollars
- `actual_steps`: (optional) copy of the steps in the evaluation target, if specified there
- `steps_score`: a real number between 0 and 1, computed by comparing the results of the last executed steps to the output of the reference's last group of steps.
    - If there is no match in the actual steps, then the score is `0.0`
    - For executed steps whose name is "retrieval":
        - If the last reference group contains a retrieval step and its output (the reference context) is specified, the score is the [recall at k](#context-recallk) of the retrieved document ids with respect to the reference.
        - If it does not specify the output (there is no reference context), the score is `1.0`
    - Otherwise, the score is the number of the matched steps on the last group divided by the total number of steps in the last group.
- `input_tokens`: input tokens usage
- `output_tokens`: output tokens usage
- `total_tokens`: total tokens usage
- `elapsed_sec`: elapsed seconds

All `actual_steps` with `name` "retrieval" contain:
- `retrieval_answer_recall`: recall of the actually retrieved context when evaluated using the reference answer
- `retrieval_answer_recall_error`: error of evaluating `retrieval_answer_recall`
- `retrieval_answer_recall_cost`: cost of evaluating `retrieval_answer_recall`, in US dollars
- `retrieval_answer_precision`: precision of the actually retrieved context when evaluated using the reference answer
- `retrieval_answer_precision_error`: error of evaluating `retrieval_answer_precision`
- `retrieval_answer_precision_cost`: cost of evaluating `retrieval_answer_precision`, in US dollars
- `retrieval_answer_f1`: F1 score of the actually retrieved context when evaluated using the reference answer
- `retrieval_answer_f1_cost`: cost of evaluating `retrieval_answer_f1`, in US dollars

#### Aggregates Keys

The `aggregates` object provides aggregated evaluation metrics.
Aggregates are computed both per-template and overall, using micro and macro averaging strategies.
These aggregates support analysis of agent quality, token efficiency, and execution performance.
Aggregates are:
- `per_template`: a dictionary mapping a template identifier to the following statistics:
  - `number_of_error_samples`: number of questions for this template, which resulted in error response
  - `number_of_success_samples`: number of questions for this template, which resulted in successful response
  - `input_tokens`: `sum`, `mean`, `median`, `min` and `max` statistics for `input_tokens` of all successful questions for this template
  - `output_tokens`: `sum`, `mean`, `median`, `min` and `max` statistics for `output_tokens` of all successful questions for this template
  - `total_tokens`: `sum`, `mean`, `median`, `min` and `max` statistics for `total_tokens` of all successful questions for this template
  - `elapsed_sec`: `sum`, `mean`, `median`, `min` and `max` statistics for `elapsed_sec` of all successful questions for this template
  - `answer_recall`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_recall` of all successful questions for this template
  - `answer_precision`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_precision` of all successful questions for this template
  - `answer_f1`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_f1` of all successful questions for this template
  - `answer_relevance`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_relevance` of all successful questions for this template
  - `steps_score`: `sum`, `mean`, `median`, `min` and `max` statistics for `steps_score` of all successful questions for this template
  - `steps`: `sum`, `mean`, `median`, `min` and `max` statistics for `steps` of all successful questions for this template. Includes:
    - `steps`: for each step type how many times it was executed
    - `once_per_sample`: how many times each step was executed, counted only once per question
    - `empty_results`: how many times the step was executed and returned empty results
    - `errors`: how many times the step was executed and resulted in error
- `micro`: statistics across questions, regardless of template. It includes:
  - `number_of_error_samples`: total number of questions, which resulted in error response
  - `number_of_success_samples`: total number of questions, which resulted in successful response
  - `input_tokens`: `sum`, `mean`, `median`, `min` and `max` for `input_tokens` of all successful questions
  - `output_tokens`: `sum`, `mean`, `median`, `min` and `max` for `output_tokens` of all successful questions
  - `total_tokens`: `sum`, `mean`, `median`, `min` and `max` for `total_tokens` of all successful questions
  - `elapsed_sec`: `sum`, `mean`, `median`, `min` and `max` for `elapsed_sec` of all successful questions
  - `answer_recall`: `sum`, `mean`, `median`, `min` and `max` for `answer_recall` of all successful questions
  - `answer_precision`: `sum`, `mean`, `median`, `min` and `max` for `answer_precision` of all successful questions
  - `answer_f1`: `sum`, `mean`, `median`, `min` and `max` for `answer_f1` of all successful questions
  - `answer_relevance`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_relevance` of all successful questions
  - `answer_relevance_cost`: `sum`, `mean`, `median`, `min` and `max` statistics for `answer_relevance_cost` of all successful questions
  - `steps_score`: `sum`, `mean`, `median`, `min` and `max` for `steps_score` of all successful questions
- `macro`: averages across templates, i.e., the mean of each metric per template, averaged. It includes:
  - `input_tokens`: `mean` for `input_tokens`
  - `output_tokens`: `mean` for `output_tokens`
  - `total_tokens`: `mean` for `total_tokens`
  - `elapsed_sec`: `mean` for `elapsed_sec`
  - `answer_recall`: `mean` for `answer_recall`
  - `answer_precision`: `mean` for `answer_precision`
  - `answer_f1`: `mean` for `answer_f1`
  - `answer_relevance`: `mean` for `answer_relevance`
  - `answer_relevance_cost`: `mean` for `answer_relevance_cost`
  - `steps_score`: `mean` for `steps_score`

#### Example Aggregates

```yaml
per_template:
  list_all_transformers_within_Substation_SUBSTATION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
        min: 0.9
        max: 0.9
        mean: 0.9
        median: 0.9
        sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
        sparql_query: 8
      once_per_sample:
        autocomplete_search: 10
        sparql_query: 8
      empty_results:
        autocomplete_search: 2
    steps_score:
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
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 10
    steps_score:
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
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 9
        sparql_query: 17
      once_per_sample:
        autocomplete_search: 9
        sparql_query: 9
      errors:
        sparql_query: 8
    steps_score:
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
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 20
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 20
    steps_score:
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
  answer_recall:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_precision:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_f1:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_relevance:
    min: 0.9
    max: 0.9
    mean: 0.9
    median: 0.9
    sum: 0.9
  answer_relevance_cost:
    min: 0.0007
    max: 0.0007
    mean: 0.0007
    median: 0.0007
    sum: 0.0007
  steps_score:
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
  answer_recall:
    mean: 1.0
  answer_precision:
    mean: 1.0
  answer_f1:
    mean: 1.0
  answer_relevance:
    mean: 0.9
  answer_relevance_cost:
    mean: 0.0007
  steps_score:
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

### Retrieval Metrics

The following metrics are based on the content of retrieved documents.

#### Context Recall@k

The fraction of relevant items among the top *k* recommendations. It answers the question: "Of all items the user cares about, how many did we inclide in the first k spots?"
* **Formula**:
    $`
    \frac{\text{Number of relevant items in top k}}{\text{Number of relevant items}}
    `$
* **Calculation**: Count the number of relevant items in the top `k` retrieved results; divide that by the first 'k' relevant items.
* **Example**: Suppose there are 4 relevant documents for a given query. Suppose our system retrieves 3 of them in the top 5 results (`k=5`). Recall@5 is `3 / 4 = 0.75`.

```python
recall_at_k(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7],
    k=5
)  # => 0.75
```

#### Context Precision@k

Evaluates a ranked list of recommendations by looking at the precision at the position of each correctly retrieved item. It rewards systems for placing relevant items higher up in the list. It's more sophisticated than just looking at precision at a single cutoff because it considers the entire ranking.
* **Formula**:
    $`
    \frac{\sum_{k=1}^{n} (P(k) \times \text{rel}(k))}{\text{Number of relevant items}}
    `$,\
    where:
    * `P(k)` is the precision at rank `k`
    * `rel(k)` is 1 if the item at rank `k` is relevant and 0 otherwise.
* **Calculation**:
    1. For each retrieved item, if it is relevant, record the precision at that index (i.e., `number of hits / current rank`).
    2. Average all of these precision scores.
    3. Divide that average by the total number of relevant items.
* **Example**:
    * Suppose:
      * The relevant items are `1, 3, 5, 6`
      * Our system retrieves `1, 4, 3, 5, 7`
    * Calculation:
      * Item at index 1 (item 1) is relevant. Precision@1 = 1/1
      * Item at index 3 (item 2) is relevant. Precision@3 = 2/3
      * Item at index 4 (item 5) is relevant. Precision@4 = 3/4
      * AP = (1.0 + 2/3 + 3/4) / 3 = 0.8055...

```python
average_precision(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7]
) # ~=> 0.8056
```
