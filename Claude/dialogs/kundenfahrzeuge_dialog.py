#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modernisierter Dialog zur Verwaltung der Fahrzeuge eines Kunden
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.fahrzeug_dialog import FahrzeugDialog

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

class ModernKundenFahrzeugeDialog:
    """Moderner Dialog zur Verwaltung aller Fahrzeuge eines Kunden"""
    def __init__(self, parent, title, kunden_id, conn):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x500")
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
        style.configure("CardInfo.TLabel", 
                       background=COLORS["bg_medium"], 
                       foreground=COLORS["text_dark"],
                       font=("Arial", 10))
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Kundendaten anzeigen
        self.load_kunde_info(main_frame)
        
        # Tabelle mit Fahrzeugen
        fahrzeuge_frame = ttk.Frame(main_frame, style="Card.TFrame")
        fahrzeuge_frame.pack(fill="both", expand=True, pady=15)
        
        # Titel und Buttons
        header_frame = ttk.Frame(fahrzeuge_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Fahrzeuge", style="CardTitle.TLabel").pack(side="left")
        
        # Moderne Button-Klasse
        class ModernButton(tk.Button):
            def __init__(self, parent, text, command, icon=None, primary=False, **kwargs):
                bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
                fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
                
                super().__init__(parent, text=text, command=command, 
                                bg=bg_color, fg=fg_color,
                                activebackground=COLORS["text_light"], 
                                activeforeground=COLORS["bg_dark"],
                                relief="flat", borderwidth=0, padx=15, pady=6,
                                font=("Arial", 10), cursor="hand2", **kwargs)
        
        # Buttons für Fahrzeuge
        btn_frame = ttk.Frame(header_frame, style="Card.TFrame")
        btn_frame.pack(side="right")
        
        btn_neu = ModernButton(btn_frame, text="Neues Fahrzeug", command=self.new_fahrzeug, primary=True)
        btn_neu.pack(side="left", padx=5)
        
        btn_bearbeiten = ModernButton(btn_frame, text="Bearbeiten", command=self.edit_fahrzeug)
        btn_bearbeiten.pack(side="left", padx=5)
        
        btn_loeschen = ModernButton(btn_frame, text="Löschen", command=self.delete_fahrzeug)
        btn_loeschen.pack(side="left", padx=5)
        
        # Tabelle
        table_frame = ttk.Frame(fahrzeuge_frame, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)
        
        columns = ('id', 'fahrzeug', 'kennzeichen', 'fahrgestellnr')
        self.fahrzeuge_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
        
        self.fahrzeuge_tree.heading('id', text='ID')
        self.fahrzeuge_tree.heading('fahrzeug', text='Fahrzeugtyp')
        self.fahrzeuge_tree.heading('kennzeichen', text='Kennzeichen')
        self.fahrzeuge_tree.heading('fahrgestellnr', text='Fahrgestellnummer')
        
        self.fahrzeuge_tree.column('id', width=50, anchor='center')
        self.fahrzeuge_tree.column('fahrzeug', width=200)
        self.fahrzeuge_tree.column('kennzeichen', width=120)
        self.fahrzeuge_tree.column('fahrgestellnr', width=200)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.fahrzeuge_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.fahrzeuge_tree.xview)
        self.fahrzeuge_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.fahrzeuge_tree.pack(fill="both", expand=True)
        
        # Doppelklick zum Bearbeiten
        self.fahrzeuge_tree.bind("<Double-1>", lambda event: self.edit_fahrzeug())
        
        # Footer-Buttons
        footer_frame = ttk.Frame(main_frame, style="Card.TFrame")
        footer_frame.pack(fill="x", pady=(15, 0))
        
        btn_schliessen = ModernButton(footer_frame, text="Schließen", command=self.dialog.destroy)
        btn_schliessen.pack(side="right")
        
        # Fahrzeuge laden
        self.load_fahrzeuge()
        
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
        
    def load_kunde_info(self, parent_frame):
        """Lädt und zeigt die Kundeninformationen an"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT vorname, nachname, telefon
        FROM kunden
        WHERE id = ?
        """, (self.kunden_id,))
        
        kunde = cursor.fetchone()
        if kunde:
            # Infobereich für Kundendaten
            info_frame = ttk.Frame(parent_frame, style="Card.TFrame")
            info_frame.pack(fill="x", pady=(0, 15))
            
            # Name und Kontaktdaten
            name_label = ttk.Label(info_frame, 
                                 text=f"{kunde[0]} {kunde[1]}", 
                                 style="CardTitle.TLabel")
            name_label.pack(side="left")
            
            contact_label = ttk.Label(info_frame, 
                                    text=f"Telefon: {kunde[2]}", 
                                    style="CardInfo.TLabel")
            contact_label.pack(side="right")
    
    def load_fahrzeuge(self):
        """Lädt die Fahrzeuge des Kunden"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, fahrzeug_typ, kennzeichen, fahrgestellnummer
        FROM fahrzeuge
        WHERE kunden_id = ?
        ORDER BY id
        """, (self.kunden_id,))
        
        # Tabelle leeren
        for item in self.fahrzeuge_tree.get_children():
            self.fahrzeuge_tree.delete(item)
            
        # Daten einfügen
        fahrzeuge = cursor.fetchall()
        for row in fahrzeuge:
            self.fahrzeuge_tree.insert('', 'end', values=row)
            
        # Hinweistext, wenn keine Fahrzeuge vorhanden
        if len(fahrzeuge) == 0:
            self.fahrzeuge_tree.insert('', 'end', values=('', 'Keine Fahrzeuge vorhanden', '', ''), tags=('no_vehicles',))
            self.fahrzeuge_tree.tag_configure('no_vehicles', foreground=COLORS["text_dark"])
    
    def get_selected_fahrzeug_id(self):
        """Gibt die ID des ausgewählten Fahrzeugs zurück"""
        selected_items = self.fahrzeuge_tree.selection()
        if not selected_items:
            return None
            
        values = self.fahrzeuge_tree.item(selected_items[0])['values']
        if not values[0]:  # Falls es der "Keine Fahrzeuge" Eintrag ist
            return None
            
        return values[0]
    
    def new_fahrzeug(self):
        """Erstellt ein neues Fahrzeug"""
        fahrzeug_dialog = FahrzeugDialog(self.dialog, "Neues Fahrzeug", self.kunden_id, self.conn)
        if fahrzeug_dialog.result:
            self.load_fahrzeuge()
            self.result = True
    
    def edit_fahrzeug(self):
        """Bearbeitet ein vorhandenes Fahrzeug"""
        fahrzeug_id = self.get_selected_fahrzeug_id()
        if not fahrzeug_id:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Fahrzeug aus.")
            return
            
        fahrzeug_dialog = FahrzeugDialog(self.dialog, "Fahrzeug bearbeiten", 
                                        self.kunden_id, self.conn, fahrzeug_id)
        if fahrzeug_dialog.result:
            self.load_fahrzeuge()
            self.result = True
    
    def delete_fahrzeug(self):
        """Löscht ein Fahrzeug"""
        fahrzeug_id = self.get_selected_fahrzeug_id()
        if not fahrzeug_id:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Fahrzeug aus.")
            return
        
        # Fahrzeuginfo für Bestätigungsmeldung
        fahrzeug_typ = self.fahrzeuge_tree.item(self.fahrzeuge_tree.selection()[0])['values'][1]
        kennzeichen = self.fahrzeuge_tree.item(self.fahrzeuge_tree.selection()[0])['values'][2]
        
        # Prüfen, ob das Fahrzeug in Aufträgen verwendet wird (falls diese Verknüpfung existiert)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM auftraege WHERE fahrzeug_id = ?", (fahrzeug_id,))
        used_in_orders = cursor.fetchone()[0]
        
        if used_in_orders > 0:
            messagebox.showwarning("Warnung", 
                                f"Das Fahrzeug wird in {used_in_orders} Aufträgen verwendet und kann nicht gelöscht werden.")
            return
        
        # Bestätigung einholen mit modernem Dialog
        fahrzeug_info = f"{fahrzeug_typ} ({kennzeichen})" if kennzeichen else fahrzeug_typ
        if messagebox.askyesno("Löschen bestätigen", 
                             f"Möchten Sie das Fahrzeug '{fahrzeug_info}' wirklich löschen?",
                             icon="warning"):
            try:
                cursor.execute("DELETE FROM fahrzeuge WHERE id = ?", (fahrzeug_id,))
                self.conn.commit()
                self.load_fahrzeuge()
                self.result = True
            except sqlite3.Error as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen des Fahrzeugs: {e}")
                self.conn.rollback()


# Alte Klasse für Kompatibilität beibehalten, ruft nur die moderne Variante auf
class KundenFahrzeugeDialog:
    """Dialog zur Verwaltung aller Fahrzeuge eines Kunden"""
    def __init__(self, parent, title, kunden_id, conn):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        # Moderne Variante verwenden
        modern_dialog = ModernKundenFahrzeugeDialog(parent, title, kunden_id, conn)
        self.result = modern_dialog.result