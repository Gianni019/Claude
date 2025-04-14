#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialoge für Ersatzteile
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.ersatzteil_dialog import ErsatzteilDialog
from dialogs.bestand_dialog import BestandsDialog

class TeileAuswahlDialog:
    """Dialog zur Auswahl von Ersatzteilen"""
    def __init__(self, parent, title, auftrag_id=None, conn=None):
        self.parent = parent
        self.auftrag_id = auftrag_id
        self.conn = conn
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Suchbereich
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(search_frame, text="Suche:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.search_parts)
        
        ttk.Button(search_frame, text="Neues Teil", command=self.new_part).pack(side="right", padx=5)
        
        # Teile-Tabelle
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        self.parts_tree = ttk.Treeview(table_frame, columns=('id', 'artikelnr', 'name', 'bestand', 'preis'), show='headings')
        self.parts_tree.heading('id', text='ID')
        self.parts_tree.heading('artikelnr', text='Artikelnr.')
        self.parts_tree.heading('name', text='Bezeichnung')
        self.parts_tree.heading('bestand', text='Bestand')
        self.parts_tree.heading('preis', text='Preis (€)')
        
        self.parts_tree.column('id', width=50, anchor='center')
        self.parts_tree.column('artikelnr', width=100)
        self.parts_tree.column('name', width=250)
        self.parts_tree.column('bestand', width=70, anchor='center')
        self.parts_tree.column('preis', width=80, anchor='e')
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.parts_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.parts_tree.xview)
        self.parts_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.parts_tree.pack(side="left", fill="both", expand=True)
        
        # Auswahlbereich
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Label(select_frame, text="Menge:").pack(side="left", padx=5)
        self.menge_var = tk.StringVar(value="1")
        ttk.Spinbox(select_frame, from_=1, to=100, textvariable=self.menge_var, width=5).pack(side="left", padx=5)
        
        ttk.Button(select_frame, text="Hinzufügen", command=self.add_selected_part).pack(side="right", padx=5)
        ttk.Button(select_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Teile laden
        self.load_parts()
        
        self.dialog.wait_window()
        
    def load_parts(self):
        """Lädt alle verfügbaren Ersatzteile"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, artikelnummer, bezeichnung, lagerbestand, printf("%.2f", verkaufspreis) as preis
        FROM ersatzteile
        ORDER BY bezeichnung
        """)
        
        # Tabelle leeren
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
            
        # Daten einfügen
        for row in cursor.fetchall():
            if row[3] > 0:  # Nur Teile mit Bestand anzeigen
                self.parts_tree.insert('', 'end', values=row)
            else:
                # Teile ohne Bestand mit roter Farbe markieren
                self.parts_tree.insert('', 'end', values=row, tags=('no_stock',))
                
        self.parts_tree.tag_configure('no_stock', foreground='red')
            
    def search_parts(self, event=None):
        """Durchsucht die Teile nach dem Suchbegriff"""
        search_term = self.search_var.get().lower()
        
        for item in self.parts_tree.get_children():
            values = self.parts_tree.item(item)['values']
            tags = list(self.parts_tree.item(item)['tags'])
            
            # Suche in Artikelnummer und Bezeichnung
            if (search_term in str(values[1]).lower() or  # Artikelnummer
                search_term in str(values[2]).lower()):   # Bezeichnung
                if 'no_stock' in tags:
                    self.parts_tree.item(item, tags=('match', 'no_stock'))
                else:
                    self.parts_tree.item(item, tags=('match',))
            else:
                if 'no_stock' in tags:
                    self.parts_tree.item(item, tags=('no_stock',))
                else:
                    self.parts_tree.item(item, tags=('',))
                
        if search_term:
            # Hervorheben der Treffer
            self.parts_tree.tag_configure('match', background='lightyellow')
            
    def new_part(self):
        """Öffnet den Dialog zum Anlegen eines neuen Ersatzteils"""
        ersatzteildialog = ErsatzteilDialog(self.dialog, "Neuer Artikel", None, self.conn)
        if ersatzteildialog.result:
            # Teileliste aktualisieren
            self.load_parts()
            
    def add_selected_part(self):
        """Fügt das ausgewählte Teil zum Auftrag hinzu"""
        selected_items = self.parts_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Teil aus.")
            return
            
        try:
            menge = int(self.menge_var.get())
            if menge <= 0:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Menge ein.")
                return
                
            selected_parts = []
            for item in selected_items:
                values = self.parts_tree.item(item)['values']
                part_id = values[0]
                bezeichnung = values[2]
                bestand = values[3]
                preis = float(values[4].replace(',', '.'))
                
                # Einheit abrufen
                cursor = self.conn.cursor()
                cursor.execute("SELECT einheit FROM ersatzteile WHERE id = ?", (part_id,))
                einheit_data = cursor.fetchone()
                einheit = einheit_data[0] if einheit_data and einheit_data[0] else "Stk."
                
                # Prüfen, ob genügend Bestand vorhanden ist
                if menge > bestand:
                    if not messagebox.askyesno("Warnung", f"Der Bestand von '{bezeichnung}' ist nicht ausreichend ({bestand}). Trotzdem hinzufügen?"):
                        continue
                        
                selected_parts.append((part_id, bezeichnung, menge, preis, einheit))
                
            if not selected_parts:
                return
                
            self.result = selected_parts
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Menge ein.")


class NachbestellDialog:
    """Dialog zur Anzeige der Nachbestellliste"""
    def __init__(self, parent, title, conn):
        self.parent = parent
        self.conn = conn
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x500")
        self.dialog.transient(parent)
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Überschrift
        ttk.Label(main_frame, text="Artikel mit niedrigem Lagerbestand", font=("Arial", 12, "bold")).pack(fill="x", pady=5)
        
        # Tabelle
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        columns = ('id', 'artikelnr', 'bezeichnung', 'kategorie', 'bestand', 'mindest', 'differenz', 'lieferant')
        self.nachbestell_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.nachbestell_tree.heading('id', text='ID')
        self.nachbestell_tree.heading('artikelnr', text='Artikelnr.')
        self.nachbestell_tree.heading('bezeichnung', text='Bezeichnung')
        self.nachbestell_tree.heading('kategorie', text='Kategorie')
        self.nachbestell_tree.heading('bestand', text='Aktuell')
        self.nachbestell_tree.heading('mindest', text='Mindest')
        self.nachbestell_tree.heading('differenz', text='Diff.')
        self.nachbestell_tree.heading('lieferant', text='Lieferant')
        
        self.nachbestell_tree.column('id', width=40, anchor='center')
        self.nachbestell_tree.column('artikelnr', width=100)
        self.nachbestell_tree.column('bezeichnung', width=200)
        self.nachbestell_tree.column('kategorie', width=100)
        self.nachbestell_tree.column('bestand', width=60, anchor='center')
        self.nachbestell_tree.column('mindest', width=60, anchor='center')
        self.nachbestell_tree.column('differenz', width=60, anchor='center')
        self.nachbestell_tree.column('lieferant', width=150)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.nachbestell_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.nachbestell_tree.xview)
        self.nachbestell_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.nachbestell_tree.pack(side="left", fill="both", expand=True)
        
        # Nachbestellwert
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(info_frame, text="Geschätzter Nachbestellwert:").pack(side="left", padx=5)
        self.nachbestellwert_var = tk.StringVar(value="0.00 €")
        ttk.Label(info_frame, textvariable=self.nachbestellwert_var, font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Bestand ändern", command=self.change_bestand).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Liste drucken", command=self.print_liste).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Schließen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Daten laden
        self.load_nachbestellliste()
        
    def load_nachbestellliste(self):
        """Lädt die Nachbestellliste"""
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
        
        # Daten einfügen
        for row in cursor.fetchall():
            self.nachbestell_tree.insert('', 'end', values=row[:-1])
            gesamtwert += row[-1]
            
        # Nachbestellwert aktualisieren
        self.nachbestellwert_var.set(f"{gesamtwert:.2f} €")
        
    def change_bestand(self):
        """Ändert den Bestand des ausgewählten Artikels"""
        selected_items = self.nachbestell_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie einen Artikel aus.")
            return
            
        # Artikeldaten
        artikel_id = self.nachbestell_tree.item(selected_items[0])['values'][0]
        bestand = self.nachbestell_tree.item(selected_items[0])['values'][4]
        
        # Dialog zur Bestandsänderung
        dialog = BestandsDialog(self.dialog, "Bestand ändern", artikel_id, self.conn, bestand)
        if dialog.result:
            # Nachbestellliste aktualisieren
            self.load_nachbestellliste()
            
    def print_liste(self):
        """Druckt die Nachbestellliste"""
        # Hinweis anzeigen (Druck-Funktionalität würde in einer produktiven Anwendung implementiert)
        messagebox.showinfo("Hinweis", "Druckfunktionalität ist in dieser Demo nicht vollständig implementiert. Die Nachbestellliste würde nun gedruckt werden.")