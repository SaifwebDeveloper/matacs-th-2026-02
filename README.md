# MATACS-TH-2026-02: AI Proposal Triage Design

**Full name:** Saif Ur Rehman  
**Assessment reference:** MATACS-TH-2026-02  
**Time actually spent:** Approximately 80 minutes

## Overview

This project designs an AI-assisted proposal triage process for evaluating contractor proposals for a commercial rooftop solar installation. Administrators configure evaluation criteria and weights, reviewers upload proposals and select a category, and the system produces an evidence-based ranking for human review.

AI assists with extracting facts from unstructured proposal documents. Deterministic code applies eligibility rules, calculates scores, ranks eligible proposals, and records the results. The system recommends an order but does not make the final award decision.

## How I Used AI Tools

I used ChatGPT to understand the assessment requirements, refine the proposal triage process, clarify the separation between AI extraction and rule-based scoring, and improve the assessment write-up and documentation. I used Claude to assist with developing, reviewing, and testing the Python scoring code and checking its logic against the expected sample results. I reviewed the outputs and made decisions to align the work with the assessment requirements.

**Where I disagreed with or corrected the AI:** I chose to flag Proposal C for human review rather than automatically disqualifying it because of the embedded instruction. I also kept Proposal D out of the ranked results because its missing completion timeline prevents confirmation of the 16-week requirement. These decisions preserve human oversight and ensure that missing or manipulative text does not replace the defined evaluation criteria.

## Repository Files

- [`WRITEUP.md`](WRITEUP.md): Answers to the five assessment questions, covering AI versus rules, consistency, human oversight, changing criteria, and risks.
- [`diagram/process-flow.png`](diagram/process-flow.png): Process-flow diagram showing the proposal evaluation workflow, AI and rule-based steps, and human checkpoints.
- [`PROMPTS.md`](PROMPTS.md): AI extraction prompt and optional prompt for wording concise evaluation reasons.
- [`ranking.json`](ranking.json): Expected evaluation results for proposals A to E, including rankings, scores, and review statuses.
- [`prototype/score.py`](prototype/score.py): Python script implementing rule-based validation, scoring, eligibility checks, and ranking using the supplied sample facts. It does not make AI API calls or require an API key.
- [`prototype/make_diagram.py`](prototype/make_diagram.py): Python script used to generate the process-flow diagram.

## How to Run the Scoring Prototype

**Requirements:** Python 3.

From the repository root, run:

```bash
python3 prototype/score.py
```

On Windows, you can also run:

```bash
python prototype/score.py
```

The prototype calculates scores using the configured formulas and evaluates the supplied sample facts. It runs locally and does not require an external AI service.

## Sample Result

| Proposal | Result | Score |
|---|---|---:|
| A | Ranked 1st | 89.3 |
| E | Ranked 2nd | 77.9 |
| C | Flagged for human review | Not published |
| D | Flagged for missing timeline | Not published |
| B | Ineligible under the stated licence rule | Not published |

Proposal C's approximate diagnostic score is 69.9, but it remains flagged rather than receiving an official rank. Proposal D requires timeline clarification before ranking. Proposal B does not meet the stated mandatory licence requirement.

## Important Design Principles

- Evaluation criteria and weights are configurable and versioned rather than hard-coded.
- Extracted facts should be supported by evidence from the original proposal.
- Missing information is flagged instead of invented.
- Scores are calculated using documented, deterministic formulas.
- Suspicious instructions inside proposals are treated as untrusted content.
- Changes to criteria do not silently modify historical results.
- An authorised human reviewer makes the final award decision.
