# AI Proposal Triage
**Assessment Reference:** MATACS-TH-2026-02

## Assumptions

The evaluation criteria and weights are configurable through admin screens and are stored as versioned settings. Since the brief does not prescribe scoring formulas, the formulas used in this prototype are documented defaults. “Within the last five years” is measured relative to the proposal evaluation date. Where dates or claims cannot be verified from the proposal, the system flags them for human review rather than assuming they are correct.

## 1. AI vs. Rules

AI is used to extract structured facts from proposal documents, including licence details, price, installation experience, completion time, warranties, and team arrangements. Each extracted fact must include an exact supporting quotation from the source document. AI may optionally help phrase a concise explanation, but it does not determine scores or select a winner.

Plain code handles document text extraction, input validation, mandatory pass/fail checks, scoring calculations, ranking, flagging, and audit logging. Rule-based checks also identify suspicious instructions directed at automated reviewers.

This separation is deliberate. AI can help interpret unstructured proposal text, while deterministic code ensures that financial calculations, eligibility rules, and rankings follow the same documented logic.

## 2. Consistency and Explainability

Criteria, weights, scoring formulas, extraction prompts, and relevant model details are versioned. The same validated facts and configuration produce the same scores and ranking. Extracted results are cached against each file's hash so that rerunning the evaluation does not unnecessarily repeat AI extraction. If a fresh extraction is requested, differences are highlighted for review.

The reviewer interface displays each proposal's extracted values, supporting quotations, criterion weights, individual scores, total score, eligibility status, and flags. This makes it possible to understand how a result was produced and verify it against the original proposal.

The default formulas are:

- **Experience (30%):** Score proportional to qualifying installations, capped at 12 installations.
- **Price (25%):** Score proportional to the lowest eligible proposal price divided by the proposal's price.
- **Timeline (15%):** Full marks at eight weeks or less, decreasing linearly to zero at 16 weeks. Missing or over-limit timelines are flagged for review.
- **Warranty (15%):** Panel and workmanship warranty scores contribute equally, capped at 25 and 15 years respectively.
- **Team and approach (15%):** Four equally weighted checklist items: named project lead, crew, safety plan, and monitoring plan.

The mandatory checks require the bidder's stated Ontario electrical contractor licence and confirmed WSIB clearance and $5 million liability insurance. A price above the $260,000 budget ceiling does not fail a proposal, because price is a weighted criterion; it is flagged for human review instead. These rules are applied before ranking.

## 3. Human in the Loop

A reviewer examines the ranked, flagged, and ineligible lists before making a decision. They can verify extracted facts, correct extraction errors with supporting evidence, request clarification from bidders, and record justified overrides. Missing or ambiguous information is not silently guessed.

Suspicious instructions, validation failures, and unresolved mandatory requirements are sent for human review according to the configured policy. The system provides a recommendation only; the final award decision always belongs to an authorised person.

The audit log records the proposal file hash, criteria version, prompt and model versions, extracted facts, supporting quotations, criterion scores, final status, flags, timestamps, and reviewer actions. Overrides include the responsible user and a written reason.

## 4. Changing Criteria

Administrators edit criteria through the configuration interface. Each saved change creates a new version, and every evaluation records the version used. Existing results are not silently altered when criteria change.

Reviewers can request re-scoring under the new version. Cached facts can be reused when they satisfy the new criteria; if a new criterion requires information that was not previously extracted, the relevant extraction must be performed and verified. Results produced under different criteria versions are not mixed in the same ranking. Historical scores and overrides remain available for audit.

## 5. Risks and Safeguards

| Risk | Safeguard |
|---|---|
| Incorrect extraction | Require supporting quotations, validate values in code, and let reviewers compare each value with the source document. |
| Fabricated or missing facts | Instruct the extractor to return null when information is not stated. Flag missing evidence instead of inventing values. |
| Prompt injection or manipulation | Treat proposal content as untrusted data. Ignore instructions embedded in documents and flag suspicious content for review. |
| Bias | Use only configured criteria and evidence-based checklist items. AI does not award points. Conduct periodic human checks for inconsistent outcomes. |
| Incorrect eligibility decisions | Show the exact failed requirement and supporting evidence. Allow authorised reviewers to resolve disputes with documented justification. |
| Cost and latency | Limit document size, avoid unnecessary AI calls, cache extraction results, and perform scoring with ordinary code. |
| Privacy and access | Restrict access to proposal documents and audit records, and send only the information necessary for extraction to the AI service. |
| Over-reliance on rankings | Display rankings as recommendations, expose scores and evidence, flag unresolved issues, and require human confirmation before an award. |

For example, Proposal B does not satisfy the stated licence requirement because its proposal leaves the licensed electrical subcontractor to be confirmed after award. Proposal D has no stated completion time, so its compliance with the 16-week limit cannot be confirmed. Proposal C contains an instruction attempting to manipulate the ranking; that instruction is ignored, and the proposal is flagged for human review rather than automatically disqualified.

## Sample Result

Proposal A ranks first with a score of 89.3, and Proposal E ranks second with 77.9. Proposal B is ineligible under the stated mandatory licence rule. Proposals C and D are flagged for human review because of suspicious embedded instructions and missing timeline information, respectively. The reviewer retains responsibility for resolving flags and making the final award decision.
