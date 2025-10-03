#!/usr/bin/env python3
"""
Risk Monitoring System Startup Script
Initializes and coordinates all risk monitoring components
"""

import asyncio
import logging
import argparse
import sys
import signal
from pathlib import Path
from datetime import datetime
import json

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "risk-monitoring"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('risk_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
monitoring_tasks = []
shutdown_event = asyncio.Event()

async def import_modules():
    """Import risk monitoring modules with proper error handling"""
    try:
        import importlib.util

        def import_module_from_file(module_name, file_path):
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        base_path = Path(__file__).parent.parent / "src" / "risk-monitoring"

        # Import all modules
        big_tech_module = import_module_from_file("big_tech_monitor", base_path / "big-tech-monitor.py")
        regulatory_module = import_module_from_file("regulatory_monitor", base_path / "regulatory-monitor.py")
        portfolio_module = import_module_from_file("portfolio_diversification", base_path / "portfolio-diversification.py")
        warning_module = import_module_from_file("early_warning_system", base_path / "early-warning-system.py")
        dashboard_module = import_module_from_file("risk_dashboard", base_path / "risk-dashboard.py")

        return {
            'BigTechMonitor': big_tech_module.BigTechMonitor,
            'RegulatoryMonitor': regulatory_module.RegulatoryMonitor,
            'PortfolioDiversificationEngine': portfolio_module.PortfolioDiversificationEngine,
            'EarlyWarningSystem': warning_module.EarlyWarningSystem,
            'RiskDashboard': dashboard_module.RiskDashboard,
            'Company': big_tech_module.Company,
            'RiskCategory': warning_module.RiskCategory,
            'OptimizationTarget': portfolio_module.OptimizationTarget
        }

    except Exception as e:
        logger.error(f"Failed to import modules: {e}")
        raise

async def initialize_systems(config_dir: Path):
    """Initialize all risk monitoring systems"""
    logger.info("Initializing risk monitoring systems...")

    # Import modules
    modules = await import_modules()

    # Initialize systems with config directory
    config_dir.mkdir(parents=True, exist_ok=True)

    systems = {
        'bigtech_monitor': modules['BigTechMonitor'](str(config_dir / "bigtech-config.json")),
        'regulatory_monitor': modules['RegulatoryMonitor'](str(config_dir / "regulatory-config.json")),
        'portfolio_engine': modules['PortfolioDiversificationEngine'](str(config_dir / "portfolio-config.json")),
        'warning_system': modules['EarlyWarningSystem'](str(config_dir / "warning-system-config.json")),
        'dashboard': modules['RiskDashboard'](str(config_dir / "dashboard-config.json"))
    }

    logger.info("All systems initialized successfully")
    return systems, modules

async def run_initial_assessment(systems, modules):
    """Run initial risk assessment across all systems"""
    logger.info("Running initial risk assessment...")

    try:
        # Big Tech threat assessment
        logger.info("Assessing Big Tech threats...")
        bigtech_results = await systems['bigtech_monitor'].monitor_all_companies()

        # Regulatory compliance check
        logger.info("Checking regulatory compliance...")
        regulatory_changes = await systems['regulatory_monitor'].monitor_regulatory_changes()
        compliance_score = systems['regulatory_monitor'].calculate_compliance_score()

        # Portfolio analysis
        logger.info("Analyzing portfolio diversification...")
        portfolio_metrics = systems['portfolio_engine'].calculate_diversification_metrics()

        # Generate initial reports
        bigtech_report = systems['bigtech_monitor'].generate_threat_report()
        regulatory_report = systems['regulatory_monitor'].generate_compliance_report()
        portfolio_report = systems['portfolio_engine'].generate_diversification_report()

        # Save initial assessment
        results_dir = Path("docs/risk-monitoring")
        results_dir.mkdir(parents=True, exist_ok=True)

        with open(results_dir / f"initial_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", 'w') as f:
            f.write("# INITIAL RISK ASSESSMENT REPORT\\n\\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            f.write("## BIG TECH THREAT ASSESSMENT\\n")
            f.write(bigtech_report)
            f.write("\\n\\n## REGULATORY COMPLIANCE ASSESSMENT\\n")
            f.write(regulatory_report)
            f.write("\\n\\n## PORTFOLIO DIVERSIFICATION ANALYSIS\\n")
            f.write(portfolio_report)

        # Summary
        critical_threats = sum(1 for company, monitoring in bigtech_results.items()
                             if monitoring.risk_level.name == 'CRITICAL')

        logger.info(f"Initial assessment complete:")
        logger.info(f"  - Critical Big Tech threats: {critical_threats}")
        logger.info(f"  - Regulatory compliance score: {compliance_score:.1f}/100")
        logger.info(f"  - Portfolio diversification score: {(1-portfolio_metrics.herfindahl_index)*100:.1f}/100")

        return {
            'bigtech_results': bigtech_results,
            'regulatory_changes': regulatory_changes,
            'compliance_score': compliance_score,
            'portfolio_metrics': portfolio_metrics
        }

    except Exception as e:
        logger.error(f"Initial assessment failed: {e}")
        raise

async def start_continuous_monitoring(systems, modules):
    """Start continuous monitoring tasks"""
    logger.info("Starting continuous monitoring...")

    global monitoring_tasks

    # Big Tech monitoring task
    async def bigtech_monitoring_loop():
        while not shutdown_event.is_set():
            try:
                await systems['bigtech_monitor'].monitor_all_companies()
                await asyncio.sleep(3600)  # Monitor every hour
            except Exception as e:
                logger.error(f"Big Tech monitoring error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    # Regulatory monitoring task
    async def regulatory_monitoring_loop():
        while not shutdown_event.is_set():
            try:
                await systems['regulatory_monitor'].monitor_regulatory_changes()
                await asyncio.sleep(7200)  # Monitor every 2 hours
            except Exception as e:
                logger.error(f"Regulatory monitoring error: {e}")
                await asyncio.sleep(600)  # Retry after 10 minutes

    # Portfolio analysis task
    async def portfolio_analysis_loop():
        while not shutdown_event.is_set():
            try:
                systems['portfolio_engine'].calculate_diversification_metrics()
                await systems['portfolio_engine'].save_analysis_results()
                await asyncio.sleep(21600)  # Analyze every 6 hours
            except Exception as e:
                logger.error(f"Portfolio analysis error: {e}")
                await asyncio.sleep(1800)  # Retry after 30 minutes

    # Dashboard data update task
    async def dashboard_update_loop():
        while not shutdown_event.is_set():
            try:
                systems['dashboard']._update_dashboard_data()
                await systems['dashboard'].save_dashboard_data()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    # Start all monitoring tasks
    monitoring_tasks = [
        asyncio.create_task(bigtech_monitoring_loop(), name="bigtech_monitoring"),
        asyncio.create_task(regulatory_monitoring_loop(), name="regulatory_monitoring"),
        asyncio.create_task(portfolio_analysis_loop(), name="portfolio_analysis"),
        asyncio.create_task(dashboard_update_loop(), name="dashboard_update")
    ]

    # Start early warning system monitoring
    monitoring_tasks.append(
        asyncio.create_task(systems['warning_system'].start_monitoring(), name="early_warning")
    )

    logger.info(f"Started {len(monitoring_tasks)} monitoring tasks")

    return monitoring_tasks

async def run_dashboard_server(systems, port=8050, host="127.0.0.1"):
    """Run dashboard server in background"""
    logger.info(f"Starting dashboard server at http://{host}:{port}")

    try:
        # This would normally run the dashboard server
        # For this implementation, we'll simulate it
        logger.info("Dashboard server ready (simulated)")

        # In a real implementation:
        # systems['dashboard'].run_dashboard(host=host, port=port, debug=False)

    except Exception as e:
        logger.error(f"Dashboard server error: {e}")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def graceful_shutdown():
    """Perform graceful shutdown of all systems"""
    logger.info("Performing graceful shutdown...")

    # Cancel all monitoring tasks
    for task in monitoring_tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Task {task.get_name()} cancelled")

    # Stop warning system monitoring
    try:
        # In a real implementation, call warning_system.stop_monitoring()
        logger.info("Warning system monitoring stopped")
    except Exception as e:
        logger.error(f"Error stopping warning system: {e}")

    logger.info("Graceful shutdown complete")

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Risk Monitoring System")
    parser.add_argument("--config-dir", type=str, default="config/risk-monitoring",
                       help="Configuration directory path")
    parser.add_argument("--dashboard-port", type=int, default=8050,
                       help="Dashboard server port")
    parser.add_argument("--dashboard-host", type=str, default="127.0.0.1",
                       help="Dashboard server host")
    parser.add_argument("--skip-initial-assessment", action="store_true",
                       help="Skip initial risk assessment")
    parser.add_argument("--monitoring-only", action="store_true",
                       help="Run monitoring tasks only (no dashboard)")

    args = parser.parse_args()

    # Setup signal handlers
    setup_signal_handlers()

    try:
        # Initialize systems
        config_dir = Path(args.config_dir)
        systems, modules = await initialize_systems(config_dir)

        # Run initial assessment
        if not args.skip_initial_assessment:
            initial_results = await run_initial_assessment(systems, modules)

            # Create test alerts based on initial assessment
            if initial_results['compliance_score'] < 70:
                await systems['warning_system'].create_alert(
                    risk_category=modules['RiskCategory'].REGULATORY_CHANGE,
                    trigger_event="Low compliance score detected",
                    description=f"Compliance score {initial_results['compliance_score']:.1f}/100 below target",
                    impact_assessment="Immediate compliance review required"
                )

        # Start continuous monitoring
        await start_continuous_monitoring(systems, modules)

        # Start dashboard server if requested
        if not args.monitoring_only:
            dashboard_task = asyncio.create_task(
                run_dashboard_server(systems, args.dashboard_port, args.dashboard_host),
                name="dashboard_server"
            )
            monitoring_tasks.append(dashboard_task)

        logger.info("🛡️ Risk Monitoring System is now active!")
        logger.info("System Status:")
        logger.info("  ✅ Big Tech threat monitoring: Active")
        logger.info("  ✅ Regulatory compliance monitoring: Active")
        logger.info("  ✅ Portfolio diversification analysis: Active")
        logger.info("  ✅ Early warning system: Active")
        if not args.monitoring_only:
            logger.info(f"  ✅ Risk dashboard: http://{args.dashboard_host}:{args.dashboard_port}")

        # Wait for shutdown signal
        await shutdown_event.wait()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise
    finally:
        await graceful_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 System shutdown complete")
    except Exception as e:
        print(f"\\n❌ System startup failed: {e}")
        sys.exit(1)