# Copyright (c) 2013-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data
    
def get_columns(filters):
    currency = "CHF"
    if filters.customer:
        currency = frappe.get_value("Customer", filters.customer, "default_currency")
        
    columns = [
        {"label": _("Sales Invoice"), "fieldname": "document", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
        {"label": _("Delivery date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 70},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group",  "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 50},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "precision": 3, "width": 50},
        {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "fieldtype": "Data", "width": 75},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 50},     
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float", "precision": 2, "width": 75}
    ]
    if currency != "CHF":
        columns.append({"label": "{0} ({1})".format(_("Net Amount"), currency), "fieldname": "net_amount", "fieldtype": "Float", "precision": 2, "width": 100})
        
    columns.append({"label": _("Net Amount"), "fieldname": "base_net_amount", "fieldtype": "Currency", "width": 100})
    columns.append({"label": _("Total Transport charges"), "fieldname": "transport_charges", "fieldtype": "Currency", "width": 100})
    columns.append({"label": _("Total Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 100})
    columns.append({"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 100})
    columns.append({"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 100})
    columns.append({"label": _("Inbound charges"), "fieldname": "inbound_charges", "fieldtype": "Currency", "width": 100})
    
    return columns
    
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
    if int(filters.hide_samples or 0) == 1:
        conditions.append("`tabBin`.`item_code` NOT LIKE '%.M%'")
	
        
    sql_query = """SELECT
         `document`,
         `delivery_date`, 
         `customer`,
         `customer_name`,
         `year`,
         `qty`,
         `gebindegroesse`,
         `item_code`,
         `item_name`,
         `currency`,
         `rate`,
         `item_group`,
         `supplier`,
         `net_amount`,
         `base_net_amount`,
         `transport_charges`,
         (`cost` + `inbound_charges`) AS `cost`,
         (`net_amount` - `transport_charges` - `cost` - `inbound_charges`) AS `margin`,
         ROUND(((100 * (`net_amount` - `transport_charges` - `cost` - `inbound_charges`))/(`net_amount`)), 2) AS `margin_percent`,
         `inbound_charges`
        FROM (SELECT 
          `tabSales Invoice`.`customer` AS `customer`,
          `tabSales Invoice`.`currency` AS `currency`,
          `tabSales Invoice`.`customer_name` AS `customer_name`,
          `tabSales Invoice`.`name` AS `document`,
          `tabSales Invoice`.`delivery_date` AS `delivery_date`,
          YEAR(`tabSales Invoice`.`posting_date`) AS `year`,
          ROUND(`tabSales Invoice Item`.`qty`, 2) AS `qty`,
          `tabItem`.`gebindegroesse` AS `gebindegroesse`,
          `tabSales Invoice Item`.`item_code` AS `item_code`,
          `tabSales Invoice Item`.`item_name` AS `item_name`,
          `tabSales Invoice Item`.`rate` AS `rate`,
          `tabItem`.`item_group` AS `item_group`,
          `tabItem Supplier`.`supplier` AS `supplier`,
          ROUND(`tabSales Invoice Item`.`net_amount`, 2) AS `net_amount`,
          ROUND(`tabSales Invoice Item`.`base_net_amount`, 2) AS `base_net_amount`,
          ROUND(`tabSales Invoice Item`.`transport_charges`, 2) AS `transport_charges`,
          ROUND((`tabSales Invoice Item`.`qty` * `tabSales Invoice Item`.`cogs_rate`), 2) AS `cost`,
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
