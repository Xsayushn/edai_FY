import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import Script from "next/script";
import "./globals.css";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://opinionlens.ai";
const GA_ID = process.env.NEXT_PUBLIC_GA_ID || "G-OPINIONLENS2026";
const GSC_TOKEN = process.env.NEXT_PUBLIC_GSC_VERIFICATION || "opinionlens-gsc-verification-token-2026";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "OpinionLens · Explainable RAG for Consumer Product Reviews",
    template: "%s · OpinionLens",
  },
  description:
    "Enterprise-grade explainable RAG engine auditing hardware reviews with 100% cited evidence, polarized consensus detection, and critical-minority safety guardrails.",
  keywords: [
    "OpinionLens",
    "Explainable RAG",
    "Review Intelligence",
    "Product Safety Guard",
    "ChromaDB",
    "Sentiment Aggregation",
    "Hardware Review Audit",
  ],
  authors: [{ name: "OpinionLens Engineering Team", url: SITE_URL }],
  creator: "OpinionLens",
  publisher: "OpinionLens",
  alternates: {
    canonical: SITE_URL,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: SITE_URL,
    siteName: "OpinionLens",
    title: "OpinionLens · Explainable RAG for Consumer Product Reviews",
    description:
      "Enterprise-grade explainable RAG engine auditing hardware reviews with 100% cited evidence and critical-minority safety guardrails.",
    images: [
      {
        url: "/og-image.webp",
        width: 1200,
        height: 630,
        alt: "OpinionLens Explainable RAG and Safety Audit Platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "OpinionLens · Explainable RAG for Consumer Product Reviews",
    description:
      "Enterprise-grade explainable RAG engine auditing hardware reviews with 100% cited evidence and critical-minority safety guardrails.",
    images: ["/og-image.webp"],
    creator: "@opinionlens",
  },
  icons: {
    icon: "/logo.webp",
    apple: "/logo.webp",
  },
  verification: {
    google: GSC_TOKEN,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const orgJsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": `${SITE_URL}/#organization`,
        name: "OpinionLens",
        url: SITE_URL,
        logo: `${SITE_URL}/logo.webp`,
        description:
          "Enterprise-grade explainable RAG engine and consumer safety audit system for hardware reviews.",
        sameAs: [
          "https://github.com/opinionlens",
          "https://twitter.com/opinionlens",
        ],
        contactPoint: {
          "@type": "ContactPoint",
          contactType: "Customer Support & Security Operations",
          url: `${SITE_URL}/contact`,
        },
      },
      {
        "@type": "SoftwareApplication",
        name: "OpinionLens Review Audit Intelligence",
        applicationCategory: "BusinessApplication",
        operatingSystem: "Cloud, Modern Browsers",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "USD",
        },
      },
    ],
  };

  return (
    <html lang="en">
      <head>
        {/* Organization Schema (Requirement 14) */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
        />

        {/* Google Analytics (Requirement 17) */}
        <Script
          strategy="afterInteractive"
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
        />
        <Script
          id="google-analytics-init"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${GA_ID}', {
                page_path: window.location.pathname,
              });
            `,
          }}
        />
      </head>
      <body>
        <div className="ambient-mesh" aria-hidden="true">
          <div className="mesh-orb-crimson" />
          <div className="mesh-orb-lime" />
          <div className="mesh-orb-amber" />
        </div>

        <div className="page-wrapper">
          {/* Header Navigation (Requirement 11: Alt text, Requirement 12: WebP images, Requirement 16: Internal links) */}
          <header className="site-header">
            <div className="container nav-container">
              <Link href="/" className="nav-brand" title="OpinionLens Homepage">
                <Image
                  src="/logo.webp"
                  alt="OpinionLens shield emblem logo"
                  width={34}
                  height={34}
                  priority
                  style={{ borderRadius: "8px" }}
                />
                <span>OpinionLens</span>
              </Link>

              <nav aria-label="Main Navigation">
                <ul className="nav-links">
                  <li>
                    <Link href="/" className="nav-link">
                      Audit Center
                    </Link>
                  </li>
                  <li>
                    <Link href="/#catalog" className="nav-link">
                      Hardware Catalog
                    </Link>
                  </li>
                  <li>
                    <Link href="/#safety" className="nav-link">
                      Safety Guard
                    </Link>
                  </li>
                  <li>
                    <Link href="/privacy" className="nav-link">
                      Privacy Policy
                    </Link>
                  </li>
                  <li>
                    <Link href="/contact" className="nav-link">
                      Contact Ops
                    </Link>
                  </li>
                </ul>
              </nav>

              <div>
                <Link href="/#catalog" className="btn btn-lime">
                  Inspect Hardware
                </Link>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="main-content" id="main-content">
            {children}
          </main>

          {/* Site Footer (Internal Links Mesh, SEO & Semantic Structure) */}
          <footer className="site-footer">
            <div className="container">
              <div className="footer-grid">
                <div className="footer-col">
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
                    <Image
                      src="/logo.webp"
                      alt="OpinionLens logo icon"
                      width={28}
                      height={28}
                      loading="lazy"
                      style={{ borderRadius: "6px" }}
                    />
                    <span style={{ fontFamily: "var(--font-heading)", fontWeight: 700, fontSize: "1.1rem" }}>
                      OpinionLens
                    </span>
                  </div>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", maxWidth: "340px", marginBottom: "18px" }}>
                    Explainable & Safe RAG system for high-stakes consumer hardware review synthesis. 100% cited evidence, zero hallucination tolerance.
                  </p>
                  <span className="badge badge-lime">Status: RAG Cluster Active</span>
                </div>

                <div className="footer-col">
                  <h4>Product Audits</h4>
                  <ul>
                    <li>
                      <Link href="/audit/B000063W3B">Toshiba Satellite 5105</Link>
                    </li>
                    <li>
                      <Link href="/audit/B00004Z5M1">KDS Valiant 6480IPT</Link>
                    </li>
                    <li>
                      <Link href="/audit/B00000J052">Kingston 64MB SODIMM</Link>
                    </li>
                    <li>
                      <Link href="/#catalog">All Verified Datasets</Link>
                    </li>
                  </ul>
                </div>

                <div className="footer-col">
                  <h4>Architecture</h4>
                  <ul>
                    <li>
                      <Link href="/#safety">Safety Guard Engine</Link>
                    </li>
                    <li>
                      <Link href="/#methodology">Vector Grounding</Link>
                    </li>
                    <li>
                      <Link href="/#contention">Polarization Radar</Link>
                    </li>
                    <li>
                      <Link href="/#offline-mode">Hybrid Groq & Offline</Link>
                    </li>
                  </ul>
                </div>

                <div className="footer-col">
                  <h4>Governance & Help</h4>
                  <ul>
                    <li>
                      <Link href="/privacy">Privacy & AI Ethics</Link>
                    </li>
                    <li>
                      <Link href="/contact">Contact & Inquiry Desk</Link>
                    </li>
                    <li>
                      <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                        GitHub Repository
                      </a>
                    </li>
                    <li>
                      <a href="/sitemap.xml">XML Sitemap</a>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="footer-bottom">
                <p>© {new Date().getFullYear()} OpinionLens Inc. All rights reserved. Strict attribution enforced.</p>
                <div style={{ display: "flex", gap: "20px" }}>
                  <Link href="/privacy">Privacy Policy</Link>
                  <Link href="/contact">Audit Request</Link>
                  <a href="/robots.txt">robots.txt</a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
