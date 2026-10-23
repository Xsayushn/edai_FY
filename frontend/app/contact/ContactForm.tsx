"use client";

import { useState } from "react";

export default function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    category: "Product Audit Request",
    subject: "",
    message: "",
  });
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [feedback, setFeedback] = useState<string>("");
  const [ticketId, setTicketId] = useState<string>("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setFeedback("");

    try {
      const fullSubject = `[${formData.category}] ${formData.subject}`;
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          subject: fullSubject,
          message: formData.message,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to submit form");
      }

      setStatus("success");
      setFeedback(data.message);
      setTicketId(data.ticket_id);
    } catch (err: unknown) {
      setStatus("error");
      setFeedback(err instanceof Error ? err.message : "Submission error occurred.");
    }
  };

  const handleReset = () => {
    setFormData({
      name: "",
      email: "",
      category: "Product Audit Request",
      subject: "",
      message: "",
    });
    setStatus("idle");
    setFeedback("");
    setTicketId("");
  };

  if (status === "success") {
    return (
      <div
        className="glass-panel"
        style={{
          padding: "44px 36px",
          textAlign: "center",
          border: "1px solid var(--neon-lime-border)",
          boxShadow: "var(--shadow-lime)",
        }}
      >
        <span className="badge badge-lime" style={{ marginBottom: "16px" }}>
          DISPATCH CONFIRMED · TICKET #{ticketId}
        </span>
        <h3
          className="font-heading"
          style={{ fontSize: "1.6rem", color: "var(--text-peach)", marginBottom: "14px" }}
        >
          Inquiry Successfully Logged
        </h3>
        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "1rem",
            maxWidth: "520px",
            margin: "0 auto 28px",
            lineHeight: 1.6,
          }}
        >
          {feedback}
        </p>
        <button
          type="button"
          onClick={handleReset}
          className="btn btn-lime"
          style={{ cursor: "pointer" }}
        >
          Send Another Message
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: "40px 36px" }}>
      {status === "error" && (
        <div
          style={{
            padding: "14px 18px",
            marginBottom: "24px",
            background: "var(--crimson-subtle)",
            border: "1px solid var(--crimson-border)",
            borderRadius: "var(--radius-sm)",
            color: "#ff6b68",
            fontSize: "0.92rem",
          }}
        >
          <strong>Error:</strong> {feedback}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="form-group">
          <label htmlFor="name" className="form-label">
            Full Name <span style={{ color: "var(--crimson-alert)" }}>*</span>
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            placeholder="Dr. Jordan Vance"
            value={formData.name}
            onChange={handleChange}
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Work Email <span style={{ color: "var(--crimson-alert)" }}>*</span>
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            placeholder="jordan@hardware-lab.org"
            value={formData.email}
            onChange={handleChange}
            className="form-input"
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: "20px" }}>
        <div className="form-group">
          <label htmlFor="category" className="form-label">
            Inquiry Category
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="form-select"
          >
            <option value="Product Audit Request">Product Audit Request</option>
            <option value="Safety Hazard Escalation">Safety Hazard Escalation</option>
            <option value="Dataset Ingestion (CSV)">Dataset Ingestion (CSV)</option>
            <option value="API Integration & License">API Integration & License</option>
            <option value="Data Privacy & Deletion">Data Privacy & Deletion</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="subject" className="form-label">
            Subject Summary <span style={{ color: "var(--crimson-alert)" }}>*</span>
          </label>
          <input
            id="subject"
            name="subject"
            type="text"
            required
            placeholder="Thermal runaway anomaly in laptop battery batch"
            value={formData.subject}
            onChange={handleChange}
            className="form-input"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="message" className="form-label">
          Detailed Report / Inquiry <span style={{ color: "var(--crimson-alert)" }}>*</span>
        </label>
        <textarea
          id="message"
          name="message"
          required
          rows={5}
          placeholder="Please describe the target ASIN/product ID, observed review anomaly, or technical integration requirements in detail..."
          value={formData.message}
          onChange={handleChange}
          className="form-textarea"
        />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
        <span style={{ fontSize: "0.82rem", color: "var(--text-faint)" }}>
          Strictly encrypted & anonymized per OpinionLens Privacy Policy.
        </span>
        <button
          type="submit"
          disabled={status === "submitting"}
          className="btn btn-lime"
          style={{ minWidth: "160px", opacity: status === "submitting" ? 0.7 : 1 }}
        >
          {status === "submitting" ? "Transmitting..." : "Submit Inquiry"}
        </button>
      </div>
    </form>
  );
}
