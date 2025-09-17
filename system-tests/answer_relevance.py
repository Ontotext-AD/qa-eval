# This is a system test intended to be skipped by pytest because it calls an
# external LLM. Run it by executing the command:
#   poetry run python system_tests/answer_relevance.py
from langevals_ragas.response_relevancy import (
    RagasResponseRelevancyEvaluator,
    RagasResponseRelevancyEntry
)
settings_dict = {
    "model": 'gpt-4o-mini',
    "max_tokens": 65_536,
}
entry = RagasResponseRelevancyEntry(
    input="Why is the sky blue?",
    output="Oxygen makes it blue",
)
evaluator = RagasResponseRelevancyEvaluator(settings=settings_dict)
result = evaluator.evaluate(entry)
print(f"status: {result.status}")
print(f"score: {result.score}")
print(f"details: {result.details}")
print(f"cost: {result.cost.amount}")
