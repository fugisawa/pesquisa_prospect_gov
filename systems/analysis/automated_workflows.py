"""
EdTech RADAR - Automated Analysis Workflows
==========================================

Orchestrates automated analysis workflows for EdTech market intelligence.
Handles batch processing, scheduled analysis, and intelligent data pipelines.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum
import schedule
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from systems.models.edtech_schemas import CompanyProfile, MarketOpportunity, AnalysisScore
from systems.data.data_manager import EdTechDataManager
from systems.analysis.scoring_engine import EdTechScoringEngine
from systems.visualization.dashboard_generator import EdTechDashboardGenerator
from systems.exports.report_generator import EdTechReportGenerator


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(Enum):
    """Types of automated analysis"""
    FULL_PORTFOLIO = "full_portfolio"
    COMPANY_SCORING = "company_scoring"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_INTEL = "competitive_intel"
    TREND_ANALYSIS = "trend_analysis"
    RISK_ASSESSMENT = "risk_assessment"


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    analysis_type: AnalysisType
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    artifacts: List[str] = None  # Generated files/reports

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []


class EdTechAnalysisOrchestrator:
    """Orchestrates automated EdTech analysis workflows"""

    def __init__(self, data_manager: EdTechDataManager,
                 scoring_engine: EdTechScoringEngine,
                 dashboard_generator: EdTechDashboardGenerator,
                 report_generator: EdTechReportGenerator):

        self.data_manager = data_manager
        self.scoring_engine = scoring_engine
        self.dashboard_generator = dashboard_generator
        self.report_generator = report_generator

        self.logger = logging.getLogger(__name__)
        self.workflow_results: Dict[str, WorkflowResult] = {}
        self.running_workflows: Dict[str, bool] = {}

        # Workflow configurations
        self.workflow_configs = {
            AnalysisType.FULL_PORTFOLIO: {
                'timeout_minutes': 30,
                'retry_attempts': 3,
                'parallel_processing': True
            },
            AnalysisType.COMPANY_SCORING: {
                'timeout_minutes': 10,
                'retry_attempts': 2,
                'batch_size': 20
            },
            AnalysisType.MARKET_ANALYSIS: {
                'timeout_minutes': 15,
                'retry_attempts': 2,
                'include_forecasting': True
            }
        }

    def execute_full_portfolio_analysis(self, workflow_id: str = None) -> WorkflowResult:
        """Execute comprehensive portfolio analysis workflow"""

        if workflow_id is None:
            workflow_id = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize workflow result
        result = WorkflowResult(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.FULL_PORTFOLIO,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now()
        )

        self.workflow_results[workflow_id] = result
        self.running_workflows[workflow_id] = True

        try:
            self.logger.info(f"Starting full portfolio analysis: {workflow_id}")

            # Step 1: Load all companies and opportunities
            companies = self._load_all_companies()
            opportunities = self._load_all_opportunities()

            if not companies:
                raise ValueError("No companies found for analysis")

            # Step 2: Batch score all companies
            self.logger.info(f"Scoring {len(companies)} companies...")
            scored_companies = self.scoring_engine.batch_score_companies(companies)
            companies, scores = zip(*scored_companies) if scored_companies else ([], [])

            # Step 3: Generate portfolio report
            self.logger.info("Generating portfolio report...")
            portfolio_report = self.scoring_engine.generate_portfolio_report(scored_companies)

            # Step 4: Create executive summary
            self.logger.info("Creating executive summary...")
            executive_summary = self.report_generator.generate_executive_summary(
                list(companies), list(scores), opportunities
            )

            # Step 5: Generate visualizations
            self.logger.info("Creating visualizations...")
            dashboard = self.dashboard_generator.create_portfolio_overview_dashboard(
                list(companies), list(scores)
            )

            # Step 6: Export results
            self.logger.info("Exporting results...")
            artifacts = []

            # Export dashboard
            dashboard_path = self.dashboard_generator.export_dashboard_html(
                dashboard, f"portfolio_dashboard_{workflow_id}"
            )
            artifacts.append(dashboard_path)

            # Export executive summary
            summary_path = self.report_generator.export_to_markdown(
                executive_summary, f"executive_summary_{workflow_id}"
            )
            artifacts.append(summary_path)

            # Export detailed data
            if companies and scores and opportunities:
                excel_path = self.report_generator.export_to_excel(
                    list(companies), list(scores), opportunities,
                    f"portfolio_data_{workflow_id}"
                )
                artifacts.append(excel_path)

            # Export JSON data
            json_path = self.report_generator.export_to_json(
                {
                    'executive_summary': executive_summary,
                    'portfolio_report': portfolio_report,
                    'analysis_metadata': {
                        'companies_analyzed': len(companies),
                        'opportunities_analyzed': len(opportunities),
                        'analysis_date': datetime.now().isoformat(),
                        'workflow_id': workflow_id
                    }
                },
                f"portfolio_analysis_{workflow_id}"
            )
            artifacts.append(json_path)

            # Update result
            result.status = WorkflowStatus.COMPLETED
            result.end_time = datetime.now()
            result.results = {
                'executive_summary': executive_summary,
                'portfolio_report': portfolio_report,
                'companies_analyzed': len(companies),
                'opportunities_analyzed': len(opportunities)
            }
            result.artifacts = artifacts

            self.logger.info(f"Portfolio analysis completed: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = str(e)

        finally:
            self.running_workflows[workflow_id] = False

        return result

    def execute_company_batch_scoring(self, company_names: List[str] = None,
                                    workflow_id: str = None) -> WorkflowResult:
        """Execute batch scoring for specific companies or all companies"""

        if workflow_id is None:
            workflow_id = f"company_scoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = WorkflowResult(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.COMPANY_SCORING,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now()
        )

        self.workflow_results[workflow_id] = result
        self.running_workflows[workflow_id] = True

        try:
            self.logger.info(f"Starting company batch scoring: {workflow_id}")

            # Load companies
            if company_names:
                companies = []
                for name in company_names:
                    company = self.data_manager.get_company(name)
                    if company:
                        companies.append(company)
            else:
                companies = self._load_all_companies()

            if not companies:
                raise ValueError("No companies found for scoring")

            # Batch process companies
            batch_size = self.workflow_configs[AnalysisType.COMPANY_SCORING]['batch_size']
            all_scores = []
            processed_companies = []

            for i in range(0, len(companies), batch_size):
                batch = companies[i:i + batch_size]
                self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(companies)-1)//batch_size + 1}")

                for company in batch:
                    try:
                        score = self.scoring_engine.score_company(company)
                        all_scores.append(score)
                        processed_companies.append(company)

                        # Store score in database
                        self.data_manager.add_analysis_score(company.name, score)

                    except Exception as e:
                        self.logger.error(f"Error scoring company {company.name}: {e}")
                        continue

            # Generate results
            scoring_summary = {
                'total_companies_processed': len(processed_companies),
                'average_score': sum(score.total_score for score in all_scores) / len(all_scores) if all_scores else 0,
                'grade_distribution': {},
                'recommendation_distribution': {},
                'top_performers': []
            }

            # Calculate distributions
            for score in all_scores:
                grade = score.investment_grade
                rec = score.recommendation
                scoring_summary['grade_distribution'][grade] = scoring_summary['grade_distribution'].get(grade, 0) + 1
                scoring_summary['recommendation_distribution'][rec] = scoring_summary['recommendation_distribution'].get(rec, 0) + 1

            # Top performers
            scored_companies = list(zip(processed_companies, all_scores))
            scored_companies.sort(key=lambda x: x[1].total_score, reverse=True)

            scoring_summary['top_performers'] = [
                {
                    'name': company.name,
                    'score': score.total_score,
                    'grade': score.investment_grade,
                    'recommendation': score.recommendation
                }
                for company, score in scored_companies[:10]
            ]

            result.status = WorkflowStatus.COMPLETED
            result.end_time = datetime.now()
            result.results = scoring_summary

            self.logger.info(f"Company batch scoring completed: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Company batch scoring failed: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = str(e)

        finally:
            self.running_workflows[workflow_id] = False

        return result

    def execute_market_analysis_workflow(self, workflow_id: str = None) -> WorkflowResult:
        """Execute comprehensive market analysis workflow"""

        if workflow_id is None:
            workflow_id = f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = WorkflowResult(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.MARKET_ANALYSIS,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now()
        )

        self.workflow_results[workflow_id] = result
        self.running_workflows[workflow_id] = True

        try:
            self.logger.info(f"Starting market analysis: {workflow_id}")

            # Load market opportunities
            opportunities = self._load_all_opportunities()

            if not opportunities:
                raise ValueError("No market opportunities found for analysis")

            # Generate market analysis report
            market_report = self.report_generator.generate_market_analysis_report(opportunities)

            # Create market visualizations
            market_matrix = self.dashboard_generator.create_market_opportunity_matrix(opportunities)

            # Export artifacts
            artifacts = []

            # Export market dashboard
            market_dashboard_path = self.dashboard_generator.export_dashboard_html(
                market_matrix, f"market_analysis_{workflow_id}"
            )
            artifacts.append(market_dashboard_path)

            # Export market report
            market_report_path = self.report_generator.export_to_markdown(
                market_report, f"market_report_{workflow_id}"
            )
            artifacts.append(market_report_path)

            # Export JSON data
            json_path = self.report_generator.export_to_json(
                market_report, f"market_analysis_{workflow_id}"
            )
            artifacts.append(json_path)

            result.status = WorkflowStatus.COMPLETED
            result.end_time = datetime.now()
            result.results = market_report
            result.artifacts = artifacts

            self.logger.info(f"Market analysis completed: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = str(e)

        finally:
            self.running_workflows[workflow_id] = False

        return result

    def execute_competitive_intelligence_workflow(self, workflow_id: str = None) -> WorkflowResult:
        """Execute competitive intelligence analysis workflow"""

        if workflow_id is None:
            workflow_id = f"competitive_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = WorkflowResult(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.COMPETITIVE_INTEL,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now()
        )

        self.workflow_results[workflow_id] = result
        self.running_workflows[workflow_id] = True

        try:
            self.logger.info(f"Starting competitive intelligence analysis: {workflow_id}")

            # Load all companies
            companies = self._load_all_companies()

            if not companies:
                raise ValueError("No companies found for competitive analysis")

            # Generate competitive landscape
            competitive_map = self.dashboard_generator.create_competitive_landscape_map(companies)

            # Technology stack analysis
            tech_analysis = self.dashboard_generator.create_technology_stack_analysis(companies)

            # Competitive intelligence summary
            competitive_intel = self._generate_competitive_intelligence_summary(companies)

            # Export artifacts
            artifacts = []

            # Export competitive landscape
            comp_landscape_path = self.dashboard_generator.export_dashboard_html(
                competitive_map, f"competitive_landscape_{workflow_id}"
            )
            artifacts.append(comp_landscape_path)

            # Export technology analysis
            tech_analysis_path = self.dashboard_generator.export_dashboard_html(
                tech_analysis, f"technology_analysis_{workflow_id}"
            )
            artifacts.append(tech_analysis_path)

            # Export competitive intelligence report
            intel_report_path = self.report_generator.export_to_json(
                competitive_intel, f"competitive_intel_{workflow_id}"
            )
            artifacts.append(intel_report_path)

            result.status = WorkflowStatus.COMPLETED
            result.end_time = datetime.now()
            result.results = competitive_intel
            result.artifacts = artifacts

            self.logger.info(f"Competitive intelligence analysis completed: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Competitive intelligence analysis failed: {e}")
            result.status = WorkflowStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = str(e)

        finally:
            self.running_workflows[workflow_id] = False

        return result

    def schedule_automated_workflows(self):
        """Set up scheduled automated workflows"""

        self.logger.info("Setting up automated workflow schedules...")

        # Daily portfolio scoring
        schedule.every().day.at("06:00").do(
            self._run_scheduled_workflow,
            AnalysisType.COMPANY_SCORING,
            "daily_scoring"
        )

        # Weekly full portfolio analysis
        schedule.every().monday.at("08:00").do(
            self._run_scheduled_workflow,
            AnalysisType.FULL_PORTFOLIO,
            "weekly_portfolio"
        )

        # Monthly market analysis
        schedule.every().month.do(
            self._run_scheduled_workflow,
            AnalysisType.MARKET_ANALYSIS,
            "monthly_market"
        )

        # Monthly competitive intelligence
        schedule.every().month.do(
            self._run_scheduled_workflow,
            AnalysisType.COMPETITIVE_INTEL,
            "monthly_competitive"
        )

        self.logger.info("Automated workflow schedules configured")

    def run_scheduler(self):
        """Run the workflow scheduler (blocking operation)"""
        self.logger.info("Starting workflow scheduler...")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Get the status of a specific workflow"""
        return self.workflow_results.get(workflow_id)

    def list_active_workflows(self) -> List[str]:
        """List all currently running workflows"""
        return [wf_id for wf_id, running in self.running_workflows.items() if running]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self.running_workflows and self.running_workflows[workflow_id]:
            self.running_workflows[workflow_id] = False
            if workflow_id in self.workflow_results:
                self.workflow_results[workflow_id].status = WorkflowStatus.CANCELLED
                self.workflow_results[workflow_id].end_time = datetime.now()
            self.logger.info(f"Workflow cancelled: {workflow_id}")
            return True
        return False

    def cleanup_old_workflows(self, days_old: int = 30):
        """Clean up workflow results older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        to_remove = []
        for workflow_id, result in self.workflow_results.items():
            if result.start_time < cutoff_date:
                to_remove.append(workflow_id)

        for workflow_id in to_remove:
            del self.workflow_results[workflow_id]
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]

        self.logger.info(f"Cleaned up {len(to_remove)} old workflow results")

    # Private helper methods

    def _load_all_companies(self) -> List[CompanyProfile]:
        """Load all companies from the database"""
        try:
            # This would implement the actual data loading logic
            # For now, returning an empty list as a placeholder
            companies = self.data_manager.search_companies()
            return companies
        except Exception as e:
            self.logger.error(f"Error loading companies: {e}")
            return []

    def _load_all_opportunities(self) -> List[MarketOpportunity]:
        """Load all market opportunities from the database"""
        try:
            # This would implement the actual data loading logic
            # For now, returning an empty list as a placeholder
            return []
        except Exception as e:
            self.logger.error(f"Error loading opportunities: {e}")
            return []

    def _run_scheduled_workflow(self, analysis_type: AnalysisType, workflow_prefix: str):
        """Execute a scheduled workflow"""
        workflow_id = f"{workflow_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            if analysis_type == AnalysisType.FULL_PORTFOLIO:
                self.execute_full_portfolio_analysis(workflow_id)
            elif analysis_type == AnalysisType.COMPANY_SCORING:
                self.execute_company_batch_scoring(workflow_id=workflow_id)
            elif analysis_type == AnalysisType.MARKET_ANALYSIS:
                self.execute_market_analysis_workflow(workflow_id)
            elif analysis_type == AnalysisType.COMPETITIVE_INTEL:
                self.execute_competitive_intelligence_workflow(workflow_id)

        except Exception as e:
            self.logger.error(f"Scheduled workflow failed: {workflow_id}, Error: {e}")

    def _generate_competitive_intelligence_summary(self, companies: List[CompanyProfile]) -> Dict[str, Any]:
        """Generate competitive intelligence summary"""

        # Competitive landscape analysis
        competitor_networks = {}
        technology_trends = {}
        market_positioning = {}

        for company in companies:
            # Analyze competitor networks
            for competitor in company.competitors:
                if competitor not in competitor_networks:
                    competitor_networks[competitor] = []
                competitor_networks[competitor].append(company.name)

            # Track technology trends
            all_tech = (company.technology_stack.frontend +
                       company.technology_stack.backend +
                       company.technology_stack.ai_ml +
                       company.technology_stack.cloud_platform)

            for tech in all_tech:
                tech_lower = tech.lower().strip()
                if tech_lower:
                    technology_trends[tech_lower] = technology_trends.get(tech_lower, 0) + 1

            # Market positioning analysis
            for category in company.category:
                cat_name = category.value
                if cat_name not in market_positioning:
                    market_positioning[cat_name] = {
                        'companies': [],
                        'total_funding': 0,
                        'total_users': 0
                    }

                market_positioning[cat_name]['companies'].append(company.name)
                market_positioning[cat_name]['total_funding'] += company.funding.total_raised or 0
                market_positioning[cat_name]['total_users'] += company.metrics.user_base or 0

        # Top competitors (most mentioned)
        top_competitors = sorted(competitor_networks.items(), key=lambda x: len(x[1]), reverse=True)[:10]

        # Top technologies
        top_technologies = sorted(technology_trends.items(), key=lambda x: x[1], reverse=True)[:15]

        # Market segment leaders
        segment_leaders = {}
        for category, data in market_positioning.items():
            segment_leaders[category] = {
                'company_count': len(data['companies']),
                'total_funding': data['total_funding'],
                'total_users': data['total_users'],
                'avg_funding_per_company': data['total_funding'] / len(data['companies']) if data['companies'] else 0
            }

        return {
            'analysis_date': datetime.now().isoformat(),
            'total_companies_analyzed': len(companies),
            'competitive_landscape': {
                'top_competitors': [{'name': name, 'mentioned_by': competitors} for name, competitors in top_competitors],
                'network_density': len(competitor_networks),
                'average_competitors_per_company': sum(len(company.competitors) for company in companies) / len(companies) if companies else 0
            },
            'technology_intelligence': {
                'top_technologies': [{'technology': tech, 'adoption_count': count} for tech, count in top_technologies],
                'technology_diversity': len(technology_trends),
                'ai_adoption_rate': sum(1 for company in companies if company.technology_stack.ai_ml) / len(companies) * 100 if companies else 0
            },
            'market_positioning': segment_leaders,
            'key_insights': self._generate_competitive_insights(companies, competitor_networks, technology_trends)
        }

    def _generate_competitive_insights(self, companies: List[CompanyProfile],
                                     competitor_networks: Dict[str, List[str]],
                                     technology_trends: Dict[str, int]) -> List[str]:
        """Generate competitive intelligence insights"""

        insights = []

        # Market concentration insights
        if competitor_networks:
            most_mentioned = max(competitor_networks.items(), key=lambda x: len(x[1]))
            insights.append(f"{most_mentioned[0]} is the most frequently cited competitor, mentioned by {len(most_mentioned[1])} companies")

        # Technology adoption insights
        if technology_trends:
            top_tech = max(technology_trends.items(), key=lambda x: x[1])
            insights.append(f"{top_tech[0]} is the most adopted technology with {top_tech[1]} companies using it")

        # AI adoption insights
        ai_companies = sum(1 for company in companies if company.technology_stack.ai_ml)
        ai_rate = (ai_companies / len(companies) * 100) if companies else 0
        insights.append(f"{ai_rate:.1f}% of companies have adopted AI/ML technologies")

        # Funding concentration insights
        total_funding = sum(company.funding.total_raised or 0 for company in companies)
        if total_funding > 0:
            top_funded = max(companies, key=lambda x: x.funding.total_raised or 0)
            top_funding_pct = ((top_funded.funding.total_raised or 0) / total_funding * 100)
            insights.append(f"{top_funded.name} represents {top_funding_pct:.1f}% of total portfolio funding")

        return insights