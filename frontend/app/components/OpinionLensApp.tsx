"use client";

import React, { useState, useMemo } from "react";
import { AmbientBackground } from "./AmbientBackground";
import { Header } from "./Header";
import { QueryStrip } from "./QueryStrip";
import { SafetyGuardCard } from "./SafetyGuardCard";
import { ConsensusCard } from "./ConsensusCard";
import { PolarizationCard } from "./PolarizationCard";
import { EvidenceInspector } from "./EvidenceInspector";
import { RepoAuditModal } from "./RepoAuditModal";
import { PRODUCT_DATASETS, REVIEWS_DATABASE } from "../data/opinionData";
import { evaluateGitHubRepoEffects } from "../utils/auditComparison";

export default function OpinionLensApp() {
  const [selectedBrandId, setSelectedBrandId] = useState("laptops");
  const [selectedModelId, setSelectedModelId] = useState("MACBOOK_AIR_M2");
  const [queryText, setQueryText] = useState("fanless thermal throttling, battery life, liquid retina");
  const [selectedReviewId, setSelectedReviewId] = useState("15");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);

  const auditResult = useMemo(() => evaluateGitHubRepoEffects(), []);

  // Retrieve current dataset and model
  const currentBrand = useMemo(() => {
    return PRODUCT_DATASETS.find((d) => d.brandId === selectedBrandId) || PRODUCT_DATASETS[0];
  }, [selectedBrandId]);

  const currentModel = useMemo(() => {
    return currentBrand.models.find((m) => m.id === selectedModelId) || currentBrand.models[0];
  }, [currentBrand, selectedModelId]);

  // Handle brand change
  const handleBrandChange = (brandId: string) => {
    setSelectedBrandId(brandId);
    const brand = PRODUCT_DATASETS.find((d) => d.brandId === brandId) || PRODUCT_DATASETS[0];
    const firstModel = brand.models[0];
    setSelectedModelId(firstModel.id);
  };

  // Handle model change
  const handleModelChange = (modelId: string) => {
    setSelectedModelId(modelId);
  };

  // Handle review selection with smooth scroll
  const handleSelectReview = (id: string) => {
    if (REVIEWS_DATABASE[id]) {
      setSelectedReviewId(id);
      const auditElement = document.getElementById("audit");
      if (auditElement) {
        auditElement.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }
  };

  // Handle review analysis simulation / backend trigger
  const handleAnalyzeReviews = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 700);
  };

  // List of active review IDs to show in the tabs
  const availableReviewIds = ["15", "2", "33", "67", "12", "4", "19", "23", "56", "7", "3", "18", "9", "44"];
  const currentReview = REVIEWS_DATABASE[selectedReviewId] || REVIEWS_DATABASE["15"];

  return (
    <div className="min-h-screen text-[#F9EAD7] font-sans antialiased relative selection:bg-[#BFE23A] selection:text-black">
      {/* Radiant ambient glow blur nodes and vector shapes */}
      <AmbientBackground />

      {/* Top frosted liquid glass navigation bar */}
      <Header
        onOpenAuditModal={() => setIsAuditModalOpen(true)}
        auditScore={auditResult.overallScore}
      />

      {/* Query & Retrieval parameter strip with live execution telemetry */}
      <QueryStrip
        datasets={PRODUCT_DATASETS}
        selectedBrandId={selectedBrandId}
        selectedModelId={selectedModelId}
        queryText={queryText}
        onBrandChange={handleBrandChange}
        onModelChange={handleModelChange}
        onQueryChange={setQueryText}
        onAnalyze={handleAnalyzeReviews}
        isAnalyzing={isAnalyzing}
        latencyText={currentModel.latency}
        totalVectors={currentModel.totalReviews}
      />

      {/* Main Canvas: Two-Panel 60% / 40% Architecture */}
      <div className="relative z-10 max-w-[1536px] mx-auto px-4 md:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column (7 cols / 60%) */}
          <section className="lg:col-span-7 space-y-6">
            {/* 1. Critical-Minority Safety Guard (Crimson Glass) */}
            <SafetyGuardCard
              hasSafetyWarning={currentModel.hasSafetyWarning}
              warningData={currentModel.safetyWarning}
              onSelectReview={handleSelectReview}
            />

            {/* 2. Attributed Consensus Summary (Translucent Glass Panel) */}
            <ConsensusCard
              groundednessScore={currentModel.groundednessScore}
              totalReviews={currentModel.totalReviews}
              bullets={currentModel.consensusBullets}
              onSelectReview={handleSelectReview}
            />

            {/* 3. Contested Viewpoints & Polarization Spectra */}
            <PolarizationCard
              aspect={currentModel.contestedAspect}
              onSelectReview={handleSelectReview}
            />
          </section>

          {/* Right Column (5 cols / 40%) */}
          <EvidenceInspector
            selectedReview={currentReview}
            availableReviewIds={availableReviewIds}
            onSelectReview={handleSelectReview}
            productId={currentModel.id}
          />
        </div>
      </div>

      {/* GitHub Repo Diagnostic Audit Modal */}
      <RepoAuditModal
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
      />
    </div>
  );
}
