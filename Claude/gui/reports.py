#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Erweitertes Berichtswesen für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os

# Moderne Farbpalette wie im Projekt verwendet
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

class ErweitertesBerichtswesen:
    """Klasse für das erweiterte Berichtswesen"""
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Erweitertes Berichtswesen")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        # Dunkler Hintergrund für das Dialog-Fenster
        self.dialog.configure(bg=COLORS["bg_dark"])
        
        # Hauptframe
        self.main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, text="Berichts-Generator", 
                 style="CardTitle.TLabel", font=("Arial", 16, "bold")).pack(side="left")
        
        # Berichtskonfiguration
        config_frame = ttk.LabelFrame(self.main_frame, text="Berichtseinstellungen", style="Card.TFrame")
        config_frame.pack(fill="x", pady=(0, 20), padx=5, ipady=10)
        
        # Berichtstyp
        report_type_frame = ttk.Frame(config_frame, style="Card.TFrame")
        report_type_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(report_type_frame, text="Berichtstyp:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.report_type_var = tk.StringVar(value="Umsatzanalyse")
        report_types = [
            "Umsatzanalyse", 
            "Gewinn und Verlust", 
            "Kundenanalyse", 
            "Auftragsstatistik",
            "Lagerbestandsanalyse", 
            "Top-Produkte", 
            "Arbeitszeiten",
            "Kostenanalyse"
        ]
        report_type_combo = ttk.Combobox(report_type_frame, textvariable=self.report_type_var, 
                                        values=report_types, width=30)
        report_type_combo.grid(row=0, column=1, sticky="w", padx=5)
        report_type_combo.bind("<<ComboboxSelected>>", self.on_report_type_changed)
        
        # Zeitraum
        period_frame = ttk.Frame(config_frame, style="Card.TFrame")
        period_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(period_frame, text="Zeitraum:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.period_var = tk.StringVar(value="Dieser Monat")
        periods = [
            "Heute", 
            "Diese Woche", 
            "Dieser Monat", 
            "Letzter Monat", 
            "Dieses Quartal",
            "Dieses Jahr", 
            "Letztes Jahr", 
            "Benutzerdefiniert"
        ]
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var, 
                                   values=periods, width=30)
        period_combo.grid(row=0, column=1, sticky="w", padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.on_period_changed)
        
        # Benutzerdefinierter Zeitraum (anfangs ausgeblendet)
        self.custom_period_frame = ttk.Frame(config_frame, style="Card.TFrame")
        
        ttk.Label(self.custom_period_frame, text="Von:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.date_from_var = tk.StringVar(value=datetime.now().replace(day=1).strftime('%d.%m.%Y'))
        ttk.Entry(self.custom_period_frame, textvariable=self.date_from_var, width=15).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.custom_period_frame, text="Bis:", style="CardText.TLabel").grid(row=0, column=2, sticky="w", padx=5)
        self.date_to_var = tk.StringVar(value=datetime.now().strftime('%d.%m.%Y'))
        ttk.Entry(self.custom_period_frame, textvariable=self.date_to_var, width=15).grid(row=0, column=3, sticky="w", padx=5)
        
        # Detailgrad
        detail_frame = ttk.Frame(config_frame, style="Card.TFrame")
        detail_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(detail_frame, text="Detailgrad:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.detail_var = tk.StringVar(value="Monatlich")
        details = ["Täglich", "Wöchentlich", "Monatlich", "Quartalsweise", "Jährlich"]
        ttk.Combobox(detail_frame, textvariable=self.detail_var, 
                    values=details, width=30).grid(row=0, column=1, sticky="w", padx=5)
        
        # Darstellungsoptionen
        display_frame = ttk.Frame(config_frame, style="Card.TFrame")
        display_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(display_frame, text="Darstellung:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.display_var = tk.StringVar(value="Balkendiagramm")
        displays = ["Tabelle", "Balkendiagramm", "Liniendiagramm", "Tortendiagramm", "Kombiniert"]
        ttk.Combobox(display_frame, textvariable=self.display_var, 
                    values=displays, width=30).grid(row=0, column=1, sticky="w", padx=5)
        
        # Zusätzliche Optionen
        options_frame = ttk.Frame(config_frame, style="Card.TFrame")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        self.include_tax_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="MwSt. einbeziehen", 
                       variable=self.include_tax_var, 
                       style="TCheckbutton").grid(row=0, column=0, sticky="w", padx=5)
        
        self.show_trend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Trend anzeigen", 
                       variable=self.show_trend_var, 
                       style="TCheckbutton").grid(row=0, column=1, sticky="w", padx=5)
        
        # Button zum Generieren des Berichts
        btn_frame = ttk.Frame(config_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Moderne Button-Klasse
        class ModernButton(tk.Button):
            def __init__(self, parent, text, command, primary=False, **kwargs):
                bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
                fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
                
                super().__init__(parent, text=text, command=command, 
                                bg=bg_color, fg=fg_color,
                                activebackground=COLORS["text_light"], 
                                activeforeground=COLORS["bg_dark"],
                                relief="flat", borderwidth=0, padx=15, pady=8,
                                font=("Arial", 10), cursor="hand2", **kwargs)
        
        generate_btn = ModernButton(btn_frame, text="Bericht generieren", 
                                  command=self.generate_report, primary=True)
        generate_btn.pack(side="right", padx=5)
        
        # Berichtsbereich
        report_frame = ttk.LabelFrame(self.main_frame, text="Berichtsergebnis", style="Card.TFrame")
        report_frame.pack(fill="both", expand=True, pady=(0, 10), padx=5)
        
        # Notebook für verschiedene Ansichten (Diagramm/Tabelle)
        self.report_notebook = ttk.Notebook(report_frame)
        self.report_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab für das Diagramm
        self.chart_frame = ttk.Frame(self.report_notebook, style="Card.TFrame")
        self.report_notebook.add(self.chart_frame, text="Diagramm")
        
        # Matplotlib-Figur und Canvas erstellen
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.patch.set_facecolor(COLORS["bg_medium"])
        self.ax.set_facecolor(COLORS["bg_medium"])
        
        # Achsen anpassen
        self.ax.tick_params(axis='x', colors=COLORS["text_light"])
        self.ax.tick_params(axis='y', colors=COLORS["text_light"])
        self.ax.grid(True, linestyle='--', alpha=0.3, color=COLORS["text_dark"])
        
        # Canvas einbetten
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab für die Tabelle
        self.table_frame = ttk.Frame(self.report_notebook, style="Card.TFrame")
        self.report_notebook.add(self.table_frame, text="Tabelle")
        
        # Treeview für Tabellendaten
        columns = ('period', 'value', 'change')
        self.data_tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        
        self.data_tree.heading('period', text='Zeitraum')
        self.data_tree.heading('value', text='Wert')
        self.data_tree.heading('change', text='Veränderung')
        
        self.data_tree.column('period', width=150)
        self.data_tree.column('value', width=150, anchor='e')
        self.data_tree.column('change', width=150, anchor='e')
        
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.data_tree.pack(side="left", fill="both", expand=True)
        
        # Export-Optionen
        export_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        export_frame.pack(fill="x", pady=10)
        
        export_btn = ModernButton(export_frame, text="Als Excel exportieren",
                                 command=self.export_excel)
        export_btn.pack(side="left", padx=5)
        
        pdf_btn = ModernButton(export_frame, text="Als PDF exportieren",
                              command=self.export_pdf)
        pdf_btn.pack(side="left", padx=5)
        
        print_btn = ModernButton(export_frame, text="Drucken",
                                command=self.print_report)
        print_btn.pack(side="left", padx=5)
        
        close_btn = ModernButton(export_frame, text="Schließen",
                               command=self.dialog.destroy)
        close_btn.pack(side="right", padx=5)
    
    def on_report_type_changed(self, event=None):
        """Reagiert auf Änderungen am Berichtstyp"""
        # Hier könnte abhängig vom Berichtstyp die Oberfläche angepasst werden
        pass
    
    def on_period_changed(self, event=None):
        """Reagiert auf Änderungen am Zeitraum"""
        # Bei benutzerdefiniertem Zeitraum das Datumsauswahl-Frame anzeigen
        if self.period_var.get() == "Benutzerdefiniert":
            self.custom_period_frame.pack(fill="x", padx=10, pady=10)
        else:
            self.custom_period_frame.pack_forget()
    
    def generate_report(self):
        """Generiert den Bericht basierend auf den Einstellungen"""
        report_type = self.report_type_var.get()
        period = self.period_var.get()
        detail = self.detail_var.get()
        display = self.display_var.get()
        
        # SQL WHERE-Klausel für den Zeitraum erstellen
        where_clause, date_values = self.get_time_period_sql()
        
        # Daten für den ausgewählten Berichtstyp abrufen
        if report_type == "Umsatzanalyse":
            title, data = self.generate_revenue_analysis(where_clause, detail)
        elif report_type == "Gewinn und Verlust":
            title, data = self.generate_profit_loss_analysis(where_clause, detail)
        elif report_type == "Kundenanalyse":
            title, data = self.generate_customer_analysis(where_clause)
        elif report_type == "Auftragsstatistik":
            title, data = self.generate_order_statistics(where_clause, detail)
        elif report_type == "Lagerbestandsanalyse":
            title, data = self.generate_inventory_analysis()
        elif report_type == "Top-Produkte":
            title, data = self.generate_top_products(where_clause)
        elif report_type == "Arbeitszeiten":
            title, data = self.generate_working_hours(where_clause, detail)
        elif report_type == "Kostenanalyse":
            title, data = self.generate_cost_analysis(where_clause, detail)
        else:
            messagebox.showerror("Fehler", f"Berichtstyp {report_type} nicht implementiert")
            return
        
        # Diagramm aktualisieren
        self.update_chart(title, data, display)
        
        # Tabelle aktualisieren
        self.update_table(data)
        
        # Notebook zum Diagramm wechseln
        self.report_notebook.select(0)
    
    def get_time_period_sql(self):
        """Erstellt die SQL-WHERE-Klausel für den ausgewählten Zeitraum"""
        period = self.period_var.get()
        where_clause = ""
        date_values = []
        
        if period == "Heute":
            where_clause = "WHERE date(datum) = date('now')"
        elif period == "Diese Woche":
            where_clause = "WHERE date(datum) >= date('now', 'weekday 0', '-7 days')"
        elif period == "Dieser Monat":
            where_clause = "WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now')"
        elif period == "Letzter Monat":
            where_clause = "WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now', '-1 month')"
        elif period == "Dieses Quartal":
            # Aktuelles Quartal berechnen
            month = datetime.now().month
            quarter_start = ((month - 1) // 3) * 3 + 1
            year = datetime.now().year
            start_date = f"{year}-{quarter_start:02d}-01"
            where_clause = f"WHERE date(datum) >= '{start_date}' AND date(datum) <= date('now')"
        elif period == "Dieses Jahr":
            where_clause = "WHERE strftime('%Y', datum) = strftime('%Y', 'now')"
        elif period == "Letztes Jahr":
            where_clause = "WHERE strftime('%Y', datum) = strftime('%Y', 'now', '-1 year')"
        elif period == "Benutzerdefiniert":
            try:
                # Datum aus Eingabefeldern konvertieren
                from_date_parts = self.date_from_var.get().split('.')
                to_date_parts = self.date_to_var.get().split('.')
                
                from_date = f"{from_date_parts[2]}-{from_date_parts[1]}-{from_date_parts[0]}"
                to_date = f"{to_date_parts[2]}-{to_date_parts[1]}-{to_date_parts[0]}"
                
                where_clause = f"WHERE date(datum) >= '{from_date}' AND date(datum) <= '{to_date}'"
            except IndexError:
                messagebox.showerror("Fehler", "Ungültiges Datumsformat. Bitte verwenden Sie TT.MM.JJJJ.")
                where_clause = ""
        
        return where_clause, date_values
    
    def generate_revenue_analysis(self, where_clause, detail):
        """Generiert eine Umsatzanalyse"""
        cursor = self.conn.cursor()
        
        # SQL-Abfrage basierend auf dem Detailgrad
        if detail == "Täglich":
            date_format = "%d.%m.%Y"
            sql_format = "%Y-%m-%d"
            group_by = "GROUP BY date(datum)"
        elif detail == "Wöchentlich":
            date_format = "KW %W %Y"
            sql_format = "%Y-%W"
            group_by = "GROUP BY strftime('%Y-%W', datum)"
        elif detail == "Monatlich":
            date_format = "%m/%Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y-%m', datum)"
        elif detail == "Quartalsweise":
            date_format = "Q%Q %Y"
            sql_format = "%Y-%m"
            # SQLite hat keine direkte Quartalsfunktion, daher berechnen wir es manuell
            group_by = "GROUP BY strftime('%Y', datum) || '-' || ((CAST(strftime('%m', datum) AS INTEGER) - 1) / 3 + 1)"
        else:  # Jährlich
            date_format = "%Y"
            sql_format = "%Y"
            group_by = "GROUP BY strftime('%Y', datum)"
        
        query = f"""
        SELECT strftime('{sql_format}', datum) as period, 
               SUM(gesamtbetrag) as revenue
        FROM rechnungen
        {where_clause}
        {group_by}
        ORDER BY period
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "changes": []
        }
        
        prev_value = None
        for i, (period, revenue) in enumerate(results):
            # Periodenbezeichnung formatieren
            if detail == "Quartalsweise":
                year, month = period.split('-')
                quarter = int(month)
                label = f"Q{quarter} {year}"
            else:
                try:
                    # Datum für bessere Formatierung parsen
                    if detail == "Täglich":
                        dt = datetime.strptime(period, "%Y-%m-%d")
                        label = dt.strftime(date_format)
                    elif detail == "Wöchentlich":
                        # KW Format
                        year, week = period.split('-')
                        label = f"KW {week} {year}"
                    elif detail == "Monatlich":
                        # Monat/Jahr Format
                        year, month = period.split('-')
                        dt = datetime(int(year), int(month), 1)
                        label = dt.strftime(date_format)
                    else:
                        label = period
                except:
                    label = period
            
            data["labels"].append(label)
            data["values"].append(revenue)
            
            # Veränderung zum Vorwert berechnen
            if prev_value is not None and prev_value != 0:
                change_percent = (revenue - prev_value) / prev_value * 100
                data["changes"].append(change_percent)
            else:
                data["changes"].append(0)
                
            prev_value = revenue
        
        return "Umsatzentwicklung", data
    
    def generate_profit_loss_analysis(self, where_clause, detail):
        """Generiert eine Gewinn- und Verlustanalyse"""
        cursor = self.conn.cursor()
        
        # SQL-Abfrage für Einnahmen und Ausgaben
        if detail == "Täglich":
            date_format = "%d.%m.%Y"
            sql_format = "%Y-%m-%d"
            group_by = "GROUP BY date(datum)"
        elif detail == "Wöchentlich":
            date_format = "KW %W %Y"
            sql_format = "%Y-%W"
            group_by = "GROUP BY strftime('%Y-%W', datum)"
        elif detail == "Monatlich":
            date_format = "%m/%Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y-%m', datum)"
        elif detail == "Quartalsweise":
            date_format = "Q%Q %Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y', datum) || '-' || ((CAST(strftime('%m', datum) AS INTEGER) - 1) / 3 + 1)"
        else:  # Jährlich
            date_format = "%Y"
            sql_format = "%Y"
            group_by = "GROUP BY strftime('%Y', datum)"
        
        # Einnahmen abfragen
        einnahmen_query = f"""
        SELECT strftime('{sql_format}', datum) as period, 
               SUM(gesamtbetrag) as revenue
        FROM rechnungen
        {where_clause}
        {group_by}
        ORDER BY period
        """
        
        cursor.execute(einnahmen_query)
        einnahmen_results = cursor.fetchall()
        
        # Ausgaben abfragen
        ausgaben_query = f"""
        SELECT strftime('{sql_format}', datum) as period, 
               SUM(betrag) as expenses
        FROM ausgaben
        {where_clause.replace('datum', 'datum')}
        {group_by}
        ORDER BY period
        """
        
        cursor.execute(ausgaben_query)
        ausgaben_results = cursor.fetchall()
        
        # Daten für alle Perioden zusammenführen
        all_periods = set()
        einnahmen_dict = {}
        ausgaben_dict = {}
        
        for period, revenue in einnahmen_results:
            all_periods.add(period)
            einnahmen_dict[period] = revenue
        
        for period, expenses in ausgaben_results:
            all_periods.add(period)
            ausgaben_dict[period] = expenses
        
        all_periods = sorted(all_periods)
        
        # Daten formatieren
        data = {
            "labels": [],
            "einnahmen": [],
            "ausgaben": [],
            "gewinn": [],
            "changes": []
        }
        
        prev_profit = None
        for period in all_periods:
            # Periodenbezeichnung formatieren
            if detail == "Quartalsweise":
                year, month = period.split('-')
                quarter = int(month)
                label = f"Q{quarter} {year}"
            else:
                try:
                    # Datum für bessere Formatierung parsen
                    if detail == "Täglich":
                        dt = datetime.strptime(period, "%Y-%m-%d")
                        label = dt.strftime(date_format)
                    elif detail == "Wöchentlich":
                        # KW Format
                        year, week = period.split('-')
                        label = f"KW {week} {year}"
                    elif detail == "Monatlich":
                        # Monat/Jahr Format
                        year, month = period.split('-')
                        dt = datetime(int(year), int(month), 1)
                        label = dt.strftime(date_format)
                    else:
                        label = period
                except:
                    label = period
            
            einnahmen = einnahmen_dict.get(period, 0)
            ausgaben = ausgaben_dict.get(period, 0)
            gewinn = einnahmen - ausgaben
            
            data["labels"].append(label)
            data["einnahmen"].append(einnahmen)
            data["ausgaben"].append(ausgaben)
            data["gewinn"].append(gewinn)
            
            # Veränderung zum Vorwert berechnen
            if prev_profit is not None and prev_profit != 0:
                change_percent = (gewinn - prev_profit) / abs(prev_profit) * 100
                data["changes"].append(change_percent)
            else:
                data["changes"].append(0)
                
            prev_profit = gewinn
        
        return "Gewinn- und Verlustrechnung", data
    
    def generate_customer_analysis(self, where_clause):
        """Generiert eine Kundenanalyse"""
        cursor = self.conn.cursor()
        
        # Top-Kunden nach Umsatz
        query = f"""
        SELECT k.id, k.vorname || ' ' || k.nachname as kundenname, 
               COUNT(DISTINCT r.id) as anzahl_rechnungen,
               SUM(r.gesamtbetrag) as umsatz
        FROM kunden k
        JOIN auftraege a ON k.id = a.kunden_id
        JOIN rechnungen r ON a.id = r.auftrag_id
        {where_clause.replace('datum', 'r.datum')}
        GROUP BY k.id
        ORDER BY umsatz DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "counts": [],
            "changes": []
        }
        
        for kunden_id, kundenname, anzahl, umsatz in results:
            data["labels"].append(kundenname)
            data["values"].append(umsatz)
            data["counts"].append(anzahl)
            data["changes"].append(0)  # Keine Veränderung für diese Analyse
        
        return "Top-Kunden nach Umsatz", data
    
    def generate_order_statistics(self, where_clause, detail):
        """Generiert Auftragsstatistiken"""
        cursor = self.conn.cursor()
        
        # SQL-Abfrage basierend auf dem Detailgrad
        if detail == "Täglich":
            date_format = "%d.%m.%Y"
            sql_format = "%Y-%m-%d"
            group_by = "GROUP BY date(erstellt_am)"
        elif detail == "Wöchentlich":
            date_format = "KW %W %Y"
            sql_format = "%Y-%W"
            group_by = "GROUP BY strftime('%Y-%W', erstellt_am)"
        elif detail == "Monatlich":
            date_format = "%m/%Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y-%m', erstellt_am)"
        elif detail == "Quartalsweise":
            date_format = "Q%Q %Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y', erstellt_am) || '-' || ((CAST(strftime('%m', erstellt_am) AS INTEGER) - 1) / 3 + 1)"
        else:  # Jährlich
            date_format = "%Y"
            sql_format = "%Y"
            group_by = "GROUP BY strftime('%Y', erstellt_am)"
        
        # Anzahl der Aufträge nach Zeitraum
        query = f"""
        SELECT strftime('{sql_format}', erstellt_am) as period, 
               COUNT(*) as auftrag_count,
               AVG(arbeitszeit) as avg_arbeitszeit
        FROM auftraege
        {where_clause.replace('datum', 'erstellt_am')}
        {group_by}
        ORDER BY period
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "avg_zeit": [],
            "changes": []
        }
        
        prev_value = None
        for i, (period, count, avg_time) in enumerate(results):
            # Periodenbezeichnung formatieren
            if detail == "Quartalsweise":
                year, month = period.split('-')
                quarter = int(month)
                label = f"Q{quarter} {year}"
            else:
                try:
                    # Datum für bessere Formatierung parsen
                    if detail == "Täglich":
                        dt = datetime.strptime(period, "%Y-%m-%d")
                        label = dt.strftime(date_format)
                    elif detail == "Wöchentlich":
                        # KW Format
                        year, week = period.split('-')
                        label = f"KW {week} {year}"
                    elif detail == "Monatlich":
                        # Monat/Jahr Format
                        year, month = period.split('-')
                        dt = datetime(int(year), int(month), 1)
                        label = dt.strftime(date_format)
                    else:
                        label = period
                except:
                    label = period
            
            data["labels"].append(label)
            data["values"].append(count)
            data["avg_zeit"].append(avg_time or 0)
            
            # Veränderung zum Vorwert berechnen
            if prev_value is not None and prev_value != 0:
                change_percent = (count - prev_value) / prev_value * 100
                data["changes"].append(change_percent)
            else:
                data["changes"].append(0)
                
            prev_value = count
        
        return "Auftragsstatistik", data
    
    def generate_inventory_analysis(self):
        """Generiert eine Lagerbestandsanalyse"""
        cursor = self.conn.cursor()
        
        # Lagerbestand nach Kategorien
        query = """
        SELECT kategorie, 
               COUNT(*) as anzahl_artikel,
               SUM(lagerbestand) as gesamtbestand,
               SUM(lagerbestand * einkaufspreis) as bestandswert
        FROM ersatzteile
        GROUP BY kategorie
        ORDER BY bestandswert DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "counts": [],
            "changes": []
        }
        
        for kategorie, anzahl, bestand, wert in results:
            # Kategoriebezeichnung anpassen
            label = kategorie if kategorie else "Ohne Kategorie"
            
            data["labels"].append(label)
            data["values"].append(wert or 0)
            data["counts"].append(bestand or 0)
            data["changes"].append(0)  # Keine Veränderung für diese Analyse
        
        return "Lagerbestandswerte nach Kategorien", data
    
    def generate_top_products(self, where_clause):
        """Generiert Analyse der meistverkauften Produkte"""
        cursor = self.conn.cursor()
        
        # Top-Produkte nach Verkaufsmenge
        query = f"""
        SELECT e.id, e.bezeichnung, 
               SUM(ae.menge) as verkaufte_menge,
               SUM(ae.menge * ae.einzelpreis) as umsatz
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        JOIN auftraege a ON ae.auftrag_id = a.id
        JOIN rechnungen r ON a.id = r.auftrag_id
        {where_clause.replace('datum', 'r.datum')}
        GROUP BY e.id
        ORDER BY verkaufte_menge DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "revenue": [],
            "changes": []
        }
        
        for produkt_id, bezeichnung, menge, umsatz in results:
            data["labels"].append(bezeichnung)
            data["values"].append(menge)
            data["revenue"].append(umsatz or 0)
            data["changes"].append(0)  # Keine Veränderung für diese Analyse
        
        return "Top-Produkte nach Verkaufsmenge", data
    
    def generate_working_hours(self, where_clause, detail):
        """Generiert Analyse der Arbeitszeiten"""
        cursor = self.conn.cursor()
        
        # SQL-Abfrage basierend auf dem Detailgrad
        if detail == "Täglich":
            date_format = "%d.%m.%Y"
            sql_format = "%Y-%m-%d"
            group_by = "GROUP BY date(erstellt_am)"
        elif detail == "Wöchentlich":
            date_format = "KW %W %Y"
            sql_format = "%Y-%W"
            group_by = "GROUP BY strftime('%Y-%W', erstellt_am)"
        elif detail == "Monatlich":
            date_format = "%m/%Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y-%m', erstellt_am)"
        elif detail == "Quartalsweise":
            date_format = "Q%Q %Y"
            sql_format = "%Y-%m"
            group_by = "GROUP BY strftime('%Y', erstellt_am) || '-' || ((CAST(strftime('%m', erstellt_am) AS INTEGER) - 1) / 3 + 1)"
        else:  # Jährlich
            date_format = "%Y"
            sql_format = "%Y"
            group_by = "GROUP BY strftime('%Y', erstellt_am)"
        
        # Arbeitszeiten nach Zeitraum
        query = f"""
        SELECT strftime('{sql_format}', erstellt_am) as period, 
               SUM(arbeitszeit) as gesamt_arbeitszeit,
               COUNT(*) as anzahl_auftraege
        FROM auftraege
        {where_clause.replace('datum', 'erstellt_am')}
        {group_by}
        ORDER BY period
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "counts": [],
            "changes": []
        }
        
        prev_value = None
        for i, (period, arbeitszeit, anzahl) in enumerate(results):
            # Periodenbezeichnung formatieren
            if detail == "Quartalsweise":
                year, month = period.split('-')
                quarter = int(month)
                label = f"Q{quarter} {year}"
            else:
                try:
                    # Datum für bessere Formatierung parsen
                    if detail == "Täglich":
                        dt = datetime.strptime(period, "%Y-%m-%d")
                        label = dt.strftime(date_format)
                    elif detail == "Wöchentlich":
                        # KW Format
                        year, week = period.split('-')
                        label = f"KW {week} {year}"
                    elif detail == "Monatlich":
                        # Monat/Jahr Format
                        year, month = period.split('-')
                        dt = datetime(int(year), int(month), 1)
                        label = dt.strftime(date_format)
                    else:
                        label = period
                except:
                    label = period
            
            data["labels"].append(label)
            data["values"].append(arbeitszeit or 0)
            data["counts"].append(anzahl)
            
            # Veränderung zum Vorwert berechnen
            if prev_value is not None and prev_value != 0:
                change_percent = ((arbeitszeit or 0) - prev_value) / prev_value * 100
                data["changes"].append(change_percent)
            else:
                data["changes"].append(0)
                
            prev_value = arbeitszeit or 0
        
        return "Arbeitszeiten nach Zeitraum", data
    
    def generate_cost_analysis(self, where_clause, detail):
        """Generiert eine Kostenanalyse"""
        cursor = self.conn.cursor()
        
        # Ausgaben nach Kategorien
        query = f"""
        SELECT kategorie, 
               SUM(betrag) as gesamt_ausgaben
        FROM ausgaben
        {where_clause}
        GROUP BY kategorie
        ORDER BY gesamt_ausgaben DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Daten formatieren
        data = {
            "labels": [],
            "values": [],
            "changes": []
        }
        
        for kategorie, ausgaben in results:
            # Kategoriebezeichnung anpassen
            label = kategorie if kategorie else "Ohne Kategorie"
            
            data["labels"].append(label)
            data["values"].append(ausgaben or 0)
            data["changes"].append(0)  # Keine Veränderung für diese Analyse
        
        return "Ausgaben nach Kategorien", data
    
    def update_chart(self, title, data, display_type):
        """Aktualisiert das Diagramm mit den generierten Daten"""
        # Figur und Achsen zurücksetzen
        self.ax.clear()
        
        # Diagrammtyp basierend auf der Auswahl
        if display_type == "Balkendiagramm":
            # Einfaches Balkendiagramm
            self.ax.bar(data["labels"], data["values"], color=COLORS["accent"], alpha=0.8)
            
            # Text-Werte über den Balken (für kleinere Datensätze)
            if len(data["labels"]) <= 10:
                for i, v in enumerate(data["values"]):
                    self.ax.text(i, v + max(data["values"]) * 0.03, f"{v:.0f}", 
                                ha='center', color=COLORS["text_light"], fontsize=8)
        
        elif display_type == "Liniendiagramm":
            # Liniendiagramm mit Markern
            self.ax.plot(data["labels"], data["values"], marker='o', 
                        color=COLORS["accent"], linewidth=2, markersize=6)
            
            # Gitternetzlinien anzeigen
            self.ax.grid(True, linestyle='--', alpha=0.3, color=COLORS["text_dark"])
        
        elif display_type == "Tortendiagramm":
            # Tortendiagramm (für kategoriale Daten)
            # Farben für die Tortenstücke
            colors = plt.cm.viridis(np.linspace(0, 1, len(data["labels"])))
            
            # Leeres Diagramm, falls keine Daten
            if sum(data["values"]) == 0:
                self.ax.text(0.5, 0.5, "Keine Daten vorhanden", 
                           ha='center', va='center', color=COLORS["text_light"])
            else:
                # Tortendiagramm zeichnen
                wedges, texts, autotexts = self.ax.pie(
                    data["values"], 
                    labels=None, 
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90,
                    wedgeprops={'edgecolor': COLORS["bg_medium"]}
                )
                
                # Textfarben anpassen
                for autotext in autotexts:
                    autotext.set_color(COLORS["bg_dark"])
                
                # Legende anzeigen
                self.ax.legend(wedges, data["labels"], 
                             loc="center left", 
                             bbox_to_anchor=(1, 0, 0.5, 1),
                             fontsize=8)
        
        elif display_type == "Kombiniert":
            # Kombiniertes Balken- und Liniendiagramm
            # Zweite Y-Achse für zusätzliche Daten
            ax2 = self.ax.twinx()
            
            # Balken für Hauptwerte
            bars = self.ax.bar(data["labels"], data["values"], 
                              color=COLORS["accent"], alpha=0.7)
            
            # Zweite Datenserie (falls vorhanden)
            if "einnahmen" in data and "ausgaben" in data:
                # Für Gewinn/Verlust-Analyse
                line = ax2.plot(data["labels"], data["gewinn"], 
                              marker='o', color='white', linewidth=2)
                ax2.set_ylabel('Gewinn/Verlust', color='white')
                ax2.tick_params(axis='y', colors='white')
            elif "avg_zeit" in data:
                # Für Auftragsstatistik
                line = ax2.plot(data["labels"], data["avg_zeit"], 
                              marker='o', color='white', linewidth=2)
                ax2.set_ylabel('Durchschn. Arbeitszeit', color='white')
                ax2.tick_params(axis='y', colors='white')
            elif "counts" in data:
                # Für andere Analysen mit Anzahlen
                line = ax2.plot(data["labels"], data["counts"], 
                              marker='o', color='white', linewidth=2)
                ax2.set_ylabel('Anzahl', color='white')
                ax2.tick_params(axis='y', colors='white')
        
        # Diagramm-Einstellungen
        self.ax.set_title(title, color=COLORS["text_light"], fontsize=14)
        self.ax.set_ylabel('Wert', color=COLORS["text_light"])
        
        # X-Achsenbeschriftungen anpassen
        if len(data["labels"]) > 6:
            # Bei vielen Labels schräg stellen
            self.ax.set_xticklabels(data["labels"], rotation=45, ha='right')
        else:
            self.ax.set_xticklabels(data["labels"])
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_table(self, data):
        """Aktualisiert die Tabelle mit den generierten Daten"""
        # Tabelle leeren
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Je nach verfügbaren Daten die Tabelle füllen
        if "einnahmen" in data and "ausgaben" in data and "gewinn" in data:
            # Für Gewinn/Verlust-Analyse - spezielle Tabellenstruktur
            # Spalten aktualisieren
            self.data_tree["columns"] = ('period', 'revenue', 'expenses', 'profit')
            self.data_tree.heading('period', text='Zeitraum')
            self.data_tree.heading('revenue', text='Einnahmen')
            self.data_tree.heading('expenses', text='Ausgaben')
            self.data_tree.heading('profit', text='Gewinn/Verlust')
            
            self.data_tree.column('period', width=150)
            self.data_tree.column('revenue', width=100, anchor='e')
            self.data_tree.column('expenses', width=100, anchor='e')
            self.data_tree.column('profit', width=100, anchor='e')
            
            # Daten einfügen
            for i, period in enumerate(data["labels"]):
                einnahmen = data["einnahmen"][i]
                ausgaben = data["ausgaben"][i]
                gewinn = data["gewinn"][i]
                
                # Farbige Markierung für Gewinn/Verlust
                if gewinn > 0:
                    self.data_tree.insert('', 'end', values=(
                        period, 
                        f"{einnahmen:.2f} CHF", 
                        f"{ausgaben:.2f} CHF", 
                        f"{gewinn:.2f} CHF"
                    ), tags=('profit',))
                else:
                    self.data_tree.insert('', 'end', values=(
                        period, 
                        f"{einnahmen:.2f} CHF", 
                        f"{ausgaben:.2f} CHF", 
                        f"{gewinn:.2f} CHF"
                    ), tags=('loss',))
            
            # Tags für Gewinn/Verlust konfigurieren
            self.data_tree.tag_configure('profit', foreground=COLORS["success"])
            self.data_tree.tag_configure('loss', foreground=COLORS["danger"])
            
        else:
            # Standardtabelle für andere Analysen
            # Spalten zurücksetzen
            self.data_tree["columns"] = ('period', 'value', 'change')
            self.data_tree.heading('period', text='Zeitraum')
            self.data_tree.heading('value', text='Wert')
            self.data_tree.heading('change', text='Veränderung')
            
            self.data_tree.column('period', width=150)
            self.data_tree.column('value', width=150, anchor='e')
            self.data_tree.column('change', width=150, anchor='e')
            
            # Daten einfügen
            for i, period in enumerate(data["labels"]):
                value = data["values"][i]
                change = data["changes"][i]
                
                # Formatieren je nach Werttyp
                if isinstance(value, float) and abs(value) < 1000:
                    value_str = f"{value:.2f} CHF"
                else:
                    value_str = f"{value:,.2f} CHF" if isinstance(value, float) else str(value)
                
                # Farbige Markierung für Veränderung
                tag = 'neutral'
                if change > 0:
                    change_str = f"+{change:.1f}%"
                    tag = 'positive'
                elif change < 0:
                    change_str = f"{change:.1f}%"
                    tag = 'negative'
                else:
                    change_str = "-"
                    tag = 'neutral'
                
                self.data_tree.insert('', 'end', values=(
                    period, value_str, change_str
                ), tags=(tag,))
            
            # Tags für Veränderungen konfigurieren
            self.data_tree.tag_configure('positive', foreground=COLORS["success"])
            self.data_tree.tag_configure('negative', foreground=COLORS["danger"])
            self.data_tree.tag_configure('neutral', foreground=COLORS["text_light"])
    
    def export_excel(self):
        """Exportiert den Bericht als Excel-Datei"""
        try:
            # Prüfen, ob Pandas verfügbar ist
            import pandas as pd
        except ImportError:
            messagebox.showerror("Fehler", 
                               "Für den Excel-Export wird die Bibliothek 'pandas' benötigt.\n"
                               "Bitte installieren Sie pandas mit 'pip install pandas'.")
            return
        
        # Speicherort wählen
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Dateien", "*.xlsx")],
            title="Bericht als Excel speichern"
        )
        
        if not file_path:
            return  # Abgebrochen
        
        try:
            # Daten aus der Tabelle extrahieren
            data = []
            for item in self.data_tree.get_children():
                values = self.data_tree.item(item)['values']
                data.append(values)
            
            # DataFrame erstellen
            columns = [self.data_tree.heading(col)['text'] for col in self.data_tree['columns']]
            df = pd.DataFrame(data, columns=columns)
            
            # Excel-Datei erstellen
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Bericht', index=False)
            
            messagebox.showinfo("Export erfolgreich", 
                              f"Der Bericht wurde erfolgreich als Excel-Datei gespeichert:\n{file_path}")
            
            # Excel-Datei öffnen
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Linux, macOS
                if os.system('command -v xdg-open') == 0:  # Linux
                    subprocess.call(['xdg-open', file_path])
                else:  # macOS
                    subprocess.call(['open', file_path])
        
        except Exception as e:
            messagebox.showerror("Fehler beim Export", str(e))
    
    def export_pdf(self):
        """Exportiert den Bericht als PDF-Datei"""
        # Hinweis: Für echte PDF-Erstellung würde man matplotlib oder reportlab verwenden
        messagebox.showinfo("Information", 
                           "Die PDF-Export-Funktion ist in der Demo-Version noch nicht vollständig implementiert.")
    
    def print_report(self):
        """Druckt den Bericht"""
        # Hinweis: Für echten Druck würde man matplotlib oder reportlab verwenden
        messagebox.showinfo("Information", 
                           "Die Druckfunktion ist in der Demo-Version noch nicht vollständig implementiert.")