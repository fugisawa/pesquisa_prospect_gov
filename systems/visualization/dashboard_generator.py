"""
EdTech RADAR - Interactive Dashboard Generator
============================================

Creates interactive visualizations and dashboards for EdTech market intelligence.
Supports multiple chart types, real-time updates, and export capabilities.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime
import logging

from systems.models.edtech_schemas import CompanyProfile, MarketOpportunity, AnalysisScore
from systems.data.data_manager import EdTechDataManager


class EdTechDashboardGenerator:
    """Generate interactive dashboards for EdTech market analysis"""

    def __init__(self, data_manager: EdTechDataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)

        # Color schemes for consistent branding
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'gradient': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        }

    def create_portfolio_overview_dashboard(self, companies: List[CompanyProfile],
                                          scores: List[AnalysisScore]) -> go.Figure:
        """Create comprehensive portfolio overview dashboard"""

        # Create subplot structure
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'Investment Grade Distribution', 'Score Distribution', 'Category Performance',
                'Funding Stage Analysis', 'Geographic Distribution', 'Growth vs Risk Matrix',
                'Technology Stack Trends', 'Market Size Analysis', 'Portfolio Timeline'
            ],
            specs=[
                [{'type': 'pie'}, {'type': 'histogram'}, {'type': 'bar'}],
                [{'type': 'bar'}, {'type': 'bar'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'scatter'}, {'type': 'scatter'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # 1. Investment Grade Distribution (Pie Chart)
        grade_counts = {}
        for score in scores:
            grade_counts[score.investment_grade] = grade_counts.get(score.investment_grade, 0) + 1

        fig.add_trace(
            go.Pie(
                labels=list(grade_counts.keys()),
                values=list(grade_counts.values()),
                hole=0.4,
                marker_colors=self.colors['gradient'][:len(grade_counts)]
            ),
            row=1, col=1
        )

        # 2. Score Distribution (Histogram)
        total_scores = [score.total_score for score in scores]
        fig.add_trace(
            go.Histogram(
                x=total_scores,
                nbinsx=20,
                marker_color=self.colors['primary'],
                opacity=0.7
            ),
            row=1, col=2
        )

        # 3. Category Performance (Bar Chart)
        category_scores = self._aggregate_by_category(companies, scores)
        fig.add_trace(
            go.Bar(
                x=list(category_scores.keys()),
                y=[data['avg_score'] for data in category_scores.values()],
                marker_color=self.colors['secondary'],
                text=[f"n={data['count']}" for data in category_scores.values()],
                textposition='auto'
            ),
            row=1, col=3
        )

        # 4. Funding Stage Analysis
        funding_scores = self._aggregate_by_funding_stage(companies, scores)
        fig.add_trace(
            go.Bar(
                x=list(funding_scores.keys()),
                y=[data['avg_score'] for data in funding_scores.values()],
                marker_color=self.colors['success']
            ),
            row=2, col=1
        )

        # 5. Geographic Distribution
        geo_scores = self._aggregate_by_geography(companies, scores)
        fig.add_trace(
            go.Bar(
                x=list(geo_scores.keys())[:10],  # Top 10 locations
                y=[data['avg_score'] for data in list(geo_scores.values())[:10]],
                marker_color=self.colors['info']
            ),
            row=2, col=2
        )

        # 6. Growth vs Risk Matrix (Scatter Plot)
        growth_scores = [score.growth_potential_score for score in scores]
        risk_scores = [score.risk_assessment_score for score in scores]
        company_names = [company.name for company in companies]

        fig.add_trace(
            go.Scatter(
                x=risk_scores,
                y=growth_scores,
                mode='markers',
                marker=dict(
                    size=[score.total_score/5 for score in scores],  # Size by total score
                    color=total_scores,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Total Score")
                ),
                text=company_names,
                hovertemplate='<b>%{text}</b><br>Risk: %{x}<br>Growth: %{y}<extra></extra>'
            ),
            row=2, col=3
        )

        # 7. Technology Stack Trends
        tech_trends = self._analyze_technology_trends(companies)
        fig.add_trace(
            go.Bar(
                x=list(tech_trends.keys())[:10],  # Top 10 technologies
                y=list(tech_trends.values())[:10],
                marker_color=self.colors['warning']
            ),
            row=3, col=1
        )

        # 8. Market Size Analysis
        market_scores = [score.market_size_score for score in scores]
        funding_amounts = [company.funding.total_raised or 0 for company in companies]

        fig.add_trace(
            go.Scatter(
                x=funding_amounts,
                y=market_scores,
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.colors['primary'],
                    opacity=0.6
                ),
                text=company_names,
                hovertemplate='<b>%{text}</b><br>Funding: $%{x:,.0f}<br>Market Score: %{y}<extra></extra>'
            ),
            row=3, col=2
        )

        # 9. Portfolio Timeline
        founded_years = [company.founded for company in companies if company.founded]
        year_counts = {}
        for year in founded_years:
            year_counts[year] = year_counts.get(year, 0) + 1

        sorted_years = sorted(year_counts.items())
        fig.add_trace(
            go.Scatter(
                x=[year for year, count in sorted_years],
                y=[count for year, count in sorted_years],
                mode='lines+markers',
                marker_color=self.colors['secondary'],
                line=dict(width=3)
            ),
            row=3, col=3
        )

        # Update layout
        fig.update_layout(
            title={
                'text': f'EdTech Portfolio Overview Dashboard - {len(companies)} Companies',
                'x': 0.5,
                'font': {'size': 20}
            },
            showlegend=False,
            height=1200,
            width=1400,
            template='plotly_white'
        )

        # Update axis labels
        fig.update_xaxes(title_text="Risk Assessment Score", row=2, col=3)
        fig.update_yaxes(title_text="Growth Potential Score", row=2, col=3)
        fig.update_xaxes(title_text="Total Funding ($)", row=3, col=2)
        fig.update_yaxes(title_text="Market Size Score", row=3, col=2)
        fig.update_xaxes(title_text="Founded Year", row=3, col=3)
        fig.update_yaxes(title_text="Number of Companies", row=3, col=3)

        return fig

    def create_company_detailed_view(self, company: CompanyProfile, score: AnalysisScore) -> go.Figure:
        """Create detailed analysis view for a specific company"""

        # Create radar chart for comprehensive scoring
        categories = [
            'Market Size', 'Growth Potential', 'Competitive Landscape',
            'Financial Strength', 'Technology', 'Team', 'Product',
            'Strategic Alignment', 'Synergy Potential', 'Risk Assessment'
        ]

        values = [
            score.market_size_score, score.growth_potential_score, score.competitive_landscape_score,
            score.financial_strength_score, score.technology_score, score.team_score, score.product_score,
            score.alignment_score, score.synergy_potential_score, score.risk_assessment_score
        ]

        # Close the radar chart
        values += values[:1]
        categories += categories[:1]

        fig = go.Figure()

        # Add radar chart
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=company.name,
            line_color=self.colors['primary'],
            fillcolor=f"rgba(31, 119, 180, 0.3)"
        ))

        # Add industry average (mock data for now)
        industry_avg = [75] * len(categories)  # Mock industry average
        fig.add_trace(go.Scatterpolar(
            r=industry_avg,
            theta=categories,
            fill='toself',
            name='Industry Average',
            line_color=self.colors['secondary'],
            fillcolor=f"rgba(255, 127, 14, 0.2)"
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title={
                'text': f'{company.name} - Detailed Analysis<br>'
                        f'Overall Score: {score.total_score:.1f} | Grade: {score.investment_grade} | '
                        f'Recommendation: {score.recommendation}',
                'x': 0.5,
                'font': {'size': 16}
            },
            showlegend=True,
            height=600,
            width=800
        )

        return fig

    def create_market_opportunity_matrix(self, opportunities: List[MarketOpportunity]) -> go.Figure:
        """Create market opportunity analysis matrix"""

        # Prepare data
        names = [opp.name for opp in opportunities]
        market_sizes = [opp.market_size or 0 for opp in opportunities]
        growth_rates = [opp.growth_rate or 0 for opp in opportunities]
        roi_potentials = [opp.roi_potential or 0 for opp in opportunities]
        risk_levels = [opp.risk_level or 5 for opp in opportunities]

        # Create bubble chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=market_sizes,
            y=growth_rates,
            mode='markers',
            marker=dict(
                size=[roi * 2 for roi in roi_potentials],  # Size by ROI potential
                color=risk_levels,
                colorscale='RdYlGn_r',  # Reverse scale (red=high risk, green=low risk)
                showscale=True,
                colorbar=dict(title="Risk Level"),
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=names,
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Market Size: $%{x:,.0f}<br>'
                'Growth Rate: %{y:.1f}%<br>'
                'ROI Potential: %{marker.size}%<br>'
                'Risk Level: %{marker.color}<br>'
                '<extra></extra>'
            )
        ))

        # Add quadrant lines
        median_market_size = np.median(market_sizes) if market_sizes else 0
        median_growth_rate = np.median(growth_rates) if growth_rates else 0

        fig.add_hline(y=median_growth_rate, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_market_size, line_dash="dash", line_color="gray", opacity=0.5)

        # Add quadrant annotations
        max_market = max(market_sizes) if market_sizes else 1
        max_growth = max(growth_rates) if growth_rates else 1

        annotations = [
            dict(x=max_market * 0.75, y=max_growth * 0.75, text="Star Opportunities", showarrow=False),
            dict(x=max_market * 0.25, y=max_growth * 0.75, text="Question Marks", showarrow=False),
            dict(x=max_market * 0.75, y=max_growth * 0.25, text="Cash Cows", showarrow=False),
            dict(x=max_market * 0.25, y=max_growth * 0.25, text="Dogs", showarrow=False),
        ]

        fig.update_layout(
            title='Market Opportunity Matrix - Size vs Growth vs Risk',
            xaxis_title='Market Size ($)',
            yaxis_title='Growth Rate (%)',
            annotations=annotations,
            height=600,
            width=900,
            template='plotly_white'
        )

        return fig

    def create_competitive_landscape_map(self, companies: List[CompanyProfile]) -> go.Figure:
        """Create competitive landscape visualization"""

        # Prepare data for plotting
        data = []
        for company in companies:
            if company.funding.total_raised and company.metrics.user_base:
                data.append({
                    'name': company.name,
                    'funding': company.funding.total_raised,
                    'users': company.metrics.user_base,
                    'category': company.category[0].value if company.category else 'Unknown',
                    'founded': company.founded or 2020,
                    'employees': company.metrics.employees_count or 0
                })

        if not data:
            # Return empty figure if no data
            return go.Figure().add_annotation(
                text="No data available for competitive landscape",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )

        df = pd.DataFrame(data)

        # Create scatter plot
        fig = px.scatter(
            df,
            x='funding',
            y='users',
            size='employees',
            color='category',
            hover_name='name',
            hover_data=['founded'],
            log_x=True,
            log_y=True,
            size_max=60,
            title='Competitive Landscape - Funding vs User Base'
        )

        fig.update_layout(
            xaxis_title='Total Funding Raised ($)',
            yaxis_title='User Base',
            height=600,
            width=1000
        )

        return fig

    def create_technology_stack_analysis(self, companies: List[CompanyProfile]) -> go.Figure:
        """Analyze and visualize technology stack trends"""

        # Aggregate technology data
        tech_categories = {
            'Frontend': [],
            'Backend': [],
            'Database': [],
            'AI/ML': [],
            'Cloud': [],
            'Mobile': []
        }

        for company in companies:
            tech_stack = company.technology_stack
            tech_categories['Frontend'].extend(tech_stack.frontend)
            tech_categories['Backend'].extend(tech_stack.backend)
            tech_categories['Database'].extend(tech_stack.database)
            tech_categories['AI/ML'].extend(tech_stack.ai_ml)
            tech_categories['Cloud'].extend(tech_stack.cloud_platform)
            tech_categories['Mobile'].extend(tech_stack.mobile)

        # Count occurrences
        tech_counts = {}
        for category, technologies in tech_categories.items():
            counts = {}
            for tech in technologies:
                tech_lower = tech.lower().strip()
                if tech_lower:
                    counts[tech_lower] = counts.get(tech_lower, 0) + 1
            tech_counts[category] = counts

        # Create subplots for each technology category
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=list(tech_categories.keys()),
            specs=[[{'type': 'bar'}] * 3] * 2
        )

        positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]

        for idx, (category, counts) in enumerate(tech_counts.items()):
            if counts and idx < len(positions):
                # Get top 5 technologies for this category
                sorted_tech = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
                technologies, usage_counts = zip(*sorted_tech) if sorted_tech else ([], [])

                row, col = positions[idx]
                fig.add_trace(
                    go.Bar(
                        x=list(technologies),
                        y=list(usage_counts),
                        name=category,
                        marker_color=self.colors['gradient'][idx % len(self.colors['gradient'])],
                        showlegend=False
                    ),
                    row=row, col=col
                )

        fig.update_layout(
            title='Technology Stack Analysis Across Portfolio',
            height=800,
            width=1200,
            template='plotly_white'
        )

        return fig

    def export_dashboard_html(self, fig: go.Figure, filename: str) -> str:
        """Export dashboard as standalone HTML file"""
        filepath = f"systems/exports/{filename}"
        fig.write_html(filepath, include_plotlyjs='cdn')
        self.logger.info(f"Dashboard exported to: {filepath}")
        return filepath

    def export_dashboard_image(self, fig: go.Figure, filename: str, format: str = 'png') -> str:
        """Export dashboard as image file"""
        filepath = f"systems/exports/{filename}.{format}"
        fig.write_image(filepath, format=format, width=1400, height=1000, scale=2)
        self.logger.info(f"Dashboard image exported to: {filepath}")
        return filepath

    # Helper methods for data aggregation

    def _aggregate_by_category(self, companies: List[CompanyProfile],
                             scores: List[AnalysisScore]) -> Dict[str, Dict[str, Any]]:
        """Aggregate scores by company category"""
        category_data = {}

        for company, score in zip(companies, scores):
            for category in company.category:
                cat_name = category.value
                if cat_name not in category_data:
                    category_data[cat_name] = {'scores': [], 'count': 0}

                category_data[cat_name]['scores'].append(score.total_score)
                category_data[cat_name]['count'] += 1

        # Calculate averages
        for cat_name, data in category_data.items():
            data['avg_score'] = np.mean(data['scores'])
            data['max_score'] = max(data['scores'])
            data['min_score'] = min(data['scores'])

        return category_data

    def _aggregate_by_funding_stage(self, companies: List[CompanyProfile],
                                  scores: List[AnalysisScore]) -> Dict[str, Dict[str, Any]]:
        """Aggregate scores by funding stage"""
        stage_data = {}

        for company, score in zip(companies, scores):
            if company.funding.stage:
                stage_name = company.funding.stage.value
                if stage_name not in stage_data:
                    stage_data[stage_name] = {'scores': [], 'count': 0}

                stage_data[stage_name]['scores'].append(score.total_score)
                stage_data[stage_name]['count'] += 1

        # Calculate averages
        for stage_name, data in stage_data.items():
            data['avg_score'] = np.mean(data['scores'])

        return stage_data

    def _aggregate_by_geography(self, companies: List[CompanyProfile],
                              scores: List[AnalysisScore]) -> Dict[str, Dict[str, Any]]:
        """Aggregate scores by geographic location"""
        geo_data = {}

        for company, score in zip(companies, scores):
            if company.geographic_presence.headquarters:
                location = company.geographic_presence.headquarters
                if location not in geo_data:
                    geo_data[location] = {'scores': [], 'count': 0}

                geo_data[location]['scores'].append(score.total_score)
                geo_data[location]['count'] += 1

        # Calculate averages and sort by count
        for location, data in geo_data.items():
            data['avg_score'] = np.mean(data['scores'])

        # Sort by count (descending)
        return dict(sorted(geo_data.items(), key=lambda x: x[1]['count'], reverse=True))

    def _analyze_technology_trends(self, companies: List[CompanyProfile]) -> Dict[str, int]:
        """Analyze technology usage trends across companies"""
        tech_usage = {}

        for company in companies:
            tech_stack = company.technology_stack
            all_tech = (tech_stack.frontend + tech_stack.backend +
                       tech_stack.database + tech_stack.ai_ml +
                       tech_stack.cloud_platform + tech_stack.mobile + tech_stack.other)

            for tech in all_tech:
                tech_lower = tech.lower().strip()
                if tech_lower:
                    tech_usage[tech_lower] = tech_usage.get(tech_lower, 0) + 1

        # Sort by usage count (descending)
        return dict(sorted(tech_usage.items(), key=lambda x: x[1], reverse=True))