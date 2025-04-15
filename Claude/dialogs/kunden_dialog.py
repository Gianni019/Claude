#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisierter Dialog zum Erstellen und Bearbeiten von Kunden
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from dialogs.kundenfahrzeuge_dialog import KundenFahrzeugeDialog

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

class ModernKundenDialog:
    """Moderner Dialog zum Erstellen und Bearbeiten von Kunden"""
    def __init__(self, parent, title, kunden_id=None, conn=None):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Dunkler Hintergrund
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
        style.configure("CardLabel.TLabel", 
                       background=COLORS["bg_medium"], 
                       foreground=COLORS["text_light"],
                       font=("Arial", 10))
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        if kunden_id:
            dialog_title = "Kunde bearbeiten"
        else:
            dialog_title = "Neuer Kunde"
            
        title_label = ttk.Label(main_frame, text=dialog_title, style="CardTitle.TLabel")
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Content-Frame für Tabs
        content_frame = ttk.Frame(main_frame, style="Card.TFrame")
        content_frame.pack(fill="both", expand=True)
        
        # Tabs für verschiedene Kundendaten
        self.tabs = ttk.Notebook(content_frame)
        self.tabs.pack(fill="both", expand=True)
        
        # Persönliche Daten Tab
        personal_tab = ttk.Frame(self.tabs, style="Card.TFrame")
        self.tabs.add(personal_tab, text="Persönliche Daten")
        
        # Grid für persönliche Daten
        for i in range(4):
            personal_tab.columnconfigure(i, weight=1)
            
        # Eingabefelder mit modernem Design
        row = 0
        ttk.Label(personal_tab, text="Vorname:", style="CardLabel.TLabel").grid(row=row, column=0, sticky="w", padx=10, pady=10)
        self.vorname_var = tk.StringVar()
        self.create_modern_entry(personal_tab, self.vorname_var).grid(row=row, column=1, sticky="ew", padx=10, pady=10)
        
        ttk.Label(personal_tab, text="Nachname:", style="CardLabel.TLabel").grid(row=row, column=2, sticky="w", padx=10, pady=10)
        self.nachname_var = tk.StringVar()
        self.create_modern_entry(personal_tab, self.nachname_var).grid(row=row, column=3, sticky="ew", padx=10, pady=10)
        
        row += 1
        ttk.Label(personal_tab, text="Telefon:", style="CardLabel.TLabel").grid(row=row, column=0, sticky="w", padx=10, pady=10)
        self.telefon_var = tk.StringVar()
        self.create_modern_entry(personal_tab, self.telefon_var).grid(row=row, column=1, sticky="ew", padx=10, pady=10)
        
        ttk.Label(personal_tab, text="E-Mail:", style="CardLabel.TLabel").grid(row=row, column=2, sticky="w", padx=10, pady=10)
        self.email_var = tk.StringVar()
        self.create_modern_entry(personal_tab, self.email_var).grid(row=row, column=3, sticky="ew", padx=10, pady=10)
        
        row += 1
        ttk.Label(personal_tab, text="Anschrift:", style="CardLabel.TLabel").grid(row=row, column=0, sticky="w", padx=10, pady=10)
        self.anschrift_var = tk.StringVar()
        self.create_modern_entry(personal_tab, self.anschrift_var, width=50).grid(row=row, column=1, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # Fahrzeugdaten Tab (falls neuer Kunde)
        if not self.kunden_id:
            vehicle_tab = ttk.Frame(self.tabs, style="Card.TFrame")
            self.tabs.add(vehicle_tab, text="Fahrzeugdaten")
            
            # Grid für Fahrzeugdaten
            for i in range(4):
                vehicle_tab.columnconfigure(i, weight=1)
                
            row = 0
            ttk.Label(vehicle_tab, text="Fahrzeugtyp:", style="CardLabel.TLabel").grid(row=row, column=0, sticky="w", padx=10, pady=10)
            self.fahrzeug_var = tk.StringVar()
            self.create_modern_entry(vehicle_tab, self.fahrzeug_var).grid(row=row, column=1, sticky="ew", padx=10, pady=10)
            
            ttk.Label(vehicle_tab, text="Kennzeichen:", style="CardLabel.TLabel").grid(row=row, column=2, sticky="w", padx=10, pady=10)
            self.kennzeichen_var = tk.StringVar()
            self.create_modern_entry(vehicle_tab, self.kennzeichen_var).grid(row=row, column=3, sticky="ew", padx=10, pady=10)
            
            row += 1
            ttk.Label(vehicle_tab, text="Fahrgestellnummer:", style="CardLabel.TLabel").grid(row=row, column=0, sticky="w", padx=10, pady=10)
            self.fahrgestellnr_var = tk.StringVar()
            self.create_modern_entry(vehicle_tab, self.fahrgestellnr_var).grid(row=row, column=1, sticky="ew", padx=10, pady=10)
        else:
            # Hinweis, dass Fahrzeuge separat verwaltet werden
            hint_frame = ttk.Frame(personal_tab, style="Card.TFrame")
            hint_frame.grid(row=row+1, column=0, columnspan=4, sticky="ew", padx=10, pady=20)
            
            hint_text = "Fahrzeuge dieses Kunden können nach dem Speichern über die Funktion 'Fahrzeuge verwalten' bearbeitet werden."
            hint_label = ttk.Label(hint_frame, text=hint_text, style="CardText.TLabel", font=("Arial", 9, "italic"))
            hint_label.pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(20, 0))
        
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
        
        # Buttons hinzufügen
        btn_speichern = ModernButton(btn_frame, text="Speichern", command=self.save_data, primary=True)
        btn_speichern.pack(side="right", padx=5)
        
        btn_abbrechen = ModernButton(btn_frame, text="Abbrechen", command=self.dialog.destroy)
        btn_abbrechen.pack(side="right", padx=5)
        
        if self.kunden_id:  # Nur bei Bearbeitung anzeigen
            btn_fahrzeuge = ModernButton(btn_frame, text="Fahrzeuge verwalten", command=self.manage_vehicles)
            btn_fahrzeuge.pack(side="left", padx=5)
        
        # Wenn ein Kunde bearbeitet wird, Daten laden
        if self.kunden_id:
            self.load_data()
            
        # Dialog zentrieren
        self.center_dialog()
        
        self.dialog.wait_window()
    
    def create_modern_entry(self, parent, textvariable, width=20):
        """Erstellt ein modernes Eingabefeld"""
        entry = tk.Entry(parent, textvariable=textvariable, width=width,
                     bg=COLORS["bg_light"], fg=COLORS["text_light"],
                     insertbackground=COLORS["text_light"], 
                     relief="flat", highlightthickness=1,
                     highlightbackground=COLORS["bg_light"],
                     highlightcolor=COLORS["accent"],
                     font=("Arial", 10))
        return entry
    
    def center_dialog(self):
        """Zentriert den Dialog auf dem Bildschirm"""
        self.dialog.update_idletasks()
        
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
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
            self.vorname_var.set(data[0] or "")
            self.nachname_var.set(data[1] or "")
            self.telefon_var.set(data[2] or "")
            self.email_var.set(data[3] or "")
            self.anschrift_var.set(data[4] or "")
            
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
                # Kundendaten einfügen
                cursor.execute("""
                INSERT INTO kunden (
                    vorname, nachname, telefon, email, anschrift, erstellt_am
                ) VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    self.vorname_var.get(), self.nachname_var.get(), self.telefon_var.get(),
                    self.email_var.get(), self.anschrift_var.get()
                ))
                
                # Neue Kunden-ID ermitteln
                cursor.execute("SELECT last_insert_rowid()")
                self.kunden_id = cursor.fetchone()[0]
                
                # Falls Fahrzeugdaten angegeben wurden, diese in die Fahrzeuge-Tabelle einfügen
                if hasattr(self, 'fahrzeug_var') and self.fahrzeug_var.get().strip():
                    cursor.execute("""
                    INSERT INTO fahrzeuge (
                        kunden_id, fahrzeug_typ, kennzeichen, fahrgestellnummer
                    ) VALUES (?, ?, ?, ?)
                    """, (
                        self.kunden_id, 
                        self.fahrzeug_var.get().strip(), 
                        self.kennzeichen_var.get().strip(), 
                        self.fahrgestellnr_var.get().strip()
                    ))
                
            # Commit ausführen und Ergebnis setzen
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Kundendaten: {e}")
            self.conn.rollback()


# Alte Klasse für Kompatibilität beibehalten, ruft nur die moderne Variante auf
class KundenDialog:
    """Dialog zum Erstellen und Bearbeiten von Kunden"""
    def __init__(self, parent, title, kunden_id=None, conn=None):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        # Moderne Variante verwenden
        modern_dialog = ModernKundenDialog(parent, title, kunden_id, conn)
        self.result = modern_dialog.result