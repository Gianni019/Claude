#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from dialogs.teile_dialog import NachbestellDialog

def create_dashboard_tab(notebook, app):
    """Dashboard-Tab mit Übersicht erstellen"""
    dashboard_frame = ttk.Frame(notebook)
    
    welcome_label = ttk.Label(dashboard_frame, text="Willkommen bei AutoMeister", font=("Arial", 16, "bold"))
    welcome_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
    
    date_label = ttk.Label(dashboard_frame, text=f"Datum: {datetime.now().strftime('%d.%m.%Y')}", font=("Arial", 10))
    date_label.grid(row=1, column=0, columnspan=2, padx=10, pady=2, sticky="w")
    
    # Linke Seite - Statistiken
    stats_frame = ttk.LabelFrame(dashboard_frame, text="Aktuelle Statistiken")
    stats_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    
    offene_auftraege_label = ttk.Label(stats_frame, text="Offene Aufträge: -")
    offene_auftraege_label.pack(anchor="w", padx=10, pady=5)
    
    aktive_kunden_label = ttk.Label(stats_frame, text="Aktive Kunden: -")
    aktive_kunden_label.pack(anchor="w", padx=10, pady=5)
    
    gesamtumsatz_label = ttk.Label(stats_frame, text="Gesamtumsatz (Monat): -")
    gesamtumsatz_label.pack(anchor="w", padx=10, pady=5)
    
    gewinn_label = ttk.Label(stats_frame, text="Aktueller Gewinn (Monat): -")
    gewinn_label.pack(anchor="w", padx=10, pady=5)
    
    lagerwert_label = ttk.Label(stats_frame, text="Aktueller Lagerwert: -")
    lagerwert_label.pack(anchor="w", padx=10, pady=5)
    
    nachbestellung_btn = ttk.Button(stats_frame, text="Nachbestellliste anzeigen", 
                                   command=lambda: show_nachbestellliste(app))
    nachbestellung_btn.pack(anchor="w", padx=10, pady=10)
    
    # Rechte Seite - Schnellzugriff und Diagramme
    right_frame = ttk.Frame(dashboard_frame)
    right_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
    
    # Schnellzugriff
    quick_frame = ttk.LabelFrame(right_frame, text="Schnellzugriff")
    quick_frame.pack(fill="x", padx=5, pady=5)
    
    quick_buttons = [
        ("Neuer Kunde", app.new_kunde),
        ("Neuer Auftrag", app.new_auftrag),
        ("Neue Rechnung", app.new_rechnung),
        ("Artikel hinzufügen", app.new_ersatzteil)
    ]
    
    for i, (text, command) in enumerate(quick_buttons):
        btn = ttk.Button(quick_frame, text=text, command=command)
        btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
    
    # Diagramm für Umsatz
    chart_frame = ttk.LabelFrame(right_frame, text="Umsatzentwicklung (letzte 6 Monate)")
    chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Konfigurieren Sie das Layout, damit es responsiv ist
    dashboard_frame.columnconfigure(0, weight=1)
    dashboard_frame.columnconfigure(1, weight=1)
    dashboard_frame.rowconfigure(2, weight=1)

    # Widget-Dictionary erstellen
    widgets = {
        'offene_auftraege_label': offene_auftraege_label,
        'aktive_kunden_label': aktive_kunden_label,
        'gesamtumsatz_label': gesamtumsatz_label,
        'gewinn_label': gewinn_label,
        'lagerwert_label': lagerwert_label,
        'fig': fig,
        'ax': ax,
        'canvas': canvas
    }
    
    return dashboard_frame, widgets

def update_dashboard_data(app):
    """Aktualisiert das Dashboard mit aktuellen Daten"""
    cursor = app.conn.cursor()
    
    # Offene Aufträge zählen
    cursor.execute("SELECT COUNT(*) FROM auftraege WHERE status != 'Abgeschlossen'")
    offene_auftraege = cursor.fetchone()[0]
    app.dashboard_widgets['offene_auftraege_label'].config(text=f"Offene Aufträge: {offene_auftraege}")
    
    # Aktive Kunden (mit Aufträgen in den letzten 3 Monaten)
    cursor.execute("""
    SELECT COUNT(DISTINCT k.id) 
    FROM kunden k
    JOIN auftraege a ON k.id = a.kunden_id
    WHERE date(a.erstellt_am) >= date('now', '-3 months')
    """)
    aktive_kunden = cursor.fetchone()[0]
    app.dashboard_widgets['aktive_kunden_label'].config(text=f"Aktive Kunden: {aktive_kunden}")
    
    # Gesamtumsatz (Monat)
    cursor.execute("""
    SELECT COALESCE(SUM(gesamtbetrag), 0)
    FROM rechnungen
    WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now')
    """)
    umsatz = cursor.fetchone()[0]
    app.dashboard_widgets['gesamtumsatz_label'].config(text=f"Gesamtumsatz (Monat): {umsatz:.2f} CHF")
    
    # Ausgaben (Monat)
    cursor.execute("""
    SELECT COALESCE(SUM(betrag), 0)
    FROM ausgaben
    WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now')
    """)
    ausgaben = cursor.fetchone()[0]
    
    # Gewinn berechnen
    gewinn = umsatz - ausgaben
    app.dashboard_widgets['gewinn_label'].config(text=f"Aktueller Gewinn (Monat): {gewinn:.2f} CHF")
    
    # Lagerwert berechnen
    cursor.execute("""
    SELECT COALESCE(SUM(lagerbestand * einkaufspreis), 0)
    FROM ersatzteile
    """)
    lagerwert = cursor.fetchone()[0]
    app.dashboard_widgets['lagerwert_label'].config(text=f"Aktueller Lagerwert: {lagerwert:.2f} CHF")
    
    # Umsatzentwicklung (letzte 6 Monate) für Diagramm
    cursor.execute("""
    SELECT strftime('%m/%Y', datum) as monat, SUM(gesamtbetrag) as umsatz
    FROM rechnungen
    WHERE datum >= date('now', '-6 months')
    GROUP BY strftime('%Y-%m', datum)
    ORDER BY strftime('%Y-%m', datum)
    """)
    
    monate = []
    umsaetze = []
    
    for row in cursor.fetchall():
        monate.append(row[0])
        umsaetze.append(row[1])
    
    # Diagramm aktualisieren
    app.dashboard_widgets['ax'].clear()
    app.dashboard_widgets['ax'].bar(monate, umsaetze, color='royalblue')
    app.dashboard_widgets['ax'].set_ylabel('Umsatz (CHF)')
    app.dashboard_widgets['ax'].set_title('Umsatzentwicklung')
    app.dashboard_widgets['ax'].tick_params(axis='x', rotation=45)
    app.dashboard_widgets['ax'].grid(axis='y', linestyle='--', alpha=0.7)
    
    for i, v in enumerate(umsaetze):
        app.dashboard_widgets['ax'].text(i, v + 50, f"{v:.0f} CHF", ha='center', fontsize=8)
    
    app.dashboard_widgets['fig'].tight_layout()
    app.dashboard_widgets['canvas'].draw()

def show_nachbestellliste(app):
    """Zeigt die Nachbestellliste an"""
    NachbestellDialog(app.root, "Nachbestellliste", app.conn)