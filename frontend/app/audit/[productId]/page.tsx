import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "../../components/Breadcrumbs";
import { fetchProductAudit } from "../../lib/api";

import DeviceSearchBox from "../../components/DeviceSearchBox";

interface PageProps {
  params: Promise<{
    productId: string;
  }>;
  searchParams?: Promise<{
    q?: string;
  }>;
}

export async function generateMetadata({ params, searchParams }: PageProps): Promise<Metadata> {
  const { productId } = await params;
  const sp = searchParams ? await searchParams : {};
  const audit = await fetchProductAudit(productId, sp.q);
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://opinionlens.ai";

  const title = `Audit: ${audit.product_name || productId} · Safety & Consensus`;
  const description = `Read explainable RAG review audit for ${audit.product_name || productId}. ${audit.review_count} verified reviews analyzed with ${audit.alerts.length} critical safety alerts.`;

  return {
    title,
    description,
    alternates: {
      canonical: `${siteUrl}/audit/${productId}`,
    },
    openGraph: {
      title,
      description,
      url: `${siteUrl}/audit/${productId}`,
      images: [
        {
          url: "/og-image.webp",
          width: 1200,
          height: 630,
          alt: `OpinionLens Audit Report for ${audit.product_name || productId}`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: ["/og-image.webp"],
    },
  };
}

export default async function AuditPage({ params, searchParams }: PageProps) {
  const { productId } = await params;
  const sp = searchParams ? await searchParams : {};
  const query = sp.q || "";
  const audit = await fetchProductAudit(productId, query);

  const hasCriticalRisks = audit.alerts && audit.alerts.length > 0;

  return (
    <div className="container" style={{ paddingTop: "20px", paddingBottom: "100px" }}>
      {/* Requirement 15: Breadcrumbs with BreadcrumbList JSON-LD */}
      <Breadcrumbs
        items={[
          { label: "Hardware Catalog", href: "/#catalog" },
          { label: `Audit ${productId}` },
        ]}
      />

      {/* Switch Device & Ask Question Bar */}
      <div style={{ marginTop: "16px", marginBottom: "28px" }}>
        <DeviceSearchBox
          currentProductId={productId}
          placeholder="Switch to another device or ask aspect (e.g. heating, battery, noise)..."
        />
      </div>

      {query && (
        <div
          style={{
            padding: "12px 20px",
            marginBottom: "24px",
            background: "var(--neon-lime-subtle)",
            border: "1px solid var(--neon-lime-border)",
            borderRadius: "var(--radius-sm)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <span style={{ fontSize: "1.1rem" }}>🔍</span>
          <span style={{ color: "var(--text-peach)", fontSize: "0.92rem" }}>
            Showing opinion consensus focused on query: <strong>&ldquo;{query}&rdquo;</strong>
          </span>
          <Link
            href={`/audit/${productId}`}
            className="badge badge-neutral"
            style={{ marginLeft: "auto", fontSize: "0.75rem" }}
          >
            Clear Filter ✕
          </Link>
        </div>
      )}

      {/* Audit Header */}
      <div style={{ marginTop: "24px", marginBottom: "36px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "12px" }}>
          <span className="badge badge-neutral">ASIN: {productId}</span>
          <span className="badge badge-lime">{audit.brand}</span>
          <span className="badge badge-neutral">{audit.review_count} Verified Customer Reviews</span>
          <span className="badge badge-neutral">⭐ {audit.rating_avg} / 5.0 Rating</span>
        </div>

        {/* Requirement 6: Exactly one H1 per page */}
        <h1
          className="font-heading"
          style={{
            fontSize: "2.6rem",
            color: "var(--text-peach)",
            lineHeight: 1.2,
            marginBottom: "14px",
          }}
        >
          {audit.product_name || `Hardware Review Audit: ${productId}`}
        </h1>

        <p style={{ color: "var(--text-muted)", fontSize: "1.05rem", maxWidth: "860px" }}>
          Deep-evidence synthesis powered by Sentence-Transformers vector clustering in ChromaDB with critical-minority safety guardrails.
        </p>
      </div>

      {/* 1. Critical-Minority Safety Guard Banner */}
      {hasCriticalRisks ? (
        <section
          aria-labelledby="safety-guard-heading"
          className="glass-panel glass-panel-crimson"
          style={{
            padding: "28px 32px",
            marginBottom: "36px",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
            <span style={{ fontSize: "1.4rem" }}>🚨</span>
            <h2
              id="safety-guard-heading"
              className="font-heading"
              style={{ fontSize: "1.35rem", color: "#ff5450", margin: 0 }}
            >
              Critical-Minority Safety Hazard Detected
            </h2>
            <span className="badge badge-crimson" style={{ marginLeft: "auto" }}>
              HIGH PRIORITY INTERCEPTION
            </span>
          </div>

          <p style={{ color: "var(--text-peach)", fontSize: "0.95rem", marginBottom: "16px", lineHeight: 1.6 }}>
            Despite positive overall ratings, our critical safety guard intercepted verified reports of acute hardware danger. These hazards represent low-frequency but catastrophic failure modes.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            {audit.alerts.map((alert, idx) => (
              <div
                key={idx}
                style={{
                  padding: "16px 20px",
                  background: "rgba(0, 0, 0, 0.35)",
                  borderRadius: "var(--radius-sm)",
                  borderLeft: "4px solid var(--crimson-alert)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <strong style={{ color: "#ff8280", textTransform: "uppercase", fontSize: "0.85rem", letterSpacing: "0.04em" }}>
                    Hazard Type: {alert.risk_term}
                  </strong>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-faint)" }}>
                    {alert.matching_reviews} reviews affected
                  </span>
                </div>
                {alert.quotes.map((quote, qIdx) => (
                  <p
                    key={qIdx}
                    style={{
                      fontStyle: "italic",
                      color: "var(--text-muted)",
                      fontSize: "0.92rem",
                      marginBottom: "6px",
                      lineHeight: 1.5,
                    }}
                  >
                    &ldquo;{quote}&rdquo;
                  </p>
                ))}
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section
          aria-labelledby="safety-guard-heading"
          className="glass-panel"
          style={{
            padding: "20px 24px",
            marginBottom: "36px",
            border: "1px solid var(--neon-lime-border)",
            display: "flex",
            alignItems: "center",
            gap: "14px",
          }}
        >
          <span style={{ fontSize: "1.3rem" }}>🛡️</span>
          <div>
            <h2
              id="safety-guard-heading"
              className="font-heading"
              style={{ fontSize: "1.05rem", color: "var(--neon-lime)", margin: 0 }}
            >
              No Acute Safety Hazards Intercepted
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.86rem", margin: 0 }}>
              Zero critical thermal runaway, electrical fire, or structural shatter incidents detected across the indexed corpus.
            </p>
          </div>
        </section>
      )}

      {/* Main Grid: Attributed Summary & Contested Dimensions */}
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "32px", marginBottom: "44px" }}>
        {/* Attributed Synthesis */}
        <section aria-labelledby="consensus-heading" className="glass-panel" style={{ padding: "32px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
            <h2 id="consensus-heading" className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)" }}>
              Attributed Consensus Synthesis
            </h2>
            <span className="badge badge-lime">100% Evidence Grounded</span>
          </div>

          <p style={{ color: "var(--text-peach)", fontSize: "1.02rem", lineHeight: 1.7, marginBottom: "24px" }}>
            {audit.summary.overview}
          </p>

          <h3
            className="font-heading"
            style={{ fontSize: "1rem", color: "var(--text-muted)", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.04em" }}
          >
            Verified Consensus Findings
          </h3>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "14px" }}>
            {audit.summary.consensus_points.map((point, idx) => (
              <li
                key={idx}
                style={{
                  display: "flex",
                  gap: "12px",
                  alignItems: "flex-start",
                  padding: "12px 16px",
                  background: "rgba(255, 255, 255, 0.03)",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "22px",
                    height: "22px",
                    borderRadius: "50%",
                    background: "var(--neon-lime-subtle)",
                    color: "var(--neon-lime)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    flexShrink: 0,
                    marginTop: "2px",
                  }}
                >
                  {idx + 1}
                </span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}>
                  {point}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Contested Dimensions */}
        <section aria-labelledby="contested-heading" className="glass-panel" style={{ padding: "32px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
            <h2 id="contested-heading" className="font-heading" style={{ fontSize: "1.4rem", color: "var(--text-peach)" }}>
              Polarized Contention Radar
            </h2>
            <span className="badge badge-amber">Contested Sentiment</span>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "20px", lineHeight: 1.6 }}>
            Aspects where consumer opinion splits closest to 50/50, indicating variable manufacturing tolerances or divided user expectations.
          </p>

          {audit.contested.length === 0 ? (
            <p style={{ color: "var(--text-faint)", fontStyle: "italic", fontSize: "0.9rem" }}>
              No high-polarity contention detected. Sentiment remains homogeneous across all extracted aspects.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {audit.contested.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "16px",
                    background: "rgba(0, 0, 0, 0.25)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-glass)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <strong style={{ color: "var(--text-peach)", fontSize: "0.92rem" }}>{item.aspect}</strong>
                    <span className="badge badge-amber" style={{ fontSize: "0.72rem" }}>
                      Polarity Index: {item.ratio}
                    </span>
                  </div>

                  <div style={{ display: "flex", gap: "10px", fontSize: "0.82rem", marginBottom: "10px" }}>
                    <span style={{ color: "var(--neon-lime)" }}>👍 {item.pos_count} Positive</span>
                    <span style={{ color: "#ff6b68" }}>👎 {item.neg_count} Negative</span>
                  </div>

                  {item.sample_positive && (
                    <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "6px" }}>
                      <span style={{ color: "var(--neon-lime)", fontWeight: 600 }}>[Pro]:</span> &ldquo;{item.sample_positive}&rdquo;
                    </div>
                  )}

                  {item.sample_negative && (
                    <div style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                      <span style={{ color: "#ff6b68", fontWeight: 600 }}>[Con]:</span> &ldquo;{item.sample_negative}&rdquo;
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Raw Verified Reviews Corpus (Evidence Inspection) */}
      <section aria-labelledby="raw-reviews-heading" style={{ marginBottom: "60px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 id="raw-reviews-heading" className="font-heading" style={{ fontSize: "1.5rem", color: "var(--text-peach)" }}>
            Ground Truth Review Corpus (Citations Source)
          </h2>
          <span style={{ color: "var(--text-faint)", fontSize: "0.88rem" }}>
            Showing verified customer purchases indexed in ChromaDB
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "20px" }}>
          {audit.reviews.slice(0, 6).map((rev) => (
            <article
              key={rev.review_id}
              className="glass-panel"
              style={{
                padding: "22px 24px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                  <span style={{ color: "var(--amber-warn)", letterSpacing: "2px", fontSize: "0.9rem" }}>
                    {"★".repeat(Math.min(5, Math.max(1, Math.round(rev.rating))))}
                    {"☆".repeat(5 - Math.min(5, Math.max(1, Math.round(rev.rating))))}
                  </span>
                  <span className="badge badge-neutral" style={{ fontSize: "0.72rem" }}>
                    Ref #{rev.review_id}
                  </span>
                </div>
                <p style={{ color: "var(--text-muted)", fontSize: "0.92rem", lineHeight: 1.6, marginBottom: "16px" }}>
                  &ldquo;{rev.review_text}&rdquo;
                </p>
              </div>

              <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.78rem", color: "var(--text-faint)" }}>{rev.date}</span>
                {rev.helpful_votes > 0 && (
                  <span style={{ fontSize: "0.78rem", color: "var(--neon-lime)" }}>
                    {rev.helpful_votes} people found helpful
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Internal Navigation & Related Audits (Requirement 16) */}
      <section
        className="glass-panel"
        style={{
          padding: "36px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "24px",
        }}
      >
        <div>
          <h3 className="font-heading" style={{ fontSize: "1.3rem", color: "var(--text-peach)", marginBottom: "8px" }}>
            Explore More Hardware Audits
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.92rem", maxWidth: "560px" }}>
            Compare evidence-backed RAG sentiment profiles across enterprise notebooks, RAM upgrades, and mobile devices.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <Link href="/audit/B00004Z5M1" className="btn btn-glass">
            Audit KDS Valiant
          </Link>
          <Link href="/audit/B00000J052" className="btn btn-glass">
            Audit Kingston RAM
          </Link>
          <Link href="/contact" className="btn btn-lime">
            Request Custom ASIN Audit
          </Link>
        </div>
      </section>
    </div>
  );
}
