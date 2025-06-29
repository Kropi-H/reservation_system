#!/usr/bin/env python3
"""
Test script pro database setup funkcionalitu
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.databaze import get_database_path, database_exists, set_database_path
from config import get_database_path_from_config, save_database_path_to_config

def test_database_functions():
    print("=== Test databázových funkcí ===")
    
    # Test 1: Zkontroluj výchozí cestu
    print(f"1. Výchozí cesta k databázi: {get_database_path()}")
    
    # Test 2: Zkontroluj, zda databáze existuje
    print(f"2. Databáze existuje: {database_exists()}")
    
    # Test 3: Zkontroluj konfiguraci
    config_path = get_database_path_from_config()
    print(f"3. Cesta z konfigurace: '{config_path}'")
    
    # Test 4: Simuluj nastavení nové cesty
    test_path = "/tmp/test_veterina.db"
    set_database_path(test_path)
    print(f"4. Po nastavení nové cesty: {get_database_path()}")
    print(f"   Databáze existuje: {database_exists()}")
    
    # Test 5: Zkontroluj, zda se cesta uložila do konfigurace
    saved_path = get_database_path_from_config()
    print(f"5. Uložená cesta v konfiguraci: {saved_path}")
    
    print("=== Test dokončen ===")

if __name__ == "__main__":
    test_database_functions()
