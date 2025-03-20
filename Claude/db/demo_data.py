#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Beispieldaten für die Autowerkstatt-Anwendung
"""

from datetime import datetime

def insert_demo_data(cursor):
    """Beispieldaten für die App einfügen"""
    # Beispielkunden
    kunden = [
        ('Max', 'Mustermann', '0123456789', 'max@example.com', 'Musterstraße 1, 12345 Stadt', 'VW Golf', 'AB-CD 123', 'WVWZZZ1KZAP047685', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Anna', 'Schmidt', '0987654321', 'anna@example.com', 'Hauptstraße 5, 54321 Dorf', 'BMW 3er', 'EF-GH 456', 'WBAPK7C59AA123456', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    cursor.executemany('INSERT INTO kunden (vorname, nachname, telefon, email, anschrift, fahrzeug_typ, kennzeichen, fahrgestellnummer, erstellt_am) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', kunden)
    
    # Beispielersatzteile
    ersatzteile = [
        ('OEL-5W40-1L', 'Motoröl 5W-40 1L', 'Öle', 15, 5, 9.99, 19.99, 'AutoTeile GmbH', 'Regal A1', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('FILT-OEL-001', 'Ölfilter Standard', 'Filter', 8, 3, 4.50, 12.99, 'FilterMax KG', 'Regal B2', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('BREMS-001', 'Bremsbeläge vorne', 'Bremsen', 4, 2, 25.00, 65.00, 'BremsenPro', 'Regal C3', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    cursor.executemany('INSERT INTO ersatzteile (artikelnummer, bezeichnung, kategorie, lagerbestand, mindestbestand, einkaufspreis, verkaufspreis, lieferant, lagerort, erstellt_am) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ersatzteile)
    
    # Beispielaufträge
    auftraege = [
        (1, 'Ölwechsel und Inspektion', 'Abgeschlossen', 'Normal', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1.5, 'Kunde wünscht Anruf nach Fertigstellung'),
        (2, 'Bremsen prüfen und ggf. erneuern', 'In Bearbeitung', 'Hoch', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, 0, 'Bremsen quietschen bei starkem Bremsen')
    ]
    
    cursor.executemany('INSERT INTO auftraege (kunden_id, beschreibung, status, prioritaet, erstellt_am, abgeschlossen_am, arbeitszeit, notizen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', auftraege)
    
    # Verknüpfung Auftrag-Ersatzteile
    auftrag_ersatzteile = [
        (1, 1, 1, 19.99),
        (1, 2, 1, 12.99)
    ]
    
    cursor.executemany('INSERT INTO auftrag_ersatzteile (auftrag_id, ersatzteil_id, menge, einzelpreis) VALUES (?, ?, ?, ?)', auftrag_ersatzteile)
    
    # Beispielrechnung
    rechnungen = [
        (1, 'RE-2023-001', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 82.98, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Bar', '')
    ]
    
    cursor.executemany('INSERT INTO rechnungen (auftrag_id, rechnungsnummer, datum, gesamtbetrag, bezahlt, bezahlt_am, zahlungsart, notizen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', rechnungen)
    
    # Beispielausgaben
    ausgaben = [
        ('Einkauf Ersatzteile', 250.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Großbestellung Filter und Öl', 'BE-2023-01'),
        ('Miete', 800.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Werkstattmiete März', 'BE-2023-02'),
        ('Versicherung', 120.00, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Haftpflichtversicherung Q1', 'BE-2023-03')
    ]
    
    cursor.executemany('INSERT INTO ausgaben (kategorie, betrag, datum, beschreibung, beleg_nr) VALUES (?, ?, ?, ?, ?)', ausgaben)