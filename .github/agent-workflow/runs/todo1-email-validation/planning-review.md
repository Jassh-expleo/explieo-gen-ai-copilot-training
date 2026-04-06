# Planning Review — `validate_customer_email` (TODO 1)

**Run:** `todo1-email-validation`
**Target file:** `6AprilOnwardsTraining/lab_starter_Day1.py`
**Test file (new):** `6AprilOnwardsTraining/test_validate_customer_email.py`
**Architecture option adopted:** Option B — one public function, three ordered internal stages
**Dependencies:** stdlib only

---

## Task List

| ID | Title | Complexity | Depends On |
|----|-------|-----------|------------|
| T1 | Scaffold the function stub | Low | — |
| T2 | Implement Stage 1 — Normalization | Low | T1 |
| T3 | Implement Stage 2 — Structural Validation | Medium | T2 |
| T4 | Implement Stage 3 — Domain Authorization | Low | T3 |
| T5 | Wire all three stages into the public function | Low | T4 |
| T6 | Write the unit test suite (≥20 tests) | Medium | T5 |

---

## Acceptance Criteria Per Task

### T1 — Scaffold the function stub
- `validate_customer_email` defined at module level, replacing/below the `# TODO 1` comment
- Exact signature: `def validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool:`
- Concise docstring: purpose, parameters, return contract, "never raises on bad input"
- Body: `return False` placeholder
- File importable; no other lines modified

### T2 — Normalization stage
- Private helper normalizes email and allowed_domains
- Non-string input → safe sentinel → public fn returns `False`
- Strips whitespace, lowercases email
- Lowercases each allowed_domains entry into a new set (no mutation)
- `None` stays `None`; `set()` stays `set()`

### T3 — Structural validation stage
- Private helper receives already-normalized string
- Returns `False` for: zero `@`, 2+ `@`, empty local, empty domain, no dot in domain, empty label (consecutive dots / leading/trailing dot), label starts/ends with `-`
- Returns `True` for: `user@example.com`, `a@b.co`, `first.last@sub.domain.org`, `a@example.com`
- Does NOT perform allowlist check

### T4 — Domain authorization stage
- Private helper `_is_domain_allowed(domain, allowed_domains) -> bool`
- `None` → `True` (no restriction)
- `set()` → `False` (rejects all)
- Exact membership only — `sub.example.com` ≠ `example.com`

### T5 — Wire and compose
- Public fn calls T2 → T3 → T4 in order, short-circuit on any `False`
- Outermost `try/except Exception` guard returns `False` on unexpected errors
- All other TODOs (2–6) untouched

### T6 — Unit test suite
- New file: `6AprilOnwardsTraining/test_validate_customer_email.py`
- `unittest.TestCase`, class `TestValidateCustomerEmail`
- ≥20 test methods, all deterministic, no network/FS side effects
- Covers: normalization, non-string inputs, structural rules (S01–S15), domain authorization (D01–D06), integration (I01–I10)
- Passes: `python -m unittest test_validate_customer_email -v` with 0 failures, 0 errors

---

## Test Strategy Summary

### Structural matrix (T3)
| Test | Input | Expected |
|------|-------|----------|
| S01 | `user@example.com` | True |
| S02 | `a@b.co` | True |
| S03 | `first.last@sub.domain.org` | True |
| S04 | `""` | False |
| S05 | `userexample.com` | False |
| S06 | `user@@example.com` | False |
| S07 | `@example.com` | False |
| S08 | `user@` | False |
| S09 | `user@nodot` | False |
| S10 | `user@.example.com` | False |
| S11 | `user@example..com` | False |
| S12 | `user@example.com.` | False |
| S13 | `user@-example.com` | False |
| S14 | `user@example-.com` | False |
| S15 | `a@b.c` | True |

### Domain authorization matrix (T4)
| Test | domain | allowed_domains | Expected |
|------|--------|----------------|----------|
| D01 | `example.com` | None | True |
| D02 | `example.com` | `set()` | False |
| D03 | `example.com` | `{"example.com"}` | True |
| D04 | `other.com` | `{"example.com"}` | False |
| D05 | `sub.example.com` | `{"example.com"}` | False |
| D06 | `example.com` | `{"example.com", "other.org"}` | True |

### Integration matrix (T5/T6)
| Test | email | allowed_domains | Expected |
|------|-------|----------------|----------|
| I01 | `user@example.com` | None | True |
| I02 | `  USER@EXAMPLE.COM  ` | None | True |
| I03 | `bad-email` | None | False |
| I04 | `""` | None | False |
| I05 | None | None | False |
| I06 | `123` | None | False |
| I07 | `user@example.com` | `{"example.com"}` | True |
| I08 | `user@other.com` | `{"example.com"}` | False |
| I09 | `user@example.com` | `set()` | False |
| I10 | `sub@sub.example.com` | `{"example.com"}` | False |

---

## Key Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Python < 3.10: `set[str] \| None` syntax fails | Use `Optional[Set[str]]` from `typing` if needed |
| R2 | Monolithic regex hides stage separation | Use string ops (`.split`, `.startswith`), not a single regex |
| R3 | Mutation of caller's `allowed_domains` | T2 must build a **new** set |
| R4 | ⚠️ Empty `set()` silently rejects all — confirm with user | Document clearly in docstring; flag before T5 |
| R5 | Internal hyphens valid: `my-company.com` must pass | Add to T6 test coverage |
| R7 | Broad `try/except` masks bugs during dev | Use guard at outermost level only |

---

## Definition of Done

- [ ] Function present and callable in target file
- [ ] Signature, docstring, type hints match architecture exactly
- [ ] Three stages clearly separated
- [ ] Zero third-party imports
- [ ] Never raises on user input (verified by tests)
- [ ] `python -m unittest test_validate_customer_email -v` → 0 failures, 0 errors, ≥20 tests
- [ ] All S01–S15, D01–D06, I01–I10 pass
- [ ] No other TODO (2–6) modified
