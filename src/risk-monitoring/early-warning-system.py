#!/usr/bin/env python3
"""
Early Warning System for Strategic Risk Management
Real-time monitoring and alerting for critical business threats
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import websockets
import aiohttp
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    GREEN = "Green"
    YELLOW = "Yellow"
    ORANGE = "Orange"
    RED = "Red"

class RiskCategory(Enum):
    BIG_TECH_THREAT = "Big Tech Threat"
    REGULATORY_CHANGE = "Regulatory Change"
    COMPETITIVE_THREAT = "Competitive Threat"
    ECONOMIC_DOWNTURN = "Economic Downturn"
    TECHNOLOGY_DISRUPTION = "Technology Disruption"
    CUSTOMER_CONCENTRATION = "Customer Concentration"
    SECURITY_BREACH = "Security Breach"
    OPERATIONAL_RISK = "Operational Risk"

class ResponseTime(Enum):
    IMMEDIATE = "0-1 hours"
    URGENT = "1-4 hours"
    PRIORITY = "4-24 hours"
    ROUTINE = "24-72 hours"

class StakeholderRole(Enum):
    CEO = "Chief Executive Officer"
    CTO = "Chief Technology Officer"
    CFO = "Chief Financial Officer"
    LEGAL = "Legal Counsel"
    SALES = "Sales Director"
    MARKETING = "Marketing Director"
    OPERATIONS = "Operations Manager"
    BOARD = "Board of Directors"

@dataclass
class Stakeholder:
    name: str
    role: StakeholderRole
    email: str
    phone: Optional[str] = None
    alert_preferences: Dict[RiskCategory, AlertSeverity] = None
    escalation_threshold: AlertSeverity = AlertSeverity.ORANGE

@dataclass
class Action:
    action_id: str
    description: str
    responsible_party: str
    deadline: datetime
    status: str = "Pending"
    priority: str = "Medium"

@dataclass
class RiskAlert:
    alert_id: str
    risk_category: RiskCategory
    severity: AlertSeverity
    trigger_event: str
    description: str
    impact_assessment: str
    recommended_actions: List[Action]
    timeline: ResponseTime
    stakeholders: List[Stakeholder]
    created_at: datetime
    last_updated: datetime
    status: str = "Active"
    escalation_count: int = 0
    auto_generated: bool = True

class AlertChannel(ABC):
    """Abstract base class for alert channels"""
    
    @abstractmethod
    async def send_alert(self, alert: RiskAlert, recipients: List[Stakeholder]) -> bool:
        pass

class EmailAlertChannel(AlertChannel):
    """Email alert channel implementation"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_alert(self, alert: RiskAlert, recipients: List[Stakeholder]) -> bool:
        try:
            # Create email content
            subject = f"🚨 {alert.severity.value} ALERT: {alert.risk_category.value}"
            
            html_body = self._create_alert_email(alert)
            
            # Send to recipients
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                for recipient in recipients:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = self.username
                    msg['To'] = recipient.email
                    
                    html_part = MIMEText(html_body, 'html')
                    msg.attach(html_part)
                    
                    server.send_message(msg)
            
            logger.info(f"Alert {alert.alert_id} sent to {len(recipients)} recipients via email")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert {alert.alert_id}: {e}")
            return False
    
    def _create_alert_email(self, alert: RiskAlert) -> str:
        """Create HTML email content for alert"""
        severity_colors = {
            AlertSeverity.GREEN: "#28a745",
            AlertSeverity.YELLOW: "#ffc107",
            AlertSeverity.ORANGE: "#fd7e14",
            AlertSeverity.RED: "#dc3545"
        }
        
        color = severity_colors.get(alert.severity, "#6c757d")
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 5px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin-top: 0;">
                    {alert.severity.value} RISK ALERT
                </h2>
                <h3>{alert.risk_category.value}</h3>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p><strong>Trigger Event:</strong> {alert.trigger_event}</p>
                <p><strong>Description:</strong> {alert.description}</p>
                <p><strong>Impact Assessment:</strong> {alert.impact_assessment}</p>
                <p><strong>Response Timeline:</strong> {alert.timeline.value}</p>
                <p><strong>Created:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h3>Recommended Actions:</h3>
            <ul>
            {''.join([f'<li><strong>{action.responsible_party}</strong>: {action.description} (Deadline: {action.deadline.strftime("%Y-%m-%d %H:%M")})</li>' for action in alert.recommended_actions])}
            </ul>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;">
                <p>Alert ID: {alert.alert_id}</p>
                <p>This is an automated alert from the Risk Management System.</p>
            </div>
        </body>
        </html>
        """

class SlackAlertChannel(AlertChannel):
    """Slack alert channel implementation"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_alert(self, alert: RiskAlert, recipients: List[Stakeholder]) -> bool:
        try:
            severity_emojis = {
                AlertSeverity.GREEN: "✅",
                AlertSeverity.YELLOW: "⚠️",
                AlertSeverity.ORANGE: "🟠",
                AlertSeverity.RED: "🚨"
            }
            
            emoji = severity_emojis.get(alert.severity, "📵")
            
            payload = {
                "text": f"{emoji} *{alert.severity.value} ALERT*: {alert.risk_category.value}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} {alert.severity.value} Risk Alert"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Category:*\n{alert.risk_category.value}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Timeline:*\n{alert.timeline.value}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Trigger:* {alert.trigger_event}\n*Description:* {alert.description}"
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Alert {alert.alert_id} sent to Slack")
                        return True
                    else:
                        logger.error(f"Failed to send Slack alert: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert {alert.alert_id}: {e}")
            return False

class SMSAlertChannel(AlertChannel):
    """SMS alert channel implementation (simulated)"""
    
    def __init__(self, api_key: str, service_url: str):
        self.api_key = api_key
        self.service_url = service_url
    
    async def send_alert(self, alert: RiskAlert, recipients: List[Stakeholder]) -> bool:
        try:
            message = f"🚨 {alert.severity.value} ALERT: {alert.risk_category.value}\n{alert.trigger_event}\nResponse needed: {alert.timeline.value}"
            
            # Simulate SMS sending (replace with actual SMS service)
            for recipient in recipients:
                if recipient.phone:
                    logger.info(f"SMS sent to {recipient.phone}: {message[:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert {alert.alert_id}: {e}")
            return False

class EarlyWarningSystem:
    def __init__(self, config_path: str = "/home/danielfugisawa/pesquisa_prospect_gov/config/risk-monitoring/warning-system-config.json"):
        self.config_path = Path(config_path)
        self.alert_channels: Dict[str, AlertChannel] = {}
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.alert_history: List[RiskAlert] = []
        self.trigger_conditions: Dict[str, Callable] = {}
        self.monitoring_tasks: List[asyncio.Task] = []
        self.load_config()
        self._setup_default_triggers()
        self._initialize_stakeholders()
        self._initialize_alert_channels()
    
    def load_config(self):
        """Load warning system configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._create_default_config()
            self.save_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default warning system configuration"""
        return {
            "alert_triggers": {
                "big_tech_announces_brazil_investment": {
                    "severity": "Red",
                    "response_time": "Immediate",
                    "stakeholders": ["CEO", "CTO", "SALES", "BOARD"]
                },
                "new_regulatory_proposal_affecting_edtech": {
                    "severity": "Orange",
                    "response_time": "Priority",
                    "stakeholders": ["CEO", "LEGAL", "OPERATIONS"]
                },
                "major_competitor_raises_funding_50m_plus": {
                    "severity": "Yellow",
                    "response_time": "Priority",
                    "stakeholders": ["CEO", "SALES", "MARKETING"]
                },
                "government_changes_procurement_rules": {
                    "severity": "Orange",
                    "response_time": "Urgent",
                    "stakeholders": ["CEO", "LEGAL", "SALES"]
                },
                "economic_indicators_suggest_budget_cuts": {
                    "severity": "Yellow",
                    "response_time": "Priority",
                    "stakeholders": ["CEO", "CFO", "SALES"]
                },
                "security_breach_in_education_sector": {
                    "severity": "Orange",
                    "response_time": "Urgent",
                    "stakeholders": ["CEO", "CTO", "LEGAL"]
                },
                "technology_paradigm_shift_detected": {
                    "severity": "Yellow",
                    "response_time": "Priority",
                    "stakeholders": ["CTO", "CEO"]
                }
            },
            "escalation_rules": {
                "no_response_within_timeline": "escalate_to_board",
                "severity_red_no_action_2_hours": "escalate_to_ceo",
                "multiple_alerts_same_category": "escalate_severity"
            },
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                },
                "sms": {
                    "enabled": False,
                    "service": "twilio"
                }
            },
            "monitoring_intervals": {
                "critical_threats": 300,  # 5 minutes
                "high_priority": 900,  # 15 minutes
                "medium_priority": 3600,  # 1 hour
                "low_priority": 86400  # 24 hours
            }
        }
    
    def save_config(self):
        """Save warning system configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _initialize_stakeholders(self):
        """Initialize stakeholder list"""
        stakeholders_data = [
            {"name": "CEO", "role": StakeholderRole.CEO, "email": "ceo@company.com", "phone": "+5511999999999"},
            {"name": "CTO", "role": StakeholderRole.CTO, "email": "cto@company.com", "phone": "+5511999999998"},
            {"name": "CFO", "role": StakeholderRole.CFO, "email": "cfo@company.com", "phone": "+5511999999997"},
            {"name": "Legal Counsel", "role": StakeholderRole.LEGAL, "email": "legal@company.com"},
            {"name": "Sales Director", "role": StakeholderRole.SALES, "email": "sales@company.com"},
            {"name": "Marketing Director", "role": StakeholderRole.MARKETING, "email": "marketing@company.com"},
            {"name": "Operations Manager", "role": StakeholderRole.OPERATIONS, "email": "ops@company.com"},
            {"name": "Board Chair", "role": StakeholderRole.BOARD, "email": "board@company.com"}
        ]
        
        for data in stakeholders_data:
            stakeholder = Stakeholder(
                name=data["name"],
                role=data["role"],
                email=data["email"],
                phone=data.get("phone"),
                alert_preferences={
                    RiskCategory.BIG_TECH_THREAT: AlertSeverity.YELLOW,
                    RiskCategory.REGULATORY_CHANGE: AlertSeverity.ORANGE,
                    RiskCategory.COMPETITIVE_THREAT: AlertSeverity.YELLOW,
                    RiskCategory.SECURITY_BREACH: AlertSeverity.ORANGE
                }
            )
            self.stakeholders[data["role"].value] = stakeholder
    
    def _initialize_alert_channels(self):
        """Initialize alert channels"""
        # Email channel (simulated credentials)
        if self.config["notification_channels"]["email"]["enabled"]:
            self.alert_channels["email"] = EmailAlertChannel(
                smtp_server=self.config["notification_channels"]["email"]["smtp_server"],
                smtp_port=self.config["notification_channels"]["email"]["smtp_port"],
                username="alerts@company.com",  # Replace with actual credentials
                password="app_password"  # Replace with actual credentials
            )
        
        # Slack channel
        if self.config["notification_channels"]["slack"]["enabled"]:
            self.alert_channels["slack"] = SlackAlertChannel(
                webhook_url=self.config["notification_channels"]["slack"]["webhook_url"]
            )
        
        # SMS channel
        if self.config["notification_channels"]["sms"]["enabled"]:
            self.alert_channels["sms"] = SMSAlertChannel(
                api_key="simulated_key",
                service_url="https://api.sms-service.com"
            )
    
    def _setup_default_triggers(self):
        """Setup default trigger conditions"""
        # Big Tech threat triggers
        self.trigger_conditions["big_tech_announces_brazil_investment"] = lambda data: (
            "Google" in data.get("title", "") or "Microsoft" in data.get("title", "") or 
            "Amazon" in data.get("title", "") or "Meta" in data.get("title", "") or 
            "Apple" in data.get("title", "")
        ) and (
            "Brazil" in data.get("content", "") or "educação" in data.get("content", "")
        ) and (
            "investment" in data.get("content", "").lower() or 
            "partnership" in data.get("content", "").lower()
        )
        
        # Regulatory change triggers
        self.trigger_conditions["new_regulatory_proposal_affecting_edtech"] = lambda data: (
            "lei" in data.get("content", "").lower() or "decreto" in data.get("content", "").lower()
        ) and (
            "edtech" in data.get("content", "").lower() or 
            "educação" in data.get("content", "").lower()
        )
        
        # Competitive threat triggers
        self.trigger_conditions["major_competitor_raises_funding_50m_plus"] = lambda data: (
            "funding" in data.get("content", "").lower() or 
            "investment" in data.get("content", "").lower()
        ) and (
            "education" in data.get("content", "").lower() or 
            "edtech" in data.get("content", "").lower()
        ) and any(
            amount in data.get("content", "") for amount in ["$50M", "$100M", "R$ 250M", "R$ 500M"]
        )
    
    async def create_alert(self, 
                          risk_category: RiskCategory,
                          trigger_event: str,
                          description: str,
                          impact_assessment: str,
                          severity: Optional[AlertSeverity] = None,
                          custom_actions: Optional[List[Action]] = None) -> RiskAlert:
        """Create a new risk alert"""
        
        alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{risk_category.name}"
        
        # Determine severity if not provided
        if severity is None:
            severity = self._calculate_alert_severity(risk_category, trigger_event, description)
        
        # Determine response timeline
        timeline = self._determine_response_timeline(severity)
        
        # Generate recommended actions
        if custom_actions:
            recommended_actions = custom_actions
        else:
            recommended_actions = self._generate_recommended_actions(risk_category, severity)
        
        # Identify stakeholders
        stakeholders = self._identify_alert_stakeholders(risk_category, severity)
        
        alert = RiskAlert(
            alert_id=alert_id,
            risk_category=risk_category,
            severity=severity,
            trigger_event=trigger_event,
            description=description,
            impact_assessment=impact_assessment,
            recommended_actions=recommended_actions,
            timeline=timeline,
            stakeholders=stakeholders,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        # Log alert creation
        logger.info(f"Created {severity.value} alert {alert_id} for {risk_category.value}")
        
        return alert
    
    def _calculate_alert_severity(self, risk_category: RiskCategory, trigger_event: str, description: str) -> AlertSeverity:
        """Calculate alert severity based on various factors"""
        # Base severity by category
        base_severity = {
            RiskCategory.BIG_TECH_THREAT: AlertSeverity.ORANGE,
            RiskCategory.REGULATORY_CHANGE: AlertSeverity.YELLOW,
            RiskCategory.COMPETITIVE_THREAT: AlertSeverity.YELLOW,
            RiskCategory.ECONOMIC_DOWNTURN: AlertSeverity.ORANGE,
            RiskCategory.SECURITY_BREACH: AlertSeverity.RED,
            RiskCategory.CUSTOMER_CONCENTRATION: AlertSeverity.ORANGE,
            RiskCategory.TECHNOLOGY_DISRUPTION: AlertSeverity.YELLOW,
            RiskCategory.OPERATIONAL_RISK: AlertSeverity.YELLOW
        }.get(risk_category, AlertSeverity.YELLOW)
        
        # Escalate based on keywords
        critical_keywords = ["immediate", "urgent", "crisis", "breach", "shutdown", "lawsuit"]
        high_keywords = ["major", "significant", "large", "acquisition", "partnership"]
        
        text_to_check = f"{trigger_event} {description}".lower()
        
        if any(keyword in text_to_check for keyword in critical_keywords):
            return AlertSeverity.RED
        elif any(keyword in text_to_check for keyword in high_keywords):
            if base_severity == AlertSeverity.YELLOW:
                return AlertSeverity.ORANGE
            elif base_severity == AlertSeverity.ORANGE:
                return AlertSeverity.RED
        
        return base_severity
    
    def _determine_response_timeline(self, severity: AlertSeverity) -> ResponseTime:
        """Determine response timeline based on severity"""
        timeline_map = {
            AlertSeverity.RED: ResponseTime.IMMEDIATE,
            AlertSeverity.ORANGE: ResponseTime.URGENT,
            AlertSeverity.YELLOW: ResponseTime.PRIORITY,
            AlertSeverity.GREEN: ResponseTime.ROUTINE
        }
        return timeline_map.get(severity, ResponseTime.PRIORITY)
    
    def _generate_recommended_actions(self, risk_category: RiskCategory, severity: AlertSeverity) -> List[Action]:
        """Generate recommended actions based on risk category and severity"""
        actions = []
        base_deadline = datetime.now() + timedelta(hours=24)
        
        if risk_category == RiskCategory.BIG_TECH_THREAT:
            if severity in [AlertSeverity.RED, AlertSeverity.ORANGE]:
                actions.extend([
                    Action(
                        action_id="BT001",
                        description="Accelerate customer acquisition in threatened segments",
                        responsible_party="Sales Director",
                        deadline=datetime.now() + timedelta(hours=48),
                        priority="Critical"
                    ),
                    Action(
                        action_id="BT002",
                        description="Review and strengthen competitive positioning",
                        responsible_party="CEO",
                        deadline=datetime.now() + timedelta(hours=24),
                        priority="Critical"
                    ),
                    Action(
                        action_id="BT003",
                        description="Evaluate strategic partnership opportunities",
                        responsible_party="CEO",
                        deadline=datetime.now() + timedelta(days=7),
                        priority="High"
                    )
                ])
        
        elif risk_category == RiskCategory.REGULATORY_CHANGE:
            actions.extend([
                Action(
                    action_id="RC001",
                    description="Assess compliance impact and requirements",
                    responsible_party="Legal Counsel",
                    deadline=datetime.now() + timedelta(hours=48),
                    priority="High"
                ),
                Action(
                    action_id="RC002",
                    description="Prepare compliance adaptation plan",
                    responsible_party="Operations Manager",
                    deadline=datetime.now() + timedelta(days=7),
                    priority="High"
                )
            ])
        
        elif risk_category == RiskCategory.COMPETITIVE_THREAT:
            actions.extend([
                Action(
                    action_id="CT001",
                    description="Analyze competitor capabilities and strategy",
                    responsible_party="Marketing Director",
                    deadline=datetime.now() + timedelta(days=3),
                    priority="Medium"
                ),
                Action(
                    action_id="CT002",
                    description="Review pricing and value proposition",
                    responsible_party="Sales Director",
                    deadline=datetime.now() + timedelta(days=5),
                    priority="Medium"
                )
            ])
        
        elif risk_category == RiskCategory.SECURITY_BREACH:
            actions.extend([
                Action(
                    action_id="SB001",
                    description="Immediate security audit and vulnerability assessment",
                    responsible_party="CTO",
                    deadline=datetime.now() + timedelta(hours=12),
                    priority="Critical"
                ),
                Action(
                    action_id="SB002",
                    description="Customer communication and transparency plan",
                    responsible_party="CEO",
                    deadline=datetime.now() + timedelta(hours=6),
                    priority="Critical"
                )
            ])
        
        return actions
    
    def _identify_alert_stakeholders(self, risk_category: RiskCategory, severity: AlertSeverity) -> List[Stakeholder]:
        """Identify stakeholders who should receive the alert"""
        stakeholders = []
        
        # Always include CEO for high severity alerts
        if severity in [AlertSeverity.RED, AlertSeverity.ORANGE]:
            stakeholders.append(self.stakeholders["Chief Executive Officer"])
        
        # Category-specific stakeholders
        category_stakeholders = {
            RiskCategory.BIG_TECH_THREAT: ["Chief Executive Officer", "Chief Technology Officer", "Sales Director"],
            RiskCategory.REGULATORY_CHANGE: ["Chief Executive Officer", "Legal Counsel", "Operations Manager"],
            RiskCategory.COMPETITIVE_THREAT: ["Sales Director", "Marketing Director"],
            RiskCategory.ECONOMIC_DOWNTURN: ["Chief Executive Officer", "Chief Financial Officer"],
            RiskCategory.SECURITY_BREACH: ["Chief Executive Officer", "Chief Technology Officer", "Legal Counsel"],
            RiskCategory.CUSTOMER_CONCENTRATION: ["Chief Executive Officer", "Sales Director"],
            RiskCategory.TECHNOLOGY_DISRUPTION: ["Chief Technology Officer", "Chief Executive Officer"],
            RiskCategory.OPERATIONAL_RISK: ["Operations Manager", "Chief Executive Officer"]
        }
        
        for role in category_stakeholders.get(risk_category, []):
            if role in self.stakeholders:
                stakeholder = self.stakeholders[role]
                if stakeholder not in stakeholders:
                    stakeholders.append(stakeholder)
        
        # Include board for critical alerts
        if severity == AlertSeverity.RED:
            board_member = self.stakeholders.get("Board of Directors")
            if board_member and board_member not in stakeholders:
                stakeholders.append(board_member)
        
        return stakeholders
    
    async def _send_alert_notifications(self, alert: RiskAlert):
        """Send alert notifications through all configured channels"""
        notification_tasks = []
        
        for channel_name, channel in self.alert_channels.items():
            task = asyncio.create_task(
                channel.send_alert(alert, alert.stakeholders),
                name=f"alert_{alert.alert_id}_{channel_name}"
            )
            notification_tasks.append(task)
        
        # Wait for all notifications to complete
        results = await asyncio.gather(*notification_tasks, return_exceptions=True)
        
        # Log results
        successful_channels = []
        failed_channels = []
        
        for i, result in enumerate(results):
            channel_name = list(self.alert_channels.keys())[i]
            if isinstance(result, Exception):
                failed_channels.append(channel_name)
                logger.error(f"Failed to send alert via {channel_name}: {result}")
            elif result:
                successful_channels.append(channel_name)
            else:
                failed_channels.append(channel_name)
        
        logger.info(f"Alert {alert.alert_id} sent via: {successful_channels}")
        if failed_channels:
            logger.warning(f"Alert {alert.alert_id} failed via: {failed_channels}")
    
    async def process_trigger_event(self, event_data: Dict[str, Any]) -> Optional[RiskAlert]:
        """Process a trigger event and create alert if conditions are met"""
        for trigger_name, condition_func in self.trigger_conditions.items():
            try:
                if condition_func(event_data):
                    logger.info(f"Trigger condition met: {trigger_name}")
                    
                    # Get trigger configuration
                    trigger_config = self.config["alert_triggers"].get(trigger_name, {})
                    
                    # Determine risk category from trigger name
                    risk_category = self._map_trigger_to_category(trigger_name)
                    
                    # Create alert
                    alert = await self.create_alert(
                        risk_category=risk_category,
                        trigger_event=trigger_name.replace('_', ' ').title(),
                        description=event_data.get("description", f"Triggered by: {trigger_name}"),
                        impact_assessment=event_data.get("impact", "Impact assessment pending"),
                        severity=AlertSeverity(trigger_config.get("severity", "Yellow"))
                    )
                    
                    return alert
                    
            except Exception as e:
                logger.error(f"Error processing trigger {trigger_name}: {e}")
        
        return None
    
    def _map_trigger_to_category(self, trigger_name: str) -> RiskCategory:
        """Map trigger name to risk category"""
        category_mapping = {
            "big_tech": RiskCategory.BIG_TECH_THREAT,
            "regulatory": RiskCategory.REGULATORY_CHANGE,
            "competitor": RiskCategory.COMPETITIVE_THREAT,
            "economic": RiskCategory.ECONOMIC_DOWNTURN,
            "security": RiskCategory.SECURITY_BREACH,
            "technology": RiskCategory.TECHNOLOGY_DISRUPTION
        }
        
        for keyword, category in category_mapping.items():
            if keyword in trigger_name.lower():
                return category
        
        return RiskCategory.OPERATIONAL_RISK
    
    async def start_monitoring(self):
        """Start continuous monitoring for trigger events"""
        logger.info("Starting Early Warning System monitoring...")
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_big_tech_threats(), name="big_tech_monitor"),
            asyncio.create_task(self._monitor_regulatory_changes(), name="regulatory_monitor"),
            asyncio.create_task(self._monitor_competitive_threats(), name="competitive_monitor"),
            asyncio.create_task(self._monitor_economic_indicators(), name="economic_monitor"),
            asyncio.create_task(self._escalation_monitor(), name="escalation_monitor")
        ]
        
        # Wait for monitoring tasks
        try:
            await asyncio.gather(*self.monitoring_tasks)
        except asyncio.CancelledError:
            logger.info("Monitoring cancelled")
    
    async def _monitor_big_tech_threats(self):
        """Monitor for Big Tech threat indicators"""
        while True:
            try:
                # Simulate monitoring (replace with actual monitoring logic)
                await asyncio.sleep(self.config["monitoring_intervals"]["critical_threats"])
                
                # Example: Check for Big Tech announcements
                # This would integrate with the BigTechMonitor from earlier
                logger.debug("Monitoring Big Tech threats...")
                
            except Exception as e:
                logger.error(f"Error in Big Tech monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_regulatory_changes(self):
        """Monitor for regulatory changes"""
        while True:
            try:
                await asyncio.sleep(self.config["monitoring_intervals"]["high_priority"])
                
                # Simulate regulatory monitoring
                logger.debug("Monitoring regulatory changes...")
                
            except Exception as e:
                logger.error(f"Error in regulatory monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_competitive_threats(self):
        """Monitor for competitive threats"""
        while True:
            try:
                await asyncio.sleep(self.config["monitoring_intervals"]["medium_priority"])
                
                # Simulate competitive monitoring
                logger.debug("Monitoring competitive threats...")
                
            except Exception as e:
                logger.error(f"Error in competitive monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_economic_indicators(self):
        """Monitor economic indicators"""
        while True:
            try:
                await asyncio.sleep(self.config["monitoring_intervals"]["low_priority"])
                
                # Simulate economic monitoring
                logger.debug("Monitoring economic indicators...")
                
            except Exception as e:
                logger.error(f"Error in economic monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _escalation_monitor(self):
        """Monitor alerts for escalation conditions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.now()
                
                for alert_id, alert in self.active_alerts.items():
                    # Check if alert needs escalation
                    time_since_creation = current_time - alert.created_at
                    
                    # Escalate Red alerts with no response after 2 hours
                    if (alert.severity == AlertSeverity.RED and 
                        time_since_creation > timedelta(hours=2) and 
                        alert.status == "Active"):
                        
                        await self._escalate_alert(alert, "No response within 2 hours for critical alert")
                    
                    # Escalate other alerts based on timeline
                    timeline_hours = {
                        ResponseTime.IMMEDIATE: 1,
                        ResponseTime.URGENT: 4,
                        ResponseTime.PRIORITY: 24,
                        ResponseTime.ROUTINE: 72
                    }
                    
                    threshold = timedelta(hours=timeline_hours.get(alert.timeline, 24))
                    if time_since_creation > threshold and alert.status == "Active":
                        await self._escalate_alert(alert, f"No response within {alert.timeline.value}")
                
            except Exception as e:
                logger.error(f"Error in escalation monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _escalate_alert(self, alert: RiskAlert, reason: str):
        """Escalate an alert to higher severity or broader stakeholder group"""
        logger.warning(f"Escalating alert {alert.alert_id}: {reason}")
        
        # Increase escalation count
        alert.escalation_count += 1
        alert.last_updated = datetime.now()
        
        # Escalate severity if possible
        severity_escalation = {
            AlertSeverity.GREEN: AlertSeverity.YELLOW,
            AlertSeverity.YELLOW: AlertSeverity.ORANGE,
            AlertSeverity.ORANGE: AlertSeverity.RED
        }
        
        if alert.severity in severity_escalation:
            alert.severity = severity_escalation[alert.severity]
        
        # Add board member for escalated alerts
        board_member = self.stakeholders.get("Board of Directors")
        if board_member and board_member not in alert.stakeholders:
            alert.stakeholders.append(board_member)
        
        # Send escalation notification
        await self._send_alert_notifications(alert)
    
    def stop_monitoring(self):
        """Stop all monitoring tasks"""
        logger.info("Stopping Early Warning System monitoring...")
        
        for task in self.monitoring_tasks:
            task.cancel()
        
        self.monitoring_tasks = []
    
    def get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status summary"""
        active_by_severity = {severity: 0 for severity in AlertSeverity}
        active_by_category = {category: 0 for category in RiskCategory}
        
        for alert in self.active_alerts.values():
            if alert.status == "Active":
                active_by_severity[alert.severity] += 1
                active_by_category[alert.risk_category] += 1
        
        return {
            "total_active_alerts": len([a for a in self.active_alerts.values() if a.status == "Active"]),
            "alerts_by_severity": {severity.value: count for severity, count in active_by_severity.items()},
            "alerts_by_category": {category.value: count for category, count in active_by_category.items()},
            "total_alerts_today": len([a for a in self.alert_history if a.created_at.date() == datetime.now().date()]),
            "escalated_alerts": len([a for a in self.active_alerts.values() if a.escalation_count > 0]),
            "last_updated": datetime.now().isoformat()
        }
    
    async def save_alert_data(self):
        """Save alert data to file"""
        alerts_path = Path("/home/danielfugisawa/pesquisa_prospect_gov/docs/risk-monitoring/early-warning-alerts.json")
        alerts_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert alerts to serializable format
        serializable_alerts = {
            "active_alerts": {
                alert_id: {
                    "alert_id": alert.alert_id,
                    "risk_category": alert.risk_category.value,
                    "severity": alert.severity.value,
                    "trigger_event": alert.trigger_event,
                    "description": alert.description,
                    "impact_assessment": alert.impact_assessment,
                    "timeline": alert.timeline.value,
                    "created_at": alert.created_at.isoformat(),
                    "last_updated": alert.last_updated.isoformat(),
                    "status": alert.status,
                    "escalation_count": alert.escalation_count,
                    "stakeholder_count": len(alert.stakeholders),
                    "action_count": len(alert.recommended_actions)
                }
                for alert_id, alert in self.active_alerts.items()
            },
            "alert_summary": self.get_alert_status(),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(alerts_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_alerts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Alert data saved to {alerts_path}")

if __name__ == "__main__":
    async def main():
        # Initialize Early Warning System
        ews = EarlyWarningSystem()
        
        # Test alert creation
        print("\n" + "="*80)
        print("EARLY WARNING SYSTEM - ALERT TESTING")
        print("="*80)
        
        # Create test alerts
        test_alerts = [
            {
                "category": RiskCategory.BIG_TECH_THREAT,
                "trigger": "Google announces $500M education investment in Brazil",
                "description": "Google has announced a major investment in Brazilian education technology, targeting government contracts.",
                "impact": "High threat to our primary market segment. Potential 30-50% revenue impact."
            },
            {
                "category": RiskCategory.REGULATORY_CHANGE,
                "trigger": "New LGPD interpretation affects educational data processing",
                "description": "ANPD released new guidance significantly restricting student data processing.",
                "impact": "Major compliance changes required. 60-90 day adaptation timeline."
            },
            {
                "category": RiskCategory.SECURITY_BREACH,
                "trigger": "Major security breach at competing EdTech platform",
                "description": "Competitor experienced data breach affecting 100,000+ student records.",
                "impact": "Reputation risk and increased security scrutiny. Opportunity for competitive advantage."
            }
        ]
        
        created_alerts = []
        for test_alert in test_alerts:
            alert = await ews.create_alert(
                risk_category=test_alert["category"],
                trigger_event=test_alert["trigger"],
                description=test_alert["description"],
                impact_assessment=test_alert["impact"]
            )
            created_alerts.append(alert)
            print(f"\n✅ Created {alert.severity.value} alert: {alert.alert_id}")
        
        # Display alert status
        print("\n" + "-"*80)
        status = ews.get_alert_status()
        print(f"Active Alerts: {status['total_active_alerts']}")
        print(f"Critical (Red): {status['alerts_by_severity']['Red']}")
        print(f"High (Orange): {status['alerts_by_severity']['Orange']}")
        print(f"Medium (Yellow): {status['alerts_by_severity']['Yellow']}")
        
        # Save alert data
        await ews.save_alert_data()
        
        print("\n🚨 Early Warning System initialized and alerts created!")
        print("Stakeholders have been notified via configured channels.")
        
        # Demonstrate escalation (simulate time passage)
        print("\n🕜 Simulating alert escalation...")
        if created_alerts:
            alert_to_escalate = created_alerts[0]
            alert_to_escalate.created_at = datetime.now() - timedelta(hours=3)  # Simulate 3 hours ago
            await ews._escalate_alert(alert_to_escalate, "Simulated escalation for demonstration")
            print(f"⬆️ Alert {alert_to_escalate.alert_id} escalated to {alert_to_escalate.severity.value}")
    
    asyncio.run(main())
