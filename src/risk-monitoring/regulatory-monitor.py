#!/usr/bin/env python3
"""
Regulatory Compliance Monitoring System
Monitors Brazilian regulations affecting EdTech and government contracts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ImpactLevel(Enum):
    MINIMAL = "Minimal"
    MODERATE = "Moderate"
    SIGNIFICANT = "Significant"
    SEVERE = "Severe"

class ComplianceStatus(Enum):
    COMPLIANT = "Compliant"
    PARTIAL = "Partial"
    NON_COMPLIANT = "Non-Compliant"
    UNKNOWN = "Unknown"

class TimeFrame(Enum):
    IMMEDIATE = "0-30 days"
    SHORT_TERM = "1-3 months"
    MEDIUM_TERM = "3-12 months"
    LONG_TERM = "12+ months"

class RegulationType(Enum):
    LGPD = "Lei Geral de Proteção de Dados (LGPD)"
    EDUCATION_DIGITAL = "Lei 14.533/2023 - Política Nacional de Educação Digital"
    STARTUP_FRAMEWORK = "Marco Legal das Startups (Lei 13.243/2016)"
    PUBLIC_PROCUREMENT = "Lei de Licitações (Lei 14.133/2021)"
    GOVERNMENT_PURCHASES = "Decreto 10.332/2020 - Compras Públicas"
    DIGITAL_EDUCATION_CNE = "Resolução CNE/CP 1/2020 - Educação Digital"
    MEC_EDTECH = "Portarias MEC específicas para EdTech"
    CYBERSECURITY = "Lei Geral de Proteção de Dados Cibernética"
    ACCESSIBILITY = "Lei Brasileira de Inclusão (LBI)"
    CONSUMER_PROTECTION = "Código de Defesa do Consumidor (CDC)"

@dataclass
class RegulatoryChange:
    regulation: RegulationType
    change_type: str  # "New", "Amendment", "Revocation", "Interpretation"
    description: str
    effective_date: datetime
    impact_assessment: str
    compliance_requirements: List[str]
    source_url: Optional[str] = None
    detected_at: datetime = None

@dataclass
class ComplianceGap:
    regulation: RegulationType
    gap_description: str
    severity: ImpactLevel
    remediation_actions: List[str]
    estimated_cost: Optional[str] = None
    timeline: TimeFrame = TimeFrame.MEDIUM_TERM

@dataclass
class RegulatoryRisk:
    regulation: RegulationType
    changes_probability: RiskLevel
    impact_severity: ImpactLevel
    compliance_status: ComplianceStatus
    adaptation_time: TimeFrame
    monitoring_priority: str
    last_assessment: datetime

class RegulatoryMonitor:
    def __init__(self, config_path: str = "/home/danielfugisawa/pesquisa_prospect_gov/config/risk-monitoring/regulatory-config.json"):
        self.config_path = Path(config_path)
        self.regulatory_risks: Dict[RegulationType, RegulatoryRisk] = {}
        self.recent_changes: List[RegulatoryChange] = []
        self.compliance_gaps: List[ComplianceGap] = []
        self.load_config()
        self._initialize_regulatory_framework()
    
    def load_config(self):
        """Load regulatory monitoring configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default regulatory monitoring configuration"""
        return {
            "monitoring_sources": {
                "official_sources": [
                    "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/",
                    "https://www.in.gov.br/",  # Diário Oficial da União
                    "https://portal.mec.gov.br/",
                    "https://www.gov.br/infraestrutura/pt-br",
                    "https://www.gov.br/anpd/pt-br"  # ANPD - LGPD Authority
                ],
                "legal_databases": [
                    "https://www.jusbrasil.com.br/",
                    "https://www.conjur.com.br/",
                    "https://www.migalhas.com.br/"
                ],
                "consultation_portals": [
                    "https://www.participa.br/",
                    "https://www.gov.br/participamaisbrasil/"
                ]
            },
            "keywords": {
                "education": ["educação", "ensino", "edtech", "educacional", "pedagógico"],
                "technology": ["tecnologia", "digital", "software", "plataforma", "sistema"],
                "government": ["governo", "público", "licitação", "contrato", "órgão"],
                "compliance": ["conformidade", "regulamentação", "norma", "lei", "decreto"]
            },
            "monitoring_frequency": {
                "critical_regulations": 86400,  # Daily
                "important_regulations": 259200,  # 3 days
                "standard_regulations": 604800  # Weekly
            },
            "alert_triggers": {
                "new_regulation": True,
                "amendment_proposed": True,
                "enforcement_action": True,
                "interpretation_change": True,
                "deadline_approaching": True
            }
        }
    
    def save_config(self):
        """Save regulatory monitoring configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _initialize_regulatory_framework(self):
        """Initialize the regulatory framework with current regulations"""
        # LGPD - Critical for any data processing
        self.regulatory_risks[RegulationType.LGPD] = RegulatoryRisk(
            regulation=RegulationType.LGPD,
            changes_probability=RiskLevel.MEDIUM,
            impact_severity=ImpactLevel.SEVERE,
            compliance_status=ComplianceStatus.PARTIAL,
            adaptation_time=TimeFrame.SHORT_TERM,
            monitoring_priority="Critical",
            last_assessment=datetime.now()
        )
        
        # Lei 14.533/2023 - Digital Education Policy
        self.regulatory_risks[RegulationType.EDUCATION_DIGITAL] = RegulatoryRisk(
            regulation=RegulationType.EDUCATION_DIGITAL,
            changes_probability=RiskLevel.HIGH,
            impact_severity=ImpactLevel.SIGNIFICANT,
            compliance_status=ComplianceStatus.UNKNOWN,
            adaptation_time=TimeFrame.MEDIUM_TERM,
            monitoring_priority="High",
            last_assessment=datetime.now()
        )
        
        # Marco Legal das Startups
        self.regulatory_risks[RegulationType.STARTUP_FRAMEWORK] = RegulatoryRisk(
            regulation=RegulationType.STARTUP_FRAMEWORK,
            changes_probability=RiskLevel.LOW,
            impact_severity=ImpactLevel.MODERATE,
            compliance_status=ComplianceStatus.COMPLIANT,
            adaptation_time=TimeFrame.LONG_TERM,
            monitoring_priority="Medium",
            last_assessment=datetime.now()
        )
        
        # Lei de Licitações
        self.regulatory_risks[RegulationType.PUBLIC_PROCUREMENT] = RegulatoryRisk(
            regulation=RegulationType.PUBLIC_PROCUREMENT,
            changes_probability=RiskLevel.MEDIUM,
            impact_severity=ImpactLevel.SEVERE,
            compliance_status=ComplianceStatus.PARTIAL,
            adaptation_time=TimeFrame.SHORT_TERM,
            monitoring_priority="Critical",
            last_assessment=datetime.now()
        )
        
        # Initialize other regulations with default assessments
        remaining_regulations = [
            RegulationType.GOVERNMENT_PURCHASES,
            RegulationType.DIGITAL_EDUCATION_CNE,
            RegulationType.MEC_EDTECH,
            RegulationType.CYBERSECURITY,
            RegulationType.ACCESSIBILITY,
            RegulationType.CONSUMER_PROTECTION
        ]
        
        for regulation in remaining_regulations:
            self.regulatory_risks[regulation] = RegulatoryRisk(
                regulation=regulation,
                changes_probability=RiskLevel.MEDIUM,
                impact_severity=ImpactLevel.MODERATE,
                compliance_status=ComplianceStatus.UNKNOWN,
                adaptation_time=TimeFrame.MEDIUM_TERM,
                monitoring_priority="Medium",
                last_assessment=datetime.now()
            )
    
    async def monitor_regulatory_changes(self) -> List[RegulatoryChange]:
        """Monitor for new regulatory changes"""
        logger.info("Monitoring regulatory changes...")
        
        changes = []
        
        # Monitor official government sources
        official_changes = await self._monitor_official_sources()
        changes.extend(official_changes)
        
        # Monitor legal databases
        legal_changes = await self._monitor_legal_databases()
        changes.extend(legal_changes)
        
        # Monitor consultation processes
        consultation_changes = await self._monitor_consultations()
        changes.extend(consultation_changes)
        
        # Update recent changes
        self.recent_changes = changes
        
        # Assess impact of changes
        await self._assess_change_impacts(changes)
        
        return changes
    
    async def _monitor_official_sources(self) -> List[RegulatoryChange]:
        """Monitor official government sources for regulatory changes"""
        changes = []
        
        # Simulate monitoring (replace with actual web scraping)
        for source in self.config["monitoring_sources"]["official_sources"]:
            try:
                # Mock regulatory change detection
                if "mec.gov.br" in source:
                    change = RegulatoryChange(
                        regulation=RegulationType.MEC_EDTECH,
                        change_type="Amendment",
                        description="Proposed changes to EdTech certification requirements",
                        effective_date=datetime.now() + timedelta(days=90),
                        impact_assessment="Moderate impact on platform certification",
                        compliance_requirements=[
                            "Updated security standards",
                            "Enhanced accessibility features",
                            "Performance benchmarking"
                        ],
                        source_url=source,
                        detected_at=datetime.now()
                    )
                    changes.append(change)
                
                elif "anpd" in source:
                    change = RegulatoryChange(
                        regulation=RegulationType.LGPD,
                        change_type="Interpretation",
                        description="New ANPD guidance on educational data processing",
                        effective_date=datetime.now() + timedelta(days=30),
                        impact_assessment="High impact on student data handling",
                        compliance_requirements=[
                            "Enhanced consent mechanisms",
                            "Data retention policy updates",
                            "Third-party processor agreements"
                        ],
                        source_url=source,
                        detected_at=datetime.now()
                    )
                    changes.append(change)
                
            except Exception as e:
                logger.error(f"Error monitoring {source}: {e}")
        
        return changes
    
    async def _monitor_legal_databases(self) -> List[RegulatoryChange]:
        """Monitor legal databases for regulatory analysis and commentary"""
        changes = []
        
        # Simulate legal database monitoring
        change = RegulatoryChange(
            regulation=RegulationType.PUBLIC_PROCUREMENT,
            change_type="New",
            description="Draft regulation on sustainable procurement in education",
            effective_date=datetime.now() + timedelta(days=180),
            impact_assessment="Potential preference for sustainable EdTech solutions",
            compliance_requirements=[
                "Environmental impact assessment",
                "Sustainability certification",
                "Carbon footprint reporting"
            ],
            source_url="https://www.jusbrasil.com.br/",
            detected_at=datetime.now()
        )
        changes.append(change)
        
        return changes
    
    async def _monitor_consultations(self) -> List[RegulatoryChange]:
        """Monitor public consultation processes"""
        changes = []
        
        # Simulate consultation monitoring
        change = RegulatoryChange(
            regulation=RegulationType.EDUCATION_DIGITAL,
            change_type="Amendment",
            description="Public consultation on AI in education guidelines",
            effective_date=datetime.now() + timedelta(days=120),
            impact_assessment="Significant impact on AI-powered educational tools",
            compliance_requirements=[
                "AI algorithm transparency",
                "Bias assessment and mitigation",
                "Human oversight requirements",
                "Student data protection in AI systems"
            ],
            source_url="https://www.participa.br/",
            detected_at=datetime.now()
        )
        changes.append(change)
        
        return changes
    
    async def _assess_change_impacts(self, changes: List[RegulatoryChange]):
        """Assess the impact of regulatory changes on business operations"""
        for change in changes:
            # Update regulatory risk assessment
            if change.regulation in self.regulatory_risks:
                risk = self.regulatory_risks[change.regulation]
                
                # Increase change probability for active regulations
                if change.change_type in ["New", "Amendment"]:
                    risk.changes_probability = RiskLevel.HIGH
                
                # Assess timeline based on effective date
                days_until_effective = (change.effective_date - datetime.now()).days
                if days_until_effective <= 30:
                    risk.adaptation_time = TimeFrame.IMMEDIATE
                elif days_until_effective <= 90:
                    risk.adaptation_time = TimeFrame.SHORT_TERM
                
                risk.last_assessment = datetime.now()
            
            # Identify compliance gaps
            gaps = self._identify_compliance_gaps(change)
            self.compliance_gaps.extend(gaps)
    
    def _identify_compliance_gaps(self, change: RegulatoryChange) -> List[ComplianceGap]:
        """Identify compliance gaps based on regulatory changes"""
        gaps = []
        
        # Analyze compliance requirements
        for requirement in change.compliance_requirements:
            if "security" in requirement.lower():
                gap = ComplianceGap(
                    regulation=change.regulation,
                    gap_description=f"Security compliance gap: {requirement}",
                    severity=ImpactLevel.SIGNIFICANT,
                    remediation_actions=[
                        "Conduct security audit",
                        "Update security policies",
                        "Implement additional controls",
                        "Staff training on new requirements"
                    ],
                    estimated_cost="R$ 50,000 - R$ 100,000",
                    timeline=TimeFrame.SHORT_TERM
                )
                gaps.append(gap)
            
            elif "accessibility" in requirement.lower():
                gap = ComplianceGap(
                    regulation=change.regulation,
                    gap_description=f"Accessibility compliance gap: {requirement}",
                    severity=ImpactLevel.MODERATE,
                    remediation_actions=[
                        "Accessibility audit",
                        "UI/UX improvements",
                        "Assistive technology integration",
                        "User testing with disabled users"
                    ],
                    estimated_cost="R$ 30,000 - R$ 80,000",
                    timeline=TimeFrame.MEDIUM_TERM
                )
                gaps.append(gap)
            
            elif "data" in requirement.lower() or "privacy" in requirement.lower():
                gap = ComplianceGap(
                    regulation=change.regulation,
                    gap_description=f"Data privacy compliance gap: {requirement}",
                    severity=ImpactLevel.SEVERE,
                    remediation_actions=[
                        "Data privacy impact assessment",
                        "Update privacy policies",
                        "Implement consent management",
                        "Data processor agreements review"
                    ],
                    estimated_cost="R$ 40,000 - R$ 120,000",
                    timeline=TimeFrame.SHORT_TERM
                )
                gaps.append(gap)
        
        return gaps
    
    def calculate_compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)"""
        if not self.regulatory_risks:
            return 0.0
        
        # Weight by importance and calculate score
        weights = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        
        total_score = 0
        total_weight = 0
        
        for risk in self.regulatory_risks.values():
            weight = weights.get(risk.monitoring_priority, 1)
            
            # Score based on compliance status
            if risk.compliance_status == ComplianceStatus.COMPLIANT:
                score = 100
            elif risk.compliance_status == ComplianceStatus.PARTIAL:
                score = 60
            elif risk.compliance_status == ComplianceStatus.NON_COMPLIANT:
                score = 20
            else:  # Unknown
                score = 40
            
            # Adjust for risk level
            if risk.changes_probability == RiskLevel.CRITICAL:
                score *= 0.7
            elif risk.changes_probability == RiskLevel.HIGH:
                score *= 0.8
            elif risk.changes_probability == RiskLevel.MEDIUM:
                score *= 0.9
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def generate_compliance_report(self) -> str:
        """Generate comprehensive compliance report"""
        compliance_score = self.calculate_compliance_score()
        
        report_lines = [
            "# REGULATORY COMPLIANCE ASSESSMENT REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Overall Compliance Score: {compliance_score:.1f}/100**",
            "",
            "## EXECUTIVE SUMMARY",
            ""
        ]
        
        # Compliance status overview
        if compliance_score >= 90:
            report_lines.append("✅ **EXCELLENT** - Strong regulatory compliance position")
        elif compliance_score >= 75:
            report_lines.append("✅ **GOOD** - Generally compliant with minor gaps")
        elif compliance_score >= 60:
            report_lines.append("⚠️ **MODERATE** - Several compliance gaps need attention")
        else:
            report_lines.append("🚨 **CRITICAL** - Significant compliance issues require immediate action")
        
        # Recent changes summary
        if self.recent_changes:
            report_lines.extend([
                "",
                f"📋 **Recent Changes Detected**: {len(self.recent_changes)}",
                f"📋 **Compliance Gaps Identified**: {len(self.compliance_gaps)}",
                ""
            ])
        
        # Critical issues
        critical_risks = [risk for risk in self.regulatory_risks.values() 
                         if risk.changes_probability == RiskLevel.CRITICAL or 
                            risk.impact_severity == ImpactLevel.SEVERE]
        
        if critical_risks:
            report_lines.extend(["## 🚨 CRITICAL REGULATORY RISKS", ""])
            for risk in critical_risks:
                report_lines.extend([
                    f"### {risk.regulation.value}",
                    f"- **Change Probability**: {risk.changes_probability.value}",
                    f"- **Impact Severity**: {risk.impact_severity.value}",
                    f"- **Compliance Status**: {risk.compliance_status.value}",
                    f"- **Adaptation Time**: {risk.adaptation_time.value}",
                    ""
                ])
        
        # Compliance gaps
        if self.compliance_gaps:
            report_lines.extend(["## 📋 COMPLIANCE GAPS", ""])
            for gap in self.compliance_gaps:
                report_lines.extend([
                    f"### {gap.regulation.value}",
                    f"**Gap**: {gap.gap_description}",
                    f"**Severity**: {gap.severity.value}",
                    f"**Timeline**: {gap.timeline.value}",
                    f"**Estimated Cost**: {gap.estimated_cost or 'TBD'}",
                    "**Actions Required**:",
                    *[f"- {action}" for action in gap.remediation_actions],
                    ""
                ])
        
        # Recent changes
        if self.recent_changes:
            report_lines.extend(["## 📰 RECENT REGULATORY CHANGES", ""])
            for change in self.recent_changes[-5:]:  # Show last 5 changes
                report_lines.extend([
                    f"### {change.regulation.value}",
                    f"**Type**: {change.change_type}",
                    f"**Description**: {change.description}",
                    f"**Effective Date**: {change.effective_date.strftime('%Y-%m-%d')}",
                    f"**Impact**: {change.impact_assessment}",
                    ""
                ])
        
        return "\n".join(report_lines)
    
    async def save_monitoring_results(self):
        """Save monitoring results to file"""
        results_path = Path("/home/danielfugisawa/pesquisa_prospect_gov/docs/risk-monitoring/regulatory-monitoring-results.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "compliance_score": self.calculate_compliance_score(),
            "last_updated": datetime.now().isoformat(),
            "regulatory_risks": {
                regulation.value: {
                    "changes_probability": risk.changes_probability.value,
                    "impact_severity": risk.impact_severity.value,
                    "compliance_status": risk.compliance_status.value,
                    "adaptation_time": risk.adaptation_time.value,
                    "monitoring_priority": risk.monitoring_priority,
                    "last_assessment": risk.last_assessment.isoformat()
                }
                for regulation, risk in self.regulatory_risks.items()
            },
            "recent_changes": [
                {
                    "regulation": change.regulation.value,
                    "change_type": change.change_type,
                    "description": change.description,
                    "effective_date": change.effective_date.isoformat(),
                    "impact_assessment": change.impact_assessment,
                    "compliance_requirements": change.compliance_requirements,
                    "detected_at": change.detected_at.isoformat() if change.detected_at else None
                }
                for change in self.recent_changes
            ],
            "compliance_gaps": [
                {
                    "regulation": gap.regulation.value,
                    "gap_description": gap.gap_description,
                    "severity": gap.severity.value,
                    "remediation_actions": gap.remediation_actions,
                    "estimated_cost": gap.estimated_cost,
                    "timeline": gap.timeline.value
                }
                for gap in self.compliance_gaps
            ]
        }
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Regulatory monitoring results saved to {results_path}")

if __name__ == "__main__":
    async def main():
        monitor = RegulatoryMonitor()
        
        # Monitor for changes
        changes = await monitor.monitor_regulatory_changes()
        
        # Save results
        await monitor.save_monitoring_results()
        
        # Generate and display report
        print("\n" + "="*80)
        print(monitor.generate_compliance_report())
        print("="*80)
        
        # Alert on critical issues
        compliance_score = monitor.calculate_compliance_score()
        if compliance_score < 70:
            print(f"\n🚨 COMPLIANCE ALERT: Score {compliance_score:.1f}/100 - Immediate action required!")
        
        critical_gaps = [gap for gap in monitor.compliance_gaps if gap.severity == ImpactLevel.SEVERE]
        if critical_gaps:
            print(f"\n⚠️ {len(critical_gaps)} CRITICAL compliance gaps detected!")
    
    asyncio.run(main())
