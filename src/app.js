const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US");

const views = {
  cockpit: document.querySelector("#cockpitView"),
  traceability: document.querySelector("#traceabilityView"),
  campaigns: document.querySelector("#campaignsView"),
  controls: document.querySelector("#controlsView"),
};

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("active"));
    Object.values(views).forEach((view) => view.classList.remove("active"));
    button.classList.add("active");
    views[button.dataset.view].classList.add("active");
  });
});

fetch("analysis/outputs/app_payload.json")
  .then((response) => response.json())
  .then((payload) => render(payload));

function render(payload) {
  renderSummary(payload.summary);
  renderTopDecision(payload.summary.top_cohort);
  renderTiers(payload.tierRules);
  renderCohorts(payload.cohorts);
  renderStories(payload.stories, payload.summary);
  renderCampaigns(payload.campaigns, payload.summary);
  renderControls(payload.controls, payload.summary);
}

function renderSummary(summary) {
  const metrics = [
    ["Cohorts", number.format(summary.cohorts), "priced segments"],
    ["Balance at risk", compactCurrency(summary.balance_at_risk), "modeled"],
    ["Story readiness", `${summary.avg_story_readiness}%`, "average"],
    ["Launch packets", number.format(summary.launchable_campaigns), "ready"],
  ];

  document.querySelector("#summaryStrip").innerHTML = metrics
    .map(
      ([label, value, note]) => `
        <div>
          <dt>${label}</dt>
          <dd>${value}</dd>
          <span>${note}</span>
        </div>
      `,
    )
    .join("");
}

function renderTopDecision(cohort) {
  document.querySelector("#topDecision").innerHTML = `
    <span>Top decision</span>
    <strong>${cohort.recommended_decision}</strong>
    <p>${cohort.cohort_id} has ${cohort.rate_gap_bps} bps of rate gap, ${cohort.rewards_utilization}% reward utilization, and ${currency.format(cohort.balances_at_risk)} in modeled balances at risk.</p>
  `;
}

function renderTiers(tiers) {
  document.querySelector("#tierList").innerHTML = tiers
    .map(
      (tier) => `
        <article>
          <div>
            <strong>${tier.tier}</strong>
            <span>${currency.format(tier.min_balance)}+</span>
          </div>
          <dl>
            <div><dt>Loyalty</dt><dd>${tier.loyalty_bonus_pct}%</dd></div>
            <div><dt>ATM</dt><dd>${tier.atm_waivers === 99 ? "Unlimited" : tier.atm_waivers}</dd></div>
            <div><dt>POS</dt><dd>${currency.format(tier.pos_limit)}</dd></div>
          </dl>
          <p>${tier.primary_message}</p>
        </article>
      `,
    )
    .join("");
}

function renderCohorts(rows) {
  const columns = [
    ["Cohort", "cohort_id"],
    ["Segment", "segment"],
    ["Product", "product"],
    ["Tier", "benefit_tier"],
    ["Gap", (row) => `${row.rate_gap_bps} bps`],
    ["Rewards", (row) => `${row.rewards_utilization}%`],
    ["Risk", (row) => `${row.attrition_risk_score}`],
    ["Balance risk", (row) => currency.format(row.balances_at_risk)],
    ["Decision", "recommended_decision"],
  ];
  renderTable("#cohortTable", columns, rows);
}

function renderStories(rows, summary) {
  document.querySelector("#storyBadge").innerHTML = `
    <span>${summary.blocked_stories}</span>
    <b>stories need blocker or control review</b>
  `;

  const columns = [
    ["Story", "story_id"],
    ["Epic", "epic"],
    ["Feature", "feature"],
    ["UAT", (row) => `${row.uat_pass_rate}%`],
    ["Questions", "open_questions"],
    ["Defects", "high_severity_defects"],
    ["Signoff", "partner_signoff"],
    ["Ready", (row) => scorePill(row.readiness_score)],
    ["Decision", "release_decision"],
  ];
  renderTable("#storyTable", columns, rows);
}

function renderCampaigns(rows, summary) {
  document.querySelector("#campaignBadge").innerHTML = `
    <span>${summary.launchable_campaigns}</span>
    <b>campaign packets are launch-ready</b>
  `;

  document.querySelector("#campaignGrid").innerHTML = rows
    .map(
      (row) => `
        <article class="campaign-card">
          <div class="campaign-title">
            <span>${row.campaign_id}</span>
            <strong>${row.decision}</strong>
          </div>
          <h3>${row.objective}</h3>
          <p>${row.complaint_driver}</p>
          <dl>
            <div><dt>Channel</dt><dd>${row.channel}</dd></div>
            <div><dt>Eligible</dt><dd>${number.format(row.eligible_accounts)}</dd></div>
            <div><dt>Lift</dt><dd>${row.expected_lift_pct}%</dd></div>
            <div><dt>Compliance</dt><dd>${row.compliance_status}</dd></div>
          </dl>
          <footer>
            <span>${row.enablement_doc}</span>
            ${scorePill(row.launch_readiness)}
          </footer>
        </article>
      `,
    )
    .join("");
}

function renderControls(rows, summary) {
  document.querySelector("#controlBadge").innerHTML = `
    <span>${summary.high_controls}</span>
    <b>high or critical controls</b>
  `;

  const columns = [
    ["Control", "control_id"],
    ["Dimension", "dimension"],
    ["Evidence", "evidence_status"],
    ["Severity", (row) => severityPill(row.severity)],
    ["Defect rate", (row) => `${row.defect_rate_pct}%`],
    ["Score", (row) => scorePill(row.control_score)],
    ["Owner", "owner"],
    ["Action", "recommended_action"],
  ];
  renderTable("#controlTable", columns, rows);
}

function renderTable(selector, columns, rows) {
  const header = columns.map(([label]) => `<th>${label}</th>`).join("");
  const body = rows
    .map(
      (row) => `
        <tr>
          ${columns
            .map(([, accessor]) => {
              const value = typeof accessor === "function" ? accessor(row) : row[accessor];
              return `<td>${value}</td>`;
            })
            .join("")}
        </tr>
      `,
    )
    .join("");

  document.querySelector(selector).innerHTML = `<thead><tr>${header}</tr></thead><tbody>${body}</tbody>`;
}

function scorePill(score) {
  const value = Number(score);
  const tone = value >= 78 ? "good" : value >= 62 ? "warn" : "bad";
  return `<span class="pill ${tone}">${value}</span>`;
}

function severityPill(severity) {
  const tone = severity === "Critical" ? "bad" : severity === "High" ? "warn" : "good";
  return `<span class="pill ${tone}">${severity}</span>`;
}

function compactCurrency(value) {
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  }
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  }
  return currency.format(value);
}
