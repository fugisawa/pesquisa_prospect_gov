#!/usr/bin/env python3
"""
ANÁLISE EXPANDIDA DE SUBSTITUTOS: UNIVERSIDADES E ESTRATÉGIAS COMERCIAIS
Complementa o mapa de substitutos com análise aprofundada e estratégias específicas
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

class EnhancedSubstituteAnalyzer:
    def __init__(self):
        self.substitute_data = None

    def load_substitute_data(self):
        """Carrega dados da análise de substitutos"""
        try:
            self.substitute_data = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/analysis/mapa_substitutos_edtech_idiomas.csv')
            print(f"✅ Dados de substitutos carregados: {len(self.substitute_data)} órgãos")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def analyze_university_potential(self):
        """Analisa potencial específico de universidades federais"""
        print("\n🎓 ANÁLISE ESPECÍFICA: UNIVERSIDADES FEDERAIS")
        print("=" * 50)

        # Perfis típicos de universidades federais com necessidade de idiomas
        university_profiles = {
            "Universidades com Programas Internacionais": {
                "potential_investment": "R$ 500K - R$ 2M/ano",
                "key_drivers": [
                    "Programas de intercâmbio",
                    "Publicações internacionais",
                    "Cooperação técnica internacional",
                    "Dupla diplomação"
                ],
                "languages_needed": ["Inglês", "Espanhol", "Francês"],
                "migration_timeline": "Q1-Q2 2025",
                "value_proposition": "Capacitação para pesquisa internacional e publicação acadêmica"
            },
            "Universidades Técnicas/Tecnológicas": {
                "potential_investment": "R$ 300K - R$ 1M/ano",
                "key_drivers": [
                    "Documentação técnica internacional",
                    "Certificações internacionais",
                    "Pesquisa aplicada global",
                    "Parcerias com empresas multinacionais"
                ],
                "languages_needed": ["Inglês técnico", "Alemão"],
                "migration_timeline": "Q2-Q3 2025",
                "value_proposition": "Inglês técnico especializado para inovação e pesquisa"
            },
            "Universidades de Medicina/Saúde": {
                "potential_investment": "R$ 400K - R$ 1.5M/ano",
                "key_drivers": [
                    "Literatura médica internacional",
                    "Conferências globais",
                    "Protocolos internacionais",
                    "Telemedicina"
                ],
                "languages_needed": ["Inglês médico", "Francês"],
                "migration_timeline": "Q1-Q2 2025",
                "value_proposition": "Inglês médico para atualização científica global"
            }
        }

        return university_profiles

    def create_commercial_strategies(self):
        """Cria estratégias comerciais específicas por órgão"""
        print("\n💼 ESTRATÉGIAS COMERCIAIS ESPECÍFICAS")
        print("=" * 40)

        if self.substitute_data is None:
            return None

        strategies = {}

        for _, row in self.substitute_data.iterrows():
            orgao = row['orgao']
            score = row['score_total']
            gasto_atual = row['total_gasto_edtech']
            timeline = row['timeline_provavel']

            strategy = {
                "prioridade": self._get_priority_level(score),
                "abordagem_inicial": self._get_initial_approach(orgao, score),
                "proposta_piloto": self._get_pilot_proposal(gasto_atual),
                "investimento_sugerido": self._get_suggested_investment(gasto_atual),
                "roi_projetado": self._calculate_projected_roi(gasto_atual),
                "timeline_negociacao": timeline,
                "stakeholders_chave": self._identify_key_stakeholders(orgao),
                "argumentos_principais": self._get_main_arguments(orgao),
                "diferenciais_competitivos": self._get_competitive_advantages(orgao)
            }

            strategies[orgao] = strategy

        return strategies

    def _get_priority_level(self, score):
        """Determina nível de prioridade"""
        if score >= 4.0:
            return "ALTA - Abordagem imediata"
        elif score >= 3.0:
            return "MÉDIA - Abordagem em Q2"
        else:
            return "BAIXA - Abordagem em Q4"

    def _get_initial_approach(self, orgao, score):
        """Define abordagem inicial"""
        if "Ministério da Educação" in orgao:
            return "Apresentação executiva sobre modernização da capacitação digital"
        elif "FNDE" in orgao:
            return "Demonstração de ROI e casos de sucesso em educação"
        elif "CAPES" in orgao:
            return "Foco em inglês acadêmico e publicações internacionais"
        else:
            return "Abordagem consultiva sobre necessidades específicas"

    def _get_pilot_proposal(self, gasto_atual):
        """Propõe projeto piloto"""
        pilot_budget = gasto_atual * 0.1  # 10% do gasto atual
        return {
            "orcamento": f"R$ {pilot_budget:,.0f}",
            "duracao": "3-6 meses",
            "escopo": "50-100 servidores prioritários",
            "métricas": ["Engajamento", "Progresso linguístico", "Satisfação", "ROI"]
        }

    def _get_suggested_investment(self, gasto_atual):
        """Sugere investimento total"""
        suggested = gasto_atual * 0.25  # 25% do gasto EAD atual
        return f"R$ {suggested:,.0f}/ano (25% do orçamento EAD atual)"

    def _calculate_projected_roi(self, gasto_atual):
        """Calcula ROI projetado"""
        return {
            "redução_custos_treinamento": "20-30%",
            "melhoria_produtividade": "15-25%",
            "acesso_a_mercados_globais": "Incalculável",
            "tempo_de_retorno": "18-24 meses"
        }

    def _identify_key_stakeholders(self, orgao):
        """Identifica stakeholders chave"""
        if "Ministério da Educação" in orgao:
            return ["Secretário Executivo", "Diretoria de Tecnologia", "Coordenação de Capacitação"]
        elif "FNDE" in orgao:
            return ["Presidência", "Diretoria de Tecnologia", "Coordenação Pedagógica"]
        elif "CAPES" in orgao:
            return ["Presidência", "Diretoria de Avaliação", "Coordenação Internacional"]
        else:
            return ["Direção Geral", "TI", "Recursos Humanos"]

    def _get_main_arguments(self, orgao):
        """Define argumentos principais"""
        if "Educação" in orgao:
            return [
                "Alinhamento com diretrizes de internacionalização da educação",
                "Capacitação para cooperação técnica internacional",
                "Modernização da formação de educadores",
                "Preparação para demandas globais da educação"
            ]
        elif "FNDE" in orgao:
            return [
                "Eficiência na gestão de recursos educacionais",
                "Capacitação para programas internacionais",
                "Melhoria na comunicação com organismos multilaterais",
                "ROI superior comparado a EAD genérico"
            ]
        elif "CAPES" in orgao:
            return [
                "Fortalecimento da pós-graduação brasileira",
                "Aumento de publicações em periódicos internacionais",
                "Melhoria na avaliação de programas de pós-graduação",
                "Facilitar intercâmbios e cooperação acadêmica"
            ]
        else:
            return [
                "Modernização da capacitação de servidores",
                "Preparação para desafios globais",
                "Melhoria na comunicação institucional",
                "Otimização de investimentos em educação"
            ]

    def _get_competitive_advantages(self, orgao):
        """Define diferenciais competitivos"""
        return [
            "Especialização vs generalização",
            "Metodologia focada em resultados mensuráveis",
            "Experiência comprovada no setor público",
            "Suporte técnico especializado",
            "Integração com plataformas existentes",
            "Certificações reconhecidas internacionalmente"
        ]

    def create_risk_mitigation_plan(self):
        """Cria plano de mitigação de riscos"""
        print("\n⚠️ PLANO DE MITIGAÇÃO DE RISCOS")
        print("=" * 35)

        risks = {
            "Resistência à mudança": {
                "probabilidade": "Média",
                "impacto": "Alto",
                "mitigação": [
                    "Demonstrações práticas de benefícios",
                    "Casos de sucesso em órgãos similares",
                    "Envolvimento de stakeholders desde o início",
                    "Programa de change management"
                ]
            },
            "Restrições orçamentárias": {
                "probabilidade": "Alta",
                "impacto": "Alto",
                "mitigação": [
                    "Modelo de pagamento flexível",
                    "Demonstração clara de ROI",
                    "Proposta de realocação de recursos",
                    "Parcerias para financiamento"
                ]
            },
            "Concorrência de EAD genérico": {
                "probabilidade": "Média",
                "impacto": "Médio",
                "mitigação": [
                    "Diferenciação clara de valor",
                    "Preço competitivo com melhor valor",
                    "Proposta de complementaridade",
                    "Foco em resultados específicos"
                ]
            },
            "Mudanças na gestão": {
                "probabilidade": "Média",
                "impacto": "Alto",
                "mitigação": [
                    "Documentação de benefícios",
                    "Múltiplos pontos de contato",
                    "Contratos de longo prazo",
                    "Alinhamento com políticas públicas"
                ]
            }
        }

        return risks

    def generate_implementation_roadmap(self):
        """Gera roadmap detalhado de implementação"""
        print("\n📅 ROADMAP DE IMPLEMENTAÇÃO DETALHADO")
        print("=" * 45)

        roadmap = {
            "Q1 2025 - Preparação & Prospecção": {
                "semana_1-2": [
                    "Validação de dados com pesquisa primária",
                    "Desenvolvimento de materiais comerciais",
                    "Treinamento da equipe de vendas"
                ],
                "semana_3-4": [
                    "Agendamento com Ministério da Educação",
                    "Preparação de proposta customizada",
                    "Benchmark competitivo detalhado"
                ],
                "semana_5-8": [
                    "Apresentações executivas",
                    "Negociação de piloto",
                    "Definição de métricas de sucesso"
                ],
                "semana_9-12": [
                    "Implementação de piloto",
                    "Acompanhamento e ajustes",
                    "Documentação de resultados"
                ]
            },
            "Q2 2025 - Expansão": {
                "mês_1": [
                    "Abordagem FNDE com casos de sucesso",
                    "Proposta baseada em ROI comprovado",
                    "Negociação comercial"
                ],
                "mês_2": [
                    "Implementação FNDE",
                    "Refinamento da proposta de valor",
                    "Desenvolvimento de parcerias"
                ],
                "mês_3": [
                    "Análise de resultados consolidados",
                    "Preparação para expansão Q3",
                    "Otimização de processos"
                ]
            },
            "Q3-Q4 2025 - Consolidação": {
                "objetivos": [
                    "Abordagem CAPES e outros órgãos menores",
                    "Padronização da oferta",
                    "Escalabilidade da operação",
                    "Planejamento para 2026"
                ]
            }
        }

        return roadmap

    def calculate_financial_projections(self):
        """Calcula projeções financeiras detalhadas"""
        print("\n💰 PROJEÇÕES FINANCEIRAS DETALHADAS")
        print("=" * 40)

        # Cenários conservador, realista e otimista
        scenarios = {
            "Conservador (30% conversão)": {
                "q1_2025": 864000,  # 30% de R$ 2.88M (MEC)
                "q2_2025": 1030500,  # + 30% de R$ 555K (FNDE)
                "q4_2025": 1118700,  # + 30% de R$ 294K (CAPES)
                "total_anual": 1118700,
                "crescimento_anual": "15%"
            },
            "Realista (50% conversão)": {
                "q1_2025": 1440000,  # 50% de R$ 2.88M
                "q2_2025": 1717500,  # + 50% de R$ 555K
                "q4_2025": 1864500,  # + 50% de R$ 294K
                "total_anual": 1864500,
                "crescimento_anual": "25%"
            },
            "Otimista (70% conversão)": {
                "q1_2025": 2016000,  # 70% de R$ 2.88M
                "q2_2025": 2404500,  # + 70% de R$ 555K
                "q4_2025": 2610300,  # + 70% de R$ 294K
                "total_anual": 2610300,
                "crescimento_anual": "35%"
            }
        }

        return scenarios

    def save_enhanced_analysis(self, university_profiles, strategies, risks, roadmap, financial_projections):
        """Salva análise expandida"""
        print("\n💾 SALVANDO ANÁLISE EXPANDIDA")
        print("=" * 30)

        # Salvar perfis de universidades
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/university_profiles.json', 'w', encoding='utf-8') as f:
            json.dump(university_profiles, f, ensure_ascii=False, indent=2)

        # Salvar estratégias comerciais
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/commercial_strategies.json', 'w', encoding='utf-8') as f:
            json.dump(strategies, f, ensure_ascii=False, indent=2)

        # Salvar plano de riscos
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/risk_mitigation.json', 'w', encoding='utf-8') as f:
            json.dump(risks, f, ensure_ascii=False, indent=2)

        # Salvar roadmap
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/implementation_roadmap.json', 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, ensure_ascii=False, indent=2)

        # Salvar projeções financeiras
        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/financial_projections.json', 'w', encoding='utf-8') as f:
            json.dump(financial_projections, f, ensure_ascii=False, indent=2)

        # Criar relatório executivo expandido
        self.create_executive_summary(university_profiles, strategies, financial_projections)

        print("✅ Análise expandida salva com sucesso")

    def create_executive_summary(self, university_profiles, strategies, financial_projections):
        """Cria resumo executivo expandido"""

        realista = financial_projections["Realista (50% conversão)"]

        summary = f"""
# MAPA DE SUBSTITUTOS - ANÁLISE EXPANDIDA
## Estratégia Comercial & Projeções Financeiras

### 🎯 OPORTUNIDADE DE MERCADO

**MERCADO IDENTIFICADO:**
- 3 órgãos prioritários com R$ 12,4M em EAD genérico
- Potencial de substituição: R$ 3,7M (30% estimado)
- Cenário realista: R$ {realista['total_anual']:,.0f}/ano

### 💼 ESTRATÉGIA COMERCIAL PRIORITÁRIA

**MINISTÉRIO DA EDUCAÇÃO (Prioridade #1):**
- Score: 4.2/5.0 | Timeline: Q1 2025
- Investimento atual EAD: R$ 9,6M
- Potencial idiomas: R$ 2,88M
- Abordagem: Apresentação executiva sobre modernização

**FNDE (Prioridade #2):**
- Score: 3.4/5.0 | Timeline: Q2 2025
- Investimento atual EAD: R$ 1,85M
- Potencial idiomas: R$ 555K
- Abordagem: ROI e casos de sucesso

**CAPES (Prioridade #3):**
- Score: 1.6/5.0 | Timeline: Q4 2025
- Investimento atual EAD: R$ 980K
- Potencial idiomas: R$ 294K
- Abordagem: Inglês acadêmico e publicações

### 📊 PROJEÇÕES FINANCEIRAS (Cenário Realista)

| Trimestre | Receita Acumulada | Conversão |
|-----------|-------------------|-----------|
| Q1 2025   | R$ {realista['q1_2025']:,.0f} | MEC (50%) |
| Q2 2025   | R$ {realista['q2_2025']:,.0f} | +FNDE (50%) |
| Q4 2025   | R$ {realista['q4_2025']:,.0f} | +CAPES (50%) |

**Crescimento anual projetado:** {realista['crescimento_anual']}

### 🎓 EXPANSÃO PARA UNIVERSIDADES FEDERAIS

**Perfis de Alto Potencial:**
1. **Universidades com Programas Internacionais**
   - Potencial: R$ 500K - R$ 2M/ano
   - Foco: Intercâmbio e publicações internacionais

2. **Universidades Técnicas/Tecnológicas**
   - Potencial: R$ 300K - R$ 1M/ano
   - Foco: Inglês técnico e certificações

3. **Universidades de Medicina/Saúde**
   - Potencial: R$ 400K - R$ 1,5M/ano
   - Foco: Literatura médica internacional

### ⚡ AÇÕES IMEDIATAS (Próximos 30 dias)

1. **Validação de dados** - Confirmar investimentos atuais
2. **Desenvolvimento de materiais** - Propostas customizadas
3. **Agendamento estratégico** - Reuniões com tomadores de decisão
4. **Preparação de piloto** - Estrutura para validação rápida

### 🏆 DIFERENCIAIS COMPETITIVOS

- **Especialização** vs generalização do EAD atual
- **ROI mensurável** em competências linguísticas
- **Metodologia comprovada** para setor público
- **Certificações internacionais** reconhecidas

### ⚠️ RISCOS E MITIGAÇÕES

**Principais Riscos:**
- Resistência à mudança (Mitigação: Casos de sucesso)
- Restrições orçamentárias (Mitigação: ROI claro)
- Concorrência EAD (Mitigação: Diferenciação de valor)

### 📈 POTENCIAL DE EXPANSÃO 2026

Com base nos sucessos de 2025:
- **Universidades Federais:** +20-30 instituições
- **Órgãos Estaduais:** Replicação do modelo
- **Mercado Potencial Total:** R$ 15-25M

---
*Análise estratégica - {datetime.now().strftime('%Y-%m-%d')}*
"""

        with open('/home/danielfugisawa/pesquisa_prospect_gov/analysis/executive_summary_expanded.md', 'w', encoding='utf-8') as f:
            f.write(summary)

def main():
    """Função principal da análise expandida"""
    print("🚀 ANÁLISE EXPANDIDA DE SUBSTITUTOS")
    print("=" * 40)

    analyzer = EnhancedSubstituteAnalyzer()

    # Carregar dados
    if not analyzer.load_substitute_data():
        return

    # Executar análises
    university_profiles = analyzer.analyze_university_potential()
    strategies = analyzer.create_commercial_strategies()
    risks = analyzer.create_risk_mitigation_plan()
    roadmap = analyzer.generate_implementation_roadmap()
    financial_projections = analyzer.calculate_financial_projections()

    # Salvar resultados
    analyzer.save_enhanced_analysis(
        university_profiles,
        strategies,
        risks,
        roadmap,
        financial_projections
    )

    print("\n✅ ANÁLISE EXPANDIDA CONCLUÍDA!")
    print("📁 Arquivos gerados:")
    print("   - university_profiles.json")
    print("   - commercial_strategies.json")
    print("   - risk_mitigation.json")
    print("   - implementation_roadmap.json")
    print("   - financial_projections.json")
    print("   - executive_summary_expanded.md")

if __name__ == "__main__":
    main()