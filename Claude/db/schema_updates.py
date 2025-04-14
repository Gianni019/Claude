#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aktualisierung des Datenbankschemas für die Autowerkstatt-Anwendung
"""

import sqlite3
from utils.config import init_default_config

def update_database_schema(conn):
    def update_database_schema(conn):
        """Aktualisiert das Datenbankschema auf die aktuelle Version"""
        cursor = conn.cursor()
        
        # Prüfen, ob Tabellen existieren
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fahrzeuge'")
        fahrzeuge_table = cursor.fetchone()
        
        # Fahrzeuge-Tabelle erstellen, falls nicht vorhanden
        if not fahrzeuge_table:
            cursor.execute('''
            CREATE TABLE fahrzeuge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kunden_id INTEGER NOT NULL,
                fahrzeug_typ TEXT,
                kennzeichen TEXT,
                fahrgestellnummer TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kunden_id) REFERENCES kunden (id)
            )
            ''')
            
            # Bestehende Fahrzeugdaten migrieren
            cursor.execute('''
            INSERT INTO fahrzeuge (kunden_id, fahrzeug_typ, kennzeichen, fahrgestellnummer)
            SELECT id, fahrzeug_typ, kennzeichen, fahrgestellnummer
            FROM kunden
            WHERE fahrzeug_typ IS NOT NULL OR kennzeichen IS NOT NULL OR fahrgestellnummer IS NOT NULL
            ''')
            
            conn.commit()
            print("Fahrzeuge-Tabelle erstellt und Daten migriert.")
        
        # Aktuelle Schemaversion abrufen
        cursor.execute("PRAGMA user_version")
        current_version = cursor.fetchone()[0]
        
        print(f"Aktuelle Datenbankversion: {current_version}")
        
        # Updates sequentiell durchführen
        if current_version < 1:
            update_to_version_1(conn)
        
        if current_version < 2:
            update_to_version_2(conn)
        
        # Füge hier weitere Versionsupgrades hinzu
        
        # Standardkonfiguration initialisieren
        init_default_config(conn)

        if current_version < 3:
            update_to_version_3(conn)

def update_to_version_1(conn):
    """Aktualisiert die Datenbank auf Version 1 (Mehrere Fahrzeuge pro Kunde)"""
    print("Aktualisiere Datenbankschema auf Version 1...")
    cursor = conn.cursor()
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 1")
    
    conn.commit()
    print("Datenbankschema auf Version 1 aktualisiert.")

def update_to_version_2(conn):
    """Aktualisiert die Datenbank auf Version 2 (Rabatt bei Rechnungen)"""
    print("Aktualisiere Datenbankschema auf Version 2...")
    cursor = conn.cursor()
    
    # Spalte für Rabatt zur Rechnungstabelle hinzufügen, wenn nicht vorhanden
    cursor.execute("PRAGMA table_info(rechnungen)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'rabatt_prozent' not in columns:
        cursor.execute("ALTER TABLE rechnungen ADD COLUMN rabatt_prozent REAL DEFAULT 0")
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 2")
    
    conn.commit()
    print("Datenbankschema auf Version 2 aktualisiert.")

def update_to_version_3(conn):
    """Aktualisiert die Datenbank auf Version 3 (Einheit für Ersatzteile)"""
    print("Aktualisiere Datenbankschema auf Version 3...")
    cursor = conn.cursor()
    
    # Spalte für Einheit zur Ersatzteile-Tabelle hinzufügen, wenn nicht vorhanden
    cursor.execute("PRAGMA table_info(ersatzteile)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'einheit' not in columns:
        cursor.execute("ALTER TABLE ersatzteile ADD COLUMN einheit TEXT")
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 3")
    
    conn.commit()
    print("Datenbankschema auf Version 3 aktualisiert.")