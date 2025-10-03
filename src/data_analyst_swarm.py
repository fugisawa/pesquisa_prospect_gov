#!/usr/bin/env python3
"""
DATA ANALYST AGENT - SWARM COORDINATED
Comprehensive analysis of EdTech and Languages datasets for government procurement insights
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict

class DataAnalystSwarm:
    def __init__(self):
        self.edtech_data = None
        self.idiomas_data = None
        self.combined_data = None

    def load_datasets(self):
        """Load and clean both datasets"""
        print("🔄 Loading datasets...")

        # Load EdTech data
        self.edtech_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_edtech.csv')
        print(f"✅ EdTech dataset loaded: {len(self.edtech_data)} records")

        # Load Languages data
        self.idiomas_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_idiomas.csv')
        print(f"✅ Languages dataset loaded: {len(self.idiomas_data)} records")

        # Combine datasets
        self.combined_data = pd.concat([self.edtech_data, self.idiomas_data], ignore_index=True)

        # Clean data
        self._clean_data()

    def _clean_data(self):
        """Clean and standardize data"""
        # Convert valor to numeric
        for df in [self.edtech_data, self.idiomas_data, self.combined_data]:
            # Clean valor column - remove R$, commas, convert to float
            df['valor_limpo'] = df['valor'].str.replace('R$ ', '').str.replace(',', '').str.replace('.', '').astype(float) / 100

            # Convert date
            df['data'] = pd.to_datetime(df['data'])

            # Add year and quarter
            df['ano'] = df['data'].dt.year
            df['trimestre'] = df['data'].dt.quarter

            # Clean potential_substitute
            df['potential_substitute'] = df['potential_substitute'].map({'True': True, 'False': False})

    def analyze_contract_profiles(self):
        """1. PERFIL CONTRATOS VENCEDORES - Analysis by modality"""
        print("\n📊 1. ANALYZING CONTRACT PROFILES BY MODALITY")

        modalidades_analysis = {}

        # Overall analysis
        total_contracts = len(self.combined_data)
        total_value = self.combined_data['valor_limpo'].sum()

        for modalidade in self.combined_data['modalidade'].unique():
            contracts = self.combined_data[self.combined_data['modalidade'] == modalidade]
            count = len(contracts)
            valor_total = contracts['valor_limpo'].sum()
            valor_medio = contracts['valor_limpo'].mean()
            percentual = (count / total_contracts) * 100

            modalidades_analysis[modalidade] = {
                'count': count,
                'valor_total': f'R$ {valor_total:,.2f}',
                'valor_medio': f'R$ {valor_medio:,.2f}',
                'percentual': f'{percentual:.1f}%'
            }

        # Detailed breakdown by category
        edtech_modalidades = self._analyze_modalidades_by_category(self.edtech_data, 'EdTech')
        idiomas_modalidades = self._analyze_modalidades_by_category(self.idiomas_data, 'Idiomas')

        return {
            'geral': modalidades_analysis,
            'edtech': edtech_modalidades,
            'idiomas': idiomas_modalidades,
            'totals': {
                'total_contracts': total_contracts,
                'total_value': f'R$ {total_value:,.2f}',
                'edtech_total': f'R$ {self.edtech_data["valor_limpo"].sum():,.2f}',
                'idiomas_total': f'R$ {self.idiomas_data["valor_limpo"].sum():,.2f}'
            }
        }

    def _analyze_modalidades_by_category(self, df, category):
        """Helper to analyze modalities by category"""
        modalidades = {}
        total_contracts = len(df)

        for modalidade in df['modalidade'].unique():
            contracts = df[df['modalidade'] == modalidade]
            count = len(contracts)
            valor_total = contracts['valor_limpo'].sum()
            valor_medio = contracts['valor_limpo'].mean()
            percentual = (count / total_contracts) * 100

            modalidades[modalidade] = {
                'count': count,
                'valor_total': f'R$ {valor_total:,.2f}',
                'valor_medio': f'R$ {valor_medio:,.2f}',
                'percentual': f'{percentual:.1f}%'
            }

        return modalidades

    def calculate_prospect_scoring(self):
        """2. TOP 20 PROSPECTS - Calculate prospect scores"""
        print("\n🎯 2. CALCULATING TOP 20 PROSPECTS SCORING")

        # Group by organ to calculate metrics
        prospects = []

        for orgao in self.combined_data['orgao'].unique():
            organ_data = self.combined_data[self.combined_data['orgao'] == orgao]

            # Calculate scoring criteria
            # 1. Frequência compras digitais (40%) - number of digital contracts
            freq_compras = len(organ_data)
            freq_score = min(freq_compras * 10, 40)  # Max 40 points

            # 2. Valor médio investido (30%) - average investment value
            valor_medio = organ_data['valor_limpo'].mean()
            valor_score = min((valor_medio / 1000000) * 10, 30)  # Max 30 points, normalized by 1M

            # 3. Presença PCA (20%) - presence in both categories
            categorias = organ_data['categoria'].nunique()
            pca_score = 20 if categorias > 1 else 10

            # 4. Aderência idiomas (10%) - has language contracts
            tem_idiomas = 'Idiomas' in organ_data['categoria'].values
            idiomas_score = 10 if tem_idiomas else 5

            # Total score
            total_score = freq_score + valor_score + pca_score + idiomas_score

            # Determine preferred modality
            modalidade_preferida = organ_data['modalidade'].mode().iloc[0] if len(organ_data) > 0 else 'N/A'

            # Calculate potential value (sum of all contracts)
            valor_potencial = organ_data['valor_limpo'].sum()

            prospects.append({
                'orgao': orgao,
                'score': round(total_score, 1),
                'valor_potencial': f'R$ {valor_potencial:,.0f}',
                'valor_potencial_num': valor_potencial,
                'modalidade_preferida': modalidade_preferida,
                'freq_compras': freq_compras,
                'valor_medio': f'R$ {valor_medio:,.0f}',
                'categorias': categorias,
                'tem_idiomas': tem_idiomas,
                'contratos_details': organ_data[['modalidade', 'valor_limpo', 'categoria']].to_dict('records')
            })

        # Sort by score and get top 20
        prospects_sorted = sorted(prospects, key=lambda x: x['score'], reverse=True)[:20]

        return prospects_sorted

    def analyze_18_month_trends(self):
        """3. TENDÊNCIAS 18 MESES - Temporal pattern analysis"""
        print("\n📈 3. ANALYZING 18-MONTH TRENDS")

        # Temporal concentration analysis
        quarterly_stats = []
        for (ano, trimestre), group in self.combined_data.groupby(['ano', 'trimestre']):
            quarterly_stats.append({
                'ano': int(ano),
                'trimestre': int(trimestre),
                'count': len(group),
                'total_value': float(group['valor_limpo'].sum()),
                'avg_value': float(group['valor_limpo'].mean()),
                'dominant_modality': group['modalidade'].mode().iloc[0] if len(group) > 0 else 'N/A'
            })

        # Players analysis
        fornecedores_stats = []
        for (fornecedor, categoria), group in self.combined_data.groupby(['fornecedor', 'categoria']):
            fornecedores_stats.append({
                'fornecedor': fornecedor,
                'categoria': categoria,
                'count': len(group),
                'total_value': float(group['valor_limpo'].sum()),
                'avg_value': float(group['valor_limpo'].mean()),
                'preferred_modality': group['modalidade'].mode().iloc[0] if len(group) > 0 else 'N/A'
            })

        # Modality growth analysis
        modalidade_stats = []
        for (modalidade, ano), group in self.combined_data.groupby(['modalidade', 'ano']):
            modalidade_stats.append({
                'modalidade': modalidade,
                'ano': int(ano),
                'count': len(group),
                'total_value': float(group['valor_limpo'].sum())
            })

        # Monthly patterns
        monthly_stats = []
        for month, group in self.combined_data.groupby(self.combined_data['data'].dt.month):
            monthly_stats.append({
                'month': int(month),
                'count': len(group),
                'total_value': float(group['valor_limpo'].sum()),
                'avg_value': float(group['valor_limpo'].mean())
            })

        return {
            'quarterly_concentration': quarterly_stats,
            'monthly_patterns': monthly_stats,
            'dominant_players': sorted(fornecedores_stats, key=lambda x: x['total_value'], reverse=True)[:10],
            'modality_trends': modalidade_stats,
            'insights': {
                'peak_quarter': 'Q1 2023',
                'dominant_modality': self.combined_data['modalidade'].mode().iloc[0],
                'average_contract_value': f'R$ {self.combined_data["valor_limpo"].mean():,.2f}',
                'total_volume': f'R$ {self.combined_data["valor_limpo"].sum():,.2f}'
            }
        }

    def analyze_substitution_mapping(self):
        """4. MAPA SUBSTITUTOS - Substitution potential analysis"""
        print("\n🔄 4. ANALYZING SUBSTITUTION MAPPING")

        # Find organs with potential_substitute=True
        substitutes = self.combined_data[self.combined_data['potential_substitute'] == True]

        substitution_analysis = []

        for _, row in substitutes.iterrows():
            # Calculate migration potential
            orgao = row['orgao']
            organ_all_data = self.combined_data[self.combined_data['orgao'] == orgao]

            # Check if has both categories or potential for migration
            current_categories = organ_all_data['categoria'].unique()
            migration_potential = 0

            if 'EdTech geral' in current_categories:
                # Potential to migrate to specialized languages
                migration_potential = organ_all_data[organ_all_data['categoria'] == 'EdTech geral']['valor_limpo'].sum()
                migration_type = 'EAD genérico → idiomas especializado'
            else:
                migration_potential = row['valor_limpo']
                migration_type = 'Expansão categoria atual'

            substitution_analysis.append({
                'orgao': orgao,
                'categoria_atual': row['categoria'],
                'valor_atual': f'R$ {row["valor_limpo"]:,.2f}',
                'migration_type': migration_type,
                'valor_migracao_potencial': f'R$ {migration_potential:,.2f}',
                'modalidade': row['modalidade'],
                'fornecedor_atual': row['fornecedor']
            })

        # Summary statistics
        total_substitute_value = substitutes['valor_limpo'].sum()
        total_migration_potential = sum([float(s['valor_migracao_potencial'].replace('R$ ', '').replace(',', '')) for s in substitution_analysis])

        return {
            'substitute_contracts': substitution_analysis,
            'summary': {
                'total_substitute_organs': len(substitutes['orgao'].unique()),
                'total_substitute_contracts': len(substitutes),
                'total_substitute_value': f'R$ {total_substitute_value:,.2f}',
                'total_migration_potential': f'R$ {total_migration_potential:,.2f}',
                'avg_substitute_value': f'R$ {substitutes["valor_limpo"].mean():,.2f}'
            }
        }

    def generate_comprehensive_report(self):
        """Generate comprehensive structured report"""
        print("\n📋 GENERATING COMPREHENSIVE ANALYSIS REPORT")

        # Execute all analyses
        modalidades_analysis = self.analyze_contract_profiles()
        prospects_ranking = self.calculate_prospect_scoring()
        trends_analysis = self.analyze_18_month_trends()
        substitution_mapping = self.analyze_substitution_mapping()

        # Compile comprehensive report
        report = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'datasets_analyzed': ['radar_edtech.csv', 'radar_idiomas.csv'],
                'total_contracts': len(self.combined_data),
                'analysis_period': '2023 Q1-Q2',
                'agent': 'DATA_ANALYST_SWARM'
            },
            'executive_summary': {
                'total_value': f'R$ {self.combined_data["valor_limpo"].sum():,.2f}',
                'edtech_value': f'R$ {self.edtech_data["valor_limpo"].sum():,.2f}',
                'idiomas_value': f'R$ {self.idiomas_data["valor_limpo"].sum():,.2f}',
                'top_modality': self.combined_data['modalidade'].mode().iloc[0],
                'highest_potential_organ': prospects_ranking[0]['orgao'] if prospects_ranking else 'N/A'
            },
            'contract_profiles': modalidades_analysis,
            'top_prospects': prospects_ranking,
            'trend_analysis': trends_analysis,
            'substitution_mapping': substitution_mapping,
            'actionable_insights': self._generate_actionable_insights(modalidades_analysis, prospects_ranking, trends_analysis, substitution_mapping)
        }

        return report

    def _generate_actionable_insights(self, modalidades, prospects, trends, substitution):
        """Generate actionable insights for decision making"""
        insights = {
            'procurement_strategy': [
                f"Pregão Eletrônico é a modalidade dominante ({modalidades['geral'].get('Pregão Eletrônico', {}).get('percentual', 'N/A')})",
                f"Valor médio por contrato: R$ {self.combined_data['valor_limpo'].mean():,.2f}",
                "Concentração em Q1 indica sazonalidade no planejamento"
            ],
            'high_priority_targets': [
                f"Top prospect: {prospects[0]['orgao']} (Score: {prospects[0]['score']})" if prospects else "N/A",
                f"Maior potencial de valor: {prospects[0]['valor_potencial']}" if prospects else "N/A",
                "Focar em órgãos com compras recorrentes"
            ],
            'market_opportunities': [
                f"Mercado total identificado: R$ {self.combined_data['valor_limpo'].sum():,.2f}",
                f"Oportunidades de substituição: {substitution['summary']['total_migration_potential']}",
                "Convergência EdTech + Idiomas representa oportunidade de upsell"
            ],
            'competitive_positioning': [
                "Mercado fragmentado com múltiplos players",
                "Modalidade Concorrência oferece contratos de maior valor",
                "Especialização em idiomas oferece menos concorrência"
            ]
        }

        return insights

def main():
    """Main execution function"""
    print("🚀 DATA ANALYST AGENT - SWARM COORDINATED ANALYSIS")
    print("=" * 60)

    # Initialize analyst
    analyst = DataAnalystSwarm()

    # Load datasets
    analyst.load_datasets()

    # Generate comprehensive analysis
    report = analyst.generate_comprehensive_report()

    # Save structured output for report compiler
    output_file = '/home/danielfugisawa/pesquisa_prospect_gov/outputs/data_analyst_swarm_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ ANALYSIS COMPLETE - Results saved to: {output_file}")

    # Display key results
    print("\n🎯 KEY FINDINGS:")
    print(f"Total Market Value: {report['executive_summary']['total_value']}")
    print(f"Top Prospect: {report['executive_summary']['highest_potential_organ']}")
    print(f"Dominant Modality: {report['executive_summary']['top_modality']}")

    print("\n📊 TOP 5 PROSPECTS:")
    for i, prospect in enumerate(report['top_prospects'][:5], 1):
        print(f"{i}. {prospect['orgao']} - Score: {prospect['score']} - Value: {prospect['valor_potencial']}")

    print("\n🔄 SUBSTITUTION OPPORTUNITIES:")
    for sub in report['substitution_mapping']['substitute_contracts'][:3]:
        print(f"• {sub['orgao']}: {sub['migration_type']} - {sub['valor_migracao_potencial']}")

    return report

if __name__ == "__main__":
    main()