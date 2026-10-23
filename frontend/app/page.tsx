import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { fetchCatalogProducts } from "./lib/api";

export const metadata: Metadata = {
  title: "OpinionLens · Explainable RAG for Consumer Product Reviews",
  description:
    "Enterprise-grade explainable RAG engine auditing hardware reviews with 100% cited evidence, polarized consensus detection, and critical-minority safety guardrails.",
  alternates: {
    canonical: "https://opinionlens.ai",
  },
  openGraph: {
    title: "OpinionLens · Explainable RAG for Consumer Product Reviews",
    description:
      "Enterprise-grade explainable RAG engine auditing hardware reviews with 100% cited evidence and critical-minority safety guardrails.",
    url: "https://opinionlens.ai",
    images: [
      {
        url: "/og-image.webp",
        width: 1200,
        height: 630,
        alt: "OpinionLens Explainable RAG and Safety Platform",
      },
    ],
  },
};

export default async function HomePage() {
  const products = await fetchCatalogProducts();

  return (
    <div className="container" style={{ paddingTop: "40px", paddingBottom: "100px" }}>
      {/* Hero Section */}
      <section
        style={{
          textAlign: "center",
          maxWidth: "920px",
          margin: "0 auto 70px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", marginBottom: "20px" }}>
          <span className="badge badge-lime">Next-Gen Review Intelligence</span>
          <span className="badge badge-neutral">ChromaDB · HuggingFace · Groq RAG</span>
        </div>

        {/* Exactly one H1 per page (Requirement 6) */}
        <h1
          className="font-heading"
          style={{
            fontSize: "3.4rem",
            color: "var(--text-peach)",
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            marginBottom: "20px",
          }}
        >
          Explainable & Safe RAG for Consumer Product Reviews
        </h1>

        <p
          style={{
            fontSize: "1.2rem",
            color: "var(--text-muted)",
            lineHeight: 1.6,
            maxWidth: "760px",
            marginBottom: "36px",
          }}
        >
          Synthesize thousands of raw hardware reviews into evidence-grounded consensus points, detect contested sentiment polarity, and intercept hidden critical-minority safety hazards.
        </p>

        {/* Quick Launch Buttons */}
        <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", justifyContent: "center", marginBottom: "40px" }}>
          <Link href="/audit/B000063W3B" className="btn btn-lime" style={{ padding: "14px 28px", fontSize: "1.05rem" }}>
            Inspect Flagship Toshiba Audit →
          </Link>
          <Link href="#catalog" className="btn btn-glass" style={{ padding: "14px 26px" }}>
            Browse Hardware Catalog
          </Link>
        </div>

        {/* Hero Visual Preview (Requirement 11: Alt text, Requirement 12: WebP images, Requirement 13: Lazy loading) */}
        <div
          className="glass-panel"
          style={{
            width: "100%",
            borderRadius: "var(--radius-lg)",
            overflow: "hidden",
            border: "1px solid var(--border-glass)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.7), 0 0 40px rgba(191, 226, 58, 0.1)",
          }}
        >
          <Image
            src="/og-image.webp"
            alt="OpinionLens interactive review intelligence dashboard showing critical safety guard and attributed citations"
            width={1200}
            height={630}
            priority
            style={{ width: "100%", height: "auto", display: "block" }}
          />
        </div>
      </section>

      {/* 3 Pillars Section */}
      <section
        id="safety"
        style={{ marginBottom: "80px" }}
      >
        <div style={{ textAlign: "center", marginBottom: "44px" }}>
          <span className="badge badge-crimson" style={{ marginBottom: "12px" }}>
            PATENT-PENDING SAFETY ENGINE
          </span>
          <h2 className="font-heading" style={{ fontSize: "2.2rem", color: "var(--text-peach)" }}>
            Engineered for Ground Truth & Consumer Protection
          </h2>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "28px" }}>
          {/* Pillar 1 */}
          <div className="glass-panel glass-panel-glow" style={{ padding: "32px 28px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "var(--crimson-subtle)",
                border: "1px solid var(--crimson-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.5rem",
                marginBottom: "20px",
              }}
            >
              🚨
            </div>
            <h3 className="font-heading" style={{ fontSize: "1.3rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              Critical-Minority Safety Guard
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}>
              A 4.5-star laptop might still have 3 reviews reporting battery fires or electrical short circuits. Conventional summaries hide them—our safety guard elevates low-frequency life-safety risks immediately.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="glass-panel glass-panel-glow" style={{ padding: "32px 28px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "var(--neon-lime-subtle)",
                border: "1px solid var(--neon-lime-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.5rem",
                marginBottom: "20px",
              }}
            >
              🔍
            </div>
            <h3 className="font-heading" style={{ fontSize: "1.3rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              100% Attributed Citations
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}>
              Every single generated claim references exact review IDs in the ChromaDB vector database. Verify any finding with one click against verified purchase testimonials.
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="glass-panel glass-panel-glow" style={{ padding: "32px 28px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "var(--amber-subtle)",
                border: "1px solid var(--amber-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.5rem",
                marginBottom: "20px",
              }}
            >
              ⚖️
            </div>
            <h3 className="font-heading" style={{ fontSize: "1.3rem", color: "var(--text-peach)", marginBottom: "12px" }}>
              Polarized Contention Radar
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}>
              Uncover contested product dimensions where sentiment splits 50/50. View side-by-side positive and negative customer quotes on thermal performance, keyboard travel, and battery lifespan.
            </p>
          </div>
        </div>
      </section>

      {/* Hardware Catalog Section (Requirement 16: Internal links mesh) */}
      <section id="catalog" style={{ marginBottom: "80px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "28px", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <span className="badge badge-lime" style={{ marginBottom: "10px" }}>
              VERIFIED CORPUS
            </span>
            <h2 className="font-heading" style={{ fontSize: "2rem", color: "var(--text-peach)" }}>
              Indexed Hardware Products
            </h2>
          </div>
          <Link href="/contact" className="btn btn-glass" style={{ fontSize: "0.9rem" }}>
            Request New Dataset Ingestion →
          </Link>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "22px" }}>
          {products.map((item) => (
            <article
              key={item.product_id}
              className="glass-panel glass-panel-glow"
              style={{ padding: "24px 28px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                  <span className="badge badge-neutral" style={{ fontSize: "0.75rem" }}>
                    {item.brand}
                  </span>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-faint)" }}>
                    ASIN: {item.product_id}
                  </span>
                </div>

                <h3 className="font-heading" style={{ fontSize: "1.2rem", color: "var(--text-peach)", marginBottom: "8px" }}>
                  {item.product_name}
                </h3>

                <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "16px" }}>
                  {item.review_count} verified purchase reviews indexed with vector embeddings.
                </p>
              </div>

              <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--neon-lime)" }}>
                  ● RAG Index Ready
                </span>
                <Link href={`/audit/${item.product_id}`} className="btn btn-lime" style={{ padding: "6px 16px", fontSize: "0.85rem" }}>
                  View Full Audit →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Trust & Architecture Banner */}
      <section
        id="methodology"
        className="glass-panel"
        style={{
          padding: "44px 40px",
          display: "grid",
          gridTemplateColumns: "1.2fr 1fr",
          gap: "36px",
          alignItems: "center",
        }}
      >
        <div>
          <span className="badge badge-neutral" style={{ marginBottom: "12px" }}>
            ARCHITECTURE SPECIFICATION
          </span>
          <h2 className="font-heading" style={{ fontSize: "1.8rem", color: "var(--text-peach)", marginBottom: "14px" }}>
            Zero Hallucination Tolerance
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.98rem", lineHeight: 1.6, marginBottom: "20px" }}>
            OpinionLens combines offline rule-based dependency parsers with Llama 3 on Groq Cloud. If external LLM inference ever fails or rate limits, our deterministic offline sentiment aggregator immediately takes over with zero downtime.
          </p>
          <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }}>
            <Link href="/privacy" className="btn btn-glass">
              Data Privacy & Architecture
            </Link>
            <Link href="/contact" className="btn btn-lime">
              Contact Research Team
            </Link>
          </div>
        </div>

        <div
          style={{
            background: "rgba(0, 0, 0, 0.45)",
            padding: "24px",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.85rem",
            color: "var(--text-peach)",
          }}
        >
          <div style={{ color: "var(--text-faint)", marginBottom: "10px" }}>// Verified System Metrics</div>
          <div style={{ marginBottom: "6px" }}><span style={{ color: "var(--neon-lime)" }}>✓</span> Vector DB: ChromaDB Multi-Collection</div>
          <div style={{ marginBottom: "6px" }}><span style={{ color: "var(--neon-lime)" }}>✓</span> Embeddings: all-MiniLM-L6-v2 (384-dim)</div>
          <div style={{ marginBottom: "6px" }}><span style={{ color: "var(--neon-lime)" }}>✓</span> Safety Interception: Critical Rule Filters</div>
          <div style={{ marginBottom: "6px" }}><span style={{ color: "var(--neon-lime)" }}>✓</span> Aspect Mining: Rule-based & Groq Llama 3</div>
          <div><span style={{ color: "var(--neon-lime)" }}>✓</span> SSR Engine: Next.js App Router</div>
        </div>
      </section>
    </div>
  );
}
