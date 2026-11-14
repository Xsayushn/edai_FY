import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "../../components/Breadcrumbs";
import ProductAuditSearch from "../../components/ProductAuditSearch";
import ReviewChat from "../../components/ReviewChat";
import { fetchProductAudit } from "../../lib/api";

interface PageProps {
  params: Promise<{
    productId: string;
  }>;
  searchParams?: Promise<{
    q?: string;
  }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { productId } = await params;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://opinionlens.ai";

  const title = `Product Review Audit · ${productId}`;
  const description = `Explore review evidence, safety signals, and differing opinions for product ${productId}.`;

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
          alt: `OpinionLens Product Review Audit for ${productId}`,
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

  if (audit.source === "unavailable") {
    return (
      <div className="container" style={{ paddingTop: "20px", paddingBottom: "100px" }}>
        <Breadcrumbs items={[{ label: "Hardware Catalog", href: "/#catalog" }, { label: "Audit unavailable" }]} />
        <div style={{ marginTop: "24px", marginBottom: "28px" }}>
          <ProductAuditSearch brands={[]} products={[]} initialProductId={productId} initialQuestion={query} />
        </div>
        <section className="glass-panel" role="status" style={{ padding: "32px", maxWidth: "760px", margin: "0 auto" }}>
          <h1 className="font-heading" style={{ fontSize: "1.7rem", color: "var(--text-peach)", marginBottom: "12px" }}>
            Live audit unavailable
          </h1>
          <p style={{ color: "var(--text-muted)", lineHeight: 1.6, marginBottom: "20px" }}>
            {audit.error_message}
          </p>
          <Link href="/" className="btn btn-lime">Back to OpinionLens</Link>
        </section>
      </div>
    );
  }

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
        <ProductAuditSearch brands={[]} products={[]} initialProductId={productId} initialQuestion={query} />
      </div>

      {audit.source === "sample" && (
        <section
          role="note"
          className="glass-panel"
          style={{ padding: "14px 18px", marginBottom: "24px", border: "1px solid var(--amber-border, rgba(255, 190, 80, 0.45))" }}
        >
          <strong style={{ color: "var(--amber-warn)" }}>Sample audit data</strong>
          <span style={{ color: "var(--text-muted)", marginLeft: "8px" }}>
            The live API is unreachable. These illustrative findings and quotes are not a live product audit or query-filtered result.
          </span>
        </section>
      )}

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
          <span aria-hidden="true" style={{ color: "var(--text-faint)" }}>Search:</span>
          <span style={{ color: "var(--text-peach)", fontSize: "0.92rem" }}>
            {audit.source === "sample" ? "Sample query:" : "Showing opinion consensus focused on query:"} <strong>&ldquo;{query}&rdquo;</strong>
          </span>
          <Link
            href={`/audit/${productId}`}
            className="badge badge-neutral"
            style={{ marginLeft: "auto", fontSize: "0.75rem" }}
          >
            Clear search
          </Link>
        </div>
      )}

      {/* Audit Header */}
      <div style={{ marginTop: "24px", marginBottom: "36px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "12px" }}>
          <span className="badge badge-neutral">Product ID: {productId}</span>
          <span className="badge badge-lime">{audit.brand}</span>
          <span className="badge badge-neutral">{audit.review_count} {audit.source === "sample" ? "sample reviews" : "reviews analyzed"}</span>
          <span className="badge badge-neutral">⭐ {audit.rating_avg} / 5.0 average in this set</span>
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
            Review themes, safety signals, and dissenting opinions from the analyzed review set.
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
            <h2
              id="safety-guard-heading"
              className="font-heading"
              style={{ fontSize: "1.35rem", color: "#ff5450", margin: 0 }}
            >
              Safety mentions
            </h2>
            <span className="badge badge-crimson" style={{ marginLeft: "auto" }}>
              Review these comments
            </span>
          </div>

          <p style={{ color: "var(--text-peach)", fontSize: "0.95rem", marginBottom: "16px", lineHeight: 1.6 }}>
            Safety signals appeared in the analyzed reviews. Read the quoted reports in context before drawing conclusions.
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
                    Potential risk: {alert.risk_term}
                  </strong>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-faint)" }}>
                    Mentioned in {alert.matching_reviews} reviews
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
          <div>
            <h2
              id="safety-guard-heading"
              className="font-heading"
              style={{ fontSize: "1.05rem", color: "var(--neon-lime)", margin: 0 }}
            >
              {audit.review_count === 0 ? "Safety not assessed" : "No safety mentions found"}
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.86rem", margin: 0 }}>
              {audit.review_count === 0
                ? "No reviews were retrieved, so safety signals could not be assessed."
                : "No matching safety terms were found in this review set. This does not rule out issues in reviews that were not analyzed."}
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
              What reviewers say
            </h2>
            <span className={`badge ${audit.source === "sample" ? "badge-amber" : "badge-lime"}`}>
              {audit.source === "sample" ? "Sample citations" : "Citations included"}
            </span>
          </div>

          <p style={{ color: "var(--text-peach)", fontSize: "1.02rem", lineHeight: 1.7, marginBottom: "24px" }}>
            {audit.summary.overview}
          </p>

          <h3
            className="font-heading"
            style={{ fontSize: "1rem", color: "var(--text-muted)", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.04em" }}
          >
            Consensus Findings
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
              Where opinions differ
            </h2>
            <span className="badge badge-amber">Mixed opinions</span>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "20px", lineHeight: 1.6 }}>
            Topics with both positive and negative comments in the reviews analyzed.
          </p>

          {audit.contested.length === 0 ? (
            <p style={{ color: "var(--text-faint)", fontStyle: "italic", fontSize: "0.9rem" }}>
              No aspect met the current threshold for a contested label in this review set.
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
                      Mixed feedback
                    </span>
                  </div>

                  <div style={{ display: "flex", gap: "10px", fontSize: "0.82rem", marginBottom: "10px" }}>
                    <span style={{ color: "var(--neon-lime)" }}>{item.pos_count} positive</span>
                    <span style={{ color: "#e8a29b" }}>{item.neg_count} negative</span>
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

      <ReviewChat productId={productId} />

      {/* Retrieved Reviews (Evidence Inspection) */}
      <section aria-labelledby="raw-reviews-heading" style={{ marginBottom: "60px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h2 id="raw-reviews-heading" className="font-heading" style={{ fontSize: "1.5rem", color: "var(--text-peach)" }}>
            Review Evidence
          </h2>
          <span style={{ color: "var(--text-faint)", fontSize: "0.88rem" }}>
            Excerpts from the reviews analyzed for this audit
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "20px" }}>
          {audit.reviews.map((rev) => (
            <article
              key={rev.review_id}
              id={`review-${rev.review_id}`}
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
                    <span aria-label={`${rev.rating} out of 5 stars`}>
                      {"★".repeat(Math.min(5, Math.max(1, Math.round(rev.rating))))}
                      {"☆".repeat(5 - Math.min(5, Math.max(1, Math.round(rev.rating))))}
                    </span>
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

      {/* Continue exploring the live catalog */}
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
            Review another product
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.92rem", maxWidth: "560px" }}>
            Choose another product from the catalog or enter its product ID.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <Link href="/" className="btn btn-lime">
            Find a product
          </Link>
        </div>
      </section>
    </div>
  );
}
