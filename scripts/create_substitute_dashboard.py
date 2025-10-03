#!/usr/bin/env python3
"""
DASHBOARD DE SUBSTITUTOS: Visualização consolidada da análise
Cria visualizações e relatório final para o mapa de substitutos EAD → Idiomas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo
plt.style.use('default')
sns.set_palette("husl")

class SubstituteDashboard:
    def __init__(self):
        self.substitute_data = None
        self.financial_data = None

    def load_data(self):
        """Carrega dados da análise"""
        try:
            self.substitute_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/analysis/mapa_substitutos_edtech_idiomas.csv')

            with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/financial_projections.json', 'r') as f:
                self.financial_data = json.load(f)

            print("✅ Dados carregados com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def create_opportunity_overview(self):
        """Cria visão geral das oportunidades"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('MAPA DE SUBSTITUTOS: EAD GENÉRICO → IDIOMAS\nVisão Geral das Oportunidades', fontsize=16, fontweight='bold')

        # 1. Score por Órgão
        orgaos_short = [org[:25] + '...' if len(org) > 25 else org for org in self.substitute_data['orgao']]
        bars1 = ax1.bar(orgaos_short, self.substitute_data['score_total'],
                       color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Score de Potencial por Órgão', fontweight='bold')
        ax1.set_ylabel('Score Total (0-5)')
        ax1.tick_params(axis='x', rotation=45)

        # Adicionar valores nas barras
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        # 2. Investimento Atual vs Potencial
        x = np.arange(len(orgaos_short))
        width = 0.35

        bars2 = ax2.bar(x - width/2, self.substitute_data['total_gasto_edtech'], width,
                       label='EAD Atual', color='#FFA07A', alpha=0.8)
        bars3 = ax2.bar(x + width/2, self.substitute_data['potencial_mercado_r$'], width,
                       label='Potencial Idiomas', color='#98D8C8', alpha=0.8)

        ax2.set_title('Investimento: Atual vs Potencial', fontweight='bold')
        ax2.set_ylabel('Valor (R$)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(orgaos_short, rotation=45)
        ax2.legend()
        ax2.ticklabel_format(style='plain', axis='y')

        # 3. Timeline de Conversão
        timeline_data = self.substitute_data.groupby('timeline_provavel').agg({
            'potencial_mercado_r$': 'sum',
            'orgao': 'count'
        }).reset_index()

        ax3.pie(timeline_data['potencial_mercado_r$'], labels=timeline_data['timeline_provavel'],
               autopct='%1.1f%%', startangle=90, colors=['#FFB6C1', '#87CEEB', '#DDA0DD'])
        ax3.set_title('Distribuição do Potencial por Timeline', fontweight='bold')

        # 4. Necessidade Missional vs Facilidade de Migração
        scatter = ax4.scatter(self.substitute_data['necessidade_missional_score'],
                            self.substitute_data['facilidade_migracao_score'],
                            s=self.substitute_data['potencial_mercado_r$']/10000,
                            c=self.substitute_data['score_total'],
                            cmap='viridis', alpha=0.7)

        ax4.set_xlabel('Necessidade Missional (1-5)')
        ax4.set_ylabel('Facilidade de Migração (1-5)')
        ax4.set_title('Mapa de Posicionamento\n(Tamanho = Potencial)', fontweight='bold')

        # Adicionar labels dos órgãos
        for i, org in enumerate(orgaos_short):
            ax4.annotate(f'{i+1}',
                        (self.substitute_data.iloc[i]['necessidade_missional_score'],
                         self.substitute_data.iloc[i]['facilidade_migracao_score']),
                        fontweight='bold', fontsize=10)

        plt.colorbar(scatter, ax=ax4, label='Score Total')
        plt.tight_layout()
        plt.savefig('/home/danielfugisawa/pesquisa_prospect_gov/analysis/substitute_opportunities_overview.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def create_financial_projections_chart(self):
        """Cria gráfico de projeções financeiras"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('PROJEÇÕES FINANCEIRAS: Cenários de Conversão', fontsize=16, fontweight='bold')

        # 1. Comparação de Cenários
        scenarios = ['Conservador\n(30%)', 'Realista\n(50%)', 'Otimista\n(70%)']
        values = [
            self.financial_data['Conservador (30% conversão)']['total_anual'],
            self.financial_data['Realista (50% conversão)']['total_anual'],
            self.financial_data['Otimista (70% conversão)']['total_anual']
        ]

        bars = ax1.bar(scenarios, values, color=['#FFB6C1', '#87CEEB', '#98FB98'])
        ax1.set_title('Receita Anual por Cenário', fontweight='bold')
        ax1.set_ylabel('Receita (R$)')
        ax1.ticklabel_format(style='plain', axis='y')

        # Adicionar valores
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 50000,
                    f'R$ {value:,.0f}', ha='center', va='bottom', fontweight='bold')

        # 2. Evolução Trimestral (Cenário Realista)
        realista = self.financial_data['Realista (50% conversão)']
        quarters = ['Q1 2025', 'Q2 2025', 'Q4 2025']
        cumulative = [realista['q1_2025'], realista['q2_2025'], realista['q4_2025']]

        ax2.plot(quarters, cumulative, marker='o', linewidth=3, markersize=8, color='#4ECDC4')
        ax2.fill_between(quarters, cumulative, alpha=0.3, color='#4ECDC4')
        ax2.set_title('Evolução da Receita Acumulada\n(Cenário Realista)', fontweight='bold')
        ax2.set_ylabel('Receita Acumulada (R$)')
        ax2.ticklabel_format(style='plain', axis='y')
        ax2.grid(True, alpha=0.3)

        # Adicionar valores
        for i, (q, v) in enumerate(zip(quarters, cumulative)):
            ax2.annotate(f'R$ {v:,.0f}', (i, v), textcoords="offset points",
                        xytext=(0,10), ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig('/home/danielfugisawa/pesquisa_prospect_gov/analysis/financial_projections.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def create_strategy_matrix(self):
        """Cria matriz de estratégia comercial"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Preparar dados para matriz
        x = self.substitute_data['facilidade_migracao_score']
        y = self.substitute_data['necessidade_missional_score']
        sizes = self.substitute_data['potencial_mercado_r$'] / 50000
        colors = self.substitute_data['score_total']

        scatter = ax.scatter(x, y, s=sizes, c=colors, cmap='RdYlGn', alpha=0.7, edgecolors='black')

        # Adicionar quadrantes
        ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=2.5, color='gray', linestyle='--', alpha=0.5)

        # Labels dos quadrantes
        ax.text(4.5, 4.5, 'PRIORIDADE\nMAXIMA', fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
        ax.text(1.5, 4.5, 'NECESSÁRIO\nMAS DIFÍCIL', fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        ax.text(4.5, 1.5, 'FÁCIL MAS\nPOUCO NECESSÁRIO', fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
        ax.text(1.5, 1.5, 'BAIXA\nPRIORIDADE', fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))

        # Adicionar labels dos órgãos
        for i, org in enumerate(self.substitute_data['orgao']):
            org_short = org[:15] + '...' if len(org) > 15 else org
            ax.annotate(f'{i+1}. {org_short}',
                       (x.iloc[i], y.iloc[i]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        ax.set_xlabel('Facilidade de Migração (1-5)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Necessidade Missional (1-5)', fontsize=12, fontweight='bold')
        ax.set_title('MATRIZ ESTRATÉGICA: Priorização de Prospects\n(Tamanho = Potencial de Mercado)',
                    fontsize=14, fontweight='bold')

        # Colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Score Total de Potencial', fontweight='bold')

        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(0.5, 5.5)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/danielfugisawa/pesquisa_prospect_gov/analysis/strategy_matrix.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def create_executive_dashboard(self):
        """Cria dashboard executivo consolidado"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

        fig.suptitle('DASHBOARD EXECUTIVO: MAPA DE SUBSTITUTOS EAD → IDIOMAS',
                    fontsize=20, fontweight='bold', y=0.98)

        # KPIs principais
        ax_kpi = fig.add_subplot(gs[0, :])
        ax_kpi.axis('off')

        total_market = self.substitute_data['total_gasto_edtech'].sum()
        total_potential = self.substitute_data['potencial_mercado_r$'].sum()
        num_prospects = len(self.substitute_data)
        avg_score = self.substitute_data['score_total'].mean()

        kpi_text = f"""
        MÉTRICAS PRINCIPAIS:

        📊 ÓRGÃOS IDENTIFICADOS: {num_prospects}
        💰 MERCADO ATUAL EAD: R$ {total_market:,.0f}
        🎯 POTENCIAL IDIOMAS: R$ {total_potential:,.0f}
        📈 TAXA DE PENETRAÇÃO: {(total_potential/total_market)*100:.1f}%
        ⭐ SCORE MÉDIO: {avg_score:.1f}/5.0
        """

        ax_kpi.text(0.5, 0.5, kpi_text, fontsize=16, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))

        # Gráfico de barras - Potencial por órgão
        ax1 = fig.add_subplot(gs[1, :2])
        orgaos_short = [org[:20] + '...' if len(org) > 20 else org for org in self.substitute_data['orgao']]
        bars = ax1.barh(orgaos_short, self.substitute_data['potencial_mercado_r$'],
                       color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Potencial de Mercado por Órgão', fontweight='bold')
        ax1.set_xlabel('Potencial (R$)')

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax1.text(width + 20000, bar.get_y() + bar.get_height()/2,
                    f'R$ {width:,.0f}', ha='left', va='center', fontweight='bold')

        # Timeline de implementação
        ax2 = fig.add_subplot(gs[1, 2:])
        timeline_data = self.substitute_data.groupby('timeline_provavel').agg({
            'potencial_mercado_r$': 'sum'
        }).reset_index()

        wedges, texts, autotexts = ax2.pie(timeline_data['potencial_mercado_r$'],
                                          labels=timeline_data['timeline_provavel'],
                                          autopct='%1.1f%%', startangle=90,
                                          colors=['#FFB6C1', '#87CEEB', '#DDA0DD'])
        ax2.set_title('Distribuição por Timeline', fontweight='bold')

        # Ranking de prioridades
        ax3 = fig.add_subplot(gs[2, :2])
        ranking = self.substitute_data.sort_values('score_total', ascending=True)
        colors_rank = ['#FF6B6B' if x >= 4 else '#4ECDC4' if x >= 3 else '#FFA07A'
                      for x in ranking['score_total']]

        bars_rank = ax3.barh(range(len(ranking)), ranking['score_total'], color=colors_rank)
        ax3.set_yticks(range(len(ranking)))
        ax3.set_yticklabels([org[:25] + '...' if len(org) > 25 else org for org in ranking['orgao']])
        ax3.set_xlabel('Score Total')
        ax3.set_title('Ranking de Prioridade', fontweight='bold')

        for i, bar in enumerate(bars_rank):
            width = bar.get_width()
            ax3.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}', ha='left', va='center', fontweight='bold')

        # Cenários financeiros
        ax4 = fig.add_subplot(gs[2, 2:])
        scenarios = ['Conservador', 'Realista', 'Otimista']
        values = [
            self.financial_data['Conservador (30% conversão)']['total_anual'],
            self.financial_data['Realista (50% conversão)']['total_anual'],
            self.financial_data['Otimista (70% conversão)']['total_anual']
        ]

        bars_fin = ax4.bar(scenarios, values, color=['#FFB6C1', '#87CEEB', '#98FB98'])
        ax4.set_title('Cenários de Receita Anual', fontweight='bold')
        ax4.set_ylabel('Receita (R$)')
        ax4.ticklabel_format(style='plain', axis='y')

        for bar, value in zip(bars_fin, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 20000,
                    f'R$ {value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.savefig('/home/danielfugisawa/pesquisa_prospect_gov/analysis/executive_dashboard.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    def create_final_report(self):
        """Cria relatório final consolidado"""

        total_market = self.substitute_data['total_gasto_edtech'].sum()
        total_potential = self.substitute_data['potencial_mercado_r$'].sum()
        realista = self.financial_data['Realista (50% conversão)']

        report = f"""
# MAPA DE SUBSTITUTOS: EAD GENÉRICO → IDIOMAS
## Relatório Final Consolidado - {datetime.now().strftime('%Y-%m-%d')}

---

## 🎯 RESUMO EXECUTIVO

### OPORTUNIDADE IDENTIFICADA
- **{len(self.substitute_data)} órgãos** com EAD genérico sem soluções de idiomas
- **Mercado atual EAD:** R$ {total_market:,.0f}
- **Potencial mercado idiomas:** R$ {total_potential:,.0f}
- **Taxa de penetração estimada:** {(total_potential/total_market)*100:.1f}%

### PRIORIZAÇÃO ESTRATÉGICA

| Ranking | Órgão | Score | Investimento EAD | Potencial Idiomas | Timeline |
|---------|-------|-------|------------------|-------------------|----------|"""

        for i, (_, row) in enumerate(self.substitute_data.sort_values('score_total', ascending=False).iterrows(), 1):
            report += f"""
| {i}º | {row['orgao'][:40]}... | {row['score_total']:.1f} | R$ {row['total_gasto_edtech']:,.0f} | R$ {row['potencial_mercado_r$']:,.0f} | {row['timeline_provavel']} |"""

        report += f"""

---

## 💰 PROJEÇÕES FINANCEIRAS

### CENÁRIOS DE CONVERSÃO

| Cenário | Taxa Conversão | Receita Anual | Crescimento |
|---------|----------------|---------------|-------------|
| Conservador | 30% | R$ {self.financial_data['Conservador (30% conversão)']['total_anual']:,.0f} | {self.financial_data['Conservador (30% conversão)']['crescimento_anual']} |
| **Realista** | **50%** | **R$ {realista['total_anual']:,.0f}** | **{realista['crescimento_anual']}** |
| Otimista | 70% | R$ {self.financial_data['Otimista (70% conversão)']['total_anual']:,.0f} | {self.financial_data['Otimista (70% conversão)']['crescimento_anual']} |

### EVOLUÇÃO TRIMESTRAL (Cenário Realista)

| Trimestre | Receita Acumulada | Órgão Adicionado |
|-----------|-------------------|------------------|
| Q1 2025 | R$ {realista['q1_2025']:,.0f} | Ministério da Educação |
| Q2 2025 | R$ {realista['q2_2025']:,.0f} | FNDE |
| Q4 2025 | R$ {realista['q4_2025']:,.0f} | CAPES |

---

## 🎯 ESTRATÉGIA DE ABORDAGEM

### PRIORIDADE MÁXIMA (Q1 2025)
**MINISTÉRIO DA EDUCAÇÃO**
- **Score:** 4.2/5.0
- **Investimento atual:** R$ 9,6M em EAD genérico
- **Potencial:** R$ 2,88M
- **Abordagem:** Apresentação executiva sobre modernização da capacitação digital
- **Stakeholders:** Secretário Executivo, Diretoria de Tecnologia

### PRIORIDADE ALTA (Q2 2025)
**FNDE - FUNDO NACIONAL DE DESENVOLVIMENTO DA EDUCAÇÃO**
- **Score:** 3.4/5.0
- **Investimento atual:** R$ 1,85M
- **Potencial:** R$ 555K
- **Abordagem:** ROI e casos de sucesso em educação
- **Stakeholders:** Presidência, Diretoria de Tecnologia

### PRIORIDADE MÉDIA (Q4 2025)
**CAPES - COORDENAÇÃO DE APERFEIÇOAMENTO DE PESSOAL**
- **Score:** 1.6/5.0
- **Investimento atual:** R$ 980K
- **Potencial:** R$ 294K
- **Abordagem:** Inglês acadêmico e publicações internacionais
- **Stakeholders:** Presidência, Diretoria de Avaliação

---

## 💡 VALUE PROPOSITIONS ESPECÍFICAS

### Para o Ministério da Educação
- **Evolução Natural:** "Próximo passo da sua jornada digital educacional"
- **Alinhamento Estratégico:** Capacitação para cooperação técnica internacional
- **ROI Comprovado:** Especialização gera maior impacto que EAD genérico

### Para o FNDE
- **Eficiência:** Otimização de recursos educacionais
- **Comunicação Global:** Melhor interação com organismos multilaterais
- **ROI Superior:** Retorno mensurável vs EAD generalista

### Para a CAPES
- **Fortalecimento Acadêmico:** Aumento de publicações internacionais
- **Cooperação:** Facilita intercâmbios e parcerias acadêmicas
- **Avaliação:** Melhoria na qualidade dos programas de pós-graduação

---

## ⚡ PLANO DE AÇÃO IMEDIATA (30 DIAS)

### Semana 1-2: Preparação
- [ ] **Validação de dados** com pesquisa primária
- [ ] **Desenvolvimento de materiais** comerciais customizados
- [ ] **Treinamento da equipe** de vendas especializada

### Semana 3-4: Prospecção
- [ ] **Agendamento estratégico** com Ministério da Educação
- [ ] **Preparação de proposta** executiva customizada
- [ ] **Benchmark competitivo** detalhado

### Semana 5-8: Negociação
- [ ] **Apresentações executivas** com tomadores de decisão
- [ ] **Negociação de piloto** (10% do orçamento = R$ 960K)
- [ ] **Definição de métricas** de sucesso

### Semana 9-12: Implementação
- [ ] **Piloto com 50-100 servidores** prioritários
- [ ] **Acompanhamento e ajustes** semanais
- [ ] **Documentação de resultados** para casos de sucesso

---

## 🏆 FATORES CRÍTICOS DE SUCESSO

### Diferenciais Competitivos
1. **Especialização vs Generalização**
2. **ROI Mensurável** em competências linguísticas
3. **Metodologia Comprovada** para setor público
4. **Certificações Internacionais** reconhecidas
5. **Suporte Técnico Especializado**

### Riscos e Mitigações
- **Resistência à mudança** → Casos de sucesso comprovados
- **Restrições orçamentárias** → ROI claro e realocação
- **Concorrência EAD** → Diferenciação de valor especializado

---

## 📈 POTENCIAL DE EXPANSÃO (2026+)

### Mercado Secundário
- **Universidades Federais:** 20-30 instituições
- **Órgãos Estaduais:** Replicação do modelo federal
- **Autarquias Especializadas:** IBAMA, ANVISA, etc.

### Projeção Total
- **Mercado Potencial:** R$ 15-25M
- **Timeline:** 18-24 meses
- **ROI Consolidado:** 150-250%

---

## 📞 PRÓXIMOS PASSOS EXECUTIVOS

1. **APROVAÇÃO ESTRATÉGICA** → Alinhar diretrizes comerciais
2. **MOBILIZAÇÃO DE RECURSOS** → Equipe dedicada aos 3 prospects
3. **CRONOGRAMA DE EXECUÇÃO** → Implementar plano de 30 dias
4. **MÉTRICAS DE ACOMPANHAMENTO** → KPIs semanais de progresso

---

### 🎯 META 2025
**Converter pelo menos 2 dos 3 prospects identificados**
**Receita alvo: R$ 1,8M (cenário realista)**
**Base para expansão em 2026**

---
*Análise completa disponível em:*
- `/analysis/mapa_substitutos_edtech_idiomas.csv`
- `/analysis/commercial_strategies.json`
- `/analysis/financial_projections.json`
- `/analysis/executive_dashboard.png`

*Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/RELATORIO_FINAL_SUBSTITUTOS.md', 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    """Função principal do dashboard"""
    print("📊 CRIANDO DASHBOARD DE SUBSTITUTOS")
    print("=" * 40)

    dashboard = SubstituteDashboard()

    if not dashboard.load_data():
        return

    print("🎨 Gerando visualizações...")

    # Criar visualizações
    dashboard.create_opportunity_overview()
    print("✅ Visão geral das oportunidades")

    dashboard.create_financial_projections_chart()
    print("✅ Projeções financeiras")

    dashboard.create_strategy_matrix()
    print("✅ Matriz estratégica")

    dashboard.create_executive_dashboard()
    print("✅ Dashboard executivo")

    dashboard.create_final_report()
    print("✅ Relatório final")

    print("\n🎯 DASHBOARD COMPLETO CRIADO!")
    print("📁 Arquivos gerados:")
    print("   - substitute_opportunities_overview.png")
    print("   - financial_projections.png")
    print("   - strategy_matrix.png")
    print("   - executive_dashboard.png")
    print("   - RELATORIO_FINAL_SUBSTITUTOS.md")

if __name__ == "__main__":
    main()