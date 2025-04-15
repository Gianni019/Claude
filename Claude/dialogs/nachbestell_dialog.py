#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisierter Dialog für die Nachbestellliste
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.bestand_dialog import BestandsDialog

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

class ModernNachbestellDialog:
    """Moderner Dialog zur Anzeige der Nachbestellliste"""
    def __init__(self, parent, title, conn):
        self.parent = parent
        self.conn = conn
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Dunkler Hintergrund für das Dialog-Fenster
        self.dialog.configure(bg=COLORS["bg_dark"])
        
        # Custom Styles für diesen Dialog
        style = ttk.Style()
        style.configure("Card.TFrame", background=COLORS["bg_medium"])
        style.configure("CardTitle.TLabel", 
                       background=COLORS["bg_medium"], 
                       foreground=COLORS["text_light"],
                       font=("Arial", 14, "bold"))
        style.configure("CardText.TLabel", 
                       background=COLORS["bg_medium"], 
                       foreground=COLORS["text_dark"],
                       font=("Arial", 10))
        style.configure("Value.TLabel", 
                       background=COLORS["bg_medium"], 
                       foreground=COLORS["accent"],
                       font=("Arial", 12, "bold"))
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header mit Titel und Info
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Artikel mit niedrigem Lagerbestand", style="CardTitle.TLabel")
        title_label.pack(side="left")
        
        # Nachbestellwert-Anzeige
        self.nachbestellwert_var = tk.StringVar(value="0.00 CHF")
        value_label = ttk.Label(header_frame, textvariable=self.nachbestellwert_var, style="Value.TLabel")
        value_label.pack(side="right")
        
        ttk.Label(header_frame, text="Geschätzter Nachbestellwert: ", style="CardText.TLabel").pack(side="right", padx=5)
        
        # Container für Tabelle und Aktionen
        content_frame = ttk.Frame(main_frame, style="Card.TFrame")
        content_frame.pack(fill="both", expand=True)
        
        # Tabelle mit Artikeln
        table_frame = ttk.Frame(content_frame, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Spalten für die Tabelle
        columns = ('id', 'artikelnr', 'bezeichnung', 'kategorie', 'bestand', 'mindest', 'differenz', 'lieferant', 'wert')
        self.nachbestell_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        # Spaltenüberschriften und -breiten
        self.nachbestell_tree.heading('id', text='ID')
        self.nachbestell_tree.heading('artikelnr', text='Artikelnr.')
        self.nachbestell_tree.heading('bezeichnung', text='Bezeichnung')
        self.nachbestell_tree.heading('kategorie', text='Kategorie')
        self.nachbestell_tree.heading('bestand', text='Aktuell')
        self.nachbestell_tree.heading('mindest', text='Mindest')
        self.nachbestell_tree.heading('differenz', text='Diff.')
        self.nachbestell_tree.heading('lieferant', text='Lieferant')
        self.nachbestell_tree.heading('wert', text='Bestellwert')
        
        self.nachbestell_tree.column('id', width=40, anchor='center')
        self.nachbestell_tree.column('artikelnr', width=100)
        self.nachbestell_tree.column('bezeichnung', width=200)
        self.nachbestell_tree.column('kategorie', width=100)
        self.nachbestell_tree.column('bestand', width=60, anchor='center')
        self.nachbestell_tree.column('mindest', width=60, anchor='center')
        self.nachbestell_tree.column('differenz', width=60, anchor='center')
        self.nachbestell_tree.column('lieferant', width=150)
        self.nachbestell_tree.column('wert', width=80, anchor='e')
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.nachbestell_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.nachbestell_tree.xview)
        self.nachbestell_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.nachbestell_tree.pack(fill="both", expand=True)
        
        # Aktions-Buttons
        btn_frame = ttk.Frame(content_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=10)
        
        # Moderne Button-Klasse
        class ModernButton(tk.Button):
            def __init__(self, parent, text, command, icon=None, primary=False, **kwargs):
                bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
                fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
                
                super().__init__(parent, text=text, command=command, 
                                bg=bg_color, fg=fg_color,
                                activebackground=COLORS["text_light"], 
                                activeforeground=COLORS["bg_dark"],
                                relief="flat", borderwidth=0, padx=15, pady=8,
                                font=("Arial", 10), cursor="hand2", **kwargs)
        
        # Buttons
        btn_bestand = ModernButton(btn_frame, text="Bestand ändern", 
                                  command=self.change_bestand, primary=True)
        btn_bestand.pack(side="left", padx=(0, 5))
        
        btn_liste_drucken = ModernButton(btn_frame, text="Liste drucken", 
                                       command=self.print_liste)
        btn_liste_drucken.pack(side="left", padx=5)
        
        btn_export = ModernButton(btn_frame, text="Exportieren", 
                                command=self.export_liste)
        btn_export.pack(side="left", padx=5)
        
        btn_schliessen = ModernButton(btn_frame, text="Schließen", 
                                    command=self.dialog.destroy)
        btn_schliessen.pack(side="right")
        
        # Doppelklick zum Bearbeiten des Bestands
        self.nachbestell_tree.bind("<Double-1>", lambda event: self.change_bestand())
        
        # Daten laden
        self.load_nachbestellliste()
        
    def load_nachbestellliste(self):
        """Lädt die Nachbestellliste mit modernem Styling"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, artikelnummer, bezeichnung, kategorie, lagerbestand, mindestbestand,
               (mindestbestand - lagerbestand) as differenz, lieferant,
               (mindestbestand - lagerbestand) * einkaufspreis as nachbestellwert
        FROM ersatzteile
        WHERE lagerbestand <= mindestbestand
        ORDER BY differenz DESC
        """)
        
        # Tabelle leeren
        for item in self.nachbestell_tree.get_children():
            self.nachbestell_tree.delete(item)
            
        # Gesamtwert berechnen
        gesamtwert = 0
        
        # Daten einfügen mit farblichen Hervorhebungen
        for row in cursor.fetchall():
            # Nachbestellwert formatieren
            nachbestellwert = row[8]
            if nachbestellwert is None:
                nachbestellwert = 0
                
            gesamtwert += nachbestellwert
            
            # Werte für die Tabelle
            values = (
                row[0],  # ID
                row[1],  # Artikelnummer
                row[2],  # Bezeichnung
                row[3],  # Kategorie
                row[4],  # Lagerbestand
                row[5],  # Mindestbestand
                row[6],  # Differenz
                row[7],  # Lieferant
                f"{nachbestellwert:.2f} CHF"  # Nachbestellwert
            )
            
            # Tag basierend auf der Differenz (Dringlichkeit)
            tag = 'normal'
            if row[6] > 5:  # Große Differenz
                tag = 'critical'
            elif row[6] > 2:  # Mittlere Differenz
                tag = 'warning'
                
            # Eintrag zur Tabelle hinzufügen
            self.nachbestell_tree.insert('', 'end', values=values, tags=(tag,))
            
        # Tags für die farbliche Gestaltung
        self.nachbestell_tree.tag_configure('normal', background=COLORS["bg_light"])
        self.nachbestell_tree.tag_configure('warning', background=COLORS["warning"], foreground=COLORS["bg_dark"])
        self.nachbestell_tree.tag_configure('critical', background=COLORS["danger"], foreground=COLORS["bg_dark"])
        
        # Nachbestellwert aktualisieren
        self.nachbestellwert_var.set(f"{gesamtwert:.2f} CHF")
        
    def change_bestand(self):
        """Ändert den Bestand des ausgewählten Artikels"""
        selected_items = self.nachbestell_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie einen Artikel aus.")
            return
            
        # Artikeldaten
        artikel_id = self.nachbestell_tree.item(selected_items[0])['values'][0]
        bestand = self.nachbestell_tree.item(selected_items[0])['values'][4]
        
        # Dialog zur Bestandsänderung mit modernem Design
        dialog = BestandsDialog(self.dialog, "Bestand ändern", artikel_id, self.conn, bestand)
        if dialog.result:
            # Nachbestellliste aktualisieren
            self.load_nachbestellliste()
            
    def print_liste(self):
        """Druckt die Nachbestellliste oder erzeugt ein PDF"""
        # In einer produktiven Anwendung würde hier eine echte Druckfunktion implementiert
        
        # Beispiel: PDF-Erstellung
        try:
            # Tabellendaten sammeln
            data = []
            for item in self.nachbestell_tree.get_children():
                values = self.nachbestell_tree.item(item)['values']
                data.append({
                    'id': values[0],
                    'artikelnr': values[1],
                    'bezeichnung': values[2],
                    'kategorie': values[3],
                    'bestand': values[4],
                    'mindest': values[5],
                    'differenz': values[6],
                    'lieferant': values[7],
                    'wert': values[8]
                })
            
            # Hinweis anzeigen
            messagebox.showinfo(
                "Druckfunktion", 
                f"Es würden {len(data)} Artikel für die Nachbestellung ausgedruckt werden.\n\n"
                "Diese Funktion ist in der Demo-Version nicht vollständig implementiert."
            )
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Druckliste: {e}")
            
    def export_liste(self):
        """Exportiert die Nachbestellliste als CSV oder Excel"""
        # Import für Dateiauswahl-Dialog
        from tkinter import filedialog
        
        # Dateiname und -typ auswählen
        file_path = filedialog.asksaveasfilename(
            title="Nachbestellliste exportieren",
            filetypes=[("CSV-Datei", "*.csv"), ("Excel-Datei", "*.xlsx")],
            defaultextension=".csv"
        )
        
        if not file_path:
            return  # Abgebrochen
            
        try:
            # Daten sammeln
            data = []
            headers = ['ID', 'Artikelnummer', 'Bezeichnung', 'Kategorie', 'Lagerbestand', 
                     'Mindestbestand', 'Differenz', 'Lieferant', 'Bestellwert']
            
            for item in self.nachbestell_tree.get_children():
                values = self.nachbestell_tree.item(item)['values']
                data.append(values)
            
            # Je nach Dateityp exportieren
            if file_path.endswith('.csv'):
                # CSV-Export
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)
                    
                messagebox.showinfo("Export erfolgreich", f"Die Nachbestellliste wurde als CSV-Datei exportiert:\n{file_path}")
                
            elif file_path.endswith('.xlsx'):
                # Excel-Export
                try:
                    import pandas as pd
                    df = pd.DataFrame(data, columns=headers)
                    df.to_excel(file_path, index=False, sheet_name='Nachbestellliste')
                    messagebox.showinfo("Export erfolgreich", f"Die Nachbestellliste wurde als Excel-Datei exportiert:\n{file_path}")
                except ImportError:
                    messagebox.showerror("Fehler", "Für den Excel-Export wird die Bibliothek 'pandas' benötigt.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Exportieren der Nachbestellliste: {e}")

# Alte Klasse für Kompatibilität beibehalten, ruft nur die moderne Variante auf
class NachbestellDialog:
    def __init__(self, parent, title, conn):
        ModernNachbestellDialog(parent, title, conn)