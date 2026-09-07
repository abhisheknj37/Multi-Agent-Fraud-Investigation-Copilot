# Hackathon Feature Set

FraudGuard is positioned as an investigation copilot rather than a black-box fraud classifier.

## 1. Multi-Agent Fraud Investigation
Four specialized agents collaborate on each investigation:
- Transaction Pattern Agent — amount, geography, merchant, time and velocity anomalies.
- Customer History Agent — spending baseline, disputes, prior flags and account age.
- Risk Scoring Agent — weighted, explainable 0–100 risk score.
- Network Intelligence Agent — device/IP relationship and cross-customer links.

## 2. Explainable Risk Score
Every score includes the factor, weight, signal and contribution. Analysts can see exactly what drove the 0–100 score.

## 3. Evidence & Audit Trail
Every investigation produces structured evidence and an agent trace. Investigations and analyst decisions are written to the audit log.

## 4. Fraud Network Analysis
Customers are connected to devices, IP addresses, merchants and locations. Shared device/IP activity across customers is surfaced as network evidence.

## 5. Human-in-the-Loop Decisions
AI recommends an action, but an analyst controls the final outcome: Approve/Clear, Reject/Confirm Fraud, or Escalate. Reject and Escalate require an analyst note and every decision is audited.
