#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisiertes Kunden-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.kunden_dialog import KundenDialog
from dialogs.auftrags_dialog import AuftragsDialog
from dialogs.common_dialogs import KundenHistorieDialog

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

def create_kunden_tab(notebook, app):
    """Kunden-Tab mit modernem Design erstellen"""
    # Hauptframe
    kunden_frame = ttk.Frame(notebook)
    
    # Custom Styles für Kunden-Tab
    style = ttk.Style()
    style.configure("Card.TFrame", background=COLORS["bg_medium"])
    style.configure("CardTitle.TLabel", 
                   background=COLORS["bg_medium"], 
                   foreground=COLORS["text_light"],
                   font=("Arial", 12, "bold"))
    
    # Hauptcontainer
    main_container = ttk.Frame(kunden_frame, style="Dashboard.TFrame")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Header mit Titel und Suchleiste
    header_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
    header_frame.pack(fill="x", pady=(0, 15))
    
    # Titel und Suche
    title_frame = ttk.Frame(header_frame, style="Dashboard.TFrame")
    title_frame.pack(side="left", anchor="w")
    
    title_label = ttk.Label(title_frame, text="Kundenverwaltung", style="DashboardTitle.TLabel")
    title_label.pack(side="left", anchor="w")
    
    # Suchbereich
    search_frame = ttk.Frame(header_frame, style="Card.TFrame")
    search_frame.pack(side="right", padx=5, pady=5, ipadx=10, ipady=5)
    
    ttk.Label(search_frame, text="Suche:", style="CardText.TLabel").pack(side="left", padx=5)
    
    # Modernes Suchfeld
    kunden_search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=kunden_search_var, width=30,
                         bg=COLORS["bg_light"], fg=COLORS["text_light"],
                         insertbackground=COLORS["text_light"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS["bg_light"],
                         highlightcolor=COLORS["accent"],
                         font=("Arial", 10))
    search_entry.pack(side="left", padx=5, ipady=4)
    search_entry.bind("<KeyRelease>", lambda event: search_kunden(app))
    
    # Aktionskarte mit Buttons
    action_card = ttk.Frame(main_container, style="Card.TFrame")
    action_card.pack(fill="x", pady=(0, 10), ipadx=10, ipady=10)
    
    ttk.Label(action_card, text="Aktionen", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    # Container für Buttons
    btn_container = ttk.Frame(action_card, style="Card.TFrame")
    btn_container.pack(fill="x", padx=15, pady=(0, 10))
    
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
    btn_neuer_kunde = ModernButton(btn_container, text="Neuer Kunde", 
                                  command=app.new_kunde, primary=True)
    btn_neuer_kunde.pack(side="left", padx=(0, 5))
    
    btn_bearbeiten = ModernButton(btn_container, text="Bearbeiten", 
                                command=app.edit_kunde)
    btn_bearbeiten.pack(side="left", padx=5)
    
    btn_loeschen = ModernButton(btn_container, text="Löschen", 
                              command=lambda: delete_kunde(app))
    btn_loeschen.pack(side="left", padx=5)
    
    btn_auftrag_erstellen = ModernButton(btn_container, text="Auftrag erstellen", 
                                       command=lambda: create_auftrag_for_kunde(app))
    btn_auftrag_erstellen.pack(side="left", padx=5)
    
    btn_historie = ModernButton(btn_container, text="Auftragshistorie", 
                             command=lambda: show_kunde_history(app))
    btn_historie.pack(side="left", padx=5)
    
    btn_aktualisieren = ModernButton(btn_container, text="Aktualisieren", 
                                   command=app.load_kunden)
    btn_aktualisieren.pack(side="right")
    
    # Container für Tabelle und Details
    content_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
    content_frame.pack(fill="both", expand=True)
    
    # Tabelle mit Kunden
    table_card = ttk.Frame(content_frame, style="Card.TFrame")
    table_card.pack(fill="both", expand=True, ipadx=10, ipady=10)
    
    ttk.Label(table_card, text="Kundenliste", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    # Tabelle für Kunden
    table_frame = ttk.Frame(table_card, style="Card.TFrame")
    table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Spalten der Tabelle
    columns = ('id', 'name', 'telefon', 'email', 'fahrzeug', 'kennzeichen')
    kunden_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
    
    # Spaltenkonfiguration
    kunden_tree.heading('id', text='ID')
    kunden_tree.heading('name', text='Name')
    kunden_tree.heading('telefon', text='Telefon')
    kunden_tree.heading('email', text='E-Mail')
    kunden_tree.heading('fahrzeug', text='Fahrzeug')
    kunden_tree.heading('kennzeichen', text='Kennzeichen')
    
    kunden_tree.column('id', width=40, anchor='center')
    kunden_tree.column('name', width=150)
    kunden_tree.column('telefon', width=100)
    kunden_tree.column('email', width=150)
    kunden_tree.column('fahrzeug', width=120)
    kunden_tree.column('kennzeichen', width=100)
    
    # Scrollbars mit modernem Aussehen
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=kunden_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=kunden_tree.xview)
    kunden_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    kunden_tree.pack(fill="both", expand=True)
    
    # Doppelklick zum Bearbeiten
    kunden_tree.bind("<Double-1>", lambda event: app.edit_kunde())
    
    # Widget-Dictionary erstellen
    widgets = {
        'kunden_search_var': kunden_search_var,
        'kunden_tree': kunden_tree
    }
    
    return kunden_frame, widgets

def load_kunden_data(app):
    """Lädt Kundendaten aus der Datenbank"""
    cursor = app.conn.cursor()
    cursor.execute("""
    SELECT id, vorname || ' ' || nachname as name, telefon, email, fahrzeug_typ, kennzeichen 
    FROM kunden
    ORDER BY name
    """)
    
    # Treeview leeren
    for item in app.kunden_widgets['kunden_tree'].get_children():
        app.kunden_widgets['kunden_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        app.kunden_widgets['kunden_tree'].insert('', 'end', values=row)
        
    app.update_status(f"{app.kunden_widgets['kunden_tree'].get_children().__len__()} Kunden geladen")

def search_kunden(app):
    """Durchsucht die Kundenliste nach dem Suchbegriff"""
    search_term = app.kunden_widgets['kunden_search_var'].get().lower()
    
    for item in app.kunden_widgets['kunden_tree'].get_children():
        values = app.kunden_widgets['kunden_tree'].item(item)['values']
        # Suche in Name, Telefon, Email, Fahrzeug und Kennzeichen
        if (search_term in str(values[1]).lower() or  # Name
            search_term in str(values[2]).lower() or  # Telefon
            search_term in str(values[3]).lower() or  # Email
            search_term in str(values[4]).lower() or  # Fahrzeug
            search_term in str(values[5]).lower()):   # Kennzeichen
            app.kunden_widgets['kunden_tree'].item(item, tags=('match',))
        else:
            app.kunden_widgets['kunden_tree'].item(item, tags=('',))
            
    if search_term:
        # Hervorheben der Treffer mit modernerer Farbe
        app.kunden_widgets['kunden_tree'].tag_configure('match', background=COLORS["accent"], foreground=COLORS["bg_dark"])
    else:
        # Alle anzeigen, wenn Suchfeld leer
        for item in app.kunden_widgets['kunden_tree'].get_children():
            app.kunden_widgets['kunden_tree'].item(item, tags=('',))

def get_selected_kunden_id(app):
    """Gibt die ID des ausgewählten Kunden zurück"""
    selected_items = app.kunden_widgets['kunden_tree'].selection()
    if not selected_items:
        return None
        
    return app.kunden_widgets['kunden_tree'].item(selected_items[0])['values'][0]

def create_auftrag_for_kunde(app):
    """Erstellt einen Auftrag für den ausgewählten Kunden"""
    kunden_id = get_selected_kunden_id(app)
    if not kunden_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Kunden aus.")
        return
        
    auftragsdialog = AuftragsDialog(app.root, "Neuer Auftrag", None, app.conn, kunden_id)
    if auftragsdialog.result:
        app.load_auftraege()
        app.update_status("Neuer Auftrag angelegt")
        
        # Zum Aufträge-Tab wechseln
        app.notebook.select(2)  # Index 2 = Aufträge-Tab

def show_kunde_history(app):
    """Zeigt die Auftragshistorie eines Kunden an"""
    kunden_id = get_selected_kunden_id(app)
    if not kunden_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Kunden aus.")
        return
        
    kunde_name = app.kunden_widgets['kunden_tree'].item(app.kunden_widgets['kunden_tree'].selection()[0])['values'][1]
    
    # Kundendialog mit Auftragshistorie anzeigen
    KundenHistorieDialog(app.root, f"Auftragshistorie: {kunde_name}", kunden_id, app.conn)

def delete_kunde(app):
    """Löscht einen Kunden"""
    kunden_id = get_selected_kunden_id(app)
    if not kunden_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Kunden aus.")
        return
        
    kunde_name = app.kunden_widgets['kunden_tree'].item(app.kunden_widgets['kunden_tree'].selection()[0])['values'][1]
    
    # Prüfen, ob noch offene Aufträge existieren
    cursor = app.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auftraege WHERE kunden_id = ? AND status != 'Abgeschlossen'", (kunden_id,))
    offene_auftraege = cursor.fetchone()[0]
    
    if offene_auftraege > 0:
        messagebox.showwarning("Warnung", f"Der Kunde '{kunde_name}' hat noch {offene_auftraege} offene Aufträge. Löschen nicht möglich.")
        return
        
    # Bestätigung einholen mit modernem Design
    confirmation = messagebox.askyesno(
        "Löschen bestätigen", 
        f"Möchten Sie den Kunden '{kunde_name}' wirklich löschen?",
        icon="warning"
    )
    
    if confirmation:
        try:
            cursor.execute("DELETE FROM kunden WHERE id = ?", (kunden_id,))
            app.conn.commit()
            app.load_kunden()
            app.update_status(f"Kunde '{kunde_name}' gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen des Kunden: {e}")
            app.conn.rollback()