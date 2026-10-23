import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "./components/Breadcrumbs";

export const metadata: Metadata = {
  title: "404 · Review Dimension Not Found",
  description:
    "The requested product audit or review vector coordinate was not found in the OpinionLens ChromaDB index.",
  alternates: {
    canonical: "https://opinionlens.ai/404",
  },
};

export default function NotFound() {
  return (
    <div className="container" style={{ paddingTop: "20px", paddingBottom: "80px" }}>
      <Breadcrumbs items={[{ label: "404 Not Found" }]} />

      <div
        className="glass-panel"
        style={{
          maxWidth: "760px",
          margin: "40px auto 0",
          padding: "54px 44px",
          textAlign: "center",
          border: "1px solid rgba(225, 6, 0, 0.3)",
          boxShadow: "0 12px 48px rgba(0,0,0,0.6), 0 0 32px rgba(225, 6, 0, 0.15)",
        }}
      >
        <span className="badge badge-crimson" style={{ marginBottom: "20px" }}>
          HTTP 404 · OUT-OF-INDEX EXCEPTION
        </span>

        {/* Exactly one H1 per page (Requirement 6) */}
        <h1
          className="font-heading"
          style={{
            fontSize: "2.4rem",
            color: "var(--text-peach)",
            marginBottom: "16px",
            lineHeight: 1.2,
          }}
        >
          Signal Lost in the Latent Space
        </h1>

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "1.05rem",
            maxWidth: "540px",
            margin: "0 auto 32px",
            lineHeight: 1.6,
          }}
        >
          The requested hardware identifier, review cluster, or audit report has not been indexed into the ChromaDB vector database.
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: "16px", flexWrap: "wrap", marginBottom: "36px" }}>
          <Link href="/" className="btn btn-lime">
            Return to Audit Center
          </Link>
          <Link href="/contact" className="btn btn-glass">
            Request Product Ingestion
          </Link>
        </div>

        <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "28px" }}>
          <p style={{ fontSize: "0.85rem", color: "var(--text-faint)", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Recommended Verified Hardware Audits
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: "12px", flexWrap: "wrap" }}>
            <Link href="/audit/B000063W3B" className="badge badge-neutral">
              Toshiba Satellite 5105
            </Link>
            <Link href="/audit/B00004Z5M1" className="badge badge-neutral">
              KDS Valiant 6480IPT
            </Link>
            <Link href="/audit/B00000J052" className="badge badge-neutral">
              Kingston 64MB RAM
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
