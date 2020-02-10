from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("CRM"),
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
                       "name": "Customer Visit Report",
                       "label": _("Customer Visit Report"),
                       "description": _("Customer Visit Report")
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
            "label": _("Procurement"),
            "icon": "octicon octicon-organization",
            "items": [
                   {
                        "type": "report",
                        "name": "Order Planning",
                        "doctype": "Item",
                        "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Purchase Order",
                       "label": _("Purchase Order"),
                       "description": _("Purchase Order")
                   },
                   {
                       "type": "doctype",
                       "name": "Sales Order",
                       "label": _("Sales Order"),
                       "description": _("Sales Order")
                   },
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
                        "name": "Sales Outlook",
                        "doctype": "Sales Order",
                        "is_query_report": True
                   },
                   {
                        "type": "report",
                        "name": "Vorgangsliste",
                        "doctype": "Sales Invoice",
                        "is_query_report": True
                   }
            ]
        }        
]
