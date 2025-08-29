Below are a query, a reference response and a candidate response to it.
1. Extract all claims from each response
2. Find matching claims between responses. Matching claims have the same meaning and details such as subjects, names, locations, amounts, IDs, commands and paths.
3. Output the values listed below (all and only those).

# Query
{question}

# Reference response
{reference_answer}

# Candidate response
{candidate_answer}

# Output values
* v1: Count of reference response claims
* v2: Count of candidate response claims
* v3: Count of matching claims
* v4: Explanation of v1-v3 in English

# Value checks
* 1 <= v1, v2
* 0 <= v3 <= v1, v2

# Output format
<v1><tab><v2><tab><v3><tab><v4>
