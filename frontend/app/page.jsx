"use client";

import { useEffect } from "react";

export default function HomePage() {
  useEffect(function () {
    const token = localStorage.getItem("access_token");

    if (token) {
      window.location.href = "/dashboard";
      return;
    }

    window.location.href = "/auth";
  }, []);

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.spinner} />
        <p style={styles.text}>Redirecting...</p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #eef6ff 0%, #f8fbf1 100%)",
    padding: "24px",
  },
  card: {
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
  text: {
    margin: 0,
    fontSize: "15px",
    fontWeight: "700",
    color: "#334155",
  },
};
