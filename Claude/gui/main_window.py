#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hauptfenster der Autowerkstatt-Anwendung
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db.database import create_database, backup_database
from dialogs.common_dialogs import HilfeDialog, ExportDialog
from gui.dashboard import create_dashboard_tab
from gui.kunden import create_kunden_tab
from gui.auftraege import create_auftraege_tab
from gui.ersatzteile import create_ersatzteile_tab
from gui.rechnungen import create_rechnungen_tab
from gui.finanzen import create_finanzen_tab

class AutowerkstattApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoMeister - Werkstattverwaltung")
        self.root.state('zoomed')  # Vollbildmodus
        
        # Datenbankinitialisierung
        self.conn = create_database()
        
        # Hauptmenü erstellen
        self.create_menu()
        
        # Hauptansicht erstellen
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tabs erstellen
        self.create_tabs()
        
        # Statusleiste
        self.status_bar = tk.Label(root, text="Bereit", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial Daten laden
        self.load_all_data()

    def new_auftrag(self):
        """Erstellt einen neuen Auftrag"""
        from dialogs.auftrags_dialog import AuftragsDialog
        auftragsdialog = AuftragsDialog(self.root, "Neuer Auftrag", None, self.conn)
        if auftragsdialog.result:
            self.load_auftraege()
            self.update_status("Neuer Auftrag angelegt")

    def new_rechnung(self):
        """Erstellt eine neue Rechnung"""
        from dialogs.rechnungs_dialog import RechnungsDialog
        rechnungsdialog = RechnungsDialog(self.root, "Neue Rechnung", None, self.conn)
        if rechnungsdialog.result:
            self.load_rechnungen()
            self.update_status("Neue Rechnung erstellt")

    def new_ersatzteil(self):
        """Erstellt ein neues Ersatzteil"""
        from dialogs.ersatzteil_dialog import ErsatzteilDialog
        ersatzteildialog = ErsatzteilDialog(self.root, "Neuer Artikel", None, self.conn)
        if ersatzteildialog.result:
            self.load_ersatzteile()
            self.load_categories()
            self.update_status("Neuer Artikel angelegt")

    def create_menu(self):
        """Hauptmenü erstellen"""
        menu_bar = tk.Menu(self.root)
        
        # Datei-Menü
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Datenbank sichern", command=self.backup_database)
        file_menu.add_command(label="Exportieren", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        menu_bar.add_cascade(label="Datei", menu=file_menu)
        
        # Bearbeiten-Menü
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Einstellungen", command=self.open_settings)
        menu_bar.add_cascade(label="Bearbeiten", menu=edit_menu)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Hilfe", command=self.show_help)
        help_menu.add_command(label="Über", command=self.show_about)
        menu_bar.add_cascade(label="Hilfe", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
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
        from gui.dashboard import update_dashboard_data
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

Version: 1.0.0
Erstellt: 2025

Eine Anwendung zur einfachen Verwaltung einer Autowerkstatt.

Entwickelt mit Python und Tkinter.
        """
        
        HilfeDialog(self.root, "Über AutoMeister", about_text)
    
    # Weitere Methoden, die in den Tabs benötigt werden
    # Diese fungieren als Schnittstelle zwischen den GUI-Modulen und den Dialog-Modulen
    
    # Kunden-Methoden
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
            
    # ... weitere Methoden für andere Tabs ...