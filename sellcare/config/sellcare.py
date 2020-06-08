from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Kunden Auftragsdokumente"),
            "icon": "octicon octicon-organization",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")
                   },
                   {
                       "type": "doctype",
                       "name": "Quotation",
                       "label": _("Quotation"),
                       "description": _("Quotation")
                   },
                   {
                        "type": "report",
                        "name": "Angebotene Preise pro Kunde",
                        "label": _("Offerte & Preis"),
                        "doctype": "Quotation",
                        "is_query_report": False
                   },
                   {
                        "type": "report",
                        "name": "Preise pro Artikel",
                        "label": "Angebotene Preise pro Artikel",
                        "doctype": "Quotation",
                        "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Order",
                       "label": _("Kunden-AB Übersicht"),
                       "description": _("Kunden-AB Übersicht")
                   },
                   {
                        "type": "report",
                        "name": "Timetable AB (SQL)",
                        "label": _("Timetable AB"),
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Delivery Note",
                       "label": _("Kunden-LS Übersicht"),
                       "description": _("Kunden-LS Übersicht")
                   },
                   {
                        "type": "report",
                        "name": "Timetable LS (SQL)",
                        "label": _("Timetable LS"),
                        "doctype": "Delivery Note",
                        "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Invoice",
                       "label": _("Kunden-RG Übersicht"),
                       "description": _("Kunden-RG Übersicht")
                   },
                   {
                       "type": "doctype",
                       "name": "Blanket Order",
                       "label": _("Rahmenauftrag"),
                       "description": _("Rahmenauftrag")
                   },
                   {
                       "type": "doctype",
                       "name": "Journal Entry",
                       "label": _("Jahresrückvergütung & Gutschrift"),
                       "description": _("Jahresrückvergütung & Gutschrift")
                   },
                   {
                        "type": "report",
                        "name": "Mahnung",
                        "label": _("Mahnung"),
                        "doctype": "Payment Reminder",
                        "is_query_report": False
                   }
            ]
        },
        {
            "label": _("Beschaffung & Lager"),
            "icon": "octicon octicon-organization",
            "items": [
                   {
                        "type": "doctype",
                        "name": "Item",
                        "label": _("Item"),
                        "description": _("Item")
                   },
                   {
                        "type": "doctype",
                        "name": "Supplier",
                        "label": _("Supplier"),
                        "description": _("Supplier")
                   },
                   {
                        "type": "report",
                        "name": "Lieferantenbestellung (SQL)",
                        "label": "Lieferanten-AB", 
                        "doctype": "Purchase Order",
                        "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Invoice",
                       "label": _("Lieferanten-RG"),
                       "description": _("Lieferanten-RG")
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Receipt",
                       "label": _("Wareneingang"),
                       "description": _("Wareneingang")
                   },
                   {
                        "type": "report",
                        "name": "Order Planning",
                        "doctype": "Item",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Batch report",
                        "label": _("Chargenübersicht"),
                        "doctype": "Batch",
                        "is_query_report": True
                   }
            ]
        },
        {
            "label": _("CRM"),
            "icon": "octicon octicon-organization",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Contact",
                       "label": _("Kontaktperson"),
                       "description": _("Kontaktperson")
                   },
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")
                   },
                    {
                       "type": "report",
                       "name": "MailChimp Reject Analysis",
                       "label": _("Mailchimp Fehlermeldungen"),
                       "doctype": "Error Log",
                       "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Customer Visit Report",
                       "label": _("Übersicht Besuchsberichte"),
                       "description": _("Übersicht Besuchsberichte")
                   },
                   {
                       "type": "doctype",
                       "name": "Customer Item Text",
                       "label": _("Customer Item Text"),
                       "description": _("Customer Item Text")
                   }
            ]
        },
        {
            "label": _("Statistics"),
            "icon": "octicon octicon-organization",
            "items": [
                   {
                        "type": "report",
                        "name": "Dispo-Report",
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Auswertung DB1",
                        "doctype": "Sales Invoice",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "DB1 Kundengruppiert",
                        "doctype": "Sales Invoice",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Sales Outlook",
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Monatlicher Einkaufsumsatz",
                        "doctype": "Purchase Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Vorgangsliste",
                        "doctype": "Sales Invoice",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Musterliste",
                        "doctype": "Delivery Note",
                        "is_query_report": True
                   }
            ]
        }        
]
