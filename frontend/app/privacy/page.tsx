import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "../components/Breadcrumbs";

export const metadata: Metadata = {
  title: "Privacy Policy & Explainable AI Data Governance",
  description:
    "Learn how OpinionLens safeguards consumer review privacy, anonymizes vector embeddings in ChromaDB, and ensures zero ungrounded training leakage.",
  alternates: {
    canonical: "https://opinionlens.ai/privacy",
  },
  openGraph: {
    title: "Privacy Policy · OpinionLens Review Intelligence",
    description:
      "Enterprise explainable AI data governance, review anonymization, and consumer data rights.",
    url: "https://opinionlens.ai/privacy",
    images: [{ url: "/og-image.webp", width: 1200, height: 630, alt: "OpinionLens Privacy & Governance" }],
  },
};

export default function PrivacyPage() {
  return (
    <div className="container" style={{ paddingTop: "20px", paddingBottom: "100px" }}>
      <Breadcrumbs items={[{ label: "Privacy Policy" }]} />

      <div style={{ maxWidth: "860px", margin: "32px auto 0" }}>
        {/* Exactly one H1 per page (Requirement 6) */}
        <header style={{ marginBottom: "40px" }}>
          <span className="badge badge-lime" style={{ marginBottom: "14px" }}>
            DATA GOVERNANCE & COMPLIANCE
          </span>
          <h1
            className="font-heading"
            style={{
              fontSize: "2.6rem",
              color: "var(--text-peach)",
              lineHeight: 1.2,
              marginBottom: "16px",
            }}
          >
            Privacy Policy & Explainable AI Governance
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "1.05rem" }}>
            Effective Date: October 2026 · Compliance Edition 2.4
          </p>
        </header>

        <div className="glass-panel" style={{ padding: "40px 44px", display: "flex", flexDirection: "column", gap: "36px" }}>
          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              1. Architecture & Ethical Foundation
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7 }}>
              OpinionLens operates as an explainable Retrieval-Augmented Generation (RAG) platform. Unlike conventional generative language systems that fabricate claims or ingest proprietary user data into model weights, OpinionLens enforces strict deterministic attribution: every single synthesis statement is mathematically backed by verified, raw consumer reviews with direct sentence-level citations.
            </p>
          </section>

          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              2. Review Ingestion & Anonymization
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7, marginBottom: "12px" }}>
              When public e-commerce catalogs or verified benchmark datasets are processed into OpinionLens, personal identifiable information (PII) including real customer names, mailing addresses, payment details, and IP addresses are stripped before ingestion.
            </p>
            <ul style={{ paddingLeft: "24px", color: "var(--text-muted)", lineHeight: 1.7 }}>
              <li><strong>Raw Text Storage:</strong> Review texts are indexed strictly for semantic search and consensus scoring.</li>
              <li><strong>Zero Permanent Private LLM Memory:</strong> User queries executed in Groq or offline fallback mode are ephemeral and never cached into foundation model training corpora.</li>
            </ul>
          </section>

          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              3. Vector Embeddings & ChromaDB Governance
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7 }}>
              Embeddings generated via HuggingFace Sentence Transformers (<code>all-MiniLM-L6-v2</code>) are stored locally in isolated, partitioned ChromaDB collections. Each hardware product is bounded by its unique Amazon Standard Identification Number (ASIN), ensuring strict multi-tenant boundary isolation.
            </p>
          </section>

          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              4. Critical-Minority Safety Interception
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7 }}>
              Our patent-pending safety engine audits severe consumer hazard terms (e.g. fire hazards, thermal runaway, explosion risks, motherboard short circuits) regardless of high average star ratings. When safety flags are detected, alerts are foregrounded with exact quotes to protect consumer wellbeing.
            </p>
          </section>

          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              5. Analytics, Cookies & Telemetry
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7 }}>
              We employ Google Analytics 4 (<code>NEXT_PUBLIC_GA_ID</code>) purely for aggregate system telemetry, measuring page responsiveness and navigation bottlenecks. We do not sell, license, or monetize behavioral data to third-party ad networks.
            </p>
          </section>

          <section>
            <h2 className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              6. Rights & Inquiries
            </h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.7, marginBottom: "16px" }}>
              Under GDPR, CCPA, and international data regulations, consumers and brand representatives may request dataset exclusion, vector purging, or audit dispute reviews at any time.
            </p>
            <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
              <Link href="/contact" className="btn btn-lime">
                Contact Data Protection Officer
              </Link>
              <Link href="/" className="btn btn-glass">
                Explore Public Audits
              </Link>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
