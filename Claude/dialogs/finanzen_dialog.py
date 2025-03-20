#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialoge für Finanzen
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AusgabenDialog:
    """Dialog zum Erstellen und Bearbeiten von Ausgaben"""
    def __init__(self, parent, title, ausgabe_id=None, conn=None):
        self.parent = parent
        self.ausgabe_id = ausgabe_id
        self.conn = conn
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Eingabefelder
        ttk.Label(main_frame, text="Kategorie:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.kategorie_var = tk.StringVar()
        self.kategorie_combo = ttk.Combobox(main_frame, textvariable=self.kategorie_var, width=20)
        self.kategorie_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Betrag (€):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.betrag_var = tk.StringVar(value="0.00")
        ttk.Entry(main_frame, textvariable=self.betrag_var, width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Datum:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.datum_var = tk.StringVar(value=datetime.now().strftime('%d.%m.%Y'))
        ttk.Entry(main_frame, textvariable=self.datum_var, width=15).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Beschreibung:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.beschreibung_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.beschreibung_var, width=50).grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Beleg-Nr.:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.beleg_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.beleg_var, width=20).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, sticky="e", pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Kategorien laden
        self.load_categories()
        
        # Wenn eine Ausgabe bearbeitet wird, Daten laden
        if self.ausgabe_id:
            self.load_data()
            
        self.dialog.wait_window()
        
    def load_categories(self):
        """Lädt die Kategorien für die Combobox"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT kategorie FROM ausgaben WHERE kategorie IS NOT NULL AND kategorie != ''")
        
        kategorien = [row[0] for row in cursor.fetchall()]
        self.kategorie_combo['values'] = kategorien
        
    def load_data(self):
        """Lädt die Daten der zu bearbeitenden Ausgabe"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT kategorie, betrag, strftime('%d.%m.%Y', datum) as datum, beschreibung, beleg_nr
        FROM ausgaben
        WHERE id = ?
        """, (self.ausgabe_id,))
        
        data = cursor.fetchone()
        if data:
            self.kategorie_var.set(data[0])
            self.betrag_var.set(f"{data[1]:.2f}")
            self.datum_var.set(data[2])
            self.beschreibung_var.set(data[3])
            self.beleg_var.set(data[4])
            
    def save_data(self):
        """Speichert die Ausgabedaten"""
        # Pflichtfelder prüfen
        if not self.kategorie_var.get() or not self.betrag_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie eine Kategorie und einen Betrag ein.")
            return
            
        try:
            # Betrag konvertieren
            betrag = float(self.betrag_var.get().replace(',', '.'))
            
            if betrag <= 0:
                messagebox.showerror("Fehler", "Der Betrag muss größer als 0 sein.")
                return
                
            # Datum konvertieren
            try:
                datum_parts = self.datum_var.get().split('.')
                datum_db = f"{datum_parts[2]}-{datum_parts[1]}-{datum_parts[0]}"
            except:
                messagebox.showerror("Fehler", "Ungültiges Datumsformat. Bitte verwenden Sie TT.MM.JJJJ.")
                return
                
            cursor = self.conn.cursor()
            
            if self.ausgabe_id:  # Bestehende Ausgabe aktualisieren
                cursor.execute("""
                UPDATE ausgaben SET 
                    kategorie = ?, betrag = ?, datum = ?, beschreibung = ?, beleg_nr = ?
                WHERE id = ?
                """, (
                    self.kategorie_var.get(), betrag, datum_db,
                    self.beschreibung_var.get(), self.beleg_var.get(), self.ausgabe_id
                ))
            else:  # Neue Ausgabe anlegen
                cursor.execute("""
                INSERT INTO ausgaben (
                    kategorie, betrag, datum, beschreibung, beleg_nr
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    self.kategorie_var.get(), betrag, datum_db,
                    self.beschreibung_var.get(), self.beleg_var.get()
                ))
                
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie einen gültigen Betrag ein.")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Ausgabe: {e}")
            self.conn.rollback()