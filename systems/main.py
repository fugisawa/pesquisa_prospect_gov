"""
EdTech RADAR - Main Application Entry Point
==========================================

Main orchestration script for the EdTech market intelligence system.
Provides CLI interface and demonstrates core functionality.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from systems import (
    EdTechDataManager, EdTechScoringEngine, EdTechDashboardGenerator,
    EdTechReportGenerator, EdTechAnalysisOrchestrator, EdTechSampleDataGenerator
)


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('systems/logs/edtech_radar.log', mode='a')
        ]
    )


def create_core_services() -> tuple:
    """Initialize and return core service instances"""
    # Create storage directory
    Path("systems/data/storage").mkdir(parents=True, exist_ok=True)
    Path("systems/exports").mkdir(parents=True, exist_ok=True)
    Path("systems/logs").mkdir(parents=True, exist_ok=True)

    # Initialize services
    data_manager = EdTechDataManager("systems/data/storage")
    scoring_engine = EdTechScoringEngine()
    dashboard_generator = EdTechDashboardGenerator(data_manager)
    report_generator = EdTechReportGenerator(data_manager, scoring_engine)
    orchestrator = EdTechAnalysisOrchestrator(
        data_manager, scoring_engine, dashboard_generator, report_generator
    )
    sample_generator = EdTechSampleDataGenerator(data_manager)

    return (data_manager, scoring_engine, dashboard_generator,
            report_generator, orchestrator, sample_generator)


def generate_sample_data(args):
    """Generate sample data for testing"""
    print("🚀 Generating sample EdTech data...")

    _, _, _, _, _, sample_generator = create_core_services()

    sample_generator.populate_database_with_samples(
        company_count=args.companies,
        opportunity_count=args.opportunities
    )

    print("✅ Sample data generation completed!")


def run_portfolio_analysis(args):
    """Run full portfolio analysis"""
    print("📊 Running portfolio analysis...")

    services = create_core_services()
    data_manager, scoring_engine, dashboard_generator, report_generator, orchestrator, _ = services

    # Execute full portfolio analysis
    result = orchestrator.execute_full_portfolio_analysis()

    if result.status.value == "completed":
        print(f"✅ Portfolio analysis completed successfully!")
        print(f"📈 Results: {result.results}")
        print(f"📁 Generated files: {len(result.artifacts)} artifacts")
        for artifact in result.artifacts:
            print(f"   - {artifact}")
    else:
        print(f"❌ Portfolio analysis failed: {result.error_message}")


def run_company_scoring(args):
    """Run company scoring workflow"""
    print("🎯 Running company scoring...")

    services = create_core_services()
    data_manager, scoring_engine, dashboard_generator, report_generator, orchestrator, _ = services

    # Execute company scoring
    company_names = args.companies.split(',') if args.companies else None
    result = orchestrator.execute_company_batch_scoring(company_names)

    if result.status.value == "completed":
        print(f"✅ Company scoring completed!")
        print(f"📊 Scored {result.results['total_companies_processed']} companies")
        print(f"📈 Average score: {result.results['average_score']:.1f}")
    else:
        print(f"❌ Company scoring failed: {result.error_message}")


def run_market_analysis(args):
    """Run market analysis workflow"""
    print("🌍 Running market analysis...")

    services = create_core_services()
    data_manager, scoring_engine, dashboard_generator, report_generator, orchestrator, _ = services

    # Execute market analysis
    result = orchestrator.execute_market_analysis_workflow()

    if result.status.value == "completed":
        print(f"✅ Market analysis completed!")
        print(f"📊 Analyzed {result.results['executive_summary']['total_opportunities']} opportunities")
        print(f"💰 Total market size: {result.results['executive_summary']['total_addressable_market']}")
    else:
        print(f"❌ Market analysis failed: {result.error_message}")


def export_data(args):
    """Export data in specified format"""
    print(f"📤 Exporting data to {args.format}...")

    data_manager, _, _, _, _, _ = create_core_services()

    if args.format.lower() == 'csv':
        # Export companies and opportunities to CSV
        companies_file = data_manager.export_companies_csv()
        opportunities_file = data_manager.export_opportunities_csv()
        print(f"✅ Exported to: {companies_file}, {opportunities_file}")

    elif args.format.lower() == 'json':
        # Get portfolio summary and export as JSON
        summary = data_manager.get_portfolio_summary()
        if summary:
            import json
            output_file = f"systems/exports/portfolio_summary.json"
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"✅ Exported to: {output_file}")
        else:
            print("❌ No data available for export")

    else:
        print(f"❌ Unsupported format: {args.format}")


def dashboard_demo(args):
    """Generate dashboard demonstration"""
    print("📊 Creating dashboard demonstration...")

    services = create_core_services()
    data_manager, scoring_engine, dashboard_generator, _, _, _ = services

    # Load sample data (if exists)
    companies = data_manager.search_companies()

    if not companies:
        print("⚠️  No companies found. Generate sample data first with: python systems/main.py generate-data")
        return

    # Score companies
    scored_companies = scoring_engine.batch_score_companies(companies)
    companies, scores = zip(*scored_companies) if scored_companies else ([], [])

    if companies and scores:
        # Create dashboard
        dashboard = dashboard_generator.create_portfolio_overview_dashboard(
            list(companies), list(scores)
        )

        # Export dashboard
        output_file = dashboard_generator.export_dashboard_html(dashboard, "demo_dashboard")
        print(f"✅ Dashboard created: {output_file}")
        print("🌐 Open the HTML file in your browser to view the interactive dashboard")
    else:
        print("❌ No scored companies available for dashboard")


def show_status(args):
    """Show system status and statistics"""
    print("📋 EdTech RADAR System Status")
    print("=" * 40)

    data_manager, _, _, _, _, _ = create_core_services()

    # Get portfolio summary
    summary = data_manager.get_portfolio_summary()

    if summary:
        stats = summary.get('company_statistics', {})
        print(f"📊 Companies: {stats.get('total_companies', 0)}")
        print(f"💰 Total Funding: ${stats.get('total_funding', 0):,.0f}")
        print(f"👥 Average Employees: {stats.get('avg_employees', 0):.0f}")
        print(f"🎯 Average Confidence: {stats.get('avg_confidence', 0):.2f}")

        opp_stats = summary.get('opportunity_statistics', {})
        print(f"🌍 Market Opportunities: {opp_stats.get('total_opportunities', 0)}")
        print(f"📈 Average Growth Rate: {opp_stats.get('avg_growth_rate', 0):.1f}%")

        print("\n📊 Category Distribution:")
        for category in summary.get('category_distribution', [])[:5]:
            print(f"   {category['category']}: {category['count']} companies")

    else:
        print("❌ No data available. Generate sample data first.")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="EdTech RADAR - Market Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python systems/main.py generate-data --companies 50 --opportunities 10
  python systems/main.py portfolio-analysis
  python systems/main.py company-scoring --companies "EduTech Innovations,LearnSphere"
  python systems/main.py market-analysis
  python systems/main.py export --format csv
  python systems/main.py dashboard-demo
  python systems/main.py status
        """
    )

    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate sample data
    gen_parser = subparsers.add_parser('generate-data', help='Generate sample data')
    gen_parser.add_argument('--companies', type=int, default=50,
                           help='Number of sample companies to generate')
    gen_parser.add_argument('--opportunities', type=int, default=10,
                           help='Number of market opportunities to generate')
    gen_parser.set_defaults(func=generate_sample_data)

    # Portfolio analysis
    portfolio_parser = subparsers.add_parser('portfolio-analysis',
                                           help='Run full portfolio analysis')
    portfolio_parser.set_defaults(func=run_portfolio_analysis)

    # Company scoring
    scoring_parser = subparsers.add_parser('company-scoring', help='Run company scoring')
    scoring_parser.add_argument('--companies', type=str,
                               help='Comma-separated list of company names to score')
    scoring_parser.set_defaults(func=run_company_scoring)

    # Market analysis
    market_parser = subparsers.add_parser('market-analysis', help='Run market analysis')
    market_parser.set_defaults(func=run_market_analysis)

    # Export data
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--format', choices=['csv', 'json'], required=True,
                              help='Export format')
    export_parser.set_defaults(func=export_data)

    # Dashboard demo
    dashboard_parser = subparsers.add_parser('dashboard-demo',
                                           help='Generate dashboard demonstration')
    dashboard_parser.set_defaults(func=dashboard_demo)

    # Status
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=show_status)

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    if not args.command:
        parser.print_help()
        return

    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.log_level == 'DEBUG':
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()