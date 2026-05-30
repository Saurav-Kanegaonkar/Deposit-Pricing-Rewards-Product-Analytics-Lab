import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"
SEED = 20260529


random.seed(SEED)
for path in [DATA, OUTPUT, ANALYSIS]:
    path.mkdir(parents=True, exist_ok=True)


TIER_RULES = [
    {
        "tier": "Level 1",
        "min_balance": 0,
        "max_balance": 9999,
        "loyalty_bonus_pct": 10,
        "atm_waivers": 0,
        "pos_limit": 3000,
        "primary_message": "Starter relationship value",
    },
    {
        "tier": "Level 2",
        "min_balance": 10000,
        "max_balance": 24999,
        "loyalty_bonus_pct": 20,
        "atm_waivers": 1,
        "pos_limit": 3000,
        "primary_message": "First balance milestone",
    },
    {
        "tier": "Level 3",
        "min_balance": 25000,
        "max_balance": 49999,
        "loyalty_bonus_pct": 30,
        "atm_waivers": 3,
        "pos_limit": 3000,
        "primary_message": "Deepening opportunity",
    },
    {
        "tier": "Level 4",
        "min_balance": 50000,
        "max_balance": 99999,
        "loyalty_bonus_pct": 40,
        "atm_waivers": 5,
        "pos_limit": 3000,
        "primary_message": "High-balance retention",
    },
    {
        "tier": "Premier",
        "min_balance": 100000,
        "max_balance": 500000,
        "loyalty_bonus_pct": 50,
        "atm_waivers": 99,
        "pos_limit": 25000,
        "primary_message": "Premium relationship protection",
    },
]


MARKETS = [
    "Southeast metro",
    "Mid-Atlantic metro",
    "Florida growth market",
    "Texas expansion market",
    "Carolinas core market",
    "Digital national",
]

SEGMENTS = [
    "Digital-first households",
    "Branch-assisted households",
    "Early-tenure checking",
    "Emerging affluent",
    "Premier relationship",
    "Debit-engaged households",
    "Small business owners",
    "Savings rate shoppers",
]

PRODUCTS = [
    "Everyday checking",
    "Relationship checking",
    "Money market",
    "Savings",
    "Certificate renewal",
    "Debit rewards",
]

OWNER_POOL = [
    "Deposit product",
    "Pricing analytics",
    "Rewards platform",
    "Marketing",
    "Servicing enablement",
    "Risk and compliance",
    "Distribution",
    "Technology",
]


def clamp(value, low, high):
    return max(low, min(high, value))


def pct(value):
    return round(value * 100, 1)


def weighted_choice(items):
    total = sum(weight for _, weight in items)
    point = random.uniform(0, total)
    current = 0
    for item, weight in items:
        current += weight
        if current >= point:
            return item
    return items[-1][0]


def balance_for_tier(tier):
    if tier["tier"] == "Premier":
        return random.randint(100000, 285000)
    return random.randint(tier["min_balance"], tier["max_balance"])


def make_cohorts():
    cohorts = []
    for idx in range(1, 49):
        tier = weighted_choice(
            [
                (TIER_RULES[0], 25),
                (TIER_RULES[1], 20),
                (TIER_RULES[2], 18),
                (TIER_RULES[3], 16),
                (TIER_RULES[4], 21),
            ]
        )
        product = random.choice(PRODUCTS)
        segment = random.choice(SEGMENTS)
        market = random.choice(MARKETS)
        accounts = random.randint(620, 11800)
        avg_balance = balance_for_tier(tier)
        if product == "Debit rewards":
            avg_balance = int(avg_balance * random.uniform(0.55, 1.15))
        if product == "Certificate renewal":
            avg_balance = int(avg_balance * random.uniform(1.2, 1.8))
        total_balance = accounts * avg_balance

        rate_base = {
            "Everyday checking": 0.01,
            "Relationship checking": 0.05,
            "Money market": 2.1,
            "Savings": 0.12,
            "Certificate renewal": 3.8,
            "Debit rewards": 0.01,
        }[product]
        current_apy = clamp(random.gauss(rate_base, 0.18), 0.01, 4.9)
        competitor_apy = clamp(current_apy + random.gauss(0.34, 0.46), 0.01, 5.2)
        rate_gap_bps = max(0, round((competitor_apy - current_apy) * 100))

        direct_deposit_rate = clamp(random.gauss(0.58, 0.18), 0.18, 0.94)
        rewards_utilization = clamp(random.gauss(0.39, 0.2) + tier["loyalty_bonus_pct"] / 250, 0.04, 0.91)
        debit_txn_per_account = clamp(random.gauss(13, 4.8) + rewards_utilization * 8, 1.5, 35)
        complaint_rate = clamp(random.gauss(1.4, 0.9) + rate_gap_bps / 125, 0.1, 9.8)
        data_quality = clamp(random.gauss(87, 8) - complaint_rate * 1.4, 51, 99)
        risk_control = clamp(random.gauss(84, 9) - (rate_gap_bps / 35), 45, 99)
        growth_rate = clamp(random.gauss(0.018, 0.032) - rate_gap_bps / 10000 + rewards_utilization / 100, -0.08, 0.13)
        attrition_risk = clamp(
            18
            + rate_gap_bps * 0.11
            + complaint_rate * 4.2
            - rewards_utilization * 12
            - direct_deposit_rate * 8
            + random.gauss(0, 4),
            5,
            88,
        )
        balances_at_risk = int(total_balance * attrition_risk / 100 * random.uniform(0.18, 0.36))
        rule_complexity = clamp(
            35 + tier["loyalty_bonus_pct"] * 0.6 + random.gauss(0, 14) + (10 if product in ["Money market", "Certificate renewal"] else 0),
            18,
            96,
        )
        priority_score = clamp(
            attrition_risk * 0.32
            + min(rate_gap_bps, 180) * 0.18
            + (100 - data_quality) * 0.18
            + (100 - risk_control) * 0.14
            + math.log10(max(balances_at_risk, 1)) * 5.6
            + (1 - rewards_utilization) * 10,
            0,
            100,
        )

        if risk_control < 65:
            decision = "Hold for risk review"
        elif data_quality < 72:
            decision = "Fix measurement gap"
        elif rate_gap_bps > 85 and balances_at_risk > 12_000_000:
            decision = "Build pricing test"
        elif rewards_utilization < 0.42 and tier["loyalty_bonus_pct"] >= 20:
            decision = "Launch reward nudge"
        elif direct_deposit_rate < 0.48:
            decision = "Run direct deposit prompt"
        else:
            decision = "Monitor in monthly review"

        cohorts.append(
            {
                "cohort_id": f"DPR{idx:03d}",
                "market": market,
                "segment": segment,
                "product": product,
                "benefit_tier": tier["tier"],
                "accounts": accounts,
                "avg_monthly_balance": avg_balance,
                "total_balance": total_balance,
                "current_apy": round(current_apy, 2),
                "competitor_apy": round(competitor_apy, 2),
                "rate_gap_bps": rate_gap_bps,
                "deposit_growth_pct": pct(growth_rate),
                "direct_deposit_rate": pct(direct_deposit_rate),
                "rewards_utilization": pct(rewards_utilization),
                "debit_txn_per_account": round(debit_txn_per_account, 1),
                "complaint_rate_per_10k": round(complaint_rate, 1),
                "data_quality_score": round(data_quality, 1),
                "risk_control_score": round(risk_control, 1),
                "rule_complexity_score": round(rule_complexity, 1),
                "attrition_risk_score": round(attrition_risk, 1),
                "balances_at_risk": balances_at_risk,
                "priority_score": round(priority_score, 1),
                "recommended_decision": decision,
                "primary_owner": random.choice(OWNER_POOL),
            }
        )
    return sorted(cohorts, key=lambda row: row["priority_score"], reverse=True)


EPIC_TEMPLATES = [
    {
        "epic": "Balance-tier benefit transparency",
        "feature": "Monthly level evaluation and client explanation",
        "persona": "Relationship banker",
        "metric": "benefit upgrade rate",
    },
    {
        "epic": "Competitive pricing exception workflow",
        "feature": "Rate-gap review packet and approval lane",
        "persona": "Deposit pricing analyst",
        "metric": "balances retained",
    },
    {
        "epic": "Rewards activation rules",
        "feature": "Debit and credit loyalty bonus eligibility cues",
        "persona": "Rewards platform owner",
        "metric": "reward utilization",
    },
    {
        "epic": "Campaign eligibility and suppression",
        "feature": "Acquisition, deepening, and retention targeting",
        "persona": "Marketing partner",
        "metric": "incremental funded accounts",
    },
    {
        "epic": "Servicing and complaint resolution",
        "feature": "Client issue taxonomy and enablement document set",
        "persona": "Servicing teammate",
        "metric": "complaint repeat rate",
    },
    {
        "epic": "Risk-controlled pricing release",
        "feature": "Legal, risk, compliance, and operations signoff",
        "persona": "Risk partner",
        "metric": "control exception rate",
    },
]


def make_stories(cohorts):
    stories = []
    for idx, template in enumerate(EPIC_TEMPLATES, start=1):
        for story_num in range(1, 5):
            cohort = cohorts[(idx * 3 + story_num) % len(cohorts)]
            acceptance = random.randint(4, 9)
            uat = clamp(random.gauss(0.78, 0.16), 0.22, 0.99)
            dependency_count = random.randint(1, 5)
            open_questions = random.randint(0, 6)
            high_defects = 0 if random.random() > 0.22 else random.randint(1, 3)
            signoff = weighted_choice(
                [
                    ("Approved", 34),
                    ("In review", 34),
                    ("Needs legal review", 12),
                    ("Needs risk review", 14),
                    ("Blocked", 6),
                ]
            )
            readiness = clamp(
                uat * 45
                + acceptance * 4.2
                + cohort["data_quality_score"] * 0.16
                + cohort["risk_control_score"] * 0.14
                - dependency_count * 5.5
                - open_questions * 3.8
                - high_defects * 12,
                0,
                100,
            )
            if readiness >= 78 and signoff == "Approved":
                decision = "Ready for release"
            elif high_defects > 0 or signoff == "Blocked":
                decision = "Escalate blockers"
            elif signoff in ["Needs legal review", "Needs risk review"]:
                decision = "Route for control review"
            else:
                decision = "Groom next sprint"

            stories.append(
                {
                    "story_id": f"DPRE-{idx}{story_num:02d}",
                    "epic": template["epic"],
                    "feature": template["feature"],
                    "user_story": f"As a {template['persona']}, I need {template['feature'].lower()} for {cohort['segment'].lower()} so I can improve {template['metric']}.",
                    "linked_cohort": cohort["cohort_id"],
                    "acceptance_criteria": acceptance,
                    "uat_pass_rate": pct(uat),
                    "dependency_count": dependency_count,
                    "open_questions": open_questions,
                    "high_severity_defects": high_defects,
                    "partner_signoff": signoff,
                    "readiness_score": round(readiness, 1),
                    "release_decision": decision,
                    "owner": random.choice(OWNER_POOL),
                }
            )
    return sorted(stories, key=lambda row: row["readiness_score"])


def make_campaigns(cohorts):
    campaigns = []
    objectives = ["Acquisition", "Deepening", "Retention", "Debit engagement", "Servicing education"]
    channels = ["Email", "Mobile app", "Branch prompt", "Contact center", "Paid search", "Debit merchant offer"]
    for idx, cohort in enumerate(cohorts[:30], start=1):
        objective = weighted_choice(
            [
                ("Retention", 28 if cohort["attrition_risk_score"] > 45 else 12),
                ("Deepening", 24),
                ("Debit engagement", 18 if cohort["product"] == "Debit rewards" else 10),
                ("Acquisition", 16),
                ("Servicing education", 14 if cohort["complaint_rate_per_10k"] > 2.4 else 8),
            ]
        )
        expected_lift = clamp(random.gauss(0.028, 0.014) + cohort["priority_score"] / 4500, 0.004, 0.085)
        suppression_rate = clamp(random.gauss(0.11, 0.05) + (100 - cohort["risk_control_score"]) / 600, 0.02, 0.42)
        eligible_accounts = int(cohort["accounts"] * (1 - suppression_rate))
        compliance_status = weighted_choice(
            [
                ("Approved", 42),
                ("Disclosure copy review", 28),
                ("Fairness review", 14),
                ("Risk exception review", 12),
                ("Blocked", 4),
            ]
        )
        readiness = clamp(
            52
            + cohort["data_quality_score"] * 0.2
            + cohort["risk_control_score"] * 0.14
            + expected_lift * 180
            - suppression_rate * 35
            - (18 if compliance_status == "Blocked" else 0)
            - (10 if "review" in compliance_status.lower() else 0),
            0,
            100,
        )
        if compliance_status == "Approved" and readiness >= 78:
            decision = "Launch"
        elif compliance_status == "Blocked":
            decision = "Do not launch"
        elif readiness >= 68:
            decision = "Prepare for next cycle"
        else:
            decision = "Revise targeting"
        campaigns.append(
            {
                "campaign_id": f"CMP{idx:03d}",
                "linked_cohort": cohort["cohort_id"],
                "objective": objective,
                "channel": random.choice(channels),
                "eligible_accounts": eligible_accounts,
                "expected_lift_pct": pct(expected_lift),
                "suppression_rate_pct": pct(suppression_rate),
                "complaint_driver": random.choice(
                    [
                        "Benefit level confusion",
                        "Rate comparison question",
                        "Reward redemption confusion",
                        "Direct deposit qualification",
                        "Fee waiver explanation",
                        "Debit offer eligibility",
                    ]
                ),
                "enablement_doc": random.choice(
                    [
                        "Benefit level FAQ",
                        "Pricing exception playbook",
                        "Rewards eligibility guide",
                        "Direct deposit talking points",
                        "Complaint escalation checklist",
                    ]
                ),
                "compliance_status": compliance_status,
                "launch_readiness": round(readiness, 1),
                "decision": decision,
                "owner": random.choice(["Marketing", "Deposit product", "Servicing enablement", "Distribution"]),
            }
        )
    return sorted(campaigns, key=lambda row: row["launch_readiness"], reverse=True)


def make_controls(cohorts, stories, campaigns):
    controls = []
    dimensions = [
        "Benefit tier calculation",
        "Combined balance feed",
        "APY comparison table",
        "Reward redemption mapping",
        "Debit transaction eligibility",
        "Direct deposit qualification",
        "Campaign suppression logic",
        "Complaint taxonomy",
        "Legal disclosure version",
        "Risk approval evidence",
        "Channel training document",
        "UAT traceability",
    ]
    for idx, dimension in enumerate(dimensions, start=1):
        affected = random.randint(3, 16)
        defect_rate = clamp(random.gauss(0.06, 0.04), 0.0, 0.22)
        owner = random.choice(OWNER_POOL)
        evidence = weighted_choice(
            [
                ("Complete", 42),
                ("Partial", 34),
                ("Missing owner signoff", 14),
                ("Needs retest", 10),
            ]
        )
        severity = weighted_choice(
            [
                ("Low", 28),
                ("Medium", 42),
                ("High", 23 if evidence != "Complete" else 10),
                ("Critical", 7 if evidence in ["Missing owner signoff", "Needs retest"] else 2),
            ]
        )
        score = clamp(
            100
            - defect_rate * 230
            - affected * 1.8
            - {"Low": 4, "Medium": 12, "High": 24, "Critical": 38}[severity]
            - (18 if evidence != "Complete" else 0),
            0,
            100,
        )
        action = "Accept"
        if severity == "Critical" or score < 55:
            action = "Escalate before release"
        elif evidence != "Complete" or score < 72:
            action = "Remediate this sprint"
        elif severity == "Medium":
            action = "Monitor with owner"
        controls.append(
            {
                "control_id": f"CTL{idx:03d}",
                "dimension": dimension,
                "affected_items": affected,
                "defect_rate_pct": pct(defect_rate),
                "evidence_status": evidence,
                "severity": severity,
                "control_score": round(score, 1),
                "recommended_action": action,
                "owner": owner,
            }
        )
    return sorted(controls, key=lambda row: row["control_score"])


def write_csv(path, rows):
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    cohorts = make_cohorts()
    stories = make_stories(cohorts)
    campaigns = make_campaigns(cohorts)
    controls = make_controls(cohorts, stories, campaigns)

    write_csv(DATA / "benefit_tier_rules.csv", TIER_RULES)
    write_csv(DATA / "deposit_cohorts.csv", cohorts)
    write_csv(DATA / "epic_story_traceability.csv", stories)
    write_csv(DATA / "campaign_issue_packet.csv", campaigns)
    write_csv(DATA / "risk_control_checks.csv", controls)

    write_csv(OUTPUT / "cohort_priority_queue.csv", cohorts[:25])
    write_csv(OUTPUT / "story_readiness_queue.csv", stories)
    write_csv(OUTPUT / "campaign_decision_packet.csv", campaigns)
    write_csv(OUTPUT / "risk_control_queue.csv", controls)

    total_balance = sum(row["total_balance"] for row in cohorts)
    balance_at_risk = sum(row["balances_at_risk"] for row in cohorts)
    launchable_campaigns = sum(1 for row in campaigns if row["decision"] == "Launch")
    blocked_stories = sum(1 for row in stories if row["release_decision"] in ["Escalate blockers", "Route for control review"])
    high_controls = sum(1 for row in controls if row["severity"] in ["High", "Critical"])
    top = cohorts[0]

    summary = {
        "seed": SEED,
        "cohorts": len(cohorts),
        "stories": len(stories),
        "campaigns": len(campaigns),
        "controls": len(controls),
        "total_balance": total_balance,
        "balance_at_risk": balance_at_risk,
        "avg_priority": round(sum(row["priority_score"] for row in cohorts) / len(cohorts), 1),
        "avg_story_readiness": round(sum(row["readiness_score"] for row in stories) / len(stories), 1),
        "launchable_campaigns": launchable_campaigns,
        "blocked_stories": blocked_stories,
        "high_controls": high_controls,
        "top_cohort": top,
    }

    payload = {
        "summary": summary,
        "tierRules": TIER_RULES,
        "cohorts": cohorts[:18],
        "stories": stories[:18],
        "campaigns": campaigns[:18],
        "controls": controls,
        "findings": [
            f"{top['cohort_id']} is the top pricing and rewards decision because it combines {top['rate_gap_bps']} bps of competitive rate gap, {top['complaint_rate_per_10k']} complaints per 10k accounts, and ${top['balances_at_risk']:,} of modeled balances at risk.",
            f"{blocked_stories} stories need blocker or control review before a release decision, which makes traceability more valuable than another static metric view.",
            f"{launchable_campaigns} campaign packets are ready to launch after suppression and compliance checks, while the rest need targeting or disclosure work.",
            f"{high_controls} risk or data controls are high severity or critical and should be addressed before scaling a pricing or rewards enhancement.",
        ],
    }

    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUTPUT / "app_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    (ANALYSIS / "executive_findings.md").write_text(
        f"""# Executive Findings

## What I analyzed

I generated a deterministic synthetic operating model for a deposit pricing and rewards engine product team. The model connects benefit tiers, deposit cohorts, rate gaps, rewards utilization, complaint drivers, campaign readiness, epic and story traceability, and risk controls.

## Findings

- The highest-priority cohort is {top["cohort_id"]}, a {top["segment"]} cohort in {top["market"]}, with a priority score of {top["priority_score"]}.
- Modeled balances at risk are ${balance_at_risk:,} across ${total_balance:,} in synthetic deposit balances.
- {blocked_stories} user stories require blocker resolution or control review before release.
- {launchable_campaigns} campaign packets are launch-ready after eligibility, suppression, and compliance checks.
- {high_controls} controls are high severity or critical.

## Recommendation

Use the priority queue to select one pricing test, one rewards activation campaign, and one servicing enablement fix for the next product review. Require story-level acceptance criteria, UAT evidence, and risk or legal signoff before moving any pricing or rewards change into release.
""",
        encoding="utf-8",
    )

    (ANALYSIS / "analysis_plan.md").write_text(
        f"""# Analysis Plan

## Product Question

Which deposit pricing and rewards engine opportunities should a product analyst bring to the next cross-functional review, and what evidence is needed before release?

## Method

1. Model deposit cohorts by market, segment, product, balance tier, current APY, competitor APY, direct deposit adoption, rewards utilization, complaints, data quality, and control readiness.
2. Score cohort priority from attrition risk, competitive rate gap, balances at risk, data quality, risk control, and rewards utilization.
3. Translate high-priority cohorts into epics, features, user stories, acceptance criteria, UAT evidence, dependencies, and partner signoff.
4. Build campaign packets with eligible accounts, suppression rates, expected lift, complaint driver, enablement document, compliance status, and launch decision.
5. Audit data and risk controls that could block a pricing or rewards enhancement.

## Current Run

- Seed: {SEED}
- Cohorts: {len(cohorts)}
- Stories: {len(stories)}
- Campaign packets: {len(campaigns)}
- Risk and data controls: {len(controls)}
- Balance at risk: ${balance_at_risk:,}
""",
        encoding="utf-8",
    )

    (ANALYSIS / "sql_checks.sql").write_text(
        """-- Portfolio SQL checks for a deposit pricing and rewards product operating packet.

-- 1. Cohorts where competitive rate gap, complaints, and balances at risk overlap.
select
  cohort_id,
  market,
  segment,
  product,
  benefit_tier,
  rate_gap_bps,
  complaint_rate_per_10k,
  balances_at_risk,
  priority_score,
  recommended_decision
from deposit_cohorts
where rate_gap_bps >= 75
  and complaint_rate_per_10k >= 2.0
order by priority_score desc;

-- 2. User stories that should not move to release.
select
  story_id,
  epic,
  feature,
  readiness_score,
  partner_signoff,
  high_severity_defects,
  release_decision
from epic_story_traceability
where release_decision in ('Escalate blockers', 'Route for control review')
   or high_severity_defects > 0
order by readiness_score asc;

-- 3. Campaign packets ready for marketing execution.
select
  campaign_id,
  linked_cohort,
  objective,
  channel,
  eligible_accounts,
  expected_lift_pct,
  compliance_status,
  launch_readiness,
  decision
from campaign_issue_packet
where decision = 'Launch'
order by launch_readiness desc;

-- 4. Controls requiring remediation before pricing or rewards release.
select
  control_id,
  dimension,
  severity,
  evidence_status,
  control_score,
  recommended_action,
  owner
from risk_control_checks
where recommended_action in ('Escalate before release', 'Remediate this sprint')
order by control_score asc;
""",
        encoding="utf-8",
    )

    (DATA / "README.md").write_text(
        f"""# Data Notes

All source-style data in this folder is synthetic and generated by `scripts/score_operating_data.py` with fixed seed `{SEED}`. It does not represent real bank clients, real accounts, real balances, real campaign results, or real company performance.

The synthetic structure is modeled on common retail banking product mechanics: balance-linked benefit levels, monthly benefit evaluation, APY comparison, debit and rewards engagement, direct deposit qualification, fee or benefit explanation, campaign suppression, complaint handling, and risk or compliance review.

## Tables

- `benefit_tier_rules.csv`: Balance tiers, loyalty bonus levels, ATM waiver counts, card limits, and tier messages.
- `deposit_cohorts.csv`: Synthetic deposit cohorts by market, segment, product, benefit tier, balance, rate gap, rewards utilization, complaint rate, data quality, and control readiness.
- `epic_story_traceability.csv`: Epics, features, user stories, acceptance criteria, UAT pass rates, dependencies, partner signoff, and release decisions.
- `campaign_issue_packet.csv`: Marketing, servicing, and channel action packets with eligibility, suppression, expected lift, complaint driver, enablement document, compliance status, and launch decision.
- `risk_control_checks.csv`: Data quality and risk controls for pricing, rewards, campaign, disclosure, UAT, and channel enablement evidence.
""",
        encoding="utf-8",
    )

    (ROOT / "data_dictionary.md").write_text(
        """# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `data/benefit_tier_rules.csv` | Benefit tier | Balance thresholds, loyalty bonus levels, ATM waivers, card limits, and primary product message. |
| `data/deposit_cohorts.csv` | Deposit cohort | Cohort-level balances, rate gap, rewards utilization, direct deposit adoption, complaints, data quality, control readiness, and recommended decision. |
| `data/epic_story_traceability.csv` | User story | Epics, features, acceptance criteria, UAT coverage, dependencies, defects, partner signoff, readiness score, and release decision. |
| `data/campaign_issue_packet.csv` | Campaign packet | Campaign objective, channel, eligibility, suppression, expected lift, complaint driver, enablement document, compliance status, and launch decision. |
| `data/risk_control_checks.csv` | Control | Risk and data quality dimensions, evidence status, severity, owner, control score, and remediation action. |
| `analysis/outputs/app_payload.json` | App payload | Static JSON used by the interactive workbench. |
| `analysis/outputs/cohort_priority_queue.csv` | Cohort | Ranked pricing and rewards priority queue. |
| `analysis/outputs/story_readiness_queue.csv` | User story | Ranked story readiness and release decision queue. |
| `analysis/outputs/campaign_decision_packet.csv` | Campaign packet | Ranked campaign and issue resolution packet. |
| `analysis/outputs/risk_control_queue.csv` | Control | Ranked controls requiring remediation, monitoring, or acceptance. |
""",
        encoding="utf-8",
    )

    (ROOT / "STATUS.md").write_text(
        """# Status

- Project: Deposit Pricing Rewards Product Analytics Lab
- Status: upgraded through the Portfolio Artifact Upgrade Workflow
- Data: deterministic synthetic product analytics, backlog, campaign, and risk-control model
- Public README: written with company-domain language and no target-company name
""",
        encoding="utf-8",
    )

    print(f"Generated {len(cohorts)} cohorts, {len(stories)} stories, {len(campaigns)} campaigns, and {len(controls)} controls.")
    print(f"Top cohort: {top['cohort_id']} priority_score={top['priority_score']} balances_at_risk=${top['balances_at_risk']:,}")


if __name__ == "__main__":
    main()
