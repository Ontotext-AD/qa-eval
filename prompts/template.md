Below is a question, a reference answer and a candidate answer to it.
1. Extract all the claims from each answer
2. Find matching claims between answers. Matching claims have the same meaning and details such as numbers, command names and paths.
3. Output the values listed below.

# Question
{question}

# Reference answer
{reference_answer}

# Candidate answer
{candidate_answer}

# Output values
* reference_claims: list of reference answer claims
* candidate_claims: list of candidate answer claims

# Output format
* JSON without formatting
* Each claim is a string
  * If the claim matches a claim from the other answer, then append the matching claim's 1-based index in square brackets
