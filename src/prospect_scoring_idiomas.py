#!/usr/bin/env python3
"""
GERAÇÃO TOP 20 PROSPECTS POR PROPENSÃO À COMPRA - IDIOMAS
Sistema de scoring quantitativo para identificar os melhores prospects governamentais.

Critérios de Scoring (peso 1-5):
1. Frequência de compras digitais (25%) - histórico de modernização
2. Valor médio dos contratos (20%) - capacidade orçamentária
3. Presença de PCA (20%) - planejamento estruturado
4. Aderência a idiomas (35%) - necessidade missional
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class ProspectScoringIdiomas:
    def __init__(self):
        self.orgaos_historico = {}
        self.scoring_weights = {
            'freq_compras_digitais': 0.25,
            'valor_medio_contratos': 0.20,
            'presenca_pca': 0.20,
            'aderencia_idiomas': 0.35
        }

        # Estrutura governamental com propensão a idiomas
        self.estrutura_gov = {
            # Órgãos com histórico confirmado
            'Ministério das Relações Exteriores': {
                'uasg': 210001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'critica'
            },
            'Ministério da Defesa': {
                'uasg': 160001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'Ministério da Justiça e Segurança Pública': {
                'uasg': 130001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'Ministério do Desenvolvimento, Indústria e Comércio Exterior': {
                'uasg': 120001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'media',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'ENAP - Escola Nacional de Administração Pública': {
                'uasg': 389001,
                'missao_internacional': False,
                'capacidade_orcamentaria': 'media',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            # Órgãos prioritários identificados
            'Ministério da Educação': {
                'uasg': 153001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'muito_alta',
                'modernizacao_digital': 'muito_alta',
                'necessidade_idiomas': 'alta'
            },
            'Tribunal de Contas da União': {
                'uasg': 40001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'media'
            },
            'Banco Central do Brasil': {
                'uasg': 245001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'muito_alta',
                'modernizacao_digital': 'muito_alta',
                'necessidade_idiomas': 'critica'
            },
            # Órgãos adicionais com alta propensão
            'Ministério das Comunicações': {
                'uasg': 250001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'muito_alta',
                'necessidade_idiomas': 'media'
            },
            'Ministério da Ciência, Tecnologia e Inovações': {
                'uasg': 240001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'muito_alta',
                'necessidade_idiomas': 'alta'
            },
            'CAPES - Coordenação de Aperfeiçoamento de Pessoal de Nível Superior': {
                'uasg': 154001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'critica'
            },
            'CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico': {
                'uasg': 240002,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'Ministério da Agricultura, Pecuária e Abastecimento': {
                'uasg': 220001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'media',
                'necessidade_idiomas': 'media'
            },
            'Ministério do Turismo': {
                'uasg': 330001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'media',
                'modernizacao_digital': 'media',
                'necessidade_idiomas': 'alta'
            },
            'Embrapa - Empresa Brasileira de Pesquisa Agropecuária': {
                'uasg': 220002,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'IBAMA - Instituto Brasileiro do Meio Ambiente': {
                'uasg': 440001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'media',
                'modernizacao_digital': 'media',
                'necessidade_idiomas': 'media'
            },
            'Polícia Federal': {
                'uasg': 130002,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'alta'
            },
            'Receita Federal do Brasil': {
                'uasg': 170001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'muito_alta',
                'necessidade_idiomas': 'media'
            },
            'ANVISA - Agência Nacional de Vigilância Sanitária': {
                'uasg': 260001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'media'
            },
            'Supremo Tribunal Federal': {
                'uasg': 10001,
                'missao_internacional': True,
                'capacidade_orcamentaria': 'alta',
                'modernizacao_digital': 'alta',
                'necessidade_idiomas': 'media'
            }
        }

    def load_historical_data(self, file_path: str) -> pd.DataFrame:
        """Carrega dados históricos de contratos"""
        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            print(f"Arquivo {file_path} não encontrado")
            return pd.DataFrame()

    def analyze_historical_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões dos contratos históricos"""
        if df.empty:
            return {}

        # Filtrar apenas contratos de idiomas
        df_idiomas = df[df['categoria'] == 'Idiomas'].copy()

        if df_idiomas.empty:
            return {}

        # Converter valores para numérico
        df_idiomas['valor_numerico'] = df_idiomas['valor'].str.replace(
            r'[R$\.\s]', '', regex=True
        ).str.replace(',', '.').astype(float)

        patterns = {}
        for orgao in df_idiomas['orgao'].unique():
            orgao_data = df_idiomas[df_idiomas['orgao'] == orgao]
            patterns[orgao] = {
                'total_contratos': len(orgao_data),
                'valor_total': orgao_data['valor_numerico'].sum(),
                'valor_medio': orgao_data['valor_numerico'].mean(),
                'ultimo_contrato': orgao_data['data'].max(),
                'modalidades': orgao_data['modalidade'].unique().tolist()
            }

        return patterns

    def calculate_frequency_score(self, orgao: str, patterns: Dict) -> float:
        """Score de frequência de compras digitais (1-5)"""
        if orgao not in patterns:
            # Baseado no perfil do órgão
            profile = self.estrutura_gov.get(orgao, {})
            modernizacao = profile.get('modernizacao_digital', 'baixa')

            score_map = {
                'muito_alta': 4.5,
                'alta': 3.5,
                'media': 2.5,
                'baixa': 1.5
            }
            return score_map.get(modernizacao, 2.0)

        # Com histórico real
        total_contratos = patterns[orgao]['total_contratos']
        if total_contratos >= 3:
            return 5.0
        elif total_contratos == 2:
            return 4.0
        elif total_contratos == 1:
            return 3.0
        else:
            return 2.0

    def calculate_budget_score(self, orgao: str, patterns: Dict) -> float:
        """Score de capacidade orçamentária (1-5)"""
        if orgao not in patterns:
            profile = self.estrutura_gov.get(orgao, {})
            capacidade = profile.get('capacidade_orcamentaria', 'baixa')

            score_map = {
                'muito_alta': 5.0,
                'alta': 4.0,
                'media': 3.0,
                'baixa': 2.0
            }
            return score_map.get(capacidade, 2.0)

        # Com histórico real
        valor_medio = patterns[orgao]['valor_medio']
        if valor_medio >= 2000000:  # R$ 2M+
            return 5.0
        elif valor_medio >= 1000000:  # R$ 1M+
            return 4.0
        elif valor_medio >= 500000:  # R$ 500K+
            return 3.0
        else:
            return 2.0

    def calculate_pca_score(self, orgao: str) -> float:
        """Score de presença de PCA (1-5)"""
        # Órgãos com maior probabilidade de ter PCA estruturado
        orgaos_pca_alta = [
            'Ministério da Educação',
            'Ministério das Relações Exteriores',
            'Ministério da Defesa',
            'Banco Central do Brasil',
            'Receita Federal do Brasil',
            'CAPES - Coordenação de Aperfeiçoamento de Pessoal de Nível Superior'
        ]

        orgaos_pca_media = [
            'Ministério da Justiça e Segurança Pública',
            'Ministério da Ciência, Tecnologia e Inovações',
            'ENAP - Escola Nacional de Administração Pública',
            'Tribunal de Contas da União'
        ]

        if orgao in orgaos_pca_alta:
            return 5.0
        elif orgao in orgaos_pca_media:
            return 3.5
        else:
            return 2.5

    def calculate_language_adherence_score(self, orgao: str) -> float:
        """Score de aderência a idiomas (1-5)"""
        profile = self.estrutura_gov.get(orgao, {})
        necessidade = profile.get('necessidade_idiomas', 'baixa')
        missao_internacional = profile.get('missao_internacional', False)

        score_map = {
            'critica': 5.0,
            'alta': 4.0,
            'media': 3.0,
            'baixa': 2.0
        }

        base_score = score_map.get(necessidade, 2.0)

        # Bonus para missão internacional
        if missao_internacional:
            base_score = min(5.0, base_score + 0.5)

        return base_score

    def calculate_final_score(self, orgao: str, patterns: Dict) -> float:
        """Calcula score final ponderado (0-100)"""
        freq_score = self.calculate_frequency_score(orgao, patterns)
        budget_score = self.calculate_budget_score(orgao, patterns)
        pca_score = self.calculate_pca_score(orgao)
        lang_score = self.calculate_language_adherence_score(orgao)

        weighted_score = (
            freq_score * self.scoring_weights['freq_compras_digitais'] +
            budget_score * self.scoring_weights['valor_medio_contratos'] +
            pca_score * self.scoring_weights['presenca_pca'] +
            lang_score * self.scoring_weights['aderencia_idiomas']
        )

        # Normalizar para 0-100
        return (weighted_score / 5.0) * 100

    def estimate_contract_value(self, orgao: str, patterns: Dict) -> float:
        """Estima valor potencial do contrato"""
        if orgao in patterns:
            # Baseado no histórico real
            base_value = patterns[orgao]['valor_medio']
            # Crescimento esperado de 15-30%
            return base_value * 1.25

        # Estimativa baseada no perfil
        profile = self.estrutura_gov.get(orgao, {})
        capacidade = profile.get('capacidade_orcamentaria', 'baixa')

        estimates = {
            'muito_alta': 2500000,  # R$ 2.5M
            'alta': 1500000,        # R$ 1.5M
            'media': 800000,        # R$ 800K
            'baixa': 400000         # R$ 400K
        }

        return estimates.get(capacidade, 500000)

    def calculate_conversion_probability(self, score: float, orgao: str, patterns: Dict) -> float:
        """Calcula probabilidade de conversão (%)"""
        base_probability = (score / 100) * 70  # Base: até 70%

        # Bonus por histórico
        if orgao in patterns:
            base_probability += 15

        # Bonus por necessidade crítica
        profile = self.estrutura_gov.get(orgao, {})
        if profile.get('necessidade_idiomas') == 'critica':
            base_probability += 10

        return min(85, base_probability)  # Máximo 85%

    def determine_timeline(self, orgao: str, patterns: Dict) -> str:
        """Determina timeline de oportunidade"""
        if orgao in patterns:
            # Órgãos com histórico - ciclo mais rápido
            return "Q1-Q2 2025"

        profile = self.estrutura_gov.get(orgao, {})
        modernizacao = profile.get('modernizacao_digital', 'baixa')

        if modernizacao in ['muito_alta', 'alta']:
            return "Q2-Q3 2025"
        else:
            return "Q3-Q4 2025"

    def generate_justification(self, orgao: str, score: float, patterns: Dict) -> str:
        """Gera justificativa para o scoring"""
        profile = self.estrutura_gov.get(orgao, {})

        factors = []

        if orgao in patterns:
            factors.append(f"histórico de {patterns[orgao]['total_contratos']} contrato(s)")

        necessidade = profile.get('necessidade_idiomas', 'baixa')
        if necessidade in ['critica', 'alta']:
            factors.append(f"necessidade {necessidade} de idiomas")

        if profile.get('missao_internacional'):
            factors.append("atuação internacional")

        capacidade = profile.get('capacidade_orcamentaria', 'baixa')
        if capacidade in ['muito_alta', 'alta']:
            factors.append(f"capacidade orçamentária {capacidade}")

        return f"Score {score:.1f}: {', '.join(factors[:3])}"

    def generate_top20_prospects(self, file_path: str) -> List[Dict]:
        """Gera ranking Top 20 prospects"""
        df = self.load_historical_data(file_path)
        patterns = self.analyze_historical_patterns(df)

        prospects = []

        for orgao in self.estrutura_gov.keys():
            score = self.calculate_final_score(orgao, patterns)
            estimated_value = self.estimate_contract_value(orgao, patterns)
            conversion_prob = self.calculate_conversion_probability(score, orgao, patterns)
            timeline = self.determine_timeline(orgao, patterns)
            justification = self.generate_justification(orgao, score, patterns)

            prospects.append({
                'rank': 0,  # Será preenchido após ordenação
                'orgao': orgao,
                'score_propensao': score,
                'valor_estimado': estimated_value,
                'probabilidade_conversao': conversion_prob,
                'timeline_oportunidade': timeline,
                'justificativa': justification,
                'tem_historico': orgao in patterns
            })

        # Ordenar por score decrescente e atribuir ranks
        prospects.sort(key=lambda x: x['score_propensao'], reverse=True)
        for i, prospect in enumerate(prospects[:20], 1):
            prospect['rank'] = i

        return prospects[:20]

def main():
    """Função principal"""
    scoring = ProspectScoringIdiomas()

    # Carregar dados
    file_path = "/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_idiomas.csv"

    # Gerar ranking
    top20 = scoring.generate_top20_prospects(file_path)

    # Exibir resultados
    print("=" * 80)
    print("TOP 20 PROSPECTS POR PROPENSÃO À COMPRA - IDIOMAS")
    print("=" * 80)
    print()

    for prospect in top20:
        print(f"#{prospect['rank']:2d} | {prospect['orgao']}")
        print(f"     Score: {prospect['score_propensao']:.1f}/100")
        print(f"     Valor Estimado: R$ {prospect['valor_estimado']:,.0f}")
        print(f"     Prob. Conversão: {prospect['probabilidade_conversao']:.1f}%")
        print(f"     Timeline: {prospect['timeline_oportunidade']}")
        print(f"     Justificativa: {prospect['justificativa']}")
        print(f"     Histórico: {'✓' if prospect['tem_historico'] else '✗'}")
        print()

    # Estatísticas gerais
    total_valor = sum(p['valor_estimado'] for p in top20)
    avg_conversion = sum(p['probabilidade_conversao'] for p in top20) / len(top20)
    historical_count = sum(1 for p in top20 if p['tem_historico'])

    print("=" * 80)
    print("ESTATÍSTICAS GERAIS")
    print("=" * 80)
    print(f"Valor Total Estimado: R$ {total_valor:,.0f}")
    print(f"Probabilidade Média de Conversão: {avg_conversion:.1f}%")
    print(f"Órgãos com Histórico: {historical_count}/20")
    print(f"Pipeline Estimado: R$ {total_valor * (avg_conversion/100):,.0f}")

if __name__ == "__main__":
    main()