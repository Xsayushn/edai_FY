import React from 'react';
import { ContestedAspect } from '../types/opinionLens';

interface PolarizationCardProps {
  aspect: ContestedAspect;
  onSelectReview: (id: string) => void;
}

export const PolarizationCard: React.FC<PolarizationCardProps> = ({
  aspect,
  onSelectReview,
}) => {
  return (
    <article className="frosted-glass-panel rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1" id="divergence">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-white/15 mb-5 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#F9EAD7]/15 border border-[#F9EAD7]/30 flex items-center justify-center text-[#F9EAD7] shadow-[0_0_16px_rgba(249,234,215,0.2),inset_0_1px_1px_rgba(255,255,255,0.4)] transition-transform duration-300 hover:scale-110">
            <span className="material-symbols-outlined text-2xl">balance</span>
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-white tracking-tight drop-shadow-[0_2px_8px_rgba(255,255,255,0.2)]">
              Contested Viewpoints &amp; Polarization Spectra
            </h2>
            <p className="text-xs text-[#F9EAD7]/75">
              Aspect clustering detecting polarized sentiment divergence ratios (N ≥ 4, Ratio ≥ 0.40)
            </p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold glass-pill-surface text-[#F9EAD7] flex items-center gap-1.5 border border-[#F9EAD7]/40 shadow-[0_0_14px_rgba(249,234,215,0.15)]">
          <span className="w-2 h-2 rounded-full bg-[#F9EAD7] shadow-[0_0_8px_#F9EAD7]" />
          Status: 1 CONTESTED ASPECT
        </span>
      </div>

      {/* Contested Aspect Widget */}
      <div className="space-y-4 relative z-10">
        <div>
          <div className="flex justify-between items-center text-xs font-mono mb-2">
            <div className="flex items-center gap-2">
              <span className="font-sans font-bold text-sm text-white">{aspect.title}</span>
              <span className="px-2.5 py-0.5 rounded-full glass-pill-surface border border-[#F9EAD7]/30 text-[#F9EAD7] text-[11px] transition-all duration-300 hover:border-[#F9EAD7]/60">
                Contention Ratio: {aspect.contentionRatio}
              </span>
            </div>
            <span className="text-[#F9EAD7]/65">{aspect.totalTuples} Extracted Aspect Tuples</span>
          </div>

          {/* Dual-Rail Frosted Divergence Progress Bar */}
          <div className="h-7 w-full rounded-full frosted-glass-well p-1 flex items-center relative overflow-hidden border border-white/20 shadow-inner group cursor-default">
            {/* Positive Segment (Lime Green Glass) */}
            <div
              className="polarization-bar-fill h-full rounded-l-full bg-gradient-to-r from-[#8EA925] to-[#BFE23A] flex items-center px-3.5 justify-start text-[11px] font-bold font-mono text-black shadow-[0_0_16px_rgba(191,226,58,0.5)] transition-all duration-500 group-hover:brightness-110"
              style={{ width: `${aspect.positivePct}%` }}
            >
              {aspect.positivePct}% Positive ({aspect.positiveCount})
            </div>

            {/* Negative Segment (Frosted Peach Glass) */}
            <div
              className="polarization-bar-fill h-full rounded-r-full bg-gradient-to-r from-[#F9EAD7]/15 to-[#F9EAD7]/30 flex items-center px-3.5 justify-end text-[11px] font-bold font-mono text-[#FFF6ED] transition-all duration-500 group-hover:brightness-110"
              style={{ width: `${aspect.negativePct}%` }}
            >
              {aspect.negativePct}% Negative ({aspect.negativeCount})
            </div>

            {/* Center Divider Specular Pin */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_12px_#ffffff] transition-all duration-500 pointer-events-none"
              style={{ left: `${aspect.positivePct}%` }}
            />
          </div>
        </div>

        {/* Pro vs Con Perspective Glass Wells */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* Pro Argument */}
          <div className="p-4 rounded-xl frosted-glass-well border-[#BFE23A]/35 relative flex flex-col justify-between shadow-[0_0_20px_rgba(191,226,58,0.1)] transition-all duration-300 hover:border-[#BFE23A]/60 hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-[#BFE23A] flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">thumb_up</span> Supporting Perspective ({aspect.supporting.count} reviews)
                </span>
                <span className="text-[11px] font-mono text-[#F9EAD7]/60">Conf: {aspect.supporting.conf}</span>
              </div>
              <p className="text-xs text-[#FFF6ED] italic leading-relaxed">
                {aspect.supporting.quote}
              </p>
            </div>
            <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-xs font-mono">
              <span className="text-[#F9EAD7]/65">Corpus citations:</span>
              <div className="flex gap-1.5">
                {aspect.supporting.citations.map((id) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => onSelectReview(id)}
                    className="px-2 py-0.5 rounded glass-chip-lime-glow text-xs cursor-pointer"
                  >
                    #{id}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Con Argument */}
          <div className="p-4 rounded-xl frosted-glass-well border-[#F9EAD7]/30 relative flex flex-col justify-between transition-all duration-300 hover:border-[#F9EAD7]/60 hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-[#F9EAD7] flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">thumb_down</span> Opposing Perspective ({aspect.opposing.count} reviews)
                </span>
                <span className="text-[11px] font-mono text-[#F9EAD7]/60">Conf: {aspect.opposing.conf}</span>
              </div>
              <p className="text-xs text-[#FFF6ED] italic leading-relaxed">
                {aspect.opposing.quote}
              </p>
            </div>
            <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-xs font-mono">
              <span className="text-[#F9EAD7]/65">Corpus citations:</span>
              <div className="flex gap-1.5">
                {aspect.opposing.citations.map((id) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => onSelectReview(id)}
                    className="px-2 py-0.5 rounded glass-pill-surface text-[#F9EAD7] text-xs hover:border-[#F9EAD7]/50 cursor-pointer"
                  >
                    #{id}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
};
