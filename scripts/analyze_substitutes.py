#!/usr/bin/env python3
"""
ANÁLISE DE SUBSTITUTOS: EAD GENÉRICO → IDIOMAS
Identifica órgãos com potencial de migração de soluções genéricas para especializadas em idiomas
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import re

class SubstituteAnalyzer:
    def __init__(self):
        self.edtech_data = None
        self.idiomas_data = None
        self.merged_data = None

    def load_data(self):
        """Carrega dados dos radares EdTech e Idiomas"""
        print("🔄 Carregando dados...")

        # Carregar dados EdTech
        try:
            self.edtech_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_edtech.csv')
            print(f"✅ EdTech data: {len(self.edtech_data)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar dados EdTech: {e}")

        # Carregar dados Idiomas
        try:
            self.idiomas_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_idiomas.csv')
            print(f"✅ Idiomas data: {len(self.idiomas_data)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar dados Idiomas: {e}")

    def clean_currency(self, value):
        """Limpa valores monetários"""
        if pd.isna(value):
            return 0
        if isinstance(value, str):
            # Remove R$, pontos e vírgulas, converte para float
            clean_value = re.sub(r'[R$\s\.]', '', value)
            clean_value = clean_value.replace(',', '.')
            try:
                return float(clean_value)
            except:
                return 0
        return float(value)

    def analyze_edtech_patterns(self):
        """Analisa padrões de compra de EAD genérico"""
        print("\n📊 ANÁLISE DE PADRÕES EAD GENÉRICO")
        print("=" * 50)

        if self.edtech_data is None:
            print("❌ Dados EdTech não carregados")
            return

        # Limpar valores monetários
        self.edtech_data['valor_numerico'] = self.edtech_data['valor'].apply(self.clean_currency)

        # Análise por órgão
        orgao_stats = self.edtech_data.groupby('orgao').agg({
            'valor_numerico': ['sum', 'count', 'mean'],
            'fornecedor': 'nunique'
        }).round(2)

        orgao_stats.columns = ['Total_Gasto', 'Num_Contratos', 'Media_Contrato', 'Num_Fornecedores']
        orgao_stats = orgao_stats.sort_values('Total_Gasto', ascending=False)

        print("\n🏛️ TOP ÓRGÃOS EM EAD GENÉRICO:")
        print(orgao_stats.head(10))

        # Identificar órgãos com alto potencial (> R$ 500K)
        high_potential = orgao_stats[orgao_stats['Total_Gasto'] > 500000]
        print(f"\n🎯 ÓRGÃOS COM INVESTIMENTO > R$ 500K: {len(high_potential)}")

        return orgao_stats, high_potential

    def identify_language_gaps(self):
        """Identifica órgãos que fazem EAD mas não têm idiomas"""
        print("\n🔍 IDENTIFICANDO GAPS DE IDIOMAS")
        print("=" * 50)

        if self.edtech_data is None or self.idiomas_data is None:
            print("❌ Dados incompletos")
            return

        # Órgãos com EAD
        edtech_orgaos = set(self.edtech_data['orgao'].unique())
        print(f"📚 Órgãos com EAD genérico: {len(edtech_orgaos)}")

        # Órgãos com idiomas
        idiomas_orgaos = set(self.idiomas_data['orgao'].unique())
        print(f"🗣️ Órgãos com soluções de idiomas: {len(idiomas_orgaos)}")

        # GAP: tem EAD mas não tem idiomas
        gap_orgaos = edtech_orgaos - idiomas_orgaos
        print(f"🎯 ÓRGÃOS COM GAP (EAD sim, idiomas não): {len(gap_orgaos)}")

        print("\n📋 LISTA DE ÓRGÃOS COM GAP:")
        for i, orgao in enumerate(sorted(gap_orgaos), 1):
            print(f"{i}. {orgao}")

        return gap_orgaos

    def calculate_mission_need_score(self, orgao):
        """Calcula score de necessidade missional de idiomas (0-5)"""

        # Mapeamento de necessidades por tipo de órgão
        high_need_keywords = [
            'relações exteriores', 'exterior', 'relações internacionais',
            'defesa', 'militar', 'aeronáutica', 'marinha', 'exército',
            'turismo', 'desenvolvimento', 'comércio exterior',
            'ciência', 'tecnologia', 'universidade', 'pesquisa'
        ]

        medium_need_keywords = [
            'justiça', 'segurança', 'receita', 'fazenda',
            'educação', 'saúde', 'agricultura',
            'trabalho', 'previdência'
        ]

        orgao_lower = orgao.lower()

        # Score alto (4-5) para órgãos com alta necessidade internacional
        for keyword in high_need_keywords:
            if keyword in orgao_lower:
                if any(international in orgao_lower for international in ['exterior', 'internacional', 'defesa']):
                    return 5
                return 4

        # Score médio (2-3) para órgãos com necessidade moderada
        for keyword in medium_need_keywords:
            if keyword in orgao_lower:
                return 3

        # Score baixo (1-2) para outros órgãos
        if any(admin in orgao_lower for admin in ['administração', 'gestão', 'enap']):
            return 2

        return 1

    def calculate_migration_ease_score(self, total_gasto, num_contratos):
        """Calcula facilidade de migração (0-5)"""

        # Baseado no volume de gastos e número de contratos
        if total_gasto > 2000000:  # > R$ 2M
            if num_contratos >= 3:
                return 5  # Alto volume, múltiplos contratos = fácil migração
            else:
                return 4  # Alto volume, poucos contratos = migração moderada
        elif total_gasto > 1000000:  # > R$ 1M
            return 3  # Volume médio
        elif total_gasto > 500000:  # > R$ 500K
            return 2  # Volume baixo mas viável
        else:
            return 1  # Volume muito baixo

    def determine_timeline(self, mission_score, ease_score, total_gasto):
        """Determina timeline provável de migração"""

        combined_score = (mission_score + ease_score) / 2

        if combined_score >= 4 and total_gasto > 1000000:
            return "Q1 2025"
        elif combined_score >= 3.5:
            return "Q2 2025"
        elif combined_score >= 2.5:
            return "Q3 2025"
        else:
            return "Q4 2025"

    def create_substitute_analysis(self):
        """Cria análise completa de substitutos"""
        print("\n🎯 CRIANDO ANÁLISE DE SUBSTITUTOS")
        print("=" * 50)

        # Carregar dados
        self.load_data()

        # Analisar padrões EdTech
        orgao_stats, high_potential = self.analyze_edtech_patterns()

        # Identificar gaps
        gap_orgaos = self.identify_language_gaps()

        # Criar análise de substitutos
        substitute_candidates = []

        for orgao in gap_orgaos:
            if orgao in orgao_stats.index:
                stats = orgao_stats.loc[orgao]

                mission_score = self.calculate_mission_need_score(orgao)
                ease_score = self.calculate_migration_ease_score(
                    stats['Total_Gasto'],
                    stats['Num_Contratos']
                )
                timeline = self.determine_timeline(
                    mission_score,
                    ease_score,
                    stats['Total_Gasto']
                )

                # Score total (média ponderada)
                total_score = (mission_score * 0.4 + ease_score * 0.6)

                substitute_candidates.append({
                    'orgao': orgao,
                    'total_gasto_edtech': stats['Total_Gasto'],
                    'num_contratos_edtech': stats['Num_Contratos'],
                    'media_contrato': stats['Media_Contrato'],
                    'necessidade_missional_score': mission_score,
                    'facilidade_migracao_score': ease_score,
                    'score_total': round(total_score, 2),
                    'timeline_provavel': timeline,
                    'potencial_mercado_r$': round(stats['Total_Gasto'] * 0.3, 2)  # 30% do gasto atual
                })

        # Converter para DataFrame e ordenar por score
        substitute_df = pd.DataFrame(substitute_candidates)
        substitute_df = substitute_df.sort_values('score_total', ascending=False)

        return substitute_df

    def generate_migration_matrix(self, substitute_df):
        """Gera matriz de migração atual vs potencial"""
        print("\n📊 MATRIZ DE MIGRAÇÃO")
        print("=" * 30)

        # Agrupar por timeline
        timeline_groups = substitute_df.groupby('timeline_provavel').agg({
            'orgao': 'count',
            'total_gasto_edtech': 'sum',
            'potencial_mercado_r$': 'sum'
        }).round(2)

        timeline_groups.columns = ['Num_Orgaos', 'Mercado_Atual_EAD', 'Potencial_Idiomas']

        print(timeline_groups)

        return timeline_groups

    def calculate_total_market(self, substitute_df):
        """Calcula mercado total de substituição"""
        print("\n💰 MERCADO TOTAL DE SUBSTITUIÇÃO")
        print("=" * 40)

        total_current = substitute_df['total_gasto_edtech'].sum()
        total_potential = substitute_df['potencial_mercado_r$'].sum()

        print(f"🔄 Mercado atual EAD genérico: R$ {total_current:,.2f}")
        print(f"🎯 Potencial mercado idiomas: R$ {total_potential:,.2f}")
        print(f"📈 Taxa de penetração estimada: {(total_potential/total_current)*100:.1f}%")

        return total_current, total_potential

    def generate_value_propositions(self, substitute_df):
        """Gera proposições de valor específicas"""
        print("\n💡 VALUE PROPOSITIONS ESPECÍFICAS")
        print("=" * 40)

        value_props = {}

        for _, row in substitute_df.head(10).iterrows():  # Top 10
            orgao = row['orgao']
            mission_score = row['necessidade_missional_score']

            if mission_score >= 4:
                if 'relações exteriores' in orgao.lower() or 'exterior' in orgao.lower():
                    value_prop = "Capacitação diplomática especializada com certificação internacional"
                elif 'defesa' in orgao.lower() or 'militar' in orgao.lower():
                    value_prop = "Treinamento militar multilíngue para operações internacionais"
                elif 'universidade' in orgao.lower() or 'pesquisa' in orgao.lower():
                    value_prop = "Inglês acadêmico para publicações e cooperação internacional"
                else:
                    value_prop = "Capacitação internacional especializada para servidores"
            elif mission_score >= 3:
                value_prop = "Modernização da capacitação com foco em comunicação global"
            else:
                value_prop = "Evolução natural do EAD para competências linguísticas"

            value_props[orgao] = value_prop

        return value_props

    def save_results(self, substitute_df, timeline_matrix, value_props):
        """Salva resultados da análise"""
        print("\n💾 SALVANDO RESULTADOS")
        print("=" * 25)

        # Salvar tabela principal
        substitute_df.to_csv('/home/danielfugisawa/pesquisa_prospect_gov/analysis/mapa_substitutos_edtech_idiomas.csv', index=False)
        print("✅ Tabela principal salva")

        # Salvar matriz de timeline
        timeline_matrix.to_csv('/home/danielfugisawa/pesquisa_prospect_gov/analysis/matriz_migracao_timeline.csv')
        print("✅ Matriz de migração salva")

        # Salvar value propositions
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/value_propositions.json', 'w', encoding='utf-8') as f:
            json.dump(value_props, f, ensure_ascii=False, indent=2)
        print("✅ Value propositions salvas")

        # Criar relatório executivo
        self.create_executive_report(substitute_df, timeline_matrix)

    def create_executive_report(self, substitute_df, timeline_matrix):
        """Cria relatório executivo"""

        total_current, total_potential = self.calculate_total_market(substitute_df)

        report = f"""
# MAPA DE SUBSTITUTOS: EAD GENÉRICO → IDIOMAS
## Relatório Executivo - {datetime.now().strftime('%Y-%m-%d')}

### 📊 RESUMO EXECUTIVO

**OPORTUNIDADE IDENTIFICADA:**
- {len(substitute_df)} órgãos com EAD genérico sem soluções de idiomas
- Mercado atual EAD: R$ {total_current:,.2f}
- Potencial mercado idiomas: R$ {total_potential:,.2f}
- Taxa de penetração estimada: {(total_potential/total_current)*100:.1f}%

### 🎯 TOP 10 PROSPECTS (Low-Hanging Fruits)

| Órgão | Score | Gasto EAD | Potencial | Timeline |
|-------|-------|-----------|-----------|----------|
"""

        for _, row in substitute_df.head(10).iterrows():
            report += f"| {row['orgao'][:50]}... | {row['score_total']:.1f} | R$ {row['total_gasto_edtech']:,.0f} | R$ {row['potencial_mercado_r$']:,.0f} | {row['timeline_provavel']} |\n"

        report += f"""

### 📈 ROADMAP DE CONVERSÃO

| Timeline | Órgãos | Mercado Atual | Potencial |
|----------|--------|---------------|-----------|
"""

        for timeline, data in timeline_matrix.iterrows():
            report += f"| {timeline} | {data['Num_Orgaos']} | R$ {data['Mercado_Atual_EAD']:,.0f} | R$ {data['Potencial_Idiomas']:,.0f} |\n"

        report += """

### 🎯 ESTRATÉGIA DE ABORDAGEM

**Q1 2025 - Ação Imediata:**
- Foco nos órgãos com score > 4.0
- Priorizar Ministérios com necessidade internacional
- Proposta de migração gradual (piloto + expansão)

**Q2-Q3 2025 - Expansão:**
- Órgãos com score 3.0-4.0
- Casos de sucesso como referência
- Modelo de ROI comprovado

**Q4 2025 - Consolidação:**
- Órgãos restantes com score < 3.0
- Oferta padronizada baseada em aprendizados

### 💡 VALUE PROPOSITIONS CHAVE

1. **Evolução Natural:** "Próximo passo da sua jornada digital educacional"
2. **ROI Comprovado:** "Investimento existente + especialização = maior impacto"
3. **Necessidade Missional:** "Capacitação alinhada aos objetivos estratégicos"
4. **Facilidade de Migração:** "Transição suave baseada na experiência EAD atual"

### 📞 PRÓXIMOS PASSOS

1. **Validação:** Confirmar dados com prospecção ativa
2. **Priorização:** Ranking por facilidade de conversão
3. **Customização:** Proposta específica por órgão
4. **Execução:** Plano de abordagem coordenado

---
*Análise gerada automaticamente baseada em dados de contratos públicos 2023*
"""

        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/relatorio_executivo_substitutos.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print("✅ Relatório executivo criado")

def main():
    """Função principal"""
    print("🚀 ANÁLISE DE SUBSTITUTOS: EAD GENÉRICO → IDIOMAS")
    print("=" * 60)

    analyzer = SubstituteAnalyzer()

    # Executar análise completa
    substitute_df = analyzer.create_substitute_analysis()

    if substitute_df is not None and len(substitute_df) > 0:
        print(f"\n🎯 ENCONTRADOS {len(substitute_df)} CANDIDATOS A SUBSTITUIÇÃO")

        # Gerar matriz de migração
        timeline_matrix = analyzer.generate_migration_matrix(substitute_df)

        # Calcular mercado total
        analyzer.calculate_total_market(substitute_df)

        # Gerar value propositions
        value_props = analyzer.generate_value_propositions(substitute_df)

        # Salvar resultados
        analyzer.save_results(substitute_df, timeline_matrix, value_props)

        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("📁 Resultados salvos em /home/danielfugisawa/pesquisa_prospect_gov/analysis/")

    else:
        print("❌ Nenhum candidato identificado ou erro na análise")

if __name__ == "__main__":
    main()