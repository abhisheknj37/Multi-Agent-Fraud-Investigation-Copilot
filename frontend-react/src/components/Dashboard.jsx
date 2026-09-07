import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  Bot,
  BriefcaseBusiness,
  ChevronDown,
  FileText,
  LayoutDashboard,
  Menu,
  Network,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  Store,
  UserRound,
  Users,
  X,
  Zap,
} from "lucide-react";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import PageWorkspace from "./PageWorkspace";
import "./Dashboard.css";


const trendData = [
  { day: "Mon", fraud: 32, transactions: 420 },
  { day: "Tue", fraud: 45, transactions: 510 },
  { day: "Wed", fraud: 38, transactions: 470 },
  { day: "Thu", fraud: 61, transactions: 620 },
  { day: "Fri", fraud: 54, transactions: 590 },
  { day: "Sat", fraud: 72, transactions: 680 },
  { day: "Sun", fraud: 48, transactions: 540 },
];


const riskData = [
  { name: "Low", value: 52 },
  { name: "Medium", value: 29 },
  { name: "High", value: 14 },
  { name: "Critical", value: 5 },
];


const transactions = [
  {
    id: "TXN-92841",
    customer: "CUS-10482",
    merchant: "Amazon",
    amount: "$4,820.00",
    location: "Bengaluru, IN",
    time: "2 min ago",
    risk: 96,
    status: "Critical",
  },
  {
    id: "TXN-92840",
    customer: "CUS-20194",
    merchant: "Binance",
    amount: "$2,940.00",
    location: "Mumbai, IN",
    time: "7 min ago",
    risk: 89,
    status: "High Risk",
  },
  {
    id: "TXN-92839",
    customer: "CUS-33821",
    merchant: "Flipkart",
    amount: "$1,280.00",
    location: "Delhi, IN",
    time: "12 min ago",
    risk: 74,
    status: "Review",
  },
  {
    id: "TXN-92838",
    customer: "CUS-55102",
    merchant: "Walmart",
    amount: "$430.00",
    location: "Chennai, IN",
    time: "18 min ago",
    risk: 43,
    status: "Medium",
  },
  {
    id: "TXN-92837",
    customer: "CUS-44218",
    merchant: "Apple",
    amount: "$210.00",
    location: "Hyderabad, IN",
    time: "25 min ago",
    risk: 18,
    status: "Low",
  },
];


const agents = [
  {
    name: "Transaction Pattern Agent",
    description: "Velocity, amount & geography analysis",
    status: "ONLINE",
  },
  {
    name: "Customer History Agent",
    description: "Customer behavior & dispute history",
    status: "ONLINE",
  },
  {
    name: "Risk Scoring Agent",
    description: "Confidence-scored fraud assessment",
    status: "ONLINE",
  },
  {
    name: "Network Intelligence Agent",
    description: "Entity relationship analysis",
    status: "ONLINE",
  },
];


function Dashboard() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [investigationOpen, setInvestigationOpen] = useState(false);
  const [copilotMessage, setCopilotMessage] = useState("");
  const [copilotResponse, setCopilotResponse] = useState("I can analyze transactions, customer history, fraud networks, risk signals and evidence. What would you like to investigate?");
  const [liveTransactions, setLiveTransactions] = useState([]);
  const [dashboardData, setDashboardData] = useState({
    kpis: { total: 0, suspicious: 0, high_risk: 0, confirmed_fraud: 0, under_review: 0 },
    risk_distribution: [],
    risk_locations: [],
    risk_merchants: [],
  });

  useEffect(() => {
    let isMounted = true;

    fetch("/api/dashboard")
      .then((res) => res.json())
      .then((data) => {
        if (isMounted) {
          setDashboardData(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setDashboardData({
            kpis: { total: 0, suspicious: 0, high_risk: 0, confirmed_fraud: 0, under_review: 0 },
            risk_distribution: [],
            risk_locations: [],
            risk_merchants: [],
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    fetch("/api/transactions?risk=high")
      .then((res) => res.json())
      .then((rows) => setLiveTransactions(rows.slice(0, 6).map((row) => ({
        id: row.id,
        customer: row.customer_id,
        merchant: row.merchant_category,
        amount: `${row.currency || "INR"} ${Number(row.amount).toLocaleString()}`,
        location: row.location,
        time: row.timestamp,
        risk: Number(row.risk_score || 0),
        status: Number(row.risk_score || 0) >= 90 ? "Critical" : Number(row.risk_score || 0) >= 75 ? "High Risk" : "Review",
      }))))
      .catch(() => setLiveTransactions([]));
  }, []);


  const handleNavigation = (page) => {
    setActivePage(page);
    setSidebarOpen(false);
  };


  const openInvestigation = (transaction) => {
    setSelectedTransaction(transaction);
    setInvestigationOpen(true);
  };


  const closeInvestigation = () => {
    setInvestigationOpen(false);
  };


  const sendCopilotMessage = async () => {
    const msg = copilotMessage.trim();
    if (!msg) return;

    setCopilotResponse("Thinking...");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });

      const data = await response.json();
      setCopilotResponse(data.answer || "I couldn't generate a valid answer.");
    } catch (error) {
      setCopilotResponse("I’m unable to reach the AI copilot service right now. Please try again in a moment.");
    }

    setCopilotMessage("");
  };


  const navigation = [
    {
      section: "MAIN",
      items: [
        { label: "Dashboard", icon: LayoutDashboard },
        { label: "Transactions", icon: Activity },
        { label: "Investigations", icon: Search },
        { label: "Network Analysis", icon: Network },
      ],
    },
    {
      section: "INTELLIGENCE",
      items: [
        { label: "AI Copilot", icon: Bot },
        { label: "Cases", icon: BriefcaseBusiness },
        { label: "Reports", icon: FileText },
        { label: "Alerts", icon: ShieldAlert },
      ],
    },
    {
      section: "ENTITIES",
      items: [
        { label: "Customers", icon: UserRound },
        { label: "Merchants", icon: Store },
      ],
    },
    {
      section: "SYSTEM",
      items: [
        { label: "Audit Logs", icon: Users },
        { label: "Settings", icon: Settings },
      ],
    },
  ];


  return (
    <div className="dashboard-shell">

      {/* MOBILE OVERLAY */}

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}


      {/* SIDEBAR */}

      <aside className={`dashboard-sidebar ${sidebarOpen ? "open" : ""}`}>

        <div className="sidebar-brand">

          <div className="brand-icon">
            <Shield size={24} />
          </div>

          <div>
            <div className="brand-name">
              FRAUDGUARD
            </div>

            <div className="brand-subtitle">
              AI COMMAND CENTER
            </div>
          </div>

          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>

        </div>


        <div className="analyst-card">

          <div className="analyst-avatar">
            AG
          </div>

          <div className="analyst-info">

            <strong>
              Security Analyst
            </strong>

            <span>
              SOC Operations
            </span>

          </div>

          <ChevronDown size={16} />

        </div>


        <nav className="sidebar-navigation">

          {navigation.map((group) => (

            <div
              className="navigation-group"
              key={group.section}
            >

              <div className="navigation-label">
                {group.section}
              </div>

              {group.items.map((item) => {

                const Icon = item.icon;

                return (
                  <button
                    key={item.label}
                    className={`navigation-item ${
                      activePage === item.label ? "active" : ""
                    }`}
                    onClick={() => handleNavigation(item.label)}
                  >

                    <Icon size={18} />

                    <span>
                      {item.label}
                    </span>

                    {item.label === "Alerts" && (
                      <span className="notification-count">
                        {dashboardData.kpis?.under_review ?? 0}
                      </span>
                    )}

                  </button>
                );
              })}

            </div>

          ))}

        </nav>


        <div className="sidebar-bottom">

          <div className="system-status">

            <span className="status-dot"></span>

            <div>
              <strong>
                System Operational
              </strong>

              <small>
                All agents online
              </small>
            </div>

          </div>

          <div className="version">
            FraudGuard AI v1.0
          </div>

        </div>

      </aside>


      {/* MAIN */}

      <main className="dashboard-main">


        {/* TOP BAR */}

        <header className="dashboard-topbar">

          <div className="topbar-left">

            <button
              className="mobile-menu"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={22} />
            </button>

            <div className="breadcrumb">

              <span>
                Security Operations
              </span>

              <span>
                /
              </span>

              <strong>
                {activePage}
              </strong>

            </div>

          </div>


          <div className="topbar-right">

            <div className="global-search">

              <Search size={17} />

              <input
                type="text"
                placeholder="Search transactions, customers..."
              />

              <kbd>
                /
              </kbd>

            </div>


            <button className="topbar-icon">
              <Bell size={19} />

              <span className="bell-indicator">
                3
              </span>
            </button>


            <div className="topbar-user">

              <div className="topbar-avatar">
                AG
              </div>

              <div className="topbar-user-info">

                <strong>
                  Analyst
                </strong>

                <span>
                  Online
                </span>

              </div>

            </div>

          </div>

        </header>


        {/* PAGE CONTENT */}

        {activePage !== "Dashboard" ? (

          <PageWorkspace
            page={activePage}
            onInvestigate={openInvestigation}
          />

        ) : (

          <div className="dashboard-content">


            {/* HERO */}

            <section className="dashboard-hero">

              <div>

                <div className="eyebrow">
                  <Zap size={14} />
                  LIVE FRAUD INTELLIGENCE
                </div>

                <h1>
                  Fraud Command Center
                </h1>

                <p>
                  Real-time multi-agent fraud detection and
                  investigation workspace.
                </p>

              </div>


              <div className="hero-actions">

                <button
                  className="secondary-button"
                  onClick={() => handleNavigation("Investigations")}
                >
                  <Search size={16} />
                  Investigations
                </button>

                <button
                  className="primary-button"
                  onClick={() => handleNavigation("AI Copilot")}
                >
                  <Bot size={16} />
                  Open AI Copilot
                </button>

              </div>

            </section>


            {/* KPI CARDS */}

            <section className="kpi-grid">

              <div className="kpi-card">

                <div className="kpi-header">
                  <span>
                    Transactions Today
                  </span>

                  <div className="kpi-icon blue">
                    <Activity size={18} />
                  </div>
                </div>

                <div className="kpi-value">
                  {dashboardData.kpis.total.toLocaleString()}
                </div>

                <div className="kpi-change positive">
                  {dashboardData.kpis.suspicious}
                  <span>
                    suspicious
                  </span>
                </div>

              </div>


              <div className="kpi-card">

                <div className="kpi-header">
                  <span>
                    Fraud Detected
                  </span>

                  <div className="kpi-icon red">
                    <ShieldAlert size={18} />
                  </div>
                </div>

                <div className="kpi-value">
                  {dashboardData.kpis.suspicious}
                </div>

                <div className="kpi-change negative">
                  {dashboardData.kpis.high_risk}
                  <span>
                    high risk
                  </span>
                </div>

              </div>


              <div className="kpi-card">

                <div className="kpi-header">
                  <span>
                    Amount at Risk
                  </span>

                  <div className="kpi-icon orange">
                    <AlertTriangle size={18} />
                  </div>
                </div>

                <div className="kpi-value">
                  {dashboardData.kpis.high_risk}
                </div>

                <div className="kpi-change negative">
                  {dashboardData.kpis.confirmed_fraud}
                  <span>
                    confirmed
                  </span>
                </div>

              </div>


              <div className="kpi-card">

                <div className="kpi-header">
                  <span>
                    Detection Accuracy
                  </span>

                  <div className="kpi-icon green">
                    <BarChart3 size={18} />
                  </div>
                </div>

                <div className="kpi-value">
                  {dashboardData.kpis.under_review}
                </div>

                <div className="kpi-change positive">
                  {dashboardData.kpis.confirmed_fraud}
                  <span>
                    under review
                  </span>
                </div>

              </div>

            </section>


            {/* CHART ROW */}

            <section className="analytics-grid">


              {/* FRAUD TREND */}

              <div className="panel trend-panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Fraud Detection Trend
                    </h2>

                    <p>
                      Fraud activity across the last 7 days
                    </p>

                  </div>

                  <button className="panel-filter">
                    Last 7 days
                    <ChevronDown size={14} />
                  </button>

                </div>


                <div className="chart-container">

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <AreaChart data={trendData}>

                      <defs>

                        <linearGradient
                          id="fraudGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >

                          <stop
                            offset="0%"
                            stopOpacity={0.35}
                          />

                          <stop
                            offset="100%"
                            stopOpacity={0}
                          />

                        </linearGradient>

                      </defs>

                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        opacity={0.08}
                      />

                      <XAxis
                        dataKey="day"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 11 }}
                      />

                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 11 }}
                      />

                      <Tooltip />

                      <Area
                        type="monotone"
                        dataKey="fraud"
                        strokeWidth={2}
                        fill="url(#fraudGradient)"
                      />

                    </AreaChart>

                  </ResponsiveContainer>

                </div>

              </div>


              {/* RISK DISTRIBUTION */}

              <div className="panel risk-panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Risk Distribution
                    </h2>

                    <p>
                      Current transaction risk levels
                    </p>

                  </div>

                </div>


                <div className="risk-chart-container">

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <PieChart>

                      <Pie
                        data={riskData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={62}
                        outerRadius={92}
                        paddingAngle={4}
                      >

                        {riskData.map((entry, index) => (

                          <Cell
                            key={`cell-${index}`}
                            fill={
                              index === 0
                                ? "#22c55e"
                                : index === 1
                                ? "#eab308"
                                : index === 2
                                ? "#f97316"
                                : "#ef4444"
                            }
                          />

                        ))}

                      </Pie>

                      <Tooltip />

                    </PieChart>

                  </ResponsiveContainer>


                  <div className="risk-center">

                    <strong>
                      24.8K
                    </strong>

                    <span>
                      Transactions
                    </span>

                  </div>

                </div>


                <div className="risk-legend">

                  {riskData.map((item, index) => (

                    <div
                      className="risk-legend-item"
                      key={item.name}
                    >

                      <span
                        className="legend-dot"
                        style={{
                          background:
                            index === 0
                              ? "#22c55e"
                              : index === 1
                              ? "#eab308"
                              : index === 2
                              ? "#f97316"
                              : "#ef4444",
                        }}
                      />

                      <span>
                        {item.name}
                      </span>

                      <strong>
                        {item.value}%
                      </strong>

                    </div>

                  ))}

                </div>

              </div>

            </section>


            {/* TRANSACTIONS */}

            <section className="panel transactions-panel">

              <div className="panel-header">

                <div>

                  <h2>
                    Recent High-Risk Transactions
                  </h2>

                  <p>
                    Transactions requiring analyst attention
                  </p>

                </div>

                <button
                  className="view-all-button"
                  onClick={() => handleNavigation("Transactions")}
                >
                  View all
                </button>

              </div>


              <div className="transaction-table-wrapper">

                <table className="transaction-table">

                  <thead>

                    <tr>
                      <th>Transaction</th>
                      <th>Customer</th>
                      <th>Merchant</th>
                      <th>Amount</th>
                      <th>Location</th>
                      <th>Risk</th>
                      <th>Status</th>
                      <th></th>
                    </tr>

                  </thead>


                  <tbody>

                    {(liveTransactions.length ? liveTransactions : transactions).map((transaction) => (

                      <tr key={transaction.id}>

                        <td>
                          <strong>
                            {transaction.id}
                          </strong>

                          <span className="table-time">
                            {transaction.time}
                          </span>
                        </td>

                        <td>
                          {transaction.customer}
                        </td>

                        <td>
                          {transaction.merchant}
                        </td>

                        <td>
                          <strong>
                            {transaction.amount}
                          </strong>
                        </td>

                        <td>
                          {transaction.location}
                        </td>

                        <td>

                          <div className="risk-score">

                            <span
                              className={
                                transaction.risk >= 85
                                  ? "risk-number critical"
                                  : transaction.risk >= 60
                                  ? "risk-number high"
                                  : transaction.risk >= 35
                                  ? "risk-number medium"
                                  : "risk-number low"
                              }
                            >
                              {transaction.risk}
                            </span>

                            <div className="risk-bar">

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
                            className={`status-badge ${
                              transaction.status === "Critical"
                                ? "status-critical"
                                : transaction.status === "High Risk"
                                ? "status-high"
                                : transaction.status === "Review"
                                ? "status-review"
                                : transaction.status === "Medium"
                                ? "status-medium"
                                : "status-low"
                            }`}
                          >
                            {transaction.status}
                          </span>

                        </td>

                        <td>

                          <button
                            className="investigate-button"
                            onClick={() =>
                              openInvestigation(transaction)
                            }
                          >
                            Investigate
                          </button>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </section>


            {/* LOWER GRID */}

            <section className="lower-grid">


              {/* NETWORK */}

              <div className="panel network-panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Fraud Network Analysis
                    </h2>

                    <p>
                      Suspicious entity relationships
                    </p>

                  </div>

                  <button
                    className="view-all-button"
                    onClick={() =>
                      handleNavigation("Network Analysis")
                    }
                  >
                    Explore
                  </button>

                </div>


                <div className="network-visual">

                  <div className="network-line line-one"></div>
                  <div className="network-line line-two"></div>
                  <div className="network-line line-three"></div>
                  <div className="network-line line-four"></div>

                  <div className="network-node node-main">
                    <Users size={18} />
                    <span>CUS-10482</span>
                  </div>

                  <div className="network-node node-one">
                    <Activity size={16} />
                    <span>TXN-92841</span>
                  </div>

                  <div className="network-node node-two">
                    <Store size={16} />
                    <span>Merchant</span>
                  </div>

                  <div className="network-node node-three">
                    <Network size={16} />
                    <span>Device-44</span>
                  </div>

                  <div className="network-node node-four">
                    <UserRound size={16} />
                    <span>CUS-8812</span>
                  </div>

                </div>

              </div>


              {/* AGENTS */}

              <div className="panel agents-panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Multi-Agent Engine
                    </h2>

                    <p>
                      Investigation intelligence status
                    </p>

                  </div>

                  <span className="live-badge">
                    LIVE
                  </span>

                </div>


                <div className="agents-list">

                  {agents.map((agent) => (

                    <div
                      className="agent-row"
                      key={agent.name}
                    >

                      <div className="agent-icon">
                        <Bot size={17} />
                      </div>

                      <div className="agent-details">

                        <strong>
                          {agent.name}
                        </strong>

                        <span>
                          {agent.description}
                        </span>

                      </div>

                      <span className="agent-status">
                        {agent.status}
                      </span>

                    </div>

                  ))}

                </div>

              </div>

            </section>


            {/* AI COPILOT */}

            <section className="panel copilot-panel">

              <div className="copilot-header">

                <div className="copilot-title">

                  <div className="copilot-icon">
                    <Bot size={22} />
                  </div>

                  <div>

                    <h2>
                      AI Investigation Copilot
                    </h2>

                    <p>
                      Ask the multi-agent system about suspicious activity.
                    </p>

                  </div>

                </div>

                <span className="ai-status">
                  AI READY
                </span>

              </div>


              <div className="copilot-body">

                <div className="copilot-message">

                  <div className="copilot-avatar">
                    AI
                  </div>

                  <div className="copilot-bubble">

                    <strong>
                      FraudGuard Copilot
                    </strong>

                    <p>
                      {copilotResponse}
                    </p>

                  </div>

                </div>


                <div className="copilot-input">

                  <input
                    value={copilotMessage}
                    onChange={(e) =>
                      setCopilotMessage(e.target.value)
                    }
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        sendCopilotMessage();
                      }
                    }}
                    placeholder="Ask: Why was TXN-92841 flagged?"
                  />

                  <button onClick={sendCopilotMessage}>
                    <Zap size={17} />
                    Ask Copilot
                  </button>

                </div>

              </div>

            </section>


          </div>

        )}

      </main>


      {/* INVESTIGATION MODAL */}

      {investigationOpen && selectedTransaction && (

        <div className="modal-backdrop">

          <div className="investigation-modal">

            <div className="modal-header">

              <div>

                <span className="modal-eyebrow">
                  AI INVESTIGATION
                </span>

                <h2>
                  {selectedTransaction.id}
                </h2>

              </div>

              <button
                className="modal-close"
                onClick={closeInvestigation}
              >
                <X size={20} />
              </button>

            </div>


            <div className="investigation-score">

              <div className="score-circle">

                <strong>
                  {selectedTransaction.risk}
                </strong>

                <span>
                  /100
                </span>

              </div>

              <div>

                <span className="score-label">
                  FRAUD RISK SCORE
                </span>

                <h3>
                  High confidence suspicious activity
                </h3>

                <p>
                  Multiple behavioral and transactional signals
                  require analyst review.
                </p>

              </div>

            </div>


            <div className="evidence-grid">

              <div className="evidence-card">

                <Activity size={18} />

                <div>

                  <strong>
                    Transaction Pattern
                  </strong>

                  <p>
                    Unusual transaction velocity detected.
                  </p>

                </div>

              </div>


              <div className="evidence-card">

                <Users size={18} />

                <div>

                  <strong>
                    Customer History
                  </strong>

                  <p>
                    Behavior deviates from historical baseline.
                  </p>

                </div>

              </div>


              <div className="evidence-card">

                <Network size={18} />

                <div>

                  <strong>
                    Network Signal
                  </strong>

                  <p>
                    Account linked to previously flagged entities.
                  </p>

                </div>

              </div>

            </div>


            <div className="analyst-decision">

              <h3>
                Human Analyst Decision
              </h3>

              <p>
                AI provides evidence and recommendation. Final
                decision remains with the analyst.
              </p>


              <div className="decision-buttons">

                <button
                  className="decision-clear"
                  onClick={closeInvestigation}
                >
                  Clear Transaction
                </button>

                <button
                  className="decision-escalate"
                  onClick={closeInvestigation}
                >
                  Escalate
                </button>

                <button
                  className="decision-fraud"
                  onClick={closeInvestigation}
                >
                  Confirm Fraud
                </button>

              </div>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}


export default Dashboard;