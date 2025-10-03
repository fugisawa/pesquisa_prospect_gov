"""
EdTech RADAR - Sample Data Generator
===================================

Generates realistic sample data for testing and demonstration purposes.
Creates mock EdTech companies, market opportunities, and analysis scenarios.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from systems.models.edtech_schemas import (
    CompanyProfile, MarketOpportunity, AnalysisScore,
    EdTechCategory, TargetAudience, BusinessModel, FundingStage,
    TechnologyStack, Funding, CompanyMetrics, GeographicPresence, Product
)
from systems.data.data_manager import EdTechDataManager


class EdTechSampleDataGenerator:
    """Generate realistic sample data for EdTech analysis"""

    def __init__(self, data_manager: EdTechDataManager):
        self.data_manager = data_manager

        # Sample data pools
        self.company_names = [
            "EduTech Innovations", "LearnSphere", "SkillCraft", "BrainBoost",
            "MindBridge", "ClassConnect", "StudySync", "EduFlow", "LearnLab",
            "WisdomWorks", "TutorTech", "SkillBridge", "EduVerse", "LearnLogic",
            "SmartStudy", "EduNext", "TeachTech", "LearnLink", "StudySmart",
            "EduGenius", "SkillStream", "LearnPath", "EduMaster", "TutorBot",
            "ClassCraft", "StudyForge", "EduPilot", "LearnQuest", "SkillHive",
            "BrainTech", "EduRise", "LearnCore", "StudyWave", "TutorAI",
            "ClassHub", "EduSpark", "LearnFlex", "SkillNet", "StudyPro",
            "EduZen", "LearnBoost", "ClassIQ", "StudyGenie", "TutorMax",
            "EduShift", "LearnEdge", "SkillForge", "StudyPlus", "ClassAI"
        ]

        self.tech_stacks = {
            'frontend': ['React', 'Vue.js', 'Angular', 'Flutter', 'React Native', 'Svelte', 'Next.js'],
            'backend': ['Node.js', 'Python', 'Java', 'Go', 'Ruby', 'PHP', 'C#', 'Scala'],
            'database': ['MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Firebase', 'DynamoDB'],
            'ai_ml': ['TensorFlow', 'PyTorch', 'OpenAI GPT', 'Hugging Face', 'spaCy', 'scikit-learn', 'BERT'],
            'cloud_platform': ['AWS', 'Google Cloud', 'Azure', 'Heroku', 'Vercel', 'DigitalOcean'],
            'mobile': ['iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic']
        }

        self.headquarters_locations = [
            "San Francisco, CA", "New York, NY", "London, UK", "Tel Aviv, Israel",
            "Singapore", "Toronto, Canada", "Berlin, Germany", "Sydney, Australia",
            "Boston, MA", "Seattle, WA", "Austin, TX", "Chicago, IL",
            "Los Angeles, CA", "Amsterdam, Netherlands", "Stockholm, Sweden",
            "Paris, France", "Barcelona, Spain", "Dublin, Ireland", "Zurich, Switzerland"
        ]

        self.investors = [
            "Andreessen Horowitz", "Sequoia Capital", "General Catalyst", "Bessemer Venture Partners",
            "New Enterprise Associates", "Accel", "Greylock Partners", "Kleiner Perkins",
            "Index Ventures", "Insight Partners", "Tiger Global", "SoftBank Vision Fund",
            "Reach Capital", "GSV Ventures", "Owl Ventures", "Rethink Education",
            "Emerge Education", "LearnStart", "NewSchools Venture Fund", "TPG Growth"
        ]

        self.competitors_pool = [
            "Coursera", "Udemy", "Khan Academy", "Duolingo", "Skillshare", "MasterClass",
            "Codecademy", "Pluralsight", "LinkedIn Learning", "edX", "FutureLearn",
            "Teachable", "Thinkific", "Canvas", "Blackboard", "Zoom", "Google Classroom",
            "Microsoft Teams", "Slack", "Notion", "Figma", "Adobe Creative Suite"
        ]

        self.market_opportunities = [
            {
                'name': 'AI-Powered Personalized Learning',
                'category': EdTechCategory.SKILL_DEVELOPMENT,
                'description': 'Adaptive learning platforms using AI to personalize education content'
            },
            {
                'name': 'Corporate Microlearning Solutions',
                'category': EdTechCategory.CORPORATE_TRAINING,
                'description': 'Bite-sized learning modules for professional development'
            },
            {
                'name': 'VR/AR Educational Experiences',
                'category': EdTechCategory.EDUCATIONAL_CONTENT,
                'description': 'Immersive virtual and augmented reality learning environments'
            },
            {
                'name': 'Language Learning for Emerging Markets',
                'category': EdTechCategory.LANGUAGE_LEARNING,
                'description': 'Affordable language learning solutions for developing countries'
            },
            {
                'name': 'Blockchain-Based Credentialing',
                'category': EdTechCategory.ASSESSMENT_TOOLS,
                'description': 'Secure, verifiable digital credentials and certifications'
            }
        ]

    def generate_sample_companies(self, count: int = 50) -> List[CompanyProfile]:
        """Generate a specified number of sample EdTech companies"""

        companies = []

        for i in range(count):
            company = self._create_sample_company(i)
            companies.append(company)

        return companies

    def generate_sample_opportunities(self, count: int = 10) -> List[MarketOpportunity]:
        """Generate sample market opportunities"""

        opportunities = []

        for i in range(count):
            opportunity = self._create_sample_opportunity(i)
            opportunities.append(opportunity)

        return opportunities

    def populate_database_with_samples(self, company_count: int = 50, opportunity_count: int = 10):
        """Populate the database with sample data"""

        print(f"Generating {company_count} sample companies...")
        companies = self.generate_sample_companies(company_count)

        print("Adding companies to database...")
        success_count = 0
        for company in companies:
            if self.data_manager.add_company(company):
                success_count += 1

        print(f"Successfully added {success_count}/{len(companies)} companies to database")

        print(f"Generating {opportunity_count} sample market opportunities...")
        opportunities = self.generate_sample_opportunities(opportunity_count)

        print("Adding opportunities to database...")
        opp_success_count = 0
        for opportunity in opportunities:
            if self.data_manager.add_opportunity(opportunity):
                opp_success_count += 1

        print(f"Successfully added {opp_success_count}/{len(opportunities)} opportunities to database")

        print("Sample data generation completed!")

    def _create_sample_company(self, index: int) -> CompanyProfile:
        """Create a single sample company with realistic data"""

        # Basic information
        name = self.company_names[index % len(self.company_names)]
        if index >= len(self.company_names):
            name += f" {index // len(self.company_names) + 1}"

        website = f"https://{name.lower().replace(' ', '').replace('', '')}.com"
        founded = random.randint(2010, 2023)

        # Categories and audience
        category = [random.choice(list(EdTechCategory))]
        if random.random() < 0.3:  # 30% chance of multiple categories
            category.append(random.choice(list(EdTechCategory)))

        target_audience = random.sample(list(TargetAudience), random.randint(1, 3))
        business_model = random.sample(list(BusinessModel), random.randint(1, 2))

        # Technology stack
        tech_stack = TechnologyStack(
            frontend=random.sample(self.tech_stacks['frontend'], random.randint(1, 3)),
            backend=random.sample(self.tech_stacks['backend'], random.randint(1, 2)),
            database=random.sample(self.tech_stacks['database'], random.randint(1, 2)),
            ai_ml=random.sample(self.tech_stacks['ai_ml'], random.randint(0, 3)),
            cloud_platform=random.sample(self.tech_stacks['cloud_platform'], random.randint(1, 2)),
            mobile=random.sample(self.tech_stacks['mobile'], random.randint(0, 2))
        )

        # Funding information
        funding_stage = random.choice(list(FundingStage))
        funding_ranges = {
            FundingStage.BOOTSTRAP: (0, 100000),
            FundingStage.PRE_SEED: (50000, 500000),
            FundingStage.SEED: (300000, 3000000),
            FundingStage.SERIES_A: (2000000, 20000000),
            FundingStage.SERIES_B: (10000000, 50000000),
            FundingStage.SERIES_C: (25000000, 100000000),
            FundingStage.LATER_STAGE: (50000000, 500000000)
        }

        min_funding, max_funding = funding_ranges.get(funding_stage, (0, 1000000))
        total_raised = random.randint(min_funding, max_funding)

        funding = Funding(
            total_raised=total_raised,
            latest_round=funding_stage.value,
            latest_round_amount=total_raised * random.uniform(0.3, 0.8),
            latest_round_date=datetime.now() - timedelta(days=random.randint(30, 365)),
            investors=random.sample(self.investors, random.randint(1, 4)),
            stage=funding_stage
        )

        # Company metrics
        employee_ranges = {
            FundingStage.BOOTSTRAP: (1, 10),
            FundingStage.PRE_SEED: (2, 15),
            FundingStage.SEED: (5, 30),
            FundingStage.SERIES_A: (15, 75),
            FundingStage.SERIES_B: (50, 200),
            FundingStage.SERIES_C: (100, 500),
            FundingStage.LATER_STAGE: (200, 2000)
        }

        min_employees, max_employees = employee_ranges.get(funding_stage, (1, 50))
        employees = random.randint(min_employees, max_employees)

        # User base correlates with funding and company maturity
        user_base = random.randint(
            max(1000, employees * 100),
            min(10000000, employees * 5000)
        )

        metrics = CompanyMetrics(
            employees_count=employees,
            annual_revenue=random.randint(total_raised // 10, total_raised // 2) if total_raised > 0 else 0,
            user_base=user_base,
            active_users=int(user_base * random.uniform(0.1, 0.8)),
            growth_rate=random.uniform(10, 200),
            market_share=random.uniform(0.1, 15) if random.random() < 0.3 else None,
            retention_rate=random.uniform(60, 95)
        )

        # Geographic presence
        geo_presence = GeographicPresence(
            headquarters=random.choice(self.headquarters_locations),
            primary_markets=random.sample([
                "United States", "Canada", "United Kingdom", "Germany", "France",
                "Australia", "Singapore", "India", "Brazil", "Mexico"
            ], random.randint(1, 4)),
            expansion_markets=random.sample([
                "Japan", "South Korea", "China", "Netherlands", "Sweden",
                "Spain", "Italy", "Argentina", "Chile", "South Africa"
            ], random.randint(0, 3))
        )

        # Products
        product_names = [
            "Core Platform", "Mobile App", "Teacher Dashboard", "Student Portal",
            "Analytics Suite", "Assessment Tools", "Content Library", "API Platform"
        ]

        products = []
        num_products = random.randint(1, 4)

        for i in range(num_products):
            product = Product(
                name=random.choice(product_names),
                description=f"Advanced {random.choice(['learning', 'educational', 'training'])} solution",
                category=random.choice(category),
                target_audience=random.sample(target_audience, random.randint(1, len(target_audience))),
                features=random.sample([
                    "Real-time collaboration", "AI-powered recommendations", "Mobile-first design",
                    "Analytics dashboard", "Gamification", "Social learning", "Offline access",
                    "Multi-language support", "Integration APIs", "Custom branding"
                ], random.randint(3, 7)),
                launch_date=datetime.now() - timedelta(days=random.randint(30, 1095)),
                status=random.choice(["active", "beta", "development"])
            )
            products.append(product)

        # Competitive analysis
        competitors = random.sample(self.competitors_pool, random.randint(3, 8))
        partnerships = random.sample([
            "Google for Education", "Microsoft Education", "Amazon Web Services",
            "Salesforce", "Adobe", "Zoom", "Canvas", "Blackboard", "McGraw-Hill"
        ], random.randint(0, 4))

        # SWOT Analysis
        competitive_advantages = random.sample([
            "First-mover advantage", "Strong brand recognition", "Advanced AI technology",
            "Exclusive partnerships", "Low customer acquisition cost", "High retention rates",
            "Scalable platform", "International presence", "Strong team expertise"
        ], random.randint(2, 5))

        weaknesses = random.sample([
            "Limited marketing budget", "Dependence on key customers", "Technical debt",
            "Limited geographic presence", "High customer acquisition cost", "Competitive market"
        ], random.randint(1, 3))

        opportunities = random.sample([
            "Emerging markets expansion", "Corporate training growth", "AI integration",
            "Mobile learning trend", "Remote work adoption", "Government contracts",
            "Partnership opportunities", "New product categories"
        ], random.randint(2, 4))

        threats = random.sample([
            "Economic downturn", "Increased competition", "Technology disruption",
            "Regulatory changes", "Funding challenges", "Customer churn"
        ], random.randint(1, 3))

        # Generate description
        description = self._generate_company_description(name, category, target_audience, tech_stack)

        # Create company profile
        company = CompanyProfile(
            name=name,
            website=website,
            founded=founded,
            description=description,
            business_model=business_model,
            category=category,
            target_audience=target_audience,
            products=products,
            funding=funding,
            metrics=metrics,
            technology_stack=tech_stack,
            geographic_presence=geo_presence,
            competitors=competitors,
            partnerships=partnerships,
            competitive_advantages=competitive_advantages,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            confidence_score=random.uniform(0.7, 0.95),
            data_sources=["Company website", "Crunchbase", "LinkedIn", "Industry reports"]
        )

        return company

    def _create_sample_opportunity(self, index: int) -> MarketOpportunity:
        """Create a sample market opportunity"""

        base_opportunity = self.market_opportunities[index % len(self.market_opportunities)]

        opportunity_id = f"MO_{datetime.now().strftime('%Y')}_{'0' + str(index + 1)}"

        # Market sizing (in USD)
        market_size = random.randint(50000000, 50000000000)  # $50M to $50B
        addressable_market = market_size
        serviceable_market = int(market_size * random.uniform(0.1, 0.5))
        target_market = int(serviceable_market * random.uniform(0.05, 0.3))

        opportunity = MarketOpportunity(
            id=opportunity_id,
            name=base_opportunity['name'],
            description=base_opportunity['description'],
            category=base_opportunity['category'],
            market_size=market_size,
            addressable_market=addressable_market,
            serviceable_market=serviceable_market,
            target_market=target_market,
            growth_rate=random.uniform(5, 80),
            key_trends=random.sample([
                "Remote learning adoption", "AI integration", "Microlearning growth",
                "Mobile-first approaches", "Personalization demand", "Skills-based hiring",
                "Lifelong learning culture", "Corporate upskilling", "Digital transformation"
            ], random.randint(3, 6)),
            driving_factors=random.sample([
                "COVID-19 impact", "Digital transformation", "Skills gap", "Remote work",
                "Government initiatives", "Technology advancement", "Changing demographics"
            ], random.randint(2, 4)),
            barriers_to_entry=random.sample([
                "High development costs", "Regulatory compliance", "Network effects",
                "Content licensing", "Customer acquisition costs", "Technology complexity"
            ], random.randint(2, 4)),
            key_players=random.sample(self.competitors_pool, random.randint(5, 10)),
            market_leaders=random.sample(self.competitors_pool, random.randint(2, 4)),
            emerging_players=random.sample(self.company_names, random.randint(3, 6)),
            competitive_intensity=random.uniform(3, 9),
            required_technologies=random.sample([
                "Machine Learning", "Natural Language Processing", "Cloud Computing",
                "Mobile Development", "Data Analytics", "Video Streaming", "APIs",
                "Blockchain", "AR/VR", "Microservices"
            ], random.randint(3, 6)),
            investment_needed=random.randint(1000000, 50000000),
            time_to_market=random.randint(6, 24),
            roi_potential=random.uniform(15, 300),
            risk_level=random.uniform(2, 8),
            primary_regions=random.sample([
                "North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"
            ], random.randint(1, 3)),
            confidence_score=random.uniform(0.6, 0.9),
            data_sources=["Industry reports", "Market research", "Expert interviews", "Competitor analysis"]
        )

        return opportunity

    def _generate_company_description(self, name: str, categories: List[EdTechCategory],
                                    audiences: List[TargetAudience],
                                    tech_stack: TechnologyStack) -> str:
        """Generate a realistic company description"""

        category_descriptions = {
            EdTechCategory.LANGUAGE_LEARNING: "language learning and communication skills",
            EdTechCategory.K12_EDUCATION: "K-12 educational solutions",
            EdTechCategory.HIGHER_EDUCATION: "higher education and university-level learning",
            EdTechCategory.CORPORATE_TRAINING: "corporate training and professional development",
            EdTechCategory.SKILL_DEVELOPMENT: "skill development and career advancement",
            EdTechCategory.ASSESSMENT_TOOLS: "assessment and evaluation tools",
            EdTechCategory.EDUCATIONAL_CONTENT: "educational content and curriculum",
            EdTechCategory.LEARNING_MANAGEMENT: "learning management systems",
            EdTechCategory.TUTORING_PLATFORMS: "tutoring and personalized instruction",
            EdTechCategory.EDUCATIONAL_GAMES: "educational games and gamified learning"
        }

        audience_descriptions = {
            TargetAudience.CHILDREN: "children",
            TargetAudience.TEENAGERS: "teenagers",
            TargetAudience.YOUNG_ADULTS: "young adults",
            TargetAudience.ADULTS: "working professionals",
            TargetAudience.SENIORS: "seniors",
            TargetAudience.TEACHERS: "educators and teachers",
            TargetAudience.PARENTS: "parents and families",
            TargetAudience.CORPORATES: "enterprises and organizations",
            TargetAudience.INSTITUTIONS: "educational institutions"
        }

        primary_category = categories[0]
        primary_audience = audiences[0] if audiences else TargetAudience.ADULTS

        ai_mention = ""
        if tech_stack.ai_ml:
            ai_mention = " leveraging artificial intelligence and machine learning"

        description = (
            f"{name} is an innovative EdTech company specializing in "
            f"{category_descriptions.get(primary_category, 'educational technology')} "
            f"for {audience_descriptions.get(primary_audience, 'learners')}"
            f"{ai_mention}. "
            f"The platform provides cutting-edge solutions that enhance learning outcomes "
            f"through personalized experiences and data-driven insights."
        )

        return description

    def export_sample_data_json(self, companies: List[CompanyProfile],
                              opportunities: List[MarketOpportunity],
                              filename: str = "sample_edtech_data") -> str:
        """Export sample data to JSON format"""

        data = {
            "generated_at": datetime.now().isoformat(),
            "companies": [company.to_dict() for company in companies],
            "market_opportunities": [opp.to_dict() for opp in opportunities],
            "metadata": {
                "company_count": len(companies),
                "opportunity_count": len(opportunities),
                "generator_version": "1.0"
            }
        }

        filepath = f"systems/data/storage/{filename}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"Sample data exported to: {filepath}")
        return filepath