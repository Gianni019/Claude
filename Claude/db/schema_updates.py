#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aktualisierung des Datenbankschemas für die Autowerkstatt-Anwendung
"""

import sqlite3
from utils.config import init_default_config

def update_database_schema(conn):
    """Aktualisiert das Datenbankschema auf die aktuelle Version"""
    cursor = conn.cursor()
    
    # Aktuelle Schemaversion abrufen
    cursor.execute("PRAGMA user_version")
    current_version = cursor.fetchone()[0]
    
    print(f"Aktuelle Datenbankversion: {current_version}")
    
    # Updates sequentiell durchführen
    if current_version < 1:
        update_to_version_1(conn)
    
    if current_version < 2:
        update_to_version_2(conn)
    
    if current_version < 3:
        update_to_version_3(conn)
        
    if current_version < 4:
        update_to_version_4(conn)
        
    if current_version < 5:
        update_to_version_5(conn)
        
    if current_version < 6:  # NEU
        update_to_version_6(conn)

    if current_version < 7:
        update_to_version_7(conn)
    
    # Standardkonfiguration initialisieren
    init_default_config(conn)
    
def update_to_version_1(conn):
    """Aktualisiert die Datenbank auf Version 1 (Mehrere Fahrzeuge pro Kunde)"""
    print("Aktualisiere Datenbankschema auf Version 1...")
    cursor = conn.cursor()
    
    # Prüfen, ob die Tabelle fahrzeuge bereits existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fahrzeuge'")
    if not cursor.fetchone():
        # Fahrzeuge-Tabelle erstellen
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
    """Aktualisiert die Datenbank auf Version 3 (Einheit bei Ersatzteilen)"""
    print("Aktualisiere Datenbankschema auf Version 3...")
    cursor = conn.cursor()
    
    # Spalte für Einheit zur Ersatzteile-Tabelle hinzufügen, wenn nicht vorhanden
    cursor.execute("PRAGMA table_info(ersatzteile)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'einheit' not in columns:
        cursor.execute("ALTER TABLE ersatzteile ADD COLUMN einheit TEXT DEFAULT 'Stk.'")
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 3")
    
    conn.commit()
    print("Datenbankschema auf Version 3 aktualisiert.")

def update_to_version_4(conn):
    """Aktualisiert die Datenbank auf Version 4 (Fahrzeug-ID in Aufträgen)"""
    print("Aktualisiere Datenbankschema auf Version 4...")
    cursor = conn.cursor()
    
    # Spalte für Fahrzeug-ID zur auftraege-Tabelle hinzufügen, wenn nicht vorhanden
    cursor.execute("PRAGMA table_info(auftraege)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'fahrzeug_id' not in columns:
        cursor.execute("ALTER TABLE auftraege ADD COLUMN fahrzeug_id INTEGER")
        
        # Optional: Bestehende Aufträge mit Fahrzeug-IDs aktualisieren
        # Für jeden Auftrag das erste Fahrzeug des Kunden verwenden
        cursor.execute("""
        SELECT a.id, a.kunden_id, MIN(f.id) as fahrzeug_id
        FROM auftraege a
        JOIN fahrzeuge f ON a.kunden_id = f.kunden_id
        GROUP BY a.id
        """)
        
        for auftrag_id, kunden_id, fahrzeug_id in cursor.fetchall():
            if fahrzeug_id:
                cursor.execute("""
                UPDATE auftraege SET fahrzeug_id = ? WHERE id = ?
                """, (fahrzeug_id, auftrag_id))
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 4")
    
    conn.commit()
    print("Datenbankschema auf Version 4 aktualisiert.")

def update_to_version_5(conn):
    """Aktualisiert die Datenbank auf Version 5 (Rabatt-Spalte in auftrag_ersatzteile)"""
    print("Aktualisiere Datenbankschema auf Version 5...")
    cursor = conn.cursor()
    
    # Spalte für Rabatt zur auftrag_ersatzteile-Tabelle hinzufügen
    cursor.execute("PRAGMA table_info(auftrag_ersatzteile)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'rabatt' not in columns:
        cursor.execute("ALTER TABLE auftrag_ersatzteile ADD COLUMN rabatt REAL DEFAULT 0")
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 5")
    
    conn.commit()
    print("Datenbankschema auf Version 5 aktualisiert.")

def update_to_version_6(conn):
    """Aktualisiert die Datenbank auf Version 6 (Termine)"""
    print("Aktualisiere Datenbankschema auf Version 6...")
    cursor = conn.cursor()
    
    # Termine-Tabelle hinzufügen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS termine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titel TEXT NOT NULL,
        beschreibung TEXT,
        datum DATE NOT NULL,
        uhrzeit_von TIME,
        uhrzeit_bis TIME,
        kunde_id INTEGER,
        auftrag_id INTEGER,
        status TEXT DEFAULT 'Geplant',
        farbe TEXT DEFAULT '#5ce0d8',
        erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kunde_id) REFERENCES kunden (id),
        FOREIGN KEY (auftrag_id) REFERENCES auftraege (id)
    )
    """)
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 6")
    
    conn.commit()
    print("Datenbankschema auf Version 6 aktualisiert.")

def update_to_version_7(conn):
    """Aktualisiert die Datenbank auf Version 7 (TODO-Liste)"""
    print("Aktualisiere Datenbankschema auf Version 7...")
    cursor = conn.cursor()
    
    # TODO-Liste Tabelle hinzufügen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        erledigt INTEGER DEFAULT 0,
        erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Schemaversion aktualisieren
    cursor.execute("PRAGMA user_version = 7")
    
    conn.commit()
    print("Datenbankschema auf Version 7 aktualisiert.")