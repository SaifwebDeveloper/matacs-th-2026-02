
from copy import deepcopy
from math import isfinite


# In production, load this configuration from admin screens and store
# each approved configuration as a versioned record.
CONFIG = {
    "version": 1,
    "budget_ceiling": 260000,
    "max_weeks": 16,
    "full_marks_weeks": 8,
    "exp_full_count": 12,
    "panel_full_years": 25,
    "work_full_years": 15,
    "weights": {
        "experience": 30,
        "price": 25,
        "timeline": 15,
        "warranty": 15,
        "team": 15,
    },
}


# These facts represent the output expected from the extraction prompt.
# The scoring engine must not treat instructions inside a proposal as
# instructions to itself.
#
# Team fields:
# [named_project_lead, crew_stated, safety_plan, monitoring_plan]
#
# For experience, installs must represent qualifying commercial
# installations of 100 kW or more within the required five-year window.
# Verify extracted counts against the original proposal before production use.

FACTS = {
    "A": {
        "licence": True,
        "wsib_insurance": True,
        "installs": 14,
        "price": 238000,
        "weeks": 12,
        "panel": 25,
        "work": 10,
        "team": [1, 1, 1, 1],
        "injection": False,
    },
    "B": {
        "licence": False,
        "wsib_insurance": True,
        "installs": 6,
        "price": 189500,
        "weeks": 10,
        "panel": 25,
        "work": 5,
        "team": [0, 0, 0, 0],
        "injection": False,
    },
    "C": {
        "licence": True,
        "wsib_insurance": True,
        "installs": 9,
        "price": 244000,
        "weeks": 14,
        "panel": 25,
        "work": 10,
        "team": [1, 1, 0, 0],
        "injection": True,
    },
    "D": {
        "licence": True,
        "wsib_insurance": True,
        "installs": 11,
        "price": 231000,
        "weeks": None,
        "panel": 25,
        "work": 10,
        "team": [1, 0, 1, 0],
        "injection": False,
    },
    "E": {
        "licence": True,
        "wsib_insurance": True,
        "installs": 8,
        "price": 242500,
        "weeks": 13,
        "panel": 25,
        "work": 12,
        "team": [1, 1, 1, 1],
        "injection": False,
    },
}


def validate_config(config):
    """Validate admin configuration before scoring."""
    weights = config["weights"]

    expected_criteria = {
        "experience",
        "price",
        "timeline",
        "warranty",
        "team",
    }

    if set(weights) != expected_criteria:
        raise ValueError("The configured weighted criteria are invalid.")

    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value >= 0
        for value in weights.values()
    ):
        raise ValueError("Weights must be finite, non-negative numbers.")

    if abs(sum(weights.values()) - 100) > 1e-9:
        raise ValueError("Weighted criteria must add up to 100.")

    if config["budget_ceiling"] <= 0:
        raise ValueError("Budget ceiling must be positive.")

    if config["exp_full_count"] <= 0:
        raise ValueError("Experience threshold must be positive.")

    if config["panel_full_years"] <= 0:
        raise ValueError("Panel warranty threshold must be positive.")

    if config["work_full_years"] <= 0:
        raise ValueError("Workmanship warranty threshold must be positive.")

    if not 0 < config["full_marks_weeks"] < config["max_weeks"]:
        raise ValueError("Timeline thresholds are invalid.")


def validate_facts(facts):
    """Validate extracted data types without inventing missing values."""
    for proposal_id, fact in facts.items():
        for field in ("licence", "wsib_insurance", "injection"):
            if not isinstance(fact.get(field), bool):
                raise ValueError(
                    f"Proposal {proposal_id}: {field} must be True or False."
                )

        for field in ("installs", "price", "panel", "work"):
            value = fact.get(field)

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not isfinite(value)
                or value < 0
            ):
                raise ValueError(
                    f"Proposal {proposal_id}: invalid {field} value."
                )

        weeks = fact.get("weeks")

        if weeks is not None and (
            not isinstance(weeks, (int, float))
            or isinstance(weeks, bool)
            or not isfinite(weeks)
            or weeks < 0
        ):
            raise ValueError(
                f"Proposal {proposal_id}: invalid weeks value."
            )

        team = fact.get("team")

        if (
            not isinstance(team, (list, tuple))
            or len(team) != 4
            or any(value not in (0, 1) for value in team)
        ):
            raise ValueError(
                f"Proposal {proposal_id}: team must contain four 0/1 values."
            )


def mandatory_failures(fact, config):
    """Return reasons why a proposal is ineligible.

    Only the brief's two mandatory criteria can fail a proposal here:
    the bidder-held licence, and WSIB clearance plus $5M liability
    insurance. Price is a weighted criterion, so a price above the
    budget ceiling is flagged for human review in evaluate_proposal,
    not treated as a mandatory failure.
    """
    failures = []

    if not fact["licence"]:
        failures.append(
            "Ontario electrical contractor licence is not confirmed "
            "as held by the bidder and stated in the proposal."
        )

    if not fact["wsib_insurance"]:
        failures.append(
            "WSIB clearance and $5M liability insurance are not both confirmed."
        )

    return failures


def score(fact, reference_price, config=CONFIG):
    """
    Return weighted criterion scores.

    reference_price is the lowest bid that passes the mandatory checks.

    A missing timeline receives None. The final total must not be
    published as complete when a criterion score is missing.
    """
    weights = config["weights"]
    scores = {}

    scores["experience"] = (
        weights["experience"]
        * min(fact["installs"], config["exp_full_count"])
        / config["exp_full_count"]
    )

    scores["price"] = (
        weights["price"] * reference_price / fact["price"]
    )

    weeks = fact["weeks"]

    if weeks is None:
        scores["timeline"] = None
    else:
        span = config["max_weeks"] - config["full_marks_weeks"]

        timeline_ratio = (
            config["max_weeks"] - weeks
        ) / span

        timeline_ratio = max(0, min(1, timeline_ratio))

        scores["timeline"] = weights["timeline"] * timeline_ratio

    panel_ratio = min(
        fact["panel"], config["panel_full_years"]
    ) / config["panel_full_years"]

    work_ratio = min(
        fact["work"], config["work_full_years"]
    ) / config["work_full_years"]

    scores["warranty"] = (
        weights["warranty"] * (panel_ratio + work_ratio) / 2
    )

    scores["team"] = (
        weights["team"] * sum(fact["team"]) / 4
    )

    # A partial score is useful for diagnostics, but is not a final score.
    missing_scores = any(value is None for value in scores.values())

    total = None if missing_scores else round(sum(scores.values()), 1)

    return scores, total


def evaluate_proposal(proposal_id, fact, reference_price, config):
    """Evaluate a single proposal and determine its review status."""
    failures = mandatory_failures(fact, config)

    if failures:
        return {
            "proposal": proposal_id,
            "rank": None,
            "status": "ineligible",
            "score": None,
            "criterion_scores": {},
            "reasons": failures,
            "review_required": False,
        }

    scores, total = score(fact, reference_price, config)
    reasons = []

    if fact["injection"]:
        reasons.append(
            "Contains an instruction aimed at manipulating automated "
            "evaluation. The instruction was ignored and the proposal "
            "was flagged for human review."
        )

    if fact["weeks"] is None:
        reasons.append(
            "Completion time is missing. Request clarification before "
            "confirming compliance with the 16-week requirement."
        )
    elif fact["weeks"] > config["max_weeks"]:
        reasons.append(
            "Proposed completion time exceeds the 16-week project limit. "
            "Human review is required."
        )

    if fact["price"] > config["budget_ceiling"]:
        reasons.append(
            f"Total price exceeds the ${config['budget_ceiling']:,.0f} "
            "budget ceiling. Price is a weighted criterion, so this is "
            "flagged for human review rather than failing the proposal."
        )

    if total is None and not reasons:
        reasons.append(
            "One or more required scoring values are missing."
        )

    status = "flagged" if reasons else "ranked"

    return {
        "proposal": proposal_id,
        "rank": None,
        "status": status,
        "score": total,
        "criterion_scores": scores,
        "reasons": reasons,
        "review_required": bool(reasons),
    }


def run(facts=None, config=None):
    """Evaluate all proposals and print a structured, deterministic result."""
    facts = deepcopy(FACTS if facts is None else facts)
    config = deepcopy(CONFIG if config is None else config)

    validate_config(config)
    validate_facts(facts)

    eligible_for_scoring = [
        proposal_id
        for proposal_id, fact in facts.items()
        if not mandatory_failures(fact, config)
    ]

    if not eligible_for_scoring:
        print("No proposals passed the mandatory checks.")
        return []

    # The reference price is the lowest bid among eligible proposals.
    reference_price = min(
        facts[proposal_id]["price"]
        for proposal_id in eligible_for_scoring
    )

    ranked = []
    flagged = []
    ineligible = []

    for proposal_id, fact in facts.items():
        result = evaluate_proposal(
            proposal_id,
            fact,
            reference_price,
            config,
        )

        if result["status"] == "ranked":
            ranked.append(result)
        elif result["status"] == "flagged":
            flagged.append(result)
        else:
            ineligible.append(result)

    # Only proposals with complete scoring and no review flags are ranked.
    ranked.sort(key=lambda item: (-item["score"], item["proposal"]))

    for rank, result in enumerate(ranked, start=1):
        result["rank"] = rank

    results = ranked + flagged + ineligible

    print(f"Configuration version: {config['version']}")
    print(f"Budget ceiling: ${config['budget_ceiling']:,.2f} CAD")
    print(f"Reference price: ${reference_price:,.2f} CAD")
    print()

    for result in results:
        print({
            "proposal": result["proposal"],
            "rank": result["rank"],
            "status": result["status"],
            "score": result["score"],
            "criterion_scores": {
                key: (
                    None if value is None else round(value, 2)
                )
                for key, value in result["criterion_scores"].items()
            },
            "reasons": result["reasons"],
            "review_required": result["review_required"],
        })

    return results


if __name__ == "__main__":
    run()
