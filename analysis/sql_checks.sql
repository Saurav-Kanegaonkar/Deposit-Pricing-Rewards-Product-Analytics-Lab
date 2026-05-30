-- Portfolio SQL checks for a deposit pricing and rewards product operating packet.

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
