#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoMeister by Gianni - Werkstattverwaltung
Hauptdatei zum Starten der Anwendung
"""

import tkinter as tk
from tkinter import ttk

from gui.main_window import AutowerkstattApp

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    root = tk.Tk()
    root.title("AutoMeister by Gianni - Werkstattverwaltung")
    
    # Style konfigurieren
    style = ttk.Style()
    style.theme_use('clam')  # Oder 'alt', 'default', 'classic' je nach Plattform
    
    # Anwendung starten
    app = AutowerkstattApp(root)
    
    # Fenster maximieren
    root.state('zoomed')
    
    # Event-Loop starten
    root.mainloop()

if __name__ == "__main__":
    main()