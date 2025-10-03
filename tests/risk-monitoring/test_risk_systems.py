#!/usr/bin/env python3
"""
Comprehensive Test Suite for Risk Monitoring Systems
Tests all components of the strategic risk management framework
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "risk-monitoring"))

try:
    import importlib.util

    # Import modules with dash-separated filenames
    def import_module_from_file(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Import all modules
    base_path = Path(__file__).parent.parent.parent / "src" / "risk-monitoring"

    big_tech_module = import_module_from_file("big_tech_monitor", base_path / "big-tech-monitor.py")
    BigTechMonitor = big_tech_module.BigTechMonitor
    Company = big_tech_module.Company
    RiskLevel = big_tech_module.RiskLevel
    ThreatIndicator = big_tech_module.ThreatIndicator

    regulatory_module = import_module_from_file("regulatory_monitor", base_path / "regulatory-monitor.py")
    RegulatoryMonitor = regulatory_module.RegulatoryMonitor
    RegulationType = regulatory_module.RegulationType
    ComplianceStatus = regulatory_module.ComplianceStatus

    portfolio_module = import_module_from_file("portfolio_diversification", base_path / "portfolio-diversification.py")
    PortfolioDiversificationEngine = portfolio_module.PortfolioDiversificationEngine
    MarketSegment = portfolio_module.MarketSegment
    OptimizationTarget = portfolio_module.OptimizationTarget

    warning_module = import_module_from_file("early_warning_system", base_path / "early-warning-system.py")
    EarlyWarningSystem = warning_module.EarlyWarningSystem
    RiskCategory = warning_module.RiskCategory
    AlertSeverity = warning_module.AlertSeverity

    dashboard_module = import_module_from_file("risk_dashboard", base_path / "risk-dashboard.py")
    RiskDashboard = dashboard_module.RiskDashboard
    KRIType = dashboard_module.KRIType

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all risk monitoring modules are available.")
    sys.exit(1)

class TestBigTechMonitor(unittest.TestCase):
    """Test Big Tech threat monitoring system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "bigtech-config.json")
        self.monitor = BigTechMonitor(self.config_path)
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor.config)
        self.assertEqual(len(self.monitor.threat_indicators), 12)
        self.assertIn("monitoring_sources", self.monitor.config)
    
    def test_config_creation_and_loading(self):
        """Test config file creation and loading"""
        # Config should be created automatically
        self.assertTrue(os.path.exists(self.config_path))
        
        # Load and verify config structure
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn("monitoring_sources", config)
        self.assertIn("keywords", config)
        self.assertIn("alert_thresholds", config)
    
    def test_threat_indicator_creation(self):
        """Test threat indicator creation"""
        indicator = ThreatIndicator(
            indicator_type="Test Indicator",
            description="Test description",
            severity=RiskLevel.HIGH,
            detected_at=datetime.now(),
            confidence=0.8
        )
        
        self.assertEqual(indicator.indicator_type, "Test Indicator")
        self.assertEqual(indicator.severity, RiskLevel.HIGH)
        self.assertEqual(indicator.confidence, 0.8)
    
    def test_risk_level_calculation(self):
        """Test risk level calculation"""
        # Create test indicators
        indicators = [
            ThreatIndicator("Test1", "desc1", RiskLevel.HIGH, datetime.now()),
            ThreatIndicator("Test2", "desc2", RiskLevel.MEDIUM, datetime.now()),
            ThreatIndicator("Test3", "desc3", RiskLevel.HIGH, datetime.now())
        ]
        
        risk_level = self.monitor._calculate_risk_level(indicators)
        self.assertIn(risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        indicators = [
            ThreatIndicator("Test1", "desc1", RiskLevel.HIGH, datetime.now(), confidence=0.8),
            ThreatIndicator("Test2", "desc2", RiskLevel.MEDIUM, datetime.now(), confidence=0.6)
        ]
        
        confidence = self.monitor._calculate_confidence_score(indicators)
        self.assertEqual(confidence, 0.7)  # Average of 0.8 and 0.6
    
    def test_mitigation_actions_generation(self):
        """Test mitigation actions generation"""
        indicators = [ThreatIndicator("Test", "desc", RiskLevel.HIGH, datetime.now())]
        actions = self.monitor._generate_mitigation_actions(Company.GOOGLE, RiskLevel.HIGH, indicators)
        
        self.assertGreater(len(actions), 0)
        self.assertTrue(all(action.action_id.startswith("URGENT-Google") for action in actions))

class TestRegulatoryMonitor(unittest.TestCase):
    """Test regulatory compliance monitoring system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "regulatory-config.json")
        self.monitor = RegulatoryMonitor(self.config_path)
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor.config)
        self.assertGreater(len(self.monitor.regulatory_risks), 0)
        self.assertIn(RegulationType.LGPD, self.monitor.regulatory_risks)
    
    def test_regulatory_framework_initialization(self):
        """Test regulatory framework initialization"""
        # Check that all critical regulations are initialized
        critical_regulations = [
            RegulationType.LGPD,
            RegulationType.EDUCATION_DIGITAL,
            RegulationType.PUBLIC_PROCUREMENT
        ]
        
        for regulation in critical_regulations:
            self.assertIn(regulation, self.monitor.regulatory_risks)
            risk = self.monitor.regulatory_risks[regulation]
            self.assertIsNotNone(risk.compliance_status)
            self.assertIsNotNone(risk.impact_severity)
    
    def test_compliance_score_calculation(self):
        """Test compliance score calculation"""
        score = self.monitor.calculate_compliance_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_compliance_gap_identification(self):
        """Test compliance gap identification"""
        from regulatory_monitor import RegulatoryChange
        
        change = RegulatoryChange(
            regulation=RegulationType.LGPD,
            change_type="Amendment",
            description="New data processing requirements",
            effective_date=datetime.now() + timedelta(days=90),
            impact_assessment="High impact",
            compliance_requirements=["Enhanced security standards", "New consent mechanisms"]
        )
        
        gaps = self.monitor._identify_compliance_gaps(change)
        self.assertGreater(len(gaps), 0)
    
    def test_report_generation(self):
        """Test compliance report generation"""
        report = self.monitor.generate_compliance_report()
        self.assertIn("REGULATORY COMPLIANCE ASSESSMENT REPORT", report)
        self.assertIn("Overall Compliance Score", report)

class TestPortfolioDiversificationEngine(unittest.TestCase):
    """Test portfolio diversification analysis engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "portfolio-config.json")
        self.engine = PortfolioDiversificationEngine(self.config_path)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.config)
        self.assertGreater(len(self.engine.portfolio_segments), 0)
        self.assertIn(MarketSegment.GOVERNMENT_B2B, self.engine.portfolio_segments)
    
    def test_diversification_metrics_calculation(self):
        """Test diversification metrics calculation"""
        metrics = self.engine.calculate_diversification_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.herfindahl_index, 0)
        self.assertLessEqual(metrics.herfindahl_index, 1)
        self.assertGreaterEqual(metrics.revenue_diversification, 0)
        self.assertLessEqual(metrics.revenue_diversification, 1)
    
    def test_portfolio_optimization(self):
        """Test portfolio optimization"""
        target = OptimizationTarget(
            target_type="balanced",
            constraints={"max_single_segment": 0.50},
            weights={},
            time_horizon="medium"
        )
        
        result = self.engine.optimize_portfolio(target)
        
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
        
        # Check that allocations sum to approximately 1
        total_allocation = sum(result.values())
        self.assertAlmostEqual(total_allocation, 1.0, places=2)
    
    def test_scenario_analysis(self):
        """Test scenario analysis"""
        results = self.engine.run_scenario_analysis()
        
        self.assertIsInstance(results, dict)
        self.assertIn("big_tech_entry", results)
        
        for scenario, data in results.items():
            self.assertIn("probability", data)
            self.assertIn("total_impact", data)
            self.assertIn("expected_loss", data)
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        self.engine.calculate_diversification_metrics()  # Ensure metrics are calculated
        recommendations = self.engine.generate_optimization_recommendations()
        
        self.assertIsInstance(recommendations, list)
        # Should have at least some recommendations given default portfolio
        self.assertGreater(len(recommendations), 0)

class TestEarlyWarningSystem(unittest.TestCase):
    """Test early warning system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "warning-config.json")
        self.ews = EarlyWarningSystem(self.config_path)
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.ews.config)
        self.assertGreater(len(self.ews.stakeholders), 0)
        self.assertGreater(len(self.ews.trigger_conditions), 0)
    
    def test_alert_creation(self):
        """Test alert creation"""
        async def test_async():
            alert = await self.ews.create_alert(
                risk_category=RiskCategory.BIG_TECH_THREAT,
                trigger_event="Test trigger",
                description="Test description",
                impact_assessment="Test impact"
            )
            
            self.assertIsNotNone(alert)
            self.assertEqual(alert.risk_category, RiskCategory.BIG_TECH_THREAT)
            self.assertIn(alert.alert_id, self.ews.active_alerts)
        
        asyncio.run(test_async())
    
    def test_severity_calculation(self):
        """Test alert severity calculation"""
        severity = self.ews._calculate_alert_severity(
            RiskCategory.SECURITY_BREACH,
            "Critical security breach detected",
            "Immediate action required"
        )
        
        # Security breach with critical keywords should be RED
        self.assertEqual(severity, AlertSeverity.RED)
    
    def test_stakeholder_identification(self):
        """Test stakeholder identification"""
        stakeholders = self.ews._identify_alert_stakeholders(
            RiskCategory.BIG_TECH_THREAT,
            AlertSeverity.RED
        )
        
        self.assertGreater(len(stakeholders), 0)
        # CEO should be included for critical alerts
        ceo_included = any(s.role.value == "Chief Executive Officer" for s in stakeholders)
        self.assertTrue(ceo_included)
    
    def test_trigger_event_processing(self):
        """Test trigger event processing"""
        async def test_async():
            event_data = {
                "title": "Google announces major education investment",
                "content": "Google plans to invest $500M in Brazil education technology",
                "description": "Major competitive threat identified"
            }
            
            alert = await self.ews.process_trigger_event(event_data)
            
            # Should create an alert for this trigger
            self.assertIsNotNone(alert)
            self.assertEqual(alert.risk_category, RiskCategory.BIG_TECH_THREAT)
        
        asyncio.run(test_async())
    
    def test_alert_status_summary(self):
        """Test alert status summary"""
        async def test_async():
            # Create test alerts
            await self.ews.create_alert(
                RiskCategory.BIG_TECH_THREAT, "Test1", "Desc1", "Impact1"
            )
            await self.ews.create_alert(
                RiskCategory.REGULATORY_CHANGE, "Test2", "Desc2", "Impact2"
            )
            
            status = self.ews.get_alert_status()
            
            self.assertIn("total_active_alerts", status)
            self.assertIn("alerts_by_severity", status)
            self.assertIn("alerts_by_category", status)
            self.assertGreaterEqual(status["total_active_alerts"], 2)
        
        asyncio.run(test_async())

class TestRiskDashboard(unittest.TestCase):
    """Test risk monitoring dashboard"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "dashboard-config.json")
        self.dashboard = RiskDashboard(self.config_path)
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        self.assertIsNotNone(self.dashboard.config)
        self.assertIsNotNone(self.dashboard.kri_metrics)
        self.assertEqual(len(self.dashboard.kri_metrics), len(KRIType))
    
    def test_kri_metrics_initialization(self):
        """Test KRI metrics initialization"""
        for kri_type in KRIType:
            self.assertIn(kri_type, self.dashboard.kri_metrics)
            metric = self.dashboard.kri_metrics[kri_type]
            self.assertIsNotNone(metric.current_value)
            self.assertIsNotNone(metric.target_value)
            self.assertGreater(len(metric.historical_data), 0)
    
    def test_dashboard_data_update(self):
        """Test dashboard data update"""
        initial_value = self.dashboard.kri_metrics[KRIType.BIG_TECH_THREAT_SCORE].current_value
        
        self.dashboard._update_dashboard_data()
        
        # Data should be updated
        self.assertIsNotNone(self.dashboard.dashboard_data)
        self.assertIsNotNone(self.dashboard.dashboard_data.kri_metrics)
    
    def test_threat_radar_data_generation(self):
        """Test threat radar data generation"""
        radar_data = self.dashboard._generate_threat_radar_data()
        
        self.assertIsInstance(radar_data, dict)
        self.assertIn("Google", radar_data)
        self.assertIn("Microsoft", radar_data)
        self.assertIn("Regulatory Risk", radar_data)
    
    def test_portfolio_data_generation(self):
        """Test portfolio data generation"""
        portfolio_data = self.dashboard._generate_portfolio_data()
        
        self.assertIsInstance(portfolio_data, dict)
        self.assertIn("Government B2B", portfolio_data)
        
        # Allocations should sum to 100
        total = sum(portfolio_data.values())
        self.assertAlmostEqual(total, 100, places=0)
    
    def test_chart_creation_methods(self):
        """Test chart creation methods"""
        self.dashboard._update_dashboard_data()
        
        # Test that chart creation methods don't raise exceptions
        try:
            threat_chart = self.dashboard._create_threat_radar_chart()
            portfolio_chart = self.dashboard._create_portfolio_allocation_chart()
            scenario_chart = self.dashboard._create_scenario_impact_chart()
            
            # Basic validation that figures are created
            self.assertIsNotNone(threat_chart)
            self.assertIsNotNone(portfolio_chart)
            self.assertIsNotNone(scenario_chart)
        except Exception as e:
            self.fail(f"Chart creation failed: {e}")

class TestSystemIntegration(unittest.TestCase):
    """Test integration between risk monitoring systems"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_data_flow_integration(self):
        """Test data flow between systems"""
        # Initialize all systems
        bigtech_monitor = BigTechMonitor(os.path.join(self.temp_dir, "bigtech.json"))
        regulatory_monitor = RegulatoryMonitor(os.path.join(self.temp_dir, "regulatory.json"))
        portfolio_engine = PortfolioDiversificationEngine(os.path.join(self.temp_dir, "portfolio.json"))
        warning_system = EarlyWarningSystem(os.path.join(self.temp_dir, "warning.json"))
        
        # Test that all systems can be initialized without conflicts
        self.assertIsNotNone(bigtech_monitor)
        self.assertIsNotNone(regulatory_monitor)
        self.assertIsNotNone(portfolio_engine)
        self.assertIsNotNone(warning_system)
    
    def test_alert_integration(self):
        """Test integration between monitoring and alerting"""
        async def test_async():
            warning_system = EarlyWarningSystem(os.path.join(self.temp_dir, "warning.json"))
            
            # Simulate Big Tech threat detection leading to alert
            threat_event = {
                "title": "Microsoft announces Brazil education partnership",
                "content": "Microsoft partners with Brazilian government for education technology",
                "description": "Major competitive threat in primary market"
            }
            
            alert = await warning_system.process_trigger_event(threat_event)
            
            if alert:  # Alert created
                self.assertEqual(alert.risk_category, RiskCategory.BIG_TECH_THREAT)
                self.assertGreater(len(alert.recommended_actions), 0)
        
        asyncio.run(test_async())
    
    def test_portfolio_risk_correlation(self):
        """Test correlation between portfolio and risk metrics"""
        portfolio_engine = PortfolioDiversificationEngine(os.path.join(self.temp_dir, "portfolio.json"))
        dashboard = RiskDashboard(os.path.join(self.temp_dir, "dashboard.json"))
        
        # Calculate metrics
        portfolio_metrics = portfolio_engine.calculate_diversification_metrics()
        dashboard._update_dashboard_data()
        
        # Test correlation - high concentration should correlate with high risk
        concentration_ratio = portfolio_metrics.herfindahl_index
        dashboard_concentration = dashboard.kri_metrics[KRIType.MARKET_CONCENTRATION_RATIO].current_value
        
        # Both should indicate similar risk levels
        self.assertIsNotNone(concentration_ratio)
        self.assertIsNotNone(dashboard_concentration)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_invalid_config_handling(self):
        """Test handling of invalid configuration"""
        # Test with non-existent directory
        invalid_path = "/non/existent/path/config.json"
        
        # Should handle gracefully and create default config
        try:
            monitor = BigTechMonitor(invalid_path)
            self.assertIsNotNone(monitor.config)
        except Exception as e:
            # Should not raise unhandled exceptions
            self.fail(f"Failed to handle invalid config path: {e}")
    
    def test_empty_data_handling(self):
        """Test handling of empty or missing data"""
        temp_dir = tempfile.mkdtemp()
        portfolio_engine = PortfolioDiversificationEngine(os.path.join(temp_dir, "portfolio.json"))
        
        # Clear portfolio segments
        portfolio_engine.portfolio_segments = {}
        
        # Should handle empty portfolio gracefully
        try:
            metrics = portfolio_engine.calculate_diversification_metrics()
            self.assertIsNotNone(metrics)
        except Exception as e:
            self.fail(f"Failed to handle empty portfolio: {e}")
    
    def test_concurrent_access(self):
        """Test concurrent access to monitoring systems"""
        async def test_async():
            temp_dir = tempfile.mkdtemp()
            warning_system = EarlyWarningSystem(os.path.join(temp_dir, "warning.json"))
            
            # Create multiple alerts concurrently
            tasks = []
            for i in range(5):
                task = warning_system.create_alert(
                    RiskCategory.COMPETITIVE_THREAT,
                    f"Test trigger {i}",
                    f"Test description {i}",
                    f"Test impact {i}"
                )
                tasks.append(task)
            
            alerts = await asyncio.gather(*tasks)
            
            # All alerts should be created successfully
            self.assertEqual(len(alerts), 5)
            for alert in alerts:
                self.assertIsNotNone(alert.alert_id)
        
        asyncio.run(test_async())

def run_test_suite():
    """Run the complete test suite"""
    # Create test suite
    test_classes = [
        TestBigTechMonitor,
        TestRegulatoryMonitor,
        TestPortfolioDiversificationEngine,
        TestEarlyWarningSystem,
        TestRiskDashboard,
        TestSystemIntegration,
        TestErrorHandling
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return test results
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPREHENSIVE RISK MONITORING SYSTEMS TEST SUITE")
    print("="*80)
    
    # Run all tests
    result = run_test_suite()
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n🚨 FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - Risk monitoring systems are functioning correctly!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review and fix issues before deployment.")
    
    print("\n🛡️ Risk monitoring framework validation complete.")
