"""
EdTech RADAR - Data Management System
====================================

Handles data storage, retrieval, and management for EdTech market intelligence.
Provides CRUD operations, data validation, and search capabilities.
"""

import json
import csv
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import logging
from dataclasses import asdict

from systems.models.edtech_schemas import (
    CompanyProfile, MarketOpportunity, AnalysisScore,
    EdTechCategory, TargetAudience, BusinessModel, FundingStage
)


class EdTechDataManager:
    """Centralized data management for EdTech market intelligence"""

    def __init__(self, data_dir: str = "systems/data/storage"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Database connections
        self.db_path = self.data_dir / "edtech_radar.db"
        self.init_database()

        # File paths
        self.companies_file = self.data_dir / "companies.json"
        self.opportunities_file = self.data_dir / "opportunities.json"
        self.scores_file = self.data_dir / "analysis_scores.json"

        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    website TEXT,
                    founded INTEGER,
                    description TEXT,
                    category TEXT,
                    target_audience TEXT,
                    business_model TEXT,
                    funding_stage TEXT,
                    total_raised REAL,
                    employees_count INTEGER,
                    annual_revenue REAL,
                    user_base INTEGER,
                    headquarters TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_json TEXT
                )
            """)

            # Market opportunities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_opportunities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    market_size REAL,
                    growth_rate REAL,
                    competitive_intensity REAL,
                    investment_needed REAL,
                    roi_potential REAL,
                    risk_level REAL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_json TEXT
                )
            """)

            # Analysis scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_scores (
                    company_name TEXT PRIMARY KEY,
                    total_score REAL,
                    investment_grade TEXT,
                    recommendation TEXT,
                    market_size_score REAL,
                    growth_potential_score REAL,
                    competitive_landscape_score REAL,
                    financial_strength_score REAL,
                    technology_score REAL,
                    team_score REAL,
                    product_score REAL,
                    alignment_score REAL,
                    synergy_potential_score REAL,
                    risk_assessment_score REAL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analyst TEXT,
                    notes TEXT
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_category ON companies(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_funding_stage ON companies(funding_stage)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_category ON market_opportunities(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_grade ON analysis_scores(investment_grade)")

            conn.commit()

    # Company Management
    def add_company(self, company: CompanyProfile) -> bool:
        """Add a new company to the database"""
        try:
            company.updated_at = datetime.now()
            company_dict = company.to_dict()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO companies (
                        name, website, founded, description, category, target_audience,
                        business_model, funding_stage, total_raised, employees_count,
                        annual_revenue, user_base, headquarters, confidence_score,
                        updated_at, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company.name,
                    company.website,
                    company.founded,
                    company.description,
                    json.dumps([cat.value for cat in company.category]) if company.category else None,
                    json.dumps([aud.value for aud in company.target_audience]) if company.target_audience else None,
                    json.dumps([bm.value for bm in company.business_model]) if company.business_model else None,
                    company.funding.stage.value if company.funding.stage else None,
                    company.funding.total_raised,
                    company.metrics.employees_count,
                    company.metrics.annual_revenue,
                    company.metrics.user_base,
                    company.geographic_presence.headquarters,
                    company.confidence_score,
                    company.updated_at.isoformat(),
                    json.dumps(company_dict)
                ))
                conn.commit()

            self.logger.info(f"Added company: {company.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding company {company.name}: {e}")
            return False

    def get_company(self, name: str) -> Optional[CompanyProfile]:
        """Retrieve a company by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM companies WHERE name = ?", (name,))
                result = cursor.fetchone()

                if result:
                    company_dict = json.loads(result[0])
                    return self._dict_to_company(company_dict)

        except Exception as e:
            self.logger.error(f"Error retrieving company {name}: {e}")

        return None

    def search_companies(self,
                        category: Optional[EdTechCategory] = None,
                        target_audience: Optional[TargetAudience] = None,
                        funding_stage: Optional[FundingStage] = None,
                        min_funding: Optional[float] = None,
                        max_funding: Optional[float] = None,
                        min_employees: Optional[int] = None,
                        max_employees: Optional[int] = None) -> List[CompanyProfile]:
        """Search companies with filters"""

        query = "SELECT data_json FROM companies WHERE 1=1"
        params = []

        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category.value}%")

        if funding_stage:
            query += " AND funding_stage = ?"
            params.append(funding_stage.value)

        if min_funding:
            query += " AND total_raised >= ?"
            params.append(min_funding)

        if max_funding:
            query += " AND total_raised <= ?"
            params.append(max_funding)

        if min_employees:
            query += " AND employees_count >= ?"
            params.append(min_employees)

        if max_employees:
            query += " AND employees_count <= ?"
            params.append(max_employees)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()

                companies = []
                for result in results:
                    company_dict = json.loads(result[0])
                    company = self._dict_to_company(company_dict)

                    # Additional filtering for target audience (stored as JSON array)
                    if target_audience and company:
                        if target_audience not in company.target_audience:
                            continue

                    if company:
                        companies.append(company)

                return companies

        except Exception as e:
            self.logger.error(f"Error searching companies: {e}")
            return []

    # Market Opportunity Management
    def add_opportunity(self, opportunity: MarketOpportunity) -> bool:
        """Add a new market opportunity"""
        try:
            opportunity.updated_at = datetime.now()
            opportunity_dict = opportunity.to_dict()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO market_opportunities (
                        id, name, description, category, market_size, growth_rate,
                        competitive_intensity, investment_needed, roi_potential,
                        risk_level, confidence_score, updated_at, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    opportunity.id,
                    opportunity.name,
                    opportunity.description,
                    opportunity.category.value if opportunity.category else None,
                    opportunity.market_size,
                    opportunity.growth_rate,
                    opportunity.competitive_intensity,
                    opportunity.investment_needed,
                    opportunity.roi_potential,
                    opportunity.risk_level,
                    opportunity.confidence_score,
                    opportunity.updated_at.isoformat(),
                    json.dumps(opportunity_dict)
                ))
                conn.commit()

            self.logger.info(f"Added opportunity: {opportunity.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding opportunity {opportunity.name}: {e}")
            return False

    def get_opportunity(self, opportunity_id: str) -> Optional[MarketOpportunity]:
        """Retrieve a market opportunity by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM market_opportunities WHERE id = ?", (opportunity_id,))
                result = cursor.fetchone()

                if result:
                    opportunity_dict = json.loads(result[0])
                    return self._dict_to_opportunity(opportunity_dict)

        except Exception as e:
            self.logger.error(f"Error retrieving opportunity {opportunity_id}: {e}")

        return None

    # Analysis Score Management
    def add_analysis_score(self, company_name: str, score: AnalysisScore) -> bool:
        """Add or update analysis score for a company"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO analysis_scores (
                        company_name, total_score, investment_grade, recommendation,
                        market_size_score, growth_potential_score, competitive_landscape_score,
                        financial_strength_score, technology_score, team_score, product_score,
                        alignment_score, synergy_potential_score, risk_assessment_score,
                        calculated_at, analyst, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_name, score.total_score, score.investment_grade, score.recommendation,
                    score.market_size_score, score.growth_potential_score, score.competitive_landscape_score,
                    score.financial_strength_score, score.technology_score, score.team_score, score.product_score,
                    score.alignment_score, score.synergy_potential_score, score.risk_assessment_score,
                    score.calculated_at.isoformat(), score.analyst, score.notes
                ))
                conn.commit()

            self.logger.info(f"Added analysis score for: {company_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding analysis score for {company_name}: {e}")
            return False

    # Data Export Functions
    def export_companies_csv(self, filename: Optional[str] = None) -> str:
        """Export companies to CSV format"""
        if not filename:
            filename = f"companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.data_dir / filename

        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT name, website, founded, description, category, target_audience,
                           business_model, funding_stage, total_raised, employees_count,
                           annual_revenue, user_base, headquarters, confidence_score
                    FROM companies
                """
                df = pd.read_sql_query(query, conn)
                df.to_csv(filepath, index=False)

            self.logger.info(f"Exported companies to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error exporting companies: {e}")
            return ""

    def export_opportunities_csv(self, filename: Optional[str] = None) -> str:
        """Export market opportunities to CSV format"""
        if not filename:
            filename = f"opportunities_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.data_dir / filename

        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT id, name, description, category, market_size, growth_rate,
                           competitive_intensity, investment_needed, roi_potential,
                           risk_level, confidence_score
                    FROM market_opportunities
                """
                df = pd.read_sql_query(query, conn)
                df.to_csv(filepath, index=False)

            self.logger.info(f"Exported opportunities to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error exporting opportunities: {e}")
            return ""

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Company statistics
                company_stats = pd.read_sql_query("""
                    SELECT
                        COUNT(*) as total_companies,
                        AVG(total_raised) as avg_funding,
                        SUM(total_raised) as total_funding,
                        AVG(employees_count) as avg_employees,
                        AVG(confidence_score) as avg_confidence
                    FROM companies
                """, conn).iloc[0].to_dict()

                # Category distribution
                category_dist = pd.read_sql_query("""
                    SELECT category, COUNT(*) as count
                    FROM companies
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """, conn).to_dict('records')

                # Funding stage distribution
                funding_dist = pd.read_sql_query("""
                    SELECT funding_stage, COUNT(*) as count
                    FROM companies
                    WHERE funding_stage IS NOT NULL
                    GROUP BY funding_stage
                    ORDER BY count DESC
                """, conn).to_dict('records')

                # Analysis scores distribution
                scores_dist = pd.read_sql_query("""
                    SELECT investment_grade, COUNT(*) as count, AVG(total_score) as avg_score
                    FROM analysis_scores
                    GROUP BY investment_grade
                    ORDER BY avg_score DESC
                """, conn).to_dict('records')

                # Market opportunities summary
                opportunity_stats = pd.read_sql_query("""
                    SELECT
                        COUNT(*) as total_opportunities,
                        AVG(market_size) as avg_market_size,
                        AVG(growth_rate) as avg_growth_rate,
                        AVG(roi_potential) as avg_roi_potential
                    FROM market_opportunities
                """, conn).iloc[0].to_dict()

                return {
                    'company_statistics': company_stats,
                    'category_distribution': category_dist,
                    'funding_distribution': funding_dist,
                    'analysis_scores_distribution': scores_dist,
                    'opportunity_statistics': opportunity_stats,
                    'generated_at': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error generating portfolio summary: {e}")
            return {}

    # Helper methods
    def _dict_to_company(self, data: Dict[str, Any]) -> Optional[CompanyProfile]:
        """Convert dictionary to CompanyProfile object"""
        try:
            # Handle datetime conversion
            if 'created_at' in data and isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            if 'updated_at' in data and isinstance(data['updated_at'], str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])

            # Convert enum strings back to enums
            if 'category' in data and data['category']:
                data['category'] = [EdTechCategory(cat) for cat in data['category']]
            if 'target_audience' in data and data['target_audience']:
                data['target_audience'] = [TargetAudience(aud) for aud in data['target_audience']]
            if 'business_model' in data and data['business_model']:
                data['business_model'] = [BusinessModel(bm) for bm in data['business_model']]

            # Handle funding stage
            if data.get('funding', {}).get('stage'):
                data['funding']['stage'] = FundingStage(data['funding']['stage'])

            # Create CompanyProfile object
            # Note: This is a simplified conversion - full implementation would handle all nested objects
            return CompanyProfile(
                name=data['name'],
                website=data['website'],
                founded=data.get('founded'),
                description=data.get('description', ''),
                # Add other fields as needed
            )

        except Exception as e:
            self.logger.error(f"Error converting dict to CompanyProfile: {e}")
            return None

    def _dict_to_opportunity(self, data: Dict[str, Any]) -> Optional[MarketOpportunity]:
        """Convert dictionary to MarketOpportunity object"""
        try:
            # Handle datetime conversion
            if 'created_at' in data and isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            if 'updated_at' in data and isinstance(data['updated_at'], str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])

            # Convert enum strings back to enums
            if 'category' in data and data['category']:
                data['category'] = EdTechCategory(data['category'])

            # Create MarketOpportunity object
            return MarketOpportunity(
                id=data['id'],
                name=data['name'],
                description=data['description'],
                category=data.get('category'),
                # Add other fields as needed
            )

        except Exception as e:
            self.logger.error(f"Error converting dict to MarketOpportunity: {e}")
            return None