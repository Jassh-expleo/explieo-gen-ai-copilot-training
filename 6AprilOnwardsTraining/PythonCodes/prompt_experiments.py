# PROMPT A (weak):
# Write a function to process data.


# PROMPT B (enterprise-ready):
# Write a Python function named get_oldest_pending_orders with type hints.
# The function must:
# - Accept a list of order dictionaries.
# - Filter records where status == 'pending'.
# - Sort by created_at in ascending order. created_at is an ISO 8601 string.
# - Return the 5 oldest pending orders.
# - Raise ValueError if created_at is missing.
# - Not mutate the input list.
# - Include a docstring and 2 example test cases.
# - Use only the Python standard library.


# PROMPT C (team alignment version):
# You are writing production-quality Python for an internal order operations service.
# Implement get_oldest_pending_orders(orders: list[dict]) -> list[dict].
# Requirements:
# - Validate the input is a list of dictionaries.
# - Ignore records with status values other than 'pending'.
# - Treat created_at as required for pending records; raise ValueError if missing.
# - Parse timestamps safely using the standard library.
# - Return a new list and do not mutate the source data.
# - Keep cyclomatic complexity low and make the function easy to review.
# - Add a short docstring, type hints, and example unit tests.
# Output only Python code.
