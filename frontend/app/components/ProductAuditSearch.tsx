"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import type { BrandCatalogItem, ProductCatalogItem } from "../lib/api";
import styles from "../page.module.css";

interface ProductAuditSearchProps {
  brands: BrandCatalogItem[];
  products: ProductCatalogItem[];
  initialProductId?: string;
  initialQuestion?: string;
  initialBrand?: string;
}

export default function ProductAuditSearch({
  products,
  brands,
  initialProductId = "",
  initialQuestion = "",
  initialBrand = "",
}: ProductAuditSearchProps) {
  const [productId, setProductId] = useState(initialProductId);
  const [question, setQuestion] = useState(initialQuestion);
  const [brand, setBrand] = useState(initialBrand);
  const [catalogProducts, setCatalogProducts] = useState(products);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [isOpeningAudit, setIsOpeningAudit] = useState(false);
  const [catalogError, setCatalogError] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const openAudit = (id: string) => {
    const cleanId = id.trim();
    if (!cleanId) {
      setError("Enter a product ID to continue.");
      return;
    }

    const query = question.trim();
    const url = query
      ? `/audit/${encodeURIComponent(cleanId)}?q=${encodeURIComponent(query)}`
      : `/audit/${encodeURIComponent(cleanId)}`;
    setIsOpeningAudit(true);
    router.push(url);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    openAudit(productId);
  };

  const handleBrandChange = async (nextBrand: string) => {
    setBrand(nextBrand);
    setProductId("");
    setCatalogError("");
    setCatalogProducts([]);
    setIsLoadingProducts(true);

    try {
      const response = await fetch(`/api/catalog?brand=${encodeURIComponent(nextBrand)}`);
      const data = await response.json();
      if (!response.ok || !Array.isArray(data.products)) {
        throw new Error(data.detail || "Could not load products.");
      }
      setCatalogProducts(data.products.slice(0, 12));
    } catch {
      setCatalogError("Could not load this category. You can still enter a product ID.");
    } finally {
      setIsLoadingProducts(false);
    }
  };

  return (
    <div className={styles.searchPanel}>
      <form onSubmit={handleSubmit}>
        <div className={`${styles.searchFields} ${brands.length > 0 ? styles.withCategory : ""}`}>
          {brands.length > 0 && (
            <div className={styles.field}>
              <label htmlFor="product-brand">Category</label>
              <select
                id="product-brand"
                value={brand}
                onChange={(event) => void handleBrandChange(event.target.value)}
                disabled={isLoadingProducts}
              >
                {brands.map((item) => (
                  <option key={item.brand} value={item.brand}>
                    {item.brand} ({item.product_count})
                  </option>
                ))}
              </select>
              <span className={styles.help}>
                {isLoadingProducts ? "Loading products…" : catalogError || "Choose a category to browse its products"}
              </span>
            </div>
          )}
          <div className={styles.field}>
            <label htmlFor="product-id">Product</label>
            <input
              id="product-id"
              name="productId"
              type="text"
              list={catalogProducts.length > 0 ? "product-options" : undefined}
              autoComplete="off"
              value={productId}
              onChange={(event) => {
                setProductId(event.target.value);
                setError("");
              }}
              placeholder="Choose a product or enter its ID"
              aria-describedby={error ? "product-error" : "product-help"}
            />
            {catalogProducts.length > 0 && (
              <datalist id="product-options">
                {catalogProducts.map((product) => (
                  <option
                    key={product.product_id}
                    value={product.product_id}
                    label={`${product.product_name} · ${product.brand}`}
                  />
                ))}
              </datalist>
            )}
            {error ? (
              <span className={styles.error} id="product-error" role="alert">{error}</span>
            ) : (
              <span className={styles.help} id="product-help">
                {catalogProducts.length > 0 ? `${catalogProducts.length} products shown · choose a suggestion or enter an ID` : "Enter a product ID from the review catalog"}
              </span>
            )}
          </div>

          <div className={styles.field}>
            <label htmlFor="review-question">What do you want to know? <span>(optional)</span></label>
            <input
              id="review-question"
              name="question"
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Battery life, camera, comfort…"
            />
            <span className={styles.help}>Leave blank to see an overall summary.</span>
          </div>

          <button className={styles.submit} type="submit" disabled={isOpeningAudit}>
            {isOpeningAudit ? "Opening summary…" : "View summary"}
            {!isOpeningAudit && <span aria-hidden="true">→</span>}
          </button>
        </div>
      </form>

      {catalogProducts.length > 0 && (
        <div className={styles.productExamples}>
          <span className={styles.exampleLabel}>Available products</span>
          {catalogProducts.slice(0, 4).map((product) => (
            <button
              className={styles.productExample}
              key={product.product_id}
              type="button"
              onClick={() => {
                setProductId(product.product_id);
                openAudit(product.product_id);
              }}
              title={`Open ${product.product_name}`}
            >
              {product.product_name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
