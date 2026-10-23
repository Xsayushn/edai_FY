import React from 'react';
import { ConsensusBullet } from '../types/opinionLens';

interface ConsensusCardProps {
  groundednessScore: string;
  totalReviews: number;
  bullets: ConsensusBullet[];
  onSelectReview: (id: string) => void;
}

export const ConsensusCard: React.FC<ConsensusCardProps> = ({
  groundednessScore,
  totalReviews,
  bullets,
  onSelectReview,
}) => {
  return (
    <article className="frosted-glass-panel rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1" id="consensus">
      <div className="flex items-center justify-between pb-4 border-b border-white/15 mb-5 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#BFE23A]/20 border border-[#BFE23A]/45 flex items-center justify-center text-[#BFE23A] shadow-[0_0_20px_rgba(191,226,58,0.3),inset_0_1px_1px_rgba(255,255,255,0.4)] transition-transform duration-300 hover:scale-110">
            <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              check_circle
            </span>
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-white tracking-tight drop-shadow-[0_2px_8px_rgba(255,255,255,0.2)]">
              Attributed Consensus Summary
            </h2>
            <p className="text-xs text-[#F9EAD7]/75">
              Grounded narrative synthesis extracted from {totalReviews} verified reviews with direct citation anchors
            </p>
          </div>
        </div>

        {/* Groundedness Metric */}
        <div className="text-right">
          <span className="text-[11px] font-mono text-[#F9EAD7]/70 block uppercase tracking-wider">
            Groundedness Score
          </span>
          <div className="flex items-center justify-end gap-1">
            <span className="font-display text-2xl font-bold text-[#BFE23A] aura-lime">
              {groundednessScore}
            </span>
            <span className="text-xs font-semibold text-[#BFE23A]">Cited</span>
          </div>
        </div>
      </div>

      {/* Structured Bullet Findings with Frosted Glass Citations */}
      <div className="space-y-3.5 relative z-10">
        {bullets.map((bullet) => {
          const isRiskBullet = bullet.isRisk;
          const firstReviewId = bullet.citations[0]?.reviewId || '12';

          return (
            <div
              key={bullet.id}
              className={`group p-4 rounded-xl frosted-glass-well transition-all flex items-start gap-3 ${
                isRiskBullet
                  ? 'border-[#E10600]/30 hover:border-[#E10600]/60 shadow-[0_0_20px_rgba(225,6,0,0.15)]'
                  : 'hover:border-[#BFE23A]/40'
              }`}
            >
              <span
                className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 transition-transform duration-300 group-hover:scale-125 ${
                  isRiskBullet
                    ? 'bg-[#E10600] shadow-[0_0_12px_#E10600]'
                    : 'bg-[#BFE23A] shadow-[0_0_12px_#BFE23A]'
                }`}
              />
              <div className="flex-1">
                <p className="text-sm text-[#FFF6ED] leading-relaxed">
                  {bullet.text}
                </p>
                <div className="mt-2.5 flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono text-[#F9EAD7]/60">Verified Citations:</span>
                  {bullet.citations.map((c) => (
                    <button
                      key={c.reviewId}
                      type="button"
                      onClick={() => onSelectReview(c.reviewId)}
                      className={`${
                        c.isRisk ? 'glass-chip-crimson-glow font-bold' : 'glass-chip-lime-glow font-medium'
                      } px-2.5 py-0.5 rounded-lg text-xs font-mono flex items-center gap-1 active:scale-95 transition-all cursor-pointer`}
                    >
                      <span className="material-symbols-outlined text-xs">
                        {c.isRisk ? 'emergency_heat' : 'link'}
                      </span>
                      Review #{c.reviewId} {c.isRisk && '(Risk)'}
                    </button>
                  ))}
                </div>
              </div>
              <button
                type="button"
                onClick={() => onSelectReview(firstReviewId)}
                className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-lg glass-pill-surface transition-all duration-200 hover:scale-110 cursor-pointer ${
                  isRiskBullet ? 'text-[#FF332C] hover:border-[#FF332C]' : 'text-[#BFE23A] hover:border-[#BFE23A]'
                }`}
                title="Inspect Citations In Evidence Panel"
                aria-label={`Inspect Review #${firstReviewId} in Evidence Panel`}
              >
                <span className="material-symbols-outlined text-lg">travel_explore</span>
              </button>
            </div>
          );
        })}
      </div>
    </article>
  );
};
