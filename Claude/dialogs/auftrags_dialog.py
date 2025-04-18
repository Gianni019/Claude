#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialog zum Erstellen und Bearbeiten von Aufträgen
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # simpledialog wurde hinzugefügt
import sqlite3
from datetime import datetime

from dialogs.kunden_dialog import KundenDialog
from dialogs.teile_dialog import TeileAuswahlDialog

class AuftragsDialog:
    """Dialog zum Erstellen und Bearbeiten von Aufträgen"""
    def __init__(self, parent, title, auftrag_id=None, conn=None, kunden_id=None):
        self.parent = parent
        self.auftrag_id = auftrag_id
        self.conn = conn
        self.kunden_id = kunden_id
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x700")  # Größere Dialogfenster
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Kundenauswahl
        kunde_frame = ttk.LabelFrame(main_frame, text="Kunde")
        kunde_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(kunde_frame, text="Kunde:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.kunde_var = tk.StringVar()
        self.kunden_combo = ttk.Combobox(kunde_frame, textvariable=self.kunde_var, width=40)
        self.kunden_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.kunden_combo.bind("<<ComboboxSelected>>", self.on_kunde_selected)
        
        ttk.Button(kunde_frame, text="Neuer Kunde", command=self.new_kunde).grid(row=0, column=2, padx=5, pady=5)
        
        # Fahrzeugauswahl
        ttk.Label(kunde_frame, text="Fahrzeug:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.fahrzeug_var = tk.StringVar()
        self.fahrzeug_combo = ttk.Combobox(kunde_frame, textvariable=self.fahrzeug_var, width=40)
        self.fahrzeug_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Auftragsdaten
        auftrag_frame = ttk.LabelFrame(main_frame, text="Auftragsdaten")
        auftrag_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(auftrag_frame, text="Beschreibung:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.beschreibung_var = tk.StringVar()
        ttk.Entry(auftrag_frame, textvariable=self.beschreibung_var, width=70).grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Offen")
        status_combo = ttk.Combobox(auftrag_frame, textvariable=self.status_var, width=20,
                                     values=["Offen", "In Bearbeitung", "Warten auf Teile", "Abgeschlossen"])
        status_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Priorität:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.prioritaet_var = tk.StringVar(value="Normal")
        prioritaet_combo = ttk.Combobox(auftrag_frame, textvariable=self.prioritaet_var, width=15,
                                        values=["Niedrig", "Normal", "Hoch", "Dringend"])
        prioritaet_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(auftrag_frame, text="Arbeitszeit (h):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.arbeitszeit_var = tk.StringVar(value="0")
        ttk.Entry(auftrag_frame, textvariable=self.arbeitszeit_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Notizen
        ttk.Label(auftrag_frame, text="Notizen:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.notizen_text = tk.Text(auftrag_frame, height=5, width=70)  # Größeres Textfeld
        self.notizen_text.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Ersatzteile
        teile_frame = ttk.LabelFrame(main_frame, text="Verwendete Ersatzteile")
        teile_frame.pack(fill="both", expand=True, pady=5)
        
        # Buttons für Teile
        teile_btn_frame = ttk.Frame(teile_frame)
        teile_btn_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Button(teile_btn_frame, text="Teil hinzufügen", command=self.add_part).pack(side="left", padx=5)
        ttk.Button(teile_btn_frame, text="Teil entfernen", command=self.remove_part).pack(side="left", padx=5)
        # Rabatt bearbeiten Button
        ttk.Button(teile_btn_frame, text="Rabatt bearbeiten", command=self.edit_rabatt).pack(side="left", padx=5)
        
        # Tabelle für Teile
        table_frame = ttk.Frame(teile_frame)
        table_frame.pack(fill="both", expand=True, pady=5)
        
        # Tabellenspalten erweitern für Rabatt
        self.teile_tree = ttk.Treeview(table_frame, columns=('id', 'name', 'menge', 'preis', 'rabatt', 'gesamtpreis'), 
                                      show='headings', height=8)  # Höhere Tabelle
        self.teile_tree.heading('id', text='ID')
        self.teile_tree.heading('name', text='Bezeichnung')
        self.teile_tree.heading('menge', text='Menge')
        self.teile_tree.heading('preis', text='Einzelpreis (CHF)')
        self.teile_tree.heading('rabatt', text='Rabatt (%)')  # Neue Spalte für Rabatt
        self.teile_tree.heading('gesamtpreis', text='Gesamtpreis (CHF)')  # Neue Spalte für Gesamtpreis nach Rabatt
        
        self.teile_tree.column('id', width=50, anchor='center')
        self.teile_tree.column('name', width=300)
        self.teile_tree.column('menge', width=80, anchor='center')
        self.teile_tree.column('preis', width=100, anchor='e')
        self.teile_tree.column('rabatt', width=80, anchor='center')  # Breite für Rabatt-Spalte
        self.teile_tree.column('gesamtpreis', width=120, anchor='e')  # Breite für Gesamtpreis-Spalte
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.teile_tree.yview)
        self.teile_tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.teile_tree.pack(side="left", fill="both", expand=True)
        
        # Auftragssumme anzeigen
        summen_frame = ttk.Frame(main_frame)
        summen_frame.pack(fill="x", expand=False, pady=5)
        
        ttk.Label(summen_frame, text="Auftragssumme:").pack(side="left", padx=5)
        self.gesamtsumme_var = tk.StringVar(value="0.00 CHF")
        ttk.Label(summen_frame, textvariable=self.gesamtsumme_var, font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", expand=False, pady=10)
        
        ttk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Kunden laden
        self.load_kunden()
        
        # Wenn ein Auftrag bearbeitet wird, Daten laden
        if self.auftrag_id:
            self.load_data()
        elif self.kunden_id:
            # Vorauswahl des Kunden, wenn von Kundendialog aufgerufen
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, vorname || ' ' || nachname FROM kunden WHERE id = ?", (self.kunden_id,))
            kunde = cursor.fetchone()
            if kunde:
                self.kunde_var.set(f"{kunde[0]}: {kunde[1]}")
                # Fahrzeuge für ausgewählten Kunden laden
                self.load_fahrzeuge_for_kunde(self.kunden_id)
            
        self.dialog.wait_window()
        
    def load_kunden(self):
        """Lädt die Kundenliste für die Combobox"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, vorname || ' ' || nachname as name FROM kunden ORDER BY name")
        
        self.kunden_combo['values'] = [f"{id}: {name}" for id, name in cursor.fetchall()]
    
    def on_kunde_selected(self, event):
        """Wird ausgeführt, wenn ein Kunde ausgewählt wird"""
        try:
            # Kunden-ID aus Combobox-Auswahl extrahieren
            kunden_id = int(self.kunde_var.get().split(":")[0])
            # Fahrzeuge für diesen Kunden laden
            self.load_fahrzeuge_for_kunde(kunden_id)
        except (ValueError, IndexError):
            # Bei ungültiger Auswahl nichts tun
            pass
            
    def load_fahrzeuge_for_kunde(self, kunden_id):
        """Lädt die Fahrzeuge für den ausgewählten Kunden"""
        if not kunden_id:
            # Fahrzeug-Combobox leeren
            self.fahrzeug_combo['values'] = []
            self.fahrzeug_var.set("")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, fahrzeug_typ || ' (' || COALESCE(kennzeichen, 'ohne Kennzeichen') || ')' as fahrzeug_info
        FROM fahrzeuge
        WHERE kunden_id = ?
        ORDER BY fahrzeug_typ
        """, (kunden_id,))
        
        fahrzeuge = cursor.fetchall()
        if fahrzeuge:
            self.fahrzeug_combo['values'] = [f"{id}: {info}" for id, info in fahrzeuge]
            # Erstes Fahrzeug auswählen
            self.fahrzeug_var.set(self.fahrzeug_combo['values'][0])
        else:
            self.fahrzeug_combo['values'] = ["Kein Fahrzeug vorhanden"]
            self.fahrzeug_var.set("")
    def load_data(self):
        """Lädt die Daten des zu bearbeitenden Auftrags"""
        cursor = self.conn.cursor()
        
        # ... bestehender Code ...
            
        # Verwendete Teile laden
        cursor.execute("""
        SELECT e.id, e.bezeichnung, ae.menge, ae.einzelpreis, ae.rabatt
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (self.auftrag_id,))
        
        # Teile-Tabelle leeren
        for item in self.teile_tree.get_children():
            self.teile_tree.delete(item)
            
        # Teile hinzufügen
        for row in cursor.fetchall():
            # Standardwerte für Rabatt setzen, falls NULL
            rabatt = row[4] if row[4] is not None else 0.0
            einzelpreis = row[3]
            menge = row[2]
            
            # Gesamtpreis mit Rabatt berechnen
            gesamtpreis = menge * einzelpreis * (1 - rabatt/100)
            
            print(f"DEBUG - Lade Teil: ID={row[0]}, '{row[1]}', Menge={menge}, Preis={einzelpreis}, Rabatt={rabatt}%, Gesamtpreis={gesamtpreis}")
            
            self.teile_tree.insert('', 'end', values=(
                row[0], row[1], menge, f"{einzelpreis:.2f} CHF", 
                f"{rabatt:.2f}%", f"{gesamtpreis:.2f} CHF"
            ))
            
        # Gesamtsumme aktualisieren
        self.update_gesamtsumme()
            
    def new_kunde(self):
        """Öffnet den Dialog zum Anlegen eines neuen Kunden"""
        from dialogs.kunden_dialog import KundenDialog
        kundendialog = KundenDialog(self.dialog, "Neuer Kunde", None, self.conn)
        if kundendialog.result:
            # Kundenliste aktualisieren
            self.load_kunden()
            
            # Neu angelegten Kunden auswählen
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT id, vorname || ' ' || nachname
            FROM kunden
            ORDER BY id DESC
            LIMIT 1
            """)
            
            last_kunde = cursor.fetchone()
            if last_kunde:
                self.kunde_var.set(f"{last_kunde[0]}: {last_kunde[1]}")
                # Fahrzeuge für diesen Kunden laden (wird in diesem Fall leer sein)
                self.load_fahrzeuge_for_kunde(last_kunde[0])
                
    def add_part(self):
        """Fügt ein Ersatzteil zum Auftrag hinzu"""
        teile_dialog = TeileAuswahlDialog(self.dialog, "Teil hinzufügen", None, self.conn)
        if teile_dialog.result:
            # Ausgewähltes Teil hinzufügen
            for teil_id, bezeichnung, menge, preis, einheit in teile_dialog.result:
                # Prüfen, ob Teil bereits in der Liste ist
                for item in self.teile_tree.get_children():
                    if self.teile_tree.item(item)['values'][0] == teil_id:
                        # Menge aktualisieren
                        current_menge = int(self.teile_tree.item(item)['values'][2])
                        new_menge = current_menge + menge
                        
                        # Rabatt und Gesamtpreis berechnen
                        rabatt_str = self.teile_tree.item(item)['values'][4]
                        if "%" in rabatt_str:
                            rabatt_str = rabatt_str.replace("%", "")
                        rabatt = float(rabatt_str.replace(',', '.'))
                        
                        gesamtpreis = new_menge * preis * (1 - rabatt/100)
                        
                        self.teile_tree.item(item, values=(
                            teil_id, bezeichnung, new_menge, f"{preis:.2f} CHF", 
                            f"{rabatt:.2f}%", f"{gesamtpreis:.2f} CHF"
                        ))
                        break
                else:
                    # Neues Teil hinzufügen mit Standardrabatt 0%
                    rabatt = 0.0
                    gesamtpreis = menge * preis
                    
                    self.teile_tree.insert('', 'end', values=(
                        teil_id, bezeichnung, menge, f"{preis:.2f} CHF", 
                        f"{rabatt:.2f}%", f"{gesamtpreis:.2f} CHF"
                    ))
            
            # Gesamtsumme aktualisieren
            self.update_gesamtsumme()
                
    def remove_part(self):
        """Entfernt ein Ersatzteil aus dem Auftrag"""
        selected_items = self.teile_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Teil aus.")
            return
            
        # Ausgewähltes Teil entfernen
        for item in selected_items:
            self.teile_tree.delete(item)
            
        # Gesamtsumme aktualisieren
        self.update_gesamtsumme()
            
    def edit_rabatt(self):
        """Ändert den Rabatt für eine Position"""
        selected_items = self.teile_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Bitte wählen Sie ein Teil aus.")
            return
            
        # Aktuelle Werte auslesen
        values = self.teile_tree.item(selected_items[0])['values']
        
        # Rabatt auslesen (wenn vorhanden)
        rabatt = 0.0
        if len(values) > 4:  # Prüfen, ob Rabatt-Spalte existiert
            rabatt_str = str(values[4])
            if "%" in rabatt_str:
                rabatt_str = rabatt_str.replace("%", "")
            try:
                rabatt = float(rabatt_str.replace(',', '.'))
            except ValueError:
                rabatt = 0.0
        
        # Dialog zur Eingabe des neuen Rabatts
        neuer_rabatt = simpledialog.askfloat(
            "Rabatt bearbeiten",
            "Neuer Rabatt (%):",
            parent=self.dialog,
            initialvalue=rabatt,
            minvalue=0.0,
            maxvalue=100.0
        )
        
        if neuer_rabatt is not None:
            # Gesamtpreis berechnen
            teil_id = values[0]
            bezeichnung = values[1]
            menge = values[2]
            einzelpreis_str = str(values[3])
            
            if " CHF" in einzelpreis_str:
                einzelpreis_str = einzelpreis_str.replace(" CHF", "")
            
            einzelpreis = float(einzelpreis_str.replace(',', '.'))
            
            # Gesamtpreis berechnen (mit Rabatt)
            gesamtpreis = menge * einzelpreis
            rabatt_betrag = gesamtpreis * (neuer_rabatt / 100)
            gesamtpreis_nach_rabatt = gesamtpreis - rabatt_betrag
            
            # Werte aktualisieren
            self.teile_tree.item(selected_items[0], values=(
                teil_id, bezeichnung, menge, f"{einzelpreis:.2f} CHF", 
                f"{neuer_rabatt:.2f}%", f"{gesamtpreis_nach_rabatt:.2f} CHF"
            ))
            
            # Gesamtsumme aktualisieren
            self.update_gesamtsumme()
        
    def update_gesamtsumme(self):
        """Aktualisiert die Gesamtsumme des Auftrags"""
        gesamtsumme = 0.0
        
        # Alle Positionen durchlaufen
        for item in self.teile_tree.get_children():
            values = self.teile_tree.item(item)['values']
            
            # Gesamtpreis auslesen, wenn vorhanden
            if len(values) > 5:  # Prüfen, ob Gesamtpreis-Spalte existiert
                gesamtpreis_str = str(values[5])
                if " CHF" in gesamtpreis_str:
                    gesamtpreis_str = gesamtpreis_str.replace(" CHF", "")
                try:
                    gesamtpreis = float(gesamtpreis_str.replace(',', '.'))
                    gesamtsumme += gesamtpreis
                except ValueError:
                    pass
            else:
                # Fallback: Berechnung ohne Rabatt
                menge_str = str(values[2])
                einzelpreis_str = str(values[3])
                
                if " CHF" in einzelpreis_str:
                    einzelpreis_str = einzelpreis_str.replace(" CHF", "")
                    
                try:
                    menge = float(menge_str)
                    einzelpreis = float(einzelpreis_str.replace(',', '.'))
                    gesamtsumme += menge * einzelpreis
                except ValueError:
                    pass
        
        # Gesamtsumme anzeigen
        self.gesamtsumme_var.set(f"{gesamtsumme:.2f} CHF")
    
    def save_data(self):
        """Speichert die Auftragsdaten"""
        # Pflichtfelder prüfen
        if not self.kunde_var.get() or not self.beschreibung_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden und geben Sie eine Beschreibung ein.")
            return
        
        try:
            # Kunden-ID aus Combobox-Auswahl extrahieren
            kunden_id = int(self.kunde_var.get().split(":")[0])
            
            # Fahrzeug-ID extrahieren, falls vorhanden
            fahrzeug_id = None
            if self.fahrzeug_var.get() and ":" in self.fahrzeug_var.get():
                try:
                    fahrzeug_id = int(self.fahrzeug_var.get().split(":")[0])
                except (ValueError, IndexError):
                    fahrzeug_id = None
            
            cursor = self.conn.cursor()
            
            if self.auftrag_id:  # Bestehenden Auftrag aktualisieren
                cursor.execute("""
                UPDATE auftraege SET 
                    kunden_id = ?, beschreibung = ?, status = ?, prioritaet = ?,
                    arbeitszeit = ?, notizen = ?, fahrzeug_id = ?
                WHERE id = ?
                """, (
                    kunden_id, self.beschreibung_var.get(), self.status_var.get(), 
                    self.prioritaet_var.get(), float(self.arbeitszeit_var.get() or 0),
                    self.notizen_text.get(1.0, tk.END).strip(), fahrzeug_id, self.auftrag_id
                ))
                
                # Bestehende Teile-Verknüpfungen löschen
                cursor.execute("DELETE FROM auftrag_ersatzteile WHERE auftrag_id = ?", (self.auftrag_id,))
                
                auftrag_id_to_use = self.auftrag_id  # Verwende die bestehende Auftrags-ID
                    
            else:  # Neuen Auftrag anlegen
                cursor.execute("""
                INSERT INTO auftraege (
                    kunden_id, beschreibung, status, prioritaet, erstellt_am,
                    abgeschlossen_am, arbeitszeit, notizen, fahrzeug_id
                ) VALUES (?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
                """, (
                    kunden_id, self.beschreibung_var.get(), self.status_var.get(), 
                    self.prioritaet_var.get(), 
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S') if self.status_var.get() == "Abgeschlossen" else None,
                    float(self.arbeitszeit_var.get() or 0), self.notizen_text.get(1.0, tk.END).strip(), fahrzeug_id
                ))
                
                # Die ID des neuen Auftrags ermitteln
                cursor.execute("SELECT last_insert_rowid()")
                auftrag_id_to_use = cursor.fetchone()[0]
            
            # Teile zum Auftrag hinzufügen (jetzt unabhängig davon, ob neu oder bestehend)
            for item in self.teile_tree.get_children():
                values = self.teile_tree.item(item)['values']
                ersatzteil_id = values[0]
                menge = values[2]
                
                # Einzelpreis extrahieren
                einzelpreis_str = str(values[3])
                if " CHF" in einzelpreis_str:
                    einzelpreis_str = einzelpreis_str.replace(" CHF", "")
                einzelpreis = float(einzelpreis_str.replace(',', '.'))
                
                # Rabatt extrahieren
                rabatt_str = str(values[4])
                if "%" in rabatt_str:
                    rabatt_str = rabatt_str.replace("%", "")
                rabatt = float(rabatt_str.replace(',', '.'))
                
                print(f"DEBUG - Speichere Ersatzteil: ID={ersatzteil_id}, Menge={menge}, Preis={einzelpreis}, Rabatt={rabatt}%")
                
                # Prüfen, ob die rabatt-Spalte in der Tabelle existiert
                try:
                    # Zuerst ohne rabatt versuchen
                    cursor.execute("""
                    PRAGMA table_info(auftrag_ersatzteile)
                    """)
                    columns = [info[1] for info in cursor.fetchall()]
                    
                    if 'rabatt' in columns:
                        # Mit rabatt einfügen
                        print(f"DEBUG - Füge Eintrag mit Rabatt-Spalte ein: {rabatt}%")
                        cursor.execute("""
                        INSERT INTO auftrag_ersatzteile (auftrag_id, ersatzteil_id, menge, einzelpreis, rabatt)
                        VALUES (?, ?, ?, ?, ?)
                        """, (auftrag_id_to_use, ersatzteil_id, menge, einzelpreis, rabatt))
                    else:
                        # Ohne rabatt einfügen
                        print("DEBUG - Rabatt-Spalte nicht gefunden, füge ohne Rabatt ein")
                        cursor.execute("""
                        INSERT INTO auftrag_ersatzteile (auftrag_id, ersatzteil_id, menge, einzelpreis)
                        VALUES (?, ?, ?, ?)
                        """, (auftrag_id_to_use, ersatzteil_id, menge, einzelpreis))
                        
                        # Warnung anzeigen
                        messagebox.showwarning("Hinweis", 
                                            "Die Rabatt-Spalte wurde in der Datenbank nicht gefunden!\n"
                                            "Bitte führen Sie das Datenbankupdate auf Version 5 durch.")
                except sqlite3.OperationalError as e:
                    print(f"DEBUG - SQL-Fehler: {e}")
                    # Fallback: Ohne Rabatt einfügen
                    cursor.execute("""
                    INSERT INTO auftrag_ersatzteile (auftrag_id, ersatzteil_id, menge, einzelpreis)
                    VALUES (?, ?, ?, ?)
                    """, (auftrag_id_to_use, ersatzteil_id, menge, einzelpreis))
            
            # Commit ausführen und Ergebnis setzen
            # HIER WAR DER FEHLER: conn.commit() -> self.conn.commit()
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            # Detaillierte Fehlerinformationen anzeigen
            print(f"Fehler beim Speichern: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Auftragsdaten: {e}")
            self.conn.rollback()