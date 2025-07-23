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
* v1: List of reference answer claims
* v2: List of candidate answer claims. Each claim string ends with the matching reference claim's 1-based index in square brackets, only if there is a such a match
* v3: Count of reference answer claims
* v4: Count of candidate answer claims
* v5: Count of matching claims

# Output format
* JSON without markup
  * v1, v2 values are lists of strings

# Value checks
* v1, v2 values are valid JSON lists of strings
* 1 <= v3, v4
* 0 <= v5 <= v3, v4
