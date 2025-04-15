#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisierter Dialog zur Änderung des Lagerbestands
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Moderne Farbpalette
COLORS = {
    "bg_dark": "#1e2330",
    "bg_medium": "#2a3142",
    "bg_light": "#353e54",
    "accent": "#5ce0d8",
    "text_light": "#ffffff",
    "text_dark": "#aab0bc",
    "success": "#5fb878",
    "warning": "#f2aa4c",
    "danger": "#f65e5e"
}

class ModernBestandsDialog:
    """Moderner Dialog zur Änderung des Lagerbestands"""
    def __init__(self, parent, title, ersatzteil_id, conn, aktueller_bestand=0):
        self.parent = parent
        self.ersatzteil_id = ersatzteil_id
        self.conn = conn
        self.aktueller_bestand = aktueller_bestand
        self.result = False
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Dunkler Hintergrund für das Dialog-Fenster
        self.dialog.configure(bg=COLORS["bg_dark"])
        
        # Custom Styles für diesen Dialog
        style = ttk.Style()
        style.configure("Card.TFrame", background=COLORS["bg_medium"])
        style.configure("CardTitle.TLabel", 
                      background=COLORS["bg_medium"], 
                      foreground=COLORS["text_light"],
                      font=("Arial", 14, "bold"))
        style.configure("CardText.TLabel", 
                      background=COLORS["bg_medium"], 
                      foreground=COLORS["text_light"],
                      font=("Arial", 11))
        style.configure("CardInfo.TLabel", 
                      background=COLORS["bg_medium"], 
                      foreground=COLORS["text_dark"],
                      font=("Arial", 10))
        style.configure("CardValue.TLabel", 
                      background=COLORS["bg_medium"], 
                      foreground=COLORS["accent"],
                      font=("Arial", 16, "bold"))
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Artikelinformationen abrufen
        cursor = conn.cursor()
        cursor.execute("SELECT bezeichnung, artikelnummer, kategorie FROM ersatzteile WHERE id = ?", (ersatzteil_id,))
        artikel = cursor.fetchone()
        
        if not artikel:
            messagebox.showerror("Fehler", "Artikel nicht gefunden!")
            self.dialog.destroy()
            return
            
        # Header mit Artikelinfo
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        artikel_name = ttk.Label(header_frame, text=artikel[0], style="CardTitle.TLabel")
        artikel_name.pack(anchor="w")
        
        artikel_info = ttk.Label(header_frame, 
                               text=f"Artikelnr.: {artikel[1]} | Kategorie: {artikel[2]}", 
                               style="CardInfo.TLabel")
        artikel_info.pack(anchor="w", pady=(5, 0))
        
        # Aktueller Bestand mit hervorgehobener Anzeige
        bestand_frame = ttk.Frame(main_frame, style="Card.TFrame")
        bestand_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(bestand_frame, text="Aktueller Bestand:", style="CardText.TLabel").pack(anchor="w")
        
        bestand_wert = ttk.Label(bestand_frame, text=str(aktueller_bestand), style="CardValue.TLabel")
        bestand_wert.pack(anchor="w", pady=(5, 0))
        
        # Trennlinie
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=15)
        
        # Bestandsänderung
        options_frame = ttk.LabelFrame(main_frame, text="Bestandsänderung", style="Card.TFrame")
        options_frame.pack(fill="x", expand=False, pady=10, padx=5, ipady=10)
        
        # Menge
        menge_frame = ttk.Frame(options_frame, style="Card.TFrame")
        menge_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(menge_frame, text="Menge:", style="CardText.TLabel").pack(side="left")
        
        # Eigenes Spinbox-Widget für Menge
        self.menge_var = tk.StringVar(value="1")
        menge_spinbox = tk.Spinbox(menge_frame, from_=1, to=9999, textvariable=self.menge_var, 
                                  width=10, bg=COLORS["bg_light"], fg=COLORS["text_light"],
                                  buttonbackground=COLORS["bg_light"], 
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=COLORS["bg_light"],
                                  highlightcolor=COLORS["accent"],
                                  font=("Arial", 12))
        menge_spinbox.pack(side="left", padx=15)
        
        # Art der Änderung mit modernen Radio-Buttons
        art_frame = ttk.Frame(options_frame, style="Card.TFrame")
        art_frame.pack(fill="x", pady=10, padx=10)
        
        self.aenderungsart_var = tk.StringVar(value="Zugefügt")
        
        # Funktion für besseres Radio-Button-Styling
        def create_radio_button(parent, text, variable, value):
            frame = ttk.Frame(parent, style="Card.TFrame")
            
            rb = ttk.Radiobutton(frame, text=text, variable=variable, value=value, 
                              style="TRadiobutton", command=self.update_neuer_bestand)
            rb.pack(side="left", padx=5)
            
            return frame
        
        ttk.Label(art_frame, text="Art der Änderung:", style="CardText.TLabel").pack(anchor="w", pady=(0, 10))
        
        radio_container = ttk.Frame(art_frame, style="Card.TFrame")
        radio_container.pack(fill="x")
        
        rb_added = create_radio_button(radio_container, "Zugefügt", self.aenderungsart_var, "Zugefügt")
        rb_added.pack(side="left", padx=(0, 20))
        
        rb_removed = create_radio_button(radio_container, "Entnommen", self.aenderungsart_var, "Entnommen")
        rb_removed.pack(side="left")
        
        # Neuer Bestand (Vorschau)
        preview_frame = ttk.Frame(options_frame, style="Card.TFrame")
        preview_frame.pack(fill="x", pady=15, padx=10)
        
        ttk.Label(preview_frame, text="Neuer Bestand:", style="CardText.TLabel").pack(side="left")
        
        self.neuer_bestand_var = tk.StringVar(value=str(aktueller_bestand))
        neuer_bestand_label = ttk.Label(preview_frame, textvariable=self.neuer_bestand_var, 
                                      style="CardValue.TLabel")
        neuer_bestand_label.pack(side="left", padx=15)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", expand=False, pady=15)
        
        # Moderne Button-Klasse
        class ModernButton(tk.Button):
            def __init__(self, parent, text, command, icon=None, primary=False, **kwargs):
                bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
                fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
                
                super().__init__(parent, text=text, command=command, 
                                bg=bg_color, fg=fg_color,
                                activebackground=COLORS["text_light"], 
                                activeforeground=COLORS["bg_dark"],
                                relief="flat", borderwidth=0, padx=15, pady=8,
                                font=("Arial", 10), cursor="hand2", **kwargs)
        
        # Buttons
        btn_speichern = ModernButton(btn_frame, text="Speichern", command=self.save_data, primary=True)
        btn_speichern.pack(side="right", padx=5)
        
        btn_abbrechen = ModernButton(btn_frame, text="Abbrechen", command=self.dialog.destroy)
        btn_abbrechen.pack(side="right", padx=5)
        
        # Menge und Art der Änderung verknüpfen
        self.menge_var.trace_add("write", self.update_neuer_bestand)
        
        # Dialog zentrieren
        self.center_dialog()
        
        self.dialog.wait_window()
        
    def center_dialog(self):
        """Zentriert den Dialog auf dem Bildschirm"""
        self.dialog.update_idletasks()
        
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
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
            
    def save_data(self):
        """Speichert die Bestandsänderung"""
        try:
            menge = int(self.menge_var.get())
            
            if self.aenderungsart_var.get() == "Zugefügt":
                # Bestand erhöhen
                delta = menge
            else:
                # Bestand verringern
                delta = -menge
                
            # Neuer Bestand berechnen
            neuer_bestand = self.aktueller_bestand + delta
            
            # Negativen Bestand verhindern
            if neuer_bestand < 0:
                neuer_bestand = 0
                
            # Aktualisierung in der Datenbank
            cursor = self.conn.cursor()
            cursor.execute("UPDATE ersatzteile SET lagerbestand = ? WHERE id = ?", 
                         (neuer_bestand, self.ersatzteil_id))
            self.conn.commit()
            
            # Optional: Protokollierung der Änderung
            self.log_bestandsaenderung(delta)
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Menge ein.")
        except sqlite3.Error as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Speichern: {e}")
            self.conn.rollback()
            
    def log_bestandsaenderung(self, delta):
        """Protokolliert die Bestandsänderung (optional)"""
        try:
            cursor = self.conn.cursor()
            
            # Prüfen ob eine Tabelle für die Bestandsprotokollierung existiert
            cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='bestandsaenderungen'
            """)
            
            if not cursor.fetchone():
                # Protokolltabelle anlegen, falls nicht vorhanden
                cursor.execute("""
                CREATE TABLE bestandsaenderungen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ersatzteil_id INTEGER NOT NULL,
                    menge INTEGER NOT NULL,
                    zeitpunkt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ersatzteil_id) REFERENCES ersatzteile (id)
                )
                """)
            
            # Änderung protokollieren
            cursor.execute("""
            INSERT INTO bestandsaenderungen (ersatzteil_id, menge)
            VALUES (?, ?)
            """, (self.ersatzteil_id, delta))
            
            self.conn.commit()
            
        except sqlite3.Error:
            # Fehler beim Protokollieren sollten den Hauptprozess nicht stören
            pass

# Alte Klasse für Kompatibilität beibehalten, ruft nur die moderne Variante auf
class BestandsDialog:
    """Dialog zur Änderung des Lagerbestands"""
    def __init__(self, parent, title, ersatzteil_id, conn, aktueller_bestand=0):
        self.parent = parent
        self.ersatzteil_id = ersatzteil_id
        self.conn = conn
        self.aktueller_bestand = aktueller_bestand
        self.result = False
        
        # Moderne Variante verwenden
        modern_dialog = ModernBestandsDialog(parent, title, ersatzteil_id, conn, aktueller_bestand)
        self.result = modern_dialog.result