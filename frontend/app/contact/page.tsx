import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "../components/Breadcrumbs";
import ContactForm from "./ContactForm";

export const metadata: Metadata = {
  title: "Contact Audit Operations & Data Desk",
  description:
    "Submit hardware review audit requests, report consumer safety signals, or query dataset ingestion pipelines with OpinionLens safety engineers.",
  alternates: {
    canonical: "https://opinionlens.ai/contact",
  },
  openGraph: {
    title: "Contact Audit Operations · OpinionLens",
    description:
      "Direct communication channel for hardware product review audits, critical safety alerts, and dataset ingestion requests.",
    url: "https://opinionlens.ai/contact",
    images: [{ url: "/og-image.webp", width: 1200, height: 630, alt: "Contact OpinionLens Ops" }],
  },
};

export default function ContactPage() {
  return (
    <div className="container" style={{ paddingTop: "20px", paddingBottom: "100px" }}>
      <Breadcrumbs items={[{ label: "Contact Operations" }]} />

      <div style={{ maxWidth: "860px", margin: "32px auto 0" }}>
        {/* Exactly one H1 per page (Requirement 6) */}
        <header style={{ marginBottom: "36px" }}>
          <span className="badge badge-lime" style={{ marginBottom: "14px" }}>
            24/7 INTELLIGENCE & SAFETY DISPATCH
          </span>
          <h1
            className="font-heading"
            style={{
              fontSize: "2.5rem",
              color: "var(--text-peach)",
              lineHeight: 1.2,
              marginBottom: "14px",
            }}
          >
            Contact Audit Operations & Data Desk
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", lineHeight: 1.6 }}>
            Connect directly with OpinionLens research engineers regarding critical-minority safety escalations, custom hardware dataset ingestions, or enterprise RAG integration.
          </p>
        </header>

        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "32px" }}>
          <ContactForm />

          {/* Cross-linking cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div className="glass-panel" style={{ padding: "24px 28px" }}>
              <h3 className="font-heading" style={{ fontSize: "1.1rem", color: "var(--text-peach)", marginBottom: "8px" }}>
                Data Rights & Compliance
              </h3>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", marginBottom: "14px", lineHeight: 1.6 }}>
                Review our comprehensive AI ethics, review anonymization, and vector storage protocols.
              </p>
              <Link href="/privacy" className="btn btn-glass" style={{ fontSize: "0.85rem", padding: "6px 14px" }}>
                Read Privacy Policy →
              </Link>
            </div>

            <div className="glass-panel" style={{ padding: "24px 28px" }}>
              <h3 className="font-heading" style={{ fontSize: "1.1rem", color: "var(--text-peach)", marginBottom: "8px" }}>
                Inspect Live Audits
              </h3>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", marginBottom: "14px", lineHeight: 1.6 }}>
                Explore real-time RAG sentiment analysis and hazard detection on benchmark hardware.
              </p>
              <Link href="/audit/B000063W3B" className="btn btn-glass" style={{ fontSize: "0.85rem", padding: "6px 14px" }}>
                View Toshiba Audit →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
