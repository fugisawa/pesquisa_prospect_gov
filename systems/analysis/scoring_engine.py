"""
EdTech RADAR - Advanced Scoring Engine
=====================================

Comprehensive scoring and evaluation framework for EdTech companies and market opportunities.
Implements multiple scoring methodologies with weighted criteria and automated analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

from systems.models.edtech_schemas import (
    CompanyProfile, MarketOpportunity, AnalysisScore,
    EdTechCategory, FundingStage, BusinessModel
)


@dataclass
class ScoringWeights:
    """Configurable weights for different scoring criteria"""

    # Market Attractiveness Weights (should sum to 1.0)
    market_size_weight: float = 0.4
    growth_potential_weight: float = 0.4
    competitive_landscape_weight: float = 0.2

    # Company Strength Weights (should sum to 1.0)
    financial_strength_weight: float = 0.3
    technology_weight: float = 0.25
    team_weight: float = 0.2
    product_weight: float = 0.25

    # Strategic Fit Weights (should sum to 1.0)
    alignment_weight: float = 0.4
    synergy_potential_weight: float = 0.3
    risk_assessment_weight: float = 0.3

    # Overall Category Weights (should sum to 1.0)
    market_category_weight: float = 0.3
    company_category_weight: float = 0.4
    strategic_category_weight: float = 0.3


class EdTechScoringEngine:
    """Advanced scoring engine for EdTech market analysis"""

    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.logger = logging.getLogger(__name__)

        # Industry benchmarks and standards
        self.industry_benchmarks = {
            'funding_stages': {
                FundingStage.BOOTSTRAP: {'min': 0, 'max': 100000, 'score_multiplier': 0.6},
                FundingStage.PRE_SEED: {'min': 100000, 'max': 500000, 'score_multiplier': 0.7},
                FundingStage.SEED: {'min': 500000, 'max': 2000000, 'score_multiplier': 0.8},
                FundingStage.SERIES_A: {'min': 2000000, 'max': 15000000, 'score_multiplier': 0.9},
                FundingStage.SERIES_B: {'min': 15000000, 'max': 50000000, 'score_multiplier': 0.95},
                FundingStage.SERIES_C: {'min': 50000000, 'max': 200000000, 'score_multiplier': 1.0},
                FundingStage.LATER_STAGE: {'min': 200000000, 'max': 1000000000, 'score_multiplier': 1.0},
            },
            'growth_rates': {
                'excellent': 100,  # >100% YoY
                'very_good': 50,   # 50-100% YoY
                'good': 25,        # 25-50% YoY
                'average': 10,     # 10-25% YoY
                'poor': 0          # <10% YoY
            },
            'market_sizes': {
                'mega': 10000000000,    # >$10B
                'large': 1000000000,    # $1B-$10B
                'medium': 100000000,    # $100M-$1B
                'small': 10000000,      # $10M-$100M
                'niche': 1000000        # <$10M
            }
        }

    def score_company(self, company: CompanyProfile) -> AnalysisScore:
        """Generate comprehensive analysis score for a company"""

        score = AnalysisScore()

        # Market Attractiveness Scoring
        score.market_size_score = self._score_market_size(company)
        score.growth_potential_score = self._score_growth_potential(company)
        score.competitive_landscape_score = self._score_competitive_landscape(company)

        # Company Strength Scoring
        score.financial_strength_score = self._score_financial_strength(company)
        score.technology_score = self._score_technology_stack(company)
        score.team_score = self._score_team_strength(company)
        score.product_score = self._score_product_quality(company)

        # Strategic Fit Scoring
        score.alignment_score = self._score_strategic_alignment(company)
        score.synergy_potential_score = self._score_synergy_potential(company)
        score.risk_assessment_score = self._score_risk_assessment(company)

        # Calculate total score and recommendations
        score.calculate_total_score()

        # Add metadata
        score.calculated_at = datetime.now()
        score.analyst = "EdTech Scoring Engine v1.0"

        self.logger.info(f"Scored company {company.name}: {score.total_score:.1f} ({score.investment_grade})")

        return score

    def score_market_opportunity(self, opportunity: MarketOpportunity) -> float:
        """Score a market opportunity (0-100 scale)"""

        scores = []

        # Market size scoring (0-25 points)
        if opportunity.market_size:
            if opportunity.market_size > self.industry_benchmarks['market_sizes']['mega']:
                market_size_score = 25
            elif opportunity.market_size > self.industry_benchmarks['market_sizes']['large']:
                market_size_score = 20
            elif opportunity.market_size > self.industry_benchmarks['market_sizes']['medium']:
                market_size_score = 15
            elif opportunity.market_size > self.industry_benchmarks['market_sizes']['small']:
                market_size_score = 10
            else:
                market_size_score = 5
            scores.append(market_size_score)

        # Growth rate scoring (0-25 points)
        if opportunity.growth_rate:
            if opportunity.growth_rate > self.industry_benchmarks['growth_rates']['excellent']:
                growth_score = 25
            elif opportunity.growth_rate > self.industry_benchmarks['growth_rates']['very_good']:
                growth_score = 20
            elif opportunity.growth_rate > self.industry_benchmarks['growth_rates']['good']:
                growth_score = 15
            elif opportunity.growth_rate > self.industry_benchmarks['growth_rates']['average']:
                growth_score = 10
            else:
                growth_score = 5
            scores.append(growth_score)

        # Competitive intensity scoring (0-25 points, inverse relationship)
        if opportunity.competitive_intensity:
            competition_score = max(5, 25 - (opportunity.competitive_intensity * 2))
            scores.append(competition_score)

        # ROI potential scoring (0-25 points)
        if opportunity.roi_potential:
            roi_score = min(25, opportunity.roi_potential / 4)  # Scale 0-100% to 0-25 points
            scores.append(roi_score)

        # Calculate weighted average
        total_score = sum(scores) if scores else 0
        max_possible = len(scores) * 25 if scores else 100

        return (total_score / max_possible) * 100 if max_possible > 0 else 0

    # Private scoring methods for individual criteria

    def _score_market_size(self, company: CompanyProfile) -> float:
        """Score based on addressable market size"""
        # This would typically use external market data
        # For now, we'll use category-based scoring

        category_scores = {
            EdTechCategory.LANGUAGE_LEARNING: 85,  # Large, growing market
            EdTechCategory.K12_EDUCATION: 90,      # Massive market
            EdTechCategory.HIGHER_EDUCATION: 80,   # Large but slower growth
            EdTechCategory.CORPORATE_TRAINING: 88, # High growth B2B market
            EdTechCategory.SKILL_DEVELOPMENT: 82,  # Growing professional market
            EdTechCategory.ASSESSMENT_TOOLS: 75,   # Specialized but important
            EdTechCategory.EDUCATIONAL_CONTENT: 70, # Competitive market
            EdTechCategory.LEARNING_MANAGEMENT: 85, # B2B institutional market
            EdTechCategory.TUTORING_PLATFORMS: 78,  # Growing personalized learning
            EdTechCategory.EDUCATIONAL_GAMES: 65,   # Niche but growing
        }

        if company.category:
            # Use highest category score if multiple categories
            scores = [category_scores.get(cat, 50) for cat in company.category]
            return max(scores)

        return 50  # Default neutral score

    def _score_growth_potential(self, company: CompanyProfile) -> float:
        """Score based on growth potential indicators"""
        score = 50  # Base score

        # Growth rate bonus
        if company.metrics.growth_rate:
            if company.metrics.growth_rate > 100:
                score += 30
            elif company.metrics.growth_rate > 50:
                score += 20
            elif company.metrics.growth_rate > 25:
                score += 10
            elif company.metrics.growth_rate > 10:
                score += 5

        # Funding stage bonus (earlier stages have higher growth potential)
        if company.funding.stage:
            stage_multipliers = {
                FundingStage.BOOTSTRAP: 1.2,
                FundingStage.PRE_SEED: 1.15,
                FundingStage.SEED: 1.1,
                FundingStage.SERIES_A: 1.05,
                FundingStage.SERIES_B: 1.0,
                FundingStage.SERIES_C: 0.95,
                FundingStage.LATER_STAGE: 0.9,
            }
            score *= stage_multipliers.get(company.funding.stage, 1.0)

        # User base growth indicators
        if company.metrics.user_base and company.metrics.user_base > 1000000:
            score += 10  # Large user base indicates market validation

        # Geographic expansion potential
        if company.geographic_presence.expansion_markets:
            score += len(company.geographic_presence.expansion_markets) * 2

        return min(100, max(0, score))

    def _score_competitive_landscape(self, company: CompanyProfile) -> float:
        """Score based on competitive position"""
        score = 50  # Base score

        # Competitive advantages
        if company.competitive_advantages:
            score += len(company.competitive_advantages) * 5

        # Market share (if available)
        if company.metrics.market_share:
            if company.metrics.market_share > 20:
                score += 25
            elif company.metrics.market_share > 10:
                score += 15
            elif company.metrics.market_share > 5:
                score += 10
            elif company.metrics.market_share > 1:
                score += 5

        # Number of competitors (inverse relationship)
        competitor_count = len(company.competitors)
        if competitor_count < 5:
            score += 15
        elif competitor_count < 10:
            score += 10
        elif competitor_count < 20:
            score += 5
        # No bonus for >20 competitors

        # Partnerships (strategic alliances)
        if company.partnerships:
            score += min(20, len(company.partnerships) * 3)

        return min(100, max(0, score))

    def _score_financial_strength(self, company: CompanyProfile) -> float:
        """Score based on financial metrics"""
        score = 50  # Base score

        # Funding amount
        if company.funding.total_raised:
            funding = company.funding.total_raised
            if funding > 100000000:  # >$100M
                score += 25
            elif funding > 50000000:  # $50M-$100M
                score += 20
            elif funding > 10000000:  # $10M-$50M
                score += 15
            elif funding > 1000000:   # $1M-$10M
                score += 10
            elif funding > 100000:    # $100K-$1M
                score += 5

        # Revenue (if available)
        if company.metrics.annual_revenue:
            revenue = company.metrics.annual_revenue
            if revenue > 50000000:    # >$50M
                score += 20
            elif revenue > 10000000:  # $10M-$50M
                score += 15
            elif revenue > 1000000:   # $1M-$10M
                score += 10
            elif revenue > 100000:    # $100K-$1M
                score += 5

        # Funding stage maturity
        if company.funding.stage:
            stage_bonuses = {
                FundingStage.SERIES_C: 15,
                FundingStage.SERIES_B: 12,
                FundingStage.SERIES_A: 10,
                FundingStage.SEED: 8,
                FundingStage.PRE_SEED: 5,
                FundingStage.BOOTSTRAP: 3,
            }
            score += stage_bonuses.get(company.funding.stage, 0)

        # Investor quality (assuming high-quality investors)
        if company.funding.investors:
            score += min(15, len(company.funding.investors) * 2)

        return min(100, max(0, score))

    def _score_technology_stack(self, company: CompanyProfile) -> float:
        """Score based on technology sophistication"""
        score = 50  # Base score

        # AI/ML capabilities
        ai_keywords = ['ai', 'ml', 'machine learning', 'artificial intelligence',
                      'nlp', 'computer vision', 'deep learning', 'neural']

        tech_stack = company.technology_stack
        ai_tech = [tech for tech in tech_stack.ai_ml if any(keyword in tech.lower() for keyword in ai_keywords)]

        if ai_tech:
            score += min(20, len(ai_tech) * 5)

        # Modern tech stack indicators
        modern_tech_score = 0
        modern_frontend = ['react', 'vue', 'angular', 'flutter', 'react native']
        modern_backend = ['node.js', 'python', 'go', 'rust', 'microservices']
        modern_cloud = ['aws', 'gcp', 'azure', 'kubernetes', 'docker']

        if any(tech.lower() in ' '.join(tech_stack.frontend).lower() for tech in modern_frontend):
            modern_tech_score += 5
        if any(tech.lower() in ' '.join(tech_stack.backend).lower() for tech in modern_backend):
            modern_tech_score += 5
        if any(tech.lower() in ' '.join(tech_stack.cloud_platform).lower() for tech in modern_cloud):
            modern_tech_score += 5

        score += modern_tech_score

        # Mobile capabilities
        if tech_stack.mobile:
            score += 10

        # Scalability indicators
        scalability_keywords = ['microservices', 'kubernetes', 'docker', 'redis', 'elasticsearch']
        all_tech = ' '.join(tech_stack.frontend + tech_stack.backend + tech_stack.cloud_platform).lower()

        scalability_score = sum(5 for keyword in scalability_keywords if keyword in all_tech)
        score += min(15, scalability_score)

        return min(100, max(0, score))

    def _score_team_strength(self, company: CompanyProfile) -> float:
        """Score based on team size and experience indicators"""
        score = 50  # Base score

        # Team size
        if company.metrics.employees_count:
            employees = company.metrics.employees_count
            if employees > 500:
                score += 20
            elif employees > 100:
                score += 15
            elif employees > 50:
                score += 12
            elif employees > 20:
                score += 10
            elif employees > 10:
                score += 8
            elif employees > 5:
                score += 5

        # Founded date (experience proxy)
        if company.founded:
            years_in_business = datetime.now().year - company.founded
            if years_in_business > 10:
                score += 15
            elif years_in_business > 5:
                score += 10
            elif years_in_business > 3:
                score += 8
            elif years_in_business > 1:
                score += 5

        # Funding success (team execution track record)
        if company.funding.total_raised and company.funding.total_raised > 10000000:
            score += 10  # Successful fundraising indicates strong team

        return min(100, max(0, score))

    def _score_product_quality(self, company: CompanyProfile) -> float:
        """Score based on product features and market fit"""
        score = 50  # Base score

        # Product diversity
        if company.products:
            score += min(15, len(company.products) * 3)

        # Key features count
        if company.key_features:
            score += min(20, len(company.key_features) * 2)

        # User engagement indicators
        if company.metrics.retention_rate:
            if company.metrics.retention_rate > 80:
                score += 20
            elif company.metrics.retention_rate > 60:
                score += 15
            elif company.metrics.retention_rate > 40:
                score += 10
            elif company.metrics.retention_rate > 20:
                score += 5

        # User base size (product-market fit indicator)
        if company.metrics.user_base:
            users = company.metrics.user_base
            if users > 10000000:      # >10M users
                score += 15
            elif users > 1000000:     # 1M-10M users
                score += 12
            elif users > 100000:      # 100K-1M users
                score += 10
            elif users > 10000:       # 10K-100K users
                score += 8
            elif users > 1000:        # 1K-10K users
                score += 5

        return min(100, max(0, score))

    def _score_strategic_alignment(self, company: CompanyProfile) -> float:
        """Score based on strategic alignment with investment thesis"""
        # This would be customized based on specific investment criteria
        # For now, we'll use general EdTech alignment factors

        score = 50  # Base score

        # High-growth categories
        preferred_categories = [
            EdTechCategory.LANGUAGE_LEARNING,
            EdTechCategory.CORPORATE_TRAINING,
            EdTechCategory.SKILL_DEVELOPMENT
        ]

        if any(cat in preferred_categories for cat in company.category):
            score += 20

        # B2B model preference (typically more scalable)
        if BusinessModel.B2B_LICENSE in company.business_model:
            score += 15

        # Geographic alignment
        preferred_markets = ['United States', 'Europe', 'Asia', 'Brazil', 'India']
        if company.geographic_presence.headquarters in preferred_markets:
            score += 10

        # Innovation indicators
        if 'ai' in company.description.lower() or 'artificial intelligence' in company.description.lower():
            score += 10

        return min(100, max(0, score))

    def _score_synergy_potential(self, company: CompanyProfile) -> float:
        """Score based on potential synergies with existing portfolio"""
        # This would be customized based on existing portfolio companies
        # For now, we'll use general synergy indicators

        score = 50  # Base score

        # Technology synergies
        complementary_tech = ['api', 'integration', 'platform', 'marketplace']
        if any(tech in company.description.lower() for tech in complementary_tech):
            score += 15

        # Market expansion potential
        if len(company.geographic_presence.expansion_markets) > 3:
            score += 15

        # Partnership potential
        if company.partnerships:
            score += min(20, len(company.partnerships) * 3)

        return min(100, max(0, score))

    def _score_risk_assessment(self, company: CompanyProfile) -> float:
        """Score based on risk factors (higher score = lower risk)"""
        score = 50  # Base score

        # Financial risk factors
        if company.funding.total_raised and company.funding.total_raised > 5000000:
            score += 15  # Well-funded companies are lower risk

        # Market risk factors
        if len(company.competitors) < 10:
            score += 10  # Less competitive markets are lower risk

        # Execution risk factors
        if company.metrics.employees_count and company.metrics.employees_count > 20:
            score += 10  # Larger teams reduce execution risk

        # Product risk factors
        if company.metrics.user_base and company.metrics.user_base > 100000:
            score += 15  # Proven market traction reduces product risk

        # Geographic risk factors
        stable_markets = ['United States', 'Canada', 'United Kingdom', 'Germany', 'Australia']
        if company.geographic_presence.headquarters in stable_markets:
            score += 10

        return min(100, max(0, score))

    def batch_score_companies(self, companies: List[CompanyProfile]) -> List[Tuple[CompanyProfile, AnalysisScore]]:
        """Score multiple companies in batch"""
        results = []

        for company in companies:
            try:
                score = self.score_company(company)
                results.append((company, score))
            except Exception as e:
                self.logger.error(f"Error scoring company {company.name}: {e}")
                continue

        # Sort by total score (descending)
        results.sort(key=lambda x: x[1].total_score, reverse=True)

        return results

    def generate_portfolio_report(self, scored_companies: List[Tuple[CompanyProfile, AnalysisScore]]) -> Dict[str, Any]:
        """Generate comprehensive portfolio analysis report"""

        if not scored_companies:
            return {}

        companies, scores = zip(*scored_companies)

        # Calculate aggregate statistics
        total_scores = [score.total_score for score in scores]

        report = {
            'summary': {
                'total_companies': len(companies),
                'average_score': np.mean(total_scores),
                'median_score': np.median(total_scores),
                'std_score': np.std(total_scores),
                'top_quartile_threshold': np.percentile(total_scores, 75),
                'generated_at': datetime.now().isoformat()
            },
            'grade_distribution': {},
            'recommendation_distribution': {},
            'top_performers': [],
            'category_analysis': {},
            'risk_analysis': {}
        }

        # Grade distribution
        grades = [score.investment_grade for score in scores]
        for grade in set(grades):
            report['grade_distribution'][grade] = grades.count(grade)

        # Recommendation distribution
        recommendations = [score.recommendation for score in scores]
        for rec in set(recommendations):
            report['recommendation_distribution'][rec] = recommendations.count(rec)

        # Top performers (top 10 or 20% whichever is smaller)
        top_count = min(10, max(1, len(scored_companies) // 5))
        report['top_performers'] = [
            {
                'name': company.name,
                'score': score.total_score,
                'grade': score.investment_grade,
                'recommendation': score.recommendation,
                'category': [cat.value for cat in company.category] if company.category else []
            }
            for company, score in scored_companies[:top_count]
        ]

        # Category performance analysis
        category_scores = {}
        for company, score in scored_companies:
            for category in company.category:
                if category.value not in category_scores:
                    category_scores[category.value] = []
                category_scores[category.value].append(score.total_score)

        report['category_analysis'] = {
            cat: {
                'average_score': np.mean(scores),
                'count': len(scores),
                'top_score': max(scores),
                'min_score': min(scores)
            }
            for cat, scores in category_scores.items()
        }

        return report