#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisiertes Ersatzteile-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.ersatzteil_dialog import ErsatzteilDialog
from dialogs.bestand_dialog import BestandsDialog
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

def create_ersatzteile_tab(notebook, app):
    """Ersatzteile-Tab mit modernem Design erstellen"""
    # Hauptframe mit dunklem Hintergrund
    ersatzteile_frame = ttk.Frame(notebook)
    
    # Custom Styles für Ersatzteile-Tab
    style = ttk.Style()
    style.configure("Card.TFrame", background=COLORS["bg_medium"])
    style.configure("CardTitle.TLabel", 
                   background=COLORS["bg_medium"], 
                   foreground=COLORS["text_light"],
                   font=("Arial", 12, "bold"))
    
    # Hauptcontainer
    main_container = ttk.Frame(ersatzteile_frame, style="Dashboard.TFrame")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Header mit Titel und Suchleiste
    header_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
    header_frame.pack(fill="x", pady=(0, 15))
    
    # Titel und Filter in separaten Frames
    title_frame = ttk.Frame(header_frame, style="Dashboard.TFrame")
    title_frame.pack(side="left", anchor="w")
    
    title_label = ttk.Label(title_frame, text="Ersatzteile & Lagerbestand", style="DashboardTitle.TLabel")
    title_label.pack(side="left", anchor="w")
    
    # Filter- und Suchbereich
    filter_frame = ttk.Frame(header_frame, style="Card.TFrame")
    filter_frame.pack(side="right", padx=5, pady=5, ipadx=10, ipady=5)
    
    # Suchfeld mit modernem Design
    search_container = ttk.Frame(filter_frame, style="Card.TFrame")
    search_container.pack(side="left", padx=10)
    
    ttk.Label(search_container, text="Suche:", style="CardText.TLabel").pack(side="left", padx=5)
    ersatzteile_search_var = tk.StringVar()
    
    # Eigenes Entry-Widget für besseres Design
    search_entry = tk.Entry(search_container, textvariable=ersatzteile_search_var, width=25,
                          bg=COLORS["bg_light"], fg=COLORS["text_light"],
                          insertbackground=COLORS["text_light"],
                          relief="flat", highlightthickness=1,
                          highlightbackground=COLORS["bg_light"],
                          highlightcolor=COLORS["accent"],
                          font=("Arial", 10))
    search_entry.pack(side="left", padx=5, ipady=4)
    search_entry.bind("<KeyRelease>", lambda event: search_ersatzteile(app))
    
    # Kategoriefilter
    category_container = ttk.Frame(filter_frame, style="Card.TFrame")
    category_container.pack(side="left", padx=10)
    
    ttk.Label(category_container, text="Kategorie:", style="CardText.TLabel").pack(side="left", padx=5)
    kategorie_filter_var = tk.StringVar(value="Alle")
    
    # Combo-Box-Design
    kategorie_combo = ttk.Combobox(category_container, textvariable=kategorie_filter_var, width=15,
                                 values=["Alle"])
    kategorie_combo.pack(side="left", padx=5)
    kategorie_combo.bind("<<ComboboxSelected>>", lambda event: filter_ersatzteile(app))
    
    # Checkbox für Artikel mit niedrigem Bestand
    low_stock_container = ttk.Frame(filter_frame, style="Card.TFrame")
    low_stock_container.pack(side="left", padx=10)
    
    low_stock_var = tk.BooleanVar()
    
    # Moderne Checkbox
    low_stock_check = ttk.Checkbutton(low_stock_container, text="Nur Artikel mit niedrigem Bestand", 
                                    variable=low_stock_var, style="TCheckbutton",
                                    command=lambda: filter_ersatzteile(app))
    low_stock_check.pack(side="left", padx=5)
    
    # Buttons-Bereich
    content_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
    content_frame.pack(fill="both", expand=True)
    
    # Linke Seite - Aktionskarte und Detailkarte
    left_column = ttk.Frame(content_frame, style="Dashboard.TFrame")
    left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Aktionskarte
    action_card = ttk.Frame(left_column, style="Card.TFrame")
    action_card.pack(fill="x", pady=(0, 10), ipadx=10, ipady=10)
    
    ttk.Label(action_card, text="Aktionen", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    # Container für Buttons
    btn_container = ttk.Frame(action_card, style="Card.TFrame")
    btn_container.pack(fill="x", padx=15, pady=(0, 15))
    
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
    
    # Buttons für Aktionen
    btn_neuer_artikel = ModernButton(btn_container, text="Neuer Artikel", 
                                    command=lambda: new_ersatzteil(app), primary=True)
    btn_neuer_artikel.pack(side="left", padx=(0, 5))
    
    btn_bearbeiten = ModernButton(btn_container, text="Bearbeiten", 
                                command=lambda: edit_ersatzteil(app))
    btn_bearbeiten.pack(side="left", padx=5)
    
    btn_loeschen = ModernButton(btn_container, text="Löschen", 
                              command=lambda: delete_ersatzteil(app))
    btn_loeschen.pack(side="left", padx=5)
    
    btn_bestand_aendern = ModernButton(btn_container, text="Bestand ändern", 
                                     command=lambda: change_inventory(app))
    btn_bestand_aendern.pack(side="left", padx=5)
    
    btn_nachbestellliste = ModernButton(btn_container, text="Nachbestellliste", 
                                       command=lambda: show_nachbestellliste(app))
    btn_nachbestellliste.pack(side="left", padx=5)
    
    btn_aktualisieren = ModernButton(btn_container, text="Aktualisieren", 
                                    command=lambda: app.load_ersatzteile())
    btn_aktualisieren.pack(side="right")
    
    # Tabelle mit Ersatzteilen
    table_card = ttk.Frame(left_column, style="Card.TFrame")
    table_card.pack(fill="both", expand=True, ipadx=10, ipady=10)
    
    ttk.Label(table_card, text="Ersatzteilbestand", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    # Tabelle für Ersatzteile
    table_frame = ttk.Frame(table_card, style="Card.TFrame")
    table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Spalten der Treeview
    columns = ('id', 'artikelnr', 'bezeichnung', 'kategorie', 'lagerbestand', 'mindestbestand', 
              'einkaufspreis', 'verkaufspreis', 'lagerort', 'einheit')
    ersatzteile_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")

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
        
    # Scrollbars mit modernem Aussehen
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=ersatzteile_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=ersatzteile_tree.xview)
    ersatzteile_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    ersatzteile_tree.pack(fill="both", expand=True)
    
    # Rechte Seite - Detailkarte
    right_column = ttk.Frame(content_frame, style="Dashboard.TFrame", width=300)
    right_column.pack(side="right", fill="y", padx=(10, 0))
    right_column.pack_propagate(False)  # Verhindert, dass der Frame sich an Inhalte anpasst
    
    # Detailkarte
    detail_card = ttk.Frame(right_column, style="Card.TFrame")
    detail_card.pack(fill="both", expand=True, ipadx=10, ipady=10)
    
    ttk.Label(detail_card, text="Artikeldetails", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    # Placeholder für "Bitte Artikel auswählen"
    placeholder_frame = ttk.Frame(detail_card, style="Card.TFrame")
    placeholder_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    placeholder_label = ttk.Label(placeholder_frame, text="Bitte wählen Sie einen Artikel aus\nder Tabelle aus, um Details zu sehen.",
                                style="CardText.TLabel", justify="center")
    placeholder_label.pack(expand=True)
    
    # Details-Frame (wird später angezeigt)
    details_frame = ttk.Frame(detail_card, style="Card.TFrame")
    
    # Artikelwert
    wert_frame = ttk.Frame(details_frame, style="Card.TFrame")
    wert_frame.pack(fill="x", pady=10)
    
    ttk.Label(wert_frame, text="Artikelwert:", style="CardText.TLabel").pack(side="left", padx=5)
    artikel_wert_info = ttk.Label(wert_frame, text="-", style="CardContent.TLabel")
    artikel_wert_info.pack(side="left", padx=5)
    
    # Lieferant
    lieferant_frame = ttk.Frame(details_frame, style="Card.TFrame")
    lieferant_frame.pack(fill="x", pady=10)
    
    ttk.Label(lieferant_frame, text="Lieferant:", style="CardText.TLabel").pack(side="left", padx=5)
    artikel_lieferant_info = ttk.Label(lieferant_frame, text="-", style="CardText.TLabel")
    artikel_lieferant_info.pack(side="left", padx=5)
    
    # Bestellstatus
    status_frame = ttk.Frame(details_frame, style="Card.TFrame")
    status_frame.pack(fill="x", pady=10)
    
    ttk.Label(status_frame, text="Bestellstatus:", style="CardText.TLabel").pack(side="left", padx=5)
    artikel_status_info = ttk.Label(status_frame, text="-", style="CardText.TLabel")
    artikel_status_info.pack(side="left", padx=5)
    
    # Bestandsentwicklung (Platzhalter für ein Diagramm)
    chart_frame = ttk.Frame(details_frame, style="Card.TFrame")
    chart_frame.pack(fill="both", expand=True, pady=10)
    
    ttk.Label(chart_frame, text="Bestandsentwicklung:", style="CardText.TLabel").pack(anchor="w", padx=5, pady=5)
    
    # Hier könnte in Zukunft eine kleine Bestandsverlaufs-Grafik angezeigt werden
    chart_placeholder = ttk.Label(chart_frame, text="Bestandsverlauf\n(in Entwicklung)", 
                               style="CardText.TLabel", justify="center")
    chart_placeholder.pack(fill="both", expand=True, pady=20)
    
    # Event-Handler für Tabellenauswahl
    def on_tree_select(event):
        """Zeigt Details zum ausgewählten Artikel und tauscht die Frames"""
        selected_items = ersatzteile_tree.selection()
        if selected_items:
            # Details anzeigen
            placeholder_frame.pack_forget()
            details_frame.pack(fill="both", expand=True, padx=15, pady=10)
            show_ersatzteil_details(app)
        else:
            # Placeholder anzeigen
            details_frame.pack_forget()
            placeholder_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    ersatzteile_tree.bind("<<TreeviewSelect>>", on_tree_select)
    
    # Doppelklick zum Bearbeiten
    ersatzteile_tree.bind("<Double-1>", lambda event: edit_ersatzteil(app))

    # Widget-Dictionary erstellen
    widgets = {
        'ersatzteile_search_var': ersatzteile_search_var,
        'kategorie_filter_var': kategorie_filter_var,
        'kategorie_combo': kategorie_combo,
        'low_stock_var': low_stock_var,
        'ersatzteile_tree': ersatzteile_tree,
        'artikel_wert_info': artikel_wert_info,
        'artikel_lieferant_info': artikel_lieferant_info,
        'artikel_status_info': artikel_status_info,
        'placeholder_frame': placeholder_frame,
        'details_frame': details_frame
    }
    
    return ersatzteile_frame, widgets

def load_ersatzteile_data(app):
    """Lädt Ersatzteildaten aus der Datenbank mit modernem Styling"""
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
            
    # Tag für niedrigen Bestand erstellen mit modernerer Farbe
    app.ersatzteile_widgets['ersatzteile_tree'].tag_configure('low_stock', background=COLORS["warning"], foreground=COLORS["bg_dark"])
        
    app.update_status(f"{app.ersatzteile_widgets['ersatzteile_tree'].get_children().__len__()} Artikel geladen")
    
    # Details zurücksetzen - Zeige Platzhalter
    if 'placeholder_frame' in app.ersatzteile_widgets and 'details_frame' in app.ersatzteile_widgets:
        app.ersatzteile_widgets['details_frame'].pack_forget()
        app.ersatzteile_widgets['placeholder_frame'].pack(fill="both", expand=True, padx=15, pady=10)

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
        # Hervorheben der Treffer mit modernerer Farbe
        app.ersatzteile_widgets['ersatzteile_tree'].tag_configure('match', background=COLORS["accent"], foreground=COLORS["bg_dark"])
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
           printf("%.2f", verkaufspreis) as verkaufspreis, lagerort, einheit
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
    
    # Bestellstatus setzen mit modernen Farben
    mindestbestand = app.ersatzteile_widgets['ersatzteile_tree'].item(app.ersatzteile_widgets['ersatzteile_tree'].selection()[0])['values'][5]
    if bestand <= mindestbestand:
        app.ersatzteile_widgets['artikel_status_info'].config(
            text="Nachbestellung erforderlich", 
            foreground=COLORS["danger"]
        )
    else:
        app.ersatzteile_widgets['artikel_status_info'].config(
            text="Ausreichend auf Lager", 
            foreground=COLORS["success"]
        )

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
        
    # Bestätigung einholen mit modernem Design
    confirmation = messagebox.askyesno(
        "Löschen bestätigen", 
        f"Möchten Sie den Artikel '{bezeichnung}' wirklich löschen?",
        icon="warning"
    )
    
    if confirmation:
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