#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ersatzteile-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.ersatzteil_dialog import ErsatzteilDialog
from dialogs.bestand_dialog import BestandsDialog
from dialogs.teile_dialog import NachbestellDialog

def create_ersatzteile_tab(notebook, app):
    """Ersatzteile-Tab erstellen"""
    ersatzteile_frame = ttk.Frame(notebook)
    
    # Suchleiste und Filter
    filter_frame = ttk.Frame(ersatzteile_frame)
    filter_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(filter_frame, text="Suche:").grid(row=0, column=0, padx=5)
    ersatzteile_search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=ersatzteile_search_var, width=20)
    search_entry.grid(row=0, column=1, padx=5)
    search_entry.bind("<KeyRelease>", lambda event: search_ersatzteile(app))
    
    ttk.Label(filter_frame, text="Kategorie:").grid(row=0, column=2, padx=5)
    kategorie_filter_var = tk.StringVar(value="Alle")
    kategorie_combo = ttk.Combobox(filter_frame, textvariable=kategorie_filter_var, width=15)
    kategorie_combo.grid(row=0, column=3, padx=5)
    kategorie_combo.bind("<<ComboboxSelected>>", lambda event: filter_ersatzteile(app))
    
    # Checkbox für Artikel mit niedrigem Bestand
    low_stock_var = tk.BooleanVar()
    ttk.Checkbutton(filter_frame, text="Nur Artikel mit niedrigem Bestand", variable=low_stock_var, 
                    command=lambda: filter_ersatzteile(app)).grid(row=0, column=4, padx=5)
    
    # Buttons
    btn_frame = ttk.Frame(ersatzteile_frame)
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(btn_frame, text="Neuer Artikel", command=lambda: new_ersatzteil(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Bearbeiten", command=lambda: edit_ersatzteil(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Löschen", command=lambda: delete_ersatzteil(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Bestand ändern", command=lambda: change_inventory(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Nachbestellliste", command=lambda: show_nachbestellliste(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Aktualisieren", command=lambda: app.load_ersatzteile()).pack(side="right", padx=5)
    
    # Tabelle
    table_frame = ttk.Frame(ersatzteile_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Spalten der Treeview aktualisieren
    columns = ('id', 'artikelnr', 'bezeichnung', 'kategorie', 'lagerbestand', 'mindestbestand', 'einkaufspreis', 'verkaufspreis', 'lagerort', 'einheit')
    ersatzteile_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

    # Spaltenkonfiguration
    ersatzteile_tree.heading('id', text='ID')
    ersatzteile_tree.heading('artikelnr', text='Artikelnr')
    ersatzteile_tree.heading('bezeichnung', text='Bezeichnung')
    ersatzteile_tree.heading('kategorie', text='Kategorie')
    ersatzteile_tree.heading('lagerbestand', text='Bestand')
    ersatzteile_tree.heading('mindestbestand', text='Min. Bestand')
    ersatzteile_tree.heading('einkaufspreis', text='EK (CHF)')
    ersatzteile_tree.heading('verkaufspreis', text='VK (CHF)')
    ersatzteile_tree.heading('lagerort', text='Lagerort')
    ersatzteile_tree.heading('einheit', text='Einheit')

    ersatzteile_tree.column('id', width=40, anchor='center')
    ersatzteile_tree.column('artikelnr', width=80)
    ersatzteile_tree.column('bezeichnung', width=200)
    ersatzteile_tree.column('kategorie', width=80)
    ersatzteile_tree.column('lagerbestand', width=60, anchor='center')
    ersatzteile_tree.column('mindestbestand', width=60, anchor='center')
    ersatzteile_tree.column('einkaufspreis', width=70, anchor='e')
    ersatzteile_tree.column('verkaufspreis', width=70, anchor='e')
    ersatzteile_tree.column('lagerort', width=80)
    ersatzteile_tree.column('einheit', width=60, anchor='center')
        
    # Scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=ersatzteile_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=ersatzteile_tree.xview)
    ersatzteile_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    ersatzteile_tree.pack(fill="both", expand=True)
    
    # Artikeldetails unten anzeigen
    details_frame = ttk.LabelFrame(ersatzteile_frame, text="Artikeldetails")
    details_frame.pack(fill="x", padx=10, pady=10)
    
    # Spalten für Details
    left_details = ttk.Frame(details_frame)
    left_details.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
    
    right_details = ttk.Frame(details_frame)
    right_details.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
    
    # Linke Spalte - Artikelinfos
    ttk.Label(left_details, text="Artikelwert:").grid(row=0, column=0, sticky="w", pady=2)
    artikel_wert_info = ttk.Label(left_details, text="-")
    artikel_wert_info.grid(row=0, column=1, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Lieferant:").grid(row=1, column=0, sticky="w", pady=2)
    artikel_lieferant_info = ttk.Label(left_details, text="-")
    artikel_lieferant_info.grid(row=1, column=1, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Bestellstatus:").grid(row=2, column=0, sticky="w", pady=2)
    artikel_status_info = ttk.Label(left_details, text="-")
    artikel_status_info.grid(row=2, column=1, sticky="w", pady=2)
    
    # Rechte Spalte - Graphik
    ttk.Label(right_details, text="Bestandsentwicklung:").grid(row=0, column=0, sticky="w", pady=2)
    # Hier würde ein Miniaturdiagramm eingebunden werden
    
    # Doppelklick zum Bearbeiten
    ersatzteile_tree.bind("<Double-1>", lambda event: edit_ersatzteil(app))
    
    # Event-Handler für Tabellenauswahl
    ersatzteile_tree.bind("<<TreeviewSelect>>", lambda event: show_ersatzteil_details(app))

    # Widget-Dictionary erstellen
    widgets = {
        'ersatzteile_search_var': ersatzteile_search_var,
        'kategorie_filter_var': kategorie_filter_var,
        'kategorie_combo': kategorie_combo,
        'low_stock_var': low_stock_var,
        'ersatzteile_tree': ersatzteile_tree,
        'artikel_wert_info': artikel_wert_info,
        'artikel_lieferant_info': artikel_lieferant_info,
        'artikel_status_info': artikel_status_info
    }
    
    return ersatzteile_frame, widgets

def load_ersatzteile_data(app):
    """Lädt Ersatzteildaten aus der Datenbank"""
    cursor = app.conn.cursor()
    cursor.execute("""
    SELECT id, artikelnummer, bezeichnung, kategorie, lagerbestand, mindestbestand,
           printf("%.2f", einkaufspreis) as einkaufspreis, 
           printf("%.2f", verkaufspreis) as verkaufspreis, lagerort, einheit
    FROM ersatzteile
    ORDER BY bezeichnung
    """)
    
    # Treeview leeren
    for item in app.ersatzteile_widgets['ersatzteile_tree'].get_children():
        app.ersatzteile_widgets['ersatzteile_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        # Farbige Markierung bei niedrigem Bestand
        if row[4] <= row[5]:  # lagerbestand <= mindestbestand
            app.ersatzteile_widgets['ersatzteile_tree'].insert('', 'end', values=row, tags=('low_stock',))
        else:
            app.ersatzteile_widgets['ersatzteile_tree'].insert('', 'end', values=row)
            
    # Tag für niedrigen Bestand erstellen
    app.ersatzteile_widgets['ersatzteile_tree'].tag_configure('low_stock', background='lightsalmon')
        
    app.update_status(f"{app.ersatzteile_widgets['ersatzteile_tree'].get_children().__len__()} Artikel geladen")

def search_ersatzteile(app):
    """Durchsucht die Ersatzteilliste nach dem Suchbegriff"""
    search_term = app.ersatzteile_widgets['ersatzteile_search_var'].get().lower()
    
    for item in app.ersatzteile_widgets['ersatzteile_tree'].get_children():
        values = app.ersatzteile_widgets['ersatzteile_tree'].item(item)['values']
        tags = list(app.ersatzteile_widgets['ersatzteile_tree'].item(item)['tags'])
        
        # Suche in Artikelnummer, Bezeichnung, Kategorie und Lagerort
        if (search_term in str(values[1]).lower() or  # Artikelnummer
            search_term in str(values[2]).lower() or  # Bezeichnung
            search_term in str(values[3]).lower() or  # Kategorie
            search_term in str(values[8]).lower()):   # Lagerort
            if 'low_stock' in tags:
                app.ersatzteile_widgets['ersatzteile_tree'].item(item, tags=('match', 'low_stock'))
            else:
                app.ersatzteile_widgets['ersatzteile_tree'].item(item, tags=('match',))
        else:
            if 'low_stock' in tags:
                app.ersatzteile_widgets['ersatzteile_tree'].item(item, tags=('low_stock',))
            else:
                app.ersatzteile_widgets['ersatzteile_tree'].item(item, tags=('',))
            
    if search_term:
        # Hervorheben der Treffer
        app.ersatzteile_widgets['ersatzteile_tree'].tag_configure('match', background='lightyellow')
    else:
        # Filter anwenden, wenn Suchfeld leer
        filter_ersatzteile(app)

def filter_ersatzteile(app):
    """Filtert Ersatzteile nach Kategorie und niedrigem Bestand"""
    kategorie_filter = app.ersatzteile_widgets['kategorie_filter_var'].get()
    low_stock_filter = app.ersatzteile_widgets['low_stock_var'].get()
    
    cursor = app.conn.cursor()
    
    where_clause = "WHERE 1=1"
    params = []
    
    if kategorie_filter != "Alle":
        where_clause += " AND kategorie = ?"
        params.append(kategorie_filter)
        
    if low_stock_filter:
        where_clause += " AND lagerbestand <= mindestbestand"
        
    query = f"""
    SELECT id, artikelnummer, bezeichnung, kategorie, lagerbestand, mindestbestand,
           printf("%.2f", einkaufspreis) as einkaufspreis, 
           printf("%.2f", verkaufspreis) as verkaufspreis, lagerort
    FROM ersatzteile
    {where_clause}
    ORDER BY bezeichnung
    """
    
    cursor.execute(query, params)
    
    # Treeview leeren
    for item in app.ersatzteile_widgets['ersatzteile_tree'].get_children():
        app.ersatzteile_widgets['ersatzteile_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        if row[4] <= row[5]:  # lagerbestand <= mindestbestand
            app.ersatzteile_widgets['ersatzteile_tree'].insert('', 'end', values=row, tags=('low_stock',))
        else:
            app.ersatzteile_widgets['ersatzteile_tree'].insert('', 'end', values=row)
            
    app.update_status(f"{app.ersatzteile_widgets['ersatzteile_tree'].get_children().__len__()} Artikel gefiltert")

def get_selected_ersatzteil_id(app):
    """Gibt die ID des ausgewählten Ersatzteils zurück"""
    selected_items = app.ersatzteile_widgets['ersatzteile_tree'].selection()
    if not selected_items:
        return None
        
    return app.ersatzteile_widgets['ersatzteile_tree'].item(selected_items[0])['values'][0]

def show_ersatzteil_details(app, event=None):
    """Zeigt Details zum ausgewählten Ersatzteil an"""
    ersatzteil_id = get_selected_ersatzteil_id(app)
    if not ersatzteil_id:
        return
        
    bestand = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][4]
    einkaufspreis = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][6]
    
    cursor = app.conn.cursor()
    
    # Lieferantinformationen abrufen
    cursor.execute("SELECT lieferant FROM ersatzteile WHERE id = ?", (ersatzteil_id,))
    lieferant = cursor.fetchone()[0] or "Nicht angegeben"
    app.ersatzteile_widgets['artikel_lieferant_info'].config(text=lieferant)
    
    # Artikelwert berechnen
    try:
        wert = float(bestand) * float(einkaufspreis.replace(',', '.'))
        app.ersatzteile_widgets['artikel_wert_info'].config(text=f"{wert:.2f} CHF")
    except ValueError:
        app.ersatzteile_widgets['artikel_wert_info'].config(text="0.00 CHF")
    
    # Bestellstatus setzen
    mindestbestand = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][5]
    if bestand <= mindestbestand:
        app.ersatzteile_widgets['artikel_status_info'].config(text="Nachbestellung erforderlich", foreground="red")
    else:
        app.ersatzteile_widgets['artikel_status_info'].config(text="Ausreichend auf Lager", foreground="green")

def new_ersatzteil(app):
    """Erstellt ein neues Ersatzteil"""
    ersatzteildialog = ErsatzteilDialog(app.root, "Neuer Artikel", None, app.conn)
    if ersatzteildialog.result:
        app.load_ersatzteile()
        app.load_categories()
        app.update_status("Neuer Artikel angelegt")

def edit_ersatzteil(app):
    """Bearbeitet ein vorhandenes Ersatzteil"""
    ersatzteil_id = get_selected_ersatzteil_id(app)
    if not ersatzteil_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Artikel aus.")
        return
        
    ersatzteildialog = ErsatzteilDialog(app.root, "Artikel bearbeiten", ersatzteil_id, app.conn)
    if ersatzteildialog.result:
        app.load_ersatzteile()
        app.load_categories()
        show_ersatzteil_details(app)
        app.update_status("Artikeldaten aktualisiert")

def delete_ersatzteil(app):
    """Löscht ein Ersatzteil"""
    ersatzteil_id = get_selected_ersatzteil_id(app)
    if not ersatzteil_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Artikel aus.")
        return
        
    bezeichnung = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][2]
    
    # Prüfen, ob Teil in Aufträgen verwendet wird
    cursor = app.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auftrag_ersatzteile WHERE ersatzteil_id = ?", (ersatzteil_id,))
    used_count = cursor.fetchone()[0]
    
    if used_count > 0:
        messagebox.showwarning("Warnung", f"Der Artikel '{bezeichnung}' wird in {used_count} Aufträgen verwendet. Löschen nicht möglich.")
        return
        
    # Bestätigung einholen
    if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie den Artikel '{bezeichnung}' wirklich löschen?"):
        try:
            cursor.execute("DELETE FROM ersatzteile WHERE id = ?", (ersatzteil_id,))
            app.conn.commit()
            app.load_ersatzteile()
            app.load_categories()
            app.update_status(f"Artikel '{bezeichnung}' gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen des Artikels: {e}")
            app.conn.rollback()

def change_inventory(app):
    """Ändert den Lagerbestand eines Artikels"""
    ersatzteil_id = get_selected_ersatzteil_id(app)
    if not ersatzteil_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Artikel aus.")
        return
        
    bestand = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][4]
    bezeichnung = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][2]
    
    dialog = BestandsDialog(app.root, f"Bestand ändern: {bezeichnung}", ersatzteil_id, app.conn, bestand)
    if dialog.result:
        app.load_ersatzteile()
        show_ersatzteil_details(app)
        app.update_status(f"Bestand für '{bezeichnung}' aktualisiert")

def show_nachbestellliste(app):
    """Zeigt eine Liste der Artikel mit niedrigem Bestand an"""
    NachbestellDialog(app.root, "Nachbestellliste", app.conn)