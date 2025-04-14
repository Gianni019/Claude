#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zur Verwaltung der Fahrzeuge eines Kunden
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from dialogs.fahrzeug_dialog import FahrzeugDialog

class KundenFahrzeugeDialog:
    """Dialog zur Verwaltung aller Fahrzeuge eines Kunden"""
    def __init__(self, parent, title, kunden_id, conn):
        self.parent = parent
        self.kunden_id = kunden_id
        self.conn = conn
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Kundendaten anzeigen
        self.load_kunde_info(main_frame)
        
        # Fahrzeugliste
        fahrzeuge_frame = ttk.LabelFrame(main_frame, text="Fahrzeuge")
        fahrzeuge_frame.pack(fill="both", expand=True, pady=10)
        
        # Buttons für Fahrzeuge
        btn_frame = ttk.Frame(fahrzeuge_frame)
        btn_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Button(btn_frame, text="Neues Fahrzeug", command=self.new_fahrzeug).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bearbeiten", command=self.edit_fahrzeug).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Löschen", command=self.delete_fahrzeug).pack(side="left", padx=5)
        
        # Tabelle
        table_frame = ttk.Frame(fahrzeuge_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ('id', 'fahrzeug', 'kennzeichen', 'fahrgestellnr')
        self.fahrzeuge_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.fahrzeuge_tree.heading('id', text='ID')
        self.fahrzeuge_tree.heading('fahrzeug', text='Fahrzeugtyp')
        self.fahrzeuge_tree.heading('kennzeichen', text='Kennzeichen')
        self.fahrzeuge_tree.heading('fahrgestellnr', text='Fahrgestellnummer')
        
        self.fahrzeuge_tree.column('id', width=50, anchor='center')
        self.fahrzeuge_tree.column('fahrzeug', width=200)
        self.fahrzeuge_tree.column('kennzeichen', width=100)
        self.fahrzeuge_tree.column('fahrgestellnr', width=150)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.fahrzeuge_tree.yview)
        self.fahrzeuge_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.fahrzeuge_tree.pack(side="left", fill="both", expand=True)
        
        # Doppelklick zum Bearbeiten
        self.fahrzeuge_tree.bind("<Double-1>", lambda event: self.edit_fahrzeug())
        
        # Buttons
        dialog_btn_frame = ttk.Frame(main_frame)
        dialog_btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(dialog_btn_frame, text="Schließen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Fahrzeuge laden
        self.load_fahrzeuge()
        
        self.dialog.wait_window()
        
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
            kunde_frame = ttk.Frame(parent_frame)
            kunde_frame.pack(fill="x", expand=False, pady=5)
            
            ttk.Label(kunde_frame, text=f"Kunde: {kunde[0]} {kunde[1]}", font=("Arial", 11, "bold")).pack(side="left", padx=5)
            ttk.Label(kunde_frame, text=f"Telefon: {kunde[2]}").pack(side="right", padx=5)
    
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
        for row in cursor.fetchall():
            self.fahrzeuge_tree.insert('', 'end', values=row)
    
    def get_selected_fahrzeug_id(self):
        """Gibt die ID des ausgewählten Fahrzeugs zurück"""
        selected_items = self.fahrzeuge_tree.selection()
        if not selected_items:
            return None
            
        return self.fahrzeuge_tree.item(selected_items[0])['values'][0]
    
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
        
        # Prüfen, ob das Fahrzeug in Aufträgen verwendet wird
        cursor = self.conn.cursor()
        # Diese Abfrage muss angepasst werden, wenn Aufträge mit Fahrzeug-ID verknüpft werden
        
        # Bestätigung einholen
        fahrzeug_info = f"{fahrzeug_typ} ({kennzeichen})" if kennzeichen else fahrzeug_typ
        if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie das Fahrzeug '{fahrzeug_info}' wirklich löschen?"):
            try:
                cursor.execute("DELETE FROM fahrzeuge WHERE id = ?", (fahrzeug_id,))
                self.conn.commit()
                self.load_fahrzeuge()
                self.result = True
            except sqlite3.Error as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen des Fahrzeugs: {e}")
                self.conn.rollback()