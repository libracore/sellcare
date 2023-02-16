# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data
    
def get_columns():
    return [
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 100},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 300},
        # {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        # {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        # {"label": _("Qty ordered"), "fieldname": "qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Liefermenge"), "fieldname": "qty_to_deliver", "fieldtype": "Data", "width": 100, "convertible": "qty"},
        {"label": _("Available Qty"), "fieldname": "available_qty", "fieldtype": "Data", "width": 100},
        {"label": "", "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    
def get_data(filters):
    if not filters.item_code:
        filters.item_code = "%"
    if not filters.item_name:
        filters.item_name = "%"
    else:
        filters.item_name = "%{0}%".format(filters.item_name)
    
    sql_query = """SELECT 
         `tabSales Order`.`name` AS `sales_order`,
         `tabSales Order`.`status` AS `status`,
         `tabSales Order`.`customer` AS `customer`,
         `tabSales Order`.`customer_name` As `customer_name`,
         `tabSales Order`.`transaction_date` As `date`,
         `tabSales Order Item`.`item_code` AS `item_code`,
         `tabSales Order Item`.`item_name` AS `item_name`,
         `tabSales Order`.`delivery_date` AS `delivery_date`,
         `tabItem`.`gebindegroesse` AS `gebindegroesse`,
         `tabSales Order Item`.`qty` AS `qty`,
         `tabSales Order Item`.`delivered_qty` As `delivered_qty`,
         (`tabSales Order Item`.`qty` - IFNULL(`tabSales Order Item`.`delivered_qty`, 0)) AS `qty_to_deliver`,
         `tabBin`.`actual_qty` AS `available_qty`,
         `tabBin`.`projected_qty` AS `projected_qty`,
         `tabSales Order Item`.`delivery_date` AS `delivery_date`,
          DATEDIFF(CURDATE(),`tabSales Order Item`.`delivery_date`) AS `delay_days`
        FROM `tabSales Order` 
         JOIN `tabSales Order Item` ON (`tabSales Order Item`.`parent` = `tabSales Order`.`name`)
         LEFT JOIN `tabBin` ON (`tabBin`.`item_code` = `tabSales Order Item`.`item_code`
            AND `tabBin`.`warehouse` = `tabSales Order Item`.`warehouse`)
         LEFT JOIN `tabItem` ON (`tabSales Order Item`.`item_code` = `tabItem`.`name`)
        WHERE
         `tabSales Order`.`docstatus` = 1
         AND `tabSales Order`.`status` NOT IN ("Stopped", "Closed", "Completed")
         AND IFNULL(`tabSales Order Item`.`delivered_qty`,0) < IFNULL(`tabSales Order Item`.`qty`,0)
         AND `tabSales Order Item`.`item_code` LIKE '{item_code}'
         AND `tabSales Order Item`.`item_name` LIKE '{item_name}'
        ORDER BY `tabSales Order`.`delivery_date` ASC, `tabSales Order`.`customer_name` ASC
      """.format(item_code=filters.item_code, item_name=filters.item_name)

    data = frappe.db.sql(sql_query, as_dict=1)

    for d in data:
        if d['qty_to_deliver'] > d['available_qty']:
            d['qty_to_deliver'] = "<span style=\"color: red; \">{0:.2f}</span>".format(d['qty_to_deliver'])
        else:
            d['qty_to_deliver'] = "{0:.2f}".format(d['qty_to_deliver'])
        
        d['available_qty'] = "{0:.2f}".format(d['available_qty'])
        
    return data
