#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zur Änderung des Lagerbestands
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class BestandsDialog:
    """Dialog zur Änderung des Lagerbestands"""
    def __init__(self, parent, title, ersatzteil_id, conn, aktueller_bestand=0):
        self.parent = parent
        self.ersatzteil_id = ersatzteil_id
        self.conn = conn
        self.aktueller_bestand = aktueller_bestand
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Artikelinformationen anzeigen
        cursor = conn.cursor()
        cursor.execute("SELECT bezeichnung, artikelnummer FROM ersatzteile WHERE id = ?", (ersatzteil_id,))
        artikel = cursor.fetchone()
        
        if artikel:
            info_text = f"Artikel: {artikel[0]}\nArtikelnr.: {artikel[1]}\nAktueller Bestand: {aktueller_bestand}"
            ttk.Label(main_frame, text=info_text).pack(fill="x", pady=10)
        
        # Optionen für Bestandsänderung
        options_frame = ttk.LabelFrame(main_frame, text="Bestandsänderung")
        options_frame.pack(fill="x", expand=False, pady=10)
        
        # Menge
        ttk.Label(options_frame, text="Menge:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.menge_var = tk.StringVar(value="1")
        ttk.Spinbox(options_frame, from_=1, to=9999, textvariable=self.menge_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Art der Änderung
        self.aenderungsart_var = tk.StringVar(value="Zugefügt")
        ttk.Radiobutton(options_frame, text="Zugefügt", variable=self.aenderungsart_var, value="Zugefügt").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(options_frame, text="Entnommen", variable=self.aenderungsart_var, value="Entnommen").grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Neuer Bestand (Vorschau)
        ttk.Label(options_frame, text="Neuer Bestand:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.neuer_bestand_var = tk.StringVar(value=str(aktueller_bestand))
        ttk.Label(options_frame, textvariable=self.neuer_bestand_var, font=("Arial", 10, "bold")).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Menge und Art der Änderung verknüpfen
        self.menge_var.trace_add("write", self.update_neuer_bestand)
        self.aenderungsart_var.trace_add("write", self.update_neuer_bestand)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        self.dialog.wait_window()
        
    def update_neuer_bestand(self, *args):
        """Aktualisiert die Vorschau des neuen Bestands"""
        try:
            menge = int(self.menge_var.get())
            
            if self.aenderungsart_var.get() == "Zugefügt":
                neuer_bestand = self.aktueller_bestand + menge
            else:
                neuer_bestand = self.aktueller_bestand - menge
                
            # Negativen Bestand verhindern
            if neuer_bestand < 0:
                neuer_bestand = 0
                menge = self.aktueller_bestand
                self.menge_var.set(str(menge))
                
            self.neuer_bestand_var.set(str(neuer_bestand))
        except ValueError:
            self.neuer_bestand_var.set("Ungültige Eingabe")