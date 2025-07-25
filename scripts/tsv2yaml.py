import csv
import yaml


def tsv_to_yaml(
    in_tsv_path: str,
    out_ref_yaml_path: str,
    out_actual_yaml_path: str
) -> None:
    """
    Convert a TSV file to a reference YAML file of questions, reference answers
    and context, and a YAML file of actual responses and context.

    Args:
        in_tsv_path: Path to input TSV file
        out_ref_yaml_path: Path to output reference YAML file
        out_actual_yaml_path: Path to output actual YAML file
    """
    # Read TSV file
    with open(in_tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    # Prepare reference YAML structure
    ref_data = []
    actual_data = []

    for i, row in enumerate(rows, start=1):
        # Process reference data
        ref_question = {
            'id': i,
            'question_text': row['Question'],
            'reference_answer': row['Reference answer'],
            'reference_steps': [
                [
                    {
                        'name': 'document_retrieval',
                        'id': 1,
                        'args': {
                            'question': row['Question']
                        },
                        'output': row['Reference context'],
                        'output_media_type': 'text/plain'
                    }
                ]
            ]
        }

        # Process actual data
        actual_question = {
            'id': i,
            'actual_answer': row['Actual answer'],
            'actual_steps': [
                {
                    'name': 'document_retrieval',
                    'id': 1,
                    'args': {
                        'question': row['Question']
                    },
                    'output': row['Actual context'],
                    'output_media_type': 'iri-reference'
                }
            ],
            'tokens': {
                'input': 0,  # Placeholder values
                'output': 0,  # Can be modified as needed
                'reasoning': 0
            },
            'elapsed_seconds': 0  # Placeholder value
        }

        # Add to appropriate lists
        # Assuming all questions belong to the same template for this example
        if not ref_data:
            ref_data.append({
                'template_id': 'graphdb_parameter',
                'questions': [ref_question]
            })
        else:
            ref_data[0]['questions'].append(ref_question)

        if not actual_data:
            actual_data.append({
                'template_id': 'graphdb_parameter',
                'questions': [actual_question]
            })
        else:
            actual_data[0]['questions'].append(actual_question)

    # Write YAML files
    with open(out_ref_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(ref_data, f, sort_keys=False, allow_unicode=True)

    with open(out_actual_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(actual_data, f, sort_keys=False, allow_unicode=True)

# Example usage:
# tsv_to_yaml('input.tsv', 'reference.yaml', 'actual.yaml')
