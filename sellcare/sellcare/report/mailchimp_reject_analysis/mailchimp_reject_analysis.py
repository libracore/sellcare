# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import re

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data
    
def get_columns():
    return [
        {"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Error Log", "width": 100},
        {"label": _("Message"), "fieldname": "message", "fieldtype": "Data", "width": 800}
    ]
    
def get_data(filters):   
    sql_query = """SELECT 
        `error`,
        `name`
	FROM 
      `tabError Log`
	WHERE DATE(`creation`) = '{date}'
	   AND `error` LIKE '%MailChimp%';
      """.format(date=filters.date)

    errors = frappe.db.sql(sql_query, as_dict=True)
    output = []
    for error in errors:
        m = re.search("""("detail":)("(.+?)")""", error['error'])
        if m:
            output.append({
                'message': m.group(2).replace("\"", ""),
                'name': error['name']
            })
      
    return output
