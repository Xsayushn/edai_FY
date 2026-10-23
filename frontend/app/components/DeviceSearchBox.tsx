"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const POPULAR_DEVICES = [
  { id: "B000063W3B", name: "Toshiba Satellite 5105", category: "💻 Laptop" },
  { id: "SONY_WH1000XM4", name: "Sony WH-1000XM4", category: "🎧 Headphones" },
  { id: "PS5_CONSOLE", name: "Sony PlayStation 5", category: "🎮 Console" },
  { id: "APPLE_WATCH_S8", name: "Apple Watch Series 8", category: "⌚ Watch" },
  { id: "MOBEZF53HHFV6S8R", name: "Samsung Galaxy J7", category: "📱 Smartphone" },
  { id: "B00004Z5M1", name: "KDS Valiant Notebook", category: "💻 Laptop" },
  { id: "B00000J052", name: "Kingston 64MB RAM", category: "💾 Component" },
];

interface DeviceSearchBoxProps {
  currentProductId?: string;
  placeholder?: string;
}

export default function DeviceSearchBox({ currentProductId, placeholder }: DeviceSearchBoxProps) {
  const [productId, setProductId] = useState(currentProductId || "");
  const [aspectQuery, setAspectQuery] = useState("");
  const router = useRouter();

  const handleAudit = (targetId: string) => {
    const cleanId = (targetId || productId).trim();
    if (!cleanId) return;
    const url = aspectQuery.trim()
      ? `/audit/${encodeURIComponent(cleanId)}?q=${encodeURIComponent(aspectQuery.trim())}`
      : `/audit/${encodeURIComponent(cleanId)}`;
    router.push(url);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAudit(productId);
  };

  return (
    <div
      className="glass-panel"
      style={{
        width: "100%",
        maxWidth: "860px",
        margin: "0 auto 36px",
        padding: "24px 28px",
        border: "1px solid var(--border-glass)",
        boxShadow: "0 12px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 var(--border-specular)",
      }}
    >
      <form onSubmit={handleSubmit}>
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1.2fr auto", gap: "12px", alignItems: "center" }}>
          <div>
            <label htmlFor="device-id-input" className="sr-only">
              Device Identifier or ASIN
            </label>
            <input
              id="device-id-input"
              type="text"
              className="form-input"
              placeholder={placeholder || "Enter Device ID / ASIN (e.g. SONY_WH1000XM4)"}
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              style={{ fontSize: "0.95rem" }}
            />
          </div>

          <div>
            <label htmlFor="aspect-query-input" className="sr-only">
              Optional Aspect Focus
            </label>
            <input
              id="aspect-query-input"
              type="text"
              className="form-input"
              placeholder="Ask aspect: e.g. battery heating, mic, display"
              value={aspectQuery}
              onChange={(e) => setAspectQuery(e.target.value)}
              style={{ fontSize: "0.95rem" }}
            />
          </div>

          <button type="submit" className="btn btn-lime" style={{ whiteSpace: "nowrap", padding: "12px 24px" }}>
            Audit Device →
          </button>
        </div>
      </form>

      {/* Quick 1-Click Device Presets */}
      <div style={{ marginTop: "18px", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
            1-Click Devices:
          </span>
          {POPULAR_DEVICES.map((dev) => (
            <button
              key={dev.id}
              type="button"
              onClick={() => {
                setProductId(dev.id);
                handleAudit(dev.id);
              }}
              className="badge badge-neutral"
              style={{
                cursor: "pointer",
                transition: "all 0.15s ease",
                background: currentProductId === dev.id ? "var(--neon-lime-subtle)" : undefined,
                borderColor: currentProductId === dev.id ? "var(--neon-lime-border)" : undefined,
                color: currentProductId === dev.id ? "var(--neon-lime)" : undefined,
              }}
            >
              <span>{dev.category}</span>
              <span>{dev.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
