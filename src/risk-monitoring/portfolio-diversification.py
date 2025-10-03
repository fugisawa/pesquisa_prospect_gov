#!/usr/bin/env python3
"""
Portfolio Diversification Analysis Engine
Analyzes and optimizes business portfolio diversification to minimize strategic risks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class GrowthRate(Enum):
    DECLINING = "Declining"
    STABLE = "Stable"
    MODERATE = "Moderate"
    HIGH = "High"
    EXPLOSIVE = "Explosive"

class Position(Enum):
    LEADER = "Market Leader"
    CHALLENGER = "Challenger"
    FOLLOWER = "Follower"
    NICHE = "Niche Player"

class MarketSegment(Enum):
    GOVERNMENT_B2B = "Government B2B"
    CORPORATE_TRAINING = "Corporate Training"
    HIGHER_EDUCATION = "Higher Education"
    K12_EDUCATION = "K-12 Education"
    INTERNATIONAL_MARKETS = "International Markets"
    CONSUMER_B2C = "Consumer B2C"
    HEALTHCARE_TRAINING = "Healthcare Training"
    PROFESSIONAL_CERTIFICATION = "Professional Certification"

@dataclass
class PortfolioSegment:
    segment: MarketSegment
    risk_level: RiskLevel
    growth_potential: GrowthRate
    competitive_position: Position
    resource_allocation: float  # Percentage (0-1)
    current_revenue: float
    projected_revenue: float
    market_size: float
    market_share: float
    customer_concentration: float  # Risk metric
    regulatory_risk: RiskLevel
    competitive_intensity: float  # 0-1 scale
    barriers_to_entry: float  # 0-1 scale
    technology_disruption_risk: RiskLevel

@dataclass
class DiversificationMetrics:
    herfindahl_index: float  # Market concentration (0-1, lower is better)
    revenue_diversification: float  # 0-1, higher is better
    risk_adjusted_return: float
    portfolio_beta: float  # Risk relative to market
    maximum_drawdown: float  # Worst-case scenario impact
    correlation_matrix: Dict[str, Dict[str, float]]
    var_95: float  # Value at Risk (95% confidence)
    expected_return: float
    sharpe_ratio: float

@dataclass
class OptimizationTarget:
    target_type: str  # "max_return", "min_risk", "balanced"
    constraints: Dict[str, Any]
    weights: Dict[str, float]
    time_horizon: str  # "short", "medium", "long"

class PortfolioDiversificationEngine:
    def __init__(self, config_path: str = "/home/danielfugisawa/pesquisa_prospect_gov/config/risk-monitoring/portfolio-config.json"):
        self.config_path = Path(config_path)
        self.portfolio_segments: Dict[MarketSegment, PortfolioSegment] = {}
        self.diversification_metrics: Optional[DiversificationMetrics] = None
        self.optimization_history: List[Dict[str, Any]] = []
        self.load_config()
        self._initialize_portfolio()
    
    def load_config(self):
        """Load portfolio configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default portfolio configuration"""
        return {
            "diversification_targets": {
                "Government B2B": {"allocation": 0.40, "risk": "Medium"},
                "Corporate Training": {"allocation": 0.25, "risk": "Low"},
                "Higher Education": {"allocation": 0.20, "risk": "Medium"},
                "International Markets": {"allocation": 0.10, "risk": "High"},
                "Consumer B2C": {"allocation": 0.05, "risk": "High"}
            },
            "risk_parameters": {
                "max_single_segment": 0.50,  # Maximum allocation to single segment
                "min_segments": 3,  # Minimum number of segments
                "max_customer_concentration": 0.30,  # Maximum revenue from single customer
                "target_herfindahl": 0.25,  # Target market concentration
                "min_liquidity_reserve": 0.15  # Minimum cash/liquid assets
            },
            "optimization_constraints": {
                "min_allocation_per_segment": 0.05,
                "max_allocation_per_segment": 0.60,
                "target_annual_growth": 0.25,
                "max_annual_variance": 0.40,
                "min_sharpe_ratio": 1.0
            },
            "scenario_parameters": {
                "economic_downturn": {"probability": 0.20, "impact": -0.30},
                "big_tech_entry": {"probability": 0.40, "impact": -0.25},
                "regulatory_change": {"probability": 0.30, "impact": -0.15},
                "technology_disruption": {"probability": 0.25, "impact": -0.20}
            }
        }
    
    def save_config(self):
        """Save portfolio configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _initialize_portfolio(self):
        """Initialize portfolio with current segments"""
        # Government B2B - Current primary segment
        self.portfolio_segments[MarketSegment.GOVERNMENT_B2B] = PortfolioSegment(
            segment=MarketSegment.GOVERNMENT_B2B,
            risk_level=RiskLevel.MEDIUM,
            growth_potential=GrowthRate.HIGH,
            competitive_position=Position.CHALLENGER,
            resource_allocation=0.60,  # Current heavy concentration
            current_revenue=1000000.0,  # R$ 1M base
            projected_revenue=1500000.0,  # R$ 1.5M projected
            market_size=5000000000.0,  # R$ 5B market
            market_share=0.0002,  # 0.02% market share
            customer_concentration=0.40,  # High concentration risk
            regulatory_risk=RiskLevel.HIGH,
            competitive_intensity=0.7,
            barriers_to_entry=0.8,
            technology_disruption_risk=RiskLevel.MEDIUM
        )
        
        # Corporate Training - Expansion target
        self.portfolio_segments[MarketSegment.CORPORATE_TRAINING] = PortfolioSegment(
            segment=MarketSegment.CORPORATE_TRAINING,
            risk_level=RiskLevel.LOW,
            growth_potential=GrowthRate.MODERATE,
            competitive_position=Position.NICHE,
            resource_allocation=0.15,
            current_revenue=200000.0,
            projected_revenue=400000.0,
            market_size=2000000000.0,
            market_share=0.0001,
            customer_concentration=0.25,
            regulatory_risk=RiskLevel.LOW,
            competitive_intensity=0.5,
            barriers_to_entry=0.4,
            technology_disruption_risk=RiskLevel.LOW
        )
        
        # Higher Education - Strategic target
        self.portfolio_segments[MarketSegment.HIGHER_EDUCATION] = PortfolioSegment(
            segment=MarketSegment.HIGHER_EDUCATION,
            risk_level=RiskLevel.MEDIUM,
            growth_potential=GrowthRate.HIGH,
            competitive_position=Position.FOLLOWER,
            resource_allocation=0.15,
            current_revenue=150000.0,
            projected_revenue=350000.0,
            market_size=3000000000.0,
            market_share=0.00005,
            customer_concentration=0.30,
            regulatory_risk=RiskLevel.MEDIUM,
            competitive_intensity=0.6,
            barriers_to_entry=0.6,
            technology_disruption_risk=RiskLevel.MEDIUM
        )
        
        # International Markets - Growth opportunity
        self.portfolio_segments[MarketSegment.INTERNATIONAL_MARKETS] = PortfolioSegment(
            segment=MarketSegment.INTERNATIONAL_MARKETS,
            risk_level=RiskLevel.HIGH,
            growth_potential=GrowthRate.EXPLOSIVE,
            competitive_position=Position.NICHE,
            resource_allocation=0.05,
            current_revenue=50000.0,
            projected_revenue=200000.0,
            market_size=10000000000.0,
            market_share=0.000005,
            customer_concentration=0.20,
            regulatory_risk=RiskLevel.HIGH,
            competitive_intensity=0.8,
            barriers_to_entry=0.9,
            technology_disruption_risk=RiskLevel.HIGH
        )
        
        # Consumer B2C - Innovation testing
        self.portfolio_segments[MarketSegment.CONSUMER_B2C] = PortfolioSegment(
            segment=MarketSegment.CONSUMER_B2C,
            risk_level=RiskLevel.HIGH,
            growth_potential=GrowthRate.HIGH,
            competitive_position=Position.NICHE,
            resource_allocation=0.05,
            current_revenue=30000.0,
            projected_revenue=100000.0,
            market_size=1000000000.0,
            market_share=0.00003,
            customer_concentration=0.10,
            regulatory_risk=RiskLevel.MEDIUM,
            competitive_intensity=0.9,
            barriers_to_entry=0.3,
            technology_disruption_risk=RiskLevel.CRITICAL
        )
    
    def calculate_diversification_metrics(self) -> DiversificationMetrics:
        """Calculate comprehensive diversification metrics"""
        segments = list(self.portfolio_segments.values())
        
        # Herfindahl-Hirschman Index (market concentration)
        allocations = [s.resource_allocation for s in segments]
        hhi = sum(a**2 for a in allocations)
        
        # Revenue diversification (entropy-based)
        revenues = [s.current_revenue for s in segments]
        total_revenue = sum(revenues)
        if total_revenue > 0:
            rev_weights = [r/total_revenue for r in revenues]
            revenue_entropy = -sum(w * np.log(w) if w > 0 else 0 for w in rev_weights)
            max_entropy = np.log(len(segments))
            revenue_diversification = revenue_entropy / max_entropy if max_entropy > 0 else 0
        else:
            revenue_diversification = 0
        
        # Risk-adjusted return calculation
        returns = [(s.projected_revenue - s.current_revenue) / s.current_revenue 
                  if s.current_revenue > 0 else 0 for s in segments]
        weights = allocations
        portfolio_return = sum(w * r for w, r in zip(weights, returns))
        
        # Risk calculation (simplified)
        risk_scores = [self._risk_to_numeric(s.risk_level) for s in segments]
        portfolio_risk = np.sqrt(sum(w**2 * r**2 for w, r in zip(weights, risk_scores)))
        
        risk_adjusted_return = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
        
        # Portfolio beta (risk relative to market)
        market_risk = 0.15  # Assumed market risk
        portfolio_beta = portfolio_risk / market_risk
        
        # Maximum drawdown simulation
        max_drawdown = self._calculate_max_drawdown(segments, weights)
        
        # Correlation matrix
        correlation_matrix = self._calculate_correlation_matrix(segments)
        
        # Value at Risk (95%)
        var_95 = self._calculate_var_95(segments, weights)
        
        # Sharpe ratio
        risk_free_rate = 0.05  # Assumed risk-free rate
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
        
        self.diversification_metrics = DiversificationMetrics(
            herfindahl_index=hhi,
            revenue_diversification=revenue_diversification,
            risk_adjusted_return=risk_adjusted_return,
            portfolio_beta=portfolio_beta,
            maximum_drawdown=max_drawdown,
            correlation_matrix=correlation_matrix,
            var_95=var_95,
            expected_return=portfolio_return,
            sharpe_ratio=sharpe_ratio
        )
        
        return self.diversification_metrics
    
    def _risk_to_numeric(self, risk_level: RiskLevel) -> float:
        """Convert risk level to numeric value"""
        risk_map = {
            RiskLevel.LOW: 0.05,
            RiskLevel.MEDIUM: 0.15,
            RiskLevel.HIGH: 0.25,
            RiskLevel.CRITICAL: 0.40
        }
        return risk_map.get(risk_level, 0.15)
    
    def _calculate_max_drawdown(self, segments: List[PortfolioSegment], weights: List[float]) -> float:
        """Calculate maximum potential drawdown"""
        # Simulate worst-case scenarios
        scenarios = [
            {"name": "Economic Downturn", "impact": -0.30},
            {"name": "Big Tech Entry", "impact": -0.25},
            {"name": "Regulatory Change", "impact": -0.15},
            {"name": "Technology Disruption", "impact": -0.20}
        ]
        
        max_loss = 0
        for scenario in scenarios:
            # Calculate segment-specific impacts
            total_loss = 0
            for i, segment in enumerate(segments):
                segment_impact = scenario["impact"]
                
                # Adjust impact based on segment characteristics
                if scenario["name"] == "Big Tech Entry":
                    if segment.segment == MarketSegment.GOVERNMENT_B2B:
                        segment_impact *= 1.5  # Government most vulnerable
                elif scenario["name"] == "Regulatory Change":
                    if segment.regulatory_risk == RiskLevel.HIGH:
                        segment_impact *= 2.0
                elif scenario["name"] == "Technology Disruption":
                    if segment.technology_disruption_risk == RiskLevel.CRITICAL:
                        segment_impact *= 2.5
                
                total_loss += weights[i] * abs(segment_impact)
            
            max_loss = max(max_loss, total_loss)
        
        return max_loss
    
    def _calculate_correlation_matrix(self, segments: List[PortfolioSegment]) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between segments"""
        segment_names = [s.segment.value for s in segments]
        correlation_matrix = {}
        
        for i, seg1 in enumerate(segment_names):
            correlation_matrix[seg1] = {}
            for j, seg2 in enumerate(segment_names):
                if i == j:
                    correlation_matrix[seg1][seg2] = 1.0
                else:
                    # Estimate correlation based on segment characteristics
                    corr = self._estimate_correlation(segments[i], segments[j])
                    correlation_matrix[seg1][seg2] = corr
        
        return correlation_matrix
    
    def _estimate_correlation(self, seg1: PortfolioSegment, seg2: PortfolioSegment) -> float:
        """Estimate correlation between two segments"""
        # Base correlation
        base_corr = 0.3  # All segments somewhat correlated
        
        # Adjust based on segment types
        if (seg1.segment == MarketSegment.GOVERNMENT_B2B and 
            seg2.segment == MarketSegment.HIGHER_EDUCATION):
            return 0.6  # Both education-related
        elif (seg1.segment == MarketSegment.CORPORATE_TRAINING and 
              seg2.segment == MarketSegment.PROFESSIONAL_CERTIFICATION):
            return 0.7  # Both corporate-focused
        elif (seg1.segment == MarketSegment.CONSUMER_B2C and 
              seg2.segment == MarketSegment.INTERNATIONAL_MARKETS):
            return 0.4  # Different risk profiles
        
        # Adjust for risk levels
        risk_diff = abs(self._risk_to_numeric(seg1.risk_level) - self._risk_to_numeric(seg2.risk_level))
        correlation_adjustment = -risk_diff * 0.5  # Lower correlation for different risk levels
        
        return max(0.1, min(0.9, base_corr + correlation_adjustment))
    
    def _calculate_var_95(self, segments: List[PortfolioSegment], weights: List[float]) -> float:
        """Calculate Value at Risk at 95% confidence level"""
        # Monte Carlo simulation for VaR
        num_simulations = 10000
        returns = []
        
        for _ in range(num_simulations):
            portfolio_return = 0
            for i, segment in enumerate(segments):
                # Simulate segment return
                expected_return = (segment.projected_revenue - segment.current_revenue) / segment.current_revenue
                risk = self._risk_to_numeric(segment.risk_level)
                
                # Random return from normal distribution
                simulated_return = np.random.normal(expected_return, risk)
                portfolio_return += weights[i] * simulated_return
            
            returns.append(portfolio_return)
        
        # 95% VaR (5th percentile loss)
        return -np.percentile(returns, 5)
    
    def optimize_portfolio(self, target: OptimizationTarget) -> Dict[MarketSegment, float]:
        """Optimize portfolio allocation based on target criteria"""
        logger.info(f"Optimizing portfolio for {target.target_type}...")
        
        segments = list(self.portfolio_segments.values())
        initial_weights = [s.resource_allocation for s in segments]
        
        # Define objective function
        def objective_function(weights):
            if target.target_type == "max_return":
                return -self._calculate_expected_return(segments, weights)
            elif target.target_type == "min_risk":
                return self._calculate_portfolio_risk(segments, weights)
            elif target.target_type == "balanced":
                ret = self._calculate_expected_return(segments, weights)
                risk = self._calculate_portfolio_risk(segments, weights)
                return -(ret / risk) if risk > 0 else -ret  # Maximize Sharpe ratio
            else:
                raise ValueError(f"Unknown target type: {target.target_type}")
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: sum(w) - 1.0},  # Weights sum to 1
        ]
        
        # Add custom constraints
        if "max_single_segment" in target.constraints:
            max_single = target.constraints["max_single_segment"]
            for i in range(len(segments)):
                constraints.append({
                    'type': 'ineq', 
                    'fun': lambda w, idx=i: max_single - w[idx]
                })
        
        if "min_segments" in target.constraints:
            min_segments = target.constraints["min_segments"]
            min_allocation = 1.0 / (len(segments) * 2)  # Ensure min segments have meaningful allocation
            active_segments = lambda w: sum(1 for weight in w if weight >= min_allocation)
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: active_segments(w) - min_segments
            })
        
        # Bounds for each weight
        bounds = [(0.0, 1.0) for _ in segments]
        
        # Optimize
        result = minimize(
            objective_function,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimized_weights = result.x
            
            # Update portfolio allocations
            optimization_result = {}
            for i, segment in enumerate(segments):
                optimization_result[segment.segment] = optimized_weights[i]
                self.portfolio_segments[segment.segment].resource_allocation = optimized_weights[i]
            
            # Record optimization
            self.optimization_history.append({
                "timestamp": datetime.now().isoformat(),
                "target_type": target.target_type,
                "objective_value": result.fun,
                "optimized_weights": dict(optimization_result),
                "constraints": target.constraints
            })
            
            logger.info(f"Portfolio optimization successful. Objective value: {result.fun:.4f}")
            return optimization_result
        else:
            logger.error(f"Portfolio optimization failed: {result.message}")
            return {segment.segment: segment.resource_allocation for segment in segments}
    
    def _calculate_expected_return(self, segments: List[PortfolioSegment], weights: List[float]) -> float:
        """Calculate expected portfolio return"""
        returns = [(s.projected_revenue - s.current_revenue) / s.current_revenue 
                  if s.current_revenue > 0 else 0 for s in segments]
        return sum(w * r for w, r in zip(weights, returns))
    
    def _calculate_portfolio_risk(self, segments: List[PortfolioSegment], weights: List[float]) -> float:
        """Calculate portfolio risk"""
        risk_scores = [self._risk_to_numeric(s.risk_level) for s in segments]
        
        # Calculate weighted risk with correlation adjustments
        portfolio_variance = 0
        for i in range(len(segments)):
            for j in range(len(segments)):
                corr = self._estimate_correlation(segments[i], segments[j])
                portfolio_variance += weights[i] * weights[j] * risk_scores[i] * risk_scores[j] * corr
        
        return np.sqrt(portfolio_variance)
    
    def run_scenario_analysis(self) -> Dict[str, Any]:
        """Run scenario analysis on portfolio"""
        scenarios = self.config["scenario_parameters"]
        results = {}
        
        for scenario_name, params in scenarios.items():
            logger.info(f"Running scenario analysis: {scenario_name}")
            
            # Calculate impact on each segment
            segment_impacts = {}
            total_impact = 0
            
            for segment in self.portfolio_segments.values():
                # Base impact
                impact = params["impact"]
                
                # Adjust impact based on segment characteristics
                if scenario_name == "big_tech_entry":
                    if segment.segment == MarketSegment.GOVERNMENT_B2B:
                        impact *= 1.5  # Most vulnerable
                    elif segment.segment == MarketSegment.CORPORATE_TRAINING:
                        impact *= 0.8  # Less vulnerable
                elif scenario_name == "regulatory_change":
                    risk_multiplier = {
                        RiskLevel.LOW: 0.5,
                        RiskLevel.MEDIUM: 1.0,
                        RiskLevel.HIGH: 2.0,
                        RiskLevel.CRITICAL: 3.0
                    }
                    impact *= risk_multiplier.get(segment.regulatory_risk, 1.0)
                
                segment_impact = segment.resource_allocation * impact
                segment_impacts[segment.segment.value] = segment_impact
                total_impact += segment_impact
            
            results[scenario_name] = {
                "probability": params["probability"],
                "total_impact": total_impact,
                "segment_impacts": segment_impacts,
                "expected_loss": total_impact * params["probability"]
            }
        
        return results
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate portfolio optimization recommendations"""
        recommendations = []
        
        metrics = self.calculate_diversification_metrics()
        
        # Check concentration risk
        if metrics.herfindahl_index > 0.40:
            recommendations.append(
                "🚨 HIGH CONCENTRATION RISK: Consider reducing allocation to dominant segment"
            )
        
        # Check revenue diversification
        if metrics.revenue_diversification < 0.60:
            recommendations.append(
                "📋 DIVERSIFICATION OPPORTUNITY: Increase revenue sources across segments"
            )
        
        # Check Sharpe ratio
        if metrics.sharpe_ratio < 1.0:
            recommendations.append(
                "📈 RISK-RETURN OPTIMIZATION: Portfolio risk may be too high for expected returns"
            )
        
        # Check individual segment risks
        high_risk_segments = [s for s in self.portfolio_segments.values() 
                             if s.risk_level == RiskLevel.HIGH and s.resource_allocation > 0.20]
        if high_risk_segments:
            recommendations.append(
                f"⚠️ HIGH-RISK ALLOCATION: Consider reducing exposure to {[s.segment.value for s in high_risk_segments]}"
            )
        
        # Check customer concentration
        high_concentration_segments = [s for s in self.portfolio_segments.values() 
                                     if s.customer_concentration > 0.30]
        if high_concentration_segments:
            recommendations.append(
                f"🎯 CUSTOMER CONCENTRATION: Diversify customer base in {[s.segment.value for s in high_concentration_segments]}"
            )
        
        # Growth opportunities
        underallocated_growth = [s for s in self.portfolio_segments.values() 
                               if s.growth_potential in [GrowthRate.HIGH, GrowthRate.EXPLOSIVE] 
                               and s.resource_allocation < 0.15]
        if underallocated_growth:
            recommendations.append(
                f"🚀 GROWTH OPPORTUNITY: Consider increasing allocation to {[s.segment.value for s in underallocated_growth]}"
            )
        
        return recommendations
    
    def generate_diversification_report(self) -> str:
        """Generate comprehensive diversification report"""
        metrics = self.calculate_diversification_metrics()
        scenario_results = self.run_scenario_analysis()
        recommendations = self.generate_optimization_recommendations()
        
        report_lines = [
            "# PORTFOLIO DIVERSIFICATION ANALYSIS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## EXECUTIVE SUMMARY",
            f"**Diversification Score: {(1 - metrics.herfindahl_index) * 100:.1f}/100**",
            f"**Risk-Adjusted Return: {metrics.risk_adjusted_return:.3f}**",
            f"**Sharpe Ratio: {metrics.sharpe_ratio:.3f}**",
            ""
        ]
        
        # Portfolio health assessment
        if metrics.herfindahl_index < 0.25:
            report_lines.append("✅ **EXCELLENT** diversification - Low concentration risk")
        elif metrics.herfindahl_index < 0.40:
            report_lines.append("✅ **GOOD** diversification - Moderate concentration")
        elif metrics.herfindahl_index < 0.60:
            report_lines.append("⚠️ **MODERATE** diversification - Some concentration risk")
        else:
            report_lines.append("🚨 **HIGH RISK** - Dangerous concentration levels")
        
        # Current allocation
        report_lines.extend(["", "## CURRENT PORTFOLIO ALLOCATION", ""])
        for segment in self.portfolio_segments.values():
            report_lines.extend([
                f"### {segment.segment.value}",
                f"- **Allocation**: {segment.resource_allocation:.1%}",
                f"- **Risk Level**: {segment.risk_level.value}",
                f"- **Growth Potential**: {segment.growth_potential.value}",
                f"- **Current Revenue**: R$ {segment.current_revenue:,.0f}",
                f"- **Projected Revenue**: R$ {segment.projected_revenue:,.0f}",
                f"- **Customer Concentration**: {segment.customer_concentration:.1%}",
                ""
            ])
        
        # Diversification metrics
        report_lines.extend([
            "## DIVERSIFICATION METRICS",
            f"- **Herfindahl Index**: {metrics.herfindahl_index:.3f} (lower is better)",
            f"- **Revenue Diversification**: {metrics.revenue_diversification:.3f}",
            f"- **Portfolio Beta**: {metrics.portfolio_beta:.3f}",
            f"- **Maximum Drawdown**: {metrics.maximum_drawdown:.1%}",
            f"- **95% Value at Risk**: {metrics.var_95:.1%}",
            f"- **Expected Return**: {metrics.expected_return:.1%}",
            ""
        ])
        
        # Scenario analysis
        report_lines.extend(["## SCENARIO ANALYSIS", ""])
        for scenario, results in scenario_results.items():
            report_lines.extend([
                f"### {scenario.replace('_', ' ').title()}",
                f"- **Probability**: {results['probability']:.1%}",
                f"- **Total Impact**: {results['total_impact']:.1%}",
                f"- **Expected Loss**: {results['expected_loss']:.1%}",
                ""
            ])
        
        # Recommendations
        if recommendations:
            report_lines.extend(["## RECOMMENDATIONS", ""])
            for rec in recommendations:
                report_lines.append(f"- {rec}")
            report_lines.append("")
        
        # Optimization history
        if self.optimization_history:
            report_lines.extend(["## RECENT OPTIMIZATIONS", ""])
            for opt in self.optimization_history[-3:]:  # Last 3 optimizations
                report_lines.extend([
                    f"**{opt['timestamp'][:10]}** - {opt['target_type']}",
                    f"Objective Value: {opt['objective_value']:.4f}",
                    ""
                ])
        
        return "\n".join(report_lines)
    
    async def save_analysis_results(self):
        """Save portfolio analysis results"""
        results_path = Path("/home/danielfugisawa/pesquisa_prospect_gov/docs/risk-monitoring/portfolio-analysis-results.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = self.calculate_diversification_metrics()
        scenario_results = self.run_scenario_analysis()
        
        results = {
            "last_updated": datetime.now().isoformat(),
            "diversification_metrics": asdict(metrics),
            "portfolio_segments": {
                segment.segment.value: {
                    "risk_level": segment.risk_level.value,
                    "growth_potential": segment.growth_potential.value,
                    "competitive_position": segment.competitive_position.value,
                    "resource_allocation": segment.resource_allocation,
                    "current_revenue": segment.current_revenue,
                    "projected_revenue": segment.projected_revenue,
                    "market_share": segment.market_share,
                    "customer_concentration": segment.customer_concentration,
                    "regulatory_risk": segment.regulatory_risk.value
                }
                for segment in self.portfolio_segments.values()
            },
            "scenario_analysis": scenario_results,
            "optimization_history": self.optimization_history,
            "recommendations": self.generate_optimization_recommendations()
        }
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Portfolio analysis results saved to {results_path}")

if __name__ == "__main__":
    async def main():
        engine = PortfolioDiversificationEngine()
        
        # Calculate current metrics
        metrics = engine.calculate_diversification_metrics()
        
        # Run optimization
        target = OptimizationTarget(
            target_type="balanced",
            constraints={
                "max_single_segment": 0.50,
                "min_segments": 3
            },
            weights={},
            time_horizon="medium"
        )
        
        optimized_allocation = engine.optimize_portfolio(target)
        
        # Save results
        await engine.save_analysis_results()
        
        # Generate and display report
        print("\n" + "="*80)
        print(engine.generate_diversification_report())
        print("="*80)
        
        # Alert on high concentration
        if metrics.herfindahl_index > 0.50:
            print(f"\n🚨 CONCENTRATION ALERT: HHI {metrics.herfindahl_index:.3f} indicates dangerous concentration!")
        
        print(f"\n📋 Optimized allocation:")
        for segment, allocation in optimized_allocation.items():
            print(f"  {segment.value}: {allocation:.1%}")
    
    asyncio.run(main())
