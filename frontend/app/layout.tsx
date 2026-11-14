import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import "./globals.css";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://opinionlens.ai";
const GA_ID = process.env.NEXT_PUBLIC_GA_ID;
const GSC_TOKEN = process.env.NEXT_PUBLIC_GSC_VERIFICATION;

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "OpinionLens — Explainable & Safe RAG for Opinion Summarization",
    template: "%s · OpinionLens",
  },
  description:
    "Summaries of product review themes, safety mentions, and differing opinions, with links to the source comments.",
  keywords: [
    "OpinionLens",
    "Explainable RAG",
    "Review Intelligence",
    "Product Safety Guard",
    "ChromaDB",
    "Sentiment Aggregation",
    "Hardware Review Audit",
  ],
  authors: [{ name: "OpinionLens", url: SITE_URL }],
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
    title: "OpinionLens — Explainable & Safe RAG for Opinion Summarization",
    description:
      "Summaries of product review themes, safety mentions, and differing opinions, with links to the source comments.",
    images: [
      {
        url: "/og-image.webp",
        width: 1200,
        height: 630,
        alt: "OpinionLens Stitch Mocha Glassmorphism UI",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "OpinionLens — Explainable & Safe RAG for Opinion Summarization",
    description:
      "Explainable and safe RAG framework for opinion summarization featuring Critical-Minority Safety Guard, Attributed Consensus, Polarization Spectra, and Live Evidence Inspector.",
    images: ["/og-image.webp"],
    creator: "@opinionlens",
  },
  icons: {
    icon: "/logo.webp",
    apple: "/logo.webp",
  },
  verification: GSC_TOKEN ? { google: GSC_TOKEN } : undefined,
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
        description: "Product review summaries with links to the source comments.",
        sameAs: ["https://github.com/Xsayushn/edai_FY"],
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
    <html lang="en" className="dark">
      <head>
        {/* Preconnect & Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />

        {/* Organization Schema (Requirement 14) */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
        />

        {/* Google Analytics (Requirement 17) */}
        {GA_ID && (
          <>
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
                  function gtag(){window.dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${GA_ID}', { page_path: window.location.pathname });
                `,
              }}
            />
          </>
        )}
      </head>
      <body className="bg-[#08090d] text-[#F9EAD7] font-sans antialiased min-h-screen relative overflow-x-hidden selection:bg-[#BFE23A] selection:text-black">
        {children}

        {/* Sleek Dark Internal Links Footer (Requirement 16) */}
        <footer className="relative z-20 border-t border-white/10 bg-[#08090d]/90 backdrop-blur-xl py-8 mt-16 text-xs text-[#9E9485]">
          <div className="max-w-[1536px] mx-auto px-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="font-display font-bold text-sm text-[#F9EAD7]">OpinionLens</span>
              <span className="text-[#8E8880]">·</span>
              <span>Product review summaries with source comments</span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="/privacy" className="hover:text-[#BFE23A] transition-colors">Privacy Policy</Link>
              <Link href="/contact" className="hover:text-[#BFE23A] transition-colors">Contact</Link>
              <Link href="/#product-id" className="hover:text-[#BFE23A] transition-colors">Find a product</Link>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
