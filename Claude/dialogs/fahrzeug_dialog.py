#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zum Verwalten von Fahrzeugen eines Kunden
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class FahrzeugDialog:
    """Dialog zum Erstellen und Bearbeiten von Fahrzeugen"""
    def __init__(self, parent, title, kunden_id, conn, fahrzeug_id=None):
        self.parent = parent
        self.kunden_id = kunden_id
        self.fahrzeug_id = fahrzeug_id
        self.conn = conn
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Fahrzeugdaten
        vehicle_frame = ttk.LabelFrame(main_frame, text="Fahrzeugdaten")
        vehicle_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(vehicle_frame, text="Fahrzeugtyp:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.fahrzeug_var = tk.StringVar()
        ttk.Entry(vehicle_frame, textvariable=self.fahrzeug_var, width=30).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vehicle_frame, text="Kennzeichen:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.kennzeichen_var = tk.StringVar()
        ttk.Entry(vehicle_frame, textvariable=self.kennzeichen_var, width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vehicle_frame, text="Fahrgestellnummer:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.fahrgestellnr_var = tk.StringVar()
        ttk.Entry(vehicle_frame, textvariable=self.fahrgestellnr_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Wenn ein Fahrzeug bearbeitet wird, Daten laden
        if self.fahrzeug_id:
            self.load_data()
            
        self.dialog.wait_window()
        
    def load_data(self):
        """Lädt die Daten des zu bearbeitenden Fahrzeugs"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT fahrzeug_typ, kennzeichen, fahrgestellnummer
        FROM fahrzeuge
        WHERE id = ?
        """, (self.fahrzeug_id,))
        
        data = cursor.fetchone()
        if data:
            self.fahrzeug_var.set(data[0] or "")
            self.kennzeichen_var.set(data[1] or "")
            self.fahrgestellnr_var.set(data[2] or "")
            
    def save_data(self):
        """Speichert die Fahrzeugdaten"""
        # Pflichtfelder prüfen
        if not self.fahrzeug_var.get() and not self.kennzeichen_var.get() and not self.fahrgestellnr_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie mindestens ein Fahrzeugmerkmal ein.")
            return
            
        try:
            cursor = self.conn.cursor()
            
            if self.fahrzeug_id:  # Bestehendes Fahrzeug aktualisieren
                cursor.execute("""
                UPDATE fahrzeuge SET 
                    fahrzeug_typ = ?, kennzeichen = ?, fahrgestellnummer = ?
                WHERE id = ?
                """, (
                    self.fahrzeug_var.get(), self.kennzeichen_var.get(), 
                    self.fahrgestellnr_var.get(), self.fahrzeug_id
                ))
            else:  # Neues Fahrzeug anlegen
                cursor.execute("""
                INSERT INTO fahrzeuge (
                    kunden_id, fahrzeug_typ, kennzeichen, fahrgestellnummer
                ) VALUES (?, ?, ?, ?)
                """, (
                    self.kunden_id, self.fahrzeug_var.get(), 
                    self.kennzeichen_var.get(), self.fahrgestellnr_var.get()
                ))
                
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Fahrzeugdaten: {e}")
            self.conn.rollback()