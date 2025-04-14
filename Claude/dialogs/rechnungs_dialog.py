#!/usr/bin/env python3
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
        self.zahlungsziel_var = tk.StringVar(value="30")
        ttk.Spinbox(self.rechnungsdaten_frame, from_=0, to=90, textvariable=self.zahlungsziel_var, width=5).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Rabatt hinzufügen
        ttk.Label(self.rechnungsdaten_frame, text="Rabatt (%):").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.rabatt_var = tk.StringVar(value="0")
        ttk.Spinbox(self.rechnungsdaten_frame, from_=0, to=100, textvariable=self.rabatt_var, width=5).grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
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
        self.gesamtbetrag_var = tk.StringVar(value="0.00 CHF")
        ttk.Label(summary_frame, textvariable=self.gesamtbetrag_var, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Rechnung speichern", command=self.save_rechnung).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Vorschau als PDF", command=self.preview_pdf).pack(side="left", padx=5)
        
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
            
            self.positionen_tree.insert('', 'end', values=(pos, row[0], row[1], f"{einzelpreis:.2f} CHF", f"{gesamtpreis:.2f} CHF"))
            pos += 1
            
        # Arbeitszeit hinzufügen
        cursor.execute("SELECT beschreibung, arbeitszeit FROM auftraege WHERE id = ?", (self.auftrag_id,))
        auftrag = cursor.fetchone()
        
        if auftrag and auftrag[1] > 0:
            # Stundensatz aus Konfiguration laden
            from utils.config import get_default_stundenlohn
            stundensatz = get_default_stundenlohn(self.conn)
            
            arbeitszeit = auftrag[1]
            arbeitskosten = arbeitszeit * stundensatz
            summe += arbeitskosten
            
            self.positionen_tree.insert('', 'end', values=(
                pos, 
                f"Arbeitszeit: {auftrag[0]}", 
                f"{arbeitszeit:.2f} h", 
                f"{stundensatz:.2f} CHF/h", 
                f"{arbeitskosten:.2f} CHF"
            ))
            
        # Gesamtbetrag aktualisieren
        self.gesamtbetrag_var.set(f"{summe:.2f} CHF")
    
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
                pos, bezeichnung, menge, f"{einzelpreis:.2f} CHF", f"{gesamtpreis:.2f} CHF"
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
        if " CHF/h" in einzelpreis_str:
            einzelpreis_str = einzelpreis_str.replace(" CHF/h", "")
        elif " CHF" in einzelpreis_str:
            einzelpreis_str = einzelpreis_str.replace(" CHF", "")
            
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
                f"{neuer_einzelpreis:.2f} CHF", f"{gesamtpreis:.2f} CHF"
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
            
            # CHF-Zeichen entfernen
            if " CHF" in gesamtpreis_str:
                gesamtpreis_str = gesamtpreis_str.replace(" CHF", "")
                
            summe += float(gesamtpreis_str.replace(',', '.'))
            
        self.gesamtbetrag_var.set(f"{summe:.2f} CHF")

    def save_rechnung(self):
        """Speichert die Rechnung"""
        # Pflichtfelder prüfen
        if not self.rechnungsnr_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie eine Rechnungsnummer ein.")
            return
            
        if not self.auftrag_id:
            messagebox.showerror("Fehler", "Kein Auftrag ausgewählt.")
            return
            
        if not self.positionen_tree.get_children():
            messagebox.showerror("Fehler", "Die Rechnung enthält keine Positionen.")
            return
            
        try:
            # Datum konvertieren
            try:
                datum_parts = self.datum_var.get().split('.')
                datum_db = f"{datum_parts[2]}-{datum_parts[1]}-{datum_parts[0]}"
            except:
                messagebox.showerror("Fehler", "Ungültiges Datumsformat. Bitte verwenden Sie TT.MM.JJJJ.")
                return
                
            # Gesamtbetrag extrahieren
            gesamtbetrag_str = self.gesamtbetrag_var.get().replace('CHF', '').strip()
            gesamtbetrag = float(gesamtbetrag_str.replace(',', '.'))
            
            # Rabatt extrahieren
            try:
                rabatt = float(self.rabatt_var.get().replace(',', '.'))
                if rabatt < 0 or rabatt > 100:
                    raise ValueError("Rabatt muss zwischen 0 und 100 liegen")
            except ValueError:
                messagebox.showerror("Fehler", "Ungültiger Rabattwert")
                return
                
            cursor = self.conn.cursor()
            
            if self.rechnung_id:  # Bestehende Rechnung aktualisieren
                cursor.execute("""
                UPDATE rechnungen SET 
                    auftrag_id = ?, rechnungsnummer = ?, datum = ?, gesamtbetrag = ?,
                    notizen = ?, rabatt_prozent = ?
                WHERE id = ?
                """, (
                    self.auftrag_id, self.rechnungsnr_var.get(), datum_db, 
                    gesamtbetrag, self.notizen_text.get(1.0, tk.END).strip(),
                    rabatt, self.rechnung_id
                ))
            else:  # Neue Rechnung erstellen
                cursor.execute("""
                INSERT INTO rechnungen (
                    auftrag_id, rechnungsnummer, datum, gesamtbetrag, notizen, rabatt_prozent
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.auftrag_id, self.rechnungsnr_var.get(), datum_db, 
                    gesamtbetrag, self.notizen_text.get(1.0, tk.END).strip(), rabatt
                ))
                
                # Auftrag als abgeschlossen markieren
                cursor.execute("""
                UPDATE auftraege SET 
                    status = 'Abgeschlossen',
                    abgeschlossen_am = datetime('now')
                WHERE id = ? AND status != 'Abgeschlossen'
                """, (self.auftrag_id,))
                
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Rechnung: {e}")
            self.conn.rollback()
            
    def preview_pdf(self):
        """Zeigt eine Vorschau der Rechnung als PDF an"""
        # Zuerst temporär speichern, um die Rechnung-ID zu erhalten
        if not self.auftrag_id:
            messagebox.showerror("Fehler", "Kein Auftrag ausgewählt.")
            return
            
        # Aktuelle Eingaben validieren
        try:
            # Gesamtbetrag extrahieren
            gesamtbetrag_str = self.gesamtbetrag_var.get().replace('CHF', '').strip()
            gesamtbetrag = float(gesamtbetrag_str.replace(',', '.'))
            
            # Rabatt extrahieren
            rabatt = float(self.rabatt_var.get().replace(',', '.'))
            if rabatt < 0 or rabatt > 100:
                raise ValueError("Rabatt muss zwischen 0 und 100 liegen")
                
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Werte in der Rechnung. Bitte überprüfen Sie Ihre Eingaben.")
            return
        
        # Temporäre Rechnung erstellen oder bestehende Rechnung verwenden
        rechnung_id = None
        temp_rechnung_erstellt = False
        
        try:
            cursor = self.conn.cursor()
            
            if self.rechnung_id:
                # Bestehende Rechnung aktualisieren
                rechnung_id = self.rechnung_id
                
                # Datum konvertieren
                datum_parts = self.datum_var.get().split('.')
                datum_db = f"{datum_parts[2]}-{datum_parts[1]}-{datum_parts[0]}"
                
                cursor.execute("""
                UPDATE rechnungen SET 
                    auftrag_id = ?, rechnungsnummer = ?, datum = ?, gesamtbetrag = ?,
                    notizen = ?, rabatt_prozent = ?
                WHERE id = ?
                """, (
                    self.auftrag_id, self.rechnungsnr_var.get(), datum_db, 
                    gesamtbetrag, self.notizen_text.get(1.0, tk.END).strip(),
                    rabatt, rechnung_id
                ))
                
            else:
                # Prüfen, ob bereits eine Rechnung für diesen Auftrag existiert
                cursor.execute("SELECT id FROM rechnungen WHERE auftrag_id = ?", (self.auftrag_id,))
                existing = cursor.fetchone()
                
                if existing:
                    rechnung_id = existing[0]
                else:
                    # Datum konvertieren
                    datum_parts = self.datum_var.get().split('.')
                    datum_db = f"{datum_parts[2]}-{datum_parts[1]}-{datum_parts[0]}"
                    
                    # Temporäre Rechnung erstellen
                    cursor.execute("""
                    INSERT INTO rechnungen (
                        auftrag_id, rechnungsnummer, datum, gesamtbetrag, notizen, rabatt_prozent
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        self.auftrag_id, self.rechnungsnr_var.get(), datum_db, 
                        gesamtbetrag, self.notizen_text.get(1.0, tk.END).strip(), rabatt
                    ))
                    
                    # ID der eingefügten Rechnung abrufen
                    cursor.execute("SELECT last_insert_rowid()")
                    rechnung_id = cursor.fetchone()[0]
                    temp_rechnung_erstellt = True
            
            self.conn.commit()
            
            # PDF generieren
            from utils.pdf_generator import generate_invoice_pdf
            import os
            import subprocess
            
            success, pdf_path = generate_invoice_pdf(self.conn, rechnung_id)

            if success:
                # PDF-Datei öffnen
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(pdf_path)
                    elif os.name == 'posix':  # Linux, Mac
                        if os.system('command -v xdg-open') == 0:  # Linux
                            subprocess.call(['xdg-open', pdf_path])
                        else:  # Mac
                            subprocess.call(['open', pdf_path])
                except Exception as e:
                    messagebox.showinfo("Information", f"PDF wurde erstellt, konnte aber nicht automatisch geöffnet werden: {pdf_path}")
            else:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen der PDF: {pdf_path}")
                
            # Wenn eine temporäre Rechnung erstellt wurde, diese wieder löschen
            if temp_rechnung_erstellt:
                cursor.execute("DELETE FROM rechnungen WHERE id = ?", (rechnung_id,))
                self.conn.commit()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der PDF-Vorschau: {e}")
            if temp_rechnung_erstellt and rechnung_id:
                # Temporäre Rechnung wieder löschen, falls erstellt
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM rechnungen WHERE id = ?", (rechnung_id,))
                self.conn.commit()


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
        
        ttk.Label(main_frame, text="Einzelpreis (CHF):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
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
        
        ttk.Button(btn_frame, text="Als PDF anzeigen", command=self.show_pdf).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Als PDF speichern", command=self.save_pdf).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Drucken", command=self.print_rechnung).pack(side="left", padx=5)
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
               r.gesamtbetrag, r.notizen, r.rabatt_prozent
        FROM rechnungen r
        JOIN auftraege a ON r.auftrag_id = a.id
        JOIN kunden k ON a.kunden_id = k.id
        WHERE r.id = ?
        """, (self.rechnung_id,))
        
        rechnung = cursor.fetchone()
        if not rechnung:
            self.rechnung_text.insert(tk.END, "Fehler: Rechnung nicht gefunden.")
            return
            
        rechnungsnr, datum, kundenname, anschrift, auftrag_id, auftrag_beschreibung, gesamtbetrag, notizen, rabatt_prozent = rechnung
        
        if rabatt_prozent is None:
            rabatt_prozent = 0
        
        # Positionen abrufen (Ersatzteile)
        cursor.execute("""
        SELECT e.bezeichnung, ae.menge, ae.einzelpreis, ae.menge * ae.einzelpreis as gesamtpreis
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (auftrag_id,))
        
        ersatzteile = cursor.fetchall()
        
        # Arbeitszeit
        cursor.execute("SELECT arbeitszeit FROM auftraege WHERE id = ?", (auftrag_id,))
        arbeitszeit = cursor.fetchone()[0]
        
        # Firmendaten abrufen
        from utils.config import get_company_info
        company_info = get_company_info(self.conn)
        
        # Stundensatz abrufen
        stundensatz = 50.0  # Standardwert
        cursor.execute("SELECT wert FROM konfiguration WHERE schluessel = 'standard_stundenlohn'")
        stundensatz_row = cursor.fetchone()
        if stundensatz_row:
            try:
                stundensatz = float(stundensatz_row[0])
            except:
                pass
        
        # MwSt-Satz abrufen
        mwst_satz = 7.7  # Standardwert für Schweiz
        if 'mwst' in company_info:
            try:
                mwst_satz = float(company_info['mwst'])
            except:
                pass
        
        # Rechnungsformatierung
        self.rechnung_text.insert(tk.END, f"{company_info['name'].upper()}\n")
        self.rechnung_text.insert(tk.END, f"{company_info['address']}\n")
        self.rechnung_text.insert(tk.END, f"Tel: {company_info['phone']}\n")
        self.rechnung_text.insert(tk.END, f"E-Mail: {company_info['email']}\n")
        self.rechnung_text.insert(tk.END, f"{company_info.get('website', '')}\n\n")
        
        self.rechnung_text.insert(tk.END, f"RECHNUNG {rechnungsnr}\n")
        self.rechnung_text.insert(tk.END, f"Datum: {datum}\n\n")
        
        self.rechnung_text.insert(tk.END, f"KUNDE:\n{kundenname}\n{anschrift or 'Keine Anschrift angegeben'}\n\n")
        
        self.rechnung_text.insert(tk.END, f"AUFTRAG: #{auftrag_id}\n")
        self.rechnung_text.insert(tk.END, f"Beschreibung: {auftrag_beschreibung}\n\n")
        
        self.rechnung_text.insert(tk.END, "POSITIONEN:\n")
        self.rechnung_text.insert(tk.END, f"{'#':<3} {'Bezeichnung':<40} {'Menge':<10} {'Einzelpreis':<15} {'Gesamtpreis':<15}\n")
        self.rechnung_text.insert(tk.END, "-" * 85 + "\n")
        
        pos = 1
        zwischensumme = 0
        
        # Ersatzteile
        for teil in ersatzteile:
            bezeichnung = teil[0]
            menge = teil[1]
            einzelpreis = teil[2]
            gesamtpreis = teil[3]
            zwischensumme += gesamtpreis
            
            self.rechnung_text.insert(tk.END, f"{pos:<3} {bezeichnung:<40} {menge:<10} {einzelpreis:>12.2f} CHF {gesamtpreis:>12.2f} CHF\n")
            pos += 1
            
        # Arbeitszeit
        if arbeitszeit > 0:
            arbeitskosten = arbeitszeit * stundensatz
            zwischensumme += arbeitskosten
            
            self.rechnung_text.insert(tk.END, f"{pos:<3} {'Arbeitszeit: ' + auftrag_beschreibung:<40} {arbeitszeit:<10.2f} h {stundensatz:>12.2f} CHF {arbeitskosten:>12.2f} CHF\n")
            
        self.rechnung_text.insert(tk.END, "-" * 85 + "\n")
        
        # Zwischensumme
        self.rechnung_text.insert(tk.END, f"Zwischensumme: {zwischensumme:>51.2f} CHF\n")
        
        # Rabatt, wenn vorhanden
        if rabatt_prozent > 0:
            rabatt_betrag = zwischensumme * rabatt_prozent / 100
            zwischensumme_nach_rabatt = zwischensumme - rabatt_betrag
            self.rechnung_text.insert(tk.END, f"Rabatt ({rabatt_prozent}%): {rabatt_betrag:>49.2f} CHF\n")
            self.rechnung_text.insert(tk.END, f"Netto: {zwischensumme_nach_rabatt:>61.2f} CHF\n")
        else:
            zwischensumme_nach_rabatt = zwischensumme
        
        # MwSt
        mwst = zwischensumme_nach_rabatt * mwst_satz / 100
        self.rechnung_text.insert(tk.END, f"MwSt ({mwst_satz}%): {mwst:>54.2f} CHF\n")
        
        # Gesamtbetrag
        gesamt = zwischensumme_nach_rabatt + mwst
        self.rechnung_text.insert(tk.END, f"GESAMTBETRAG: {gesamt:>51.2f} CHF\n\n")
        
        self.rechnung_text.insert(tk.END, f"HINWEISE:\n{notizen}\n\n")
        
        self.rechnung_text.insert(tk.END, "ZAHLUNGSINFORMATIONEN:\n")
        self.rechnung_text.insert(tk.END, f"Bitte überweisen Sie den Betrag innerhalb von {company_info.get('zahlungsfrist', '30')} Tagen auf folgendes Konto:\n")
        self.rechnung_text.insert(tk.END, f"Bank: {company_info.get('bank_name', 'Schweizer Kantonalbank')}\n")
        self.rechnung_text.insert(tk.END, f"IBAN: {company_info.get('bank_iban', 'CH00 0000 0000 0000 0000 0')}\n")
        self.rechnung_text.insert(tk.END, f"BIC: {company_info.get('bank_bic', 'POFICHBEXXX')}\n")
        self.rechnung_text.insert(tk.END, f"Verwendungszweck: {rechnungsnr}\n\n")
        
        self.rechnung_text.insert(tk.END, "Vielen Dank für Ihren Auftrag!\n")
        
        # Schreibschutz aktivieren
        self.rechnung_text.config(state="disabled")

    def show_pdf(self):
        """Zeigt die Rechnung als PDF an"""
        from utils.pdf_generator import generate_invoice_pdf
        import os
        import subprocess
        
        success, pdf_path = generate_invoice_pdf(self.conn, self.rechnung_id)
        
        if success:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':  # Linux, Mac
                    if os.system('command -v xdg-open') == 0:  # Linux
                        subprocess.call(['xdg-open', pdf_path])
                    else:  # Mac
                        subprocess.call(['open', pdf_path])
            except Exception as e:
                messagebox.showinfo("Information", f"PDF wurde erstellt, konnte aber nicht automatisch geöffnet werden: {pdf_path}")
        else:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der PDF: {pdf_path}")
        
    def print_rechnung(self):
        """Druckt die Rechnung"""
        # Zuerst PDF erstellen und dann das PDF drucken lassen
        from utils.pdf_generator import generate_invoice_pdf
        import os
        import subprocess
        
        success, pdf_path = generate_invoice_pdf(self.conn, self.rechnung_id)
        
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
                        self.show_pdf()
            except Exception as e:
                messagebox.showinfo("Information", f"Drucken nicht möglich: {e}")
                # Als Fallback die PDF anzeigen
                self.show_pdf()
        else:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der PDF: {pdf_path}")

    def save_pdf(self):
        """Speichert die Rechnung als PDF"""
        from utils.pdf_generator import generate_invoice_pdf
        from tkinter import filedialog
        import os
        
        # Dateiname vorschlagen
        cursor = self.conn.cursor()
        cursor.execute("SELECT rechnungsnummer FROM rechnungen WHERE id = ?", (self.rechnung_id,))
        rechnungsnr = cursor.fetchone()[0].replace('/', '_').replace(' ', '_')
        
        default_filename = f"Rechnung_{rechnungsnr}.pdf"
        
        # Speicherort wählen
        file_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            defaultextension=".pdf",
            filetypes=[("PDF Dateien", "*.pdf")],
            initialfile=default_filename
        )
        
        if not file_path:
            return  # Abgebrochen
            
        # PDF generieren
        success, pdf_path = generate_invoice_pdf(self.conn, self.rechnung_id, file_path)
        
        if success:
            messagebox.showinfo("Information", f"Die Rechnung wurde als PDF gespeichert: {file_path}")
        else:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der PDF: {pdf_path}")