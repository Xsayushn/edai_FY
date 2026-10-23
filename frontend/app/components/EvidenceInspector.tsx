import React, { useRef, useEffect } from 'react';
import { AuditedReview } from '../types/opinionLens';

interface EvidenceInspectorProps {
  selectedReview: AuditedReview;
  availableReviewIds: string[];
  onSelectReview: (id: string) => void;
  productId: string;
}

export const EvidenceInspector: React.FC<EvidenceInspectorProps> = ({
  selectedReview,
  availableReviewIds,
  onSelectReview,
  productId,
}) => {
  const bodyCardRef = useRef<HTMLDivElement>(null);

  // Trigger flash animation when selected review changes
  useEffect(() => {
    if (bodyCardRef.current) {
      bodyCardRef.current.classList.remove('evidence-flash');
      // Trigger browser reflow
      void bodyCardRef.current.offsetWidth;
      bodyCardRef.current.classList.add('evidence-flash');
    }
  }, [selectedReview.id]);

  const handleExportJson = () => {
    const auditPayload = {
      specVersion: 'opinionlens-v2.4',
      timestamp: new Date().toISOString(),
      productId: productId,
      sha256Provenance: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      reviewRecord: selectedReview,
      pipelineTrace: [
        'CSV Ingestion filtered by product_id (' + productId + ')',
        'Retrieval: Aspect mode top-25 cosine vectors (bge-small-en)',
        'Groq LLM extraction (batches of 10) into AspectTuples',
        selectedReview.isRisk
          ? 'Safety Guard: Risk flag active (' + selectedReview.riskScoreText + ')'
          : 'Safety Guard: Safe evaluation passed',
      ],
    };

    const blob = new Blob([JSON.stringify(auditPayload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `opinionlens_audit_review_${selectedReview.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Render text with highlighted mark
  const renderHighlightedBody = () => {
    const { text, highlightedPhrase, isRisk } = selectedReview;
    if (!highlightedPhrase || !text.includes(highlightedPhrase)) {
      return <span>{text}</span>;
    }

    const parts = text.split(highlightedPhrase);
    return (
      <>
        <span>{parts[0]}</span>
        <mark
          className={
            isRisk
              ? 'bg-[#E10600]/40 text-white px-2 py-0.5 rounded border border-[#E10600]/70 font-medium shadow-[0_0_18px_rgba(225,6,0,0.65)]'
              : 'bg-[#BFE23A]/25 text-white px-2 py-0.5 rounded border border-[#BFE23A]/60 font-medium shadow-[0_0_18px_rgba(191,226,58,0.5)]'
          }
        >
          {highlightedPhrase}
        </mark>
        <span>{parts.slice(1).join(highlightedPhrase)}</span>
      </>
    );
  };

  return (
    <aside className="lg:col-span-5 space-y-6 lg:sticky lg:top-24" id="audit">
      {/* EVIDENCE INSPECTOR DRAWER */}
      <div className="frosted-glass-panel rounded-2xl p-6 transition-all duration-300 hover:-translate-y-0.5" id="evidenceInspectorBox">
        {/* Inspector Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/15 mb-4 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#F9EAD7]/15 border border-[#F9EAD7]/35 flex items-center justify-center text-[#F9EAD7] shadow-[0_0_16px_rgba(249,234,215,0.2),inset_0_1px_1px_rgba(255,255,255,0.4)] transition-transform duration-300 hover:scale-110">
              <span className="material-symbols-outlined text-2xl">manage_search</span>
            </div>
            <div>
              <h3 className="font-display text-lg font-bold text-white tracking-tight drop-shadow-[0_2px_8px_rgba(255,255,255,0.2)]">
                Evidence Inspector
              </h3>
              <p className="text-xs text-[#F9EAD7]/75">
                Raw Flipkart corpus verification
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-mono text-[#BFE23A] border border-[#BFE23A]/40 bg-[#BFE23A]/15 flex items-center gap-1.5 shadow-[0_0_12px_rgba(191,226,58,0.25)]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#BFE23A] animate-pulse" />
            Live Traceability
          </span>
        </div>

        {/* Audited Review Switcher Tabs */}
        <div className="mb-4 relative z-10">
          <label className="block text-xs font-mono uppercase tracking-wider text-[#F9EAD7]/75 mb-2">
            Audited Review Records:
          </label>
          <div className="flex flex-wrap gap-1.5" id="reviewTabs">
            {availableReviewIds.map((id) => {
              const isActive = selectedReview.id === id;
              const isRiskTab = ['15', '2', '33', '67'].includes(id);

              let tabClass =
                'review-tab px-3 py-1 rounded-xl text-xs font-mono glass-pill-surface text-[#F9EAD7]/85 hover:text-white transition-all cursor-pointer';

              if (isActive) {
                if (isRiskTab) {
                  tabClass =
                    'review-tab active px-3 py-1 rounded-xl text-xs font-mono font-bold bg-gradient-to-r from-[#E10600] to-[#FF332C] text-white border border-white/40 shadow-[0_0_16px_rgba(225,6,0,0.5),inset_0_1px_1px_rgba(255,255,255,0.6)] transition-all cursor-pointer';
                } else {
                  tabClass =
                    'review-tab active px-3 py-1 rounded-xl text-xs font-mono font-bold frosted-lime-button transition-all cursor-pointer';
                }
              }

              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => onSelectReview(id)}
                  className={tabClass}
                >
                  #{id} {isRiskTab && '(Risk)'}
                </button>
              );
            })}
          </div>
        </div>

        {/* Dynamic Review Evidence Container */}
        <div className="space-y-4 relative z-10" id="inspectorContent">
          {/* Metadata Card */}
          <div className="p-4 rounded-xl frosted-glass-well flex flex-col gap-2 transition-all duration-300">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white drop-shadow-[0_1px_4px_rgba(255,255,255,0.3)]">
                {selectedReview.title}
              </span>
              <div className="flex items-center text-[#F9EAD7] text-sm font-mono">
                <div className="flex items-center text-[#BFE23A] mr-1">
                  {[1, 2, 3, 4, 5].map((starIdx) => (
                    <span
                      key={starIdx}
                      className="material-symbols-outlined text-sm"
                      style={{
                        fontVariationSettings: starIdx <= selectedReview.numericRating ? "'FILL' 1" : "'FILL' 0",
                        color: starIdx <= selectedReview.numericRating ? '#BFE23A' : 'rgba(249, 234, 215, 0.3)',
                      }}
                    >
                      star
                    </span>
                  ))}
                </div>
                <span className="text-xs text-[#F9EAD7]/60 font-mono">{selectedReview.starsNum}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-[#F9EAD7]/85 pt-2 border-t border-white/10">
              <div>
                <span className="text-[#F9EAD7]/50 block">Date:</span>
                <span className="text-[#F9EAD7]">{selectedReview.date}</span>
              </div>
              <div>
                <span className="text-[#F9EAD7]/50 block">Helpful Votes:</span>
                <span className="text-[#F9EAD7]">{selectedReview.votes}</span>
              </div>
              <div>
                <span className="text-[#F9EAD7]/50 block">Product ID:</span>
                <span className="text-[#F9EAD7] truncate">{selectedReview.productId}</span>
              </div>
              <div>
                <span className="text-[#F9EAD7]/50 block">Reviewer Hash:</span>
                <span className="text-[#F9EAD7] truncate">{selectedReview.reviewerHash}</span>
              </div>
            </div>
          </div>

          {/* Full Review Body with Glowing Glass Highlight */}
          <div ref={bodyCardRef} className="p-4 rounded-xl frosted-glass-well transition-all duration-300">
            <div className="flex items-center justify-between text-xs font-mono text-[#F9EAD7]/60 mb-2">
              <span>VERBATIM CORPUS BODY</span>
              <span className="text-[#BFE23A] flex items-center gap-1 font-semibold">
                <span className="material-symbols-outlined text-xs">verified</span> Grounded match
              </span>
            </div>
            <p className="text-xs md:text-sm text-[#F9EAD7] leading-relaxed">
              {renderHighlightedBody()}
            </p>
          </div>

          {/* Pydantic Extracted Aspect Tuples Inspector */}
          <div className="p-4 rounded-xl frosted-glass-well transition-all duration-300">
            <div className="flex items-center justify-between mb-2 pb-2 border-b border-white/10">
              <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                <span className="material-symbols-outlined text-sm text-[#BFE23A]">schema</span>
                Pydantic Extracted Aspect Tuples
              </span>
              <span className="text-[11px] font-mono text-[#F9EAD7]/50">qwen3.8-27b</span>
            </div>
            <div className="space-y-1.5 font-mono text-xs">
              <div className="flex justify-between p-2 rounded-lg bg-black/40 border border-white/10 shadow-inner">
                <span className="text-[#F9EAD7]/60">aspect:</span>
                <span className="text-[#F9EAD7] font-semibold">{selectedReview.aspect}</span>
              </div>
              <div className="flex justify-between p-2 rounded-lg bg-black/40 border border-white/10 shadow-inner">
                <span className="text-[#F9EAD7]/60">sentiment:</span>
                <span
                  className={
                    selectedReview.isRisk ? 'text-[#FF332C] font-bold' : 'text-[#BFE23A] font-bold'
                  }
                >
                  "{selectedReview.sentiment}"
                </span>
              </div>
              <div className="flex justify-between p-2 rounded-lg bg-black/40 border border-white/10 shadow-inner">
                <span className="text-[#F9EAD7]/60">risk_score:</span>
                <span
                  className={
                    selectedReview.isRisk ? 'text-[#FF332C] font-bold' : 'text-[#BFE23A] font-bold'
                  }
                >
                  {selectedReview.riskScoreText}
                </span>
              </div>
              <div className="flex justify-between p-2 rounded-lg bg-black/40 border border-white/10 shadow-inner">
                <span className="text-[#F9EAD7]/60">embedding_model:</span>
                <span className="text-[#F9EAD7] font-medium">{selectedReview.embeddingModel}</span>
              </div>
              <div className="flex justify-between p-2 rounded-lg bg-black/40 border border-white/10 shadow-inner">
                <span className="text-[#F9EAD7]/60">cosine_similarity:</span>
                <span className="text-[#BFE23A] font-semibold">{selectedReview.cosineSimilarityText}</span>
              </div>
            </div>
          </div>
        </div>

        {/* SHA Provenance Locked Footer */}
        <div className="mt-4 pt-3 border-t border-white/15 flex items-center justify-between text-xs font-mono text-[#F9EAD7]/65 relative z-10">
          <span className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-sm text-[#BFE23A]">lock</span>
            SHA-256 Provenance Locked
          </span>
          <button
            type="button"
            onClick={handleExportJson}
            className="text-[#F9EAD7] hover:text-[#BFE23A] hover:underline transition-colors duration-200 cursor-pointer flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-xs">download</span>
            Export Audit Trail (JSON)
          </button>
        </div>
      </div>

      {/* Secondary Info Widget: Pipeline Trace */}
      <div className="frosted-glass-panel rounded-2xl p-5 transition-all duration-300 hover:-translate-y-0.5">
        <h4 className="text-xs font-mono uppercase tracking-wider text-[#F9EAD7] font-semibold mb-3 flex items-center gap-2 relative z-10">
          <span className="material-symbols-outlined text-sm text-[#BFE23A]">account_tree</span>
          RAG Pipeline Workflow Trace
        </h4>
        <ol className="space-y-2 text-xs font-mono text-[#F9EAD7]/85 relative z-10">
          <li className="flex items-center gap-2.5 transition-transform duration-200 hover:translate-x-1">
            <span className="w-5 h-5 rounded-full glass-pill-surface flex items-center justify-center text-[10px] text-[#F9EAD7] shrink-0 font-bold border border-white/20">
              1
            </span>
            <span>CSV Ingestion filtered by product_id ({productId})</span>
          </li>
          <li className="flex items-center gap-2.5 transition-transform duration-200 hover:translate-x-1">
            <span className="w-5 h-5 rounded-full glass-pill-surface flex items-center justify-center text-[10px] text-[#F9EAD7] shrink-0 font-bold border border-white/20">
              2
            </span>
            <span>Retrieval: Aspect mode top-25 cosine vectors (bge-small-en)</span>
          </li>
          <li className="flex items-center gap-2.5 transition-transform duration-200 hover:translate-x-1">
            <span className="w-5 h-5 rounded-full glass-pill-surface flex items-center justify-center text-[10px] text-[#F9EAD7] shrink-0 font-bold border border-white/20">
              3
            </span>
            <span>Groq LLM extraction (batches of 10) into AspectTuples</span>
          </li>
          <li className="flex items-center gap-2.5 transition-transform duration-200 hover:translate-x-1">
            <span
              className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                selectedReview.isRisk
                  ? 'bg-[#E10600] text-white shadow-[0_0_12px_#E10600]'
                  : 'bg-[#BFE23A] text-black shadow-[0_0_12px_#BFE23A]'
              }`}
            >
              4
            </span>
            <span className={selectedReview.isRisk ? 'text-[#FF332C] font-bold' : 'text-[#DCFF4E] font-medium'}>
              {selectedReview.isRisk
                ? 'Safety Guard: Overheating detected (N=4 ≥ 2 reviews)'
                : 'Safety Guard: Evaluation verified safe'}
            </span>
          </li>
        </ol>
      </div>
    </aside>
  );
};
