import type { Metadata } from "next";
import OpinionLensApp from "./components/OpinionLensApp";

export const metadata: Metadata = {
  title: "OpinionLens — Explainable & Safe RAG for Opinion Summarization",
  description:
    "Explainable and safe RAG framework for opinion summarization featuring Critical-Minority Safety Guard, Attributed Consensus, Polarization Spectra, and Live Evidence Inspector.",
  alternates: {
    canonical: "https://opinionlens.ai",
  },
  openGraph: {
    title: "OpinionLens — Explainable & Safe RAG for Opinion Summarization",
    description:
      "Explainable and safe RAG framework for opinion summarization featuring Critical-Minority Safety Guard, Attributed Consensus, Polarization Spectra, and Live Evidence Inspector.",
    url: "https://opinionlens.ai",
    images: [
      {
        url: "/og-image.webp",
        width: 1200,
        height: 630,
        alt: "OpinionLens Stitch Mocha Glassmorphism UI",
      },
    ],
  },
};

export default function HomePage() {
  return (
    <>
      {/* Exactly one H1 per page for SEO (Requirement 6) */}
      <h1 className="sr-only">OpinionLens — Explainable &amp; Safe RAG for Opinion Summarization</h1>
      <OpinionLensApp />
    </>
  );
}
