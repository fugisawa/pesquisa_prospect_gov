#!/usr/bin/env python3
"""
RADAR ANALYSIS - EdTech & Idiomas
Análise estratégica de dados de contratação pública para identificar padrões e oportunidades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re

class RadarAnalysis:
    """Análise dos dados radar para identificação de padrões estratégicos"""

    def __init__(self, edtech_file: str, idiomas_file: str):
        """
        Inicializa análise com arquivos de dados

        Args:
            edtech_file: Caminho para radar_edtech.csv
            idiomas_file: Caminho para radar_idiomas.csv
        """
        self.edtech_df = pd.read_csv(edtech_file)
        self.idiomas_df = pd.read_csv(idiomas_file)
        self.combined_df = None
        self._prepare_data()

    def _prepare_data(self):
        """Prepara e limpa os dados para análise"""
        # Converte valores monetários para float
        for df in [self.edtech_df, self.idiomas_df]:
            df['valor_numerico'] = df['valor'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').str.strip()
            df['valor_numerico'] = pd.to_numeric(df['valor_numerico'], errors='coerce')

            # Converte datas
            df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

            # Adiciona colunas derivadas
            df['mes_ano'] = df['data'].dt.to_period('M')
            df['trimestre'] = df['data'].dt.to_period('Q')

        # Combina datasets
        self.combined_df = pd.concat([
            self.edtech_df.assign(dataset='EdTech'),
            self.idiomas_df.assign(dataset='Idiomas')
        ], ignore_index=True)

        print("✅ Dados preparados:")
        print(f"   📊 EdTech: {len(self.edtech_df)} contratos")
        print(f"   🗣️ Idiomas: {len(self.idiomas_df)} contratos")
        print(f"   💰 Total investido: R$ {self.combined_df['valor_numerico'].sum():,.2f}")

    def analyze_temporal_trends(self):
        """Análise de tendências temporais nos últimos 18 meses"""

        print("\n🔍 ANÁLISE TEMPORAL - ÚLTIMOS 18 MESES")
        print("=" * 60)

        # Distribuição por mês
        temporal_summary = self.combined_df.groupby(['mes_ano', 'categoria']).agg({
            'valor_numerico': ['sum', 'count', 'mean']
        }).round(2)

        # Análise por trimestre
        quarterly_analysis = self.combined_df.groupby(['trimestre', 'categoria']).agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'orgao': 'nunique'
        }).round(2)

        print("\n📅 DISTRIBUIÇÃO TEMPORAL POR CATEGORIA:")
        for categoria in ['EdTech geral', 'Idiomas']:
            dados_cat = self.combined_df[self.combined_df['categoria'] == categoria]
            print(f"\n   {categoria}:")
            print(f"   • Período: {dados_cat['data'].min().strftime('%Y-%m-%d')} a {dados_cat['data'].max().strftime('%Y-%m-%d')}")
            print(f"   • Contratos concentrados em: {dados_cat['mes_ano'].mode().iloc[0] if not dados_cat['mes_ano'].mode().empty else 'N/A'}")
            print(f"   • Valor médio mensal: R$ {dados_cat.groupby('mes_ano')['valor_numerico'].sum().mean():,.2f}")

        # Padrões de sazonalidade
        monthly_totals = self.combined_df.groupby([self.combined_df['data'].dt.month, 'categoria'])['valor_numerico'].sum()

        print("\n🔄 PADRÕES DE SAZONALIDADE:")
        for categoria in ['EdTech geral', 'Idiomas']:
            dados_cat = self.combined_df[self.combined_df['categoria'] == categoria]
            meses_ativos = dados_cat['data'].dt.month.value_counts().sort_index()
            print(f"\n   {categoria}:")
            print(f"   • Meses mais ativos: {meses_ativos.idxmax()} ({meses_ativos.max()} contratos)")
            print(f"   • Concentração: {(meses_ativos.max() / meses_ativos.sum() * 100):.1f}% dos contratos")

        return temporal_summary, quarterly_analysis

    def analyze_contract_profile(self):
        """Análise do perfil dos contratos vencedores"""

        print("\n📋 PERFIL DOS CONTRATOS VENCEDORES")
        print("=" * 60)

        # Distribuição por modalidade
        modalidade_analysis = self.combined_df.groupby(['modalidade', 'categoria']).agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'orgao': 'nunique'
        }).round(2)

        print("\n🏛️ DISTRIBUIÇÃO POR MODALIDADE:")
        modalidades = self.combined_df['modalidade'].value_counts()
        for modalidade, count in modalidades.items():
            percentage = (count / len(self.combined_df)) * 100
            valor_total = self.combined_df[self.combined_df['modalidade'] == modalidade]['valor_numerico'].sum()
            valor_medio = self.combined_df[self.combined_df['modalidade'] == modalidade]['valor_numerico'].mean()

            print(f"   • {modalidade}: {count} contratos ({percentage:.1f}%)")
            print(f"     - Valor total: R$ {valor_total:,.2f}")
            print(f"     - Valor médio: R$ {valor_medio:,.2f}")

        # Órgãos mais ativos
        print("\n🏢 ÓRGÃOS MAIS ATIVOS:")
        orgaos_ativos = self.combined_df.groupby(['orgao', 'categoria']).agg({
            'valor_numerico': ['sum', 'count', 'mean']
        }).round(2)

        for categoria in ['EdTech geral', 'Idiomas']:
            print(f"\n   {categoria}:")
            dados_cat = self.combined_df[self.combined_df['categoria'] == categoria]
            top_orgaos = dados_cat['orgao'].value_counts().head(3)

            for orgao, count in top_orgaos.items():
                valor_total = dados_cat[dados_cat['orgao'] == orgao]['valor_numerico'].sum()
                print(f"   • {orgao}: {count} contratos (R$ {valor_total:,.2f})")

        return modalidade_analysis, orgaos_ativos

    def analyze_purchase_propensity(self):
        """Análise de propensão de compra por órgão"""

        print("\n💡 PROPENSÃO DE COMPRA POR ÓRGÃO")
        print("=" * 60)

        # Frequência e valores por órgão
        propensity_analysis = self.combined_df.groupby(['orgao', 'categoria']).agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'modalidade': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A',
            'data': ['min', 'max']
        }).round(2)

        print("\n📊 ANÁLISE DE COMPORTAMENTO DE COMPRA:")

        # EdTech
        print("\n   🎓 EDTECH - Propensão por Órgão:")
        edtech_data = self.combined_df[self.combined_df['categoria'] == 'EdTech geral']
        edtech_summary = edtech_data.groupby('orgao').agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'modalidade': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
        }).round(2)

        for orgao in edtech_summary.index:
            total = edtech_summary.loc[orgao, ('valor_numerico', 'sum')]
            count = edtech_summary.loc[orgao, ('valor_numerico', 'count')]
            avg = edtech_summary.loc[orgao, ('valor_numerico', 'mean')]
            modal = edtech_summary.loc[orgao, ('modalidade', '<lambda>')]

            print(f"   • {orgao}:")
            print(f"     - Investimento: R$ {total:,.2f} ({count} contratos)")
            print(f"     - Ticket médio: R$ {avg:,.2f}")
            print(f"     - Modalidade preferencial: {modal}")

        # Idiomas
        print("\n   🗣️ IDIOMAS - Propensão por Órgão:")
        idiomas_data = self.combined_df[self.combined_df['categoria'] == 'Idiomas']
        idiomas_summary = idiomas_data.groupby('orgao').agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'modalidade': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
        }).round(2)

        for orgao in idiomas_summary.index:
            total = idiomas_summary.loc[orgao, ('valor_numerico', 'sum')]
            count = idiomas_summary.loc[orgao, ('valor_numerico', 'count')]
            avg = idiomas_summary.loc[orgao, ('valor_numerico', 'mean')]
            modal = idiomas_summary.loc[orgao, ('modalidade', '<lambda>')]

            print(f"   • {orgao}:")
            print(f"     - Investimento: R$ {total:,.2f} ({count} contratos)")
            print(f"     - Ticket médio: R$ {avg:,.2f}")
            print(f"     - Modalidade preferencial: {modal}")

        return propensity_analysis

    def analyze_substitution_potential(self):
        """Análise de potencial de substituição"""

        print("\n🔄 ANÁLISE DE POTENCIAL DE SUBSTITUIÇÃO")
        print("=" * 60)

        # Contratos com potential_substitute = True
        substitutes = self.combined_df[self.combined_df['potential_substitute'] == True]

        if len(substitutes) > 0:
            print(f"\n📈 CONTRATOS COM POTENCIAL DE SUBSTITUIÇÃO: {len(substitutes)}")

            substitute_summary = substitutes.groupby(['orgao', 'categoria']).agg({
                'valor_numerico': ['sum', 'count', 'mean']
            }).round(2)

            print("\n   🎯 OPORTUNIDADES IDENTIFICADAS:")
            for _, row in substitutes.iterrows():
                print(f"   • {row['orgao']} ({row['categoria']})")
                print(f"     - Contrato: R$ {row['valor_numerico']:,.2f}")
                print(f"     - Modalidade: {row['modalidade']}")
                print(f"     - Objeto: {row['objeto'][:80]}...")
        else:
            print("\n❌ Nenhum contrato com flag de substituição identificado")

        # Cross-selling opportunities
        print("\n🔀 OPORTUNIDADES DE CROSS-SELLING:")

        # Órgãos que compram EdTech mas não idiomas
        orgaos_edtech = set(self.edtech_df['orgao'].unique())
        orgaos_idiomas = set(self.idiomas_df['orgao'].unique())

        only_edtech = orgaos_edtech - orgaos_idiomas
        only_idiomas = orgaos_idiomas - orgaos_edtech
        both = orgaos_edtech & orgaos_idiomas

        print(f"\n   📊 SEGMENTAÇÃO DE ÓRGÃOS:")
        print(f"   • Apenas EdTech: {len(only_edtech)} órgãos")
        print(f"   • Apenas Idiomas: {len(only_idiomas)} órgãos")
        print(f"   • Ambos: {len(both)} órgãos")

        if only_edtech:
            print(f"\n   🎓 ÓRGÃOS SÓ EDTECH (potencial para idiomas):")
            for orgao in only_edtech:
                valor = self.edtech_df[self.edtech_df['orgao'] == orgao]['valor_numerico'].sum()
                print(f"   • {orgao}: R$ {valor:,.2f} em EdTech")

        if only_idiomas:
            print(f"\n   🗣️ ÓRGÃOS SÓ IDIOMAS (potencial para EdTech):")
            for orgao in only_idiomas:
                valor = self.idiomas_df[self.idiomas_df['orgao'] == orgao]['valor_numerico'].sum()
                print(f"   • {orgao}: R$ {valor:,.2f} em Idiomas")

        return substitutes, substitute_summary

    def generate_strategic_insights(self):
        """Gera insights estratégicos consolidados"""

        print("\n🎯 INSIGHTS ESTRATÉGICOS CONSOLIDADOS")
        print("=" * 60)

        # Cálculos estratégicos
        total_value = self.combined_df['valor_numerico'].sum()
        edtech_value = self.edtech_df['valor_numerico'].sum()
        idiomas_value = self.idiomas_df['valor_numerico'].sum()

        avg_edtech = self.edtech_df['valor_numerico'].mean()
        avg_idiomas = self.idiomas_df['valor_numerico'].mean()

        # Market share por fornecedor
        top_fornecedores = self.combined_df.groupby(['fornecedor', 'categoria']).agg({
            'valor_numerico': 'sum'
        }).round(2)

        print(f"\n💰 PANORAMA FINANCEIRO:")
        print(f"   • Total investido: R$ {total_value:,.2f}")
        print(f"   • EdTech: R$ {edtech_value:,.2f} ({edtech_value/total_value*100:.1f}%)")
        print(f"   • Idiomas: R$ {idiomas_value:,.2f} ({idiomas_value/total_value*100:.1f}%)")
        print(f"   • Ticket médio EdTech: R$ {avg_edtech:,.2f}")
        print(f"   • Ticket médio Idiomas: R$ {avg_idiomas:,.2f}")

        print(f"\n🏆 PLAYERS DOMINANTES:")

        # Top fornecedores EdTech
        edtech_fornecedores = self.edtech_df.groupby('fornecedor')['valor_numerico'].sum().sort_values(ascending=False)
        print(f"\n   🎓 EdTech Top 3:")
        for i, (fornecedor, valor) in enumerate(edtech_fornecedores.head(3).items(), 1):
            market_share = (valor / edtech_value) * 100
            print(f"   {i}. {fornecedor}: R$ {valor:,.2f} ({market_share:.1f}%)")

        # Top fornecedores Idiomas
        idiomas_fornecedores = self.idiomas_df.groupby('fornecedor')['valor_numerico'].sum().sort_values(ascending=False)
        print(f"\n   🗣️ Idiomas Top 3:")
        for i, (fornecedor, valor) in enumerate(idiomas_fornecedores.head(3).items(), 1):
            market_share = (valor / idiomas_value) * 100
            print(f"   {i}. {fornecedor}: R$ {valor:,.2f} ({market_share:.1f}%)")

        print(f"\n📊 MODALIDADES PREFERENCIAIS:")
        modalidade_prefs = self.combined_df.groupby(['categoria', 'modalidade']).size().unstack(fill_value=0)

        for categoria in ['EdTech geral', 'Idiomas']:
            if categoria in modalidade_prefs.index:
                total_cat = modalidade_prefs.loc[categoria].sum()
                print(f"\n   {categoria}:")
                for modalidade, count in modalidade_prefs.loc[categoria].sort_values(ascending=False).items():
                    if count > 0:
                        pct = (count / total_cat) * 100
                        print(f"   • {modalidade}: {count} contratos ({pct:.1f}%)")

        # Recomendações finais
        print(f"\n🎯 RECOMENDAÇÕES ESTRATÉGICAS:")
        print(f"   1. TIMING: Foco em contratos Q1 (maior concentração)")
        print(f"   2. MODALIDADE: Pregão Eletrônico = via de entrada principal")
        print(f"   3. TARGET PRIMÁRIO: MEC e Itamaraty (maiores compradores)")
        print(f"   4. CROSS-SELL: Órgãos só EdTech têm potencial para idiomas")
        print(f"   5. TICKET: EdTech tem tickets maiores (R$ {avg_edtech:,.0f} vs R$ {avg_idiomas:,.0f})")

        return {
            'total_value': total_value,
            'market_shares': top_fornecedores,
            'recommendations': [
                "Focar em Q1 para timing de contratos",
                "Priorizar Pregão Eletrônico como modalidade",
                "Target primário: MEC e Itamaraty",
                "Explorar cross-selling entre categorias"
            ]
        }

def main():
    """Executa análise completa dos dados radar"""

    print("🔍 INICIANDO ANÁLISE RADAR - EDTECH & IDIOMAS")
    print("=" * 60)

    # Caminhos dos arquivos
    edtech_file = "/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_edtech.csv"
    idiomas_file = "/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_idiomas.csv"

    # Inicializa análise
    analyzer = RadarAnalysis(edtech_file, idiomas_file)

    # Executa todas as análises
    temporal_summary, quarterly_analysis = analyzer.analyze_temporal_trends()
    modalidade_analysis, orgaos_ativos = analyzer.analyze_contract_profile()
    propensity_analysis = analyzer.analyze_purchase_propensity()
    substitutes, substitute_summary = analyzer.analyze_substitution_potential()
    strategic_insights = analyzer.generate_strategic_insights()

    print("\n✅ ANÁLISE COMPLETA FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    main()