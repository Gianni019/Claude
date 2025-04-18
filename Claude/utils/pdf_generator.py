#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF-Generator für die Autowerkstatt-Anwendung mit direkter Logo-Einbettung
"""

import os
import base64
import tempfile
from datetime import datetime
from io import BytesIO

# ReportLab-Import
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm      
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from utils.config import get_company_info

def generate_invoice_pdf(conn, rechnung_id, output_path=None):
    """Erzeugt eine PDF-Datei für die Rechnung"""
    try:
        cursor = conn.cursor()
        
        # Rechnungsdaten abrufen
        cursor.execute("""
        SELECT r.rechnungsnummer, strftime('%d.%m.%Y', r.datum) as datum,
               r.gesamtbetrag, r.rabatt_prozent, r.notizen, r.auftrag_id
        FROM rechnungen r
        WHERE r.id = ?
        """, (rechnung_id,))
        
        rechnung = cursor.fetchone()
        if not rechnung:
            return False, "Rechnung nicht gefunden"
        
        rechnungsnr, datum, gesamtbetrag, rabatt_prozent, notizen, auftrag_id = rechnung
        
        if rabatt_prozent is None:
            rabatt_prozent = 0
        
        # Kundendaten abrufen
        cursor.execute("""
        SELECT k.id, k.vorname || ' ' || k.nachname as kunde, k.anschrift, k.telefon, k.email
        FROM kunden k
        JOIN auftraege a ON k.id = a.kunden_id
        WHERE a.id = ?
        """, (auftrag_id,))
        
        kunde = cursor.fetchone()
        if not kunde:
            return False, "Kundendaten nicht gefunden"
            
        kunden_id, kundenname, anschrift, telefon, email = kunde
        
        # Fahrzeugdaten abrufen (bevorzugt vom in Auftrag gespeicherten Fahrzeug)
        cursor.execute("""
        SELECT f.fahrzeug_typ, f.kennzeichen, f.fahrgestellnummer
        FROM auftraege a
        LEFT JOIN fahrzeuge f ON a.fahrzeug_id = f.id
        WHERE a.id = ?
        """, (auftrag_id,))
        
        fahrzeug_data = cursor.fetchone()
        
        # Wenn kein Fahrzeug im Auftrag gespeichert ist, versuche erstes Fahrzeug des Kunden
        if not fahrzeug_data or (not fahrzeug_data[0] and not fahrzeug_data[1] and not fahrzeug_data[2]):
            cursor.execute("""
            SELECT f.fahrzeug_typ, f.kennzeichen, f.fahrgestellnummer
            FROM fahrzeuge f
            JOIN auftraege a ON f.kunden_id = a.kunden_id
            WHERE a.id = ?
            ORDER BY f.id
            LIMIT 1
            """, (auftrag_id,))
            fahrzeug_data = cursor.fetchone()
        
        fahrzeug_info = ""
        if fahrzeug_data:
            fahrzeug_typ, kennzeichen, fahrgestellnr = fahrzeug_data
            if fahrzeug_typ:
                fahrzeug_info += f"Fahrzeug: {fahrzeug_typ}\n"
            if kennzeichen:
                fahrzeug_info += f"Kennzeichen: {kennzeichen}\n"
            if fahrgestellnr:
                fahrzeug_info += f"Fahrgestellnr.: {fahrgestellnr}\n"
        
        # Auftragsdaten abrufen
        cursor.execute("""
        SELECT beschreibung, arbeitszeit
        FROM auftraege
        WHERE id = ?
        """, (auftrag_id,))
        
        auftrag_data = cursor.fetchone()
        if not auftrag_data:
            return False, "Auftragsdaten nicht gefunden"
            
        auftrag_beschreibung, arbeitszeit = auftrag_data
        
        # Positionen abrufen (Ersatzteile mit Rabatt)
        cursor.execute("""
        SELECT e.bezeichnung, ae.menge, ae.einzelpreis, COALESCE(ae.rabatt, 0) as rabatt
        FROM auftrag_ersatzteile ae
        JOIN ersatzteile e ON ae.ersatzteil_id = e.id
        WHERE ae.auftrag_id = ?
        """, (auftrag_id,))
        
        ersatzteile = cursor.fetchall()
        
        # Firmendaten abrufen
        company_info = get_company_info(conn)
        
        # Firmenlogo abrufen
        logo_data = None
        cursor.execute("SELECT wert FROM konfiguration WHERE schluessel = 'firmenlogo'")
        logo_row = cursor.fetchone()
        if logo_row and logo_row[0]:
            logo_data = logo_row[0]
        
        # Stundensatz abrufen
        stundensatz = 50.0  # Standardwert
        cursor.execute("SELECT wert FROM konfiguration WHERE schluessel = 'standard_stundenlohn'")
        stundensatz_row = cursor.fetchone()
        if stundensatz_row:
            try:
                stundensatz = float(stundensatz_row[0])
            except:
                pass
        
        # MwSt-Satz abrufen
        mwst_satz = 7.7  # Standardwert für Schweiz
        if 'mwst' in company_info:
            try:
                mwst_satz = float(company_info['mwst'])
            except:
                pass
        
        # Temporäre Datei erstellen, wenn kein Ausgabepfad angegeben wurde
        if not output_path:
            handle, output_path = tempfile.mkstemp(suffix='.pdf')
            os.close(handle)
        
        # PDF erstellen
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Stile definieren
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            alignment=TA_RIGHT
        ))
        styles.add(ParagraphStyle(
            name='CenterAlign',
            parent=styles['Normal'],
            alignment=TA_CENTER
        ))
        styles.add(ParagraphStyle(
            name='LeftAlign',
            parent=styles['Normal'],
            alignment=TA_LEFT
        ))
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=14,
            fontName='Helvetica-Bold'
        ))
        
        # Inhalte für das PDF
        elements = []
        
        # Logo und Firmeninformationen
        header_data = [[]]
        
        # Firmeninformationen mit größerem Firmennamen
        if logo_data:
            # Anstelle eines Logos nur den Firmennamen größer darstellen
            header_data[0].append(Paragraph(f"<b>{company_info['name']}</b>", styles['CompanyName']))
        else:
            header_data[0].append(Paragraph(f"<b>{company_info['name']}</b>", styles['CompanyName']))
            
        company_text = f"""
        {company_info['address']}
        Tel: {company_info['phone']}
        E-Mail: {company_info['email']}
        {company_info.get('website', '')}
        """
        header_data[0].append(Paragraph(company_text, styles['Normal']))
        
        # Rechts: Rechnung-Text und Datum
        rechnung_title = f"""
        <font size="14"><b>RECHNUNG</b></font>
        <br/><br/>
        Rechnungsnummer: {rechnungsnr}
        <br/>
        Datum: {datum}
        """
        header_data[0].append(Paragraph(rechnung_title, styles['RightAlign']))
        
        # Header-Tabelle erstellen
        header_table = Table(header_data, colWidths=[4*cm, 9*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Kundeninformationen
        elements.append(Paragraph("<b>Kundeninformationen:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.2*cm))
        kunde_text = f"{kundenname}"
        if anschrift:
            kunde_text += f"<br/>{anschrift}"
        if telefon:
            kunde_text += f"<br/>Tel: {telefon}"
        if email:
            kunde_text += f"<br/>E-Mail: {email}"
        elements.append(Paragraph(kunde_text, styles['Normal']))
        
        # Fahrzeuginformationen
        if fahrzeug_info:
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("<b>Fahrzeuginformationen:</b>", styles['Normal']))
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Paragraph(fahrzeug_info, styles['Normal']))
        
        # Auftragsbeschreibung
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("<b>Auftragsbeschreibung:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(auftrag_beschreibung, styles['Normal']))
        
        # Trennlinie
        elements.append(Spacer(1, 0.5*cm))
        
        # Positionen
        elements.append(Paragraph("<b>Positionen:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # Tabellenkopf für Positionen mit Rabatt-Spalte
        positionen_data = [
            ['Pos', 'Bezeichnung', 'Menge', 'Einzelpreis', 'Rabatt', 'Gesamtpreis']
        ]
        
        # Gesamtsumme
        zwischensumme = 0
        pos = 1
        
        # Ersatzteile hinzufügen
        for bezeichnung, menge, einzelpreis, rabatt in ersatzteile:
            # Gesamtpreis mit Rabatt berechnen
            rabatt_betrag = menge * einzelpreis * (rabatt / 100)
            gesamtpreis = (menge * einzelpreis) - rabatt_betrag
            zwischensumme += gesamtpreis
            
            # Formatierte Rabattanzeige
            rabatt_anzeige = f"{rabatt:.2f} %" if rabatt > 0 else "-"
            
            positionen_data.append([
                str(pos),
                bezeichnung,
                str(menge),
                f"{einzelpreis:.2f} CHF",
                rabatt_anzeige,  # Rabatt anzeigen
                f"{gesamtpreis:.2f} CHF"
            ])
            pos += 1
        
        # Arbeitszeit hinzufügen, wenn vorhanden
        if arbeitszeit > 0:
            arbeitskosten = arbeitszeit * stundensatz
            # Kein Rabatt für Arbeitszeit (oder anpassen, falls nötig)
            rabatt_arbeitszeit = 0
            arbeitskosten_nach_rabatt = arbeitszeit * stundensatz * (1 - rabatt_arbeitszeit/100)
            zwischensumme += arbeitskosten_nach_rabatt
            
            positionen_data.append([
                str(pos),
                f"Arbeitszeit: {auftrag_beschreibung}",
                f"{arbeitszeit:.2f} h",
                f"{stundensatz:.2f} CHF/h",
                "-",  # Kein Rabatt auf Arbeitszeit
                f"{arbeitskosten_nach_rabatt:.2f} CHF"
            ])
        
        # Rabatt berechnen und anwenden, wenn vorhanden
        rabatt_betrag = 0
        if rabatt_prozent > 0:
            rabatt_betrag = zwischensumme * rabatt_prozent / 100
            zwischensumme_nach_rabatt = zwischensumme - rabatt_betrag
        else:
            zwischensumme_nach_rabatt = zwischensumme
        
        # MwSt berechnen
        mwst = zwischensumme_nach_rabatt * mwst_satz / 100
        
        # Gesamtsumme
        endsumme = zwischensumme_nach_rabatt + mwst
        
        # Positions-Tabelle erstellen
        col_widths = [0.8*cm, 7*cm, 2*cm, 3*cm, 2*cm, 3*cm]  # Spaltenbreiten angepasst für Rabatt
        positionen_table = Table(positionen_data, colWidths=col_widths)
        positionen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (5, -1), 'RIGHT'),  # Rechtsbündige Ausrichtung für Preise und Rabatte
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(positionen_table)
        
        # Zusammenfassung (Zwischensumme, Rabatt, MwSt, Endsumme)
        elements.append(Spacer(1, 0.5*cm))
        summary_data = []
        
        # Zwischensumme
        summary_data.append(['', '', '', '', 'Zwischensumme:', f"{zwischensumme:.2f} CHF"])
        
        # Rabatt, wenn vorhanden
        if rabatt_prozent > 0:
            summary_data.append(['', '', '', '', f'Rabatt ({rabatt_prozent}%):', f"- {rabatt_betrag:.2f} CHF"])
            summary_data.append(['', '', '', '', 'Netto:', f"{zwischensumme_nach_rabatt:.2f} CHF"])
        
        # MwSt
        summary_data.append(['', '', '', '', f'MwSt ({mwst_satz}%):', f"{mwst:.2f} CHF"])
        
        # Gesamtbetrag
        summary_data.append(['', '', '', '', 'Gesamtbetrag:', f"{endsumme:.2f} CHF"])
        
        # Zusammenfassungs-Tabelle erstellen
        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
            ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (4, -1), (5, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        
        # Notizen/Hinweise
        if notizen:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph("<b>Hinweise:</b>", styles['Normal']))
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Paragraph(notizen, styles['Normal']))
        
        # Zahlungsinformationen
        elements.append(Spacer(1, 0.7*cm))
        elements.append(Paragraph("<b>Zahlungsinformationen:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.2*cm))
        
        zahlungsfrist = company_info.get('zahlungsfrist', '30')
        zahlungs_text = f"Bitte überweisen Sie den Betrag innerhalb von {zahlungsfrist} Tagen auf folgendes Konto:"
        elements.append(Paragraph(zahlungs_text, styles['Normal']))
        
        bank_info = f"""
        Bank: {company_info.get('bank_name', 'Schweizer Kantonalbank')}
        IBAN: {company_info.get('bank_iban', 'CH00 0000 0000 0000 0000 0')}
        BIC: {company_info.get('bank_bic', 'POFICHBEXXX')}
        Verwendungszweck: {rechnungsnr}
        """
        elements.append(Paragraph(bank_info, styles['Normal']))
        
        # Danke
        elements.append(Spacer(1, 0.7*cm))
        elements.append(Paragraph("Vielen Dank für Ihren Auftrag!", styles['Normal']))
        
        # PDF generieren
        doc.build(elements)
        
        return True, output_path
        
    except Exception as e:
        print(f"Fehler beim Erstellen der PDF: {e}")
        return False, str(e)