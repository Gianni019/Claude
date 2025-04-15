#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisiertes Hauptfenster der Autowerkstatt-Anwendung
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sv_ttk  # Optional: Für ein moderneres Erscheinungsbild

from db.database import create_database, backup_database
from dialogs.common_dialogs import HilfeDialog, ExportDialog
from gui.dashboard_modern import create_dashboard_tab  # Verwenden Sie das modernisierte Dashboard
from gui.kunden import create_kunden_tab
from gui.auftraege import create_auftraege_tab
from gui.ersatzteile import create_ersatzteile_tab
from gui.rechnungen import create_rechnungen_tab
from gui.finanzen import create_finanzen_tab
from gui.reports import ErweitertesBerichtswesen
from gui.calendar_manager import KalenderVerwaltung

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

class ModernAutowerkstattApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoMeister - Werkstattverwaltung")
        
        # Vollbildmodus und Mindestgröße festlegen
        self.root.state('zoomed')
        self.root.minsize(1200, 700)  # Minimale Fenstergröße
        
        # Dunkles Design aktivieren, wenn sv_ttk installiert ist
        try:
            sv_ttk.set_theme("dark")
        except NameError:
            # Wenn sv_ttk nicht installiert ist, eigene Dark-Theme-Konfiguration
            self.configure_dark_theme()
            
        # Datenbankinitialisierung
        self.conn = create_database()
        
        # Frame für die Navigationsleiste
        self.nav_frame = tk.Frame(root, bg=COLORS["bg_dark"], width=200)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(0)  # Verhindert, dass der Frame sich an Inhalte anpasst
        
        # App-Logo und -Titel
        logo_frame = tk.Frame(self.nav_frame, bg=COLORS["bg_dark"], height=80)
        logo_frame.pack(fill="x", pady=10)
        
        app_title = tk.Label(logo_frame, text="AutoMeister", 
                            bg=COLORS["bg_dark"], fg=COLORS["accent"],
                            font=("Arial", 18, "bold"))
        app_title.pack(pady=10)
        
        subtitle = tk.Label(logo_frame, text="Werkstattverwaltung", 
                          bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                          font=("Arial", 10))
        subtitle.pack()
        
        # Navigationsmenü erstellen
        self.create_nav_menu()
        
        # Hauptcontainer für Tabs
        main_container = tk.Frame(root, bg=COLORS["bg_medium"])
        main_container.pack(side="right", fill="both", expand=True)
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tabs erstellen
        self.create_tabs()
        
        # Statusleiste
        self.status_bar = tk.Label(root, text="Bereit", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                bg=COLORS["bg_dark"], fg=COLORS["text_light"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial Daten laden
        self.load_all_data()
        
        # Callbacks für Navigation
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def configure_dark_theme(self):
        """Konfiguriert ein dunkles Design für Tkinter"""
        style = ttk.Style()
        
        # Notebook-Design
        style.configure("TNotebook", background=COLORS["bg_dark"])
        style.configure("TNotebook.Tab", background=COLORS["bg_medium"], foreground=COLORS["text_light"])
        style.map("TNotebook.Tab", 
                 background=[("selected", COLORS["accent"])],
                 foreground=[("selected", COLORS["bg_dark"])])
        
        # Frame-Design
        style.configure("TFrame", background=COLORS["bg_medium"])
        
        # Label-Design
        style.configure("TLabel", background=COLORS["bg_medium"], foreground=COLORS["text_light"])
        
        # Button-Design
        style.configure("TButton", 
                      background=COLORS["accent"], 
                      foreground=COLORS["bg_dark"],
                      borderwidth=0)
        style.map("TButton",
                 background=[("active", COLORS["text_light"])],
                 foreground=[("active", COLORS["bg_dark"])])
        
        # Eingabefelder
        style.configure("TEntry", 
                      fieldbackground=COLORS["bg_light"],
                      foreground=COLORS["text_light"],
                      borderwidth=0)
        
        # Weitere Widget-Stile...
        style.configure("Treeview", 
                      background=COLORS["bg_light"], 
                      fieldbackground=COLORS["bg_light"],
                      foreground=COLORS["text_light"])
        style.map("Treeview", 
                 background=[("selected", COLORS["accent"])],
                 foreground=[("selected", COLORS["bg_dark"])])

    def create_nav_menu(self):
        """Erstellt ein vertikales Navigationsmenü"""
        nav_items = [
            ("Dashboard", lambda: self.notebook.select(0), "dashboard"),
            ("Kunden", lambda: self.notebook.select(1), "customers"),
            ("Aufträge", lambda: self.notebook.select(2), "orders"),
            ("Ersatzteile", lambda: self.notebook.select(3), "parts"),
            ("Rechnungen", lambda: self.notebook.select(4), "invoices"),
            ("Finanzen", lambda: self.notebook.select(5), "finances"),
            ("Kalender", self.open_calendar, "calendar"),  # NEU
            ("Berichte", self.open_reports, "reports"),    # NEU
            ("Einstellungen", self.open_settings, "settings")
        ]
        
        menu_frame = tk.Frame(self.nav_frame, bg=COLORS["bg_dark"])
        menu_frame.pack(fill="x", pady=20)
        
        self.nav_buttons = []
        
        for i, (text, command, icon_name) in enumerate(nav_items):
            # Frame für jeden Menüpunkt
            btn_frame = tk.Frame(menu_frame, bg=COLORS["bg_dark"], height=40)
            btn_frame.pack(fill="x", pady=2)
            
            # Hier könnte man Icons hinzufügen, wenn gewünscht
            # icon = tk.PhotoImage(file=f"icons/{icon_name}.png")
            # icon_label = tk.Label(btn_frame, image=icon, bg=COLORS["bg_dark"])
            # icon_label.image = icon
            # icon_label.pack(side="left", padx=10)
            
            # Button mit hover-Effekt
            btn = tk.Label(btn_frame, text=text, bg=COLORS["bg_dark"], fg=COLORS["text_light"],
                          font=("Arial", 11), cursor="hand2", pady=8, padx=15)
            btn.pack(fill="x")
            
            # Bind-Events für Hover-Effekt und Klick
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_light"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["bg_dark"]))
            btn.bind("<Button-1>", lambda e, cmd=command: cmd())
            
            self.nav_buttons.append((btn, i if i < 6 else None))  # Button mit Index speichern
    
    def on_tab_change(self, event):
        """Aktualisiert die Hervorhebung im Navigationsmenü beim Tab-Wechsel"""
        selected_tab = self.notebook.index("current")
        
        # Alle Buttons zurücksetzen
        for btn, idx in self.nav_buttons:
            if idx == selected_tab:
                btn.config(bg=COLORS["bg_light"], fg=COLORS["accent"], 
                         font=("Arial", 11, "bold"))
            else:
                btn.config(bg=COLORS["bg_dark"], fg=COLORS["text_light"], 
                         font=("Arial", 11))

    def create_tabs(self):
        """Erstellt alle Tabs der Anwendung"""
        # Dashboard-Tab
        self.dashboard_frame, self.dashboard_widgets = create_dashboard_tab(self.notebook, self)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Kunden-Tab
        self.kunden_frame, self.kunden_widgets = create_kunden_tab(self.notebook, self)
        self.notebook.add(self.kunden_frame, text="Kunden")
        
        # Aufträge-Tab
        self.auftraege_frame, self.auftraege_widgets = create_auftraege_tab(self.notebook, self)
        self.notebook.add(self.auftraege_frame, text="Aufträge")
        
        # Ersatzteile-Tab
        self.ersatzteile_frame, self.ersatzteile_widgets = create_ersatzteile_tab(self.notebook, self)
        self.notebook.add(self.ersatzteile_frame, text="Ersatzteile")
        
        # Rechnungen-Tab
        self.rechnungen_frame, self.rechnungen_widgets = create_rechnungen_tab(self.notebook, self)
        self.notebook.add(self.rechnungen_frame, text="Rechnungen")
        
        # Finanzen-Tab
        self.finanzen_frame, self.finanzen_widgets = create_finanzen_tab(self.notebook, self)
        self.notebook.add(self.finanzen_frame, text="Finanzen")

    def load_all_data(self):
        """Lädt alle Daten aus der Datenbank"""
        self.load_kunden()
        self.load_auftraege()
        self.load_ersatzteile()
        self.load_rechnungen()
        self.update_dashboard()
        self.update_finanzen()
        self.load_categories()
    
    # Implementiere die restlichen Methoden (load_data, update-Methoden, etc.)
    def load_kunden(self):
        # Kunden laden (implementiert in gui.kunden)
        from gui.kunden import load_kunden_data
        load_kunden_data(self)
        
    def load_auftraege(self):
        # Aufträge laden (implementiert in gui.auftraege)
        from gui.auftraege import load_auftraege_data
        load_auftraege_data(self)
        
    def load_ersatzteile(self):
        # Ersatzteile laden (implementiert in gui.ersatzteile)
        from gui.ersatzteile import load_ersatzteile_data
        load_ersatzteile_data(self)
        
    def load_rechnungen(self):
        # Rechnungen laden (implementiert in gui.rechnungen)
        from gui.rechnungen import load_rechnungen_data
        load_rechnungen_data(self)
    
    def load_categories(self):
        """Lädt Kategorien für Dropdowns"""
        cursor = self.conn.cursor()
    
        # Kategorien für Ersatzteile laden
        cursor.execute("SELECT DISTINCT kategorie FROM ersatzteile WHERE kategorie IS NOT NULL AND kategorie != ''")
        kategorien = [row[0] for row in cursor.fetchall()]
        self.ersatzteile_widgets['kategorie_combo']['values'] = ["Alle"] + kategorien
    
        # Kategorien für Ausgaben laden
        cursor.execute("SELECT DISTINCT kategorie FROM ausgaben WHERE kategorie IS NOT NULL AND kategorie != ''")
        ausgaben_kategorien = [row[0] for row in cursor.fetchall()]
        self.finanzen_widgets['ausgaben_kategorie_combo']['values'] = ["Alle"] + ausgaben_kategorien
        
    def update_dashboard(self):
        """Aktualisiert das Dashboard mit aktuellen Daten"""
        from gui.dashboard_modern import update_dashboard_data
        update_dashboard_data(self)
        
    def update_finanzen(self, event=None):
        """Aktualisiert die Finanzübersicht"""
        from gui.finanzen import update_finanzen_data
        update_finanzen_data(self, event)
        
    def update_status(self, message):
        """Aktualisiert die Statusleiste mit einer Nachricht"""
        self.status_bar.config(text=f"{message} | {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
    # Menü-Funktionen
    def backup_database(self):
        """Sichert die Datenbank"""
        try:
            # Backup erstellen
            self.conn, backup_path = backup_database(self.conn)
            messagebox.showinfo("Information", f"Datenbank wurde gesichert als:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Datensicherung: {e}")
    
    def export_data(self):
        """Exportiert Daten aus der Datenbank"""
        ExportDialog(self.root, "Daten exportieren", self.conn)
    
    def open_settings(self):
        """Öffnet die Einstellungen"""
        from dialogs.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self.root, self.conn)
        # Nach Schließen des Dialogs, Daten neu laden
        self.load_all_data()
    
    def show_help(self):
        """Zeigt die Hilfe an"""
        help_text = """
AutoMeister - Werkstattverwaltung
=================================

Diese Software ermöglicht die Verwaltung einer Autowerkstatt mit folgenden Funktionen:

- Kundenverwaltung: Erfassen und verwalten von Kundendaten und Fahrzeugen
- Auftragsverwaltung: Erfassen, bearbeiten und abrechnen von Werkstattaufträgen
- Ersatzteilverwaltung: Lagerverwaltung für Ersatzteile inkl. Bestandsführung
- Rechnungswesen: Erstellung von Rechnungen und Überwachung von Zahlungseingängen
- Finanzen: Übersicht über Einnahmen, Ausgaben, Gewinn und Lagerwert
- Berichte: Verschiedene Auswertungen und Statistiken

Bei Fragen wenden Sie sich an den Support.
        """
        
        HilfeDialog(self.root, "Hilfe zu AutoMeister", help_text)
    
    def show_about(self):
        """Zeigt Informationen über die Software an"""
        about_text = """
AutoMeister - Werkstattverwaltung
=================================

Version: 2.0.0
Erstellt: 2025

Eine Anwendung zur einfachen Verwaltung einer Autowerkstatt.

Entwickelt mit Python und Tkinter.
        """
        
        HilfeDialog(self.root, "Über AutoMeister", about_text)
    
    # Aktionen für die Schnellzugriff-Buttons
    def new_kunde(self):
        from dialogs.kunden_dialog import KundenDialog
        kundendialog = KundenDialog(self.root, "Neuer Kunde", None, self.conn)
        if kundendialog.result:
            self.load_kunden()
            self.update_status("Neuer Kunde angelegt")
            
    def edit_kunde(self):
        from gui.kunden import get_selected_kunden_id
        from dialogs.kunden_dialog import KundenDialog
        
        kunden_id = get_selected_kunden_id(self)
        if not kunden_id:
            messagebox.showinfo("Information", "Bitte wählen Sie einen Kunden aus.")
            return
            
        kundendialog = KundenDialog(self.root, "Kunde bearbeiten", kunden_id, self.conn)
        if kundendialog.result:
            self.load_kunden()
            self.update_status("Kundendaten aktualisiert")
    
    def new_auftrag(self):
        """Erstellt einen neuen Auftrag"""
        from dialogs.auftrags_dialog import AuftragsDialog
        auftragsdialog = AuftragsDialog(self.root, "Neuer Auftrag", None, self.conn)
        if auftragsdialog.result:
            self.load_auftraege()
            self.update_status("Neuer Auftrag angelegt")
            
            # Zum Aufträge-Tab wechseln
            self.notebook.select(2)  # Index 2 = Aufträge-Tab
            
    def new_rechnung(self):
        """Erstellt eine neue Rechnung"""
        from dialogs.rechnungs_dialog import RechnungsDialog
        rechnungsdialog = RechnungsDialog(self.root, "Neue Rechnung", None, self.conn)
        if rechnungsdialog.result:
            self.load_rechnungen()
            self.update_status("Neue Rechnung erstellt")
            
            # Zum Rechnungen-Tab wechseln
            self.notebook.select(4)  # Index 4 = Rechnungen-Tab
            
    def new_ersatzteil(self):
        """Erstellt ein neues Ersatzteil"""
        from dialogs.ersatzteil_dialog import ErsatzteilDialog
        ersatzteildialog = ErsatzteilDialog(self.root, "Neuer Artikel", None, self.conn)
        if ersatzteildialog.result:
            self.load_ersatzteile()
            self.load_categories()
            self.update_status("Neuer Artikel angelegt")
            
            # Zum Ersatzteile-Tab wechseln
            self.notebook.select(3)  # Index 3 = Ersatzteile-Tab

    # Neue Methoden für die erweiterten Funktionen
    def open_calendar(self):
        """Öffnet den Kalender zur Terminverwaltung"""
        KalenderVerwaltung(self.root, self.conn)
    
    def open_reports(self):
        """Öffnet das erweiterte Berichtswesen"""
        ErweitertesBerichtswesen(self.root, self.conn)