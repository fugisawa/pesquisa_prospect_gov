#!/usr/bin/env python3
"""
Risk Monitoring Dashboard
Real-time visualization and KRI tracking for strategic risk management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KRIType(Enum):
    BIG_TECH_THREAT_SCORE = "Big Tech Threat Score"
    REGULATORY_STABILITY_INDEX = "Regulatory Stability Index"
    MARKET_CONCENTRATION_RATIO = "Market Concentration Ratio"
    COMPETITIVE_PRESSURE_INDEX = "Competitive Pressure Index"
    PORTFOLIO_DIVERSIFICATION_SCORE = "Portfolio Diversification Score"
    CUSTOMER_CONCENTRATION_RISK = "Customer Concentration Risk"
    FINANCIAL_STABILITY_SCORE = "Financial Stability Score"
    OPERATIONAL_RISK_INDEX = "Operational Risk Index"

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

@dataclass
class KRIMetric:
    metric_type: KRIType
    current_value: float
    target_value: float
    threshold_high: float
    threshold_critical: float
    trend_direction: str  # "up", "down", "stable"
    last_updated: datetime
    historical_data: List[Tuple[datetime, float]]
    risk_level: RiskLevel
    description: str

@dataclass
class DashboardData:
    kri_metrics: Dict[KRIType, KRIMetric]
    threat_radar: Dict[str, float]
    portfolio_allocation: Dict[str, float]
    recent_alerts: List[Dict[str, Any]]
    scenario_impacts: Dict[str, float]
    compliance_status: Dict[str, Any]
    competitive_intelligence: List[Dict[str, Any]]
    last_updated: datetime

class RiskDashboard:
    def __init__(self, config_path: str = "/home/danielfugisawa/pesquisa_prospect_gov/config/risk-monitoring/dashboard-config.json"):
        self.config_path = Path(config_path)
        self.dashboard_data: Optional[DashboardData] = None
        self.app: Optional[Dash] = None
        self.load_config()
        self._initialize_kri_metrics()
        self._setup_dashboard()
    
    def load_config(self):
        """Load dashboard configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default dashboard configuration"""
        return {
            "kri_thresholds": {
                "big_tech_threat_score": {"high": 70, "critical": 85, "target": 40},
                "regulatory_stability_index": {"high": 60, "critical": 40, "target": 80},
                "market_concentration_ratio": {"high": 0.6, "critical": 0.8, "target": 0.4},
                "competitive_pressure_index": {"high": 75, "critical": 90, "target": 50},
                "portfolio_diversification_score": {"high": 40, "critical": 25, "target": 75},
                "customer_concentration_risk": {"high": 0.4, "critical": 0.6, "target": 0.25},
                "financial_stability_score": {"high": 60, "critical": 40, "target": 85},
                "operational_risk_index": {"high": 65, "critical": 80, "target": 30}
            },
            "refresh_intervals": {
                "real_time_metrics": 30,  # seconds
                "threat_intelligence": 300,  # 5 minutes
                "portfolio_data": 3600,  # 1 hour
                "compliance_data": 7200  # 2 hours
            },
            "visualization_settings": {
                "color_scheme": {
                    "low": "#28a745",
                    "medium": "#ffc107",
                    "high": "#fd7e14",
                    "critical": "#dc3545"
                },
                "chart_height": 400,
                "animation_duration": 1000
            },
            "alert_settings": {
                "show_last_n_alerts": 10,
                "auto_refresh_alerts": True,
                "alert_sound_enabled": False
            }
        }
    
    def save_config(self):
        """Save dashboard configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _initialize_kri_metrics(self):
        """Initialize KRI metrics with default values"""
        now = datetime.now()
        
        # Generate sample historical data
        def generate_historical_data(base_value: float, days: int = 30) -> List[Tuple[datetime, float]]:
            data = []
            for i in range(days):
                date = now - timedelta(days=days-i)
                # Add some random variation
                variation = np.random.normal(0, base_value * 0.1)
                value = max(0, min(100, base_value + variation))
                data.append((date, value))
            return data
        
        self.kri_metrics = {
            KRIType.BIG_TECH_THREAT_SCORE: KRIMetric(
                metric_type=KRIType.BIG_TECH_THREAT_SCORE,
                current_value=65.0,
                target_value=40.0,
                threshold_high=70.0,
                threshold_critical=85.0,
                trend_direction="up",
                last_updated=now,
                historical_data=generate_historical_data(65.0),
                risk_level=RiskLevel.MEDIUM,
                description="Aggregated threat score from Google, Microsoft, Amazon, Meta, and Apple activities"
            ),
            KRIType.REGULATORY_STABILITY_INDEX: KRIMetric(
                metric_type=KRIType.REGULATORY_STABILITY_INDEX,
                current_value=72.0,
                target_value=80.0,
                threshold_high=60.0,
                threshold_critical=40.0,
                trend_direction="stable",
                last_updated=now,
                historical_data=generate_historical_data(72.0),
                risk_level=RiskLevel.LOW,
                description="Stability of regulatory environment for EdTech and government contracts"
            ),
            KRIType.MARKET_CONCENTRATION_RATIO: KRIMetric(
                metric_type=KRIType.MARKET_CONCENTRATION_RATIO,
                current_value=0.55,
                target_value=0.40,
                threshold_high=0.60,
                threshold_critical=0.80,
                trend_direction="down",
                last_updated=now,
                historical_data=[(date, value/100) for date, value in generate_historical_data(55.0)],
                risk_level=RiskLevel.MEDIUM,
                description="Herfindahl-Hirschman Index measuring market concentration risk"
            ),
            KRIType.COMPETITIVE_PRESSURE_INDEX: KRIMetric(
                metric_type=KRIType.COMPETITIVE_PRESSURE_INDEX,
                current_value=68.0,
                target_value=50.0,
                threshold_high=75.0,
                threshold_critical=90.0,
                trend_direction="up",
                last_updated=now,
                historical_data=generate_historical_data(68.0),
                risk_level=RiskLevel.MEDIUM,
                description="Pressure from existing competitors and new market entrants"
            ),
            KRIType.PORTFOLIO_DIVERSIFICATION_SCORE: KRIMetric(
                metric_type=KRIType.PORTFOLIO_DIVERSIFICATION_SCORE,
                current_value=58.0,
                target_value=75.0,
                threshold_high=40.0,
                threshold_critical=25.0,
                trend_direction="up",
                last_updated=now,
                historical_data=generate_historical_data(58.0),
                risk_level=RiskLevel.MEDIUM,
                description="Diversification across market segments, geographies, and customer types"
            ),
            KRIType.CUSTOMER_CONCENTRATION_RISK: KRIMetric(
                metric_type=KRIType.CUSTOMER_CONCENTRATION_RISK,
                current_value=0.35,
                target_value=0.25,
                threshold_high=0.40,
                threshold_critical=0.60,
                trend_direction="stable",
                last_updated=now,
                historical_data=[(date, value/100) for date, value in generate_historical_data(35.0)],
                risk_level=RiskLevel.LOW,
                description="Risk from dependence on small number of large customers"
            ),
            KRIType.FINANCIAL_STABILITY_SCORE: KRIMetric(
                metric_type=KRIType.FINANCIAL_STABILITY_SCORE,
                current_value=78.0,
                target_value=85.0,
                threshold_high=60.0,
                threshold_critical=40.0,
                trend_direction="stable",
                last_updated=now,
                historical_data=generate_historical_data(78.0),
                risk_level=RiskLevel.LOW,
                description="Overall financial health and stability metrics"
            ),
            KRIType.OPERATIONAL_RISK_INDEX: KRIMetric(
                metric_type=KRIType.OPERATIONAL_RISK_INDEX,
                current_value=42.0,
                target_value=30.0,
                threshold_high=65.0,
                threshold_critical=80.0,
                trend_direction="down",
                last_updated=now,
                historical_data=generate_historical_data(42.0),
                risk_level=RiskLevel.LOW,
                description="Operational risks including technology, processes, and human resources"
            )
        }
    
    def _setup_dashboard(self):
        """Setup Dash application"""
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            title="Risk Monitoring Dashboard"
        )
        
        # Define layout
        self.app.layout = self._create_layout()
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _create_layout(self) -> html.Div:
        """Create dashboard layout"""
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🚨 Risk Monitoring Dashboard", className="text-center mb-4"),
                    html.P(
                        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        className="text-center text-muted",
                        id="last-updated"
                    )
                ])
            ]),
            
            # KRI Summary Cards
            dbc.Row([
                dbc.Col([
                    html.H3("📊 Key Risk Indicators (KRIs)", className="mb-3"),
                    html.Div(id="kri-cards")
                ], width=12)
            ], className="mb-4"),
            
            # Main Dashboard Row
            dbc.Row([
                # Threat Radar Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("🎯 Threat Radar", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(id="threat-radar-chart")
                        ])
                    ])
                ], width=6),
                
                # Portfolio Allocation
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("💼 Portfolio Allocation", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(id="portfolio-allocation-chart")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # KRI Trends and Alerts Row
            dbc.Row([
                # KRI Trends
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("📈 KRI Trends", className="mb-0")),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="kri-selector",
                                options=[
                                    {"label": kri.value, "value": kri.name} 
                                    for kri in KRIType
                                ],
                                value=KRIType.BIG_TECH_THREAT_SCORE.name,
                                className="mb-3"
                            ),
                            dcc.Graph(id="kri-trend-chart")
                        ])
                    ])
                ], width=8),
                
                # Recent Alerts
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("🚨 Recent Alerts", className="mb-0")),
                        dbc.CardBody([
                            html.Div(id="recent-alerts-list")
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Scenario Analysis and Compliance Status
            dbc.Row([
                # Scenario Impact Analysis
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("🎭 Scenario Impact Analysis", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(id="scenario-impact-chart")
                        ])
                    ])
                ], width=6),
                
                # Compliance Status
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("⚖️ Compliance Status", className="mb-0")),
                        dbc.CardBody([
                            html.Div(id="compliance-status")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # Auto-refresh interval
            dcc.Interval(
                id="interval-component",
                interval=30*1000,  # 30 seconds
                n_intervals=0
            )
            
        ], fluid=True)
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [
                Output("kri-cards", "children"),
                Output("threat-radar-chart", "figure"),
                Output("portfolio-allocation-chart", "figure"),
                Output("recent-alerts-list", "children"),
                Output("scenario-impact-chart", "figure"),
                Output("compliance-status", "children"),
                Output("last-updated", "children")
            ],
            [Input("interval-component", "n_intervals")]
        )
        def update_dashboard(n):
            """Update all dashboard components"""
            # Update data
            self._update_dashboard_data()
            
            # Generate components
            kri_cards = self._create_kri_cards()
            threat_radar = self._create_threat_radar_chart()
            portfolio_chart = self._create_portfolio_allocation_chart()
            alerts_list = self._create_recent_alerts_list()
            scenario_chart = self._create_scenario_impact_chart()
            compliance_status = self._create_compliance_status()
            
            last_updated = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return (kri_cards, threat_radar, portfolio_chart, alerts_list, 
                   scenario_chart, compliance_status, last_updated)
        
        @self.app.callback(
            Output("kri-trend-chart", "figure"),
            [
                Input("kri-selector", "value"),
                Input("interval-component", "n_intervals")
            ]
        )
        def update_kri_trend(selected_kri, n):
            """Update KRI trend chart"""
            return self._create_kri_trend_chart(selected_kri)
    
    def _update_dashboard_data(self):
        """Update dashboard data from various sources"""
        # In a real implementation, this would fetch data from:
        # - BigTechMonitor
        # - RegulatoryMonitor
        # - PortfolioDiversificationEngine
        # - EarlyWarningSystem
        
        # For now, simulate data updates
        now = datetime.now()
        
        # Update KRI values with small random changes
        for kri_type, metric in self.kri_metrics.items():
            # Simulate small changes
            change = np.random.normal(0, 2.0)
            new_value = max(0, min(100, metric.current_value + change))
            
            # For ratio metrics, keep in 0-1 range
            if "ratio" in kri_type.value.lower() or "concentration" in kri_type.value.lower():
                new_value = max(0, min(1, metric.current_value + change/100))
            
            metric.current_value = new_value
            metric.last_updated = now
            
            # Update historical data
            metric.historical_data.append((now, new_value))
            if len(metric.historical_data) > 100:  # Keep last 100 points
                metric.historical_data = metric.historical_data[-100:]
            
            # Update risk level based on thresholds
            if new_value >= metric.threshold_critical:
                metric.risk_level = RiskLevel.CRITICAL
            elif new_value >= metric.threshold_high:
                metric.risk_level = RiskLevel.HIGH
            elif abs(new_value - metric.target_value) <= 10:
                metric.risk_level = RiskLevel.LOW
            else:
                metric.risk_level = RiskLevel.MEDIUM
        
        # Update dashboard data object
        self.dashboard_data = DashboardData(
            kri_metrics=self.kri_metrics,
            threat_radar=self._generate_threat_radar_data(),
            portfolio_allocation=self._generate_portfolio_data(),
            recent_alerts=self._generate_recent_alerts(),
            scenario_impacts=self._generate_scenario_impacts(),
            compliance_status=self._generate_compliance_status(),
            competitive_intelligence=self._generate_competitive_intelligence(),
            last_updated=now
        )
    
    def _generate_threat_radar_data(self) -> Dict[str, float]:
        """Generate threat radar data"""
        return {
            "Google": 75,
            "Microsoft": 65,
            "Amazon": 55,
            "Meta": 45,
            "Apple": 35,
            "Local Competitors": 60,
            "Regulatory Risk": 70,
            "Economic Risk": 50
        }
    
    def _generate_portfolio_data(self) -> Dict[str, float]:
        """Generate portfolio allocation data"""
        return {
            "Government B2B": 60,
            "Corporate Training": 15,
            "Higher Education": 15,
            "International Markets": 5,
            "Consumer B2C": 5
        }
    
    def _generate_recent_alerts(self) -> List[Dict[str, Any]]:
        """Generate recent alerts data"""
        return [
            {
                "id": "ALERT_001",
                "severity": "Orange",
                "category": "Big Tech Threat",
                "message": "Google announces education partnership in São Paulo",
                "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%H:%M")
            },
            {
                "id": "ALERT_002",
                "severity": "Yellow",
                "category": "Regulatory Change",
                "message": "New LGPD interpretation published",
                "timestamp": (datetime.now() - timedelta(hours=6)).strftime("%H:%M")
            },
            {
                "id": "ALERT_003",
                "severity": "Yellow",
                "category": "Competitive Threat",
                "message": "Competitor raises $25M funding round",
                "timestamp": (datetime.now() - timedelta(hours=12)).strftime("%H:%M")
            }
        ]
    
    def _generate_scenario_impacts(self) -> Dict[str, float]:
        """Generate scenario impact data"""
        return {
            "Big Tech Entry": -25,
            "Economic Downturn": -30,
            "Regulatory Change": -15,
            "Tech Disruption": -20,
            "Market Expansion": +35
        }
    
    def _generate_compliance_status(self) -> Dict[str, Any]:
        """Generate compliance status data"""
        return {
            "overall_score": 78,
            "lgpd_compliance": 85,
            "procurement_compliance": 75,
            "security_compliance": 80,
            "accessibility_compliance": 70,
            "gaps_count": 3,
            "critical_gaps": 1
        }
    
    def _generate_competitive_intelligence(self) -> List[Dict[str, Any]]:
        """Generate competitive intelligence data"""
        return [
            {"company": "Competitor A", "threat_level": "High", "activity": "New product launch"},
            {"company": "Competitor B", "threat_level": "Medium", "activity": "Partnership announced"},
            {"company": "Big Tech Co", "threat_level": "Critical", "activity": "Market entry rumors"}
        ]
    
    def _create_kri_cards(self) -> List[dbc.Card]:
        """Create KRI summary cards"""
        cards = []
        
        for kri_type, metric in self.kri_metrics.items():
            # Determine card color based on risk level
            color_map = {
                RiskLevel.LOW: "success",
                RiskLevel.MEDIUM: "warning",
                RiskLevel.HIGH: "danger",
                RiskLevel.CRITICAL: "danger"
            }
            
            # Trend icon
            trend_icons = {
                "up": "fa-arrow-up",
                "down": "fa-arrow-down",
                "stable": "fa-minus"
            }
            
            # Format value based on metric type
            if "ratio" in kri_type.value.lower() or "concentration" in kri_type.value.lower():
                value_display = f"{metric.current_value:.1%}"
                target_display = f"{metric.target_value:.1%}"
            else:
                value_display = f"{metric.current_value:.1f}"
                target_display = f"{metric.target_value:.1f}"
            
            card = dbc.Card([
                dbc.CardBody([
                    html.H6(kri_type.value, className="card-title"),
                    html.H4([
                        value_display,
                        html.I(
                            className=f"fas {trend_icons.get(metric.trend_direction, 'fa-minus')} ms-2",
                            style={"color": "gray" if metric.trend_direction == "stable" else 
                                   "red" if metric.trend_direction == "up" and metric.current_value > metric.target_value else "green"}
                        )
                    ], className="card-text"),
                    html.Small(f"Target: {target_display}", className="text-muted"),
                    html.Br(),
                    dbc.Badge(
                        metric.risk_level.value,
                        color=color_map[metric.risk_level],
                        className="mt-2"
                    )
                ])
            ], color=color_map[metric.risk_level], outline=True, className="mb-3")
            
            cards.append(card)
        
        # Arrange cards in rows
        card_rows = []
        for i in range(0, len(cards), 4):
            row_cards = cards[i:i+4]
            card_rows.append(
                dbc.Row([
                    dbc.Col(card, width=3) for card in row_cards
                ], className="mb-3")
            )
        
        return card_rows
    
    def _create_threat_radar_chart(self) -> go.Figure:
        """Create threat radar chart"""
        if not self.dashboard_data:
            return go.Figure()
        
        threat_data = self.dashboard_data.threat_radar
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(threat_data.values()),
            theta=list(threat_data.keys()),
            fill='toself',
            name='Threat Level',
            line=dict(color='red', width=2),
            fillcolor='rgba(255, 0, 0, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickmode='linear',
                    tick0=0,
                    dtick=20
                )
            ),
            showlegend=False,
            title=dict(
                text="Threat Assessment by Source",
                x=0.5,
                font=dict(size=16)
            ),
            height=400
        )
        
        return fig
    
    def _create_portfolio_allocation_chart(self) -> go.Figure:
        """Create portfolio allocation chart"""
        if not self.dashboard_data:
            return go.Figure()
        
        portfolio_data = self.dashboard_data.portfolio_allocation
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        
        fig = go.Figure(data=[go.Pie(
            labels=list(portfolio_data.keys()),
            values=list(portfolio_data.values()),
            hole=0.3,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title=dict(
                text="Current Portfolio Allocation (%)",
                x=0.5,
                font=dict(size=16)
            ),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        return fig
    
    def _create_kri_trend_chart(self, selected_kri: str) -> go.Figure:
        """Create KRI trend chart"""
        if not selected_kri or selected_kri not in [kri.name for kri in KRIType]:
            return go.Figure()
        
        kri_type = KRIType[selected_kri]
        metric = self.kri_metrics[kri_type]
        
        # Prepare data
        dates = [point[0] for point in metric.historical_data]
        values = [point[1] for point in metric.historical_data]
        
        fig = go.Figure()
        
        # Add main trend line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Current Value',
            line=dict(color='blue', width=2),
            marker=dict(size=4)
        ))
        
        # Add target line
        fig.add_hline(
            y=metric.target_value,
            line_dash="dash",
            line_color="green",
            annotation_text="Target",
            annotation_position="right"
        )
        
        # Add threshold lines
        fig.add_hline(
            y=metric.threshold_high,
            line_dash="dot",
            line_color="orange",
            annotation_text="High Threshold",
            annotation_position="right"
        )
        
        fig.add_hline(
            y=metric.threshold_critical,
            line_dash="dot",
            line_color="red",
            annotation_text="Critical Threshold",
            annotation_position="right"
        )
        
        # Format y-axis for ratio metrics
        if "ratio" in kri_type.value.lower() or "concentration" in kri_type.value.lower():
            fig.update_yaxis(tickformat=".1%")
        
        fig.update_layout(
            title=dict(
                text=f"{kri_type.value} - Last 30 Days",
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def _create_recent_alerts_list(self) -> List[html.Div]:
        """Create recent alerts list"""
        if not self.dashboard_data:
            return [html.P("No alerts available", className="text-muted")]
        
        alerts = self.dashboard_data.recent_alerts
        
        if not alerts:
            return [html.P("No recent alerts", className="text-muted")]
        
        alert_items = []
        
        for alert in alerts[:5]:  # Show last 5 alerts
            severity_colors = {
                "Red": "danger",
                "Orange": "warning",
                "Yellow": "info",
                "Green": "success"
            }
            
            severity_icons = {
                "Red": "fa-exclamation-triangle",
                "Orange": "fa-exclamation-circle",
                "Yellow": "fa-info-circle",
                "Green": "fa-check-circle"
            }
            
            alert_item = dbc.Alert([
                html.Div([
                    html.I(className=f"fas {severity_icons.get(alert['severity'], 'fa-bell')} me-2"),
                    html.Strong(alert['category']),
                    html.Br(),
                    html.Small(alert['message'], className="text-wrap"),
                    html.Br(),
                    html.Small(f"Time: {alert['timestamp']}", className="text-muted")
                ])
            ], color=severity_colors.get(alert['severity'], 'info'), className="py-2")
            
            alert_items.append(alert_item)
        
        return alert_items
    
    def _create_scenario_impact_chart(self) -> go.Figure:
        """Create scenario impact analysis chart"""
        if not self.dashboard_data:
            return go.Figure()
        
        scenario_data = self.dashboard_data.scenario_impacts
        
        scenarios = list(scenario_data.keys())
        impacts = list(scenario_data.values())
        
        # Color code positive vs negative impacts
        colors = ['green' if impact > 0 else 'red' for impact in impacts]
        
        fig = go.Figure(data=[go.Bar(
            x=scenarios,
            y=impacts,
            marker_color=colors,
            text=[f"{impact:+.0f}%" for impact in impacts],
            textposition='auto',
        )])
        
        fig.update_layout(
            title=dict(
                text="Scenario Impact Analysis (% Revenue Impact)",
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title="Scenario",
            yaxis_title="Revenue Impact (%)",
            height=400,
            xaxis=dict(tickangle=45)
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
        
        return fig
    
    def _create_compliance_status(self) -> List[html.Div]:
        """Create compliance status display"""
        if not self.dashboard_data:
            return [html.P("No compliance data available", className="text-muted")]
        
        compliance = self.dashboard_data.compliance_status
        
        # Overall score
        overall_score = compliance.get('overall_score', 0)
        score_color = "success" if overall_score >= 80 else "warning" if overall_score >= 60 else "danger"
        
        components = [
            # Overall score
            dbc.Row([
                dbc.Col([
                    html.H4(f"{overall_score}%", className="text-center"),
                    html.P("Overall Compliance Score", className="text-center text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Individual compliance areas
            html.H6("Compliance Areas:", className="mb-2"),
        ]
        
        compliance_areas = {
            "LGPD Compliance": compliance.get('lgpd_compliance', 0),
            "Procurement Compliance": compliance.get('procurement_compliance', 0),
            "Security Compliance": compliance.get('security_compliance', 0),
            "Accessibility Compliance": compliance.get('accessibility_compliance', 0)
        }
        
        for area, score in compliance_areas.items():
            progress_color = "success" if score >= 80 else "warning" if score >= 60 else "danger"
            
            components.append(
                html.Div([
                    html.Small(area, className="text-muted"),
                    dbc.Progress(
                        value=score,
                        color=progress_color,
                        className="mb-2",
                        style={"height": "8px"}
                    )
                ])
            )
        
        # Gaps summary
        gaps_count = compliance.get('gaps_count', 0)
        critical_gaps = compliance.get('critical_gaps', 0)
        
        if gaps_count > 0:
            components.extend([
                html.Hr(),
                html.H6("Compliance Gaps:", className="mb-2"),
                html.P([
                    f"Total Gaps: {gaps_count}",
                    html.Br(),
                    html.Span(
                        f"Critical: {critical_gaps}",
                        className="text-danger" if critical_gaps > 0 else "text-success"
                    )
                ], className="small")
            ])
        
        return components
    
    async def save_dashboard_data(self):
        """Save dashboard data to file"""
        if not self.dashboard_data:
            return
        
        data_path = Path("/home/danielfugisawa/pesquisa_prospect_gov/docs/risk-monitoring/dashboard-data.json")
        data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        serializable_data = {
            "kri_metrics": {
                kri_type.value: {
                    "current_value": metric.current_value,
                    "target_value": metric.target_value,
                    "threshold_high": metric.threshold_high,
                    "threshold_critical": metric.threshold_critical,
                    "trend_direction": metric.trend_direction,
                    "risk_level": metric.risk_level.value,
                    "last_updated": metric.last_updated.isoformat(),
                    "description": metric.description
                }
                for kri_type, metric in self.dashboard_data.kri_metrics.items()
            },
            "threat_radar": self.dashboard_data.threat_radar,
            "portfolio_allocation": self.dashboard_data.portfolio_allocation,
            "recent_alerts": self.dashboard_data.recent_alerts,
            "scenario_impacts": self.dashboard_data.scenario_impacts,
            "compliance_status": self.dashboard_data.compliance_status,
            "last_updated": self.dashboard_data.last_updated.isoformat()
        }
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dashboard data saved to {data_path}")
    
    def run_dashboard(self, host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
        """Run the dashboard server"""
        logger.info(f"Starting Risk Monitoring Dashboard at http://{host}:{port}")
        
        if self.app:
            self.app.run_server(host=host, port=port, debug=debug)
        else:
            logger.error("Dashboard not initialized")

if __name__ == "__main__":
    async def main():
        # Initialize dashboard
        dashboard = RiskDashboard()
        
        # Update data
        dashboard._update_dashboard_data()
        
        # Save data
        await dashboard.save_dashboard_data()
        
        print("\n" + "="*80)
        print("RISK MONITORING DASHBOARD INITIALIZED")
        print("="*80)
        
        # Display current KRI status
        print("\n📊 CURRENT KRI STATUS:")
        for kri_type, metric in dashboard.kri_metrics.items():
            if "ratio" in kri_type.value.lower() or "concentration" in kri_type.value.lower():
                value_display = f"{metric.current_value:.1%}"
            else:
                value_display = f"{metric.current_value:.1f}"
            
            print(f"  {kri_type.value}: {value_display} ({metric.risk_level.value})")
        
        print("\n🎯 THREAT RADAR:")
        if dashboard.dashboard_data:
            for threat, level in dashboard.dashboard_data.threat_radar.items():
                print(f"  {threat}: {level}/100")
        
        print("\n🚨 RECENT ALERTS:")
        if dashboard.dashboard_data:
            for alert in dashboard.dashboard_data.recent_alerts[:3]:
                print(f"  [{alert['severity']}] {alert['category']}: {alert['message']}")
        
        print("\n🚀 Starting dashboard server...")
        print("Access dashboard at: http://127.0.0.1:8050")
        print("Press Ctrl+C to stop")
        
        # Run dashboard (comment out for testing)
        # dashboard.run_dashboard(debug=True)
        
        print("\n✅ Dashboard ready! (Server start commented out for testing)")
    
    asyncio.run(main())
