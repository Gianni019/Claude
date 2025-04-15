#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoMeister by Gianni - Werkstattverwaltung
Hauptdatei zum Starten der modernisierten Anwendung
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Fügen Sie das aktuelle Verzeichnis dem Suchpfad hinzu, um Module zu finden
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from gui.main_window import ModernAutowerkstattApp

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    root = tk.Tk()
    root.title("AutoMeister - Moderne Werkstattverwaltung")
    
    # Bildschirmgröße ermitteln für optimale Fenstergröße
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Zentriertes Fenster mit 90% der Bildschirmgröße
    width = int(screen_width * 0.9)
    height = int(screen_height * 0.9)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Fenstergröße und -position setzen
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Anwendungs-Icon setzen (falls vorhanden)
    try:
        root.iconbitmap("icons/app_icon.ico")  # Windows
    except:
        try:
            logo = tk.PhotoImage(file="icons/app_icon.png")
            root.iconphoto(True, logo)  # Linux/Mac
        except:
            pass  # Icon nicht verfügbar, Standard-Symbol verwenden
    
    # Dark Mode für alle Plattformen aktivieren
    try:
        # Für Windows 10/11
        from ctypes import windll
        windll.dwmapi.DwmSetWindowAttribute(
            windll.user32.GetParent(root.winfo_id()), 
            20, 
            byref(c_int(2)), 
            sizeof(c_int))
    except:
        pass
    
    # Moderne Anwendung starten
    app = ModernAutowerkstattApp(root)
    
    # Event-Loop starten
    root.mainloop()

if __name__ == "__main__":
    main()