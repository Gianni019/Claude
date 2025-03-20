#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialoge für Rechnungen
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

from utils.helpers import get_selected_rechnung_id
from gui.rechnungen import get_selected_rechnung_id



class RechnungsDialog:
    
    def __init__(self, parent, title, rechnung_id=None, conn=None, auftrag_id=None):
        self.parent = parent
        self.rechnung_id = rechnung_id
        self.conn = conn
        self.auftrag_id = auftrag_id
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Wenn keine Rechnung bearbeitet wird und kein Auftrag vorgegeben ist
        if not self.rechnung_id and not self.auftrag_id:
            # Auftragsauswahl
            auftrag_frame = ttk.LabelFrame(main_frame, text="Auftrag auswählen")
            auftrag_frame.pack(fill="x", expand=False, pady=5)
            
            # Tabelle mit offenen Aufträgen
            table_frame = ttk.Frame(auftrag_frame)
            table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            columns = ('id', 'kunde', 'beschreibung', 'status', 'datum')
            self.auftraege_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
            
            self.auftraege_tree.heading('id', text='ID')
            self.auftraege_tree.heading('kunde', text='Kunde')
            self.auftraege_tree.heading('beschreibung', text='Beschreibung')
            self.auftraege_tree.heading('status', text='Status')
            self.auftraege_tree.heading('datum', text='Datum')
            
            self.auftraege_tree.column('id', width=50, anchor='center')
            self.auftraege_tree.column('kunde', width=150)
            self.auftraege_tree.column('beschreibung', width=200)
            self.auftraege_tree.column('status', width=100)
            self.auftraege_tree.column('datum', width=80)
            
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.auftraege_tree.yview)
            self.auftraege_tree.configure(yscrollcommand=vsb.set)
            
            vsb.pack(side="right", fill="y")
            self.auftraege_tree.pack(side="left", fill="both", expand=True)
            
            # Aufträge laden
            self.load_auftraege()
            
            # Auftrag auswählen-Button
            ttk.Button(auftrag_frame, text="Auftrag auswählen", command=self.select_auftrag).pack(side="right", padx=5, pady=5)
            
            # Rest des Dialogs wird erst angezeigt, wenn ein Auftrag ausgewählt wurde
            self.rechnungsdaten_frame = None
            
            # Event-Handler für Doppelklick
            self.auftraege_tree.bind("<Double-1>", lambda event: self.select_auftrag())
        else:
            # Direkt Rechnungsdaten anzeigen, wenn Auftrag bekannt ist
            self.create_rechnung_view(main_frame)
            
        self.dialog.wait_window()

    

    def generate_pdf(self, output_path):
        """Erzeugt eine PDF-Datei für die Rechnung"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            
            # Titel
            elements.append(Paragraph(f"Rechnung {self.rechnungsnr_var.get()}", styles['Title']))
            elements.append(Spacer(1, 20))
            
            # Firmeninfo
            elements.append(Paragraph("AutoMeister - Werkstattverwaltung", styles['Heading2']))
            elements.append(Paragraph("Musterstrasse 123", styles['Normal']))
            elements.append(Paragraph("1234 Musterhausen", styles['Normal']))
            elements.append(Paragraph("Schweiz", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Kundendaten
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT k.vorname, k.nachname, k.anschrift 
            FROM kunden k
            JOIN auftraege a ON k.id = a.kunden_id
            WHERE a.id = ?
            """, (self.auftrag_id,))
            
            kunde = cursor.fetchone()
            if kunde:
                elements.append(Paragraph(f"Kunde: {kunde[0]} {kunde[1]}", styles['Heading3']))
                elements.append(Paragraph(f"Anschrift: {kunde[2] or 'Keine Anschrift angegeben'}", styles['Normal']))
                elements.append(Spacer(1, 20))
            
            # Positionen als Tabelle
            positionen_data = [["Pos", "Bezeichnung", "Menge", "Einzelpreis", "Gesamtpreis"]]
            
            # Gesamtsumme
            gesamtsumme = 0
            
            # Positionen hinzufügen
            for i, item in enumerate(self.positionen_tree.get_children(), 1):
                values = self.positionen_tree.item(item)['values']
                bezeichnung = values[1]
                menge = values[2]
                einzelpreis = values[3].replace(" €", "").replace(" CHF", "")
                gesamtpreis = values[4].replace(" €", "").replace(" CHF", "")
                
                positionen_data.append([i, bezeichnung, menge, f"{einzelpreis} CHF", f"{gesamtpreis} CHF"])
                
                try:
                    gesamtsumme += float(gesamtpreis.replace(',', '.'))
                except:
                    pass
            
            # MwSt berechnen
            mwst = gesamtsumme * mwst_satz / 100
            
            # MwSt und Gesamtsumme hinzufügen
            positionen_data.append(["", "", "", "Zwischensumme:", f"{gesamtsumme:.2f} CHF"])
            positionen_data.append(["", "", "", f"MwSt ({mwst_satz}%):", f"{mwst:.2f} CHF"])
            positionen_data.append(["", "", "", "Gesamtbetrag:", f"{gesamtsumme + mwst:.2f} CHF"])
            
            # Tabelle erstellen
            table = Table(positionen_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('SPAN', (0, -3), (2, -3)),
                ('SPAN', (0, -2), (2, -2)),
                ('SPAN', (0, -1), (2, -1)),
                ('ALIGN', (3, -3), (4, -1), 'RIGHT'),
                ('FONTNAME', (3, -1), (4, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Hinweise
            elements.append(Paragraph("Hinweise:", styles['Heading4']))
            elements.append(Paragraph(self.notizen_text.get(1.0, tk.END).strip() or "Vielen Dank für Ihren Auftrag!", styles['Normal']))
            
            # Zahlungsinformationen
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Zahlungsinformationen:", styles['Heading4']))
            elements.append(Paragraph("Bitte überweisen Sie den Betrag innerhalb von 30 Tagen auf folgendes Konto:", styles['Normal']))
            elements.append(Paragraph("Bank: Musterbank", styles['Normal']))
            elements.append(Paragraph("IBAN: CH00 0000 0000 0000 0000 0", styles['Normal']))
            elements.append(Paragraph(f"Verwendungszweck: {self.rechnungsnr_var.get()}", styles['Normal']))
            
            # PDF erstellen
            doc.build(elements)
            return True
        except Exception as e:
            print(f"Fehler beim Erstellen der PDF: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der PDF: {e}")
            return False

    def save_rechnung_pdf(app):
        """Speichert eine Rechnung als PDF"""
        from tkinter import filedialog
        import os
        
        rechnung_id = get_selected_rechnung_id(app)
        if not rechnung_id:
            messagebox.showinfo("Information", "Bitte wählen Sie eine Rechnung aus.")
            return
            
        rechnung_nr = app.rechnungen_widgets['rechnungen_tree'].item(app.rechnungen_widgets['rechnungen_tree'].selection()[0])['values'][1]
        
        # Dateiname vorschlagen
        default_filename = f"Rechnung_{rechnung_nr.replace(' ', '_')}.pdf"
        
        # Speicherort auswählen
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialfile=default_filename
        )
        
        if not file_path:
            return  # Abgebrochen durch Benutzer
        
        # PDF generieren
        rechnungs_anzeige = RechnungsAnzeigeDialog(app.root, "Rechnung als PDF speichern", rechnung_id, app.conn, preview_only=True)
        if rechnungs_anzeige.generate_pdf(file_path):
            messagebox.showinfo("Information", f"Rechnung wurde als PDF gespeichert: {file_path}")
            
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
    
    def load_auftraege(self):
        """Lädt abgeschlossene Aufträge ohne Rechnung"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.beschreibung, a.status,
               strftime('%d.%m.%Y', a.erstellt_am) as datum
        FROM auftraege a
        JOIN kunden k ON a.kunden_id = k.id
        LEFT JOIN rechnungen r ON a.id = r.auftrag_id
        WHERE r.id IS NULL
        ORDER BY a.erstellt_am DESC
        """)
        
        # Tabelle leeren
        for item in self.auftraege_tree.get_children():
            self.auftraege_tree.delete(item)
            
        # Daten einfügen
        for row in cursor.fetchall():
            self.auftraege_tree.insert('', 'end', values=row)
            
    def select_auftrag(self):
        """Wählt einen Auftrag aus und zeigt die Rechnungsdaten an"""
        selected_items = self.auftraege_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
            return
            
        # Auftrag auswählen
        self.auftrag_id = self.auftraege_tree.item(selected_items[0])['values'][0]
        
        # Auftragsauswahl ausblenden
        for widget in self.dialog.winfo_children():
            widget.destroy()
            
        # Hauptframe neu erstellen
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Rechnungsdaten anzeigen
        self.create_rechnung_view(main_frame)
        
    def create_rechnung_view(self, parent_frame=None):
        """Erstellt die Ansicht für die Rechnungsdaten"""
        if parent_frame is None:
            parent_frame = ttk.Frame(self.dialog, padding=10)
            parent_frame.pack(fill="both", expand=True)
            
        # Rechnungsdaten
        self.rechnungsdaten_frame = ttk.LabelFrame(parent_frame, text="Rechnungsdaten")
        self.rechnungsdaten_frame.pack(fill="x", expand=False, pady=5)
        
        # Auftragsinformationen anzeigen
        if self.auftrag_id:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.beschreibung
            FROM auftraege a
            JOIN kunden k ON a.kunden_id = k.id
            WHERE a.id = ?
            """, (self.auftrag_id,))
            
            auftrag = cursor.fetchone()
            if auftrag:
                auftrag_info = ttk.Label(self.rechnungsdaten_frame, 
                                       text=f"Auftrag: #{auftrag[0]} - {auftrag[2]} (Kunde: {auftrag[1]})",
                                       font=("Arial", 10, "bold"))
                auftrag_info.grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.rechnungsdaten_frame, text="Rechnungsnummer:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.rechnungsnr_var = tk.StringVar()
        ttk.Entry(self.rechnungsdaten_frame, textvariable=self.rechnungsnr_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Automatische Rechnungsnummer generieren
        self.generate_rechnung_nummer()
        
        ttk.Label(self.rechnungsdaten_frame, text="Datum:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.datum_var = tk.StringVar(value=datetime.now().strftime('%d.%m.%Y'))
        ttk.Entry(self.rechnungsdaten_frame, textvariable=self.datum_var, width=15).grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.rechnungsdaten_frame, text="Zahlungsziel (Tage):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.zahlungsziel_var = tk.StringVar(value="14")
        ttk.Spinbox(self.rechnungsdaten_frame, from_=0, to=90, textvariable=self.zahlungsziel_var, width=5).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.rechnungsdaten_frame, text="Notizen:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.notizen_text = tk.Text(self.rechnungsdaten_frame, height=3, width=50)
        self.notizen_text.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Standardtext einfügen
        self.notizen_text.insert(tk.END, "Vielen Dank für Ihren Auftrag. Bitte überweisen Sie den Betrag innerhalb der Zahlungsfrist.")
        
        # Rechnungspositionen
        positionen_frame = ttk.LabelFrame(parent_frame, text="Rechnungspositionen")
        positionen_frame.pack(fill="both", expand=True, pady=5)
        
        # Tabelle für Positionen
        table_frame = ttk.Frame(positionen_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ('pos', 'bezeichnung', 'menge', 'einzelpreis', 'gesamtpreis')
        self.positionen_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.positionen_tree.heading('pos', text='#')
        self.positionen_tree.heading('bezeichnung', text='Bezeichnung')
        self.positionen_tree.heading('menge', text='Menge')
        self.positionen_tree.heading('einzelpreis', text='Einzelpreis')
        self.positionen_tree.heading('gesamtpreis', text='Gesamtpreis')
        
        self.positionen_tree.column('pos', width=30, anchor='center')
        self.positionen_tree.column('bezeichnung', width=300)
        self.positionen_tree.column('menge', width=50, anchor='center')
        self.positionen_tree.column('einzelpreis', width=80, anchor='e')
        self.positionen_tree.column('gesamtpreis', width=80, anchor='e')
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.positionen_tree.yview)
        self.positionen_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.positionen_tree.pack(side="left", fill="both", expand=True)
        
        # Buttons für Positionen
        btn_frame = ttk.Frame(positionen_frame)
        btn_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Position hinzufügen", command=self.add_position).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Position bearbeiten", command=self.edit_position).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Position entfernen", command=self.remove_position).pack(side="left", padx=5)
        
        # Zusammenfassung
        summary_frame = ttk.Frame(parent_frame)
        summary_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(summary_frame, text="Gesamtbetrag:").pack(side="left", padx=5)
        self.gesamtbetrag_var = tk.StringVar(value="0.00 €")
        ttk.Label(summary_frame, textvariable=self.gesamtbetrag_var, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Rechnung speichern", command=self.save_rechnung).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Positionen automatisch aus Auftrag laden
        self.load_auftrag_positionen()
        
    def generate_rechnung_nummer(self):
        """Generiert eine neue Rechnungsnummer"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rechnungen")
        count = cursor.fetchone()[0] + 1
        
        # Format: RE-JAHR-NUMMER (z.B. RE-2023-0001)
        rechnungsnr = f"RE-{datetime.now().year}-{count:04d}"
        self.rechnungsnr_var.set(rechnungsnr)
        
    def load_auftrag_positionen(self):
        """Lädt die Positionen aus dem ausgewählten Auftrag"""
        if not self.auftrag_id:
            return
            
        cursor = self.conn.cursor()
        
        # Verwendete Ersatzteile laden
        cursor.execute("""
        SELECT e.bezeichnung, ae.menge, ae.einzelpreis, ae.menge * ae.einzelpreis as gesamtpreis
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (self.auftrag_id,))
        
        # Tabelle leeren
        for item in self.positionen_tree.get_children():
            self.positionen_tree.delete(item)
            
        # Positionen einfügen
        pos = 1
        summe = 0
        
        # Ersatzteile hinzufügen
        for row in cursor.fetchall():
            einzelpreis = row[2]
            gesamtpreis = row[3]
            summe += gesamtpreis
            
            self.positionen_tree.insert('', 'end', values=(pos, row[0], row[1], f"{einzelpreis:.2f} €", f"{gesamtpreis:.2f} €"))
            pos += 1
            
        # Arbeitszeit hinzufügen
        cursor.execute("SELECT beschreibung, arbeitszeit FROM auftraege WHERE id = ?", (self.auftrag_id,))
        auftrag = cursor.fetchone()
        
        if auftrag and auftrag[1] > 0:
            stundensatz = 60.0  # Fester Stundensatz in €
            arbeitszeit = auftrag[1]
            arbeitskosten = arbeitszeit * stundensatz
            summe += arbeitskosten
            
            self.positionen_tree.insert('', 'end', values=(
                pos, 
                f"Arbeitszeit: {auftrag[0]}", 
                f"{arbeitszeit:.2f} h", 
                f"{stundensatz:.2f} €/h", 
                f"{arbeitskosten:.2f} €"
            ))
            
        # Gesamtbetrag aktualisieren
        self.gesamtbetrag_var.set(f"{summe:.2f} €")
        
    def add_position(self):
        """Fügt eine manuelle Position zur Rechnung hinzu"""
        position_dialog = PositionDialog(self.dialog, "Position hinzufügen")
        
        if position_dialog.result:
            bezeichnung, menge, einzelpreis = position_dialog.result
            
            # Positionsnummer bestimmen
            pos = len(self.positionen_tree.get_children()) + 1
            
            # Gesamtpreis berechnen
            gesamtpreis = menge * einzelpreis
            
            # Position einfügen
            self.positionen_tree.insert('', 'end', values=(
                pos, bezeichnung, menge, f"{einzelpreis:.2f} €", f"{gesamtpreis:.2f} €"
            ))
            
            # Gesamtbetrag aktualisieren
            self.update_gesamtbetrag()
            
    def edit_position(self):
        """Bearbeitet eine Position"""
        selected_items = self.positionen_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie eine Position aus.")
            return
            
        # Aktuelle Werte auslesen
        values = self.positionen_tree.item(selected_items[0])['values']
        bezeichnung = values[1]
        menge_str = str(values[2])
        
        # Einheiten entfernen, wenn vorhanden
        if " h" in menge_str:
            menge_str = menge_str.replace(" h", "")
            
        menge = float(menge_str)
        
        einzelpreis_str = str(values[3])
        if " €/h" in einzelpreis_str:
            einzelpreis_str = einzelpreis_str.replace(" €/h", "")
        elif " €" in einzelpreis_str:
            einzelpreis_str = einzelpreis_str.replace(" €", "")
            
        einzelpreis = float(einzelpreis_str.replace(',', '.'))
        
        # Dialog zur Bearbeitung
        position_dialog = PositionDialog(self.dialog, "Position bearbeiten", 
                                        bezeichnung, menge, einzelpreis)
        
        if position_dialog.result:
            neue_bezeichnung, neue_menge, neuer_einzelpreis = position_dialog.result
            
            # Gesamtpreis berechnen
            gesamtpreis = neue_menge * neuer_einzelpreis
            
            # Position aktualisieren
            self.positionen_tree.item(selected_items[0], values=(
                values[0], neue_bezeichnung, neue_menge, 
                f"{neuer_einzelpreis:.2f} €", f"{gesamtpreis:.2f} €"
            ))
            
            # Gesamtbetrag aktualisieren
            self.update_gesamtbetrag()
            
    def remove_position(self):
        """Entfernt eine Position"""
        selected_items = self.positionen_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie eine Position aus.")
            return
            
        # Position entfernen
        self.positionen_tree.delete(selected_items[0])
        
        # Positionen neu nummerieren
        self.renumber_positions()
        
        # Gesamtbetrag aktualisieren
        self.update_gesamtbetrag()
        
    def renumber_positions(self):
        """Nummeriert die Positionen neu durch"""
        items = self.positionen_tree.get_children()
        
        for i, item in enumerate(items, start=1):
            values = self.positionen_tree.item(item)['values']
            self.positionen_tree.item(item, values=(i, values[1], values[2], values[3], values[4]))
            
    def update_gesamtbetrag(self):
        """Aktualisiert den Gesamtbetrag der Rechnung"""
        summe = 0
        
        for item in self.positionen_tree.get_children():
            gesamtpreis_str = self.positionen_tree.item(item)['values'][4]
            
            # Euro-Zeichen entfernen
            if " €" in gesamtpreis_str:
                gesamtpreis_str = gesamtpreis_str.replace(" €", "")
                
            summe += float(gesamtpreis_str.replace(',', '.'))
            
        self.gesamtbetrag_var.set(f"{summe:.2f} €")
        
   


class PositionDialog:
    """Dialog zum Hinzufügen oder Bearbeiten einer Rechnungsposition"""
    def __init__(self, parent, title, bezeichnung=None, menge=None, einzelpreis=None):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Eingabefelder
        ttk.Label(main_frame, text="Bezeichnung:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.bezeichnung_var = tk.StringVar(value=bezeichnung or "")
        ttk.Entry(main_frame, textvariable=self.bezeichnung_var, width=40).grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Menge:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.menge_var = tk.StringVar(value=str(menge) if menge is not None else "1")
        ttk.Spinbox(main_frame, from_=0.01, to=9999, increment=0.01, textvariable=self.menge_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Einzelpreis (€):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.einzelpreis_var = tk.StringVar(value=f"{einzelpreis:.2f}" if einzelpreis is not None else "0.00")
        ttk.Entry(main_frame, textvariable=self.einzelpreis_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="e", pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        self.dialog.wait_window()
        
    def save_data(self):
        """Speichert die Positionsdaten"""
        # Pflichtfelder prüfen
        if not self.bezeichnung_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie eine Bezeichnung ein.")
            return
            
        try:
            menge = float(self.menge_var.get().replace(',', '.'))
            einzelpreis = float(self.einzelpreis_var.get().replace(',', '.'))
            
            if menge <= 0 or einzelpreis < 0:
                messagebox.showerror("Fehler", "Menge muss größer als 0 und Preis darf nicht negativ sein.")
                return
            
            self.result = (self.bezeichnung_var.get(), menge, einzelpreis)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Werte für Menge und Preis ein.")


class RechnungsAnzeigeDialog:
    """Dialog zur Anzeige einer Rechnung"""
    def __init__(self, parent, title, rechnung_id, conn):
        self.parent = parent
        self.rechnung_id = rechnung_id
        self.conn = conn
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Rechnungsanzeige (als Text mit Formatierung)
        self.rechnung_text = tk.Text(main_frame, wrap="word", padx=10, pady=10, font=("Courier", 10))
        self.rechnung_text.pack(fill="both", expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Drucken", command=self.print_rechnung).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Als PDF speichern", command=self.save_pdf).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Schließen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Rechnungsdaten laden und anzeigen
        self.load_rechnung()
        
    def load_rechnung(self):
        """Lädt und formatiert die Rechnungsdaten"""
        cursor = self.conn.cursor()
        
        # Rechnungskopfdaten
        cursor.execute("""
        SELECT r.rechnungsnummer, strftime('%d.%m.%Y', r.datum) as datum, 
               k.vorname || ' ' || k.nachname as kunde, k.anschrift,
               a.id as auftrag_id, a.beschreibung,
               r.gesamtbetrag, r.notizen
        FROM rechnungen r
        JOIN auftraege a ON r.auftrag_id = a.id
        JOIN kunden k ON a.kunden_id = k.id
        WHERE r.id = ?
        """, (self.rechnung_id,))
        
        rechnung = cursor.fetchone()
        if not rechnung:
            self.rechnung_text.insert(tk.END, "Fehler: Rechnung nicht gefunden.")
            return
            
        # Positionen
        cursor.execute("""
        SELECT e.bezeichnung, ae.menge, ae.einzelpreis, ae.menge * ae.einzelpreis as gesamtpreis
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (rechnung[4],))
        
        ersatzteile = cursor.fetchall()
        
        # Arbeitszeit
        cursor.execute("SELECT arbeitszeit FROM auftraege WHERE id = ?", (rechnung[4],))
        arbeitszeit = cursor.fetchone()[0]
        
        # Rechnungsformatierung
        self.rechnung_text.insert(tk.END, "AUTOWERKSTATT MEISTER\n")
        self.rechnung_text.insert(tk.END, "Musterstraße 123\n")
        self.rechnung_text.insert(tk.END, "12345 Musterstadt\n")
        self.rechnung_text.insert(tk.END, "Tel: 0123-456789\n")
        self.rechnung_text.insert(tk.END, "Email: info@autowerkstatt-meister.de\n\n")
        
        self.rechnung_text.insert(tk.END, f"RECHNUNG {rechnung[0]}\n")
        self.rechnung_text.insert(tk.END, f"Datum: {rechnung[1]}\n\n")
        
        self.rechnung_text.insert(tk.END, f"KUNDE:\n{rechnung[2]}\n{rechnung[3] or 'Keine Anschrift angegeben'}\n\n")
        
        self.rechnung_text.insert(tk.END, f"AUFTRAG: #{rechnung[4]}\n")
        self.rechnung_text.insert(tk.END, f"Beschreibung: {rechnung[5]}\n\n")
        
        self.rechnung_text.insert(tk.END, "POSITIONEN:\n")
        self.rechnung_text.insert(tk.END, f"{'#':<3} {'Bezeichnung':<40} {'Menge':<10} {'Einzelpreis':<15} {'Gesamtpreis':<15}\n")
        self.rechnung_text.insert(tk.END, "-" * 85 + "\n")
        
        pos = 1
        summe = 0
        
        # Ersatzteile
        for teil in ersatzteile:
            bezeichnung = teil[0]
            menge = teil[1]
            einzelpreis = teil[2]
            gesamtpreis = teil[3]
            summe += gesamtpreis
            
            self.rechnung_text.insert(tk.END, f"{pos:<3} {bezeichnung:<40} {menge:<10} {einzelpreis:>12.2f} € {gesamtpreis:>12.2f} €\n")
            pos += 1
            
        # Arbeitszeit
        if arbeitszeit > 0:
            stundensatz = 60.0
            arbeitskosten = arbeitszeit * stundensatz
            summe += arbeitskosten
            
            self.rechnung_text.insert(tk.END, f"{pos:<3} {'Arbeitszeit: ' + rechnung[5]:<40} {arbeitszeit:<10.2f} h {stundensatz:>12.2f} € {arbeitskosten:>12.2f} €\n")
            
        self.rechnung_text.insert(tk.END, "-" * 85 + "\n")
        self.rechnung_text.insert(tk.END, f"GESAMTBETRAG: {rechnung[6]:>51.2f} €\n\n")
        
        self.rechnung_text.insert(tk.END, f"HINWEISE:\n{rechnung[7]}\n\n")
        
        self.rechnung_text.insert(tk.END, "ZAHLUNGSINFORMATIONEN:\n")
        self.rechnung_text.insert(tk.END, "Bitte überweisen Sie den Betrag innerhalb von 14 Tagen auf folgendes Konto:\n")
        self.rechnung_text.insert(tk.END, "Bank: Musterbank\n")
        self.rechnung_text.insert(tk.END, "IBAN: DE12 3456 7890 1234 5678 90\n")
        self.rechnung_text.insert(tk.END, "BIC: MUSTEBANK123\n")
        self.rechnung_text.insert(tk.END, f"Verwendungszweck: {rechnung[0]}\n\n")
        
        self.rechnung_text.insert(tk.END, "Vielen Dank für Ihren Auftrag!\n")
        
        # Schreibschutz aktivieren
        self.rechnung_text.config(state="disabled")
        
    def print_rechnung(self):
        """Druckt die Rechnung"""
        # Hinweis anzeigen (Druck-Funktionalität würde in einer produktiven Anwendung implementiert)
        messagebox.showinfo("Hinweis", "Druckfunktionalität ist in dieser Demo nicht vollständig implementiert. Die Rechnung würde nun gedruckt werden.")

    def save_pdf(self):
        """Speichert die Rechnung als PDF"""
        # Hinweis anzeigen (PDF-Export würde in einer produktiven Anwendung implementiert)
        messagebox.showinfo("Hinweis", "PDF-Export ist in dieser Demo nicht vollständig implementiert. Die Rechnung würde nun als PDF gespeichert werden.")#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialoge für Rechnungen
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

class RechnungsDialog:
    """Dialog zum Erstellen einer Rechnung"""
    def __init__(self, parent, title, rechnung_id=None, conn=None, auftrag_id=None):
        self.parent = parent
        self.rechnung_id = rechnung_id
        self.conn = conn
        self.auftrag_id = auftrag_id
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Wenn keine Rechnung bearbeitet wird und kein Auftrag vorgegeben ist
        if not self.rechnung_id and not self.auftrag_id:
            # Auftragsauswahl
            auftrag_frame = ttk.LabelFrame(main_frame, text="Auftrag auswählen")
            auftrag_frame.pack(fill="x", expand=False, pady=5)
            
            # Tabelle mit offenen Aufträgen
            table_frame = ttk.Frame(auftrag_frame)
            table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            columns = ('id', 'kunde', 'beschreibung', 'status', 'datum')
            self.auftraege_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
            
            self.auftraege_tree.heading('id', text='ID')
            self.auftraege_tree.heading('kunde', text='Kunde')
            self.auftraege_tree.heading('beschreibung', text='Beschreibung')
            self.auftraege_tree.heading('status', text='Status')
            self.auftraege_tree.heading('datum', text='Datum')
            
            self.auftraege_tree.column('id', width=50, anchor='center')
            self.auftraege_tree.column('kunde', width=150)
            self.auftraege_tree.column('beschreibung', width=200)
            self.auftraege_tree.column('status', width=100)
            self.auftraege_tree.column('datum', width=80)
            
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.auftraege_tree.yview)
            self.auftraege_tree.configure(yscrollcommand=vsb.set)
            
            vsb.pack(side="right", fill="y")
            self.auftraege_tree.pack(side="left", fill="both", expand=True)
            
            # Aufträge laden
            self.load_auftraege()
            
            # Auftrag auswählen-Button
            ttk.Button(auftrag_frame, text="Auftrag auswählen", command=self.select_auftrag).pack(side="right", padx=5, pady=5)
            
            # Rest des Dialogs wird erst angezeigt, wenn ein Auftrag ausgewählt wurde
            self.rechnungsdaten_frame = None
            
            # Event-Handler für Doppelklick
            self.auftraege_tree.bind("<Double-1>", lambda event: self.select_auftrag())
        else:
            # Direkt Rechnungsdaten anzeigen, wenn Auftrag bekannt ist
            self.create_rechnung_view(main_frame)
            
        self.dialog.wait_window()
        
    def load_auftraege(self):
        """Lädt abgeschlossene Aufträge ohne Rechnung"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT a.id, k.vorname || ' ' || k.nachname as kunde, a.beschreibung, a.status,
               strftime('%d.%m.%Y', a.erstellt_am) as datum
        FROM auftraege a
        JOIN kunden k ON a.kunden_id = k.id
        LEFT JOIN rechnungen r ON a.id = r.auftrag_id
        WHERE r.id IS NULL
        ORDER BY a.erstellt_am DESC
        """)
        
        # Tabelle leeren
        for item in self.auftraege_tree.get_children():
            self.auftraege_tree.delete(item)
            
        # Daten einfügen
        for row in cursor.fetchall():
            self.auftraege_tree.insert('', 'end', values=row)
            
    def select_auftrag(self):
        """Wählt einen Auftrag aus und zeigt die Rechnungsdaten an"""
        selected_items = self.auftraege_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie einen Auftrag aus.")
            return
            
        # Auftrag auswählen
        self.auftrag_id = self.auftraege_tree.item(selected_items[0])['values'][0]
        
        # Auftragsauswahl ausblenden
        for widget in self.dialog.winfo_children():
            widget.destroy()
            
        # Hauptframe neu erstellen
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        #