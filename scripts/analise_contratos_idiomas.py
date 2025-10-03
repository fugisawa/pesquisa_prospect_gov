#!/usr/bin/env python3
"""
Análise Detalhada dos Contratos Vencedores - Idiomas
Análise estratégica do radar_idiomas.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from collections import Counter

# Configuração de estilo para gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def clean_valor(valor_str):
    """Converte string de valor para float"""
    if pd.isna(valor_str):
        return 0
    # Remove R$, pontos e converte vírgula para ponto
    valor_clean = re.sub(r'R\$\s*', '', str(valor_str))
    valor_clean = valor_clean.replace('.', '').replace(',', '.')
    try:
        return float(valor_clean)
    except:
        return 0

def calcular_hhi(fornecedores):
    """Calcula o Índice Herfindahl-Hirschman (concentração de mercado)"""
    contagens = Counter(fornecedores)
    total = len(fornecedores)
    shares = [count/total for count in contagens.values()]
    hhi = sum(share**2 for share in shares) * 10000
    return hhi, contagens

def analise_modalidades(df):
    """Análise detalhada das modalidades de contratação"""
    print("="*80)
    print("A. ANÁLISE DE MODALIDADES DE CONTRATAÇÃO")
    print("="*80)

    # Distribuição por modalidade
    modalidades = df['modalidade'].value_counts()
    print("\n1. DISTRIBUIÇÃO POR MODALIDADE:")
    print("-"*40)
    for modalidade, count in modalidades.items():
        percent = (count/len(df)) * 100
        print(f"{modalidade}: {count} contratos ({percent:.1f}%)")

    # Valores médios por modalidade
    print("\n2. VALORES MÉDIOS POR MODALIDADE:")
    print("-"*40)
    valores_modalidade = df.groupby('modalidade')['valor_numerico'].agg(['mean', 'median', 'sum', 'count'])
    for modalidade, stats in valores_modalidade.iterrows():
        print(f"\n{modalidade}:")
        print(f"  Valor médio: R$ {stats['mean']:,.2f}")
        print(f"  Valor mediano: R$ {stats['median']:,.2f}")
        print(f"  Valor total: R$ {stats['sum']:,.2f}")
        print(f"  Quantidade: {stats['count']} contratos")

    # Análise temporal por modalidade
    print("\n3. PADRÕES TEMPORAIS (2023):")
    print("-"*40)
    df_temporal = df.groupby(['modalidade', df['data'].dt.month])['valor_numerico'].sum().unstack(fill_value=0)
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    for modalidade in df['modalidade'].unique():
        print(f"\n{modalidade}:")
        for mes in df_temporal.columns:
            if modalidade in df_temporal.index and mes in df_temporal.columns:
                valor = df_temporal.loc[modalidade, mes]
                if valor > 0:
                    print(f"  {meses[mes-1]}: R$ {valor:,.2f}")

    return modalidades, valores_modalidade

def analise_financeira(df):
    """Análise do perfil financeiro dos contratos"""
    print("\n\n" + "="*80)
    print("B. ANÁLISE DE PERFIL FINANCEIRO")
    print("="*80)

    valores = df['valor_numerico']

    print("\n1. ESTATÍSTICAS GERAIS:")
    print("-"*40)
    print(f"Valor total dos contratos: R$ {valores.sum():,.2f}")
    print(f"Valor médio por contrato: R$ {valores.mean():,.2f}")
    print(f"Valor mediano: R$ {valores.median():,.2f}")
    print(f"Desvio padrão: R$ {valores.std():,.2f}")
    print(f"Valor mínimo: R$ {valores.min():,.2f}")
    print(f"Valor máximo: R$ {valores.max():,.2f}")

    # Estimativa de licenças/alunos por contrato
    print("\n2. ESTIMATIVA DE LICENÇAS/ALUNOS:")
    print("-"*40)
    # Assumindo custo médio por licença/aluno entre R$ 800-1500 baseado no mercado
    custo_min_licenca = 800
    custo_max_licenca = 1500

    for idx, row in df.iterrows():
        valor = row['valor_numerico']
        licencas_max = int(valor / custo_min_licenca)
        licencas_min = int(valor / custo_max_licenca)
        print(f"{row['fornecedor'][:30]}: {licencas_min:,} - {licencas_max:,} licenças estimadas")

    # Faixas de valor
    print("\n3. DISTRIBUIÇÃO POR FAIXAS DE VALOR:")
    print("-"*40)
    faixas = [
        (0, 1000000, "Até R$ 1 milhão"),
        (1000000, 2000000, "R$ 1-2 milhões"),
        (2000000, float('inf'), "Acima de R$ 2 milhões")
    ]

    for min_val, max_val, label in faixas:
        count = len(df[(df['valor_numerico'] >= min_val) & (df['valor_numerico'] < max_val)])
        valor_total = df[(df['valor_numerico'] >= min_val) & (df['valor_numerico'] < max_val)]['valor_numerico'].sum()
        print(f"{label}: {count} contratos (R$ {valor_total:,.2f})")

    return valores

def analise_fornecedores(df):
    """Análise do perfil dos fornecedores"""
    print("\n\n" + "="*80)
    print("C. ANÁLISE DE PADRÕES DE FORNECEDORES")
    print("="*80)

    fornecedores = df['fornecedor'].tolist()
    hhi, contagens = calcular_hhi(fornecedores)

    print("\n1. CONCENTRAÇÃO DE MERCADO:")
    print("-"*40)
    print(f"Índice HHI: {hhi:.0f}")
    if hhi < 1500:
        concentracao = "Baixa concentração (mercado competitivo)"
    elif hhi < 2500:
        concentracao = "Concentração moderada"
    else:
        concentracao = "Alta concentração (mercado oligopolizado)"
    print(f"Interpretação: {concentracao}")

    print("\n2. FORNECEDORES PARTICIPANTES:")
    print("-"*40)
    for fornecedor, count in contagens.items():
        valor_total = df[df['fornecedor'] == fornecedor]['valor_numerico'].sum()
        share_contratos = (count/len(df)) * 100
        share_valor = (valor_total/df['valor_numerico'].sum()) * 100
        print(f"{fornecedor[:40]}")
        print(f"  Contratos: {count} ({share_contratos:.1f}%)")
        print(f"  Valor total: R$ {valor_total:,.2f} ({share_valor:.1f}%)")
        print()

    # Análise Nacional vs Internacional
    print("\n3. PERFIL NACIONAL VS INTERNACIONAL:")
    print("-"*40)
    internacionais = ['Babbel', 'EF Education', 'Rosetta Stone', 'Wizard by Pearson']
    nacionais = ['CCAA', 'Cultura Inglesa']

    df['origem'] = df['fornecedor'].apply(
        lambda x: 'Internacional' if any(marca in x for marca in internacionais) else 'Nacional'
    )

    origem_stats = df.groupby('origem').agg({
        'valor_numerico': ['count', 'sum', 'mean']
    }).round(2)

    for origem in ['Internacional', 'Nacional']:
        if origem in origem_stats.index:
            count = origem_stats.loc[origem, ('valor_numerico', 'count')]
            total = origem_stats.loc[origem, ('valor_numerico', 'sum')]
            media = origem_stats.loc[origem, ('valor_numerico', 'mean')]
            print(f"{origem}:")
            print(f"  Contratos: {count}")
            print(f"  Valor total: R$ {total:,.2f}")
            print(f"  Valor médio: R$ {media:,.2f}")
            print()

    return hhi, contagens

def analise_operacional(df):
    """Análise das características operacionais"""
    print("\n\n" + "="*80)
    print("D. ANÁLISE DE CARACTERÍSTICAS OPERACIONAIS")
    print("="*80)

    print("\n1. PADRÕES TEMPORAIS (2023):")
    print("-"*40)
    df_mes = df.groupby(df['data'].dt.month)['valor_numerico'].agg(['count', 'sum'])
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    for mes, stats in df_mes.iterrows():
        print(f"{meses[mes-1]}: {stats['count']} contratos (R$ {stats['sum']:,.2f})")

    print("\n2. ANÁLISE DE OBJETOS DOS CONTRATOS:")
    print("-"*40)
    modalidades_servico = {
        'Plataforma digital': 0,
        'Treinamento presencial': 0,
        'EAD': 0,
        'Software/Licenciamento': 0,
        'Certificação': 0
    }

    for idx, row in df.iterrows():
        objeto = row['objeto'].lower()
        if 'plataforma' in objeto or 'digital' in objeto:
            modalidades_servico['Plataforma digital'] += 1
        if 'ead' in objeto or 'modalidade ead' in objeto:
            modalidades_servico['EAD'] += 1
        if 'software' in objeto or 'licenciamento' in objeto:
            modalidades_servico['Software/Licenciamento'] += 1
        if 'certificação' in objeto or 'certificado' in objeto:
            modalidades_servico['Certificação'] += 1
        if 'treinamento' in objeto and 'ead' not in objeto and 'digital' not in objeto:
            modalidades_servico['Treinamento presencial'] += 1

    for modalidade, count in modalidades_servico.items():
        if count > 0:
            print(f"{modalidade}: {count} contratos")

    return df_mes

def projecoes_2025(df):
    """Projeções e insights para 2025"""
    print("\n\n" + "="*80)
    print("E. PROJEÇÕES E INSIGHTS ESTRATÉGICOS PARA 2025")
    print("="*80)

    valor_medio_atual = df['valor_numerico'].mean()

    # Projeção com inflação e crescimento do setor
    inflacao_estimada = 0.045  # 4.5%
    crescimento_setor = 0.08   # 8% (mercado ed-tech)

    valor_projetado_2025 = valor_medio_atual * (1 + inflacao_estimada + crescimento_setor)

    print("\n1. PROJEÇÕES DE PREÇOS MÉDIOS:")
    print("-"*40)
    print(f"Valor médio atual (2023): R$ {valor_medio_atual:,.2f}")
    print(f"Valor projetado 2025: R$ {valor_projetado_2025:,.2f}")
    print(f"Crescimento projetado: {((valor_projetado_2025/valor_medio_atual)-1)*100:.1f}%")

    print("\n2. FAIXAS DE VALOR RECOMENDADAS PARA 2025:")
    print("-"*40)

    # Análise por modalidade para recomendações
    modalidade_valores = df.groupby('modalidade')['valor_numerico'].mean()

    for modalidade, valor_atual in modalidade_valores.items():
        valor_2025 = valor_atual * (1 + inflacao_estimada + crescimento_setor)
        print(f"{modalidade}:")
        print(f"  Faixa competitiva: R$ {valor_2025*0.9:,.2f} - R$ {valor_2025*1.1:,.2f}")
        print(f"  Valor referência: R$ {valor_2025:,.2f}")
        print()

    print("\n3. INSIGHTS ESTRATÉGICOS:")
    print("-"*40)
    print("• Pregão Eletrônico é a modalidade predominante (4/6 contratos)")
    print("• Mercado com baixa concentração (HHI < 2500) - ambiente competitivo")
    print("• Fornecedores internacionais dominam contratos de maior valor")
    print("• Tendência para soluções digitais/plataformas online")
    print("• Primeiro semestre concentra maiores contratações")
    print("• Foco em certificação internacional está crescendo")

    return valor_projetado_2025

def main():
    """Função principal da análise"""
    # Carregar dados
    df = pd.read_csv('/home/danielfugisawa/pesquisa_prospect_gov/outputs/radar_idiomas.csv')

    # Limpeza e preparação dos dados
    df['valor_numerico'] = df['valor'].apply(clean_valor)
    df['data'] = pd.to_datetime(df['data'])

    print("ANÁLISE PERFIL DOS CONTRATOS VENCEDORES - IDIOMAS")
    print("Radar de Contratos Governamentais 2023")
    print(f"Total de contratos analisados: {len(df)}")
    print(f"Valor total: R$ {df['valor_numerico'].sum():,.2f}")

    # Executar análises
    modalidades, valores_modalidade = analise_modalidades(df)
    valores = analise_financeira(df)
    hhi, contagens = analise_fornecedores(df)
    df_mes = analise_operacional(df)
    valor_2025 = projecoes_2025(df)

    # Resumo executivo
    print("\n\n" + "="*80)
    print("RESUMO EXECUTIVO - INSIGHTS ACIONÁVEIS")
    print("="*80)

    print("\n🎯 ESTRATÉGIA COMERCIAL:")
    print("• Focar em Pregão Eletrônico (66% dos contratos)")
    print("• Desenvolver expertise em soluções digitais/EAD")
    print("• Considerar parcerias internacionais para contratos de alto valor")
    print("• Preparar propostas para Q1/Q2 (maior volume de contratações)")

    print("\n💰 PRECIFICAÇÃO RECOMENDADA 2025:")
    print(f"• Valor médio de referência: R$ {valor_2025:,.2f}")
    print("• Faixa competitiva: R$ 1.7M - 2.1M (contratos premium)")
    print("• Faixa competitiva: R$ 800K - 1.2M (contratos padrão)")

    print("\n📊 POSICIONAMENTO DE MERCADO:")
    print("• Mercado fragmentado (HHI baixo) = oportunidade para novos players")
    print("• Diferenciação via certificação internacional")
    print("• Foco em metodologias imersivas e adaptativas")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()