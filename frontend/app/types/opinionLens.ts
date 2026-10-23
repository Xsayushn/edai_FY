export interface AuditedReview {
  id: string;
  isRisk: boolean;
  title: string;
  rating: string;
  numericRating: number;
  starsNum: string;
  date: string;
  votes: string;
  productId: string;
  reviewerHash: string;
  text: string;
  highlightedPhrase: string;
  aspect: string;
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  riskScoreText: string;
  embeddingModel: string;
  cosineSimilarityText: string;
}

export interface ConsensusBullet {
  id: string;
  text: string;
  isRisk?: boolean;
  citations: {
    reviewId: string;
    isRisk?: boolean;
  }[];
}

export interface ContestedAspect {
  title: string;
  contentionRatio: string;
  totalTuples: number;
  positivePct: number;
  positiveCount: number;
  negativePct: number;
  negativeCount: number;
  supporting: {
    count: number;
    conf: string;
    quote: string;
    citations: string[];
  };
  opposing: {
    count: number;
    conf: string;
    quote: string;
    citations: string[];
  };
}

export interface ProductDataset {
  brandId: string;
  brandName: string;
  csvFileName: string;
  models: {
    id: string;
    name: string;
    totalReviews: number;
    groundednessScore: string;
    latency: string;
    hasSafetyWarning: boolean;
    safetyWarning?: {
      title: string;
      thresholdText: string;
      riskLevel: string;
      detectedReviews: string[];
      taxonomy: string;
      verbatimQuote: string;
      ruleText: string;
    };
    consensusBullets: ConsensusBullet[];
    contestedAspect: ContestedAspect;
  }[];
}
