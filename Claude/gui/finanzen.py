#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Finanzen-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from dialogs.finanzen_dialog import AusgabenDialog

def create_finanzen_tab(notebook, app):
    """Finanzen-Tab erstellen"""
    finanzen_frame = ttk.Frame(notebook)
    
    # Oberer Bereich - Finanzübersicht
    übersicht_frame = ttk.LabelFrame(finanzen_frame, text="Finanzübersicht")
    übersicht_frame.pack(fill="x", padx=10, pady=10)
    
    # Linke Seite - Kennzahlen
    kennzahlen_frame = ttk.Frame(übersicht_frame)
    kennzahlen_frame.pack(side="left", fill="y", padx=10, pady=10)
    
    # Zeitraum-Auswahl
    ttk.Label(kennzahlen_frame, text="Zeitraum:").grid(row=0, column=0, sticky="w", pady=5)
    finanzen_zeitraum_var = tk.StringVar(value="Dieser Monat")
    zeitraum_combo = ttk.Combobox(kennzahlen_frame, textvariable=finanzen_zeitraum_var, width=15, 
                                 values=["Dieser Monat", "Letzter Monat", "Dieses Jahr", "Letztes Jahr", "Benutzerdefiniert"])
    zeitraum_combo.grid(row=0, column=1, sticky="w", pady=5)
    zeitraum_combo.bind("<<ComboboxSelected>>", lambda event: update_finanzen_data(app, event))
    
    # Kennzahlen
    kennzahlen = [
        ("Gesamtumsatz:", "finanzen_umsatz"),
        ("Materialkosten:", "finanzen_materialkosten"),
        ("Sonstige Ausgaben:", "finanzen_sonstige_ausgaben"),
        ("Gewinn/Verlust:", "finanzen_gewinn"),
        ("Offene Forderungen:", "finanzen_forderungen"),
        ("Lagerwert:", "finanzen_lagerwert"),
        ("Liquidität:", "finanzen_liquidität")
    ]
    
    kennzahlen_labels = {}
    for i, (label_text, var_name) in enumerate(kennzahlen, start=1):
        ttk.Label(kennzahlen_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=2)
        kennzahlen_labels[var_name] = ttk.Label(kennzahlen_frame, text="-")
        kennzahlen_labels[var_name].grid(row=i, column=1, sticky="w", pady=2)
    
    # Rechte Seite - Diagramme
    chart_frame = ttk.Frame(übersicht_frame)
    chart_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    finanzen_fig, finanzen_ax = plt.subplots(figsize=(6, 4))
    finanzen_canvas = FigureCanvasTkAgg(finanzen_fig, master=chart_frame)
    finanzen_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Unterer Bereich - Tabs für Einnahmen, Ausgaben, Berichte
    finanzen_notebook = ttk.Notebook(finanzen_frame)
    finanzen_notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Einnahmen-Tab
    einnahmen_frame = ttk.Frame(finanzen_notebook)
    finanzen_notebook.add(einnahmen_frame, text="Einnahmen")
    
    # Suchleiste und Filter für Einnahmen
    einnahmen_filter_frame = ttk.Frame(einnahmen_frame)
    einnahmen_filter_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(einnahmen_filter_frame, text="Zeitraum:").pack(side="left", padx=5)
    einnahmen_zeitraum_var = tk.StringVar(value="Alle")
    einnahmen_zeitraum_combo = ttk.Combobox(einnahmen_filter_frame, textvariable=einnahmen_zeitraum_var, width=15, 
                                           values=["Alle", "Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr"])
    einnahmen_zeitraum_combo.pack(side="left", padx=5)
    einnahmen_zeitraum_combo.bind("<<ComboboxSelected>>", lambda event: filter_einnahmen(app))
    
    ttk.Button(einnahmen_filter_frame, text="Bericht erstellen", command=lambda: create_einnahmen_bericht(app)).pack(side="right", padx=5)
    
    # Einnahmen-Tabelle
    einnahmen_table_frame = ttk.Frame(einnahmen_frame)
    einnahmen_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    columns = ('id', 'datum', 'rechnungsnr', 'kunde', 'betrag', 'zahlungsart')
    einnahmen_tree = ttk.Treeview(einnahmen_table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    einnahmen_tree.heading('id', text='ID')
    einnahmen_tree.heading('datum', text='Datum')
    einnahmen_tree.heading('rechnungsnr', text='Rechnungsnr.')
    einnahmen_tree.heading('kunde', text='Kunde')
    einnahmen_tree.heading('betrag', text='Betrag (CHF)')
    einnahmen_tree.heading('zahlungsart', text='Zahlungsart')
    
    einnahmen_tree.column('id', width=40, anchor='center')
    einnahmen_tree.column('datum', width=80)
    einnahmen_tree.column('rechnungsnr', width=100)
    einnahmen_tree.column('kunde', width=150)
    einnahmen_tree.column('betrag', width=80, anchor='e')
    einnahmen_tree.column('zahlungsart', width=100)
    
    # Scrollbars
    vsb = ttk.Scrollbar(einnahmen_table_frame, orient="vertical", command=einnahmen_tree.yview)
    hsb = ttk.Scrollbar(einnahmen_table_frame, orient="horizontal", command=einnahmen_tree.xview)
    einnahmen_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    einnahmen_tree.pack(fill="both", expand=True)
    
    # Ausgaben-Tab
    ausgaben_frame = ttk.Frame(finanzen_notebook)
    finanzen_notebook.add(ausgaben_frame, text="Ausgaben")
    
    # Suchleiste und Filter für Ausgaben
    ausgaben_filter_frame = ttk.Frame(ausgaben_frame)
    ausgaben_filter_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(ausgaben_filter_frame, text="Kategorie:").pack(side="left", padx=5)
    ausgaben_kategorie_var = tk.StringVar(value="Alle")
    ausgaben_kategorie_combo = ttk.Combobox(ausgaben_filter_frame, textvariable=ausgaben_kategorie_var, width=15)
    ausgaben_kategorie_combo.pack(side="left", padx=5)
    ausgaben_kategorie_combo.bind("<<ComboboxSelected>>", lambda event: filter_ausgaben(app))
    
    ttk.Label(ausgaben_filter_frame, text="Zeitraum:").pack(side="left", padx=5)
    ausgaben_zeitraum_var = tk.StringVar(value="Alle")
    ausgaben_zeitraum_combo = ttk.Combobox(ausgaben_filter_frame, textvariable=ausgaben_zeitraum_var, width=15, 
                                          values=["Alle", "Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr"])
    ausgaben_zeitraum_combo.pack(side="left", padx=5)
    ausgaben_zeitraum_combo.bind("<<ComboboxSelected>>", lambda event: filter_ausgaben(app))
    
    ttk.Button(ausgaben_filter_frame, text="Neue Ausgabe", command=lambda: new_ausgabe(app)).pack(side="right", padx=5)
    ttk.Button(ausgaben_filter_frame, text="Löschen", command=lambda: delete_ausgabe(app)).pack(side="right", padx=5)
    
    # Ausgaben-Tabelle
    ausgaben_table_frame = ttk.Frame(ausgaben_frame)
    ausgaben_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    columns = ('id', 'datum', 'kategorie', 'beschreibung', 'betrag', 'beleg')
    ausgaben_tree = ttk.Treeview(ausgaben_table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    ausgaben_tree.heading('id', text='ID')
    ausgaben_tree.heading('datum', text='Datum')
    ausgaben_tree.heading('kategorie', text='Kategorie')
    ausgaben_tree.heading('beschreibung', text='Beschreibung')
    ausgaben_tree.heading('betrag', text='Betrag (CHF)')
    ausgaben_tree.heading('beleg', text='Beleg-Nr.')
    
    ausgaben_tree.column('id', width=40, anchor='center')
    ausgaben_tree.column('datum', width=80)
    ausgaben_tree.column('kategorie', width=100)
    ausgaben_tree.column('beschreibung', width=200)
    ausgaben_tree.column('betrag', width=80, anchor='e')
    ausgaben_tree.column('beleg', width=80)
    
    # Scrollbars
    vsb = ttk.Scrollbar(ausgaben_table_frame, orient="vertical", command=ausgaben_tree.yview)
    hsb = ttk.Scrollbar(ausgaben_table_frame, orient="horizontal", command=ausgaben_tree.xview)
    ausgaben_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    ausgaben_tree.pack(fill="both", expand=True)
    
    # Berichte-Tab
    berichte_frame = ttk.Frame(finanzen_notebook)
    finanzen_notebook.add(berichte_frame, text="Berichte")
    
    # Berichtsauswahl
    berichte_options_frame = ttk.Frame(berichte_frame)
    berichte_options_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(berichte_options_frame, text="Berichtstyp:").grid(row=0, column=0, padx=5, pady=5)
    bericht_typ_var = tk.StringVar(value="Umsatzübersicht")
    bericht_typ_combo = ttk.Combobox(berichte_options_frame, textvariable=bericht_typ_var, width=20, 
                                    values=["Umsatzübersicht", "Gewinn und Verlust", "Einnahmen nach Kunden", 
                                            "Ausgaben nach Kategorien", "Lagerbestandswert", "Werkstattauslastung"])
    bericht_typ_combo.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(berichte_options_frame, text="Zeitraum:").grid(row=0, column=2, padx=5, pady=5)
    bericht_zeitraum_var = tk.StringVar(value="Dieser Monat")
    bericht_zeitraum_combo = ttk.Combobox(berichte_options_frame, textvariable=bericht_zeitraum_var, width=15, 
                                         values=["Dieser Monat", "Letzter Monat", "Dieses Jahr", "Letztes Jahr", "Benutzerdefiniert"])
    bericht_zeitraum_combo.grid(row=0, column=3, padx=5, pady=5)
    
    ttk.Button(berichte_options_frame, text="Bericht generieren", command=lambda: generate_bericht(app)).grid(row=0, column=4, padx=5, pady=5)
    ttk.Button(berichte_options_frame, text="Als PDF speichern", command=lambda: save_bericht_pdf(app)).grid(row=0, column=5, padx=5, pady=5)
    
    # Berichtsanzeige
    bericht_text = tk.Text(berichte_frame, height=20, width=80)
    bericht_text.pack(fill="both", expand=True, padx=10, pady=10)

    # Widget-Dictionary erstellen
    widgets = {
        'finanzen_zeitraum_var': finanzen_zeitraum_var,
        'einnahmen_zeitraum_var': einnahmen_zeitraum_var,
        'ausgaben_kategorie_var': ausgaben_kategorie_var,
        'ausgaben_kategorie_combo': ausgaben_kategorie_combo,
        'ausgaben_zeitraum_var': ausgaben_zeitraum_var,
        'bericht_typ_var': bericht_typ_var,
        'bericht_zeitraum_var': bericht_zeitraum_var,
        'bericht_text': bericht_text,
        'einnahmen_tree': einnahmen_tree,
        'ausgaben_tree': ausgaben_tree,
        'finanzen_fig': finanzen_fig,
        'finanzen_ax': finanzen_ax,
        'finanzen_canvas': finanzen_canvas
    }
    
    # Kennzahlen-Labels hinzufügen
    widgets.update(kennzahlen_labels)
    
    return finanzen_frame, widgets

def update_finanzen_data(app, event=None):
    """Aktualisiert die Finanzübersicht"""
    cursor = app.conn.cursor()
    
    # Zeitraum für Abfragen bestimmen
    zeitraum_filter = ""
    if app.finanzen_widgets['finanzen_zeitraum_var'].get() == "Dieser Monat":
        zeitraum_filter = "WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now')"
    elif app.finanzen_widgets['finanzen_zeitraum_var'].get() == "Letzter Monat":
        zeitraum_filter = "WHERE strftime('%Y-%m', datum) = strftime('%Y-%m', 'now', '-1 month')"
    elif app.finanzen_widgets['finanzen_zeitraum_var'].get() == "Dieses Jahr":
        zeitraum_filter = "WHERE strftime('%Y', datum) = strftime('%Y', 'now')"
    elif app.finanzen_widgets['finanzen_zeitraum_var'].get() == "Letztes Jahr":
        zeitraum_filter = "WHERE strftime('%Y', datum) = strftime('%Y', 'now', '-1 year')"
    
    # Gesamtumsatz
    cursor.execute(f"""
    SELECT COALESCE(SUM(gesamtbetrag), 0)
    FROM rechnungen
    {zeitraum_filter}
    """)
    umsatz = cursor.fetchone()[0]
    app.finanzen_widgets['finanzen_umsatz'].config(text=f"{umsatz:.2f} CHF")
    
    # Materialkosten (aus verwendeten Teilen in abgeschlossenen Aufträgen)
    cursor.execute(f"""
    SELECT COALESCE(SUM(ae.menge * e.einkaufspreis), 0)
    FROM auftrag_ersatzteile ae
    JOIN ersatzteile e ON ae.ersatzteil_id = e.id
    JOIN auftraege a ON ae.auftrag_id = a.id
    JOIN rechnungen r ON a.id = r.auftrag_id
    {zeitraum_filter.replace('datum', 'r.datum')}
    """)
    materialkosten = cursor.fetchone()[0]
    app.finanzen_widgets['finanzen_materialkosten'].config(text=f"{materialkosten:.2f} CHF")
    
    # Sonstige Ausgaben
    cursor.execute(f"""
    SELECT COALESCE(SUM(betrag), 0)
    FROM ausgaben
    {zeitraum_filter}
    """)
    sonstige_ausgaben = cursor.fetchone()[0]
    app.finanzen_widgets['finanzen_sonstige_ausgaben'].config(text=f"{sonstige_ausgaben:.2f} CHF")
    
    # Gewinn/Verlust
    gewinn = umsatz - materialkosten - sonstige_ausgaben
    app.finanzen_widgets['finanzen_gewinn'].config(text=f"{gewinn:.2f} CHF")
    
    # Offene Forderungen
    cursor.execute("""
    SELECT COALESCE(SUM(gesamtbetrag), 0)
    FROM rechnungen
    WHERE bezahlt = 0
    """)
    forderungen = cursor.fetchone()[0]
    app.finanzen_widgets['finanzen_forderungen'].config(text=f"{forderungen:.2f} CHF")
    
    # Lagerwert
    cursor.execute("""
    SELECT COALESCE(SUM(lagerbestand * einkaufspreis), 0)
    FROM ersatzteile
    """)
    lagerwert = cursor.fetchone()[0]
    app.finanzen_widgets['finanzen_lagerwert'].config(text=f"{lagerwert:.2f} CHF")
    
    # Liquidität (fiktiv)
    liquidität = 5000 + gewinn - forderungen  # Annahme: Startkapital von 5000CHF
    app.finanzen_widgets['finanzen_liquidität'].config(text=f"{liquidität:.2f} CHF")
    
    # Einnahmen und Ausgaben für das Diagramm
    cursor.execute(f"""
    SELECT strftime('%m/%Y', datum) as monat, SUM(gesamtbetrag) as umsatz
    FROM rechnungen
    WHERE datum >= date('now', '-6 months')
    GROUP BY strftime('%Y-%m', datum)
    ORDER BY strftime('%Y-%m', datum)
    """)
    
    monate = []
    umsaetze = []
    
    for row in cursor.fetchall():
        monate.append(row[0])
        umsaetze.append(row[1])
        
    cursor.execute("""
    SELECT strftime('%m/%Y', datum) as monat, SUM(betrag) as ausgaben
    FROM ausgaben
    WHERE datum >= date('now', '-6 months')
    GROUP BY strftime('%Y-%m', datum)
    ORDER BY strftime('%Y-%m', datum)
    """)
    
    ausgaben_monate = []
    ausgaben_werte = []
    
    for row in cursor.fetchall():
        ausgaben_monate.append(row[0])
        ausgaben_werte.append(row[1])
        
    # Alle Monate vereinen und sortieren
    alle_monate = sorted(list(set(monate + ausgaben_monate)))
    
    # Daten für Diagramm vorbereiten
    umsatz_data = [0] * len(alle_monate)
    ausgaben_data = [0] * len(alle_monate)
    
    for i, monat in enumerate(alle_monate):
        if monat in monate:
            umsatz_data[i] = umsaetze[monate.index(monat)]
        if monat in ausgaben_monate:
            ausgaben_data[i] = ausgaben_werte[ausgaben_monate.index(monat)]
    
    # Diagramm aktualisieren
    app.finanzen_widgets['finanzen_ax'].clear()
    
    x = range(len(alle_monate))
    width = 0.35
    
    app.finanzen_widgets['finanzen_ax'].bar([i - width/2 for i in x], umsatz_data, width, label='Einnahmen', color='forestgreen')
    app.finanzen_widgets['finanzen_ax'].bar([i + width/2 for i in x], ausgaben_data, width, label='Ausgaben', color='indianred')
    
    app.finanzen_widgets['finanzen_ax'].set_ylabel('Betrag (CHF)')
    app.finanzen_widgets['finanzen_ax'].set_title('Einnahmen und Ausgaben')
    app.finanzen_widgets['finanzen_ax'].set_xticks(x)
    app.finanzen_widgets['finanzen_ax'].set_xticklabels(alle_monate, rotation=45)
    app.finanzen_widgets['finanzen_ax'].legend()
    app.finanzen_widgets['finanzen_ax'].grid(axis='y', linestyle='--', alpha=0.7)
    
    app.finanzen_widgets['finanzen_fig'].tight_layout()
    app.finanzen_widgets['finanzen_canvas'].draw()
    
    # Einnahmen und Ausgaben Tabellen aktualisieren
    load_einnahmen(app)
    load_ausgaben(app)

def load_einnahmen(app):
    """Lädt Einnahmendaten aus der Datenbank"""
    cursor = app.conn.cursor()
    
    zeitraum_filter = ""
    if app.finanzen_widgets['einnahmen_zeitraum_var'].get() != "Alle":
        if app.finanzen_widgets['einnahmen_zeitraum_var'].get() == "Heute":
            zeitraum_filter = "WHERE date(r.bezahlt_am) = date('now')"
        elif app.finanzen_widgets['einnahmen_zeitraum_var'].get() == "Diese Woche":
            zeitraum_filter = "WHERE date(r.bezahlt_am) >= date('now', 'weekday 0', '-7 days')"
        elif app.finanzen_widgets['einnahmen_zeitraum_var'].get() == "Dieser Monat":
            zeitraum_filter = "WHERE strftime('%Y-%m', r.bezahlt_am) = strftime('%Y-%m', 'now')"
        elif app.finanzen_widgets['einnahmen_zeitraum_var'].get() == "Dieses Jahr":
            zeitraum_filter = "WHERE strftime('%Y', r.bezahlt_am) = strftime('%Y', 'now')"
    
    query = f"""
    SELECT r.id, strftime('%d.%m.%Y', r.bezahlt_am) as datum, r.rechnungsnummer, 
           k.vorname || ' ' || k.nachname as kunde, 
           printf("%.2f", r.gesamtbetrag) as betrag, r.zahlungsart
    FROM rechnungen r
    LEFT JOIN auftraege a ON r.auftrag_id = a.id
    LEFT JOIN kunden k ON a.kunden_id = k.id
    {zeitraum_filter}
    WHERE r.bezahlt = 1
    ORDER BY r.bezahlt_am DESC
    """
    
    cursor.execute(query)
    
    # Treeview leeren
    for item in app.finanzen_widgets['einnahmen_tree'].get_children():
        app.finanzen_widgets['einnahmen_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        app.finanzen_widgets['einnahmen_tree'].insert('', 'end', values=row)

def load_ausgaben(app):
    """Lädt Ausgabendaten aus der Datenbank"""
    cursor = app.conn.cursor()
    
    kategorie_filter = ""
    if app.finanzen_widgets['ausgaben_kategorie_var'].get() != "Alle":
        kategorie_filter = f"AND kategorie = '{app.finanzen_widgets['ausgaben_kategorie_var'].get()}'"
        
    zeitraum_filter = ""
    if app.finanzen_widgets['ausgaben_zeitraum_var'].get() != "Alle":
        if app.finanzen_widgets['ausgaben_zeitraum_var'].get() == "Heute":
            zeitraum_filter = "AND date(datum) = date('now')"
        elif app.finanzen_widgets['ausgaben_zeitraum_var'].get() == "Diese Woche":
            zeitraum_filter = "AND date(datum) >= date('now', 'weekday 0', '-7 days')"
        elif app.finanzen_widgets['ausgaben_zeitraum_var'].get() == "Dieser Monat":
            zeitraum_filter = "AND strftime('%Y-%m', datum) = strftime('%Y-%m', 'now')"
        elif app.finanzen_widgets['ausgaben_zeitraum_var'].get() == "Dieses Jahr":
            zeitraum_filter = "AND strftime('%Y', datum) = strftime('%Y', 'now')"
    
    query = f"""
    SELECT id, strftime('%d.%m.%Y', datum) as datum, kategorie, beschreibung, 
           printf("%.2f", betrag) as betrag, beleg_nr
    FROM ausgaben
    WHERE 1=1 {kategorie_filter} {zeitraum_filter}
    ORDER BY datum DESC
    """
    
    cursor.execute(query)
    
    # Treeview leeren
    for item in app.finanzen_widgets['ausgaben_tree'].get_children():
        app.finanzen_widgets['ausgaben_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        app.finanzen_widgets['ausgaben_tree'].insert('', 'end', values=row)

def filter_einnahmen(app):
    """Filtert Einnahmen nach Zeitraum"""
    load_einnahmen(app)

def filter_ausgaben(app):
    """Filtert Ausgaben nach Kategorie und Zeitraum"""
    load_ausgaben(app)

def get_selected_ausgabe_id(app):
    """Gibt die ID der ausgewählten Ausgabe zurück"""
    selected_items = app.finanzen_widgets['ausgaben_tree'].selection()
    if not selected_items:
        return None
        
    return app.finanzen_widgets['ausgaben_tree'].item(selected_items[0])['values'][0]

def new_ausgabe(app):
    """Erstellt eine neue Ausgabe"""
    ausgabedialog = AusgabenDialog(app.root, "Neue Ausgabe", None, app.conn)
    if ausgabedialog.result:
        load_ausgaben(app)
        app.load_categories()
        app.update_finanzen()
        app.update_status("Neue Ausgabe erfasst")

def delete_ausgabe(app):
    """Löscht eine Ausgabe"""
    ausgabe_id = get_selected_ausgabe_id(app)
    if not ausgabe_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Ausgabe aus.")
        return
        
    beschreibung = app.finanzen_widgets['ausgaben_tree'].item(app.finanzen_widgets['ausgaben_tree'].selection()[0])['values'][3]
    
    # Bestätigung einholen
    if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie die Ausgabe '{beschreibung}' wirklich löschen?"):
        try:
            cursor = app.conn.cursor()
            cursor.execute("DELETE FROM ausgaben WHERE id = ?", (ausgabe_id,))
            app.conn.commit()
            load_ausgaben(app)
            app.load_categories()
            app.update_finanzen()
            app.update_status(f"Ausgabe gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Ausgabe: {e}")
            app.conn.rollback()

def create_einnahmen_bericht(app):
    """Erstellt einen Einnahmenbericht"""
    zeitraum = app.finanzen_widgets['einnahmen_zeitraum_var'].get()
    
    # Berichtsdaten sammeln
    cursor = app.conn.cursor()
    
    zeitraum_filter = ""
    if zeitraum != "Alle":
        if zeitraum == "Heute":
            zeitraum_filter = "WHERE date(r.bezahlt_am) = date('now')"
        elif zeitraum == "Diese Woche":
            zeitraum_filter = "WHERE date(r.bezahlt_am) >= date('now', 'weekday 0', '-7 days')"
        elif zeitraum == "Dieser Monat":
            zeitraum_filter = "WHERE strftime('%Y-%m', r.bezahlt_am) = strftime('%Y-%m', 'now')"
        elif zeitraum == "Dieses Jahr":
            zeitraum_filter = "WHERE strftime('%Y', r.bezahlt_am) = strftime('%Y', 'now')"
    
    # Gesamteinnahmen
    query = f"""
    SELECT printf("%.2f", SUM(r.gesamtbetrag)) as gesamt_einnahmen
    FROM rechnungen r
    {zeitraum_filter}
    WHERE r.bezahlt = 1
    """
    
    cursor.execute(query)
    gesamt_einnahmen = cursor.fetchone()[0] or "0.00"