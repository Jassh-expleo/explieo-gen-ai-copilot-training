"""Enterprise-ready GitHub Copilot training starter.

Use this file to train engineers on how to prompt Copilot with
clear requirements, guardrails, and acceptance criteria.

Team standards for every exercise:
1. Add type hints.
2. Add concise docstrings.
3. Validate inputs and raise meaningful exceptions.
4. Handle edge cases explicitly.
5. Keep functions small and readable.
6. Prefer standard library unless there is a clear reason not to.
7. Write tests for success and failure scenarios.
"""
from __future__ import annotations


# GitHub Copilot Hands-On Lab
# ─────────────────────────────────────────
# Instructions:
# 1. Read the TODO and acceptance criteria.
# 2. Prompt Copilot with the business context, constraints, and expected output.
# 3. Review the generated code before accepting it.
# 4. Refactor until it meets the team standards above.


# TODO 1: Implement validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool
# Business context:
# Validate customer or employee email addresses before onboarding them into an internal platform.
# Acceptance criteria:
# - Reject empty or whitespace-only input.
# - Normalize case before validation.
# - Validate basic email structure.
# - If allowed_domains is provided, only accept emails from those domains.
# - Return False for invalid emails instead of crashing.


def _normalize_email_inputs(
    email: str,
    allowed_domains: set[str] | None,
) -> tuple[str, set[str] | None]:
    """Normalize raw inputs before validation logic runs.

    Parameters
    ----------
    email:
        Raw value supplied by the caller.  Non-``str`` values are coerced to
        an empty string so that downstream logic can return ``False`` cleanly.
    allowed_domains:
        Optional set of permitted domain strings.  When provided a **new** set
        is returned with every entry stripped and lowercased; the caller's
        original set is never mutated.  ``None`` is passed through unchanged.

    Returns
    -------
    tuple[str, set[str] | None]
        ``(normalized_email, normalized_allowed_domains)``
    """
    # Rule 1 — non-string email: treat as invalid by returning empty string.
    if not isinstance(email, str):
        normalized_email = ""
    else:
        # Rule 2 — strip whitespace; Rule 3 — lowercase.
        normalized_email = email.strip().lower()

    # Rule 4 — normalize allowed_domains without mutating the caller's set.
    if allowed_domains is None:
        normalized_domains: set[str] | None = None
    else:
        normalized_domains = {d.strip().lower() for d in allowed_domains}

    return normalized_email, normalized_domains


def validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool:
    """Validate a customer email for platform onboarding.

    Parameters
    ----------
    email:
        Raw email string supplied by the caller.
    allowed_domains:
        Optional set of permitted domain strings (e.g. ``{"example.com", "corp.io"}``).
        ``None`` means no domain restriction is applied.
        An *empty* set rejects all emails regardless of content.

    Returns
    -------
    bool
        ``True`` if the email passes all applicable checks, ``False`` otherwise.
        This function never raises on user-supplied input.
    """
    email, allowed_domains = _normalize_email_inputs(email, allowed_domains)
    if not email:
        return False
    return False  # placeholder — structural validation comes next (T3)


# TODO 2: Implement calculate_compound_interest(principal: float, annual_rate: float, years: int, compounds_per_year: int = 12) -> float
# Business context:
# Finance teams use this to estimate returns for investment products.
# Acceptance criteria:
# - Reject negative principal, rate, years, or compounds_per_year.
# - Use a deterministic calculation and round to 2 decimal places.
# - Raise ValueError for invalid numeric inputs.
# - Add examples in the docstring.


# TODO 3: Implement load_csv_records(file_path: str, required_columns: list[str] | None = None) -> list[dict[str, str]]
# Business context:
# Data operations teams ingest partner CSV files into downstream systems.
# Acceptance criteria:
# - Open the file using utf-8.
# - Raise FileNotFoundError if the file does not exist.
# - Raise ValueError if required columns are missing.
# - Return a list of dictionaries keyed by column name.
# - Keep the function readable and easy to test.


# TODO 4: Implement fetch_api_json(url: str, timeout_seconds: float = 5.0) -> dict
# Business context:
# Platform teams call external services and need safe error handling.
# Acceptance criteria:
# - Use the standard library.
# - Add a timeout.
# - Return parsed JSON for successful 200 responses.
# - Raise a clear RuntimeError for HTTP, timeout, or JSON parsing failures.
# - Include enough error detail for troubleshooting without leaking secrets.


# TODO 5: Implement mask_pii(record: dict[str, str]) -> dict[str, str]
# Business context:
# Logs and exported support data must not expose sensitive customer data.
# Acceptance criteria:
# - Mask common fields such as email, phone, account_number, and ssn when present.
# - Return a new dictionary instead of mutating the input.
# - Leave non-sensitive fields unchanged.
# - Document masking rules clearly.


# TODO 6: Write unit tests for the functions above.
# Minimum test coverage:
# - Happy path for each function.
# - Invalid input and edge-case scenarios.
# - At least one failure-path test for file and API handling.
# - Tests should be deterministic and not depend on live external services.
