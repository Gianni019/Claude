#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Allgemeine Dialogfenster für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HilfeDialog:
    """Einfacher Dialog zur Anzeige von Hilfe-Texten"""
    def __init__(self, parent, title, text):
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Text mit Scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        text_widget = tk.Text(text_frame, wrap="word", padx=10, pady=10)
        text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert(tk.END, text)
        text_widget.config(state="disabled")  # Schreibschutz
        
        # Schließen-Button
        ttk.Button(main_frame, text="Schließen", command=self.dialog.destroy).pack(side="right", pady=10)

class ExportDialog:
    """Dialog zum Exportieren von Daten"""
    def __init__(self, parent, title, conn):
        self.parent = parent
        self.conn = conn
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Exportoptionen
        options_frame = ttk.LabelFrame(main_frame, text="Exportoptionen")
        options_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Label(options_frame, text="Daten:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.daten_var = tk.StringVar(value="Kunden")
        daten_combo = ttk.Combobox(options_frame, textvariable=self.daten_var, width=20,
                                  values=["Kunden", "Aufträge", "Ersatzteile", "Rechnungen", "Ausgaben"])
        daten_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(options_frame, text="Format:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.format_var = tk.StringVar(value="CSV")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, width=20,
                                   values=["CSV", "Excel", "JSON"])
        format_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Zeitraumfilter
        filter_frame = ttk.LabelFrame(main_frame, text="Filter")
        filter_frame.pack(fill="x", expand=False, pady=10)
        
        self.filter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Zeitraum filtern", variable=self.filter_var).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Von:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.von_var = tk.StringVar(value="01.01." + str(datetime.now().year))
        ttk.Entry(filter_frame, textvariable=self.von_var, width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Bis:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.bis_var = tk.StringVar(value=datetime.now().strftime('%d.%m.%Y'))
        ttk.Entry(filter_frame, textvariable=self.bis_var, width=15).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Exportieren", command=self.export_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
    def export_data(self):
        """Exportiert die ausgewählten Daten"""
        # In einer echten Anwendung würde hier der Datei-Dialog geöffnet und die Daten exportiert werden
        messagebox.showinfo("Hinweis", f"Die Daten '{self.daten_var.get()}' würden nun im Format '{self.format_var.get()}' exportiert werden.")
        self.dialog.destroy()

class KundenHistorieDialog:
    """Dialog zur Anzeige der Auftragshistorie eines Kunden"""
    def __init__(self, parent, title, kunden_id, conn):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x500")
        self.dialog.transient(parent)
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Kundeninformationen
        self.load_kunde_info(main_frame)
        
        # Aufträge
        auftraege_frame = ttk.LabelFrame(main_frame, text="Aufträge")
        auftraege_frame.pack(fill="both", expand=True, pady=10)
        
        # Tabelle
        table_frame = ttk.Frame(auftraege_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ('id', 'datum', 'beschreibung', 'status', 'betrag')
        self.auftraege_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.auftraege_tree.heading('id', text='ID')
        self.auftraege_tree.heading('datum', text='Datum')
        self.auftraege_tree.heading('beschreibung', text='Beschreibung')
        self.auftraege_tree.heading('status', text='Status')
        self.auftraege_tree.heading('betrag', text='Betrag')
        
        self.auftraege_tree.column('id', width=50, anchor='center')
        self.auftraege_tree.column('datum', width=80)
        self.auftraege_tree.column('beschreibung', width=300)
        self.auftraege_tree.column('status', width=100)
        self.auftraege_tree.column('betrag', width=80, anchor='e')
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.auftraege_tree.yview)
        self.auftraege_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.auftraege_tree.pack(side="left", fill="both", expand=True)

        # Statistiken
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Label(stats_frame, text="Gesamtausgaben:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.gesamtausgaben_var = tk.StringVar(value="-")
        ttk.Label(stats_frame, textvariable=self.gesamtausgaben_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stats_frame, text="Durchschnittliche Auftragssumme:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.durchschnitt_var = tk.StringVar(value="-")
        ttk.Label(stats_frame, textvariable=self.durchschnitt_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Neuer Auftrag", command=self.new_auftrag).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Schließen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Daten laden
        self.load_auftraege()
        self.load_statistics()
        
    def load_kunde_info(self, parent_frame):
        """Lädt die Kundeninformationen"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT vorname, nachname, telefon, email, anschrift, fahrzeug_typ, kennzeichen
        FROM kunden
        WHERE id = ?
        """, (self.kunden_id,))
        
        kunde = cursor.fetchone()
        if kunde:
            info_frame = ttk.LabelFrame(parent_frame, text="Kundeninformationen")
            info_frame.pack(fill="x", expand=False, pady=5)
            
            # Spalte 1 - Persönliche Daten
            col1 = ttk.Frame(info_frame)
            col1.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
            
            ttk.Label(col1, text=f"Name: {kunde[0]} {kunde[1]}", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
            ttk.Label(col1, text=f"Telefon: {kunde[2]}").grid(row=1, column=0, sticky="w")
            ttk.Label(col1, text=f"Email: {kunde[3]}").grid(row=2, column=0, sticky="w")
            ttk.Label(col1, text=f"Anschrift: {kunde[4] or '-'}").grid(row=3, column=0, sticky="w")
            
            # Spalte 2 - Fahrzeugdaten
            col2 = ttk.Frame(info_frame)
            col2.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
            
            ttk.Label(col2, text=f"Fahrzeug: {kunde[5] or '-'}", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
            ttk.Label(col2, text=f"Kennzeichen: {kunde[6] or '-'}").grid(row=1, column=0, sticky="w")
            
    def load_auftraege(self):
        """Lädt die Auftragsdaten des Kunden"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT a.id, strftime('%d.%m.%Y', a.erstellt_am) as datum, a.beschreibung, a.status,
               CASE 
                  WHEN r.gesamtbetrag IS NOT NULL THEN printf("%.2f €", r.gesamtbetrag)
                  ELSE '-'
               END as betrag
        FROM auftraege a
        LEFT JOIN rechnungen r ON a.id = r.auftrag_id
        WHERE a.kunden_id = ?
        ORDER BY a.erstellt_am DESC
        """, (self.kunden_id,))
        
        # Tabelle leeren
        for item in self.auftraege_tree.get_children():
            self.auftraege_tree.delete(item)
            
        # Daten einfügen
        for row in cursor.fetchall():
            if row[3] == "Abgeschlossen":
                self.auftraege_tree.insert('', 'end', values=row, tags=('abgeschlossen',))
            else:
                self.auftraege_tree.insert('', 'end', values=row)
                
        # Tag für abgeschlossene Aufträge konfigurieren
        self.auftraege_tree.tag_configure('abgeschlossen', background='lightgreen')
        
    def load_statistics(self):
        """Lädt statistische Daten zu den Kundenaufträgen"""
        cursor = self.conn.cursor()
        
        # Gesamtausgaben
        cursor.execute("""
        SELECT SUM(r.gesamtbetrag)
        FROM rechnungen r
        JOIN auftraege a ON r.auftrag_id = a.id
        WHERE a.kunden_id = ?
        """, (self.kunden_id,))
        
        gesamtausgaben = cursor.fetchone()[0] or 0
        self.gesamtausgaben_var.set(f"{gesamtausgaben:.2f} €")
        
        # Durchschnittliche Auftragssumme
        cursor.execute("""
        SELECT AVG(r.gesamtbetrag)
        FROM rechnungen r
        JOIN auftraege a ON r.auftrag_id = a.id
        WHERE a.kunden_id = ?
        """, (self.kunden_id,))
        
        durchschnitt = cursor.fetchone()[0] or 0
        self.durchschnitt_var.set(f"{durchschnitt:.2f} €")
        
    def new_auftrag(self):
        """Erstellt einen neuen Auftrag für den Kunden"""
        # Dialog schließen
        self.dialog.destroy()
        
        # Auftragsdialog öffnen
        from dialogs.auftrags_dialog import AuftragsDialog
        AuftragsDialog(self.parent, "Neuer Auftrag", None, self.conn, self.kunden_id)