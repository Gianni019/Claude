#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Datenbankfunktionen für die Autowerkstatt-Anwendung von Gianni Schnyder und Claude
"""

import os
import sqlite3
from datetime import datetime

from db.demo_data import insert_demo_data
from db.schema_updates import update_database_schema

def create_database():
    """Datenbank erstellen oder verbinden"""
    db_path = 'autowerkstatt.db'
    db_exists = os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    
    if not db_exists:
        print("Erstelle neue Datenbank...")
        cursor = conn.cursor()
        
        # Konfiguration Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS konfiguration (
            schluessel TEXT PRIMARY KEY,
            wert TEXT NOT NULL,
            beschreibung TEXT
        )
        ''')
        
        # Kunden Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS kunden (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vorname TEXT NOT NULL,
            nachname TEXT NOT NULL,
            telefon TEXT,
            email TEXT,
            anschrift TEXT,
            fahrzeug_typ TEXT,
            kennzeichen TEXT,
            fahrgestellnummer TEXT,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Aufträge Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS auftraege (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kunden_id INTEGER,
            beschreibung TEXT NOT NULL,
            status TEXT DEFAULT 'Offen',
            prioritaet TEXT DEFAULT 'Normal',
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            abgeschlossen_am TIMESTAMP,
            arbeitszeit REAL DEFAULT 0,
            notizen TEXT,
            FOREIGN KEY (kunden_id) REFERENCES kunden (id)
        )
        ''')
        
        # Ersatzteile Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ersatzteile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artikelnummer TEXT UNIQUE,
            bezeichnung TEXT NOT NULL,
            kategorie TEXT,
            lagerbestand INTEGER DEFAULT 0,
            mindestbestand INTEGER DEFAULT 1,
            einkaufspreis REAL,
            verkaufspreis REAL,
            lieferant TEXT,
            lagerort TEXT,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Aufträge-Ersatzteile Verknüpfungstabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS auftrag_ersatzteile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auftrag_id INTEGER,
            ersatzteil_id INTEGER,
            menge INTEGER DEFAULT 1,
            einzelpreis REAL,
            FOREIGN KEY (auftrag_id) REFERENCES auftraege (id),
            FOREIGN KEY (ersatzteil_id) REFERENCES ersatzteile (id)
        )
        ''')
        
        # Rechnungen Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rechnungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auftrag_id INTEGER UNIQUE,
            rechnungsnummer TEXT UNIQUE,
            datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gesamtbetrag REAL,
            bezahlt BOOLEAN DEFAULT 0,
            bezahlt_am TIMESTAMP,
            zahlungsart TEXT,
            notizen TEXT,
            FOREIGN KEY (auftrag_id) REFERENCES auftraege (id)
        )
        ''')
        
        # Ausgaben Tabelle für die Finanzen
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ausgaben (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategorie TEXT NOT NULL,
            betrag REAL NOT NULL,
            datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            beschreibung TEXT,
            beleg_nr TEXT
        )
        ''')
        
        # Beispieldaten einfügen
        insert_demo_data(cursor)
        
        conn.commit()
        print("Datenbank erfolgreich erstellt und mit Beispieldaten gefüllt")
    else:
        print(f"Verbinde mit vorhandener Datenbank: {db_path}")
    
    # Schema-Updates durchführen (falls nötig)
    update_database_schema(conn)
    
    return conn

def backup_database(conn, backup_path=None):
    """Sichert die Datenbank"""
    import shutil
    
    if backup_path is None:
        backup_path = f"autowerkstatt_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # Verbindung schließen, um Datei zu sichern
    conn.close()
    
    # Datei sichern
    shutil.copy2('autowerkstatt.db', backup_path)
    
    # Verbindung wieder herstellen
    conn = sqlite3.connect('autowerkstatt.db')
    
    return conn, backup_path