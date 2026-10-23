import type { MetadataRoute } from "next";

const DEFAULT_PRODUCT_IDS = [
  "B000063W3B",
  "B00004Z5M1",
  "B00000J052",
  "B00004ZCJE",
  "B00005LENO",
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://opinionlens.ai";
  const now = new Date();

  // Base routes
  const routes: MetadataRoute.Sitemap = [
    {
      url: `${siteUrl}/`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 1.0,
    },
    {
      url: `${siteUrl}/contact`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${siteUrl}/privacy`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];

  // Dynamically add product audit routes
  let productIds = [...DEFAULT_PRODUCT_IDS];

  try {
    const res = await fetch("http://127.0.0.1:8000/api/products", {
      next: { revalidate: 3600 },
      headers: { "Content-Type": "application/json" },
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.products) && data.products.length > 0) {
        const ids = data.products.map((p: { product_id: string }) => p.product_id);
        productIds = Array.from(new Set([...productIds, ...ids]));
      }
    }
  } catch {
    // Graceful fallback to static product list
  }

  const productRoutes: MetadataRoute.Sitemap = productIds.map((id) => ({
    url: `${siteUrl}/audit/${id}`,
    lastModified: now,
    changeFrequency: "daily",
    priority: 0.9,
  }));

  return [...routes, ...productRoutes];
}
