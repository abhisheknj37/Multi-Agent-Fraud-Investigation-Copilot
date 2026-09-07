import { useEffect, useRef, useState } from "react";
import Dashboard from "./components/Dashboard";

import {
  ShieldCheck,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Smartphone,
  Fingerprint,
  RefreshCw,
  Activity,
  Globe,
  Server,
} from "lucide-react";
import "./App.css";

export default function App() {
  const [mode, setMode] = useState("login");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [capsLock, setCapsLock] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [countdown, setCountdown] = useState(30);

  const otpRefs = useRef([]);

  // -----------------------------
  // PASSWORD STRENGTH
  // -----------------------------

  const getPasswordScore = () => {
    let score = 0;

    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    return score;
  };

  const passwordScore = getPasswordScore();

  // -----------------------------
  // EMAIL VALIDATION
  // -----------------------------

  const validEmail =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // -----------------------------
  // LOGIN
  // -----------------------------

  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");

    if (!email) {
      setError("Please enter your analyst email.");
      return;
    }

    if (!validEmail) {
      setError("Please enter a valid email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);

    try {
      const username = email.trim() || "analyst";
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload.detail || "Login failed");
      }

      setTimeout(() => {
        setLoading(false);
        setMode("mfa");
        setCountdown(30);
      }, 600);
    } catch (err) {
      setLoading(false);
      setError(err.message || "Unable to sign in");
    }
  };

  // -----------------------------
  // OTP INPUT
  // -----------------------------

  const handleOtpChange = (value, index) => {
    if (!/^\d?$/.test(value)) return;

    const newOtp = [...otp];

    newOtp[index] = value;

    setOtp(newOtp);

    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (event, index) => {
    if (
      event.key === "Backspace" &&
      !otp[index] &&
      index > 0
    ) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  // -----------------------------
  // VERIFY OTP
  // -----------------------------

  const verifyOtp = () => {
    if (otp.join("").length !== 6) {
      return;
    }

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      setMode("dashboard");
    }, 1000);
  };

  // -----------------------------
  // OTP TIMER
  // -----------------------------

  useEffect(() => {
    if (mode !== "mfa" || countdown <= 0) {
      return;
    }

    const timer = setInterval(() => {
      setCountdown((value) => value - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [mode, countdown]);

  // -----------------------------
  // LOGIN PAGE
  // -----------------------------

 if (mode === "dashboard") {
  return <Dashboard />;
}

return (
  <div className="auth-shell">

      {/* Animated background */}
      <div className="network-bg">
        <span />
        <span />
        <span />
        <span />
        <span />
        <span />
        <span />
        <span />
      </div>

      <div className="auth-container">

        {/* ================================================= */}
        {/* LEFT BRANDING PANEL */}
        {/* ================================================= */}

        <section className="brand-panel">

          <div className="brand">

            <div className="brand-icon">
              <ShieldCheck size={30} />
            </div>

            <div>
              <h1>FraudGuard</h1>

              <span>
                AI INVESTIGATION COPILOT
              </span>
            </div>

          </div>

          <div className="brand-content">

            <div className="status-pill">
              <span className="status-dot" />

              FRAUD INTELLIGENCE PLATFORM
            </div>

            <h2>
              Investigate smarter.
              <br />

              <span>
                Stop fraud faster.
              </span>
            </h2>

            <p>
              An AI-powered fraud investigation command
              center that correlates transactions, customer
              behavior and fraud networks for human analysts.
            </p>

            {/* Security cards */}

            <div className="security-cards">

              <div className="security-card">

                <Fingerprint size={21} />

                <div>
                  <strong>
                    Multi-Agent Analysis
                  </strong>

                  <small>
                    Specialized AI investigators
                  </small>
                </div>

              </div>

              <div className="security-card">

                <ShieldCheck size={21} />

                <div>
                  <strong>
                    Explainable Risk
                  </strong>

                  <small>
                    Evidence-backed decisions
                  </small>
                </div>

              </div>

              <div className="security-card">

                <LockKeyhole size={21} />

                <div>
                  <strong>
                    Human Controlled
                  </strong>

                  <small>
                    Analyst approval required
                  </small>
                </div>

              </div>

            </div>

            {/* Platform intelligence */}

            <div className="platform-status">

              <div>
                <Activity size={15} />

                <span>
                  AI Agents
                </span>

                <strong>
                  ONLINE
                </strong>
              </div>

              <div>
                <Globe size={15} />

                <span>
                  Network
                </span>

                <strong>
                  MONITORED
                </strong>
              </div>

              <div>
                <Server size={15} />

                <span>
                  API
                </span>

                <strong>
                  SECURE
                </strong>
              </div>

            </div>

          </div>

          <div className="brand-footer">

            <span>
              ● Systems operational
            </span>

            <span>
              FraudGuard v1.0 Enterprise
            </span>

          </div>

        </section>


        {/* ================================================= */}
        {/* RIGHT AUTH PANEL */}
        {/* ================================================= */}

        <section className="auth-panel">


          {/* ================================================= */}
          {/* LOGIN */}
          {/* ================================================= */}

          {mode === "login" && (

            <form
              className="login-card"
              onSubmit={handleLogin}
            >

              <div className="card-heading">

                <div className="mobile-logo">
                  <ShieldCheck size={28} />
                </div>

                <div className="secure-badge">
                  <LockKeyhole size={13} />

                  SECURE ANALYST ACCESS
                </div>

                <h2>
                  Welcome back
                </h2>

                <p>
                  Sign in to access your fraud investigation
                  command center.
                </p>

              </div>


              {/* ERROR */}

              {error && (

                <div className="error-box">

                  <AlertTriangle size={17} />

                  <span>
                    {error}
                  </span>

                </div>

              )}


              {/* EMAIL */}

              <label>
                ANALYST EMAIL
              </label>

              <div className="input-wrapper">

                <Mail size={18} />

                <input
                  type="email"
                  placeholder="analyst@fraudguard.ai"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  autoComplete="username"
                />

                {validEmail && (

                  <CheckCircle2
                    className="valid-icon"
                    size={18}
                  />

                )}

              </div>


              {/* PASSWORD */}

              <div className="password-label">

                <label>
                  PASSWORD
                </label>

                <button
                  type="button"
                  className="forgot"
                  onClick={() => {
                    setError("");
                    setMode("forgot");
                  }}
                >
                  Forgot password?
                </button>

              </div>

              <div className="input-wrapper">

                <LockKeyhole size={18} />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  onKeyUp={(event) =>
                    setCapsLock(
                      event.getModifierState("CapsLock")
                    )
                  }
                  autoComplete="current-password"
                />

                <button
                  type="button"
                  className="icon-button"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >

                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}

                </button>

              </div>


              {/* CAPS LOCK */}

              {capsLock && (

                <div className="caps-warning">

                  <AlertTriangle size={15} />

                  Caps Lock is enabled

                </div>

              )}


              {/* PASSWORD STRENGTH */}

              {password && (

                <div className="password-strength">

                  <div className="strength-bars">

                    {[1, 2, 3, 4].map((bar) => (

                      <span
                        key={bar}
                        className={
                          bar <= passwordScore
                            ? "active"
                            : ""
                        }
                      />

                    ))}

                  </div>

                  <small>

                    {passwordScore <= 1 &&
                      "Weak password"}

                    {passwordScore === 2 &&
                      "Fair password"}

                    {passwordScore === 3 &&
                      "Strong password"}

                    {passwordScore === 4 &&
                      "Excellent password"}

                  </small>

                </div>

              )}


              {/* REMEMBER */}

              <label className="remember">

                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(event) =>
                    setRemember(event.target.checked)
                  }
                />

                <span>
                  Remember this device
                </span>

              </label>


              {/* LOGIN BUTTON */}

              <button
                type="submit"
                className="primary-button"
                disabled={loading}
              >

                {loading ? (

                  <>
                    <RefreshCw
                      size={19}
                      className="spin"
                    />

                    Authenticating...
                  </>

                ) : (

                  <>
                    Continue to Console

                    <ArrowRight size={19} />
                  </>

                )}

              </button>


              {/* SECURITY */}

              <div className="security-note">

                <LockKeyhole size={15} />

                <span>
                  256-bit encrypted secure session
                </span>

              </div>

            </form>

          )}


          {/* ================================================= */}
          {/* MFA */}
          {/* ================================================= */}

          {mode === "mfa" && (

            <div className="login-card mfa-card">

              <div className="mfa-icon">
                <Smartphone size={30} />
              </div>

              <div className="secure-badge">
                <ShieldCheck size={13} />

                MULTI-FACTOR AUTHENTICATION
              </div>

              <h2>
                Verify your identity
              </h2>

              <p>
                Enter the 6-digit verification code from
                your registered authenticator.
              </p>


              {/* OTP */}

              <div className="otp-container">

                {otp.map((value, index) => (

                  <input
                    key={index}
                    ref={(element) =>
                      (otpRefs.current[index] = element)
                    }
                    value={value}
                    maxLength={1}
                    inputMode="numeric"
                    onChange={(event) =>
                      handleOtpChange(
                        event.target.value,
                        index
                      )
                    }
                    onKeyDown={(event) =>
                      handleOtpKeyDown(
                        event,
                        index
                      )
                    }
                  />

                ))}

              </div>


              {/* VERIFY */}

              <button
                className="primary-button"
                onClick={verifyOtp}
                disabled={
                  loading ||
                  otp.join("").length !== 6
                }
              >

                {loading
                  ? "Verifying..."
                  : "Verify Identity"}

                {!loading && (
                  <ArrowRight size={19} />
                )}

              </button>


              {/* RESEND */}

              <div className="otp-footer">

                {countdown > 0 ? (

                  <span>
                    Resend code in{" "}
                    <strong>
                      {countdown}s
                    </strong>
                  </span>

                ) : (

                  <button
                    className="resend"
                    onClick={() => {
                      setOtp([
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                      ]);

                      setCountdown(30);

                      otpRefs.current[0]?.focus();
                    }}
                  >
                    Resend verification code
                  </button>

                )}

              </div>


              <button
                className="back-button"
                onClick={() => {
                  setOtp([
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                  ]);

                  setMode("login");
                }}
              >
                ← Back to login
              </button>

            </div>

          )}


          {/* ================================================= */}
          {/* SUCCESS */}
          {/* ================================================= */}

          {mode === "success" && (

            <div className="login-card success-card">

              <div className="success-icon">

                <CheckCircle2 size={46} />

              </div>

              <div className="secure-badge">
                <ShieldCheck size={13} />

                AUTHENTICATION SUCCESSFUL
              </div>

              <h2>
                Identity verified
              </h2>

              <p>
                Your secure analyst session has been
                established.
              </p>

              <div className="loading-line">
                <span />
              </div>

              <small>
                Loading investigation console...
              </small>

            </div>

          )}


          {/* ================================================= */}
          {/* FORGOT PASSWORD */}
          {/* ================================================= */}

          {mode === "forgot" && (

            <div className="login-card">

              <div className="mfa-icon">
                <LockKeyhole size={30} />
              </div>

              <div className="secure-badge">
                <ShieldCheck size={13} />

                ACCOUNT RECOVERY
              </div>

              <h2>
                Reset password
              </h2>

              <p>
                Enter your analyst email and we'll send
                secure password-reset instructions.
              </p>


              <label>
                ANALYST EMAIL
              </label>

              <div className="input-wrapper">

                <Mail size={18} />

                <input
                  type="email"
                  placeholder="analyst@fraudguard.ai"
                />

              </div>


              <button
                className="primary-button"
                onClick={() => setMode("login")}
              >

                Send Reset Link

                <ArrowRight size={19} />

              </button>


              <button
                className="back-button"
                onClick={() => setMode("login")}
              >
                ← Back to login
              </button>

            </div>

          )}

        </section>

      </div>

    </div>
  );
}
