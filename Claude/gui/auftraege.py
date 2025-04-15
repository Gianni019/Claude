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
    """Aufträge-Tab mit verbesserter Benutzeroberfläche erstellen"""
    auftraege_frame = ttk.Frame(notebook)
    
    # Horizontale Aufteilung in zwei Frames (links: Tabelle, rechts: Detailansicht)
    paned_window = ttk.PanedWindow(auftraege_frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Linker Frame für die Liste der Aufträge
    left_frame = ttk.Frame(paned_window)
    paned_window.add(left_frame, weight=1)
    
    # Rechter Frame für die Detailansicht und Bearbeitung
    right_frame = ttk.Frame(paned_window)
    paned_window.add(right_frame, weight=2)
    
    # Suchleiste und Filter im linken Frame
    filter_frame = ttk.Frame(left_frame)
    filter_frame.pack(fill="x", padx=5, pady=5)
    
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
    
    # Buttons im linken Frame
    btn_frame = ttk.Frame(left_frame)
    btn_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Button(btn_frame, text="Neuer Auftrag", command=app.new_auftrag).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Löschen", command=lambda: delete_auftrag(app)).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="Aktualisieren", command=app.load_auftraege).pack(side="right", padx=2)
    
    # Tabelle im linken Frame
    table_frame = ttk.Frame(left_frame)
    table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    columns = ('id', 'kunde', 'status', 'datum')  # Reduzierte Spalten für bessere Übersicht
    auftraege_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    auftraege_tree.heading('id', text='ID')
    auftraege_tree.heading('kunde', text='Kunde')
    auftraege_tree.heading('status', text='Status')
    auftraege_tree.heading('datum', text='Erstelldatum')
    
    auftraege_tree.column('id', width=50, anchor='center')
    auftraege_tree.column('kunde', width=150)
    auftraege_tree.column('status', width=100)
    auftraege_tree.column('datum', width=100)
    
    # Scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=auftraege_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=auftraege_tree.xview)
    auftraege_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    auftraege_tree.pack(fill="both", expand=True)
    
    #----------------------------------------------------------------------------------
    # RECHTER FRAME - DETAILANSICHT UND BEARBEITUNG
    #----------------------------------------------------------------------------------
    
    # Hinweistext, wenn kein Auftrag ausgewählt ist
    no_selection_label = ttk.Label(right_frame, text="Bitte wählen Sie einen Auftrag aus der Liste aus, oder erstellen Sie einen neuen Auftrag.",
                                 font=("Arial", 11), foreground="gray")
    no_selection_label.pack(fill="both", expand=True, padx=20, pady=50)
    
    # Frame für Auftragsdetails (zunächst versteckt)
    details_frame = ttk.Frame(right_frame)
    
    # Auftragsdetails - Header mit Grundinformationen
    header_frame = ttk.Frame(details_frame)
    header_frame.pack(fill="x", padx=10, pady=5)
    
    auftrag_id_label = ttk.Label(header_frame, text="Auftrag #", font=("Arial", 12, "bold"))
    auftrag_id_label.pack(side="left", padx=5)
    
    # Buttons für Auftragsaktionen
    actions_frame = ttk.Frame(header_frame)
    actions_frame.pack(side="right", padx=5)
    
    ttk.Button(actions_frame, text="Bearbeiten", command=lambda: edit_auftrag(app)).pack(side="left", padx=3)
    ttk.Button(actions_frame, text="Teile hinzufügen", command=lambda: add_parts_to_auftrag(app)).pack(side="left", padx=3)
    ttk.Button(actions_frame, text="Status ändern", command=lambda: change_auftrag_status(app)).pack(side="left", padx=3)
    ttk.Button(actions_frame, text="Rechnung erstellen", command=lambda: create_invoice_for_auftrag(app)).pack(side="left", padx=3)
    
    # Kunde und Fahrzeug
    kunde_frame = ttk.LabelFrame(details_frame, text="Kundeninformationen")
    kunde_frame.pack(fill="x", padx=10, pady=5)
    
    auftrag_kunde_info = ttk.Label(kunde_frame, text="-")
    auftrag_kunde_info.pack(anchor="w", padx=10, pady=5)
    
    fahrzeug_frame = ttk.LabelFrame(details_frame, text="Fahrzeug")
    fahrzeug_frame.pack(fill="x", padx=10, pady=5)
    
    auftrag_fahrzeug_info = ttk.Label(fahrzeug_frame, text="-")
    auftrag_fahrzeug_info.pack(anchor="w", padx=10, pady=5)
    
    # Auftragsbeschreibung und Details
    beschreibung_frame = ttk.LabelFrame(details_frame, text="Auftragsbeschreibung")
    beschreibung_frame.pack(fill="x", padx=10, pady=5)
    
    auftrag_beschreibung = ttk.Label(beschreibung_frame, text="-")
    auftrag_beschreibung.pack(anchor="w", padx=10, pady=5)
    
    details_container = ttk.Frame(beschreibung_frame)
    details_container.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(details_container, text="Status:").grid(row=0, column=0, sticky="w", padx=5)
    auftrag_status = ttk.Label(details_container, text="-")
    auftrag_status.grid(row=0, column=1, sticky="w", padx=5)
    
    ttk.Label(details_container, text="Priorität:").grid(row=0, column=2, sticky="w", padx=5)
    auftrag_prioritaet = ttk.Label(details_container, text="-")
    auftrag_prioritaet.grid(row=0, column=3, sticky="w", padx=5)
    
    ttk.Label(details_container, text="Arbeitszeit:").grid(row=1, column=0, sticky="w", padx=5)
    auftrag_arbeitszeit = ttk.Label(details_container, text="-")
    auftrag_arbeitszeit.grid(row=1, column=1, sticky="w", padx=5)
    
    ttk.Label(details_container, text="Erstellt am:").grid(row=1, column=2, sticky="w", padx=5)
    auftrag_erstelldatum = ttk.Label(details_container, text="-")
    auftrag_erstelldatum.grid(row=1, column=3, sticky="w", padx=5)
    # Verwendete Ersatzteile
    parts_frame = ttk.LabelFrame(details_frame, text="Verwendete Ersatzteile")
    parts_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    parts_table_frame = ttk.Frame(parts_frame)
    parts_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    columns = ('name', 'menge', 'preis', 'rabatt', 'gesamt')
    auftrag_parts_tree = ttk.Treeview(parts_table_frame, columns=columns, show='headings', height=5)
    auftrag_parts_tree.heading('name', text='Artikelname')
    auftrag_parts_tree.heading('menge', text='Menge')
    auftrag_parts_tree.heading('preis', text='Einzelpreis')
    auftrag_parts_tree.heading('rabatt', text='Rabatt')
    auftrag_parts_tree.heading('gesamt', text='Gesamtpreis')
    
    auftrag_parts_tree.column('name', width=250)
    auftrag_parts_tree.column('menge', width=70, anchor='center')
    auftrag_parts_tree.column('preis', width=100, anchor='e')
    auftrag_parts_tree.column('rabatt', width=70, anchor='center')
    auftrag_parts_tree.column('gesamt', width=100, anchor='e')
    
    parts_vsb = ttk.Scrollbar(parts_table_frame, orient="vertical", command=auftrag_parts_tree.yview)
    auftrag_parts_tree.configure(yscrollcommand=parts_vsb.set)
    
    parts_vsb.pack(side="right", fill="y")
    auftrag_parts_tree.pack(side="left", fill="both", expand=True)
    
    # Gesamtsumme
    summe_frame = ttk.Frame(parts_frame)
    summe_frame.pack(fill="x", padx=5, pady=5, anchor="e")
    
    ttk.Label(summe_frame, text="Gesamtbetrag:").pack(side="left")
    auftrag_gesamt = ttk.Label(summe_frame, text="0.00 CHF", font=("Arial", 10, "bold"))
    auftrag_gesamt.pack(side="left", padx=5)
    
    # Notizen
    notizen_frame = ttk.LabelFrame(details_frame, text="Notizen")
    notizen_frame.pack(fill="x", padx=10, pady=5)
    
    auftrag_notizen = tk.Text(notizen_frame, height=3, width=50)
    auftrag_notizen.pack(fill="x", padx=5, pady=5)
    
    ttk.Button(notizen_frame, text="Notizen speichern", command=lambda: save_auftrag_notizen(app)).pack(side="right", padx=5, pady=5)
    
    # Event-Handler für Tabellenauswahl
    auftraege_tree.bind("<<TreeviewSelect>>", lambda event: show_auftrag_details(app, no_selection_label, details_frame))
    
    # Widget-Dictionary erstellen
    widgets = {
        'auftraege_search_var': auftraege_search_var,
        'status_filter_var': status_filter_var,
        'auftraege_tree': auftraege_tree,
        'no_selection_label': no_selection_label,
        'details_frame': details_frame,
        'auftrag_id_label': auftrag_id_label,
        'auftrag_kunde_info': auftrag_kunde_info,
        'auftrag_fahrzeug_info': auftrag_fahrzeug_info,
        'auftrag_beschreibung': auftrag_beschreibung,
        'auftrag_status': auftrag_status,
        'auftrag_prioritaet': auftrag_prioritaet,
        'auftrag_arbeitszeit': auftrag_arbeitszeit,
        'auftrag_erstelldatum': auftrag_erstelldatum,
        'auftrag_parts_tree': auftrag_parts_tree,
        'auftrag_gesamt': auftrag_gesamt,
        'auftrag_notizen': auftrag_notizen,
    }
    
    return auftraege_frame, widgets

def load_auftraege_data(app):
    """Lädt Auftragsdaten aus der Datenbank mit reduziertem Datensatz für die Übersicht"""
    cursor = app.conn.cursor()
    cursor.execute("""
    SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.status,
           strftime('%d.%m.%Y', a.erstellt_am) as datum
    FROM auftraege a
    LEFT JOIN kunden k ON a.kunden_id = k.id
    ORDER BY a.erstellt_am DESC
    """)
    
    # Treeview leeren
    for item in app.auftraege_widgets['auftraege_tree'].get_children():
        app.auftraege_widgets['auftraege_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        # Farbliche Markierung je nach Status
        tag = row[2].lower().replace(' ', '_')
        app.auftraege_widgets['auftraege_tree'].insert('', 'end', values=row, tags=(tag,))
        
    # Tags für verschiedene Status definieren
    app.auftraege_widgets['auftraege_tree'].tag_configure('offen', background='#FFE0E0')  # Leicht rot
    app.auftraege_widgets['auftraege_tree'].tag_configure('in_bearbeitung', background='#FFFFD0')  # Leicht gelb
    app.auftraege_widgets['auftraege_tree'].tag_configure('warten_auf_teile', background='#E0E0FF')  # Leicht blau
    app.auftraege_widgets['auftraege_tree'].tag_configure('abgeschlossen', background='#E0FFE0')  # Leicht grün
        
    app.update_status(f"{app.auftraege_widgets['auftraege_tree'].get_children().__len__()} Aufträge geladen")
    
    # Detailansicht zurücksetzen
    app.auftraege_widgets['no_selection_label'].pack(fill="both", expand=True, padx=20, pady=50)
    app.auftraege_widgets['details_frame'].pack_forget()

def search_auftraege(app):
    """Durchsucht die Auftragsliste nach dem Suchbegriff"""
    search_term = app.auftraege_widgets['auftraege_search_var'].get().lower()
    
    for item in app.auftraege_widgets['auftraege_tree'].get_children():
        values = app.auftraege_widgets['auftraege_tree'].item(item)['values']
        
        # Original-Tags speichern (für Status-Farben)
        current_tags = list(app.auftraege_widgets['auftraege_tree'].item(item)['tags'])
        status_tags = [tag for tag in current_tags if tag in ['offen', 'in_bearbeitung', 'warten_auf_teile', 'abgeschlossen']]
        
        # Suche in ID, Kunde, Status und Datum
        if (search_term in str(values[0]).lower() or  # ID
            search_term in str(values[1]).lower() or  # Kunde
            search_term in str(values[2]).lower() or  # Status
            search_term in str(values[3]).lower()):   # Datum
            app.auftraege_widgets['auftraege_tree'].item(item, tags=(['match'] + status_tags))
        else:
            app.auftraege_widgets['auftraege_tree'].item(item, tags=status_tags)
            
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
        SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.status,
               strftime('%d.%m.%Y', a.erstellt_am) as datum
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
            # Farbliche Markierung je nach Status
            tag = row[2].lower().replace(' ', '_')
            app.auftraege_widgets['auftraege_tree'].insert('', 'end', values=row, tags=(tag,))
            
    app.update_status(f"{app.auftraege_widgets['auftraege_tree'].get_children().__len__()} Aufträge gefiltert")

def show_auftrag_details(app, no_selection_label=None, details_frame=None):
    """Zeigt Details zum ausgewählten Auftrag an"""
    # Nutze die übergebenen Widgets, wenn vorhanden
    no_selection_label = no_selection_label or app.auftraege_widgets['no_selection_label']
    details_frame = details_frame or app.auftraege_widgets['details_frame']
    
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        # Hinweis anzeigen
        no_selection_label.pack(fill="both", expand=True, padx=20, pady=50)
        details_frame.pack_forget()
        return
    
    # Hinweis ausblenden und Details anzeigen
    no_selection_label.pack_forget()
    details_frame.pack(fill="both", expand=True)
    
    # Instanzvariable setzen, um die Auftrag-ID zu speichern
    app.current_auftrag_id = auftrag_id
    
    cursor = app.conn.cursor()
    
    # Vollständige Auftragsdaten laden
    cursor.execute("""
    SELECT a.id, a.beschreibung, a.status, a.prioritaet, a.arbeitszeit,
           strftime('%d.%m.%Y', a.erstellt_am) as erstellt_am,
           strftime('%d.%m.%Y', a.abgeschlossen_am) as abgeschlossen_am,
           a.notizen, k.vorname || ' ' || k.nachname as kunde,
           k.telefon, k.email
    FROM auftraege a
    JOIN kunden k ON a.kunden_id = k.id
    WHERE a.id = ?
    """, (auftrag_id,))
    
    auftrag = cursor.fetchone()
    if auftrag:
        # ID und Beschreibung
        app.auftraege_widgets['auftrag_id_label'].config(text=f"Auftrag #{auftrag[0]}: {auftrag[1]}")
        app.auftraege_widgets['auftrag_beschreibung'].config(text=auftrag[1])
        
        # Status-abhängige Farbe für Status
        status_farbe = "black"
        if auftrag[2] == "Offen":
            status_farbe = "#CC0000"  # Rot
        elif auftrag[2] == "In Bearbeitung":
            status_farbe = "#CC6600"  # Orange
        elif auftrag[2] == "Warten auf Teile":
            status_farbe = "#0000CC"  # Blau
        elif auftrag[2] == "Abgeschlossen":
            status_farbe = "#006600"  # Grün
            
        app.auftraege_widgets['auftrag_status'].config(text=auftrag[2], foreground=status_farbe)
        app.auftraege_widgets['auftrag_prioritaet'].config(text=auftrag[3])
        app.auftraege_widgets['auftrag_arbeitszeit'].config(text=f"{auftrag[4]} Stunden")
        app.auftraege_widgets['auftrag_erstelldatum'].config(text=auftrag[5])
        
        # Kundeninformationen
        kunde_info = f"{auftrag[8]}\nTel: {auftrag[9]}\nE-Mail: {auftrag[10]}"
        app.auftraege_widgets['auftrag_kunde_info'].config(text=kunde_info)
        
        # Notizen
        app.auftraege_widgets['auftrag_notizen'].delete(1.0, tk.END)
        if auftrag[7]:
            app.auftraege_widgets['auftrag_notizen'].insert(tk.END, auftrag[7])
    
    # Fahrzeuginformationen abrufen
    cursor.execute("""
    SELECT f.fahrzeug_typ, f.kennzeichen, f.fahrgestellnummer
    FROM auftraege a
    LEFT JOIN fahrzeuge f ON a.fahrzeug_id = f.id
    WHERE a.id = ?
    """, (auftrag_id,))
    
    fahrzeug = cursor.fetchone()
    if fahrzeug and fahrzeug[0]:
        fahrzeug_info = f"{fahrzeug[0]}\nKennzeichen: {fahrzeug[1] or 'Nicht angegeben'}\nFahrgestellnr.: {fahrzeug[2] or 'Nicht angegeben'}"
    else:
        # Wenn kein Fahrzeug im Auftrag hinterlegt ist, erstes Fahrzeug des Kunden versuchen
        cursor.execute("""
        SELECT f.fahrzeug_typ, f.kennzeichen, f.fahrgestellnummer
        FROM fahrzeuge f
        JOIN auftraege a ON f.kunden_id = a.kunden_id
        WHERE a.id = ?
        ORDER BY f.id
        LIMIT 1
        """, (auftrag_id,))
        
        fahrzeug = cursor.fetchone()
        if fahrzeug and fahrzeug[0]:
            fahrzeug_info = f"{fahrzeug[0]}\nKennzeichen: {fahrzeug[1] or 'Nicht angegeben'}\nFahrgestellnr.: {fahrzeug[2] or 'Nicht angegeben'}"
        else:
            fahrzeug_info = "Kein Fahrzeug zugeordnet"
    
    app.auftraege_widgets['auftrag_fahrzeug_info'].config(text=fahrzeug_info)

    # Verwendete Ersatzteile abrufen - HIER WURDE DIE ABFRAGE GEÄNDERT
    cursor.execute("""
    SELECT e.bezeichnung, ae.menge, ae.einzelpreis, COALESCE(ae.rabatt, 0) as rabatt
    FROM auftrag_ersatzteile ae
    JOIN ersatzteile e ON ae.ersatzteil_id = e.id
    WHERE ae.auftrag_id = ?
    """, (auftrag_id,))
    
    # Ersatzteile-Tabelle leeren
    for item in app.auftraege_widgets['auftrag_parts_tree'].get_children():
        app.auftraege_widgets['auftrag_parts_tree'].delete(item)
        
    # Gesamtsumme berechnen
    gesamtsumme = 0
    
    # Ersatzteile einfügen
    for row in cursor.fetchall():
        bezeichnung = row[0]
        menge = row[1]
        einzelpreis = float(row[2])
        rabatt = float(row[3])  # Rabatt jetzt aus der Datenbank
        
        # Gesamtpreis unter Berücksichtigung des Rabatts berechnen
        rabatt_betrag = einzelpreis * menge * (rabatt / 100)
        gesamtpreis = (einzelpreis * menge) - rabatt_betrag
        gesamtsumme += gesamtpreis
        
        print(f"DEBUG - Zeige Teil an: '{bezeichnung}', Menge={menge}, Preis={einzelpreis}, Rabatt={rabatt}%, Gesamtpreis={gesamtpreis}")
        
        app.auftraege_widgets['auftrag_parts_tree'].insert('', 'end', values=(
            bezeichnung, menge, f"{einzelpreis:.2f} CHF", f"{rabatt:.2f}%", f"{gesamtpreis:.2f} CHF"
        ))
    
    # Arbeitszeit hinzufügen, wenn vorhanden
    if auftrag and auftrag[4] > 0:
        # Stundensatz aus Konfiguration laden
        from utils.config import get_default_stundenlohn
        stundensatz = get_default_stundenlohn(app.conn)
        
        arbeitszeit = auftrag[4]
        bezeichnung = f"Arbeitszeit: {auftrag[1]}"
        rabatt = 0.0  # Standardwert
        arbeitskosten = arbeitszeit * stundensatz * (1 - rabatt/100)
        gesamtsumme += arbeitskosten
        
        app.auftraege_widgets['auftrag_parts_tree'].insert('', 'end', values=(
            bezeichnung, f"{arbeitszeit:.2f} h", f"{stundensatz:.2f} CHF/h", 
            f"{rabatt:.2f}%", f"{arbeitskosten:.2f} CHF"
        ))
    
    # Gesamtbetrag aktualisieren
    app.auftraege_widgets['auftrag_gesamt'].config(text=f"{gesamtsumme:.2f} CHF")

def get_selected_auftrag_id(app):
    """Gibt die ID des ausgewählten Auftrags zurück"""
    selected_items = app.auftraege_widgets['auftraege_tree'].selection()
    if not selected_items:
        return None
        
    return app.auftraege_widgets['auftraege_tree'].item(selected_items[0])['values'][0]

def save_auftrag_notizen(app):
    """Speichert Notizen zu einem Auftrag"""
    try:
        # Auftrag-ID abrufen
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

def edit_auftrag(app):
    """Bearbeitet einen vorhandenen Auftrag"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    auftragsdialog = AuftragsDialog(app.root, "Auftrag bearbeiten", auftrag_id, app.conn)
    if auftragsdialog.result:
        app.load_auftraege()
        # Auftrag wieder anzeigen nach dem Speichern
        for item in app.auftraege_widgets['auftraege_tree'].get_children():
            if app.auftraege_widgets['auftraege_tree'].item(item)['values'][0] == auftrag_id:
                app.auftraege_widgets['auftraege_tree'].selection_set(item)
                app.auftraege_widgets['auftraege_tree'].focus(item)
                app.auftraege_widgets['auftraege_tree'].see(item)
                show_auftrag_details(app)
                break
        app.update_status("Auftragsdaten aktualisiert")

def add_parts_to_auftrag(app):
    """Fügt Ersatzteile zu einem Auftrag hinzu"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    # Dialog zum Hinzufügen von Teilen
    teile_dialog = TeileAuswahlDialog(app.root, "Teile hinzufügen", auftrag_id, app.conn)
    if teile_dialog.result:
        # Auftrag aktualisieren
        for item in app.auftraege_widgets['auftraege_tree'].get_children():
            if app.auftraege_widgets['auftraege_tree'].item(item)['values'][0] == auftrag_id:
                app.auftraege_widgets['auftraege_tree'].selection_set(item)
                app.auftraege_widgets['auftraege_tree'].focus(item)
                app.auftraege_widgets['auftraege_tree'].see(item)
                show_auftrag_details(app)
                break
        app.update_status("Teile zum Auftrag hinzugefügt")

def change_auftrag_status(app):
    """Ändert den Status eines Auftrags"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    # Aktuellen Status abrufen
    cursor = app.conn.cursor()
    cursor.execute("SELECT status FROM auftraege WHERE id = ?", (auftrag_id,))
    aktueller_status = cursor.fetchone()[0]
    
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
            
            # Auftrag wieder anzeigen nach dem Speichern
            for item in app.auftraege_widgets['auftraege_tree'].get_children():
                if app.auftraege_widgets['auftraege_tree'].item(item)['values'][0] == auftrag_id:
                    app.auftraege_widgets['auftraege_tree'].selection_set(item)
                    app.auftraege_widgets['auftraege_tree'].focus(item)
                    app.auftraege_widgets['auftraege_tree'].see(item)
                    show_auftrag_details(app)
                    break
                    
            app.update_status(f"Auftragsstatus auf '{new_status}' geändert")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Ändern des Status: {e}")
            app.conn.rollback()

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
        
        # Zur Rechnung springen, falls die Tabs existieren
        try:
            if hasattr(app, 'notebook') and app.notebook is not None:
                app.notebook.select(4)  # Index 4 = Rechnungen-Tab
                
                # Rechnung in der Tabelle suchen und auswählen
                if 'rechnungen_widgets' in app.__dict__ and app.rechnungen_widgets is not None:
                    if 'rechnungen_tree' in app.rechnungen_widgets and app.rechnungen_widgets['rechnungen_tree'] is not None:
                        for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
                            values = app.rechnungen_widgets['rechnungen_tree'].item(item)['values']
                            if values[0] == existing_invoice[0]:
                                app.rechnungen_widgets['rechnungen_tree'].selection_set(item)
                                app.rechnungen_widgets['rechnungen_tree'].see(item)
                                if hasattr(app.rechnungen_widgets, 'show_rechnung_details'):
                                    app.rechnungen_widgets['show_rechnung_details'](app)
                                break
        except Exception as e:
            print(f"Fehler beim Anzeigen der Rechnung: {e}")
        return
        
    # Dialog zur Rechnungserstellung
    from dialogs.rechnungs_dialog import RechnungsDialog
    rechnungsdialog = RechnungsDialog(app.root, "Neue Rechnung", None, app.conn, auftrag_id)
    if rechnungsdialog.result:
        app.load_rechnungen()
        app.update_status("Neue Rechnung erstellt")
        
        # Zum Rechnungen-Tab wechseln
        try:
            if hasattr(app, 'notebook') and app.notebook is not None:
                app.notebook.select(4)  # Index 4 = Rechnungen-Tab
        except Exception as e:
            print(f"Fehler beim Wechseln zum Rechnungen-Tab: {e}")

def delete_auftrag(app):
    """Löscht einen Auftrag"""
    auftrag_id = get_selected_auftrag_id(app)
    if not auftrag_id:
        messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
        return
        
    # Auftragsbeschreibung für Bestätigungsdialog
    cursor = app.conn.cursor()
    cursor.execute("SELECT beschreibung FROM auftraege WHERE id = ?", (auftrag_id,))
    auftrag_desc = cursor.fetchone()[0]
    
    # Prüfen, ob bereits eine Rechnung existiert
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
        
        # Hier das Problem beheben: Prüfen, ob die Tabs und Widgets existieren, bevor wir darauf zugreifen
        try:
            # Zur Rechnung springen, falls die Tabs existieren
            if hasattr(app, 'notebook') and app.notebook is not None:
                app.notebook.select(4)  # Index 4 = Rechnungen-Tab
                
                # Rechnung in der Tabelle suchen und auswählen, falls die Widgets existieren
                if hasattr(app, 'rechnungen_widgets') and app.rechnungen_widgets is not None:
                    if 'rechnungen_tree' in app.rechnungen_widgets and app.rechnungen_widgets['rechnungen_tree'] is not None:
                        for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
                            values = app.rechnungen_widgets['rechnungen_tree'].item(item)['values']
                            if values[0] == existing_invoice[0]:
                                app.rechnungen_widgets['rechnungen_tree'].selection_set(item)
                                app.rechnungen_widgets['rechnungen_tree'].see(item)
                                
                                # Prüfen, ob die show_rechnung_details-Funktion existiert
                                if 'show_rechnung_details' in app.rechnungen_widgets and callable(app.rechnungen_widgets['show_rechnung_details']):
                                    app.rechnungen_widgets['show_rechnung_details'](None)
                                break
        except Exception as e:
            # Bei einem Fehler eine Meldung anzeigen, aber nicht abstürzen
            messagebox.showinfo("Hinweis", f"Die Rechnung existiert bereits, aber konnte nicht angezeigt werden.")
            print(f"Fehler beim Anzeigen der Rechnung: {e}")
                
        return
        
    # Dialog zur Rechnungserstellung
    rechnungsdialog = RechnungsDialog(app.root, "Neue Rechnung", None, app.conn, auftrag_id)
    if rechnungsdialog.result:
        app.load_rechnungen()
        app.update_status("Neue Rechnung erstellt")
        
        # Zum Rechnungen-Tab wechseln, mit Fehlerbehandlung
        try:
            if hasattr(app, 'notebook') and app.notebook is not None:
                app.notebook.select(4)  # Index 4 = Rechnungen-Tab
        except Exception as e:
            print(f"Fehler beim Wechseln zum Rechnungen-Tab: {e}")