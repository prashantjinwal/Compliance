"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const loginInitialState = {
  email: "",
  password: "",
};

const signupInitialState = {
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  confirm_password: "",
  organization: "",
};

function getApiErrorMessage(data, fallbackMessage) {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data === "string") {
    return data;
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (typeof data.error === "string") {
    return data.error;
  }

  if (typeof data.message === "string") {
    return data.message;
  }

  const fieldErrors = Object.entries(data)
    .map(function ([key, value]) {
      if (Array.isArray(value)) {
        return key + ": " + value.join(", ");
      }

      if (typeof value === "string") {
        return key + ": " + value;
      }

      return "";
    })
    .filter(Boolean);

  if (fieldErrors.length > 0) {
    return fieldErrors.join(" | ");
  }

  return fallbackMessage;
}

async function parseApiResponse(response) {
  const responseText = await response.text();

  if (!responseText) {
    return null;
  }

  try {
    return JSON.parse(responseText);
  } catch (parseError) {
    return {
      detail: responseText,
    };
  }
}

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [loginForm, setLoginForm] = useState(loginInitialState);
  const [signupForm, setSignupForm] = useState(signupInitialState);
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(function () {
    const token = localStorage.getItem("access_token");

    if (token) {
      window.location.href = "/dashboard";
      return;
    }

    setCheckingAuth(false);
  }, []);

  function switchMode(nextMode) {
    if (loading) {
      return;
    }

    setMode(nextMode);
    setError("");
    setSuccess("");
  }

  function handleLoginChange(event) {
    const name = event.target.name;
    const value = event.target.value;

    setLoginForm(function (previous) {
      return {
        ...previous,
        [name]: value,
      };
    });
  }

  function handleSignupChange(event) {
    const name = event.target.name;
    const value = event.target.value;

    setSignupForm(function (previous) {
      return {
        ...previous,
        [name]: value,
      };
    });
  }

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(API_BASE + "/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: loginForm.email.trim(),
          password: loginForm.password,
        }),
      });

      const data = await parseApiResponse(response);

      if (!response.ok) {
        throw new Error(getApiErrorMessage(data, "Login failed."));
      }

      if (!data || !data.access || !data.refresh) {
        throw new Error("Login failed. Tokens were not returned.");
      }

      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      window.location.href = "/dashboard";
    } catch (requestError) {
      if (requestError instanceof TypeError) {
        setError(
          "Cannot reach the backend at " +
            API_BASE +
            ". Make sure Django is running and CORS is configured."
        );
      } else {
        setError(requestError.message || "Login failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleSignup(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    if (signupForm.password !== signupForm.confirm_password) {
      setError("Password and confirm password must match.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(API_BASE + "/api/auth/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: signupForm.first_name.trim(),
          last_name: signupForm.last_name.trim(),
          email: signupForm.email.trim(),
          password: signupForm.password,
          confirm_password: signupForm.confirm_password,
          organization: signupForm.organization.trim(),
          username: signupForm.email.trim(),
        }),
      });

      const data = await parseApiResponse(response);

      if (!response.ok) {
        throw new Error(getApiErrorMessage(data, "Signup failed."));
      }

      setSuccess("Signup successful. Please log in.");
      setMode("login");
      setSignupForm(signupInitialState);
      setLoginForm(function (previous) {
        return {
          ...previous,
          email: signupForm.email.trim(),
        };
      });
    } catch (requestError) {
      if (requestError instanceof TypeError) {
        setError(
          "Cannot reach the backend at " +
            API_BASE +
            ". Make sure Django is running and CORS is configured."
        );
      } else {
        setError(requestError.message || "Signup failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (checkingAuth) {
    return (
      <div style={styles.centeredPage}>
        <div style={styles.loaderCard}>
          <div style={styles.spinner} />
          <p style={styles.loaderText}>Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.heroSection}>
        <div style={styles.heroBadge}>Compliance Platform</div>
        <h1 style={styles.heroTitle}>Secure access for your compliance team</h1>
        <p style={styles.heroText}>
          Sign in to monitor risk, manage controls, and keep your organization
          aligned with regulatory requirements.
        </p>
        <div style={styles.heroList}>
          <div style={styles.heroItem}>Real-time compliance visibility</div>
          <div style={styles.heroItem}>Centralized team workflows</div>
          <div style={styles.heroItem}>Fast and secure JWT-based access</div>
        </div>
      </div>

      <div style={styles.formSection}>
        <div style={styles.card}>
          <div style={styles.toggleRow}>
            <button
              type="button"
              onClick={function () {
                switchMode("login");
              }}
              disabled={loading}
              style={{
                ...styles.toggleButton,
                ...(mode === "login" ? styles.toggleButtonActive : {}),
              }}
            >
              Login
            </button>
            <button
              type="button"
              onClick={function () {
                switchMode("signup");
              }}
              disabled={loading}
              style={{
                ...styles.toggleButton,
                ...(mode === "signup" ? styles.toggleButtonActive : {}),
              }}
            >
              Sign Up
            </button>
          </div>

          <h2 style={styles.cardTitle}>
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h2>
          <p style={styles.cardSubtitle}>
            {mode === "login"
              ? "Enter your email and password to continue."
              : "Fill in your details to get started."}
          </p>

          {error ? <div style={styles.errorBox}>{error}</div> : null}
          {success ? <div style={styles.successBox}>{success}</div> : null}

          {mode === "login" ? (
            <form onSubmit={handleLogin} style={styles.form}>
              <div style={styles.field}>
                <label htmlFor="login-email" style={styles.label}>
                  Email
                </label>
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  value={loginForm.email}
                  onChange={handleLoginChange}
                  placeholder="name@company.com"
                  style={styles.input}
                  required
                  disabled={loading}
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="login-password" style={styles.label}>
                  Password
                </label>
                <input
                  id="login-password"
                  name="password"
                  type="password"
                  value={loginForm.password}
                  onChange={handleLoginChange}
                  placeholder="Enter your password"
                  style={styles.input}
                  required
                  disabled={loading}
                />
              </div>

              <button type="submit" style={styles.submitButton} disabled={loading}>
                {loading ? "Logging in..." : "Login"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignup} style={styles.form}>
              <div style={styles.row}>
                <div style={styles.field}>
                  <label htmlFor="first_name" style={styles.label}>
                    First Name
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    value={signupForm.first_name}
                    onChange={handleSignupChange}
                    placeholder="John"
                    style={styles.input}
                    required
                    disabled={loading}
                  />
                </div>

                <div style={styles.field}>
                  <label htmlFor="last_name" style={styles.label}>
                    Last Name
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    value={signupForm.last_name}
                    onChange={handleSignupChange}
                    placeholder="Doe"
                    style={styles.input}
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div style={styles.field}>
                <label htmlFor="signup-email" style={styles.label}>
                  Email
                </label>
                <input
                  id="signup-email"
                  name="email"
                  type="email"
                  value={signupForm.email}
                  onChange={handleSignupChange}
                  placeholder="name@company.com"
                  style={styles.input}
                  required
                  disabled={loading}
                />
              </div>

              <div style={styles.field}>
                <label htmlFor="organization" style={styles.label}>
                  Organization
                </label>
                <input
                  id="organization"
                  name="organization"
                  type="text"
                  value={signupForm.organization}
                  onChange={handleSignupChange}
                  placeholder="Your organization"
                  style={styles.input}
                  required
                  disabled={loading}
                />
              </div>

              <div style={styles.row}>
                <div style={styles.field}>
                  <label htmlFor="signup-password" style={styles.label}>
                    Password
                  </label>
                  <input
                    id="signup-password"
                    name="password"
                    type="password"
                    value={signupForm.password}
                    onChange={handleSignupChange}
                    placeholder="Create a password"
                    style={styles.input}
                    required
                    disabled={loading}
                  />
                </div>

                <div style={styles.field}>
                  <label htmlFor="confirm_password" style={styles.label}>
                    Confirm Password
                  </label>
                  <input
                    id="confirm_password"
                    name="confirm_password"
                    type="password"
                    value={signupForm.confirm_password}
                    onChange={handleSignupChange}
                    placeholder="Confirm password"
                    style={styles.input}
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <button type="submit" style={styles.submitButton} disabled={loading}>
                {loading ? "Creating account..." : "Create Account"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    background: "linear-gradient(135deg, #eef6ff 0%, #f8fbf1 100%)",
  },
  centeredPage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #eef6ff 0%, #f8fbf1 100%)",
    padding: "24px",
  },
  heroSection: {
    background: "#0f172a",
    color: "#ffffff",
    padding: "48px 36px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
  },
  heroBadge: {
    alignSelf: "flex-start",
    background: "rgba(255, 255, 255, 0.12)",
    color: "#bfdbfe",
    borderRadius: "999px",
    padding: "8px 14px",
    fontSize: "12px",
    fontWeight: "700",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: "18px",
  },
  heroTitle: {
    fontSize: "42px",
    lineHeight: "1.1",
    fontWeight: "800",
    margin: "0 0 18px 0",
  },
  heroText: {
    fontSize: "17px",
    lineHeight: "1.7",
    color: "#cbd5e1",
    margin: "0 0 28px 0",
    maxWidth: "540px",
  },
  heroList: {
    display: "grid",
    gap: "14px",
  },
  heroItem: {
    background: "rgba(255, 255, 255, 0.08)",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    borderRadius: "16px",
    padding: "16px 18px",
    color: "#e2e8f0",
    fontSize: "15px",
  },
  formSection: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "32px 20px",
  },
  card: {
    width: "100%",
    maxWidth: "560px",
    background: "#ffffff",
    borderRadius: "24px",
    boxShadow: "0 20px 60px rgba(15, 23, 42, 0.12)",
    padding: "32px",
  },
  toggleRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "10px",
    background: "#e2e8f0",
    padding: "6px",
    borderRadius: "14px",
    marginBottom: "24px",
  },
  toggleButton: {
    border: "none",
    borderRadius: "10px",
    padding: "12px",
    background: "transparent",
    color: "#475569",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
  },
  toggleButtonActive: {
    background: "#ffffff",
    color: "#0f172a",
    boxShadow: "0 6px 18px rgba(15, 23, 42, 0.08)",
  },
  cardTitle: {
    margin: "0 0 8px 0",
    color: "#0f172a",
    fontSize: "30px",
    fontWeight: "800",
  },
  cardSubtitle: {
    margin: "0 0 20px 0",
    color: "#64748b",
    fontSize: "15px",
    lineHeight: "1.6",
  },
  form: {
    display: "grid",
    gap: "16px",
  },
  row: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
  },
  field: {
    display: "grid",
    gap: "8px",
  },
  label: {
    fontSize: "14px",
    fontWeight: "700",
    color: "#334155",
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    border: "1px solid #cbd5e1",
    borderRadius: "12px",
    padding: "14px 16px",
    fontSize: "15px",
    color: "#0f172a",
    background: "#ffffff",
    outline: "none",
  },
  submitButton: {
    border: "none",
    borderRadius: "14px",
    padding: "15px 18px",
    background: "linear-gradient(135deg, #0f766e 0%, #2563eb 100%)",
    color: "#ffffff",
    fontSize: "15px",
    fontWeight: "800",
    cursor: "pointer",
  },
  errorBox: {
    background: "#fee2e2",
    color: "#b91c1c",
    border: "1px solid #fecaca",
    borderRadius: "12px",
    padding: "12px 14px",
    marginBottom: "16px",
    fontSize: "14px",
    lineHeight: "1.5",
  },
  successBox: {
    background: "#dcfce7",
    color: "#166534",
    border: "1px solid #bbf7d0",
    borderRadius: "12px",
    padding: "12px 14px",
    marginBottom: "16px",
    fontSize: "14px",
    lineHeight: "1.5",
  },
  loaderCard: {
    background: "#ffffff",
    borderRadius: "20px",
    padding: "28px 32px",
    boxShadow: "0 20px 60px rgba(15, 23, 42, 0.1)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "16px",
  },
  spinner: {
    width: "40px",
    height: "40px",
    borderRadius: "999px",
    border: "4px solid #cbd5e1",
    borderTopColor: "#2563eb",
  },
  loaderText: {
    margin: 0,
    fontSize: "15px",
    color: "#334155",
    fontWeight: "700",
  },
};
