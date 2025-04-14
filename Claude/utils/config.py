"""
Schnyders Werkstattverwaltung - Konfigurationshilfen
===================================================
Dieses Modul enthält Hilfsfunktionen für die Konfiguration der Anwendung.
"""

def get_config_value(conn, key, default=None):
    """Konfigurationswert aus der Datenbank auslesen"""
    cursor = conn.cursor()
    cursor.execute("SELECT wert FROM konfiguration WHERE schluessel = ?", (key,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return default

def set_config_value(conn, key, value, description=None):
    """Konfigurationswert in der Datenbank setzen"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM konfiguration WHERE schluessel = ?", (key,))
    if cursor.fetchone():
        cursor.execute("UPDATE konfiguration SET wert = ? WHERE schluessel = ?", (value, key))
    else:
        cursor.execute("INSERT INTO konfiguration (schluessel, wert, beschreibung) VALUES (?, ?, ?)", 
                      (key, value, description or key))
    conn.commit()

def init_default_config(conn):
    """Initialisiert Standardkonfigurationswerte, falls nicht vorhanden"""
    print("Initialisiere Standardkonfiguration...")
    
    # Prüfen, ob die Tabelle konfiguration existiert
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='konfiguration'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE konfiguration (
            schluessel TEXT PRIMARY KEY,
            wert TEXT NOT NULL,
            beschreibung TEXT
        )
        ''')
        conn.commit()
    
    defaults = {
        'standard_stundenlohn': ('50.0', 'Standard-Stundenlohn in CHF'),
        'firmenname': ('Schnyders Werkstatt', 'Name der Firma'),
        'adresse': ('Musterstraße 123, 8000 Zürich', 'Adresse der Firma'),
        'telefon': ('044 123 45 67', 'Telefonnummer'),
        'email': ('info@schnyders-werkstatt.ch', 'E-Mail-Adresse'),
        'website': ('www.schnyders-werkstatt.ch', 'Website der Firma'),
        'mwst_satz': ('7.7', 'MwSt-Satz in %'),
        'bank_name': ('Schweizer Kantonalbank', 'Name der Bank'),
        'bank_iban': ('CH93 0076 2011 6238 5295 7', 'IBAN-Nummer'),
        'bank_bic': ('POFICHBEXXX', 'BIC/SWIFT-Code'),
        'zahlungsfrist': ('30', 'Zahlungsfrist in Tagen'),
        'standard_rabatt': ('0', 'Standard-Rabatt in %')
    }
    
    for key, (value, description) in defaults.items():
        if get_config_value(conn, key) is None:
            set_config_value(conn, key, value, description)
    
    print("Standardkonfiguration initialisiert.")

def get_default_stundenlohn(conn):
    """Standard-Stundenlohn aus der Konfiguration auslesen"""
    stundenlohn = get_config_value(conn, 'standard_stundenlohn', '50.0')
    try:
        return float(stundenlohn)
    except (ValueError, TypeError):
        return 50.0  # Fallback-Wert, falls keine valide Konfiguration vorhanden

def set_default_stundenlohn(conn, stundenlohn):
    """Standard-Stundenlohn in der Konfiguration setzen"""
    set_config_value(conn, 'standard_stundenlohn', str(stundenlohn), 
                    'Standard-Stundenlohn in CHF')

def get_company_info(conn):
    """Firmendaten aus der Konfiguration auslesen"""
    return {
        'name': get_config_value(conn, 'firmenname', 'Schnyders Werkstatt'),
        'address': get_config_value(conn, 'adresse', 'Musterstraße 123, 8000 Zürich'),
        'phone': get_config_value(conn, 'telefon', '044 123 45 67'),
        'email': get_config_value(conn, 'email', 'info@schnyders-werkstatt.ch'),
        'website': get_config_value(conn, 'website', 'www.schnyders-werkstatt.ch'),
        'mwst': get_config_value(conn, 'mwst_satz', '7.7'),
        'bank_name': get_config_value(conn, 'bank_name', 'Schweizer Kantonalbank'),
        'bank_iban': get_config_value(conn, 'bank_iban', 'CH93 0076 2011 6238 5295 7'),
        'bank_bic': get_config_value(conn, 'bank_bic', 'POFICHBEXXX'),
        'zahlungsfrist': get_config_value(conn, 'zahlungsfrist', '30'),
        'standard_rabatt': get_config_value(conn, 'standard_rabatt', '0')
    }

def set_company_info(conn, info):
    """Firmendaten in der Konfiguration setzen"""
    for key, value in info.items():
        if key == 'name':
            set_config_value(conn, 'firmenname', value, 'Name der Firma')
        elif key == 'address':
            set_config_value(conn, 'adresse', value, 'Adresse der Firma')
        elif key == 'phone':
            set_config_value(conn, 'telefon', value, 'Telefonnummer')
        elif key == 'email':
            set_config_value(conn, 'email', value, 'E-Mail-Adresse')
        elif key == 'website':
            set_config_value(conn, 'website', value, 'Website der Firma')
        elif key == 'mwst':
            set_config_value(conn, 'mwst_satz', value, 'MwSt-Satz in %')
        elif key == 'bank_name':
            set_config_value(conn, 'bank_name', value, 'Name der Bank')
        elif key == 'bank_iban':
            set_config_value(conn, 'bank_iban', value, 'IBAN-Nummer')
        elif key == 'bank_bic':
            set_config_value(conn, 'bank_bic', value, 'BIC/SWIFT-Code')
        elif key == 'zahlungsfrist':
            set_config_value(conn, 'zahlungsfrist', value, 'Zahlungsfrist in Tagen')
        elif key == 'standard_rabatt':
            set_config_value(conn, 'standard_rabatt', value, 'Standard-Rabatt in %')

