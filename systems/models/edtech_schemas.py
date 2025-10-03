"""
EdTech RADAR - Core Data Schemas and Models
===========================================

This module defines the data structures for organizing EdTech market intelligence.
Includes company profiles, market opportunities, and classification systems.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from datetime import datetime
import json


class EdTechCategory(Enum):
    """EdTech solution categories"""
    LANGUAGE_LEARNING = "language_learning"
    K12_EDUCATION = "k12_education"
    HIGHER_EDUCATION = "higher_education"
    CORPORATE_TRAINING = "corporate_training"
    SKILL_DEVELOPMENT = "skill_development"
    ASSESSMENT_TOOLS = "assessment_tools"
    EDUCATIONAL_CONTENT = "educational_content"
    LEARNING_MANAGEMENT = "learning_management"
    TUTORING_PLATFORMS = "tutoring_platforms"
    EDUCATIONAL_GAMES = "educational_games"


class TargetAudience(Enum):
    """Target audience segments"""
    CHILDREN = "children"  # 0-12
    TEENAGERS = "teenagers"  # 13-18
    YOUNG_ADULTS = "young_adults"  # 18-25
    ADULTS = "adults"  # 25-65
    SENIORS = "seniors"  # 65+
    TEACHERS = "teachers"
    PARENTS = "parents"
    CORPORATES = "corporates"
    INSTITUTIONS = "institutions"


class BusinessModel(Enum):
    """Business model types"""
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    ONE_TIME_PURCHASE = "one_time_purchase"
    B2B_LICENSE = "b2b_license"
    MARKETPLACE = "marketplace"
    ADVERTISING = "advertising"
    HYBRID = "hybrid"


class FundingStage(Enum):
    """Company funding stages"""
    BOOTSTRAP = "bootstrap"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    LATER_STAGE = "later_stage"
    IPO = "ipo"
    ACQUIRED = "acquired"


@dataclass
class TechnologyStack:
    """Technology stack information"""
    frontend: List[str] = field(default_factory=list)
    backend: List[str] = field(default_factory=list)
    database: List[str] = field(default_factory=list)
    ai_ml: List[str] = field(default_factory=list)
    cloud_platform: List[str] = field(default_factory=list)
    mobile: List[str] = field(default_factory=list)
    other: List[str] = field(default_factory=list)


@dataclass
class Funding:
    """Funding information"""
    total_raised: Optional[float] = None  # In USD
    latest_round: Optional[str] = None
    latest_round_amount: Optional[float] = None
    latest_round_date: Optional[datetime] = None
    investors: List[str] = field(default_factory=list)
    valuation: Optional[float] = None
    stage: Optional[FundingStage] = None


@dataclass
class CompanyMetrics:
    """Key company metrics"""
    employees_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    user_base: Optional[int] = None
    active_users: Optional[int] = None
    growth_rate: Optional[float] = None  # Percentage
    market_share: Optional[float] = None  # Percentage
    retention_rate: Optional[float] = None  # Percentage


@dataclass
class GeographicPresence:
    """Geographic market presence"""
    headquarters: Optional[str] = None
    primary_markets: List[str] = field(default_factory=list)
    expansion_markets: List[str] = field(default_factory=list)
    total_countries: Optional[int] = None


@dataclass
class Product:
    """Product/service information"""
    name: str
    description: str
    category: EdTechCategory
    target_audience: List[TargetAudience] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    pricing: Dict[str, Any] = field(default_factory=dict)
    launch_date: Optional[datetime] = None
    status: str = "active"  # active, beta, discontinued


@dataclass
class CompanyProfile:
    """Complete company profile for EdTech market analysis"""

    # Basic Information
    name: str
    website: str
    founded: Optional[int] = None
    description: str = ""

    # Business Details
    business_model: List[BusinessModel] = field(default_factory=list)
    category: List[EdTechCategory] = field(default_factory=list)
    target_audience: List[TargetAudience] = field(default_factory=list)

    # Products and Services
    products: List[Product] = field(default_factory=list)
    key_features: List[str] = field(default_factory=list)

    # Financial Information
    funding: Funding = field(default_factory=Funding)
    metrics: CompanyMetrics = field(default_factory=CompanyMetrics)

    # Technical Information
    technology_stack: TechnologyStack = field(default_factory=TechnologyStack)

    # Market Information
    geographic_presence: GeographicPresence = field(default_factory=GeographicPresence)
    competitors: List[str] = field(default_factory=list)
    partnerships: List[str] = field(default_factory=list)

    # Analysis Fields
    competitive_advantages: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    data_sources: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None  # 0-1 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        def convert_enum_list(enum_list):
            return [item.value if hasattr(item, 'value') else item for item in enum_list]

        def convert_datetime(dt):
            return dt.isoformat() if dt else None

        return {
            'name': self.name,
            'website': self.website,
            'founded': self.founded,
            'description': self.description,
            'business_model': convert_enum_list(self.business_model),
            'category': convert_enum_list(self.category),
            'target_audience': convert_enum_list(self.target_audience),
            'products': [
                {
                    'name': p.name,
                    'description': p.description,
                    'category': p.category.value if p.category else None,
                    'target_audience': convert_enum_list(p.target_audience),
                    'features': p.features,
                    'pricing': p.pricing,
                    'launch_date': convert_datetime(p.launch_date),
                    'status': p.status
                } for p in self.products
            ],
            'key_features': self.key_features,
            'funding': {
                'total_raised': self.funding.total_raised,
                'latest_round': self.funding.latest_round,
                'latest_round_amount': self.funding.latest_round_amount,
                'latest_round_date': convert_datetime(self.funding.latest_round_date),
                'investors': self.funding.investors,
                'valuation': self.funding.valuation,
                'stage': self.funding.stage.value if self.funding.stage else None
            },
            'metrics': {
                'employees_count': self.metrics.employees_count,
                'annual_revenue': self.metrics.annual_revenue,
                'user_base': self.metrics.user_base,
                'active_users': self.metrics.active_users,
                'growth_rate': self.metrics.growth_rate,
                'market_share': self.metrics.market_share,
                'retention_rate': self.metrics.retention_rate
            },
            'technology_stack': {
                'frontend': self.technology_stack.frontend,
                'backend': self.technology_stack.backend,
                'database': self.technology_stack.database,
                'ai_ml': self.technology_stack.ai_ml,
                'cloud_platform': self.technology_stack.cloud_platform,
                'mobile': self.technology_stack.mobile,
                'other': self.technology_stack.other
            },
            'geographic_presence': {
                'headquarters': self.geographic_presence.headquarters,
                'primary_markets': self.geographic_presence.primary_markets,
                'expansion_markets': self.geographic_presence.expansion_markets,
                'total_countries': self.geographic_presence.total_countries
            },
            'competitors': self.competitors,
            'partnerships': self.partnerships,
            'competitive_advantages': self.competitive_advantages,
            'weaknesses': self.weaknesses,
            'opportunities': self.opportunities,
            'threats': self.threats,
            'created_at': convert_datetime(self.created_at),
            'updated_at': convert_datetime(self.updated_at),
            'data_sources': self.data_sources,
            'confidence_score': self.confidence_score
        }


@dataclass
class MarketOpportunity:
    """Market opportunity analysis structure"""

    # Basic Information
    id: str
    name: str
    description: str
    category: EdTechCategory

    # Market Sizing
    market_size: Optional[float] = None  # In USD
    addressable_market: Optional[float] = None  # TAM
    serviceable_market: Optional[float] = None  # SAM
    target_market: Optional[float] = None  # SOM
    growth_rate: Optional[float] = None  # Annual percentage

    # Market Dynamics
    key_trends: List[str] = field(default_factory=list)
    driving_factors: List[str] = field(default_factory=list)
    barriers_to_entry: List[str] = field(default_factory=list)
    regulatory_factors: List[str] = field(default_factory=list)

    # Competitive Landscape
    key_players: List[str] = field(default_factory=list)
    market_leaders: List[str] = field(default_factory=list)
    emerging_players: List[str] = field(default_factory=list)
    competitive_intensity: Optional[float] = None  # 1-10 scale

    # Technology Requirements
    required_technologies: List[str] = field(default_factory=list)
    emerging_technologies: List[str] = field(default_factory=list)
    technical_complexity: Optional[float] = None  # 1-10 scale

    # Investment Analysis
    investment_needed: Optional[float] = None  # Estimated USD
    time_to_market: Optional[int] = None  # Months
    roi_potential: Optional[float] = None  # Percentage
    risk_level: Optional[float] = None  # 1-10 scale

    # Geographic Information
    primary_regions: List[str] = field(default_factory=list)
    expansion_potential: List[str] = field(default_factory=list)
    regulatory_complexity: Dict[str, float] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence_score: Optional[float] = None  # 0-1 scale
    data_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        def convert_datetime(dt):
            return dt.isoformat() if dt else None

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'market_size': self.market_size,
            'addressable_market': self.addressable_market,
            'serviceable_market': self.serviceable_market,
            'target_market': self.target_market,
            'growth_rate': self.growth_rate,
            'key_trends': self.key_trends,
            'driving_factors': self.driving_factors,
            'barriers_to_entry': self.barriers_to_entry,
            'regulatory_factors': self.regulatory_factors,
            'key_players': self.key_players,
            'market_leaders': self.market_leaders,
            'emerging_players': self.emerging_players,
            'competitive_intensity': self.competitive_intensity,
            'required_technologies': self.required_technologies,
            'emerging_technologies': self.emerging_technologies,
            'technical_complexity': self.technical_complexity,
            'investment_needed': self.investment_needed,
            'time_to_market': self.time_to_market,
            'roi_potential': self.roi_potential,
            'risk_level': self.risk_level,
            'primary_regions': self.primary_regions,
            'expansion_potential': self.expansion_potential,
            'regulatory_complexity': self.regulatory_complexity,
            'created_at': convert_datetime(self.created_at),
            'updated_at': convert_datetime(self.updated_at),
            'confidence_score': self.confidence_score,
            'data_sources': self.data_sources
        }


@dataclass
class AnalysisScore:
    """Comprehensive scoring framework for prospects"""

    # Market Attractiveness (0-100)
    market_size_score: float = 0.0
    growth_potential_score: float = 0.0
    competitive_landscape_score: float = 0.0

    # Company Strength (0-100)
    financial_strength_score: float = 0.0
    technology_score: float = 0.0
    team_score: float = 0.0
    product_score: float = 0.0

    # Strategic Fit (0-100)
    alignment_score: float = 0.0
    synergy_potential_score: float = 0.0
    risk_assessment_score: float = 0.0

    # Overall Scores
    total_score: float = 0.0
    investment_grade: str = "C"  # A+, A, B+, B, C+, C, D
    recommendation: str = "HOLD"  # BUY, STRONG_BUY, HOLD, SELL

    # Metadata
    calculated_at: datetime = field(default_factory=datetime.now)
    analyst: Optional[str] = None
    notes: str = ""

    def calculate_total_score(self) -> float:
        """Calculate weighted total score"""
        weights = {
            'market': 0.3,
            'company': 0.4,
            'strategic': 0.3
        }

        market_avg = (self.market_size_score + self.growth_potential_score + self.competitive_landscape_score) / 3
        company_avg = (self.financial_strength_score + self.technology_score + self.team_score + self.product_score) / 4
        strategic_avg = (self.alignment_score + self.synergy_potential_score + self.risk_assessment_score) / 3

        self.total_score = (market_avg * weights['market'] +
                           company_avg * weights['company'] +
                           strategic_avg * weights['strategic'])

        # Determine grade
        if self.total_score >= 90:
            self.investment_grade = "A+"
        elif self.total_score >= 85:
            self.investment_grade = "A"
        elif self.total_score >= 80:
            self.investment_grade = "B+"
        elif self.total_score >= 75:
            self.investment_grade = "B"
        elif self.total_score >= 70:
            self.investment_grade = "C+"
        elif self.total_score >= 60:
            self.investment_grade = "C"
        else:
            self.investment_grade = "D"

        # Determine recommendation
        if self.total_score >= 85:
            self.recommendation = "STRONG_BUY"
        elif self.total_score >= 75:
            self.recommendation = "BUY"
        elif self.total_score >= 60:
            self.recommendation = "HOLD"
        else:
            self.recommendation = "SELL"

        return self.total_score