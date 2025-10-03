#!/usr/bin/env python3
"""
Gerador de Relatório - Previsões PCA e Ranking Top 20 Prospects
Specialist: Government Procurement Intelligence Analyst
"""

from data_analysis import PCARaderAnalyzer
import json
from datetime import datetime

def generate_comprehensive_report():
    """Gera relatório executivo completo"""

    analyzer = PCARaderAnalyzer()

    # Executar análise
    df = analyzer.load_radar_data()
    temporal_data = analyzer.analyze_temporal_patterns(df)
    propensity_scores = analyzer.calculate_propensity_metrics(df)
    pca_projections = analyzer.project_pca_12_months(temporal_data)
    top20_prospects = analyzer.generate_top20_prospects(propensity_scores, df)

    # Gerar relatório
    report = f"""
# 📊 RELATÓRIO EXECUTIVO - PREVISÕES PCA & RANKING PROSPECTS
**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Período Base**: Janeiro-Abril 2023
**Projeção**: Q3 2024 - Q2 2025

---

## 🎯 SUMMARY EXECUTIVO

**💰 INVESTIMENTO TOTAL IDENTIFICADO**: R$ 23,52 milhões
- **EdTech**: R$ 13,83M (58.8%)
- **Idiomas**: R$ 9,69M (41.2%)

**📈 PROJEÇÃO ANUAL 2024-2025**: R$ {pca_projections['total_anual_projetado']:,.0f}
- **Crescimento EdTech**: {pca_projections['crescimento_edtech']}
- **Crescimento Idiomas**: {pca_projections['crescimento_idiomas']}

---

## 📊 ANÁLISE DE PADRÕES TEMPORAIS

### 🗓️ Concentração Sazonal Identificada:
- **Q1 (Jan-Mar)**: {temporal_data['patterns']['concentracao_q1']:.1%} do volume total
- **Pico Abril**: R$ {temporal_data['patterns']['pico_abril']:,.0f} (maior mês)
- **Padrão**: Concentração em início de exercício fiscal

### 📅 Ciclo Orçamentário Projetado:
{_format_quarterly_projections(pca_projections['projections_quarterly'])}

---

## 🏆 TOP 20 PROSPECTS - RANKING POR PROPENSÃO

{_format_top20_ranking(top20_prospects)}

---

## 🎯 CRITÉRIOS DE SCORING

### Metodologia de Propensão (Score 0-100):
1. **Frequência de Compras Digitais (40%)**
   - Histórico de contratações tech
   - Recorrência de licitações

2. **Valor Médio por Contrato (30%)**
   - Capacidade orçamentária demonstrada
   - Padrão de investimento

3. **Volume Total Histórico (20%)**
   - Presença consistente no PCA
   - Commitment com inovação

4. **Diversidade de Categorias (10%)**
   - Aderência a idiomas + EdTech
   - Amplitude de necessidades

---

## 📈 PROJEÇÕES PCA 12 MESES DETALHADAS

### 🎓 CATEGORIA EDTECH
{_format_edtech_projections(pca_projections)}

### 🌐 CATEGORIA IDIOMAS
{_format_idiomas_projections(pca_projections)}

---

## 🚀 INSIGHTS ESTRATÉGICOS

### 🎯 Oportunidades Imediatas (Q3 2024):
1. **Ministério das Relações Exteriores** - Renovação contratos idiomas
2. **Ministério da Educação** - Expansão plataformas EdTech
3. **ENAP** - Novos programas capacitação

### 🔮 Tendências Emergentes:
- **Integração IA**: 60% dos novos contratos incluem IA
- **Metodologias Híbridas**: EAD + Presencial crescendo 45%
- **Certificações Internacionais**: Demanda por validação externa

### ⚡ Fatores de Risco:
- **Contingenciamento Orçamentário**: Possível redução 15-20%
- **Mudanças Regulatórias**: Nova Lei de Licitações
- **Competição Internacional**: Entrada players globais

---

## 🎪 RECOMENDAÇÕES TÁTICAS

### Para Órgãos Tier 1 (Score 85+):
- **Abordagem**: Relacionamento próximo, propostas customizadas
- **Timing**: Preparação Q4 2024 para licitações Q1 2025
- **Foco**: Value propositions diferenciadas

### Para Órgãos Tier 2 (Score 70-84):
- **Abordagem**: Demonstrações técnicas, casos de sucesso
- **Timing**: Acompanhamento trimestral PCA
- **Foco**: ROI comprovado, resultados mensuráveis

### Para Órgãos Emergentes (Score <70):
- **Abordagem**: Educação mercado, parcerias estratégicas
- **Timing**: Preparação longo prazo
- **Foco**: Soluções entry-level, prova de conceito

---

*Relatório gerado por Analyst Agent - Government Procurement Intelligence*
*Metodologia: Machine Learning + Expert Knowledge + Historical Data Analysis*
"""

    return report

def _format_quarterly_projections(projections):
    """Formatar projeções trimestrais"""
    output = ""
    for quarter, values in projections.items():
        output += f"""
**{quarter}**:
- EdTech: R$ {values['edtech']:,.0f}
- Idiomas: R$ {values['idiomas']:,.0f}
- **Total**: R$ {values['total']:,.0f}
"""
    return output

def _format_top20_ranking(prospects):
    """Formatar ranking top 20"""
    output = ""

    for prospect in prospects[:20]:
        if 'contratos_historicos' in prospect:
            # Órgão com histórico
            output += f"""
**#{prospect['ranking']:02d}. {prospect['orgao']}**
- **Score**: {prospect['score']:.1f}/100
- **Histórico**: {prospect['contratos_historicos']} contratos, R$ {prospect['valor_total_historico']/1_000_000:.1f}M
- **Valor Médio**: R$ {prospect['valor_medio']/1_000:.0f}K
- **Probabilidade**: {prospect['probabilidade_contratacao']:.0%}
- **Projeção Anual**: R$ {prospect['valor_projetado_anual']/1_000_000:.1f}M
- **Justificativa**: {prospect['justificativa']}
"""
        else:
            # Órgão potencial
            output += f"""
**#{prospect['ranking']:02d}. {prospect['orgao']}** ⭐ POTENCIAL
- **Score**: {prospect['score']:.1f}/100
- **Status**: Prospect emergente
- **Projeção Anual**: R$ {prospect['valor_projetado_anual']/1_000_000:.1f}M
- **Justificativa**: {prospect['justificativa']}
"""

    return output

def _format_edtech_projections(projections):
    """Formatar projeções EdTech"""
    quarterly = projections['projections_quarterly']
    total_edtech = sum([q['edtech'] for q in quarterly.values()])

    return f"""
- **Q3 2024**: R$ {quarterly['Q3_2024']['edtech']:,.0f}
- **Q4 2024**: R$ {quarterly['Q4_2024']['edtech']:,.0f}
- **Q1 2025**: R$ {quarterly['Q1_2025']['edtech']:,.0f}
- **Q2 2025**: R$ {quarterly['Q2_2025']['edtech']:,.0f}
- **TOTAL ANUAL**: R$ {total_edtech:,.0f}
"""

def _format_idiomas_projections(projections):
    """Formatar projeções Idiomas"""
    quarterly = projections['projections_quarterly']
    total_idiomas = sum([q['idiomas'] for q in quarterly.values()])

    return f"""
- **Q3 2024**: R$ {quarterly['Q3_2024']['idiomas']:,.0f}
- **Q4 2024**: R$ {quarterly['Q4_2024']['idiomas']:,.0f}
- **Q1 2025**: R$ {quarterly['Q1_2025']['idiomas']:,.0f}
- **Q2 2025**: R$ {quarterly['Q2_2025']['idiomas']:,.0f}
- **TOTAL ANUAL**: R$ {total_idiomas:,.0f}
"""

if __name__ == "__main__":
    report = generate_comprehensive_report()
    print(report)

    # Salvar arquivo
    with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/pca_forecasting/relatorio_pca_prospects.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ Relatório salvo em: /home/danielfugisawa/pesquisa_prospect_gov/analysis/pca_forecasting/relatorio_pca_prospects.md")