import React from 'react';

interface SafetyGuardCardProps {
  hasSafetyWarning: boolean;
  warningData?: {
    title: string;
    thresholdText: string;
    riskLevel: string;
    detectedReviews: string[];
    taxonomy: string;
    verbatimQuote: string;
    ruleText: string;
  };
  onSelectReview: (id: string) => void;
}

export const SafetyGuardCard: React.FC<SafetyGuardCardProps> = ({
  hasSafetyWarning,
  warningData,
  onSelectReview,
}) => {
  if (!hasSafetyWarning || !warningData) {
    return (
      <article
        id="safety"
        className="frosted-glass-panel rounded-2xl p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-1 border border-lime-500/30"
      >
        <div className="flex items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-[#BFE23A]/20 border border-[#BFE23A]/50 flex items-center justify-center text-[#BFE23A] shadow-[0_0_20px_rgba(191,226,58,0.3)]">
              <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                verified_user
              </span>
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-white tracking-tight">
                Safety Guard: Normal Operating Parameters
              </h2>
              <p className="text-xs text-[#F9EAD7]/80 mt-0.5">
                Zero critical safety anomalies detected across verified corpus • Hazard threshold &lt; 0.20
              </p>
            </div>
          </div>
          <span className="px-3.5 py-1.5 rounded-full text-xs font-mono font-bold bg-[#BFE23A]/20 text-[#DCFF4E] border border-[#BFE23A]/40 flex items-center gap-1.5 shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-[#BFE23A] animate-pulse" />
            SAFE CORPUS
          </span>
        </div>
      </article>
    );
  }

  const primaryReviewId = warningData.detectedReviews[1] || warningData.detectedReviews[0] || '15';

  return (
    <article
      id="safety"
      className="frosted-crimson-glass rounded-2xl p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-1"
    >
      {/* Background Radiant Flare inside the card */}
      <div className="absolute -right-16 -top-16 w-52 h-52 rounded-full bg-[#E10600]/35 blur-3xl pointer-events-none animate-pulse" />

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className="pulse-danger w-11 h-11 rounded-xl bg-[#E10600]/40 border border-[#FF332C] flex items-center justify-center text-white">
            <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              warning
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-display text-lg font-bold text-white tracking-tight flex items-center gap-1.5 drop-shadow-[0_2px_8px_rgba(225,6,0,0.5)]">
                {warningData.title}
              </h2>
            </div>
            <p className="text-xs text-[#F9EAD7]/85 mt-0.5">
              {warningData.thresholdText}
            </p>
          </div>
        </div>
        <span className="pulse-danger px-3.5 py-1.5 rounded-full text-xs font-mono font-bold bg-gradient-to-r from-[#E10600] to-[#FF332C] text-white border border-white/40 flex items-center gap-1.5 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
          {warningData.riskLevel}
        </span>
      </div>

      {/* Detected corpus stats & Verbatim Quote (Nested Frosted Dark Glass Well) */}
      <div className="rounded-xl frosted-glass-well p-4 mb-4 relative z-10 border-[#E10600]/35">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-[#F9EAD7]/95 mb-2.5 pb-2 border-b border-[#E10600]/25">
          <span className="flex items-center gap-1.5 text-[#FF332C] font-medium">
            <span className="material-symbols-outlined text-base">emergency_heat</span>
            Detected in {warningData.detectedReviews.length} distinct reviews (
            {warningData.detectedReviews.map((id, idx) => (
              <React.Fragment key={id}>
                {idx > 0 && ', '}
                <button
                  type="button"
                  onClick={() => onSelectReview(id)}
                  className={`underline hover:text-white transition-colors duration-200 cursor-pointer ${
                    id === primaryReviewId ? 'font-bold' : ''
                  }`}
                >
                  #{id}
                </button>
              </React.Fragment>
            ))}
            )
          </span>
          <span className="font-mono text-[#F9EAD7]/75">
            Taxonomy: <strong className="text-[#F9EAD7] underline decoration-[#E10600] font-semibold">{warningData.taxonomy}</strong>
          </span>
        </div>

        {/* Verbatim high-risk snippet with glowing frosted crimson highlight */}
        <div className="p-3.5 rounded-lg bg-[#E10600]/25 border-l-4 border-[#E10600] text-[#FFF6ED] font-mono text-xs leading-relaxed shadow-[inset_0_1px_2px_rgba(255,255,255,0.2)]">
          <span className="text-[#FF332C] font-bold uppercase tracking-wider block mb-1">
            Verbatim Corpus Evidence:
          </span>
          <p className="italic text-white">
            {warningData.verbatimQuote}
          </p>
        </div>
      </div>

      {/* Action bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs relative z-10">
        <span className="text-[#F9EAD7]/75 font-mono">
          {warningData.ruleText}
        </span>
        <button
          type="button"
          onClick={() => onSelectReview(primaryReviewId)}
          className="btn-shine-effect px-4 py-2 rounded-xl bg-gradient-to-r from-[#E10600] to-[#FF332C] text-white font-semibold flex items-center gap-1.5 border border-white/40 hover:brightness-110 shadow-[0_4px_22px_rgba(225,6,0,0.6),inset_0_1px_1px_rgba(255,255,255,0.5)] transition-all duration-300 active:scale-95 hover:scale-105 cursor-pointer"
        >
          <span className="material-symbols-outlined text-base">visibility</span>
          Inspect Review #{primaryReviewId} In Evidence Panel
        </button>
      </div>
    </article>
  );
};
