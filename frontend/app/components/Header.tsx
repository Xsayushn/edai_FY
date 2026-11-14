import React from 'react';

export const Header: React.FC = () => {
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
          <a
            className="px-4 py-1.5 rounded-full text-xs font-semibold bg-[#F9EAD7]/20 text-white border border-[#F9EAD7]/40 shadow-[0_2px_14px_rgba(249,234,215,0.25),inset_0_1px_1px_rgba(255,255,255,0.5)] flex items-center gap-1.5 transition-all duration-300 hover:scale-105"
            href="#consensus"
          >
            <span className="material-symbols-outlined text-sm text-[#BFE23A]">check_circle</span>
            Consensus Matrix
          </a>
          <a
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="#divergence"
          >
            <span className="material-symbols-outlined text-sm">tune</span>
            Divergence Spectra
          </a>
          <a
            className="px-4 py-1.5 rounded-full text-xs font-medium text-[#F9EAD7]/80 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105 flex items-center gap-1.5"
            href="#audit"
          >
            <span className="material-symbols-outlined text-sm">verified</span>
            Audit Provenance
          </a>
          <a
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#FF332C] hover:bg-[#E10600]/20 transition-all duration-300 hover:scale-105 flex items-center gap-1.5 border border-[#E10600]/40 bg-[#E10600]/10 shadow-[0_0_12px_rgba(225,6,0,0.25)]"
            href="#safety"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#E10600] animate-ping" />
            Safety Guard
          </a>
        </nav>

        {/* Sample dashboard status and source link */}
        <div className="flex items-center gap-2.5">
          <span
            className="px-3 py-1.5 rounded-full glass-pill-surface border border-white/20 text-xs font-mono text-[#F9EAD7]/80"
          >
            Sample dashboard
          </span>
          <a
            href="https://github.com/Xsayushn/edai_FY"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full glass-pill-surface text-xs font-semibold text-[#F9EAD7]/90 hover:text-white hover:border-white/40 transition-all"
          >
            <span className="material-symbols-outlined text-sm">open_in_new</span>
            Source
          </a>

        </div>
      </div>
    </header>
  );
};
