#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kunden-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.kunden_dialog import KundenDialog
from dialogs.auftrags_dialog import AuftragsDialog
from dialogs.common_dialogs import KundenHistorieDialog

def create_kunden_tab(notebook, app):
    """Kunden-Tab erstellen"""
    kunden_frame = ttk.Frame(notebook)
    
    # Suchleiste
    search_frame = ttk.Frame(kunden_frame)
    search_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(search_frame, text="Suche:").pack(side="left", padx=5)
    kunden_search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=kunden_search_var, width=30)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: search_kunden(app))
    
    # Buttons
    btn_frame = ttk.Frame(kunden_frame)
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(btn_frame, text="Neuer Kunde", command=app.new_kunde).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Bearbeiten", command=app.edit_kunde).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Löschen", command=lambda: delete_kunde(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Auftrag erstellen", command=lambda: create_auftrag_for_kunde(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Auftragshistorie", command=lambda: show_kunde_history(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Aktualisieren", command=app.load_kunden).pack(side="right", padx=5)
    
    # Tabelle
    table_frame = ttk.Frame(kunden_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns = ('id', 'name', 'telefon', 'email', 'fahrzeug', 'kennzeichen')
    kunden_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    kunden_tree.heading('id', text='ID')
    kunden_tree.heading('name', text='Name')
    kunden_tree.heading('telefon', text='Telefon')
    kunden_tree.heading('email', text='E-Mail')
    kunden_tree.heading('fahrzeug', text='Fahrzeug')
    kunden_tree.heading('kennzeichen', text='Kennzeichen')
    
    kunden_tree.column('id', width=50, anchor='center')
    kunden_tree.column('name', width=150)
    kunden_tree.column('telefon', width=100)
    kunden_tree.column('email', width=150)
    kunden_tree.column('fahrzeug', width=100)
    kunden_tree.column('kennzeichen', width=100)
    
    # Scrollbars
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
        # Hervorheben der Treffer
        app.kunden_widgets['kunden_tree'].tag_configure('match', background='lightyellow')
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
        
    # Bestätigung einholen
    if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie den Kunden '{kunde_name}' wirklich löschen?"):
        try:
            cursor.execute("DELETE FROM kunden WHERE id = ?", (kunden_id,))
            app.conn.commit()
            app.load_kunden()
            app.update_status(f"Kunde '{kunde_name}' gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen des Kunden: {e}")
            app.conn.rollback()