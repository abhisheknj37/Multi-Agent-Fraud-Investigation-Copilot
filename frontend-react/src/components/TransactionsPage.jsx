import { useEffect, useMemo, useState } from "react";

import {
  Activity,
  AlertTriangle,
  ArrowDownUp,
  ChevronDown,
  Eye,
  Filter,
  MapPin,
  Search,
  ShieldAlert,
  UserRound,
  Store,
  X,
} from "lucide-react";

import "./TransactionsPage.css";


const transactionData = [
  {
    id: "TXN-92841",
    customer: "CUS-10482",
    merchant: "Amazon",
    amount: 4820,
    location: "Bengaluru, IN",
    time: "2 min ago",
    risk: 96,
    status: "Critical",
    velocity: "Very High",
    device: "DEV-8842",
  },
  {
    id: "TXN-92840",
    customer: "CUS-20194",
    merchant: "Binance",
    amount: 2940,
    location: "Mumbai, IN",
    time: "7 min ago",
    risk: 89,
    status: "High Risk",
    velocity: "High",
    device: "DEV-4421",
  },
  {
    id: "TXN-92839",
    customer: "CUS-33821",
    merchant: "Flipkart",
    amount: 1280,
    location: "Delhi, IN",
    time: "12 min ago",
    risk: 74,
    status: "Review",
    velocity: "High",
    device: "DEV-2281",
  },
  {
    id: "TXN-92838",
    customer: "CUS-55102",
    merchant: "Walmart",
    amount: 430,
    location: "Chennai, IN",
    time: "18 min ago",
    risk: 43,
    status: "Medium",
    velocity: "Normal",
    device: "DEV-9123",
  },
  {
    id: "TXN-92837",
    customer: "CUS-44218",
    merchant: "Apple",
    amount: 210,
    location: "Hyderabad, IN",
    time: "25 min ago",
    risk: 18,
    status: "Low",
    velocity: "Normal",
    device: "DEV-1182",
  },
  {
    id: "TXN-92836",
    customer: "CUS-77291",
    merchant: "Myntra",
    amount: 890,
    location: "Pune, IN",
    time: "31 min ago",
    risk: 67,
    status: "Review",
    velocity: "High",
    device: "DEV-6612",
  },
  {
    id: "TXN-92835",
    customer: "CUS-55189",
    merchant: "PayPal",
    amount: 3250,
    location: "Kolkata, IN",
    time: "38 min ago",
    risk: 83,
    status: "High Risk",
    velocity: "Very High",
    device: "DEV-7719",
  },
  {
    id: "TXN-92834",
    customer: "CUS-31284",
    merchant: "eBay",
    amount: 175,
    location: "Jaipur, IN",
    time: "44 min ago",
    risk: 22,
    status: "Low",
    velocity: "Normal",
    device: "DEV-5521",
  },
];


function TransactionsPage() {
  const [transactions, setTransactions] = useState(transactionData);
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [sortHighRisk, setSortHighRisk] = useState(false);

  useEffect(() => {
    fetch("/api/transactions")
      .then((response) => response.json())
      .then((rows) => {
        if (!Array.isArray(rows) || rows.length === 0) return;
        setTransactions(rows.map((row) => ({
          id: row.id,
          customer: row.customer_id,
          merchant: row.merchant_category,
          amount: Number(row.amount),
          location: row.location,
          time: row.timestamp,
          risk: Number(row.risk_score || 0),
          status: Number(row.risk_score || 0) >= 75 ? "Critical" : Number(row.risk_score || 0) >= 50 ? "High Risk" : "Low",
          velocity: Number(row.risk_score || 0) >= 75 ? "Very High" : "Normal",
          device: row.device_id,
        })));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedTransaction) {
      setWorkflow(null);
      return;
    }
    fetch(`/api/workflow/${selectedTransaction.id}`)
      .then((response) => response.json())
      .then(setWorkflow)
      .catch(() => setWorkflow(null));
  }, [selectedTransaction]);


  const filteredTransactions = useMemo(() => {
    let result = transactions.filter((transaction) => {
      const search = searchTerm.toLowerCase();

      const matchesSearch =
        transaction.id.toLowerCase().includes(search) ||
        transaction.customer.toLowerCase().includes(search) ||
        transaction.merchant.toLowerCase().includes(search) ||
        transaction.location.toLowerCase().includes(search);

      const matchesRisk =
        riskFilter === "All" ||
        (riskFilter === "Critical" && transaction.risk >= 90) ||
        (riskFilter === "High" &&
          transaction.risk >= 70 &&
          transaction.risk < 90) ||
        (riskFilter === "Medium" &&
          transaction.risk >= 40 &&
          transaction.risk < 70) ||
        (riskFilter === "Low" && transaction.risk < 40);

      return matchesSearch && matchesRisk;
    });

    if (sortHighRisk) {
      result = [...result].sort(
        (a, b) => b.risk - a.risk
      );
    }

    return result;
  }, [transactions, searchTerm, riskFilter, sortHighRisk]);


  const getRiskClass = (risk) => {
    if (risk >= 90) return "transaction-risk critical";
    if (risk >= 70) return "transaction-risk high";
    if (risk >= 40) return "transaction-risk medium";
    return "transaction-risk low";
  };


  const getStatusClass = (status) => {
    if (status === "Critical") return "status-critical";
    if (status === "High Risk") return "status-high";
    if (status === "Review") return "status-review";
    if (status === "Medium") return "status-medium";
    return "status-low";
  };

  const submitDecision = async (decision, note) => {
    const caseId = workflow?.case?.id || `CASE-${selectedTransaction.id.replace("TXN", "")}`;
    await fetch(`/api/cases/${caseId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, note }),
    });
    setSelectedTransaction(null);
  };


  return (
    <div className="transactions-page">

      {/* HEADER */}

      <div className="transactions-page-header">

        <div>

          <div className="transactions-eyebrow">
            <Activity size={14} />
            TRANSACTION INTELLIGENCE
          </div>

          <h1>
            Transaction Intelligence
          </h1>

          <p>
            Search, filter and investigate financial transactions
            using real-time fraud intelligence.
          </p>

        </div>


        <div className="transaction-live-status">
          <span />
          LIVE MONITORING
        </div>

      </div>


      {/* SUMMARY CARDS */}

      <div className="transaction-summary-grid">

        <div className="transaction-summary-card">

          <div className="summary-icon blue">
            <Activity size={18} />
          </div>

          <div>
            <span>Total Transactions</span>
            <strong>24,892</strong>
          </div>

        </div>


        <div className="transaction-summary-card">

          <div className="summary-icon red">
            <ShieldAlert size={18} />
          </div>

          <div>
            <span>High Risk</span>
            <strong>342</strong>
          </div>

        </div>


        <div className="transaction-summary-card">

          <div className="summary-icon orange">
            <AlertTriangle size={18} />
          </div>

          <div>
            <span>Amount at Risk</span>
            <strong>$1.28M</strong>
          </div>

        </div>


        <div className="transaction-summary-card">

          <div className="summary-icon green">
            <Activity size={18} />
          </div>

          <div>
            <span>Processed Today</span>
            <strong>97.8%</strong>
          </div>

        </div>

      </div>


      {/* FILTER BAR */}

      <div className="transaction-filter-panel">

        <div className="transaction-search">

          <Search size={17} />

          <input
            value={searchTerm}
            onChange={(e) =>
              setSearchTerm(e.target.value)
            }
            placeholder="Search transaction, customer, merchant or location..."
          />

          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="clear-search"
            >
              <X size={15} />
            </button>
          )}

        </div>


        <div className="filter-controls">

          <div className="filter-select">

            <Filter size={14} />

            <select
              value={riskFilter}
              onChange={(e) =>
                setRiskFilter(e.target.value)
              }
            >
              <option value="All">
                All Risk Levels
              </option>

              <option value="Critical">
                Critical
              </option>

              <option value="High">
                High Risk
              </option>

              <option value="Medium">
                Medium
              </option>

              <option value="Low">
                Low
              </option>
            </select>

            <ChevronDown size={13} />

          </div>


          <button
            className={`sort-button ${
              sortHighRisk ? "active" : ""
            }`}
            onClick={() =>
              setSortHighRisk(!sortHighRisk)
            }
          >
            <ArrowDownUp size={14} />
            Highest Risk
          </button>

        </div>

      </div>


      {/* RESULTS */}

      <div className="transactions-results-bar">

        <div>
          Showing{" "}
          <strong>
            {filteredTransactions.length}
          </strong>{" "}
          transactions
        </div>

        <span>
          AI fraud engine active
        </span>

      </div>


      {/* TRANSACTION TABLE */}

      <div className="transactions-table-card">

        <div className="transactions-table-wrapper">

          <table className="transactions-page-table">

            <thead>

              <tr>
                <th>Transaction</th>
                <th>Customer</th>
                <th>Merchant</th>
                <th>Amount</th>
                <th>Location</th>
                <th>Risk Score</th>
                <th>Status</th>
                <th>Action</th>
              </tr>

            </thead>


            <tbody>

              {filteredTransactions.map(
                (transaction) => (

                  <tr key={transaction.id}>

                    <td>

                      <div className="transaction-id">

                        <Activity size={14} />

                        <div>

                          <strong>
                            {transaction.id}
                          </strong>

                          <span>
                            {transaction.time}
                          </span>

                        </div>

                      </div>

                    </td>


                    <td>

                      <div className="entity-cell">

                        <div className="entity-icon customer">
                          <UserRound size={14} />
                        </div>

                        {transaction.customer}

                      </div>

                    </td>


                    <td>

                      <div className="entity-cell">

                        <div className="entity-icon merchant">
                          <Store size={14} />
                        </div>

                        {transaction.merchant}

                      </div>

                    </td>


                    <td>

                      <strong className="transaction-amount">
                        ${transaction.amount.toLocaleString()}
                      </strong>

                    </td>


                    <td>

                      <div className="location-cell">

                        <MapPin size={13} />

                        {transaction.location}

                      </div>

                    </td>


                    <td>

                      <div className="transaction-risk-container">

                        <span
                          className={getRiskClass(
                            transaction.risk
                          )}
                        >
                          {transaction.risk}
                        </span>

                        <div className="transaction-risk-bar">

                          <div
                            style={{
                              width: `${transaction.risk}%`,
                            }}
                          />

                        </div>

                      </div>

                    </td>


                    <td>

                      <span
                        className={`status-badge ${getStatusClass(
                          transaction.status
                        )}`}
                      >
                        {transaction.status}
                      </span>

                    </td>


                    <td>

                      <button
                        className="transaction-view-button"
                        onClick={() =>
                          setSelectedTransaction(
                            transaction
                          )
                        }
                      >
                        <Eye size={14} />
                        Investigate
                      </button>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>


          {filteredTransactions.length === 0 && (

            <div className="no-transactions">

              <Search size={30} />

              <h3>
                No transactions found
              </h3>

              <p>
                Try changing your search or risk filter.
              </p>

            </div>

          )}

        </div>

      </div>


      {/* ================================================== */}
      {/* AI MULTI-AGENT INVESTIGATION DRAWER */}
      {/* ================================================== */}

      {selectedTransaction && (

        <div
          className="transaction-drawer-backdrop"
          onClick={() =>
            setSelectedTransaction(null)
          }
        >

          <div
            className="transaction-drawer advanced-investigation-drawer"
            onClick={(e) =>
              e.stopPropagation()
            }
          >


            {/* HEADER */}

            <div className="drawer-header">

              <div>

                <span className="investigation-label">
                  AI MULTI-AGENT INVESTIGATION
                </span>

                <h2>
                  {selectedTransaction.id}
                </h2>

                <p className="investigation-subtitle">
                  Autonomous fraud investigation with
                  human oversight
                </p>

              </div>


              <button
                onClick={() =>
                  setSelectedTransaction(null)
                }
                className="drawer-close-button"
              >
                <X size={19} />
              </button>

            </div>


            {/* RISK OVERVIEW */}

            <div className="advanced-risk-overview">

              <div
                className={`advanced-risk-score ${
                  selectedTransaction.risk >= 70
                    ? "danger"
                    : "safe"
                }`}
              >

                <strong>
                  {selectedTransaction.risk}
                </strong>

                <span>/100</span>

              </div>


              <div className="risk-overview-content">

                <div className="risk-overview-top">

                  <span>
                    FINAL RISK ASSESSMENT
                  </span>

                  <strong>

                    {selectedTransaction.risk >= 85
                      ? "CRITICAL RISK"
                      : selectedTransaction.risk >= 70
                      ? "HIGH RISK"
                      : selectedTransaction.risk >= 40
                      ? "MEDIUM RISK"
                      : "LOW RISK"}

                  </strong>

                </div>


                <p>
                  Risk score generated by correlating
                  transaction, customer, network and
                  behavioral intelligence.
                </p>


                <div className="risk-confidence">

                  <span>
                    Model confidence
                  </span>

                  <strong>
                    {selectedTransaction.risk >= 70
                      ? "94%"
                      : "91%"}
                  </strong>

                </div>

              </div>

            </div>


            {/* TRANSACTION SNAPSHOT */}

            <div className="drawer-section">

              <div className="section-heading-row">

                <div>

                  <span className="section-eyebrow">
                    CASE CONTEXT
                  </span>

                  <h3>
                    Transaction Snapshot
                  </h3>

                </div>


                <span className="agent-status-badge">
                  ANALYZED
                </span>

              </div>


              <div className="advanced-detail-grid">

                <div>
                  <span>Customer</span>
                  <strong>
                    {selectedTransaction.customer}
                  </strong>
                </div>

                <div>
                  <span>Merchant</span>
                  <strong>
                    {selectedTransaction.merchant}
                  </strong>
                </div>

                <div>
                  <span>Amount</span>
                  <strong>
                    ${selectedTransaction.amount.toLocaleString()}
                  </strong>
                </div>

                <div>
                  <span>Location</span>
                  <strong>
                    {selectedTransaction.location}
                  </strong>
                </div>

                <div>
                  <span>Velocity</span>
                  <strong>
                    {selectedTransaction.velocity}
                  </strong>
                </div>

                <div>
                  <span>Device</span>
                  <strong>
                    {selectedTransaction.device}
                  </strong>
                </div>

              </div>

            </div>


            {/* MULTI AGENT ENGINE */}

            <div className="drawer-section">

              <div className="section-heading-row">

                <div>

                  <span className="section-eyebrow">
                    AGENTIC INVESTIGATION ENGINE
                  </span>

                  <h3>
                    Multi-Agent Analysis
                  </h3>

                </div>


                <span className="agents-running">
                  ● 4 AGENTS COMPLETED
                </span>

              </div>


              {/* TRANSACTION PATTERN AGENT */}

              <div className="investigation-agent-card">

                <div className="agent-card-icon pattern">
                  <Activity size={18} />
                </div>


                <div className="agent-card-content">

                  <div className="agent-card-header">

                    <div>

                      <strong>
                        Transaction Pattern Agent
                      </strong>

                      <span>
                        Behavior & velocity analysis
                      </span>

                    </div>


                    <strong className="agent-confidence">
                      96%
                    </strong>

                  </div>


                  <div className="agent-progress">

                    <div
                      style={{
                        width: "96%",
                      }}
                    />

                  </div>


                  <p>
                    Detected abnormal transaction velocity
                    and transaction amount deviation compared
                    with the expected customer pattern.
                  </p>


                  <div className="agent-evidence">

                    <span>
                      ✓ Velocity anomaly
                    </span>

                    <span>
                      ✓ Amount deviation
                    </span>

                    <span>
                      ✓ Merchant pattern deviation
                    </span>

                  </div>

                </div>

              </div>


              {/* CUSTOMER HISTORY AGENT */}

              <div className="investigation-agent-card">

                <div className="agent-card-icon customer">
                  <UserRound size={18} />
                </div>


                <div className="agent-card-content">

                  <div className="agent-card-header">

                    <div>

                      <strong>
                        Customer History Agent
                      </strong>

                      <span>
                        Historical behavior analysis
                      </span>

                    </div>


                    <strong className="agent-confidence">
                      91%
                    </strong>

                  </div>


                  <div className="agent-progress">

                    <div
                      style={{
                        width: "91%",
                      }}
                    />

                  </div>


                  <p>
                    Customer behavior differs from the
                    established historical baseline. Previous
                    activity shows a lower transaction frequency
                    and lower average value.
                  </p>


                  <div className="agent-evidence">

                    <span>
                      ✓ Behavioral deviation
                    </span>

                    <span>
                      ✓ Baseline mismatch
                    </span>

                    <span>
                      ✓ Historical risk comparison
                    </span>

                  </div>

                </div>

              </div>


              {/* NETWORK INTELLIGENCE AGENT */}

              <div className="investigation-agent-card">

                <div className="agent-card-icon network">
                  <Activity size={18} />
                </div>


                <div className="agent-card-content">

                  <div className="agent-card-header">

                    <div>

                      <strong>
                        Network Intelligence Agent
                      </strong>

                      <span>
                        Entity & relationship analysis
                      </span>

                    </div>


                    <strong className="agent-confidence">
                      88%
                    </strong>

                  </div>


                  <div className="agent-progress">

                    <div
                      style={{
                        width: "88%",
                      }}
                    />

                  </div>


                  <p>
                    Device and transaction relationships
                    indicate potential connections with other
                    high-risk activity. Network evidence requires
                    analyst validation.
                  </p>


                  <div className="agent-evidence">

                    <span>
                      ✓ Device relationship
                    </span>

                    <span>
                      ✓ Entity correlation
                    </span>

                    <span>
                      ✓ Network risk signal
                    </span>

                  </div>

                </div>

              </div>


              {/* RISK SCORING AGENT */}

              <div className="investigation-agent-card risk-agent-card">

                <div className="agent-card-icon risk">
                  <ShieldAlert size={18} />
                </div>


                <div className="agent-card-content">

                  <div className="agent-card-header">

                    <div>

                      <strong>
                        Risk Scoring Agent
                      </strong>

                      <span>
                        Cross-agent risk synthesis
                      </span>

                    </div>


                    <strong className="agent-confidence">
                      94%
                    </strong>

                  </div>


                  <div className="agent-progress">

                    <div
                      style={{
                        width: "94%",
                      }}
                    />

                  </div>


                  <p>
                    Correlated evidence from all investigation
                    agents and generated the final risk assessment.
                  </p>


                  <div className="agent-evidence">

                    <span>
                      ✓ Pattern evidence
                    </span>

                    <span>
                      ✓ Customer evidence
                    </span>

                    <span>
                      ✓ Network evidence
                    </span>

                  </div>

                </div>

              </div>

            </div>


            {/* EVIDENCE TRAIL */}

            <div className="drawer-section evidence-section">

              <div className="section-heading-row">

                <div>

                  <span className="section-eyebrow">
                    EXPLAINABILITY
                  </span>

                  <h3>
                    Evidence Trail
                  </h3>

                </div>


                <span className="evidence-count">
                  06 EVIDENCE ITEMS
                </span>

              </div>


              <div className="evidence-timeline">


                <div className="evidence-item">

                  <span className="evidence-dot danger" />

                  <div>

                    <strong>
                      Unusual transaction velocity
                    </strong>

                    <p>
                      Transaction frequency exceeds the
                      customer's normal behavioral baseline.
                    </p>

                  </div>

                </div>


                <div className="evidence-item">

                  <span className="evidence-dot danger" />

                  <div>

                    <strong>
                      Geographic anomaly
                    </strong>

                    <p>
                      Current transaction location differs
                      from recent customer activity.
                    </p>

                  </div>

                </div>


                <div className="evidence-item">

                  <span className="evidence-dot warning" />

                  <div>

                    <strong>
                      Amount deviation
                    </strong>

                    <p>
                      Transaction value is outside the
                      customer's historical spending pattern.
                    </p>

                  </div>

                </div>


                <div className="evidence-item">

                  <span className="evidence-dot warning" />

                  <div>

                    <strong>
                      Device relationship detected
                    </strong>

                    <p>
                      Device identity contributes additional
                      network risk context.
                    </p>

                  </div>

                </div>


                <div className="evidence-item">

                  <span className="evidence-dot info" />

                  <div>

                    <strong>
                      Merchant pattern anomaly
                    </strong>

                    <p>
                      Merchant activity differs from the
                      expected customer transaction profile.
                    </p>

                  </div>

                </div>


                <div className="evidence-item">

                  <span className="evidence-dot info" />

                  <div>

                    <strong>
                      Cross-agent agreement
                    </strong>

                    <p>
                      Multiple independent agents identified
                      consistent risk signals.
                    </p>

                  </div>

                </div>


              </div>

            </div>


            {/* AI INVESTIGATION SUMMARY */}

            {workflow && (
              <div className="ai-investigation-summary">
                <div className="ai-summary-header">
                  <div className="ai-summary-icon">AI</div>
                  <div>
                    <span>LIVE FRAUD AI ENGINE</span>
                    <strong>{workflow.risk.level} risk / {workflow.risk.score} score</strong>
                  </div>
                </div>
                <p>
                  {workflow.anomaly_detection.count} anomaly signals detected. Typologies: {workflow.typologies.length ? workflow.typologies.join(", ") : "No confirmed typology"}.
                </p>
                <div className="recommendation-row">
                  <span>Evidence vault</span>
                  <strong>{workflow.evidence_vault.length} persisted evidence items</strong>
                </div>
              </div>
            )}

            <div className="ai-investigation-summary">

              <div className="ai-summary-header">

                <div className="ai-summary-icon">
                  ✦
                </div>


                <div>

                  <span>
                    AI INVESTIGATION SUMMARY
                  </span>

                  <strong>
                    Explainable recommendation
                  </strong>

                </div>

              </div>


              <p>
                The investigation engine identifies this
                transaction as potentially fraudulent based on
                abnormal velocity, behavioral deviation,
                geographic inconsistency and correlated network
                signals. The evidence is strong enough to require
                human analyst review.
              </p>


              <div className="recommendation-row">

                <span>
                  Recommended action
                </span>


                <strong>

                  {selectedTransaction.risk >= 85
                    ? "ESCALATE FOR FRAUD REVIEW"
                    : selectedTransaction.risk >= 70
                    ? "MANUAL REVIEW"
                    : "CLEAR WITH MONITORING"}

                </strong>

              </div>

            </div>


            {/* HUMAN ANALYST DECISION */}

            <div className="drawer-decision advanced-decision">

              <div className="decision-header">

                <div>

                  <span className="section-eyebrow">
                    HUMAN-IN-THE-LOOP
                  </span>

                  <strong>
                    Final Analyst Decision
                  </strong>

                  <p>
                    AI provides evidence and recommendations.
                    The human analyst retains final authority.
                  </p>

                </div>


                <div className="decision-required">
                  DECISION REQUIRED
                </div>

              </div>


              <div className="drawer-actions advanced-actions">

                <button
                  className="clear-action"
                  onClick={() => submitDecision("false_positive", "Analyst marked the alert as a false positive.")}
                >
                  ✓ Clear
                </button>


                <button
                  className="escalate-action"
                  onClick={() => submitDecision("escalate", "Analyst escalated for enhanced investigation.")}
                >
                  ↗ Escalate
                </button>


                <button
                  className="fraud-action"
                  onClick={() => submitDecision("confirm_suspicious", "Analyst confirmed suspicious activity.")}
                >
                  ⚠ Confirm Fraud
                </button>

              </div>

            </div>


            {/* AUDIT FOOTER */}

            <div className="investigation-audit-footer">

              <div>

                <span>
                  INVESTIGATION ID
                </span>

                <strong>
                  FG-
                  {selectedTransaction.id.replace(
                    "TXN-",
                    ""
                  )}
                </strong>

              </div>


              <div>

                <span>
                  AGENTS
                </span>

                <strong>
                  4 / 4 COMPLETED
                </strong>

              </div>


              <div>

                <span>
                  DECISION OWNER
                </span>

                <strong>
                  HUMAN ANALYST
                </strong>

              </div>

            </div>


          </div>

        </div>

      )}


    </div>
  );
}


export default TransactionsPage;