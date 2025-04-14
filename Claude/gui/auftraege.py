#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aufträge-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

from dialogs.auftrags_dialog import AuftragsDialog
from dialogs.teile_dialog import TeileAuswahlDialog
from dialogs.rechnungs_dialog import RechnungsDialog

def create_auftraege_tab(notebook, app):
    """Aufträge-Tab erstellen"""
    auftraege_frame = ttk.Frame(notebook)
    
    # Suchleiste und Filter
    filter_frame = ttk.Frame(auftraege_frame)
    filter_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(filter_frame, text="Suche:").grid(row=0, column=0, padx=5)
    auftraege_search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=auftraege_search_var, width=20)
    search_entry.grid(row=0, column=1, padx=5)
    search_entry.bind("<KeyRelease>", lambda event: search_auftraege(app))
    
    ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, padx=5)
    status_filter_var = tk.StringVar(value="Alle")
    status_combo = ttk.Combobox(filter_frame, textvariable=status_filter_var, width=15, 
                               values=["Alle", "Offen", "In Bearbeitung", "Warten auf Teile", "Abgeschlossen"])
    status_combo.grid(row=0, column=3, padx=5)
    status_combo.bind("<<ComboboxSelected>>", lambda event: filter_auftraege(app))
    
    # Buttons
    btn_frame = ttk.Frame(auftraege_frame)
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(btn_frame, text="Neuer Auftrag", command=app.new_auftrag).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Bearbeiten", command=lambda: edit_auftrag(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Teile hinzufügen", command=lambda: add_parts_to_auftrag(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Status ändern", command=lambda: change_auftrag_status(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Rechnung erstellen", command=lambda: create_invoice_for_auftrag(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Löschen", command=lambda: delete_auftrag(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Aktualisieren", command=app.load_auftraege).pack(side="right", padx=5)
    
    # Tabelle
    table_frame = ttk.Frame(auftraege_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns = ('id', 'kunde', 'beschreibung', 'status', 'prioritaet', 'datum', 'arbeitszeit')
    auftraege_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    auftraege_tree.heading('id', text='ID')
    auftraege_tree.heading('kunde', text='Kunde')
    auftraege_tree.heading('beschreibung', text='Beschreibung')
    auftraege_tree.heading('status', text='Status')
    auftraege_tree.heading('prioritaet', text='Priorität')
    auftraege_tree.heading('datum', text='Erstelldatum')
    auftraege_tree.heading('arbeitszeit', text='Arbeitszeit (h)')
    
    auftraege_tree.column('id', width=50, anchor='center')
    auftraege_tree.column('kunde', width=150)
    auftraege_tree.column('beschreibung', width=200)
    auftraege_tree.column('status', width=100)
    auftraege_tree.column('prioritaet', width=80)
    auftraege_tree.column('datum', width=100)
    auftraege_tree.column('arbeitszeit', width=100, anchor='center')
    
    # Scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=auftraege_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=auftraege_tree.xview)
    auftraege_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    auftraege_tree.pack(fill="both", expand=True)
    
    # Auftragsdetails unten anzeigen
    details_frame = ttk.LabelFrame(auftraege_frame, text="Auftragsdetails")
    details_frame.pack(fill="x", padx=10, pady=10)
    
    # Spalten für Details
    left_details = ttk.Frame(details_frame)
    left_details.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
    
    right_details = ttk.Frame(details_frame)
    right_details.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
    
    # Linke Spalte - Kundeninfos
    ttk.Label(left_details, text="Kundeninformationen:").grid(row=0, column=0, sticky="w", pady=2)
    auftrag_kunde_info = ttk.Label(left_details, text="-")
    auftrag_kunde_info.grid(row=1, column=0, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Fahrzeug:").grid(row=2, column=0, sticky="w", pady=2)
    auftrag_fahrzeug_info = ttk.Label(left_details, text="-")
    auftrag_fahrzeug_info.grid(row=3, column=0, sticky="w", pady=2)
    
    # Rechte Spalte - Auftragsinfos und verbaute Teile
    ttk.Label(right_details, text="Verwendete Ersatzteile:").grid(row=0, column=0, sticky="w", pady=2)
    
    parts_frame = ttk.Frame(right_details)
    parts_frame.grid(row=1, column=0, sticky="w", pady=2)
    
    auftrag_parts_tree = ttk.Treeview(parts_frame, columns=('name', 'menge', 'preis'), show='headings', height=4)
    auftrag_parts_tree.heading('name', text='Artikelname')
    auftrag_parts_tree.heading('menge', text='Menge')
    auftrag_parts_tree.heading('preis', text='Einzelpreis')
    
    auftrag_parts_tree.column('name', width=200)
    auftrag_parts_tree.column('menge', width=50, anchor='center')
    auftrag_parts_tree.column('preis', width=80, anchor='e')
    
    parts_vsb = ttk.Scrollbar(parts_frame, orient="vertical", command=auftrag_parts_tree.yview)
    auftrag_parts_tree.configure(yscrollcommand=parts_vsb.set)
    
    parts_vsb.pack(side="right", fill="y")
    auftrag_parts_tree.pack(side="left", fill="both", expand=True)
    
    # Notizen
    ttk.Label(details_frame, text="Notizen:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
    auftrag_notizen = tk.Text(details_frame, height=3, width=50)
    auftrag_notizen.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
    
    ttk.Button(details_frame, text="Notizen speichern", command=lambda: save_auftrag_notizen(app)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    
    # Event-Handler für Tabellenauswahl
    auftraege_tree.bind("<<TreeviewSelect>>", lambda event: show_auftrag_details(app))
    
    # Doppelklick zum Bearbeiten
    auftraege_tree.bind("<Double-1>", lambda event: edit_auftrag(app))

    # Widget-Dictionary erstellen
    widgets = {
        'auftraege_search_var': auftraege_search_var,
        'status_filter_var': status_filter_var,
        'auftraege_tree': auftraege_tree,
        'auftrag_kunde_info': auftrag_kunde_info,
        'auftrag_fahrzeug_info': auftrag_fahrzeug_info,
        'auftrag_parts_tree': auftrag_parts_tree,
        'auftrag_notizen': auftrag_notizen,
    }
    
    return auftraege_frame, widgets

def load_auftraege_data(app):
    """Lädt Auftragsdaten aus der Datenbank"""
    cursor = app.conn.cursor()
    cursor.execute("""
    SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.beschreibung, a.status, a.prioritaet,
           strftime('%d.%m.%Y', a.erstellt_am) as datum, a.arbeitszeit
    FROM auftraege a
    LEFT JOIN kunden k ON a.kunden_id = k.id
    ORDER BY a.erstellt_am DESC
    """)
    
    # Treeview leeren
    for item in app.auftraege_widgets['auftraege_tree'].get_children():
        app.auftraege_widgets['auftraege_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        app.auftraege_widgets['auftraege_tree'].insert('', 'end', values=row)
        
    app.update_status(f"{app.auftraege_widgets['auftraege_tree'].get_children().__len__()} Aufträge geladen")

def search_auftraege(app):
    """Durchsucht die Auftragsliste nach dem Suchbegriff"""
    search_term = app.auftraege_widgets['auftraege_search_var'].get().lower()
    
    for item in app.auftraege_widgets['auftraege_tree'].get_children():
        values = app.auftraege_widgets['auftraege_tree'].item(item)['values']
        # Suche in Kunde, Beschreibung, Status und Priorität
        if (search_term in str(values[1]).lower() or  # Kunde
            search_term in str(values[2]).lower() or  # Beschreibung
            search_term in str(values[3]).lower() or  # Status
            search_term in str(values[4]).lower()):   # Priorität
            app.auftraege_widgets['auftraege_tree'].item(item, tags=('match',))
        else:
            app.auftraege_widgets['auftraege_tree'].item(item, tags=('',))
            
    if search_term:
        # Hervorheben der Treffer
        app.auftraege_widgets['auftraege_tree'].tag_configure('match', background='lightyellow')
    else:
        # Alle anzeigen, wenn Suchfeld leer
        filter_auftraege(app)

def filter_auftraege(app):
    """Filtert Aufträge nach Status"""
    status_filter = app.auftraege_widgets['status_filter_var'].get()
    
    cursor = app.conn.cursor()
    
    if status_filter == "Alle":
        load_auftraege_data(app)
    else:
        cursor.execute("""
        SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.beschreibung, a.status, a.prioritaet,
               strftime('%d.%m.%Y', a.erstellt_am) as datum, a.arbeitszeit
        FROM auftraege a
        LEFT JOIN kunden k ON a.kunden_id = k.id
        WHERE a.status = ?
        ORDER BY a.erstellt_am DESC
        """, (status_filter,))
        
        # Treeview leeren
        for item in app.auftraege_widgets['auftraege_tree'].get_children():
            app.auftraege_widgets['auftraege_tree'].delete(item)
            
        # Daten einfügen
        for row in cursor.fetchall():
            app.auftraege_widgets['auftraege_tree'].insert('', 'end', values=row)
            
    app.update_status(f"{app.auftraege_widgets['auftraege_tree'].get_children().__len__()} Aufträge gefiltert")

def get_selected_auftrag_id(app):
    """Gibt die ID des ausgewählten Auftrags zurück"""
    selected_items = app.auftraege_widgets['auftraege_tree'].selection()
    if not selected_items:
        return None
        
    return app.auftraege_widgets['auftraege_tree'].item(selected_items[0])['values'][0]

def show_auftrag_details(app):
    """Zeigt Details zum ausgewählten Auftrag an"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        return
    
    # Instanzvariable setzen, um die Auftrag-ID zu speichern
    app.current_auftrag_id = auftrag_id
    
    cursor = app.conn.cursor()
    
    # Kundeninformationen abrufen
    cursor.execute("""
    SELECT k.vorname || ' ' || k.nachname as name, k.telefon, k.email
    FROM auftraege a
    JOIN kunden k ON a.kunden_id = k.id
    WHERE a.id = ?
    """, (auftrag_id,))
    
    kunde_info = cursor.fetchone()
    if kunde_info:
        app.auftraege_widgets['auftrag_kunde_info'].config(text=f"{kunde_info[0]}\nTel: {kunde_info[1]}\nE-Mail: {kunde_info[2]}")
    
    # Fahrzeuginformationen abrufen
    cursor.execute("""
    SELECT k.fahrzeug_typ, k.kennzeichen, k.fahrgestellnummer
    FROM auftraege a
    JOIN kunden k ON a.kunden_id = k.id
    WHERE a.id = ?
    """, (auftrag_id,))
    
    fahrzeug_info = cursor.fetchone()
    if fahrzeug_info:
        app.auftraege_widgets['auftrag_fahrzeug_info'].config(text=f"{fahrzeug_info[0]}\nKennzeichen: {fahrzeug_info[1]}\nFIN: {fahrzeug_info[2]}")
    
    # Verwendete Ersatzteile abrufen
    cursor.execute("""
    SELECT e.bezeichnung, ae.menge, printf("%.2f", ae.einzelpreis) as preis
    FROM auftrag_ersatzteile ae
    JOIN ersatzteile e ON ae.ersatzteil_id = e.id
    WHERE ae.auftrag_id = ?
    """, (auftrag_id,))
    
    # Ersatzteile-Tabelle leeren
    for item in app.auftraege_widgets['auftrag_parts_tree'].get_children():
        app.auftraege_widgets['auftrag_parts_tree'].delete(item)
        
    # Ersatzteile einfügen
    for row in cursor.fetchall():
        app.auftraege_widgets['auftrag_parts_tree'].insert('', 'end', values=row)
    
    # Notizen abrufen
    cursor.execute("SELECT notizen FROM auftraege WHERE id = ?", (auftrag_id,))
    notizen = cursor.fetchone()[0] or ""
    
    # Notizen-Textfeld aktualisieren
    app.auftraege_widgets['auftrag_notizen'].delete(1.0, tk.END)
    app.auftraege_widgets['auftrag_notizen'].insert(tk.END, notizen)

def edit_auftrag(app):
    """Bearbeitet einen vorhandenen Auftrag"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    auftragsdialog = AuftragsDialog(app.root, "Auftrag bearbeiten", auftrag_id, app.conn)
    if auftragsdialog.result:
        app.load_auftraege()
        show_auftrag_details(app)
        app.update_status("Auftragsdaten aktualisiert")

def delete_auftrag(app):
    """Löscht einen Auftrag"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    auftrag_desc = app.auftraege_widgets['auftraege_tree'].item(app.auftraege_widgets['auftraege_tree'].selection()[0])['values'][2]
    
    # Prüfen, ob bereits eine Rechnung existiert
    cursor = app.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rechnungen WHERE auftrag_id = ?", (auftrag_id,))
    hat_rechnung = cursor.fetchone()[0] > 0
    
    if hat_rechnung:
        messagebox.showwarning("Warnung", f"Für den Auftrag existiert bereits eine Rechnung. Löschen nicht möglich.")
        return
        
    # Bestätigung einholen
    if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie den Auftrag '{auftrag_desc}' wirklich löschen?"):
        try:
            # Verknüpfte Ersatzteile löschen
            cursor.execute("DELETE FROM auftrag_ersatzteile WHERE auftrag_id = ?", (auftrag_id,))
            # Auftrag löschen
            cursor.execute("DELETE FROM auftraege WHERE id = ?", (auftrag_id,))
            app.conn.commit()
            app.load_auftraege()
            app.update_status(f"Auftrag '{auftrag_desc}' gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen des Auftrags: {e}")
            app.conn.rollback()

def add_parts_to_auftrag(app):
    """Fügt Ersatzteile zu einem Auftrag hinzu"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    # Dialog zum Hinzufügen von Teilen
    teile_dialog = TeileAuswahlDialog(app.root, "Teile hinzufügen", auftrag_id, app.conn)
    if teile_dialog.result:
        show_auftrag_details(app)
        app.update_status("Teile zum Auftrag hinzugefügt")

def change_auftrag_status(app):
    """Ändert den Status eines Auftrags"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    aktueller_status = app.auftraege_widgets['auftraege_tree'].item(app.auftraege_widgets['auftraege_tree'].selection()[0])['values'][3]
    
    # Statusauswahl
    status_options = ["Offen", "In Bearbeitung", "Warten auf Teile", "Abgeschlossen"]
    new_status = simpledialog.askstring(
        "Status ändern",
        "Neuer Status:",
        initialvalue=aktueller_status,
        parent=app.root
    )
    
    if new_status and new_status in status_options:
        try:
            cursor = app.conn.cursor()
            
            # Bei Abschluss das Abschlussdatum setzen
            if new_status == "Abgeschlossen":
                cursor.execute(
                    "UPDATE auftraege SET status = ?, abgeschlossen_am = datetime('now') WHERE id = ?",
                    (new_status, auftrag_id)
                )
            else:
                cursor.execute(
                    "UPDATE auftraege SET status = ? WHERE id = ?",
                    (new_status, auftrag_id)
                )
                
            app.conn.commit()
            app.load_auftraege()
            app.update_status(f"Auftragsstatus auf '{new_status}' geändert")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Ändern des Status: {e}")
            app.conn.rollback()

def save_auftrag_notizen(app):
    """Speichert Notizen zu einem Auftrag"""
    try:
        # Statt tag_cget die gespeicherte Instanzvariable verwenden
        auftrag_id = app.current_auftrag_id
        if not auftrag_id:
            messagebox.showinfo("Information", "Bitte wählen Sie zuerst einen Auftrag aus.")
            return
            
        notizen = app.auftraege_widgets['auftrag_notizen'].get(1.0, tk.END).strip()
        
        cursor = app.conn.cursor()
        cursor.execute("UPDATE auftraege SET notizen = ? WHERE id = ?", (notizen, auftrag_id))
        app.conn.commit()
        app.update_status("Notizen gespeichert")
    except Exception as e:
        messagebox.showinfo("Fehler", f"Fehler beim Speichern der Notizen: {e}")

def create_invoice_for_auftrag(app):
    """Erstellt eine Rechnung für den ausgewählten Auftrag"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    # Prüfen, ob der Auftrag abgeschlossen ist
    cursor = app.conn.cursor()
    cursor.execute("SELECT status FROM auftraege WHERE id = ?", (auftrag_id,))
    status = cursor.fetchone()[0]
    
    if status != "Abgeschlossen":
        if not messagebox.askyesno("Warnung", "Der Auftrag ist noch nicht abgeschlossen. Möchten Sie dennoch eine Rechnung erstellen?"):
            return
    
    # Prüfen, ob bereits eine Rechnung existiert
    cursor.execute("SELECT id FROM rechnungen WHERE auftrag_id = ?", (auftrag_id,))
    existing_invoice = cursor.fetchone()
    
    if existing_invoice:
        messagebox.showinfo("Information", "Für diesen Auftrag existiert bereits eine Rechnung.")
        # Zur Rechnung springen
        app.notebook.select(4)  # Index 4 = Rechnungen-Tab
        
        # Rechnung in der Tabelle suchen und auswählen
        for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
            values = app.rechnungen_widgets['rechnungen_tree'].item(item)['values']
            if values[0] == existing_invoice[0]:
                app.rechnungen_widgets['rechnungen_tree'].selection_set(item)
                app.rechnungen_widgets['rechnungen_tree'].see(item)
                app.rechnungen_widgets['show_rechnung_details'](None)
                break
                
        return
        
    # Dialog zur Rechnungserstellung
    rechnungsdialog = RechnungsDialog(app.root, "Neue Rechnung", None, app.conn, auftrag_id)
    if rechnungsdialog.result:
        app.load_rechnungen()
        app.update_status("Neue Rechnung erstellt")
        
        # Zum Rechnungen-Tab wechseln
        app.notebook.select(4)  # Index 4 = Rechnungen-Tab