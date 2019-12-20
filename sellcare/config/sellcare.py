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
                   }
            ]
        }
]
