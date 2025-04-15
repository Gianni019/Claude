#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kalender- und Terminverwaltung für die Autowerkstatt-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import calendar
import locale

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

class ModernButton(tk.Button):
    def __init__(self, parent, text, command, primary=False, **kwargs):
        bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
        fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
        
        super().__init__(parent, text=text, command=command, 
                        bg=bg_color, fg=fg_color,
                        activebackground=COLORS["text_light"], 
                        activeforeground=COLORS["bg_dark"],
                        relief="flat", borderwidth=0, padx=15, pady=8,
                        font=("Arial", 10), cursor="hand2", **kwargs)

class KalenderVerwaltung:
    """Hauptklasse für die Kalenderverwaltung"""
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        
        # Spracheinstellung für Monatsnamen
        try:
            locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')  # Deutsch
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'de_DE')
            except:
                pass  # Fallback auf Systemstandard
        
        # Aktuelles Datum für die Anzeige
        self.current_date = datetime.now()
        self.selected_date = datetime.now()
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Werkstattkalender")
        self.dialog.geometry("1100x700")
        self.dialog.transient(parent)
        
        # Dunkler Hintergrund für das Dialog-Fenster
        self.dialog.configure(bg=COLORS["bg_dark"])
        
        # Hauptcontainer mit Grid-Layout
        self.main_container = ttk.Frame(self.dialog, style="Card.TFrame")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Kalender-Header mit Monatsnavigation
        self.create_calendar_header()
        
        # Hauptbereich: Kalender links, Details rechts
        content_frame = ttk.Frame(self.main_container, style="Card.TFrame")
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Linke Seite - Kalender
        self.calendar_frame = ttk.Frame(content_frame, style="Card.TFrame", width=700)
        self.calendar_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Rechte Seite - Termindetails
        self.details_frame = ttk.Frame(content_frame, style="Card.TFrame", width=380)
        self.details_frame.pack(side="right", fill="both", expand=False, padx=(10, 0))
        
        # Kalender erstellen
        self.create_calendar()
        
        # Termin-Details erstellen
        self.create_appointment_details()
        
        # Datenbank-Schema prüfen/aktualisieren
        self.check_appointments_table()
        
        # Termine für den aktuellen Monat laden
        self.load_appointments()
    
    def create_calendar_header(self):
        """Erstellt den Kalender-Header mit Navigation"""
        header_frame = ttk.Frame(self.main_container, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Titel und Navigation
        title_frame = ttk.Frame(header_frame, style="Card.TFrame")
        title_frame.pack(fill="x", pady=5)
        
        # Vorheriger Monat
        prev_btn = ModernButton(title_frame, text="◀", command=self.previous_month, 
                              font=("Arial", 12), padx=10)
        prev_btn.pack(side="left", padx=5)
        
        # Aktueller Monat und Jahr
        self.month_label = ttk.Label(title_frame, text="", 
                                   style="CardTitle.TLabel", font=("Arial", 16, "bold"))
        self.month_label.pack(side="left", padx=20)
        self.update_month_label()
        
        # Nächster Monat
        next_btn = ModernButton(title_frame, text="▶", command=self.next_month, 
                              font=("Arial", 12), padx=10)
        next_btn.pack(side="left", padx=5)
        
        # Zum aktuellen Monat zurückkehren
        today_btn = ModernButton(title_frame, text="Heute", command=self.go_to_today, 
                               primary=True)
        today_btn.pack(side="right", padx=5)
        
        # Ansicht-Auswahl
        view_frame = ttk.Frame(header_frame, style="Card.TFrame")
        view_frame.pack(side="right", padx=10)
        
        ttk.Label(view_frame, text="Ansicht:", style="CardText.TLabel").pack(side="left", padx=5)
        self.view_var = tk.StringVar(value="Monat")
        view_combo = ttk.Combobox(view_frame, textvariable=self.view_var, width=10,
                                 values=["Tag", "Woche", "Monat"])
        view_combo.pack(side="left", padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.change_view)
    
    def create_calendar(self):
        """Erstellt den Kalender für die aktuelle Monatsansicht"""
        # Bestehenden Kalender löschen
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Container für den Kalender
        calendar_container = ttk.Frame(self.calendar_frame, style="Card.TFrame")
        calendar_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Kopfzeile mit Wochentagen
        days_header = ttk.Frame(calendar_container, style="Card.TFrame")
        days_header.pack(fill="x", pady=5)
        
        days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        for i, day in enumerate(days):
            day_label = ttk.Label(days_header, text=day, style="CardTitle.TLabel",
                                font=("Arial", 10, "bold"))
            day_label.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            days_header.columnconfigure(i, weight=1)
        
        # Kalender-Grid
        self.days_frame = ttk.Frame(calendar_container, style="Card.TFrame")
        self.days_frame.pack(fill="both", expand=True, pady=5)
        
        # Tage des aktuellen Monats einfügen
        self.day_buttons = {}
        self.fill_calendar()
        
        # Gleiche Größe für alle Zellen
        for i in range(6):  # 6 Wochen maximal
            self.days_frame.rowconfigure(i, weight=1)
        for i in range(7):  # 7 Tage pro Woche
            self.days_frame.columnconfigure(i, weight=1)
    
    def fill_calendar(self):
        """Füllt den Kalender mit den Tagen des aktuellen Monats"""
        # Aktuelle Daten
        year = self.current_date.year
        month = self.current_date.month
        
        # Tagesbuttons leeren
        self.day_buttons = {}
        
        # Monatskalender abrufen
        cal = calendar.monthcalendar(year, month)
        
        # Tage einfügen
        for week_index, week in enumerate(cal):
            for day_index, day in enumerate(week):
                # Tag-Frame für jeden Tag erstellen
                day_frame = ttk.Frame(self.days_frame, style="Card.TFrame")
                day_frame.grid(row=week_index, column=day_index, sticky="nsew", padx=2, pady=2)
                self.days_frame.columnconfigure(day_index, weight=1)
                
                if day == 0:  # Leerer Tag
                    empty_label = ttk.Label(day_frame, text="", style="CardText.TLabel")
                    empty_label.pack(fill="both", expand=True)
                    day_frame.configure(style="TFrame")  # Hintergrund ändern
                    continue
                
                # Tag-Container
                day_container = ttk.Frame(day_frame, style="Card.TFrame")
                day_container.pack(fill="both", expand=True)
                
                # Kopfzeile mit Tagesnummer
                header_frame = ttk.Frame(day_container, style="Card.TFrame")
                header_frame.pack(fill="x", expand=False)
                
                # Aktuelle Tagesdaten
                current_day_date = datetime(year, month, day)
                is_today = current_day_date.date() == datetime.now().date()
                is_selected = current_day_date.date() == self.selected_date.date()
                is_weekend = day_index >= 5  # Sa/So
                
                # Tag-Button mit entsprechendem Styling
                day_btn = tk.Label(
                    header_frame, 
                    text=str(day), 
                    font=("Arial", 9, "bold" if is_today else "normal"),
                    bg=COLORS["accent"] if is_selected else (
                        COLORS["bg_light"] if is_weekend else COLORS["bg_medium"]
                    ),
                    fg=COLORS["bg_dark"] if is_selected else (
                        COLORS["warning"] if is_weekend else COLORS["text_light"]
                    ),
                    cursor="hand2",
                    padx=5,
                    pady=2,
                    width=2,
                    anchor="center"
                )
                day_btn.pack(side="left", padx=2, pady=2)
                
                # Klick-Event für Tagesauswahl
                day_btn.bind("<Button-1>", lambda e, d=day: self.select_day(d))
                
                # Container für Termine des Tages
                self.day_buttons[day] = {
                    'button': day_btn,
                    'container': day_container,
                    'date': current_day_date,
                    'appointments': []
                }
                
                # Termine-Container
                appointments_frame = ttk.Frame(day_container, style="Card.TFrame")
                appointments_frame.pack(fill="both", expand=True, pady=2)
                
                # Dummy-Label für Termine (wird beim Laden der Termine ersetzt)
                appointment_placeholder = ttk.Label(
                    appointments_frame, text="", style="CardText.TLabel",
                    font=("Arial", 8)
                )
                appointment_placeholder.pack(fill="x", expand=True)
                
                # Appointment-Container speichern
                self.day_buttons[day]['appointment_container'] = appointments_frame
    
    def select_day(self, day):
        """Wählt einen Tag aus"""
        # Datum aktualisieren
        self.selected_date = datetime(
            self.current_date.year, 
            self.current_date.month, 
            day
        )
        
        # Visuelles Feedback - Alle Tage zurücksetzen
        for d, data in self.day_buttons.items():
            day_btn = data['button']
            is_weekend = self.days_frame.grid_info(day_btn.master.master)['column'] >= 5
            day_btn.config(
                bg=COLORS["bg_light"] if is_weekend else COLORS["bg_medium"],
                fg=COLORS["warning"] if is_weekend else COLORS["text_light"]
            )
        
        # Ausgewählten Tag hervorheben
        if day in self.day_buttons:
            self.day_buttons[day]['button'].config(
                bg=COLORS["accent"],
                fg=COLORS["bg_dark"]
            )
        
        # Termine für den ausgewählten Tag anzeigen
        self.show_appointments_for_day()
    
    def previous_month(self):
        """Zum vorherigen Monat wechseln"""
        # Datum für den vorherigen Monat berechnen
        year = self.current_date.year
        month = self.current_date.month - 1
        
        if month < 1:
            month = 12
            year -= 1
            
        self.current_date = datetime(year, month, 1)
        self.update_month_label()
        self.fill_calendar()
        self.load_appointments()
    
    def next_month(self):
        """Zum nächsten Monat wechseln"""
        # Datum für den nächsten Monat berechnen
        year = self.current_date.year
        month = self.current_date.month + 1
        
        if month > 12:
            month = 1
            year += 1
            
        self.current_date = datetime(year, month, 1)
        self.update_month_label()
        self.fill_calendar()
        self.load_appointments()
    
    def go_to_today(self):
        """Zum aktuellen Monat und Tag wechseln"""
        today = datetime.now()
        
        # Nur wechseln, wenn nicht im aktuellen Monat
        if (self.current_date.year != today.year or 
            self.current_date.month != today.month):
            self.current_date = datetime(today.year, today.month, 1)
            self.update_month_label()
            self.fill_calendar()
            self.load_appointments()
        
        # Heutigen Tag auswählen
        self.select_day(today.day)
    
    def update_month_label(self):
        """Aktualisiert die Anzeige des Monats und Jahres"""
        # Formatierung für den Monat und Jahr
        month_name = self.current_date.strftime("%B %Y").capitalize()
        self.month_label.config(text=month_name)
    
    def change_view(self, event=None):
        """Wechselt zwischen Tages-, Wochen- und Monatsansicht"""
        view = self.view_var.get()
        
        # Aktuell wird nur die Monatsansicht implementiert
        # Hier könnten die anderen Ansichten ergänzt werden
        if view == "Monat":
            self.fill_calendar()
            self.load_appointments()
        elif view == "Woche":
            messagebox.showinfo("Information", 
                              "Die Wochenansicht wird in der nächsten Version implementiert.")
        elif view == "Tag":
            messagebox.showinfo("Information", 
                              "Die Tagesansicht wird in der nächsten Version implementiert.")
    
    def create_appointment_details(self):
        """Erstellt den Bereich für die Termindetails"""
        # Header für Termindetails
        header_frame = ttk.Frame(self.details_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=5)
        
        ttk.Label(header_frame, text="Termindetails", 
                style="CardTitle.TLabel", font=("Arial", 14, "bold")).pack(side="left")
        
        # Neuer Termin Button
        new_appointment_btn = ModernButton(header_frame, text="Neuer Termin", 
                                         command=self.new_appointment, primary=True)
        new_appointment_btn.pack(side="right", padx=5)
        
        # Ausgewähltes Datum anzeigen
        date_frame = ttk.Frame(self.details_frame, style="Card.TFrame")
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Ausgewählter Tag:", 
                style="CardText.TLabel").pack(side="left", padx=5)
        
        self.selected_date_label = ttk.Label(date_frame, 
                                          text=self.selected_date.strftime("%d.%m.%Y"), 
                                          style="CardTitle.TLabel")
        self.selected_date_label.pack(side="left", padx=5)
        
        # Termine für den ausgewählten Tag
        appointments_frame = ttk.LabelFrame(self.details_frame, text="Termine", 
                                         style="Card.TFrame")
        appointments_frame.pack(fill="both", expand=True, pady=5)
        
        # Container für die Terminliste
        self.appointment_list_container = ttk.Frame(appointments_frame, style="Card.TFrame")
        self.appointment_list_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Platzhalter für "Keine Termine"
        self.no_appointments_label = ttk.Label(self.appointment_list_container, 
                                            text="Keine Termine für diesen Tag", 
                                            style="CardText.TLabel")
        self.no_appointments_label.pack(fill="both", expand=True)
        
        # Container für Termindetails (wird dynamisch gefüllt)
        self.appointment_details_container = ttk.Frame(self.details_frame, style="Card.TFrame")
    
    def check_appointments_table(self):
        """Prüft, ob die Termine-Tabelle existiert und erstellt sie ggf."""
        cursor = self.conn.cursor()
        
        # Prüfen, ob die Tabelle existiert
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='termine'
        """)
        
        if not cursor.fetchone():
            # Tabelle erstellen, falls nicht vorhanden
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS termine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titel TEXT NOT NULL,
                beschreibung TEXT,
                datum DATE NOT NULL,
                uhrzeit_von TIME,
                uhrzeit_bis TIME,
                kunde_id INTEGER,
                auftrag_id INTEGER,
                status TEXT DEFAULT 'Geplant',
                farbe TEXT DEFAULT '#5ce0d8',
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kunde_id) REFERENCES kunden (id),
                FOREIGN KEY (auftrag_id) REFERENCES auftraege (id)
            )
            """)
            
            self.conn.commit()
    
    def load_appointments(self):
        """Lädt die Termine für den aktuellen Monat"""
        cursor = self.conn.cursor()
        
        # Monatsanfang und -ende berechnen
        year = self.current_date.year
        month = self.current_date.month
        
        # Erster und letzter Tag des Monats
        first_day = datetime(year, month, 1).strftime('%Y-%m-%d')
        
        # Letzter Tag berechnen (erster Tag des nächsten Monats - 1 Tag)
        if month == 12:
            last_day = datetime(year + 1, 1, 1)
        else:
            last_day = datetime(year, month + 1, 1)
        last_day = (last_day - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Termine für den Monat abrufen
        query = """
        SELECT id, titel, beschreibung, 
               date(datum) as datum_tag, 
               time(uhrzeit_von) as von, 
               time(uhrzeit_bis) as bis,
               kunde_id, auftrag_id, status, farbe
        FROM termine
        WHERE datum BETWEEN ? AND ?
        ORDER BY datum, uhrzeit_von
        """
        
        try:
            cursor.execute(query, (first_day, last_day))
            appointments = cursor.fetchall()
            
            # Termine dem jeweiligen Tag zuordnen
            for appt in appointments:
                appt_id, titel, beschreibung, datum, von, bis, kunde_id, auftrag_id, status, farbe = appt
                
                # Datum parsen
                year, month, day = map(int, datum.split('-'))
                
                # Termin dem entsprechenden Tag zuordnen
                if day in self.day_buttons:
                    appointment_data = {
                        'id': appt_id,
                        'title': titel,
                        'description': beschreibung,
                        'time_from': von,
                        'time_to': bis,
                        'customer_id': kunde_id,
                        'order_id': auftrag_id,
                        'status': status,
                        'color': farbe if farbe else COLORS["accent"]
                    }
                    
                    # Termin zur Liste hinzufügen
                    self.day_buttons[day]['appointments'].append(appointment_data)
                    
                    # Termin auf dem Kalender anzeigen
                    self.add_appointment_to_day(day, appointment_data)
            
            # Termine für den ausgewählten Tag aktualisieren
            self.show_appointments_for_day()
            
        except sqlite3.Error as e:
            print(f"Datenbankfehler beim Laden der Termine: {e}")
    
    def add_appointment_to_day(self, day, appointment):
        """Fügt einen Termin-Eintrag zum Kalender hinzu"""
        if day not in self.day_buttons:
            return
            
        day_data = self.day_buttons[day]
        container = day_data['appointment_container']
        
        # Bestehende Einträge löschen
        for widget in container.winfo_children():
            if widget.winfo_name() == 'appointment':
                widget.destroy()
        
        # Termin-Einträge erstellen für alle Termine des Tages
        for i, appt in enumerate(day_data['appointments']):
            if i >= 3:  # Max. 3 Termine anzeigen
                # "+X weitere" Anzeige
                more_label = ttk.Label(
                    container, 
                    text=f"+{len(day_data['appointments']) - 3} weitere", 
                    background=COLORS["bg_light"],
                    foreground=COLORS["text_light"],
                    font=("Arial", 7),
                    anchor="w",
                    padding=(3, 0)
                )
                more_label.pack(fill="x", padx=1, pady=1)
                more_label.winfo_name = lambda: 'appointment'
                break
                
            # Zeitanzeige formatieren, falls vorhanden
            time_text = ""
            if appt['time_from']:
                from_time = appt['time_from']
                if isinstance(from_time, str) and ":" in from_time:
                    hour, minute = from_time.split(":")[:2]
                    time_text = f"{hour}:{minute} "
            
            # Termin-Label mit Hintergrundfarbe
            appt_label = ttk.Label(
                container, 
                text=f"{time_text}{appt['title'][:15]}{'...' if len(appt['title']) > 15 else ''}", 
                background=appt['color'],
                foreground=COLORS["bg_dark"],
                font=("Arial", 7),
                anchor="w",
                padding=(3, 0)
            )
            appt_label.pack(fill="x", padx=1, pady=1)
            
            # Name für spätere Identifikation
            appt_label.winfo_name = lambda: 'appointment'
            
            # Klick-Event für Termindetails
            appt_label.bind("<Button-1>", lambda e, a=appt: self.show_appointment_details(a))
    
    def show_appointments_for_day(self):
        """Zeigt die Termine für den ausgewählten Tag an"""
        # Datum aktualisieren
        self.selected_date_label.config(text=self.selected_date.strftime("%d.%m.%Y"))
        
        # Container leeren
        for widget in self.appointment_list_container.winfo_children():
            widget.destroy()
        
        # Tag aus dem ausgewählten Datum extrahieren
        day = self.selected_date.day
        
        # Prüfen, ob der Tag im aktuellen Monat liegt
        if day not in self.day_buttons:
            # Keine Termine anzeigen
            self.no_appointments_label = ttk.Label(
                self.appointment_list_container, 
                text="Keine Termine für diesen Tag", 
                style="CardText.TLabel"
            )
            self.no_appointments_label.pack(fill="both", expand=True)
            return
        
        # Termine für den Tag abrufen
        appointments = self.day_buttons[day]['appointments']
        
        if not appointments:
            # Keine Termine
            self.no_appointments_label = ttk.Label(
                self.appointment_list_container, 
                text="Keine Termine für diesen Tag", 
                style="CardText.TLabel"
            )
            self.no_appointments_label.pack(fill="both", expand=True)
            return
        
        # Termine anzeigen
        for appt in appointments:
            # Termin-Frame
            appt_frame = ttk.Frame(self.appointment_list_container, style="Card.TFrame")
            appt_frame.pack(fill="x", padx=5, pady=3)
            
            # Zeitanzeige formatieren
            time_str = ""
            if appt['time_from']:
                from_time = appt['time_from']
                if isinstance(from_time, str) and ":" in from_time:
                    hour, minute = from_time.split(":")[:2]
                    time_str += f"{hour}:{minute}"
            
            if appt['time_to']:
                to_time = appt['time_to']
                if isinstance(to_time, str) and ":" in to_time:
                    hour, minute = to_time.split(":")[:2]
                    time_str += f" - {hour}:{minute}"
            
            # Zeitleiste mit Farbe
            color_bar = tk.Frame(appt_frame, width=5, 
                               background=appt['color'])
            color_bar.pack(side="left", fill="y")
            
            # Termin-Daten
            content_frame = ttk.Frame(appt_frame, style="Card.TFrame", padding=(5, 5))
            content_frame.pack(side="left", fill="both", expand=True)
            
            # Titel und Zeit
            header_frame = ttk.Frame(content_frame, style="Card.TFrame")
            header_frame.pack(fill="x")
            
            title_label = ttk.Label(header_frame, text=appt['title'], 
                                  font=("Arial", 10, "bold"),
                                  foreground=COLORS["text_light"])
            title_label.pack(side="left")
            
            if time_str:
                time_label = ttk.Label(header_frame, text=time_str, 
                                     font=("Arial", 9),
                                     foreground=COLORS["text_dark"])
                time_label.pack(side="right")
            
            # Status anzeigen
            status_label = ttk.Label(content_frame, text=appt['status'], 
                                   font=("Arial", 8),
                                   foreground=COLORS["text_dark"])
            status_label.pack(anchor="w")
            
            # Kundename anzeigen, falls vorhanden
            if appt['customer_id']:
                customer_name = self.get_customer_name(appt['customer_id'])
                customer_label = ttk.Label(content_frame, text=f"Kunde: {customer_name}", 
                                        font=("Arial", 8),
                                        foreground=COLORS["text_dark"])
                customer_label.pack(anchor="w")
            
            # Buttons für Aktionen
            btn_frame = ttk.Frame(content_frame, style="Card.TFrame")
            btn_frame.pack(fill="x", pady=(5, 0))
            
            # Einfache Button-Klasse
            class SmallButton(tk.Button):
                def __init__(self, parent, text, command, **kwargs):
                    super().__init__(
                        parent, text=text, command=command,
                        bg=COLORS["bg_light"], fg=COLORS["text_light"],
                        activebackground=COLORS["accent"], 
                        activeforeground=COLORS["bg_dark"],
                        relief="flat", borderwidth=0,
                        padx=5, pady=2,
                        font=("Arial", 8),
                        cursor="hand2",
                        **kwargs
                    )
            
            # Bearbeiten-Button
            edit_btn = SmallButton(btn_frame, text="Bearbeiten", 
                                  command=lambda a=appt: self.edit_appointment(a))
            edit_btn.pack(side="left", padx=(0, 3))
            
            # Löschen-Button
            delete_btn = SmallButton(btn_frame, text="Löschen", 
                                    command=lambda a=appt: self.delete_appointment(a))
            delete_btn.pack(side="left")
            
            # Klick-Event für Detailansicht
            for widget in (appt_frame, content_frame, title_label, status_label):
                widget.bind("<Button-1>", lambda e, a=appt: self.show_appointment_details(a))
    
    def get_customer_name(self, customer_id):
        """Gibt den Namen eines Kunden anhand seiner ID zurück"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT vorname || ' ' || nachname FROM kunden WHERE id = ?", 
            (customer_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else "Unbekannt"
    
    def show_appointment_details(self, appointment):
        """Zeigt Details zu einem Termin an"""
        # Platzhalter - hier würde eine detaillierte Ansicht implementiert
        messagebox.showinfo(
            "Termindetails", 
            f"Titel: {appointment['title']}\n"
            f"Zeit: {appointment['time_from']} - {appointment['time_to']}\n"
            f"Status: {appointment['status']}\n"
            f"Beschreibung: {appointment['description'] or 'Keine Beschreibung'}"
        )
    
    def new_appointment(self):
        """Erstellt einen neuen Termin"""
        # Terminbearbeitungsdialog öffnen
        AppointmentDialog(self.dialog, "Neuer Termin", self.conn, self.selected_date, 
                          on_save=self.refresh_calendar)
    
    def edit_appointment(self, appointment):
        """Bearbeitet einen bestehenden Termin"""
        # Terminbearbeitungsdialog öffnen
        AppointmentDialog(self.dialog, "Termin bearbeiten", self.conn, self.selected_date, 
                          appointment_id=appointment['id'], on_save=self.refresh_calendar)
    
    def delete_appointment(self, appointment):
        """Löscht einen Termin"""
        if messagebox.askyesno("Löschen bestätigen", 
                              f"Möchten Sie den Termin '{appointment['title']}' wirklich löschen?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM termine WHERE id = ?", (appointment['id'],))
                self.conn.commit()
                
                # Kalender aktualisieren
                self.refresh_calendar()
                
                messagebox.showinfo("Erfolg", "Termin wurde gelöscht")
            except sqlite3.Error as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen des Termins: {e}")
    
    def refresh_calendar(self):
        """Aktualisiert den Kalender"""
        # Termine neu laden
        self.fill_calendar()
        self.load_appointments()


class AppointmentDialog:
    """Dialog zur Bearbeitung von Terminen"""
    def __init__(self, parent, title, conn, date, appointment_id=None, on_save=None):
        self.parent = parent
        self.conn = conn
        self.date = date
        self.appointment_id = appointment_id
        self.on_save = on_save
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Dunkler Hintergrund für das Dialog-Fenster
        self.dialog.configure(bg=COLORS["bg_dark"])
        
        # Hauptframe
        self.main_frame = ttk.Frame(self.dialog, style="Card.TFrame", padding=20)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, text=title, 
                style="CardTitle.TLabel", font=("Arial", 16, "bold")).pack(side="left")
        
        # Formularbereich
        form_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        form_frame.pack(fill="both", expand=True)
        
        # Titel
        ttk.Label(form_frame, text="Titel:", 
                style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=40).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )
        
        # Datum
        ttk.Label(form_frame, text="Datum:", 
                style="CardText.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar(value=date.strftime("%d.%m.%Y"))
        ttk.Entry(form_frame, textvariable=self.date_var, width=15).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )
        
        # Uhrzeit von/bis
        ttk.Label(form_frame, text="Von:", 
                style="CardText.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.time_from_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.time_from_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )
        
        ttk.Label(form_frame, text="Bis:", 
                style="CardText.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.time_to_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.time_to_var, width=10).grid(
            row=3, column=1, sticky="w", padx=5, pady=5
        )
        
        # Hinweis zur Zeitformatierung
        ttk.Label(form_frame, text="Format: HH:MM", 
                foreground=COLORS["text_dark"], font=("Arial", 8)).grid(
            row=2, column=1, sticky="e", padx=5
        )
        
        # Status
        ttk.Label(form_frame, text="Status:", 
                style="CardText.TLabel").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Geplant")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, width=15,
                                   values=["Geplant", "Bestätigt", "In Bearbeitung", "Abgeschlossen", "Storniert"])
        status_combo.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Farbe
        ttk.Label(form_frame, text="Farbe:", 
                style="CardText.TLabel").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.color_var = tk.StringVar(value=COLORS["accent"])
        
        # Farbauswahl-Container
        color_frame = ttk.Frame(form_frame, style="Card.TFrame")
        color_frame.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Farboptionen
        colors = [
            COLORS["accent"], COLORS["success"], COLORS["warning"], 
            COLORS["danger"], "#9966CC", "#3399FF"
        ]
        
        self.color_buttons = []
        for i, color in enumerate(colors):
            color_btn = tk.Frame(color_frame, width=20, height=20, bg=color, 
                               bd=2, relief="flat")
            color_btn.grid(row=0, column=i, padx=2)
            
            color_btn.bind("<Button-1>", lambda e, c=color: self.select_color(c))
            self.color_buttons.append((color_btn, color))
        
        # Kunde
        ttk.Label(form_frame, text="Kunde:", 
                style="CardText.TLabel").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        
        # Kunden laden
        self.customers = self.load_customers()
        customer_values = ["Keiner"] + [f"{id}: {name}" for id, name in self.customers]
        
        self.customer_var = tk.StringVar(value="Keiner")
        customer_combo = ttk.Combobox(form_frame, textvariable=self.customer_var, width=30,
                                    values=customer_values)
        customer_combo.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        # Auftrag
        ttk.Label(form_frame, text="Auftrag:", 
                style="CardText.TLabel").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        
        # Aufträge laden
        self.orders = self.load_orders()
        order_values = ["Keiner"] + [f"{id}: {desc}" for id, desc in self.orders]
        
        self.order_var = tk.StringVar(value="Keiner")
        order_combo = ttk.Combobox(form_frame, textvariable=self.order_var, width=30,
                                 values=order_values)
        order_combo.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        
        # Beschreibung
        ttk.Label(form_frame, text="Beschreibung:", 
                style="CardText.TLabel").grid(row=8, column=0, sticky="nw", padx=5, pady=5)
        self.description_text = tk.Text(form_frame, height=6, width=40, 
                                     bg=COLORS["bg_light"], fg=COLORS["text_light"])
        self.description_text.grid(row=8, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        # Einfache Button-Klasse
        class DialogButton(tk.Button):
            def __init__(self, parent, text, command, primary=False, **kwargs):
                bg_color = COLORS["accent"] if primary else COLORS["bg_light"]
                fg_color = COLORS["bg_dark"] if primary else COLORS["text_light"]
                super().__init__(
                    parent, text=text, command=command,
                    bg=bg_color, fg=fg_color,
                    activebackground=COLORS["text_light"], 
                    activeforeground=COLORS["bg_dark"],
                    relief="flat", borderwidth=0,
                    padx=15, pady=8,
                    font=("Arial", 10),
                    cursor="hand2",
                    **kwargs
                )
        
        save_btn = DialogButton(btn_frame, text="Speichern", 
                              command=self.save_appointment, primary=True)
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = DialogButton(btn_frame, text="Abbrechen", 
                                command=self.dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        # Termin laden, falls vorhanden
        if self.appointment_id:
            self.load_appointment()
        
        # Dialog zentrieren
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_customers(self):
        """Lädt die Kundenliste"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, vorname || ' ' || nachname as name
        FROM kunden
        ORDER BY name
        """)
        return cursor.fetchall()
    
    def load_orders(self):
        """Lädt die Auftragsliste"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, beschreibung
        FROM auftraege
        WHERE status != 'Abgeschlossen'
        ORDER BY id DESC
        """)
        return cursor.fetchall()
    
    def load_appointment(self):
        """Lädt die Daten eines bestehenden Termins"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT titel, datum, uhrzeit_von, uhrzeit_bis, kunde_id, auftrag_id, 
               status, farbe, beschreibung
        FROM termine
        WHERE id = ?
        """, (self.appointment_id,))
        
        appointment = cursor.fetchone()
        if appointment:
            titel, datum, von, bis, kunde_id, auftrag_id, status, farbe, beschreibung = appointment
            
            # Daten in die Formularfelder übertragen
            self.title_var.set(titel)
            
            # Datum formatieren
            try:
                date_obj = datetime.strptime(datum, '%Y-%m-%d')
                self.date_var.set(date_obj.strftime('%d.%m.%Y'))
            except:
                self.date_var.set(self.date.strftime('%d.%m.%Y'))
            
            # Zeiten formatieren
            if von:
                self.time_from_var.set(von)
            if bis:
                self.time_to_var.set(bis)
                
            # Status setzen
            self.status_var.set(status)
            
            # Farbe auswählen
            self.select_color(farbe or COLORS["accent"])
            
            # Kunde auswählen
            if kunde_id:
                for i, (cid, name) in enumerate(self.customers):
                    if cid == kunde_id:
                        self.customer_var.set(f"{cid}: {name}")
                        break
            
            # Auftrag auswählen
            if auftrag_id:
                for i, (oid, desc) in enumerate(self.orders):
                    if oid == auftrag_id:
                        self.order_var.set(f"{oid}: {desc}")
                        break
            
            # Beschreibung setzen
            if beschreibung:
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert('1.0', beschreibung)
    
    def select_color(self, color):
        """Wählt eine Farbe aus"""
        self.color_var.set(color)
        
        # Visuelle Rückmeldung - Ausgewählte Farbe hervorheben
        for btn, clr in self.color_buttons:
            if clr == color:
                btn.config(relief="raised", bd=3)
            else:
                btn.config(relief="flat", bd=2)
    
    def save_appointment(self):
        """Speichert den Termin"""
        # Daten validieren
        if not self.title_var.get():
            messagebox.showerror("Fehler", "Bitte geben Sie einen Titel ein.")
            return
        
        try:
            # Datum validieren und konvertieren
            datum_parts = self.date_var.get().split('.')
            if len(datum_parts) != 3:
                raise ValueError("Ungültiges Datumsformat")
                
            day, month, year = map(int, datum_parts)
            datum_str = f"{year:04d}-{month:02d}-{day:02d}"
            
            # Zeiten validieren
            von_str = self.time_from_var.get()
            bis_str = self.time_to_var.get()
            
            if von_str and ":" not in von_str:
                raise ValueError("Ungültiges Zeitformat für 'Von'")
            if bis_str and ":" not in bis_str:
                raise ValueError("Ungültiges Zeitformat für 'Bis'")
                
            # Kunde-ID extrahieren
            kunde_id = None
            kunde_str = self.customer_var.get()
            if kunde_str and kunde_str != "Keiner" and ":" in kunde_str:
                kunde_id = int(kunde_str.split(":")[0])
                
            # Auftrags-ID extrahieren
            auftrag_id = None
            auftrag_str = self.order_var.get()
            if auftrag_str and auftrag_str != "Keiner" and ":" in auftrag_str:
                auftrag_id = int(auftrag_str.split(":")[0])
            
            # Beschreibung
            beschreibung = self.description_text.get('1.0', tk.END).strip()
            
            cursor = self.conn.cursor()
            
            if self.appointment_id:
                # Bestehenden Termin aktualisieren
                cursor.execute("""
                UPDATE termine SET 
                    titel = ?, datum = ?, uhrzeit_von = ?, uhrzeit_bis = ?,
                    kunde_id = ?, auftrag_id = ?, status = ?, farbe = ?, beschreibung = ?
                WHERE id = ?
                """, (
                    self.title_var.get(), datum_str, von_str, bis_str, 
                    kunde_id, auftrag_id, self.status_var.get(), 
                    self.color_var.get(), beschreibung, self.appointment_id
                ))
            else:
                # Neuen Termin erstellen
                cursor.execute("""
                INSERT INTO termine 
                    (titel, datum, uhrzeit_von, uhrzeit_bis, kunde_id, auftrag_id, 
                     status, farbe, beschreibung)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.title_var.get(), datum_str, von_str, bis_str, 
                    kunde_id, auftrag_id, self.status_var.get(), 
                    self.color_var.get(), beschreibung
                ))
                
            self.conn.commit()
            
            # Kalender aktualisieren
            if self.on_save:
                self.on_save()
                
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Fehler", f"Eingabefehler: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Speichern: {e}")
            self.conn.rollback()