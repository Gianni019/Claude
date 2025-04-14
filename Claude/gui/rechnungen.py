#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rechnungen-Tab für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def create_rechnungen_tab(notebook, app):
    """Rechnungen-Tab erstellen"""
    rechnungen_frame = ttk.Frame(notebook)
    
    # Suchleiste und Filter
    filter_frame = ttk.Frame(rechnungen_frame)
    filter_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(filter_frame, text="Suche:").grid(row=0, column=0, padx=5)
    rechnungen_search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=rechnungen_search_var, width=20)
    search_entry.grid(row=0, column=1, padx=5)
    search_entry.bind("<KeyRelease>", lambda event: search_rechnungen(app))
    
    ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, padx=5)
    rechnung_status_var = tk.StringVar(value="Alle")
    status_combo = ttk.Combobox(filter_frame, textvariable=rechnung_status_var, width=15, 
                               values=["Alle", "Bezahlt", "Offen"])
    status_combo.grid(row=0, column=3, padx=5)
    status_combo.bind("<<ComboboxSelected>>", lambda event: filter_rechnungen(app))
    
    ttk.Label(filter_frame, text="Zeitraum:").grid(row=0, column=4, padx=5)
    rechnung_zeitraum_var = tk.StringVar(value="Alle")
    zeitraum_combo = ttk.Combobox(filter_frame, textvariable=rechnung_zeitraum_var, width=15, 
                                 values=["Alle", "Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr"])
    zeitraum_combo.grid(row=0, column=5, padx=5)
    zeitraum_combo.bind("<<ComboboxSelected>>", lambda event: filter_rechnungen(app))
    
    # Buttons
    btn_frame = ttk.Frame(rechnungen_frame)
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(btn_frame, text="Neue Rechnung", command=lambda: new_rechnung(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Rechnung anzeigen", command=lambda: view_rechnung(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Drucken", command=lambda: print_rechnung(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Als PDF speichern", command=lambda: save_rechnung_pdf(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Als bezahlt markieren", command=lambda: mark_rechnung_paid(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Löschen", command=lambda: delete_rechnung(app)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Aktualisieren", command=app.load_rechnungen).pack(side="right", padx=5)

    # Tabelle
    table_frame = ttk.Frame(rechnungen_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    columns = ('id', 'rechnungsnummer', 'kunde', 'datum', 'betrag', 'status', 'zahlungsart')
    rechnungen_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    
    # Spaltenkonfiguration
    rechnungen_tree.heading('id', text='ID')
    rechnungen_tree.heading('rechnungsnummer', text='Rechnungsnr.')
    rechnungen_tree.heading('kunde', text='Kunde')
    rechnungen_tree.heading('datum', text='Datum')
    rechnungen_tree.heading('betrag', text='Betrag (CHF)')
    rechnungen_tree.heading('status', text='Status')
    rechnungen_tree.heading('zahlungsart', text='Zahlungsart')
    
    rechnungen_tree.column('id', width=40, anchor='center')
    rechnungen_tree.column('rechnungsnummer', width=100)
    rechnungen_tree.column('kunde', width=150)
    rechnungen_tree.column('datum', width=80)
    rechnungen_tree.column('betrag', width=80, anchor='e')
    rechnungen_tree.column('status', width=80)
    rechnungen_tree.column('zahlungsart', width=100)
    
    # Scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=rechnungen_tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=rechnungen_tree.xview)
    rechnungen_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    rechnungen_tree.pack(fill="both", expand=True)

    # Rechnungsdetails unten anzeigen
    details_frame = ttk.LabelFrame(rechnungen_frame, text="Rechnungsdetails")
    details_frame.pack(fill="x", padx=10, pady=10)
    
    # Spalten für Details
    left_details = ttk.Frame(details_frame)
    left_details.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
    
    right_details = ttk.Frame(details_frame)
    right_details.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
    
    # Linke Spalte - Rechnungsübersicht
    ttk.Label(left_details, text="Rechnungsnummer:").grid(row=0, column=0, sticky="w", pady=2)
    rechnung_nummer_info = ttk.Label(left_details, text="-")
    rechnung_nummer_info.grid(row=0, column=1, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Kunde:").grid(row=1, column=0, sticky="w", pady=2)
    rechnung_kunde_info = ttk.Label(left_details, text="-")
    rechnung_kunde_info.grid(row=1, column=1, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Datum:").grid(row=2, column=0, sticky="w", pady=2)
    rechnung_datum_info = ttk.Label(left_details, text="-")
    rechnung_datum_info.grid(row=2, column=1, sticky="w", pady=2)
    
    ttk.Label(left_details, text="Status:").grid(row=3, column=0, sticky="w", pady=2)
    rechnung_status_info = ttk.Label(left_details, text="-")
    rechnung_status_info.grid(row=3, column=1, sticky="w", pady=2)
    
    # Rechte Spalte - Positionen
    ttk.Label(right_details, text="Positionen:").grid(row=0, column=0, sticky="w", pady=2)
    
    positions_frame = ttk.Frame(right_details)
    positions_frame.grid(row=1, column=0, sticky="w", pady=2)
    
    rechnung_positions_tree = ttk.Treeview(positions_frame, columns=('pos', 'bezeichnung', 'menge', 'einzelpreis', 'gesamtpreis'), show='headings', height=4)
    rechnung_positions_tree.heading('pos', text='#')
    rechnung_positions_tree.heading('bezeichnung', text='Bezeichnung')
    rechnung_positions_tree.heading('menge', text='Menge')
    rechnung_positions_tree.heading('einzelpreis', text='Einzelpreis')
    rechnung_positions_tree.heading('gesamtpreis', text='Gesamtpreis')
    
    rechnung_positions_tree.column('pos', width=30, anchor='center')
    rechnung_positions_tree.column('bezeichnung', width=200)
    rechnung_positions_tree.column('menge', width=50, anchor='center')
    rechnung_positions_tree.column('einzelpreis', width=80, anchor='e')
    rechnung_positions_tree.column('gesamtpreis', width=80, anchor='e')
    
    positions_vsb = ttk.Scrollbar(positions_frame, orient="vertical", command=rechnung_positions_tree.yview)
    rechnung_positions_tree.configure(yscrollcommand=positions_vsb.set)
    
    positions_vsb.pack(side="right", fill="y")
    rechnung_positions_tree.pack(side="left", fill="both", expand=True)
    
    # Doppelklick zum Anzeigen
    rechnungen_tree.bind("<Double-1>", lambda event: view_rechnung(app))
    
    # Event-Handler für Tabellenauswahl
    rechnungen_tree.bind("<<TreeviewSelect>>", lambda event: show_rechnung_details(app))

    # Widget-Dictionary erstellen
    widgets = {
        'rechnungen_search_var': rechnungen_search_var,
        'rechnung_status_var': rechnung_status_var,
        'rechnung_zeitraum_var': rechnung_zeitraum_var,
        'rechnungen_tree': rechnungen_tree,
        'rechnung_nummer_info': rechnung_nummer_info,
        'rechnung_kunde_info': rechnung_kunde_info,
        'rechnung_datum_info': rechnung_datum_info,
        'rechnung_status_info': rechnung_status_info,
        'rechnung_positions_tree': rechnung_positions_tree,
        'show_rechnung_details': show_rechnung_details
    }
    
    return rechnungen_frame, widgets

def load_rechnungen_data(app):
    """Lädt Rechnungsdaten aus der Datenbank"""
    cursor = app.conn.cursor()
    cursor.execute("""
    SELECT r.id, r.rechnungsnummer, k.vorname || ' ' || k.nachname as kunde, 
           strftime('%d.%m.%Y', r.datum) as datum, 
           printf("%.2f", r.gesamtbetrag) as betrag,
           CASE WHEN r.bezahlt = 1 THEN 'Bezahlt' ELSE 'Offen' END as status,
           r.zahlungsart
    FROM rechnungen r
    LEFT JOIN auftraege a ON r.auftrag_id = a.id
    LEFT JOIN kunden k ON a.kunden_id = k.id
    ORDER BY r.datum DESC
    """)
    
    # Treeview leeren
    for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
        app.rechnungen_widgets['rechnungen_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        # Farbige Markierung für bezahlte/unbezahlte Rechnungen
        if row[5] == 'Bezahlt':
            app.rechnungen_widgets['rechnungen_tree'].insert('', 'end', values=row, tags=('bezahlt',))
        else:
            app.rechnungen_widgets['rechnungen_tree'].insert('', 'end', values=row, tags=('offen',))
            
    # Tags für Rechnungsstatus konfigurieren
    app.rechnungen_widgets['rechnungen_tree'].tag_configure('bezahlt', background='lightgreen')
    app.rechnungen_widgets['rechnungen_tree'].tag_configure('offen', background='lightyellow')
        
    app.update_status(f"{app.rechnungen_widgets['rechnungen_tree'].get_children().__len__()} Rechnungen geladen")

def search_rechnungen(app):
    """Durchsucht die Rechnungsliste nach dem Suchbegriff"""
    search_term = app.rechnungen_widgets['rechnungen_search_var'].get().lower()
    
    for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
        values = app.rechnungen_widgets['rechnungen_tree'].item(item)['values']
        current_tags = app.rechnungen_widgets['rechnungen_tree'].item(item)['tags']
        
        # Status-Tag beibehalten
        status_tag = 'bezahlt' if 'bezahlt' in current_tags else 'offen'
        
        # Suche in Rechnungsnummer, Kunde und Zahlungsart
        if (search_term in str(values[1]).lower() or  # Rechnungsnummer
            search_term in str(values[2]).lower() or  # Kunde
            search_term in str(values[6]).lower()):   # Zahlungsart
            app.rechnungen_widgets['rechnungen_tree'].item(item, tags=('match', status_tag))
        else:
            app.rechnungen_widgets['rechnungen_tree'].item(item, tags=(status_tag,))
            
    if search_term:
        # Hervorheben der Treffer
        app.rechnungen_widgets['rechnungen_tree'].tag_configure('match', background='lightyellow')
    else:
        # Filter anwenden, wenn Suchfeld leer
        filter_rechnungen(app)

def filter_rechnungen(app):
    """Filtert Rechnungen nach Status und Zeitraum"""
    status_filter = app.rechnungen_widgets['rechnung_status_var'].get()
    zeitraum_filter = app.rechnungen_widgets['rechnung_zeitraum_var'].get()
    
    cursor = app.conn.cursor()
    
    where_clause = "WHERE 1=1"
    
    if status_filter != "Alle":
        bezahlt_value = 1 if status_filter == "Bezahlt" else 0
        where_clause += f" AND r.bezahlt = {bezahlt_value}"
        
    if zeitraum_filter != "Alle":
        if zeitraum_filter == "Heute":
            where_clause += " AND date(r.datum) = date('now')"
        elif zeitraum_filter == "Diese Woche":
            where_clause += " AND date(r.datum) >= date('now', 'weekday 0', '-7 days')"
        elif zeitraum_filter == "Dieser Monat":
            where_clause += " AND strftime('%Y-%m', r.datum) = strftime('%Y-%m', 'now')"
        elif zeitraum_filter == "Dieses Jahr":
            where_clause += " AND strftime('%Y', r.datum) = strftime('%Y', 'now')"
        
    query = f"""
    SELECT r.id, r.rechnungsnummer, k.vorname || ' ' || k.nachname as kunde, 
           strftime('%d.%m.%Y', r.datum) as datum, 
           printf("%.2f", r.gesamtbetrag) as betrag,
           CASE WHEN r.bezahlt = 1 THEN 'Bezahlt' ELSE 'Offen' END as status,
           r.zahlungsart
    FROM rechnungen r
    LEFT JOIN auftraege a ON r.auftrag_id = a.id
    LEFT JOIN kunden k ON a.kunden_id = k.id
    {where_clause}
    ORDER BY r.datum DESC
    """
    
    cursor.execute(query)
    
    # Treeview leeren
    for item in app.rechnungen_widgets['rechnungen_tree'].get_children():
        app.rechnungen_widgets['rechnungen_tree'].delete(item)
        
    # Daten einfügen
    for row in cursor.fetchall():
        if row[5] == 'Bezahlt':
            app.rechnungen_widgets['rechnungen_tree'].insert('', 'end', values=row, tags=('bezahlt',))
        else:
            app.rechnungen_widgets['rechnungen_tree'].insert('', 'end', values=row, tags=('offen',))
            
    app.update_status(f"{app.rechnungen_widgets['rechnungen_tree'].get_children().__len__()} Rechnungen gefiltert")

def get_selected_rechnung_id(app):
    """Gibt die ID der ausgewählten Rechnung zurück"""
    selected_items = app.rechnungen_widgets['rechnungen_tree'].selection()
    if not selected_items:
        return None
        
    return app.rechnungen_widgets['rechnungen_tree'].item(selected_items[0])['values'][0]

def show_rechnung_details(app, event=None):
    """Zeigt Details zur ausgewählten Rechnung an"""
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        return
    
    cursor = app.conn.cursor()
    
    # Rechnungsinformationen abrufen
    cursor.execute("""
    SELECT r.rechnungsnummer, k.vorname || ' ' || k.nachname as kunde, 
           strftime('%d.%m.%Y', r.datum) as datum,
           CASE WHEN r.bezahlt = 1 THEN 'Bezahlt am ' || strftime('%d.%m.%Y', r.bezahlt_am) ELSE 'Offen' END as status
    FROM rechnungen r
    LEFT JOIN auftraege a ON r.auftrag_id = a.id
    LEFT JOIN kunden k ON a.kunden_id = k.id
    WHERE r.id = ?
    """, (rechnung_id,))
    
    rechnung_info = cursor.fetchone()
    if rechnung_info:
        app.rechnungen_widgets['rechnung_nummer_info'].config(text=rechnung_info[0])
        app.rechnungen_widgets['rechnung_kunde_info'].config(text=rechnung_info[1])
        app.rechnungen_widgets['rechnung_datum_info'].config(text=rechnung_info[2])
        app.rechnungen_widgets['rechnung_status_info'].config(text=rechnung_info[3])
        
        # Status-Farbe setzen
        if "Bezahlt" in rechnung_info[3]:
            app.rechnungen_widgets['rechnung_status_info'].config(foreground="green")
        else:
            app.rechnungen_widgets['rechnung_status_info'].config(foreground="red")

# Auftragsinformationen und verwendete Ersatzteile abrufen
    cursor.execute("""
    SELECT a.id, a.beschreibung, a.arbeitszeit
    FROM rechnungen r
    JOIN auftraege a ON r.auftrag_id = a.id
    WHERE r.id = ?
    """, (rechnung_id,))
    
    auftrag_info = cursor.fetchone()
    if auftrag_info:
        auftrag_id = auftrag_info[0]
        
        # Rechnungspositionen abrufen (Ersatzteile + Arbeitszeit)
        cursor.execute("""
        SELECT e.bezeichnung, ae.menge, printf("%.2f", ae.einzelpreis) as einzelpreis, 
               printf("%.2f", ae.menge * ae.einzelpreis) as gesamtpreis
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (auftrag_id,))
        
        # Positionen-Tabelle leeren
        for item in app.rechnungen_widgets['rechnung_positions_tree'].get_children():
            app.rechnungen_widgets['rechnung_positions_tree'].delete(item)
            
        # Positionen einfügen (Ersatzteile)
        pos = 1
        for row in cursor.fetchall():
            app.rechnungen_widgets['rechnung_positions_tree'].insert('', 'end', values=(pos, row[0], row[1], f"{row[2]} CHF", f"{row[3]} CHF"))
            pos += 1
            
        # Arbeitszeit als Position hinzufügen, wenn vorhanden
        if auftrag_info[2] > 0:
            # Stundensatz aus Konfiguration laden
            from utils.config import get_default_stundenlohn
            stundensatz = get_default_stundenlohn(app.conn)
            
            arbeitszeit = auftrag_info[2]
            arbeitskosten = arbeitszeit * stundensatz
            app.rechnungen_widgets['rechnung_positions_tree'].insert('', 'end', values=(
                pos, 
                f"Arbeitszeit: {auftrag_info[1]}", 
                f"{arbeitszeit:.2f} h", 
                f"{stundensatz:.2f} CHF", 
                f"{arbeitskosten:.2f} CHF"
            ))

def new_rechnung(app):
    """Erstellt eine neue Rechnung"""
    from dialogs.rechnungs_dialog import RechnungsDialog
    rechnungsdialog = RechnungsDialog(app.root, "Neue Rechnung", None, app.conn)
    if rechnungsdialog.result:
        app.load_rechnungen()
        app.update_status("Neue Rechnung erstellt")

def view_rechnung(app):
    """Zeigt eine Rechnung an"""
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
        return
        
    # Rechnungsanzeige-Dialog
    from dialogs.rechnungs_dialog import RechnungsAnzeigeDialog
    RechnungsAnzeigeDialog(app.root, "Rechnung anzeigen", rechnung_id, app.conn)

def print_rechnung(app):
    """Druckt eine Rechnung"""
    from utils.pdf_generator import generate_invoice_pdf
    import os
    import subprocess
    
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
        return
        
    success, pdf_path = generate_invoice_pdf(app.conn, rechnung_id)
    
    if success:
        try:
            if os.name == 'nt':  # Windows
                # Mit Standard-PDF-Reader drucken
                os.startfile(pdf_path, "print")
            elif os.name == 'posix':  # Linux, Mac
                # Unter Linux/Mac den Standard-Druckbefehl verwenden
                if os.system('command -v lpr') == 0:  # Linux/Mac
                    subprocess.call(['lpr', pdf_path])
                else:
                    messagebox.showinfo("Hinweis", "Bitte öffnen Sie die PDF-Datei und drucken Sie sie manuell.")
                    # PDF öffnen
                    if os.system('command -v xdg-open') == 0:  # Linux
                        subprocess.call(['xdg-open', pdf_path])
                    else:  # Mac
                        subprocess.call(['open', pdf_path])
        except Exception as e:
            messagebox.showinfo("Information", f"Drucken nicht möglich: {e}")
            # Als Fallback die PDF anzeigen
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':  # Linux, Mac
                    if os.system('command -v xdg-open') == 0:  # Linux
                        subprocess.call(['xdg-open', pdf_path])
                    else:  # Mac
                        subprocess.call(['open', pdf_path])
            except Exception as e:
                messagebox.showinfo("Information", f"PDF wurde erstellt, konnte aber nicht geöffnet werden: {pdf_path}")
    else:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen der PDF: {pdf_path}")

def save_rechnung_pdf(app):
    """Speichert eine Rechnung als PDF"""
    from utils.pdf_generator import generate_invoice_pdf
    from tkinter import filedialog
    import os
    
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
        return
        
    # Dateiname vorschlagen
    cursor = app.conn.cursor()
    cursor.execute("SELECT rechnungsnummer FROM rechnungen WHERE id = ?", (rechnung_id,))
    rechnungsnr = cursor.fetchone()[0].replace('/', '_').replace(' ', '_')
    
    default_filename = f"Rechnung_{rechnungsnr}.pdf"
    
    # Speicherort wählen
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Dateien", "*.pdf")],
        initialfile=default_filename
    )
    
    if not file_path:
        return  # Abgebrochen
        
    # PDF generieren
    success, pdf_path = generate_invoice_pdf(app.conn, rechnung_id, file_path)
    
    if success:
        messagebox.showinfo("Information", f"Die Rechnung wurde als PDF gespeichert: {file_path}")
        
        # PDF öffnen
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Linux':
                subprocess.call(['xdg-open', file_path])
            else:  # macOS
                subprocess.call(['open', file_path])
        except Exception as e:
            messagebox.showinfo("Hinweis", f"PDF wurde gespeichert, konnte aber nicht automatisch geöffnet werden: {e}")
    else:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der PDF: {pdf_path}")

def mark_rechnung_paid(app):
    """Markiert eine Rechnung als bezahlt"""
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
        return
        
    status = app.rechnungen_widgets['rechnungen_tree'].item(app.rechnungen_widgets['rechnungen_tree'].selection()[0])['values'][5]
    
    if status == "Bezahlt":
        messagebox.showinfo("Information", "Diese Rechnung ist bereits als bezahlt markiert.")
        return
        
    # Zahlungsart abfragen
    zahlungsarten = ["Bar", "Überweisung", "EC-Karte", "Kreditkarte", "PayPal", "Twint"]
    zahlungsart = tk.simpledialog.askstring(
        "Zahlungsart",
        "Bitte wählen Sie die Zahlungsart:",
        parent=app.root
    )
    
    if not zahlungsart:
        return
        
    try:
        cursor = app.conn.cursor()
        cursor.execute(
            "UPDATE rechnungen SET bezahlt = 1, bezahlt_am = datetime('now'), zahlungsart = ? WHERE id = ?",
            (zahlungsart, rechnung_id)
        )
        app.conn.commit()
        app.load_rechnungen()
        show_rechnung_details(app)
        app.update_status("Rechnung als bezahlt markiert")
        
        # Dashboard und Finanzen aktualisieren
        app.update_dashboard()
        app.update_finanzen()
    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Rechnung: {e}")
        app.conn.rollback()

def delete_rechnung(app):
    """Löscht eine Rechnung"""
    rechnung_id = get_selected_rechnung_id(app)
    if not rechnung_id:
        messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
        return
        
    rechnung_nr = app.rechnungen_widgets['rechnungen_tree'].item(app.rechnungen_widgets['rechnungen_tree'].selection()[0])['values'][1]
    status = app.rechnungen_widgets['rechnungen_tree'].item(app.rechnungen_widgets['rechnungen_tree'].selection()[0])['values'][5]
    
    if status == "Bezahlt":
        messagebox.showwarning("Warnung", "Bezahlte Rechnungen können nicht gelöscht werden.")
        return
        
    # Bestätigung einholen
    if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie die Rechnung {rechnung_nr} wirklich löschen?"):
        try:
            cursor = app.conn.cursor()
            cursor.execute("DELETE FROM rechnungen WHERE id = ?", (rechnung_id,))
            app.conn.commit()
            app.load_rechnungen()
            app.update_status(f"Rechnung {rechnung_nr} gelöscht")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Rechnung: {e}")
            app.conn.rollback()