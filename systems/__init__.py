"""
EdTech RADAR - Systems Package
=============================

Comprehensive EdTech market intelligence and analysis platform.
Provides data structures, analysis engines, visualization tools, and automated workflows.
"""

__version__ = "1.0.0"
__author__ = "EdTech RADAR Development Team"

# Core imports for easy access
from systems.models.edtech_schemas import (
    CompanyProfile, MarketOpportunity, AnalysisScore,
    EdTechCategory, TargetAudience, BusinessModel, FundingStage
)

from systems.data.data_manager import EdTechDataManager
from systems.analysis.scoring_engine import EdTechScoringEngine
from systems.visualization.dashboard_generator import EdTechDashboardGenerator
from systems.exports.report_generator import EdTechReportGenerator
from systems.analysis.automated_workflows import EdTechAnalysisOrchestrator
from systems.data.sample_data_generator import EdTechSampleDataGenerator

__all__ = [
    # Core Models
    "CompanyProfile",
    "MarketOpportunity",
    "AnalysisScore",
    "EdTechCategory",
    "TargetAudience",
    "BusinessModel",
    "FundingStage",

    # Core Services
    "EdTechDataManager",
    "EdTechScoringEngine",
    "EdTechDashboardGenerator",
    "EdTechReportGenerator",
    "EdTechAnalysisOrchestrator",
    "EdTechSampleDataGenerator"
]