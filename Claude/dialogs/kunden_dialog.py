#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zum Erstellen und Bearbeiten von Kunden
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.kundenfahrzeuge_dialog import KundenFahrzeugeDialog

class KundenDialog:
    """Dialog zum Erstellen und Bearbeiten von Kunden"""
    def __init__(self, parent, title, kunden_id=None, conn=None):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Eingabefelder
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill="both", expand=True, pady=5)
        
        # Persönliche Daten
        personal_frame = ttk.LabelFrame(fields_frame, text="Persönliche Daten")
        personal_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(personal_frame, text="Vorname:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.vorname_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.vorname_var, width=20).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(personal_frame, text="Nachname:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.nachname_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.nachname_var, width=20).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(personal_frame, text="Telefon:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.telefon_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.telefon_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(personal_frame, text="E-Mail:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.email_var, width=20).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(personal_frame, text="Anschrift:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.anschrift_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.anschrift_var, width=50).grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=2)
        
        # Hinweis auf Fahrzeugverwaltung
        if self.kunden_id:
            vehicle_note_frame = ttk.Frame(fields_frame)
            vehicle_note_frame.pack(fill="x", expand=False, pady=5)
            
            ttk.Label(vehicle_note_frame, text="Fahrzeuge dieses Kunden können nach dem Speichern über die Funktion 'Fahrzeuge verwalten' bearbeitet werden.", 
                     font=("Arial", 9, "italic")).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        if self.kunden_id:  # Nur bei Bearbeitung anzeigen
            ttk.Button(btn_frame, text="Fahrzeuge verwalten", command=self.manage_vehicles).pack(side="left", padx=5)
        
        # Wenn ein Kunde bearbeitet wird, Daten laden
        if self.kunden_id:
            self.load_data()
            
        self.dialog.wait_window()
        
    def load_data(self):
        """Lädt die Daten des zu bearbeitenden Kunden"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT vorname, nachname, telefon, email, anschrift
        FROM kunden
        WHERE id = ?
        """, (self.kunden_id,))
        
        data = cursor.fetchone()
        if data:
            self.vorname_var.set(data[0])
            self.nachname_var.set(data[1])
            self.telefon_var.set(data[2])
            self.email_var.set(data[3])
            self.anschrift_var.set(data[4])
            
    def manage_vehicles(self):
        """Öffnet den Dialog zur Verwaltung der Fahrzeuge"""
        if not self.kunden_id:
            messagebox.showinfo("Information", "Bitte speichern Sie den Kunden zuerst.")
            return
            
        fahrzeuge_dialog = KundenFahrzeugeDialog(
            self.dialog, 
            f"Fahrzeuge für {self.vorname_var.get()} {self.nachname_var.get()}", 
            self.kunden_id, 
            self.conn
        )
        
    def save_data(self):
        """Speichert die Kundendaten"""
        # Pflichtfelder prüfen
        if not self.vorname_var.get() or not self.nachname_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie Vor- und Nachname ein.")
            return
            
        try:
            cursor = self.conn.cursor()
            
            if self.kunden_id:  # Bestehenden Kunden aktualisieren
                cursor.execute("""
                UPDATE kunden SET 
                    vorname = ?, nachname = ?, telefon = ?, email = ?, anschrift = ?
                WHERE id = ?
                """, (
                    self.vorname_var.get(), self.nachname_var.get(), self.telefon_var.get(),
                    self.email_var.get(), self.anschrift_var.get(), self.kunden_id
                ))
            else:  # Neuen Kunden anlegen
                cursor.execute("""
                INSERT INTO kunden (
                    vorname, nachname, telefon, email, anschrift, erstellt_am
                ) VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    self.vorname_var.get(), self.nachname_var.get(), self.telefon_var.get(),
                    self.email_var.get(), self.anschrift_var.get()
                ))
                
                # Neue Kunden-ID ermitteln, falls der Dialog offen bleiben soll
                cursor.execute("SELECT last_insert_rowid()")
                self.kunden_id = cursor.fetchone()[0]
                
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Kundendaten: {e}")
            self.conn.rollback()