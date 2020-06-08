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
        {"label": _("Quotation"), "fieldname": "document_nr", "fieldtype": "Link", "options": "Quotation", "width": 100},
        {"label": _("Offered"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 75},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 140},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 150},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "width": 50, 'precision': '2'},
        {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "fieldtype": "Data", "width": 75},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 50},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float", "width": 75, 'precision': '2'},
        {"label": _("Amount"), "fieldname": "net_amount", "fieldtype": "Float", "width": 100, 'precision': '2'},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 120},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group",  "width": 120},
    ]
    
def get_data(filters):
    if not filters.customer:
        filters.customer = "%"
    if not filters.item_name:
        filters.item_name = "%"
    if not filters.from_date:
        filters.from_date = "%"
    if not filters.to_date:
        filters.to_date = "%"
    else:
        filters.item_name = "%{0}%".format(filters.item_name)
    if not filters.supplier:
        filters.supplier = "%"
        
    sql_query = """SELECT
         `document_nr`,
         `transaction_date`, 
         `customer`,
         `customer_name`,
         `qty`,
         `gebindegroesse`,
         `item_code`,
         `item_name`,
         `currency`,
         `rate`,
         `item_group`,
         `supplier`,
         `net_amount`
        FROM (SELECT 
          `tabQuotation`.`party_name` AS `customer`,
          `tabQuotation`.`customer_name` AS `customer_name`,
          `tabQuotation`.`name` AS `document_nr`,
          `tabQuotation`.`transaction_date` AS `transaction_date`,
          ROUND(`tabQuotation Item`.`qty`, 2) AS `qty`,
          `tabItem`.`gebindegroesse` AS `gebindegroesse`,
          `tabQuotation Item`.`item_code` AS `item_code`,
          `tabQuotation`.`currency` AS `currency`,
          `tabQuotation Item`.`item_name` AS `item_name`,
		  ROUND(`tabQuotation Item`.`rate`, 2) AS `rate`,
          `tabItem`.`item_group` AS `item_group`,
          `tabItem Supplier`.`supplier` AS `supplier`,
          ROUND(`tabQuotation Item`.`net_amount`, 2) AS `net_amount`,
          ROUND((`tabQuotation Item`.`qty` * `tabItem`.`last_inbound_charges`), 2) AS `inbound_charges`
        FROM `tabQuotation Item`
        LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabQuotation Item`.`item_code`
        LEFT JOIN `tabQuotation` ON `tabQuotation`.`name` = `tabQuotation Item`.`parent`
        LEFT JOIN `tabCustomer` ON `tabCustomer`.`name`= `tabQuotation Item`.`item_code`
        LEFT JOIN `tabItem Supplier` ON (`tabItem Supplier`.`parent` = `tabQuotation Item`.`item_code` AND `tabItem Supplier`.`parenttype` = "Item")
        WHERE `tabQuotation`.`party_name` LIKE '{customer}'
          AND `tabQuotation Item`.`item_name` LIKE '{item_name}'
          AND `tabQuotation`.`transaction_date` >= '{from_date}'
          AND `tabQuotation`.`transaction_date` <= '{to_date}'
          AND `tabQuotation`.`docstatus` = 1
          AND IFNULL(`tabItem Supplier`.`supplier`, "") LIKE '{supplier}'
        ) AS `raw`
        ORDER BY `transaction_date` DESC, `item_name`, `qty` ASC;
      """.format(customer=filters.customer, item_name=filters.item_name, year=filters.year, 
        from_date=filters.from_date, to_date=filters.to_date, supplier=filters.supplier)
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
