Given a question, a reference answer and a candidate answer to it, extract all the claims from each answer, find corresponding claims between answers. Pay attention to details such as numbers, command names and paths. Output the values listed below, in JSON.

# Question
{question}

# Reference answer
{reference_answer}

# Candidate answer
{candidate_answer}

# Output values
v1: Numbered list of reference answer claims
v2: Numbered list of candidate answer claims, each followed by its matching reference answer claim number (if any), in square brackets
v3: Count of reference answer claims
v4: Count of candidate answer claims
v5: Count of matching claims

Output the values in JSON without markup.


# Value checks
1 <= v3, v4
0 <= v5 <= v3, v4
