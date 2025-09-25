#!/usr/bin/env python3
"""
Test du web scraper avec Selenium corrigé.
"""

import sys
import os
sys.path.append('/Users/jeobrankombou/Dev/Perso/Pro/DGI/Model/src')

from web_scraper import WebScraper
import logging

logging.basicConfig(level=logging.INFO)

def test_scraper():
    print("🧪 Test du WebScraper")
    
    # Test sans Selenium d'abord
    print("\n1. Test sans Selenium (BeautifulSoup uniquement)")
    scraper = WebScraper(use_selenium=False)
    
    test_url = "https://httpbin.org/html"  # Site de test simple
    
    try:
        result = scraper.scrape_url(test_url)
        if result:
            print(f"✅ Scraping réussi: {len(result.content)} caractères")
            print(f"   Titre: {result.title[:50]}...")
        else:
            print("❌ Échec du scraping")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test avec Selenium
    print("\n2. Test avec Selenium activé")
    scraper_selenium = WebScraper(use_selenium=True)
    
    try:
        result = scraper_selenium.scrape_url(test_url)
        if result:
            print(f"✅ Scraping Selenium réussi: {len(result.content)} caractères")
            print(f"   Titre: {result.title[:50]}...")
        else:
            print("❌ Échec du scraping Selenium")
    except Exception as e:
        print(f"❌ Erreur Selenium: {e}")
    
    # Nettoyage
    scraper_selenium.cleanup()
    
    print("\n🎉 Test du scraper terminé !")

if __name__ == "__main__":
    test_scraper()
