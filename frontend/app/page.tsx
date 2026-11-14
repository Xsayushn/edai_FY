import type { Metadata } from "next";
import Link from "next/link";
import ProductAuditSearch from "./components/ProductAuditSearch";
import { fetchCatalogBrands, fetchCatalogProducts } from "./lib/api";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Product review summaries | OpinionLens",
  description:
    "Explore common themes, safety mentions, and differing opinions in product reviews, with links back to the source text.",
  alternates: {
    canonical: "https://opinionlens.ai",
  },
  openGraph: {
    title: "Product review summaries | OpinionLens",
    description:
      "Explore common themes, safety mentions, and differing opinions in product reviews, with links back to the source text.",
    url: "https://opinionlens.ai",
    images: [
      {
        url: "/og-image.webp",
        width: 1200,
        height: 630,
        alt: "OpinionLens product review summaries",
      },
    ],
  },
};

export default async function HomePage() {
  const brands = await fetchCatalogBrands();
  const initialBrand = [...brands].sort((a, b) => b.product_count - a.product_count)[0]?.brand || "";
  const products = initialBrand ? (await fetchCatalogProducts(initialBrand)).slice(0, 12) : [];

  return (
    <main className={styles.home}>
      <div className={styles.shell}>
        <header className={styles.header}>
          <Link href="/" className={styles.brand} aria-label="OpinionLens home">
            <span className={styles.brandMark} aria-hidden="true">O</span>
            <span>OpinionLens</span>
          </Link>
          <nav className={styles.navigation} aria-label="Main navigation">
            <a href="#how-it-works">How it works</a>
            <Link href="/privacy">Privacy</Link>
            <Link href="/contact">Contact</Link>
          </nav>
        </header>

        <section className={styles.hero} aria-labelledby="home-title">
          <p className={styles.eyebrow}>PRODUCT REVIEW RESEARCH</p>
          <h1 id="home-title">Get a clearer picture before you buy.</h1>
          <p className={styles.intro}>
            Find the themes that come up in product reviews, see where people disagree, and read the comments behind each finding.
          </p>
          <ProductAuditSearch brands={brands} products={products} initialBrand={initialBrand} />
        </section>

        <section className={styles.howItWorks} id="how-it-works" aria-labelledby="how-title">
          <div className={styles.sectionHeading}>
            <div>
              <p className={styles.eyebrow}>A useful summary, with the source close by</p>
              <h2 id="how-title">From reviews to a more informed choice</h2>
            </div>
            <p className={styles.sectionIntro}>
              OpinionLens organizes review feedback. It does not replace your judgment or guarantee a product is safe.
            </p>
          </div>

          <div className={styles.featureGrid}>
            <article className={styles.feature}>
              <span className={styles.featureNumber}>01</span>
              <h3>Recurring themes</h3>
              <p>See what reviewers often praise or criticize, with links to the comments used in the summary.</p>
            </article>
            <article className={styles.feature}>
              <span className={styles.featureNumber}>02</span>
              <h3>Different experiences</h3>
              <p>Find aspects where positive and negative opinions both appear in the reviews.</p>
            </article>
            <article className={styles.feature}>
              <span className={styles.featureNumber}>03</span>
              <h3>Safety mentions</h3>
              <p>Review comments that mention potential risks, so you can read the original wording in context.</p>
            </article>
          </div>
        </section>

        <footer className={styles.footer}>
          <span>OpinionLens · Product review summaries</span>
          <a href="https://github.com/Xsayushn/edai_FY" target="_blank" rel="noreferrer">
            View project source
          </a>
        </footer>
      </div>
    </main>
  );
}
