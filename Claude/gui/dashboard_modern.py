#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisiertes Dashboard für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import logging
matplotlib.use("TkAgg")

from dialogs.teile_dialog import NachbestellDialog

# Moderne Farbpalette
COLORS = {
    "bg_dark": "#1e2330",
    "bg_medium": "#2a3142",
    "bg_light": "#353e54",
    "accent": "#5ce0d8",
    "text_light": "#ffffff",
    "text_dark": "#aab0bc",
    "success": "#5fb878",
    "warning": "#f2aa4c",
    "danger": "#f65e5e"
}

class ModernButton(tk.Button):
    def __init__(self, parent, text="", command=None, **kwargs):
        # Standard-Styles für den Button
        default_styles = {
            'bg': COLORS["bg_light"], 
            'fg': COLORS["text_light"],
            'activebackground': COLORS["accent"], 
            'activeforeground': COLORS["bg_dark"],
            'relief': tk.FLAT,
            'borderwidth': 0,
            'padx': 15,
            'pady': 10,
            'font': ("Arial", 10),
            'cursor': "hand2"
        }
        
        # Überschreiben der Standard-Styles mit benutzerdefinierten Kwargs
        default_styles.update(kwargs)
        
        # Button mit den finalen Styles initialisieren
        super().__init__(parent, text=text, command=command, **default_styles)

def create_dashboard_tab(notebook, app):
    """Dashboard-Tab mit moderner Übersicht erstellen"""
    
    # Hauptframe mit dunklem Hintergrund
    dashboard_frame = ttk.Frame(notebook)
    
    # Individuelle Styles für das Dashboard definieren
    style = ttk.Style()
    style.configure("Dashboard.TFrame", background=COLORS["bg_dark"])
    style.configure("DashboardTitle.TLabel", 
                    background=COLORS["bg_dark"], 
                    foreground=COLORS["text_light"], 
                    font=("Arial", 24, "bold"))
    style.configure("DashboardDate.TLabel", 
                   background=COLORS["bg_dark"], 
                   foreground=COLORS["text_dark"],
                   font=("Arial", 10))
    style.configure("Card.TFrame", 
                   background=COLORS["bg_medium"],
                   relief="flat",
                   borderwidth=0)
    style.configure("CardTitle.TLabel", 
                   background=COLORS["bg_medium"], 
                   foreground=COLORS["text_light"],
                   font=("Arial", 12, "bold"))
    style.configure("CardContent.TLabel", 
                  background=COLORS["bg_medium"], 
                  foreground=COLORS["accent"],
                  font=("Arial", 20, "bold"))
    style.configure("CardText.TLabel", 
                  background=COLORS["bg_medium"], 
                  foreground=COLORS["text_dark"],
                  font=("Arial", 10))
    style.configure("Accent.TButton", 
                  background=COLORS["accent"],
                  foreground=COLORS["bg_dark"])
    
    # Hauptcontainer mit Grid-Layout
    main_container = ttk.Frame(dashboard_frame, style="Dashboard.TFrame")
    main_container.pack(fill="both", expand=True)
    
    # Header-Bereich
    header_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
    
    welcome_label = ttk.Label(header_frame, text="Dashboard", style="DashboardTitle.TLabel")
    welcome_label.pack(side="left", anchor="w")
    
    date_label = ttk.Label(header_frame, text=f"{datetime.now().strftime('%d.%m.%Y')}", style="DashboardDate.TLabel")
    date_label.pack(side="right", anchor="e")
    
    # Linke Spalte - Karten mit Kennzahlen
    left_column = ttk.Frame(main_container, style="Dashboard.TFrame")
    left_column.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)

# Karte: Offene Aufträge
    offene_auftraege_card = create_card(left_column, "Offene Aufträge", "-", "Aktuelle Aufträge in Bearbeitung")
    offene_auftraege_card.pack(fill="x", pady=(0, 10))
    
    # Karte: Aktive Kunden
    aktive_kunden_card = create_card(left_column, "Aktive Kunden", "-", "Kunden mit Aufträgen in den letzten 3 Monaten")
    aktive_kunden_card.pack(fill="x", pady=(0, 10))
    
    # Karte: Lagerwert
    lagerwert_card = create_card(left_column, "Aktueller Lagerwert", "-", "Gesamtwert aller Ersatzteile")
    lagerwert_card.pack(fill="x", pady=(0, 10))
    
    # Karte: To-Do Liste (NEU)
    todo_card = create_todo_card(left_column)
    todo_card.pack(fill="x", expand=True)
    
    # Rechte Spalte - Diagramm und Schnellzugriff
    right_column = ttk.Frame(main_container, style="Dashboard.TFrame")
    right_column.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
    
    # Karte: Umsatzdiagramm
    chart_card = ttk.Frame(right_column, style="Card.TFrame")
    chart_card.pack(fill="x", pady=(0, 10), ipady=10)
    
    ttk.Label(chart_card, text="Umsatzentwicklung", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 5))
    
    # Matplotlib-Diagramm mit modernem Design
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Hintergrundfarbe des Diagramms anpassen
    fig.patch.set_facecolor(COLORS["bg_medium"])
    ax.set_facecolor(COLORS["bg_medium"])
    
    # Achsenfarben anpassen
    ax.tick_params(axis='x', colors=COLORS["text_dark"])
    ax.tick_params(axis='y', colors=COLORS["text_dark"])
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["text_dark"])
    
    # Gitternetzlinien anpassen
    ax.grid(True, linestyle='--', alpha=0.3, color=COLORS["text_dark"])
    
    # Diagramm in Tkinter einbetten
    chart_frame = ttk.Frame(chart_card, style="Card.TFrame")
    chart_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.get_tk_widget().configure(bg=COLORS["bg_medium"], highlightbackground=COLORS["bg_medium"])
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Karte: Schnellzugriff
    quick_card = ttk.Frame(right_column, style="Card.TFrame")
    quick_card.pack(fill="x", expand=True, pady=(0, 10), ipady=10)
    
    ttk.Label(quick_card, text="Schnellzugriff", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    button_frame = ttk.Frame(quick_card, style="Card.TFrame")
    button_frame.pack(fill="x", padx=15, pady=5)
    
    # Schnellzugriff-Buttons mit modernem Design
    quick_buttons = [
        ("Neuer Kunde", app.new_kunde),
        ("Neuer Auftrag", app.new_auftrag),
        ("Neue Rechnung", app.new_rechnung),
        ("Artikel hinzufügen", app.new_ersatzteil)
    ]
    
    for i, (text, command) in enumerate(quick_buttons):
        btn = ModernButton(button_frame, text=text, command=command)
        btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
    
    # Nachbestellung-Button
    nachbestellung_btn = ModernButton(quick_card, text="Nachbestellliste anzeigen", 
                                     command=lambda: show_nachbestellliste(app),
                                     bg=COLORS["accent"], fg=COLORS["bg_dark"])
    nachbestellung_btn.pack(anchor="center", pady=15)
    
    # Spaltengewichtung für gleichmäßige Aufteilung
    main_container.columnconfigure(0, weight=1)
    main_container.columnconfigure(1, weight=1)
    main_container.rowconfigure(1, weight=1)

    # Widget-Dictionary erstellen
    widgets = {
        'offene_auftraege_label': get_content_label(offene_auftraege_card),
        'aktive_kunden_label': get_content_label(aktive_kunden_card),
        'lagerwert_label': get_content_label(lagerwert_card),
        'todo_listbox': get_todo_listbox(todo_card),
        'todo_entry': get_todo_entry(todo_card),
        'fig': fig,
        'ax': ax,
        'canvas': canvas
    }
    
    return dashboard_frame, widgets

def create_card(parent, title, value, description):
    """Erstellt eine Infokarte mit Titel, Wert und Beschreibung"""
    card = ttk.Frame(parent, style="Card.TFrame")
    
    ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 5))
    content_label = ttk.Label(card, text=value, style="CardContent.TLabel")
    content_label.pack(anchor="w", padx=15, pady=5)
    ttk.Label(card, text=description, style="CardText.TLabel").pack(anchor="w", padx=15, pady=(0, 15))
    
    return card

def create_todo_card(parent):
    """Erstellt eine To-Do-Liste Karte"""
    card = ttk.Frame(parent, style="Card.TFrame")
    
    ttk.Label(card, text="To-Do Liste", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 5))
    
    # Liste mit benutzerdefinierten Farben
    todo_frame = ttk.Frame(card, style="Card.TFrame")
    todo_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    # Listbox mit modernisierten Farben und Rahmen
    todo_listbox = tk.Listbox(todo_frame, bg=COLORS["bg_light"], fg=COLORS["text_light"],
                             font=("Arial", 10), selectbackground=COLORS["accent"],
                             selectforeground=COLORS["bg_dark"], borderwidth=0,
                             highlightthickness=0, activestyle="none")
    todo_listbox.pack(side="left", fill="both", expand=True)
    
    # Beispiel-To-Dos
    todo_listbox.insert(tk.END, "Ölfilter für Werkstatt bestellen")
    todo_listbox.insert(tk.END, "Herrn Müller wegen Bremsen anrufen")
    todo_listbox.insert(tk.END, "Rechnung #RE-2023-045 verschicken")
    todo_listbox.insert(tk.END, "Serviceplan für BMW aktualisieren")
    
    # Scrollbar mit angepassten Farben
    scrollbar = tk.Scrollbar(todo_frame, orient="vertical", command=todo_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    scrollbar.config(troughcolor=COLORS["bg_light"], bg=COLORS["bg_medium"])
    todo_listbox.config(yscrollcommand=scrollbar.set)
    
    # Eingabebereich für neue To-Dos
    input_frame = ttk.Frame(card, style="Card.TFrame")
    input_frame.pack(fill="x", padx=15, pady=(5, 15))
    
    todo_entry = tk.Entry(input_frame, bg=COLORS["bg_light"], fg=COLORS["text_light"],
                         insertbackground=COLORS["text_light"], font=("Arial", 10),
                         relief="flat", highlightthickness=0)
    todo_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
    
    # Funktionen für die To-Do-Liste
    def add_todo():
        todo_text = todo_entry.get().strip()
        if todo_text:
            todo_listbox.insert(tk.END, todo_text)
            todo_entry.delete(0, tk.END)
    
    def remove_selected_todo():
        selected = todo_listbox.curselection()
        if selected:
            todo_listbox.delete(selected)
    
    # Enter-Taste zum Hinzufügen
    todo_entry.bind("<Return>", lambda event: add_todo())
    
    # Doppelklick oder Entf-Taste zum Entfernen
    todo_listbox.bind("<Double-1>", lambda event: remove_selected_todo())
    todo_listbox.bind("<Delete>", lambda event: remove_selected_todo())
    
    # Buttons für Hinzufügen/Entfernen
    add_btn = tk.Button(input_frame, text="+", command=add_todo,
                       bg=COLORS["accent"], fg=COLORS["bg_dark"],
                       activebackground=COLORS["accent"], activeforeground=COLORS["bg_dark"],
                       font=("Arial", 10, "bold"), width=3, relief="flat", cursor="hand2")
    add_btn.pack(side="left", ipady=3)
    
    return card

def get_content_label(card):
    """Hilfsfunktion zum Abrufen des Wert-Labels aus einer Karte"""
    for child in card.winfo_children():
        if isinstance(child, ttk.Label) and child.cget("style") == "CardContent.TLabel":
            return child
    return None

def get_todo_listbox(card):
    """Hilfsfunktion zum Abrufen der Listbox aus der To-Do-Karte"""
    for frame in card.winfo_children():
        if isinstance(frame, ttk.Frame):
            for child in frame.winfo_children():
                if isinstance(child, tk.Listbox):
                    return child
    return None

def get_todo_entry(card):
    """Hilfsfunktion zum Abrufen des Eingabefelds aus der To-Do-Karte"""
    for frame in card.winfo_children():
        if isinstance(frame, ttk.Frame):
            for child in frame.winfo_children():
                if isinstance(child, tk.Entry):
                    return child
    return None

def update_dashboard_data(app):
    """Aktualisiert das Dashboard mit aktuellen Daten"""
    try:
        # Logging konfigurieren
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
        cursor = app.conn.cursor()
        
        # Offene Aufträge zählen
        try:
            cursor.execute("SELECT COUNT(*) FROM auftraege WHERE status != 'Abgeschlossen'")
            offene_auftraege = cursor.fetchone()[0]
            app.dashboard_widgets['offene_auftraege_label'].config(text=f"{offene_auftraege}")
        except Exception as e:
            logging.error(f"Fehler bei Zählung offener Aufträge: {e}")
            offene_auftraege = 0
        
        # Aktive Kunden (mit Aufträgen in den letzten 3 Monaten)
        try:
            cursor.execute("""
            SELECT COUNT(DISTINCT k.id) 
            FROM kunden k
            JOIN auftraege a ON k.id = a.kunden_id
            WHERE date(a.erstellt_am) >= date('now', '-3 months')
            """)
            aktive_kunden = cursor.fetchone()[0]
            app.dashboard_widgets['aktive_kunden_label'].config(text=f"{aktive_kunden}")
        except Exception as e:
            logging.error(f"Fehler bei Zählung aktiver Kunden: {e}")
            aktive_kunden = 0
        
        # Lagerwert berechnen
        try:
            cursor.execute("""
            SELECT COALESCE(SUM(lagerbestand * einkaufspreis), 0)
            FROM ersatzteile
            """)
            lagerwert = cursor.fetchone()[0]
            app.dashboard_widgets['lagerwert_label'].config(text=f"{lagerwert:.2f} CHF")
        except Exception as e:
            logging.error(f"Fehler bei Berechnung des Lagerwerts: {e}")
            lagerwert = 0.0
        
        # Umsatzentwicklung für Diagramm
        try:
            cursor.execute("""
            SELECT strftime('%m/%Y', datum) as monat, 
                   COALESCE(SUM(gesamtbetrag), 0) as umsatz
            FROM rechnungen
            WHERE datum >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', datum)
            ORDER BY strftime('%Y-%m', datum)
            """)
            
            umsatz_daten = cursor.fetchall()
            monate = [row[0] for row in umsatz_daten]
            umsaetze = [row[1] for row in umsatz_daten]
            
            # Diagramm aktualisieren
            ax = app.dashboard_widgets['ax']
            ax.clear()
            
            if umsaetze:
                ax.bar(monate, umsaetze, color=COLORS["accent"], alpha=0.8)
                
                # Text-Werte über den Balken
                for i, v in enumerate(umsaetze):
                    ax.text(i, v + max(umsaetze) * 0.03, f"{v:.0f} CHF", 
                            ha='center', color=COLORS["text_light"], fontsize=8)
            
            # Diagramm-Einstellungen
            ax.set_ylabel('Umsatz (CHF)', color=COLORS["text_light"])
            ax.set_title('Umsatzentwicklung (letzte 6 Monate)', 
                         color=COLORS["text_light"], fontsize=12)
            ax.tick_params(axis='x', rotation=45, colors=COLORS["text_light"])
            ax.tick_params(axis='y', colors=COLORS["text_light"])
            ax.grid(axis='y', linestyle='--', alpha=0.3, color=COLORS["text_dark"])
            
            app.dashboard_widgets['fig'].tight_layout()
            app.dashboard_widgets['canvas'].draw()
            
        except Exception as e:
            logging.error(f"Fehler bei Umsatzdiagramm-Erstellung: {e}")
        
    except Exception as e:
        logging.error(f"Unerwarteter Fehler im Dashboard-Update: {e}")

def show_nachbestellliste(app):
    """Zeigt die Nachbestellliste an"""
    try:
        NachbestellDialog(app.root, "Nachbestellliste", app.conn)
    except Exception as e:
        logging.error(f"Fehler beim Öffnen der Nachbestellliste: {e}")
        messagebox.showerror("Fehler", f"Konnte Nachbestellliste nicht öffnen: {e}")