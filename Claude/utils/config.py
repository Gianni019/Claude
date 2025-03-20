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

def get_default_stundenlohn(conn):
    """Standard-Stundenlohn aus der Konfiguration auslesen"""
    stundenlohn = get_config_value(conn, 'standard_stundenlohn', '120.0')
    try:
        return float(stundenlohn)
    except (ValueError, TypeError):
        return 120.0  # Fallback-Wert, falls keine valide Konfiguration vorhanden

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
        'mwst': get_config_value(conn, 'mwst_satz', '7.7')
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
        elif key == 'mwst':
            set_config_value(conn, 'mwst_satz', value, 'MwSt-Satz in %')