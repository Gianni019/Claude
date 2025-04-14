#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zum Erstellen und Bearbeiten von Aufträgen
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

from dialogs.kunden_dialog import KundenDialog
from dialogs.teile_dialog import TeileAuswahlDialog

class AuftragsDialog:
    """Dialog zum Erstellen und Bearbeiten von Aufträgen"""
    def __init__(self, parent, title, auftrag_id=None, conn=None, kunden_id=None):
        self.parent = parent
        self.auftrag_id = auftrag_id
        self.conn = conn
        self.kunden_id = kunden_id
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Kundenauswahl
        kunde_frame = ttk.LabelFrame(main_frame, text="Kunde")
        kunde_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(kunde_frame, text="Kunde:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.kunde_var = tk.StringVar()
        self.kunden_combo = ttk.Combobox(kunde_frame, textvariable=self.kunde_var, width=40)
        self.kunden_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(kunde_frame, text="Neuer Kunde", command=self.new_kunde).grid(row=0, column=2, padx=5, pady=5)
        
        # Auftragsdaten
        auftrag_frame = ttk.LabelFrame(main_frame, text="Auftragsdaten")
        auftrag_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(auftrag_frame, text="Beschreibung:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.beschreibung_var = tk.StringVar()
        ttk.Entry(auftrag_frame, textvariable=self.beschreibung_var, width=50).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Offen")
        status_combo = ttk.Combobox(auftrag_frame, textvariable=self.status_var, width=20,
                                     values=["Offen", "In Bearbeitung", "Warten auf Teile", "Abgeschlossen"])
        status_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Priorität:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.prioritaet_var = tk.StringVar(value="Normal")
        prioritaet_combo = ttk.Combobox(auftrag_frame, textvariable=self.prioritaet_var, width=15,
                                        values=["Niedrig", "Normal", "Hoch", "Dringend"])
        prioritaet_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Arbeitszeit (h):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.arbeitszeit_var = tk.StringVar(value="0")
        ttk.Entry(auftrag_frame, textvariable=self.arbeitszeit_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Notizen
        ttk.Label(auftrag_frame, text="Notizen:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.notizen_text = tk.Text(auftrag_frame, height=4, width=50)
        self.notizen_text.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Ersatzteile
        teile_frame = ttk.LabelFrame(main_frame, text="Verwendete Ersatzteile")
        teile_frame.pack(fill="both", expand=True, pady=5)
        
        # Buttons für Teile
        teile_btn_frame = ttk.Frame(teile_frame)
        teile_btn_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Button(teile_btn_frame, text="Teil hinzufügen", command=self.add_part).pack(side="left", padx=5)
        ttk.Button(teile_btn_frame, text="Teil entfernen", command=self.remove_part).pack(side="left", padx=5)
        
        # Tabelle für Teile
        table_frame = ttk.Frame(teile_frame)
        table_frame.pack(fill="both", expand=True, pady=5)
        
        self.teile_tree = ttk.Treeview(table_frame, columns=('id', 'name', 'menge', 'preis'), show='headings', height=5)
        self.teile_tree.heading('id', text='ID')
        self.teile_tree.heading('name', text='Bezeichnung')
        self.teile_tree.heading('menge', text='Menge')
        self.teile_tree.heading('preis', text='Einzelpreis (€)')
        
        self.teile_tree.column('id', width=50, anchor='center')
        self.teile_tree.column('name', width=250)
        self.teile_tree.column('menge', width=80, anchor='center')
        self.teile_tree.column('preis', width=100, anchor='e')
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.teile_tree.yview)
        self.teile_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.teile_tree.pack(side="left", fill="both", expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Kunden laden
        self.load_kunden()
        
        # Wenn ein Auftrag bearbeitet wird, Daten laden
        if self.auftrag_id:
            self.load_data()
        elif self.kunden_id:
            # Vorauswahl des Kunden, wenn von Kundendialog aufgerufen
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, vorname || ' ' || nachname FROM kunden WHERE id = ?", (self.kunden_id,))
            kunde = cursor.fetchone()
            if kunde:
                self.kunde_var.set(f"{kunde[0]}: {kunde[1]}")
            
        self.dialog.wait_window()
        
    def load_kunden(self):
        """Lädt die Kundenliste für die Combobox"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, vorname || ' ' || nachname as name FROM kunden ORDER BY name")
        
        self.kunden_combo['values'] = [f"{id}: {name}" for id, name in cursor.fetchall()]
        
    def load_data(self):
        """Lädt die Daten des zu bearbeitenden Auftrags"""
        cursor = self.conn.cursor()
        
        # Auftragsdaten laden
        cursor.execute("""
        SELECT a.kunden_id, k.vorname || ' ' || k.nachname as kundenname, a.beschreibung, 
               a.status, a.prioritaet, a.arbeitszeit, a.notizen
        FROM auftraege a
        JOIN kunden k ON a.kunden_id = k.id
        WHERE a.id = ?
        """, (self.auftrag_id,))
        
        data = cursor.fetchone()
        if data:
            self.kunde_var.set(f"{data[0]}: {data[1]}")
            self.beschreibung_var.set(data[2])
            self.status_var.set(data[3])
            self.prioritaet_var.set(data[4])
            self.arbeitszeit_var.set(str(data[5]))
            self.notizen_text.delete(1.0, tk.END)
            if data[6]:
                self.notizen_text.insert(tk.END, data[6])
                
        # Verwendete Teile laden
        cursor.execute("""
        SELECT e.id, e.bezeichnung, ae.menge, ae.einzelpreis
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (self.auftrag_id,))
        
        # Teile-Tabelle leeren
        for item in self.teile_tree.get_children():
            self.teile_tree.delete(item)
            
        # Teile hinzufügen
        for row in cursor.fetchall():
            self.teile_tree.insert('', 'end', values=(row[0], row[1], row[2], f"{row[3]:.2f}"))
            
    def new_kunde(self):
        """Öffnet den Dialog zum Anlegen eines neuen Kunden"""
        kundendialog = KundenDialog(self.dialog, "Neuer Kunde", None, self.conn)
        if kundendialog.result:
            # Kundenliste aktualisieren
            self.load_kunden()
            
            # Neu angelegten Kunden auswählen
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT id, vorname || ' ' || nachname
            FROM kunden
            ORDER BY id DESC
            LIMIT 1
            """)
            
            last_kunde = cursor.fetchone()
            if last_kunde:
                self.kunde_var.set(f"{last_kunde[0]}: {last_kunde[1]}")
                
    def add_part(self):
        """Fügt ein Ersatzteil zum Auftrag hinzu"""
        teile_dialog = TeileAuswahlDialog(self.dialog, "Teil hinzufügen", None, self.conn)
        if teile_dialog.result:
            # Ausgewähltes Teil hinzufügen
            for teil_id, bezeichnung, menge, preis in teile_dialog.result:
                # Prüfen, ob Teil bereits in der Liste ist
                for item in self.teile_tree.get_children():
                    if self.teile_tree.item(item)['values'][0] == teil_id:
                        # Menge aktualisieren
                        current_menge = int(self.teile_tree.item(item)['values'][2])
                        self.teile_tree.item(item, values=(teil_id, bezeichnung, current_menge + menge, f"{preis:.2f}"))
                        break
                else:
                    # Neues Teil hinzufügen
                    self.teile_tree.insert('', 'end', values=(teil_id, bezeichnung, menge, f"{preis:.2f}"))
                
    def remove_part(self):
        """Entfernt ein Ersatzteil aus dem Auftrag"""
        selected_items = self.teile_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Teil aus.")
            return
            
        # Ausgewähltes Teil entfernen
        for item in selected_items:
            self.teile_tree.delete(item)
            
    def save_data(self):
        """Speichert die Auftragsdaten"""
        # Pflichtfelder prüfen
        if not self.kunde_var.get() or not self.beschreibung_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden und geben Sie eine Beschreibung ein.")
            return
        
        try:
            # Kunden-ID aus Combobox-Auswahl extrahieren
            kunden_id = int(self.kunde_var.get().split(":")[0])
            
            cursor = self.conn.cursor()
            
            if self.auftrag_id:  # Bestehenden Auftrag aktualisieren
                cursor.execute("""
                UPDATE auftraege SET 
                    kunden_id = ?, beschreibung = ?, status = ?, prioritaet = ?,
                    arbeitszeit = ?, notizen = ?
                WHERE id = ?
                """, (
                    kunden_id, self.beschreibung_var.get(), self.status_var.get(), 
                    self.prioritaet_var.get(), float(self.arbeitszeit_var.get() or 0),
                    self.notizen_text.get(1.0, tk.END).strip(), self.auftrag_id
                ))
                
                # Bestehende Teile-Verknüpfungen löschen
                cursor.execute("DELETE FROM auftrag_ersatzteile WHERE auftrag_id = ?", (self.auftrag_id,))
                
                auftrag_id_to_use = self.auftrag_id  # Verwende die bestehende Auftrags-ID
                    
            else:  # Neuen Auftrag anlegen
                cursor.execute("""
                INSERT INTO auftraege (
                    kunden_id, beschreibung, status, prioritaet, erstellt_am,
                    abgeschlossen_am, arbeitszeit, notizen
                ) VALUES (?, ?, ?, ?, datetime('now'), ?, ?, ?)
                """, (
                    kunden_id, self.beschreibung_var.get(), self.status_var.get(), 
                    self.prioritaet_var.get(), 
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S') if self.status_var.get() == "Abgeschlossen" else None,
                    float(self.arbeitszeit_var.get() or 0), self.notizen_text.get(1.0, tk.END).strip()
                ))
                
                # Die ID des neuen Auftrags ermitteln
                cursor.execute("SELECT last_insert_rowid()")
                auftrag_id_to_use = cursor.fetchone()[0]
            
            # Teile zum Auftrag hinzufügen (jetzt unabhängig davon, ob neu oder bestehend)
            for item in self.teile_tree.get_children():
                values = self.teile_tree.item(item)['values']
                ersatzteil_id = values[0]
                bezeichnung = values[1]
                menge = values[2]
                
                # Einzelpreis extrahieren
                einzelpreis_str = str(values[3])
                if " CHF" in einzelpreis_str:
                    einzelpreis_str = einzelpreis_str.replace(" CHF", "")
                elif " €" in einzelpreis_str:
                    einzelpreis_str = einzelpreis_str.replace(" €", "")
                einzelpreis = float(einzelpreis_str.replace(',', '.'))
                
                # Rabatt aus Bezeichnung extrahieren
                rabatt = 0.0
                if "Rabatt:" in bezeichnung:
                    try:
                        rabatt_text = bezeichnung.split("Rabatt: ")[1].split("%")[0]
                        rabatt = float(rabatt_text)
                        bezeichnung = bezeichnung.split(" (Rabatt:")[0]
                    except (IndexError, ValueError):
                        pass
                
                cursor.execute("""
                INSERT INTO auftrag_ersatzteile (auftrag_id, ersatzteil_id, menge, einzelpreis, rabatt)
                VALUES (?, ?, ?, ?, ?)
                """, (auftrag_id_to_use, ersatzteil_id, menge, einzelpreis, rabatt))
            
            # Commit ausführen und Ergebnis setzen
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            # Detaillierte Fehlerinformationen anzeigen
            print(f"Fehler beim Speichern: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Auftragsdaten: {e}")
            self.conn.rollback()