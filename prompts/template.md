Given a question, a reference answer and a candidate answer to it, split each answer into claims, find corresponding claims between answers, and output the values listed below.

# Question
{question}

# Reference answer
{reference_answer}

# Candidate answer
{candidate_answer}

# Output values
v1: Count of reference answer claims
v2: Count of candidate answer claims
v3: Count of matching claims
v4: Explanation of v1-v3 (in English)

# Value checks
1 <= v1, v2
0 <= v3 <= v1, v2

# Output format
<v1><tab><v2><tab><v3><tab><v4>
