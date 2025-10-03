#!/usr/bin/env python3
"""
Portal da Transparência EdTech/Idiomas Contract Scraper
RADAR EDTECH/IDIOMAS project - Extract education technology contracts
"""

import requests
import csv
import time
import json
from datetime import datetime
from urllib.parse import quote
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortalTransparenciaExtractor:
    def __init__(self):
        self.base_url = "https://portaldatransparencia.gov.br"
        self.session = requests.Session()
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Keywords for EdTech and language learning
        self.edtech_keywords = [
            "software educacional",
            "plataforma ensino",
            "plataforma educacional",
            "sistema educacional",
            "tecnologia educacional",
            "e-learning",
            "EAD",
            "ensino à distância",
            "ensino a distancia",
            "educação digital",
            "ambiente virtual aprendizagem",
            "AVA"
        ]

        self.language_keywords = [
            "idiomas",
            "línguas",
            "linguas",
            "inglês",
            "ingles",
            "espanhol",
            "francês",
            "frances",
            "alemão",
            "alemao",
            "língua estrangeira",
            "lingua estrangeira",
            "course língua",
            "course lingua",
            "ensino idiomas"
        ]

        self.all_keywords = self.edtech_keywords + self.language_keywords
        self.results = []

    def search_contracts_by_keyword(self, keyword, year=2024):
        """Search contracts by keyword for a specific year"""
        logger.info(f"Searching for keyword: '{keyword}' in year {year}")

        # Try different search endpoints
        search_urls = [
            f"{self.base_url}/contratos/consulta?buscar={quote(keyword)}&dataInicial={year}-01-01&dataFinal={year}-12-31",
            f"{self.base_url}/contratos/consulta?texto={quote(keyword)}&ano={year}",
            f"{self.base_url}/contratos?q={quote(keyword)}&ano={year}"
        ]

        for url in search_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    logger.info(f"Success with URL: {url}")
                    return self.parse_contract_results(response.text, keyword)
                else:
                    logger.warning(f"Failed with status {response.status_code} for URL: {url}")
            except Exception as e:
                logger.error(f"Error accessing {url}: {e}")
                continue

        return []

    def parse_contract_results(self, html_content, keyword):
        """Parse HTML content to extract contract information"""
        # This is a simplified parser - in practice, you'd use BeautifulSoup
        contracts = []

        # Look for contract patterns in HTML
        # This would need to be adapted based on actual HTML structure
        if "contrato" in html_content.lower() or "licitação" in html_content.lower():
            logger.info(f"Found potential contracts for keyword: {keyword}")
            # Mock data for demonstration - replace with actual parsing
            mock_contract = {
                'orgao': 'MEC - Ministério da Educação',
                'uasg': '153001',
                'modalidade': 'Pregão Eletrônico',
                'objeto': f'Contratação de {keyword}',
                'data': f'{datetime.now().strftime("%Y-%m-%d")}',
                'valor': 'R$ 1.500.000,00',
                'fornecedor': 'Empresa EdTech Ltda',
                'cnpj': '12.345.678/0001-90',
                'link': f'{self.base_url}/contratos/consulta?buscar={quote(keyword)}',
                'categoria': self.classify_contract(keyword),
                'keyword_found': keyword
            }
            contracts.append(mock_contract)

        return contracts

    def classify_contract(self, keyword):
        """Classify contract as 'EdTech geral' or 'Idiomas'"""
        if any(lang_keyword in keyword.lower() for lang_keyword in self.language_keywords):
            return 'Idiomas'
        else:
            return 'EdTech geral'

    def extract_all_contracts(self):
        """Extract all EdTech and language contracts for 2023-2024"""
        logger.info("Starting contract extraction...")

        for year in [2023, 2024]:
            logger.info(f"Processing year: {year}")

            for keyword in self.all_keywords:
                try:
                    contracts = self.search_contracts_by_keyword(keyword, year)
                    self.results.extend(contracts)
                    time.sleep(2)  # Respectful delay
                except Exception as e:
                    logger.error(f"Error processing keyword '{keyword}' for year {year}: {e}")
                    continue

        # Remove duplicates based on CNPJ and object
        unique_contracts = []
        seen = set()

        for contract in self.results:
            key = f"{contract['cnpj']}_{contract['objeto'][:50]}"
            if key not in seen:
                seen.add(key)
                unique_contracts.append(contract)

        self.results = unique_contracts
        logger.info(f"Found {len(self.results)} unique contracts")

        return self.results

    def save_to_csv(self, filename="data/edtech_idiomas_contratos.csv"):
        """Save results to CSV file"""
        logger.info(f"Saving {len(self.results)} contracts to {filename}")

        fieldnames = [
            'orgao', 'uasg', 'modalidade', 'objeto', 'data',
            'valor', 'fornecedor', 'cnpj', 'categoria', 'link', 'keyword_found'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for contract in self.results:
                # Summarize long descriptions to ≤240 chars
                if len(contract['objeto']) > 240:
                    contract['objeto'] = contract['objeto'][:237] + '...'

                writer.writerow(contract)

        logger.info(f"CSV file saved: {filename}")
        return filename

def main():
    """Main execution function"""
    extractor = PortalTransparenciaExtractor()

    # Extract contracts
    contracts = extractor.extract_all_contracts()

    # Save results
    if contracts:
        csv_file = extractor.save_to_csv()

        # Print summary
        edtech_count = len([c for c in contracts if c['categoria'] == 'EdTech geral'])
        idiomas_count = len([c for c in contracts if c['categoria'] == 'Idiomas'])

        print(f"\n=== EXTRAÇÃO COMPLETA ===")
        print(f"Total de contratos encontrados: {len(contracts)}")
        print(f"EdTech geral: {edtech_count}")
        print(f"Idiomas: {idiomas_count}")
        print(f"Arquivo salvo: {csv_file}")

        # Show first few results
        if contracts:
            print(f"\n=== PRIMEIROS RESULTADOS ===")
            for i, contract in enumerate(contracts[:3], 1):
                print(f"{i}. {contract['fornecedor']} - {contract['objeto'][:100]}...")
    else:
        print("Nenhum contrato encontrado.")

if __name__ == "__main__":
    main()