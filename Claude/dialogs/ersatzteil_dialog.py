#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zum Erstellen und Bearbeiten von Ersatzteilen
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ErsatzteilDialog:
    """Dialog zum Erstellen und Bearbeiten von Ersatzteilen"""
    def __init__(self, parent, title, ersatzteil_id=None, conn=None):
        self.parent = parent
        self.ersatzteil_id = ersatzteil_id
        self.conn = conn
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Artikeldetails
        details_frame = ttk.LabelFrame(main_frame, text="Artikeldetails")
        details_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(details_frame, text="Artikelnummer:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.artikelnr_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.artikelnr_var, width=20).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Bezeichnung:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.bezeichnung_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.bezeichnung_var, width=40).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Kategorie:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.kategorie_var = tk.StringVar()
        self.kategorie_combo = ttk.Combobox(details_frame, textvariable=self.kategorie_var, width=20)
        self.kategorie_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Lagerort:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lagerort_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.lagerort_var, width=20).grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Einheit hinzufügen
        ttk.Label(details_frame, text="Einheit:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.einheit_var = tk.StringVar(value="Stk.")
        self.einheit_combo = ttk.Combobox(details_frame, textvariable=self.einheit_var, width=10, 
                                         values=["Stk.", "Liter", "h", "kg", "m", "Paar", "Set"])
        self.einheit_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Lagerdaten
        lager_frame = ttk.LabelFrame(main_frame, text="Lagerbestand")
        lager_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(lager_frame, text="Aktueller Bestand:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.bestand_var = tk.StringVar(value="0")
        ttk.Spinbox(lager_frame, from_=0, to=9999, textvariable=self.bestand_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(lager_frame, text="Mindestbestand:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.mindestbestand_var = tk.StringVar(value="1")
        ttk.Spinbox(lager_frame, from_=0, to=9999, textvariable=self.mindestbestand_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Preisdaten
        preis_frame = ttk.LabelFrame(main_frame, text="Preisdaten")
        preis_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(preis_frame, text="Einkaufspreis (CHF):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.einkaufspreis_var = tk.StringVar(value="0.00")
        ttk.Entry(preis_frame, textvariable=self.einkaufspreis_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(preis_frame, text="Verkaufspreis (CHF):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.verkaufspreis_var = tk.StringVar(value="0.00")
        ttk.Entry(preis_frame, textvariable=self.verkaufspreis_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Lieferanten
        lieferant_frame = ttk.LabelFrame(main_frame, text="Lieferantendaten")
        lieferant_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(lieferant_frame, text="Lieferant:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lieferant_var = tk.StringVar()
        ttk.Entry(lieferant_frame, textvariable=self.lieferant_var, width=30).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Kategorien laden
        self.load_categories()
        
        # Wenn ein Ersatzteil bearbeitet wird, Daten laden
        if self.ersatzteil_id:
            self.load_data()
            
        self.dialog.wait_window()
        
    def load_categories(self):
        """Lädt die Kategorien für die Combobox"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT kategorie FROM ersatzteile WHERE kategorie IS NOT NULL AND kategorie != ''")
        
        kategorien = [row[0] for row in cursor.fetchall()]
        self.kategorie_combo['values'] = kategorien
        
    def load_data(self):
        """Lädt die Daten des zu bearbeitenden Ersatzteils"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT artikelnummer, bezeichnung, kategorie, lagerort, lagerbestand, mindestbestand,
               einkaufspreis, verkaufspreis, lieferant, einheit
        FROM ersatzteile
        WHERE id = ?
        """, (self.ersatzteil_id,))
        
        data = cursor.fetchone()
        if data:
            self.artikelnr_var.set(data[0])
            self.bezeichnung_var.set(data[1])
            self.kategorie_var.set(data[2])
            self.lagerort_var.set(data[3])
            self.bestand_var.set(str(data[4]))
            self.mindestbestand_var.set(str(data[5]))
            self.einkaufspreis_var.set(f"{data[6]:.2f}")
            self.verkaufspreis_var.set(f"{data[7]:.2f}")
            self.lieferant_var.set(data[8])
            # Einheit laden, falls vorhanden
            if data[9]:
                self.einheit_var.set(data[9])
            
    def save_data(self):
        """Speichert die Ersatzteildaten"""
        # Pflichtfelder prüfen
        if not self.artikelnr_var.get() or not self.bezeichnung_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie eine Artikelnummer und eine Bezeichnung ein.")
            return
            
        try:
            # Preise und Bestandsdaten konvertieren
            bestand = int(self.bestand_var.get())
            mindestbestand = int(self.mindestbestand_var.get())
            einkaufspreis = float(self.einkaufspreis_var.get().replace(',', '.'))
            verkaufspreis = float(self.verkaufspreis_var.get().replace(',', '.'))
            
            cursor = self.conn.cursor()
            
            if self.ersatzteil_id:  # Bestehendes Teil aktualisieren
                cursor.execute("""
                UPDATE ersatzteile SET 
                    artikelnummer = ?, bezeichnung = ?, kategorie = ?, lagerort = ?,
                    lagerbestand = ?, mindestbestand = ?, einkaufspreis = ?, verkaufspreis = ?,
                    lieferant = ?, einheit = ?
                WHERE id = ?
                """, (
                    self.artikelnr_var.get(), self.bezeichnung_var.get(), self.kategorie_var.get(), 
                    self.lagerort_var.get(), bestand, mindestbestand, einkaufspreis, verkaufspreis,
                    self.lieferant_var.get(), self.einheit_var.get(), self.ersatzteil_id
                ))
            else:  # Neues Teil anlegen
                cursor.execute("""
                INSERT INTO ersatzteile (
                    artikelnummer, bezeichnung, kategorie, lagerort, lagerbestand,
                    mindestbestand, einkaufspreis, verkaufspreis, lieferant, einheit, erstellt_am
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    self.artikelnr_var.get(), self.bezeichnung_var.get(), self.kategorie_var.get(), 
                    self.lagerort_var.get(), bestand, mindestbestand, einkaufspreis, verkaufspreis,
                    self.lieferant_var.get(), self.einheit_var.get()
                ))
                
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Werte für Bestand und Preise ein.")
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Artikeldaten: {e}")
            self.conn.rollback()