# Architecture Review - TODO 1 validate_customer_email

## 1. Problem Summary

The target is the TODO in [6AprilOnwardsTraining/lab_starter_Day1.py](6AprilOnwardsTraining/lab_starter_Day1.py#L26), which requires an architecture-level design for validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool without writing production code. The business purpose is to validate customer or employee email addresses before onboarding into an internal platform.

Current code context is minimal by design: [6AprilOnwardsTraining/lab_starter_Day1.py](6AprilOnwardsTraining/lab_starter_Day1.py#L1) contains only training instructions and acceptance criteria, not an implementation. The relevant behavioral constraints are explicit in [6AprilOnwardsTraining/lab_starter_Day1.py](6AprilOnwardsTraining/lab_starter_Day1.py#L28):
- Reject empty or whitespace-only input.
- Normalize case before validation.
- Validate basic email structure.
- If allowed_domains is provided, only accept emails from those domains.
- Return False for invalid emails instead of crashing.

There is one important design tension to resolve: the file-level team standards in [6AprilOnwardsTraining/lab_starter_Day1.py](6AprilOnwardsTraining/lab_starter_Day1.py#L6) say to validate inputs and raise meaningful exceptions, but TODO 1 explicitly requires returning False for invalid emails instead of crashing. For this function, the TODO-specific behavior should take precedence for user-supplied validation failures, while still allowing truly exceptional programmer errors to be handled deliberately if the team chooses to enforce stricter typing later.

## 2. Assumptions

- The function is intended as a lightweight business-validation utility, not a full RFC 5322-compliant email parser.
- Basic email structure means pragmatic validation suitable for onboarding workflows, not exhaustive standards compliance.
- The function should be deterministic and side-effect free.
- Email normalization is limited to case normalization and surrounding whitespace handling; it is not expected to canonicalize provider-specific aliases such as Gmail dots or plus-addressing.
- The domain comparison should be case-insensitive because the acceptance criteria require case normalization before validation.
- allowed_domains=None means domain allowlisting is disabled.
- An empty allowed_domains set should result in rejecting all otherwise valid emails, because an explicit allowlist with no entries logically permits no domains.
- The function should treat malformed input conservatively by returning False, consistent with the instead of crashing requirement.
- The design should prefer Python standard library only, aligning with the file's standards, unless a future approval explicitly broadens scope.

## 3. Options Considered

### Option A: Single-function inline validation with string checks
- Description: Implement all logic in one function using whitespace trimming, lowercasing, simple string operations, and a small set of structural checks.
- Pros:
  - Minimal surface area and very easy to read in a training file.
  - No dependency on regex complexity.
  - Straightforward for junior engineers to review and test.
- Cons:
  - String-only validation tends to become ad hoc and brittle as edge cases accumulate.
  - Harder to express basic structure precisely without growing a long sequence of conditionals.
  - Domain parsing and local-part checks can become less maintainable over time.

### Option B: Single public function with private validation helpers and a constrained regex
- Description: Keep one public API, but internally split work into normalization, structural validation, and optional domain-allowlist checks. Use a deliberately limited regex or equivalent structured checks for basic format validation.
- Pros:
  - Best balance between readability, testability, and correctness.
  - Makes acceptance criteria traceable to distinct validation phases.
  - Easier to evolve without changing the external contract.
  - Reduces risk of accidental crashes by containing parsing steps.
- Cons:
  - Slightly more architectural ceremony than a one-block implementation.
  - Requires discipline to keep the helper logic small and not over-engineer.

### Option C: Use the standard library email parsing modules as primary validator
- Description: Rely on email.utils or related parsing utilities to parse the address, then layer domain allowlist checks on top.
- Pros:
  - Reuses standard library parsing behavior.
  - Avoids maintaining custom parsing logic for some cases.
- Cons:
  - Standard library email parsing is oriented toward broader email address syntax and message parsing, not strict business acceptance validation.
  - Can accept syntactic forms that are valid in email headers but undesirable for onboarding workflows.
  - More opaque for training purposes and harder to map directly to basic email structure.

## 4. Recommended Design

Recommend Option B: one public function with three internal validation stages.

Rationale:
- It matches the acceptance criteria cleanly without introducing unnecessary framework or dependencies.
- It preserves a simple external contract: input parameters in, boolean out.
- It supports formal review because each acceptance criterion can be tied to a distinct stage:
  - Stage 1: normalize and reject blank input.
  - Stage 2: validate basic email structure.
  - Stage 3: enforce optional allowlisted domains.
- It is the safest interpretation of Return False for invalid emails instead of crashing because each stage can fail closed and return False rather than raising on bad user input.
- It remains readable for a training exercise and consistent with the keep functions small and readable standard in [6AprilOnwardsTraining/lab_starter_Day1.py](6AprilOnwardsTraining/lab_starter_Day1.py#L9).

Recommended behavioral model:
- Normalize input by trimming surrounding whitespace and lowercasing the full address.
- Reject if the normalized value is empty.
- Perform pragmatic structural validation:
  - Exactly one @.
  - Non-empty local part.
  - Non-empty domain part.
  - Domain contains at least one dot.
  - Domain labels are non-empty and do not begin or end with -.
  - Reject obvious malformed patterns such as consecutive dots in the domain or local/domain boundary anomalies.
- If allowed_domains is provided:
  - Normalize the allowed domains to lowercase.
  - Compare the parsed domain for exact membership.
  - Do not allow suffix matching unless explicitly approved later.
- Return True only when all applicable checks pass.
- Return False for any invalid or malformed business input.

## 5. Component Boundaries

### Public component
- validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool
- Responsibility: Orchestrate normalization, structural validation, and optional domain authorization; expose a single boolean result.

### Internal capability area: Normalization
- Responsibility: Trim surrounding whitespace and normalize case.
- Input: raw email, raw allowed_domains.
- Output: normalized email string and normalized domain allowlist.
- Boundary rule: No structural judgment beyond blank detection.

### Internal capability area: Structural email validation
- Responsibility: Decide whether the normalized email meets the agreed basic structure standard.
- Output: boolean validity plus parsed domain when valid.
- Boundary rule: This layer should not know business authorization rules such as which domains are allowed.

### Internal capability area: Domain authorization
- Responsibility: If an allowlist exists, confirm the parsed domain is present.
- Boundary rule: Exact-domain policy only unless future business requirements expand to subdomain or tenant policies.

### Non-goals
- Full RFC-compliant parsing.
- DNS checks, MX lookups, or SMTP verification.
- Provider-specific canonicalization such as stripping +tag.
- Internationalized domain or Unicode local-part support unless explicitly approved.

## 6. Interface Contracts

### Primary function contract
- Signature: validate_customer_email(email: str, allowed_domains: set[str] | None = None) -> bool
- Input contract:
  - email is expected to be a string.
  - allowed_domains is expected to be either None or a set of strings representing accepted domains.
- Output contract:
  - Returns True only for normalized, structurally valid emails that also satisfy the optional domain policy.
  - Returns False for blank, malformed, or disallowed email inputs.
- Error contract:
  - Preferred contract for this TODO is non-throwing for invalid business input.
  - If the implementation later chooses to defend against programmer misuse such as non-string allowed_domains contents, that decision must be explicit and documented because it intersects with the do not crash requirement.

### Normalization contract
- Email normalization:
  - Strip leading and trailing whitespace.
  - Convert to lowercase before validation and comparison.
- Allowed domain normalization:
  - If provided, each domain is normalized to lowercase.
  - Optional future enhancement: strip whitespace around each domain entry if the team wants defensive configuration handling.

### Structural validation contract
- Minimum accepted structure:
  - One and only one @.
  - Local part length greater than zero.
  - Domain part length greater than zero.
  - Domain contains at least one dot.
  - Domain labels separated by dots are each non-empty.
  - Domain labels do not start or end with hyphen.
- Minimum rejected structure examples:
  - Empty string or whitespace-only string.
  - user
  - @example.com
  - user@
  - user@@example.com
  - user@example
  - user@.com
  - user@example..com

### Domain policy contract
- If allowed_domains is None, any structurally valid domain is accepted.
- If allowed_domains is an empty set, no domain is accepted.
- Membership check is exact against the normalized domain.
- user@sub.example.com does not match example.com unless the allowlist explicitly contains sub.example.com.

## 7. Data and Error Flows

### Nominal flow
- Receive email and optional allowed_domains.
- Normalize the email string by trimming and lowercasing.
- If the result is blank, return False.
- Parse and validate basic structure.
- If structural validation fails, return False.
- Extract the normalized domain.
- If allowed_domains is provided, normalize the allowlist and test exact membership.
- Return True if membership succeeds or if no allowlist is configured.
- Otherwise return False.

### Failure flow: blank input
- Input such as empty string or whitespace enters normalization.
- Normalization yields an empty string.
- Function returns False immediately.

### Failure flow: malformed structure
- Input normalizes successfully but fails one or more structural checks.
- No exception should propagate for these cases.
- Function returns False.

### Failure flow: disallowed domain
- Email is structurally valid.
- Domain extracted successfully.
- Domain not present in normalized allowlist.
- Function returns False.

### Failure flow: defensive robustness
- If parsing logic encounters an unexpected condition during splitting or validation, the design intent is to fail closed and return False, not to crash the onboarding path.
- Any future decision to raise for programmer misuse should be constrained to clearly non-business inputs and documented separately from user-input validation behavior.

### Edge cases requiring explicit handling
- Leading and trailing whitespace around email.
- Uppercase or mixed-case addresses and domains.
- Empty allowlist.
- Multiple @ characters.
- Consecutive dots in the domain.
- Missing top-level domain.
- Single-character local part.
- Subdomains versus exact parent-domain membership.
- Inputs that are technically string-typed but operationally unusable, such as whitespace around the @ boundary after trimming.

## 8. Risks and Mitigations

- Risk: Ambiguity in basic email structure.
  - Mitigation: Define and approve a constrained, business-oriented structural policy before implementation.
- Risk: Conflict between team standard raise meaningful exceptions and TODO requirement return False.
  - Mitigation: Approve a function-specific exception policy: return False for invalid business input, and only consider exceptions for explicit programmer misuse.
- Risk: Over-validation rejects legitimate but uncommon addresses.
  - Mitigation: Keep validation intentionally basic and avoid exotic restrictions on the local part unless required.
- Risk: Under-validation accepts malformed addresses that should be blocked.
  - Mitigation: Require tests for representative malformed patterns.
- Risk: Domain authorization semantics are misinterpreted.
  - Mitigation: Approve exact-match behavior explicitly.
- Risk: Hidden configuration hygiene issues in allowed_domains.
  - Mitigation: Normalize case consistently and decide whether allowlist whitespace normalization is in scope.

### Non-functional requirements
- Readability: logic should remain understandable in a training file.
- Determinism: same input always yields same output.
- Safety: invalid user input must not crash the function.
- Testability: each stage should be independently reasoned about and covered by deterministic tests.
- Maintainability: future changes such as subdomain policy or stricter validation should fit separated validation stages.

## 9. Open Questions

- Should non-string email inputs be treated as False, or should they raise TypeError as programmer misuse despite the non-crashing requirement?
- Should allowed_domains entries be normalized only for case, or also trimmed for surrounding whitespace?
- Is exact domain membership the approved business rule, or should example.com also authorize sub.example.com?
- Should the validator explicitly reject consecutive dots in the local part as well as the domain, or is that beyond intended basic scope?
- Are internationalized domain names or Unicode mailbox names out of scope for this training exercise?

## 10. Handoff To Planning Agent

Plan the solution around these capability areas:
- Validation policy definition: codify the approved interpretation of basic email structure and exception-versus-boolean behavior.
- API contract preservation: keep the public signature and boolean return semantics unchanged.
- Internal decomposition: structure implementation around normalization, structural validation, and optional domain authorization.
- Deterministic test design: cover valid inputs, blank inputs, malformed structures, mixed-case normalization, empty allowlist behavior, and disallowed domains.
- Review checkpoints: confirm exact-domain policy, treatment of programmer misuse, and whether allowlist whitespace normalization is in scope.
