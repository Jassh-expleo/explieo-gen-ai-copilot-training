# Architecture Review: `calculate_compound_interest`

---

## 1. Problem Summary

Finance teams within the Explieo Copilot Training programme need a reliable, deterministic Python utility function that computes compound interest using the standard formula:

```
A = P × (1 + r/n)^(n×t)
```

where **A** is the final amount (principal + interest), **P** is the principal, **r** is the annual rate as a decimal, **n** is the number of compounding periods per year, and **t** is the time in years.

The function must enforce clear input validation, raise descriptive exceptions on bad data, handle canonical edge cases gracefully, and return a consistently rounded monetary result. It exists as **TODO 2** in the training lab (`lab_starter_Day1.py`) and must conform to the established team coding standards already visible in the codebase (`Day2.py`, `lab_starter_Day1.py`).

---

## 2. Assumptions

| # | Assumption | Basis |
|---|---|---|
| A1 | `annual_rate` is supplied as a **decimal fraction** (0.05 = 5%), not a percentage (5.0). | Standard mathematical convention for the formula; consistent with finance API patterns. |
| A2 | The function returns the **final amount A**, not just the interest earned `(A − P)`. | Requirement explicitly states this. |
| A3 | Return value must be **rounded to 2 decimal places** (cents). | TODO 2 acceptance criteria in `lab_starter_Day1.py` says "round to 2 decimal places." |
| A4 | Only the **Python standard library** is used (`math` module). | Team standard #6 in `lab_starter_Day1.py`: "Prefer standard library unless there is a clear reason not to." |
| A5 | `years` is a non-negative **integer**. | Signature: `years: int`. Fractional years are out of scope for this function. |
| A6 | `principal` may be a whole number passed as `int` at call-site (Python duck-typing). | Type hints are advisory; the validation layer should accept numeric-compatible inputs and coerce or reject gracefully. |
| A7 | This function is **not** thread-safety-sensitive; it is a pure mathematical function with no shared state. | No I/O, no global mutation. |
| A8 | The project uses **pytest** (`.pytest_cache` at root). | Confirmed by `.pytest_cache` directory presence. |
| A9 | `principal > 0` (strictly positive). A principal of zero has no financial meaning and should be rejected. | Domain logic; a zero-balance account produces A=0 regardless of rate, which is a degenerate case offering no value. |
| A10 | The function will eventually live alongside other TODOs from the same lab (email validator, CSV loader, etc.) and may be called from a FastAPI endpoint or training demo script. | `dashboard/server.py` and `demo_day2_run.py` suggest a demo-integration pathway. |

---

## 3. Options Considered

### Option A — Inline in `lab_starter_Day1.py` (TODO 2 in place)

Place the function directly in `6AprilOnwardsTraining/lab_starter_Day1.py`, completing the TODO already stubbed there.

**Pros**: Zero structural change. Consistent with `validate_customer_email` already partially implemented in the same file.

**Cons**: `lab_starter_Day1.py` will grow to contain 5+ unrelated utilities — low cohesion over time. Not reusable as a standalone finance module without importing the entire lab file.

---

### Option B — Dedicated `finance_utils.py` module (RECOMMENDED)

Create `6AprilOnwardsTraining/finance_utils.py` as a single-responsibility module. Companion test: `6AprilOnwardsTraining/PythonCodes/test_finance_utils.py`.

**Pros**: High cohesion. Clean import path. Scales for future financial helpers. Importable by `dashboard/server.py` without side-effects from unrelated stubs.

**Cons**: Adds a new file. Slight convention mismatch with the "one file = one lab day" pattern.

---

### Option C — `decimal.Decimal`-based precision module

Use Python's `decimal.Decimal` with `ROUND_HALF_UP` quantization.

**Pros**: Eliminates all IEEE 754 floating-point rounding artifacts. The gold standard for financial software.

**Cons**: Materially increases complexity. The function signature explicitly uses `float`. Overkill for training context.

---

## 4. Recommended Design

**→ Option B: Dedicated `finance_utils.py` with `float`-based arithmetic and `round(..., 2)` return, companion `test_finance_utils.py` using `pytest`.**

**Rationale:**
1. **Single Responsibility**: Finance logic deserves its own home.
2. **Reusability**: Clean import path for `dashboard/server.py` or `demo_day2_run.py`.
3. **`float` over `Decimal`**: The function signature mandates `float`. `round(result, 2)` is the deterministic, testable contract stipulated in the acceptance criteria.
4. **pytest**: The `.pytest_cache` at the repo root confirms pytest is the project runner.
5. **Lab integration**: `lab_starter_Day1.py` TODO 2 remains as the exercise prompt, directing learners to implement in `finance_utils.py`.

---

## 5. Component Boundaries

```
6AprilOnwardsTraining/
│
├── lab_starter_Day1.py          ← Training prompt file (TODO 2 remains as prompt)
│                                   Imports from finance_utils for demo/reference
│
├── finance_utils.py             ← NEW: Owner of calculate_compound_interest()
│   │                               Pure function, no I/O, no global state
│   └── calculate_compound_interest()
│       ├── _validate_inputs()   ← Internal guard (private helper, not exported)
│       └── **                   ← Standard library only
│
└── PythonCodes/
    └── test_finance_utils.py    ← NEW: pytest test suite
        ├── test_happy_path_*
        ├── test_edge_case_*
        └── test_invalid_input_*
```

**Dependency graph (no cycles):**
```
test_finance_utils.py → finance_utils.py → math (stdlib)
```

---

## 6. Interface Contracts

### 6.1 Public Function Signature

```python
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
) -> float:
```

### 6.2 Parameter Contracts

| Parameter | Type | Valid Range | Notes |
|---|---|---|---|
| `principal` | `float` (or int-compatible) | `> 0` | Strictly positive. |
| `annual_rate` | `float` | `>= 0.0` | Zero is valid. Expressed as decimal: `0.05` = 5%. |
| `years` | `int` | `>= 0` | Zero years returns principal unchanged. |
| `compounds_per_year` | `int` | `>= 1` | Default 12 (monthly). 1=annual, 4=quarterly, 365=daily. |

### 6.3 Return Contract

- **Type**: `float`
- **Value**: Final amount `A`, rounded to 2 decimal places via `round(A, 2)`.
- **Invariant**: Return value is always `>= principal` when `annual_rate >= 0` and `years >= 0`.

### 6.4 Exception Contract

| Condition | Exception | Message Pattern |
|---|---|---|
| `principal <= 0` | `ValueError` | `"principal must be greater than 0, got {principal}"` |
| `annual_rate < 0` | `ValueError` | `"annual_rate must be >= 0, got {annual_rate}"` |
| `years < 0` | `ValueError` | `"years must be >= 0, got {years}"` |
| `compounds_per_year < 1` | `ValueError` | `"compounds_per_year must be >= 1, got {compounds_per_year}"` |
| Non-numeric `principal` or `annual_rate` | `TypeError` | `"principal must be a number, got {type}"` |
| Non-integer `years` or `compounds_per_year` | `TypeError` | `"years must be an integer, got {type}"` |

### 6.5 Mathematical Formula

```
A = P × (1 + r/n)^(n×t)

exponent = compounds_per_year * years
base     = 1.0 + (annual_rate / compounds_per_year)
A        = principal * (base ** exponent)
return round(A, 2)
```

### 6.6 Docstring Contract

Must include: Summary line, `Args:`, `Returns:`, `Raises:`, `Examples:` (min 3 entries covering normal case, `rate=0`, `years=0`, daily compounding).

---

## 7. Data and Error Flows

### 7.1 Happy Path

```
Caller
  │  calculate_compound_interest(1000.0, 0.05, 10, 12)
  ▼
_validate_inputs()  →  all checks pass
  ▼
base = 1.0 + (0.05 / 12) → 1.004166̄
exponent = 12 × 10        → 120
A = 1000.0 × 1.004166̄^120 → 1647.009...
round(1647.009..., 2)      → 1647.01
  ▼
Caller receives 1647.01
```

### 7.2 Edge Cases

| Case | Formula result |
|---|---|
| `annual_rate = 0` | `A = P × 1.0^(n×t) = P` |
| `years = 0` | `A = P × base^0 = P × 1.0 = P` |
| `compounds_per_year = 1` | `A = P × (1 + r)^t` (classical annual) |
| `compounds_per_year = 365` | Large exponent, handled natively by Python `**` |

### 7.3 Test Data Matrix

| Test Case | principal | annual_rate | years | n | Expected A |
|---|---|---|---|---|---|
| Standard monthly | 1000.0 | 0.05 | 10 | 12 | 1647.01 |
| Zero rate | 1000.0 | 0.0 | 10 | 12 | 1000.00 |
| Zero years | 1000.0 | 0.05 | 0 | 12 | 1000.00 |
| Annual compounding | 1000.0 | 0.05 | 1 | 1 | 1050.00 |
| Daily compounding | 1000.0 | 0.05 | 1 | 365 | 1051.27 |
| Quarterly | 5000.0 | 0.04 | 5 | 4 | 6104.00* |
| Invalid: principal≤0 | -100.0 | 0.05 | 1 | 12 | `ValueError` |
| Invalid: rate<0 | 1000.0 | -0.05 | 1 | 12 | `ValueError` |
| Invalid: years<0 | 1000.0 | 0.05 | -1 | 12 | `ValueError` |
| Invalid: n<1 | 1000.0 | 0.05 | 1 | 0 | `ValueError` |
| Invalid: wrong type | "1000" | 0.05 | 1 | 12 | `TypeError` |

*Exact values to be computed during implementation.

---

## 8. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | `float` rounding drift | Medium | Low | `round(A, 2)` at return boundary |
| R2 | Rate convention ambiguity (5.0 vs 0.05) | Medium | Medium | `warnings.warn` if `annual_rate > 1.0` |
| R3 | Overflow for extreme inputs | Low | Medium | Check for `math.inf`; raise `OverflowError` |
| R4 | Non-integer float passed as `years` | Low | Medium | `isinstance(years, int) and not isinstance(years, bool)` |
| R5 | Boolean inputs | Low | Low | Reject booleans for `principal` and `annual_rate` |
| R6 | `principal` passed as `int` | High | Low | Accept `isinstance(principal, (int, float))` excluding bool |
| R7 | Test precision fragility | Medium | Medium | Use `pytest.approx(expected, abs=0.005)` |
| R8 | Learner passes percentage rate | High (training) | Low | Explicit docstring `Examples:` with wrong-usage note |

---

## 9. Open Questions

| # | Question | Impact if Unresolved |
|---|---|---|
| OQ1 | Should `principal = 0` be valid? | Validation boundary changes |
| OQ2 | Return `float` only vs `tuple[float, float]` (amount + interest earned)? | Breaking signature change |
| OQ3 | `annual_rate > 1.0` → warning vs hard `ValueError`? | Validation logic differs |
| OQ4 | Should fractional `years` be supported in a future iteration? | Signature must change if yes |
| OQ5 | Module long-term location re: dashboard import resolution? | Module placement differs |
| OQ6 | Should `compounds_per_year` have an approved allow-list (1,2,4,12,52,365)? | Extra guard logic |

---

## 10. Handoff To Planning Agent

### Decisions Locked
- **Formula**: `A = P × (1 + r/n)^(n×t)`, returns final amount.
- **Rounding**: `round(result, 2)`.
- **Exceptions**: `ValueError` for bad values, `TypeError` for wrong types.
- **Library**: Standard library only.
- **Test runner**: pytest with `approx` for float assertions.
- **Module path**: `6AprilOnwardsTraining/finance_utils.py` (new file).

### Decisions Pending (block implementation until resolved)
- OQ2: Return type — `float` only vs `tuple[float, float]`.
- OQ3: `annual_rate > 1.0` — warning vs hard error.
- OQ5: Dashboard import resolution.

### Files to Create
```
6AprilOnwardsTraining/finance_utils.py
6AprilOnwardsTraining/PythonCodes/test_finance_utils.py
```

### Definition of Done
- [ ] `calculate_compound_interest(1000, 0.05, 10, 12)` returns `1647.01`
- [ ] `calculate_compound_interest(1000, 0.0, 10)` returns `1000.0`
- [ ] `calculate_compound_interest(1000, 0.05, 0)` returns `1000.0`
- [ ] All invalid inputs raise the documented exception with a message containing the bad value
- [ ] All tests pass under `pytest` with zero warnings
- [ ] Docstring includes at minimum 3 `Examples:` entries
- [ ] No `import` outside the Python standard library
