#!/usr/bin/env python3
"""
Data Deduplication and Normalization Script for RADAR EDTECH/IDIOMAS
Processes and deduplicates collected EdTech and language learning contracts
"""

import pandas as pd
import re
from datetime import datetime
import os
import sys

def normalize_cnpj(cnpj):
    """Normalize CNPJ to XX.XXX.XXX/XXXX-XX format"""
    if pd.isna(cnpj) or cnpj == "CNPJ não informado":
        return cnpj

    # Remove all non-numeric characters
    clean_cnpj = re.sub(r'[^\d]', '', str(cnpj))

    # Check if we have 14 digits
    if len(clean_cnpj) == 14:
        # Format as XX.XXX.XXX/XXXX-XX
        formatted = f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:14]}"
        return formatted
    else:
        return cnpj  # Return original if not 14 digits

def normalize_date(date_str):
    """Normalize date to YYYY-MM-DD format"""
    if pd.isna(date_str):
        return date_str

    try:
        # Try parsing as YYYY-MM-DD first
        parsed_date = pd.to_datetime(date_str, format='%Y-%m-%d')
        return parsed_date.strftime('%Y-%m-%d')
    except:
        try:
            # Try other common formats
            parsed_date = pd.to_datetime(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            return date_str  # Return original if parsing fails

def normalize_currency(value_str):
    """Normalize currency values to consistent format"""
    if pd.isna(value_str) or value_str == "Valor não informado":
        return value_str

    # Keep the R$ prefix but ensure consistent formatting
    if isinstance(value_str, str):
        # Remove extra spaces and normalize
        normalized = re.sub(r'\s+', ' ', value_str.strip())
        # Ensure R$ format
        if not normalized.startswith('R$'):
            normalized = f"R$ {normalized}"
        return normalized

    return value_str

def trim_description(description, max_length=240):
    """Trim description to max_length characters"""
    if pd.isna(description):
        return description

    description = str(description).strip()
    if len(description) <= max_length:
        return description

    # Trim and add ellipsis
    return description[:max_length-3] + "..."

def is_potential_substitute(row):
    """Identify potential substitutes (generic e-learning with language potential)"""
    if pd.isna(row['objeto']) or pd.isna(row['categoria']):
        return False

    objeto_lower = str(row['objeto']).lower()
    categoria = str(row['categoria']).lower()

    # Look for generic e-learning platforms that could include language learning
    generic_elearning_keywords = [
        'plataforma de ensino',
        'plataforma educacional',
        'software educacional',
        'ensino adaptativo',
        'aprendizagem personalizada',
        'conteúdo educacional digital',
        'sistema integrado',
        'gestão educacional'
    ]

    language_potential_keywords = [
        'multilíngue',
        'internacional',
        'capacitação',
        'treinamento',
        'adaptativo',
        'personalizado'
    ]

    # Check if it's EdTech geral with potential for language learning
    if categoria == 'edtech geral':
        has_generic = any(keyword in objeto_lower for keyword in generic_elearning_keywords)
        has_potential = any(keyword in objeto_lower for keyword in language_potential_keywords)
        return has_generic and has_potential

    return False

def deduplicate_data(df):
    """Deduplicate by CNPJ + objeto + data combination"""
    # Create deduplication key
    df['dedup_key'] = df['cnpj'].astype(str) + '|' + df['objeto'].astype(str) + '|' + df['data'].astype(str)

    # Keep first occurrence of each unique combination
    before_count = len(df)
    df_deduped = df.drop_duplicates(subset=['dedup_key'], keep='first')
    after_count = len(df_deduped)

    print(f"Deduplication: {before_count} records → {after_count} records ({before_count - after_count} duplicates removed)")

    # Remove the temporary dedup key
    df_deduped = df_deduped.drop('dedup_key', axis=1)

    return df_deduped

def process_contracts_data(input_file, output_dir):
    """Main processing function"""
    print(f"Reading data from: {input_file}")

    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} records")
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Remove rows with incomplete/invalid data
    print("Filtering out incomplete records...")
    initial_count = len(df)

    # Filter out rows with N/A status or missing critical data
    df_clean = df[
        (df['status'] != 'N/A') &
        (df['cnpj'] != 'CNPJ não informado') &
        (df['fornecedor'] != 'Fornecedor não identificado') &
        (df['valor'] != 'Valor não informado')
    ].copy()

    print(f"Removed {initial_count - len(df_clean)} incomplete records")

    # Normalize data fields
    print("Normalizing data fields...")

    # Trim whitespace from all string columns
    string_columns = df_clean.select_dtypes(include=['object']).columns
    for col in string_columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()

    # Normalize specific fields
    df_clean['cnpj'] = df_clean['cnpj'].apply(normalize_cnpj)
    df_clean['data'] = df_clean['data'].apply(normalize_date)
    df_clean['valor'] = df_clean['valor'].apply(normalize_currency)
    df_clean['objeto'] = df_clean['objeto'].apply(lambda x: trim_description(x, 240))

    # Add potential substitute marker
    df_clean['potential_substitute'] = df_clean.apply(is_potential_substitute, axis=1)

    # Deduplicate data
    print("Deduplicating records...")
    df_deduped = deduplicate_data(df_clean)

    # Split into EdTech and Idiomas
    print("Splitting into categories...")

    edtech_df = df_deduped[df_deduped['categoria'] == 'EdTech geral'].copy()
    idiomas_df = df_deduped[df_deduped['categoria'] == 'Idiomas'].copy()

    print(f"EdTech geral: {len(edtech_df)} contracts")
    print(f"Idiomas: {len(idiomas_df)} contracts")

    # Save to separate files
    edtech_output = os.path.join(output_dir, 'radar_edtech.csv')
    idiomas_output = os.path.join(output_dir, 'radar_idiomas.csv')

    # Sort by date and value for better organization
    edtech_df_sorted = edtech_df.sort_values(['data', 'valor'], ascending=[False, False])
    idiomas_df_sorted = idiomas_df.sort_values(['data', 'valor'], ascending=[False, False])

    # Save files
    edtech_df_sorted.to_csv(edtech_output, index=False)
    idiomas_df_sorted.to_csv(idiomas_output, index=False)

    print(f"\nFiles saved:")
    print(f"- EdTech: {edtech_output}")
    print(f"- Idiomas: {idiomas_output}")

    # Generate summary statistics
    print(f"\n=== PROCESSING SUMMARY ===")
    print(f"Total valid contracts processed: {len(df_deduped)}")
    print(f"EdTech geral contracts: {len(edtech_df)}")
    print(f"Idiomas contracts: {len(idiomas_df)}")

    potential_subs = edtech_df[edtech_df['potential_substitute'] == True]
    print(f"Potential substitutes identified: {len(potential_subs)}")

    if len(potential_subs) > 0:
        print("Potential substitute contracts:")
        for _, row in potential_subs.iterrows():
            print(f"  - {row['fornecedor']}: {row['objeto'][:80]}...")

    # Verify all records have source links
    missing_links = df_deduped[df_deduped['link'].isna() | (df_deduped['link'] == '')].shape[0]
    print(f"Records missing source links: {missing_links}")

    return True

if __name__ == "__main__":
    input_file = "/home/danielfugisawa/pesquisa_prospect_gov/results/contratos_edtech_idiomas_FINAL_RADAR.csv"
    output_dir = "/home/danielfugisawa/pesquisa_prospect_gov/outputs"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    success = process_contracts_data(input_file, output_dir)

    if success:
        print("\n✅ Data processing completed successfully!")
    else:
        print("\n❌ Data processing failed!")
        sys.exit(1)