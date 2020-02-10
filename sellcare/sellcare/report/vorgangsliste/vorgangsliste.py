# Copyright (c) 2013-2020, libracore and contributors
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
        {"label": _("Sales Invoice"), "fieldname": "document", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
        {"label": _("Delivery date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 70},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group",  "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 50},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Net amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Total transport charges"), "fieldname": "total_transport_charges", "fieldtype": "Currency", "width": 100},
        {"label": _("Total cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 100},
        {"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 100},
        {"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 100},
        {"label": _("Inbound charges"), "fieldname": "inbound_charges", "fieldtype": "Currency", "width": 100}
    ]
    
def get_data(filters):
    if not filters.customer:
        filters.customer = "%"
    if not filters.year:
        filters.year = "%"
    if not filters.item_name:
        filters.item_name = "%"
    else:
        filters.item_name = "%{0}%".format(filters.item_name)
    if not filters.supplier:
        filters.supplier = "%"
        
    sql_query = """SELECT
         `document`,
         `delivery_date`, 
         `customer`,
         `customer_name`,
         `year`,
         `item_code`,
         `item_name`,
         `rate`,
         `item_group`,
         `supplier`,
         `net_amount`,
         `transport_charges`,
         (`cost` - `inbound_charges`) AS `cost`,
         (`net_amount` - `transport_charges` - `cost` - `inbound_charges`) AS `margin`,
         ROUND(((100 * (`net_amount` - `transport_charges` - `cost` - `inbound_charges`))/(`net_amount`)), 2) AS `margin_percent`,
         `inbound_charges`
        FROM (SELECT 
          `tabSales Invoice`.`customer` AS `customer`,
          `tabSales Invoice`.`customer_name` AS `customer_name`,
          `tabSales Invoice`.`name` AS `document`,
          `tabSales Invoice`.`delivery_date` AS `delivery_date`,
          YEAR(`tabSales Invoice`.`posting_date`) AS `year`,
          `tabSales Invoice Item`.`item_code` AS `item_code`,
          `tabSales Invoice Item`.`item_name` AS `item_name`,
          `tabSales Invoice Item`.`rate` AS `rate`,
          `tabItem`.`item_group` AS `item_group`,
          `tabItem Supplier`.`supplier` AS `supplier`,
          ROUND(`tabSales Invoice Item`.`base_net_amount`, 2) AS `net_amount`,
          ROUND(`tabSales Invoice Item`.`transport_charges`, 2) AS `transport_charges`,
          ROUND((`tabSales Invoice Item`.`qty` * `tabSales Invoice Item`.`last_purchase_rate`), 2) AS `cost`,
          CONCAT(`tabSales Invoice`.`customer`,YEAR(`tabSales Invoice`.`posting_date`),`tabSales Invoice Item`.`item_code`) AS `key`,
          ROUND((`tabSales Invoice Item`.`qty` * `tabItem`.`last_inbound_charges`), 2) AS `inbound_charges`
        FROM `tabSales Invoice Item`
        LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabSales Invoice Item`.`item_code`
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem Supplier` ON (`tabItem Supplier`.`parent` = `tabSales Invoice Item`.`item_code` AND `tabItem Supplier`.`parenttype` = "Item")
        WHERE `tabSales Invoice`.`customer` LIKE '{customer}'
          AND `tabSales Invoice Item`.`item_name` LIKE '{item_name}'
          AND `tabSales Invoice`.`posting_date` >= '{from_date}'
          AND `tabSales Invoice`.`posting_date` <= '{to_date}'
          AND `tabSales Invoice`.`docstatus` = 1
          AND YEAR(`tabSales Invoice`.`posting_date`) LIKE '{year}'
          AND IFNULL(`tabItem Supplier`.`supplier`, "") LIKE '{supplier}'
        ) AS `raw`
        ORDER BY `delivery_date` DESC;
      """.format(customer=filters.customer, item_name=filters.item_name, year=filters.year, 
        from_date=filters.from_date, to_date=filters.to_date, supplier=filters.supplier)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data