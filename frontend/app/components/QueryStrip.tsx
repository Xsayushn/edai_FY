import React from 'react';
import Link from 'next/link';
import { ProductDataset } from '../types/opinionLens';

interface QueryStripProps {
  datasets: ProductDataset[];
  selectedBrandId: string;
  selectedModelId: string;
  queryText: string;
  onBrandChange: (brandId: string) => void;
  onModelChange: (modelId: string) => void;
  onQueryChange: (query: string) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  totalReviews: number;
}

export const QueryStrip: React.FC<QueryStripProps> = ({
  datasets,
  selectedBrandId,
  selectedModelId,
  queryText,
  onBrandChange,
  onModelChange,
  onQueryChange,
  onAnalyze,
  isAnalyzing,
  totalReviews,
}) => {
  const currentBrand = datasets.find((d) => d.brandId === selectedBrandId) || datasets[0];

  return (
    <section className="relative z-10 frosted-glass-panel border-b border-white/15 px-4 md:px-8 py-4 backdrop-blur-2xl">
      <div className="max-w-[1536px] mx-auto flex flex-col xl:flex-row items-stretch xl:items-center justify-between gap-4">
        {/* Brand, Target Model, and RAG Query */}
        <div className="flex flex-wrap lg:flex-nowrap items-center gap-3 flex-1">
          {/* Brand Selector */}
          <div className="w-full sm:w-auto min-w-[170px]">
            <label
              htmlFor="brandSelect"
              className="block text-[11px] font-mono uppercase tracking-wider text-[#F9EAD7]/75 mb-1 flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-xs text-[#BFE23A]">category</span> Brand Dataset
            </label>
            <select
              id="brandSelect"
              value={selectedBrandId}
              onChange={(e) => onBrandChange(e.target.value)}
              className="glass-input-field w-full rounded-xl px-3 py-2 text-xs font-medium text-[#F9EAD7] focus:text-white cursor-pointer"
            >
              {datasets.map((d) => (
                <option key={d.brandId} value={d.brandId} className="bg-[#111317] text-[#F9EAD7]">
                  {d.brandName}
                </option>
              ))}
            </select>
          </div>

          {/* Product Model Selector */}
          <div className="w-full sm:w-auto flex-1 min-w-[280px]">
            <label
              htmlFor="productSelect"
              className="block text-[11px] font-mono uppercase tracking-wider text-[#F9EAD7]/75 mb-1 flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-xs text-[#BFE23A]">devices</span> Target Product Model
            </label>
            <select
              id="productSelect"
              value={selectedModelId}
              onChange={(e) => onModelChange(e.target.value)}
              className="glass-input-field w-full rounded-xl px-3 py-2 text-xs font-medium text-[#F9EAD7] focus:text-white cursor-pointer truncate"
            >
              {currentBrand.models.map((m) => (
                <option key={m.id} value={m.id} className="bg-[#111317] text-[#F9EAD7]">
                  {m.name} • {m.totalReviews} Reviews
                </option>
              ))}
            </select>
          </div>

          {/* RAG Aspect Query Input */}
          <div className="w-full lg:flex-[1.4] min-w-[270px]">
            <label
              htmlFor="queryInput"
              className="block text-[11px] font-mono uppercase tracking-wider text-[#F9EAD7]/75 mb-1 flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-xs text-[#BFE23A]">saved_search</span> RAG Aspect Query (or blank for balanced)
            </label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-base text-[#F9EAD7]/60 transition-colors duration-200 group-focus-within:text-[#BFE23A]">
                search
              </span>
              <input
                id="queryInput"
                type="text"
                value={queryText}
                onChange={(e) => onQueryChange(e.target.value)}
                placeholder="e.g. battery heating, camera quality, low light..."
                className="glass-input-field w-full rounded-xl pl-9 pr-3 py-2 text-xs font-medium text-white placeholder:text-[#F9EAD7]/40"
              />
            </div>
          </div>
        </div>

        {/* Sample dashboard action */}
        <div className="flex items-center gap-2.5 self-end xl:self-center pt-1">
          <button
            id="analyzeBtn"
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="frosted-lime-button px-5 py-2 rounded-xl font-display font-semibold text-xs flex items-center gap-2 tracking-wide cursor-pointer disabled:opacity-75"
          >
            {isAnalyzing ? (
              <>
                <span className="material-symbols-outlined text-base animate-spin">sync</span>
                <span>Loading sample...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-base font-bold transition-transform duration-300 group-hover:scale-110">
                  auto_awesome
                </span>
                <span>Replay Sample</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Sample data status */}
      <div className="max-w-[1536px] mx-auto mt-3 pt-2.5 border-t border-white/10 flex flex-wrap items-center justify-between text-xs font-mono text-[#F9EAD7]/70 gap-2">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#BFE23A] shadow-[0_0_10px_#BFE23A]" />
          Sample dashboard: <strong className="text-white font-semibold">{currentBrand.brandName}</strong>
          <span className="text-white/40">·</span>
          {totalReviews} example reviews
        </span>
        <Link href="/audit/MOBE7JXXKS6PWW2C" className="text-[#BFE23A] hover:text-white transition-colors">
          Open live Lenovo audit →
        </Link>
      </div>
    </section>
  );
};
