#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Einstellungsdialog für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import base64
import sqlite3
from PIL import Image, ImageTk

from utils.config import get_company_info, set_company_info, get_default_stundenlohn, set_default_stundenlohn

class SettingsDialog:
    """Dialog für Anwendungseinstellungen"""
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.logo_path = None
        self.logo_data = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("650x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe mit Tabs
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs erstellen
        self.create_company_tab()
        self.create_financial_tab()
        self.create_design_tab()
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_settings).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Daten laden
        self.load_settings()
        
        self.dialog.wait_window()
        
    def create_company_tab(self):
        """Tab für Firmeninformationen erstellen"""
        company_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(company_frame, text="Firmeninformationen")
        
        # Firmenname
        ttk.Label(company_frame, text="Firmenname:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.company_name_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_name_var, width=40).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Adresse
        ttk.Label(company_frame, text="Adresse:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.company_address_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_address_var, width=40).grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Telefon
        ttk.Label(company_frame, text="Telefon:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.company_phone_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_phone_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Email
        ttk.Label(company_frame, text="E-Mail:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.company_email_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_email_var, width=30).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Website
        ttk.Label(company_frame, text="Website:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.company_website_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_website_var, width=30).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Bankverbindung
        bank_frame = ttk.LabelFrame(company_frame, text="Bankverbindung", padding=5)
        bank_frame.grid(row=5, column=0, columnspan=3, sticky="we", padx=5, pady=10)
        
        ttk.Label(bank_frame, text="Bank:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.bank_name_var = tk.StringVar()
        ttk.Entry(bank_frame, textvariable=self.bank_name_var, width=30).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(bank_frame, text="IBAN:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bank_iban_var = tk.StringVar()
        ttk.Entry(bank_frame, textvariable=self.bank_iban_var, width=30).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(bank_frame, text="BIC/SWIFT:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.bank_bic_var = tk.StringVar()
        ttk.Entry(bank_frame, textvariable=self.bank_bic_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
    def create_financial_tab(self):
        """Tab für finanzielle Einstellungen erstellen"""
        financial_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(financial_frame, text="Finanzen")
        
        # Stundenlohn
        ttk.Label(financial_frame, text="Standard-Stundenlohn (CHF):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hourly_rate_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.hourly_rate_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # MwSt-Satz
        ttk.Label(financial_frame, text="MwSt-Satz (%):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.vat_rate_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.vat_rate_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Zahlungsfrist
        ttk.Label(financial_frame, text="Standard-Zahlungsfrist (Tage):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.payment_term_var = tk.StringVar()
        ttk.Entry(financial_frame, textvariable=self.payment_term_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Standard-Rabatt
        ttk.Label(financial_frame, text="Standard-Rabatt (%):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.discount_var = tk.StringVar(value="0")
        ttk.Entry(financial_frame, textvariable=self.discount_var, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
    def create_design_tab(self):
        """Tab für Design-Einstellungen erstellen"""
        design_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(design_frame, text="Design")
        
        # Firmenlogo
        logo_frame = ttk.LabelFrame(design_frame, text="Firmenlogo", padding=5)
        logo_frame.pack(fill="x", expand=False, pady=10)
        
        self.logo_preview = ttk.Label(logo_frame)
        self.logo_preview.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Button(logo_frame, text="Logo auswählen", command=self.select_logo).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(logo_frame, text="Logo entfernen", command=self.remove_logo).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
    def select_logo(self):
        """Öffnet einen Dialog zur Auswahl eines Logos"""
        file_path = filedialog.askopenfilename(
            parent=self.dialog,
            title="Logo auswählen",
            filetypes=[("Bildateien", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                # Bild öffnen und für die Vorschau skalieren
                image = Image.open(file_path)
                image = image.resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.logo_preview.config(image=photo)
                self.logo_preview.image = photo  # Referenz behalten
                
                # Pfad und Daten speichern
                self.logo_path = file_path
                
                # Bilddaten als Base64 für Speicherung in der Datenbank
                with open(file_path, "rb") as f:
                    self.logo_data = base64.b64encode(f.read()).decode('utf-8')
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden des Logos: {e}")
    
    def remove_logo(self):
        """Entfernt das aktuell ausgewählte Logo"""
        self.logo_preview.config(image="")
        self.logo_path = None
        self.logo_data = None
        
    def load_settings(self):
        """Lädt die aktuellen Einstellungen"""
        # Firmendaten laden
        company_info = get_company_info(self.conn)
        
        self.company_name_var.set(company_info['name'])
        self.company_address_var.set(company_info['address'])
        self.company_phone_var.set(company_info['phone'])
        self.company_email_var.set(company_info['email'])
        self.company_website_var.set(company_info.get('website', ''))
        
        self.bank_name_var.set(company_info.get('bank_name', ''))
        self.bank_iban_var.set(company_info.get('bank_iban', ''))
        self.bank_bic_var.set(company_info.get('bank_bic', ''))
        
        # Finanzeinstellungen laden
        self.hourly_rate_var.set(str(get_default_stundenlohn(self.conn)))
        self.vat_rate_var.set(company_info['mwst'])
        self.payment_term_var.set(company_info.get('zahlungsfrist', '30'))
        self.discount_var.set(company_info.get('standard_rabatt', '0'))
        
        # Logo laden
        cursor = self.conn.cursor()
        cursor.execute("SELECT wert FROM konfiguration WHERE schluessel = 'firmenlogo'")
        row = cursor.fetchone()
        
        if row and row[0]:
            try:
                # Base64-kodiertes Bild decodieren und anzeigen
                logo_data = base64.b64decode(row[0])
                
                # In temporäre Datei speichern und mit PIL öffnen
                with open('temp_logo.png', 'wb') as f:
                    f.write(logo_data)
                
                image = Image.open('temp_logo.png')
                image = image.resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.logo_preview.config(image=photo)
                self.logo_preview.image = photo  # Referenz behalten
                
                self.logo_data = row[0]  # Original Base64-Daten beibehalten
                
                # Temporäre Datei löschen
                os.remove('temp_logo.png')
                
            except Exception as e:
                print(f"Fehler beim Laden des Logos: {e}")
        
    def save_settings(self):
        """Speichert die Einstellungen"""
        try:
            # Stundenlohn validieren und speichern
            try:
                hourly_rate = float(self.hourly_rate_var.get().replace(',', '.'))
                if hourly_rate <= 0:
                    raise ValueError("Der Stundenlohn muss größer als 0 sein.")
                set_default_stundenlohn(self.conn, hourly_rate)
            except ValueError as e:
                messagebox.showerror("Fehler", f"Ungültiger Stundenlohn: {e}")
                return
            
            # Firmendaten speichern
            company_info = {
                'name': self.company_name_var.get(),
                'address': self.company_address_var.get(),
                'phone': self.company_phone_var.get(),
                'email': self.company_email_var.get(),
                'website': self.company_website_var.get(),
                'mwst': self.vat_rate_var.get(),
                'bank_name': self.bank_name_var.get(),
                'bank_iban': self.bank_iban_var.get(),
                'bank_bic': self.bank_bic_var.get(),
                'zahlungsfrist': self.payment_term_var.get(),
                'standard_rabatt': self.discount_var.get()
            }
            
            set_company_info(self.conn, company_info)
            
            # Logo speichern, falls vorhanden
            if self.logo_data:
                cursor = self.conn.cursor()
                cursor.execute("SELECT 1 FROM konfiguration WHERE schluessel = 'firmenlogo'")
                if cursor.fetchone():
                    cursor.execute("UPDATE konfiguration SET wert = ? WHERE schluessel = 'firmenlogo'", 
                                  (self.logo_data,))
                else:
                    cursor.execute("INSERT INTO konfiguration (schluessel, wert, beschreibung) VALUES (?, ?, ?)", 
                                  ('firmenlogo', self.logo_data, 'Firmenlogo als Base64'))
                self.conn.commit()
            elif self.logo_data is None and self.logo_path is None:
                # Logo entfernen
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM konfiguration WHERE schluessel = 'firmenlogo'")
                self.conn.commit()
            
            messagebox.showinfo("Information", "Einstellungen wurden gespeichert.")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {e}")