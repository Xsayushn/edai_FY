import React from 'react';
import Link from 'next/link';

interface HeaderProps {
  onOpenAuditModal: () => void;
  auditScore: number;
}

export const Header: React.FC<HeaderProps> = ({ onOpenAuditModal, auditScore }) => {
  return (
    <header className="frosted-glass-panel sticky top-0 z-50 w-full border-b border-white/15 px-4 md:px-8 py-3.5 backdrop-blur-2xl">
      <div className="max-w-[1536px] mx-auto flex items-center justify-between gap-4">
        {/* Brand & Explanatory Tag */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-white/20 via-white/5 to-[#BFE23A]/30 border border-white/40 flex items-center justify-center shadow-[0_0_20px_rgba(191,226,58,0.35),inset_0_1px_1px_rgba(255,255,255,0.6)] transition-transform duration-300 hover:rotate-6 hover:scale-105">
            <span
              className="material-symbols-outlined text-[#BFE23A] text-2xl"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              insights
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-xl tracking-tight text-white drop-shadow-[0_2px_10px_rgba(255,255,255,0.25)]">
                OpinionLens
              </span>
              <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full bg-[#F9EAD7]/15 text-[#FFF6ED] border border-[#F9EAD7]/30 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3)]">
                v2.4
              </span>
            </div>
            <span className="text-xs font-medium text-[#F9EAD7]/75 block">
              Explainable &amp; Safe RAG for Opinion Summarization
            </span>
          </div>
        </div>

        {/* Center Navigation Glass Segmented Pills */}
        <nav aria-label="Main Navigation" className="hidden lg:flex items-center gap-1.5 p-1 rounded-full glass-pill-surface">
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-semibold bg-[#F9EAD7]/20 text-white border border-[#F9EAD7]/40 shadow-[0_2px_14px_rgba(249,234,215,0.25),inset_0_1px_1px_rgba(255,255,255,0.5)] flex items-center gap-1.5 transition-all duration-300 hover:scale-105"
            href="/#consensus"
          >
            <span className="material-symbols-outlined text-sm text-[#BFE23A]">check_circle</span>
            Consensus Matrix
          </Link>
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="/#divergence"
          >
            <span className="material-symbols-outlined text-sm">tune</span>
            Divergence Spectra
          </Link>
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="/#audit"
          >
            <span className="material-symbols-outlined text-sm">verified</span>
            Audit Provenance
          </Link>
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#FF332C] hover:bg-[#E10600]/20 transition-all duration-300 hover:scale-105 flex items-center gap-1.5 border border-[#E10600]/40 bg-[#E10600]/10 shadow-[0_0_12px_rgba(225,6,0,0.25)]"
            href="/#safety"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#E10600] animate-ping" />
            Safety Guard
          </Link>
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="/contact"
          >
            <span className="material-symbols-outlined text-sm text-[#BFE23A]">contact_support</span>
            Contact Ops
          </Link>
          <Link
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="/privacy"
          >
            <span className="material-symbols-outlined text-sm">policy</span>
            Privacy
          </Link>
        </nav>

        {/* Trailing Action Badges & Repo Audit Button */}
        <div className="flex items-center gap-2.5">
          {/* GitHub Repo Push Status Button */}
          <button
            onClick={onOpenAuditModal}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-pill-surface border border-[#BFE23A]/50 bg-[#BFE23A]/15 hover:bg-[#BFE23A]/25 text-xs font-mono text-white transition-all shadow-[0_0_14px_rgba(191,226,58,0.3)] active:scale-95 hover:scale-105 cursor-pointer"
            title="edai_FY changes successfully committed and pushed to GitHub main"
          >
            <span className="w-2 h-2 rounded-full bg-[#BFE23A] animate-pulse" />
            <span className="hidden sm:inline font-semibold text-[#DCFF4E]">edai_FY:</span>
            <span className="font-bold text-[#DCFF4E]">Pushed (55ddaab)</span>
          </button>

          {/* ChromaDB + Groq Online Status Glass Capsule */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full glass-pill-surface border border-[#BFE23A]/40 text-xs font-mono text-[#F9EAD7] shadow-[0_0_15px_rgba(191,226,58,0.2)]">
            <span className="w-2 h-2 rounded-full bg-[#BFE23A] shadow-[0_0_12px_#BFE23A] animate-pulse" />
            <span>ChromaDB + Groq Online</span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              className="w-9 h-9 rounded-xl glass-pill-surface flex items-center justify-center text-[#F9EAD7]/80 hover:text-white hover:border-white/40 transition-all duration-200 active:scale-95 hover:scale-105"
              title="Pipeline Configuration"
              aria-label="Pipeline Configuration"
            >
              <span className="material-symbols-outlined text-lg">tune</span>
            </button>
            <button
              className="w-9 h-9 rounded-xl glass-pill-surface flex items-center justify-center text-[#F9EAD7]/80 hover:text-white hover:border-white/40 transition-all duration-200 active:scale-95 hover:scale-105"
              title="Vector DB Cache & Index"
              aria-label="Vector DB Cache & Index"
            >
              <span className="material-symbols-outlined text-lg">database</span>
            </button>
          </div>

          {/* User Profile Avatar Pill */}
          <div
            className="w-9 h-9 rounded-xl glass-pill-surface flex items-center justify-center text-xs font-mono font-bold text-[#BFE23A] border border-[#BFE23A]/40 shadow-[0_0_14px_rgba(191,226,58,0.3)] transition-all duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(191,226,58,0.5)] cursor-pointer"
            title="Auditor Profile: Ayush"
          >
            AL
          </div>
        </div>
      </div>
    </header>
  );
};
