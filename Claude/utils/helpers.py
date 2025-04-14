# utils/helpers.py


def get_selected_rechnung_id(app):
    """Gibt die ID der ausgewählten Rechnung zurück"""
    selected_items = app.rechnungen_widgets['rechnungen_tree'].selection()
    if not selected_items:
        return None
    return app.rechnungen_widgets['rechnungen_tree'].item(selected_items[0])['values'][0]

def get_selected_rechnung_id(app):
    """Gibt die ID der ausgewählten Rechnung zurück"""
    selected_items = app.rechnungen_widgets['rechnungen_tree'].selection()
    if not selected_items:
        return None
    return app.rechnungen_widgets['rechnungen_tree'].item(selected_items[0])['values'][0]