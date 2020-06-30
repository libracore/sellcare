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
        {"label": _("Delivery Date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 75},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 75},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 140},
        {"label": _("Packaging"), "fieldname": "gebindegroesse", "width": 75},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 75},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "precision": 3, "width": 80},
        {"label": _("Net amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Cost"), "fieldname": "cost", "fieldtype": "Currency", "width": 100},
        {"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 100},
        {"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 70},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100}
    ]
    
def get_data(filters):
    if not filters.item_code:
        filters.item_code = "%"
    if not filters.item_name:
        filters.item_name = "%"
    else:
        filters.item_name = "%{0}%".format(filters.item_name)
    if not filters.supplier:
        filters.supplier = "%"
    if not filters.customer:
        filters.customer = "%"
                    
    sql_query = """SELECT
          `delivery_date`,
          `sales_order`,
          `item_code`,
          `item_name`,
          `gebindegroesse`,
          `customer`,
          `customer_name`,
          `qty`,
          `base_net_amount` AS `net_amount`,
          `cost`,
          (`base_net_amount` - `cost`) AS `margin`,
          ROUND(((100 * `base_net_amount` - `cost`) / `base_net_amount`), 2) AS `margin_percent`,
          `supplier`
        FROM 
        (SELECT 
         `tabSales Order`.`name` AS `sales_order`,
         `tabSales Order`.`status` AS `status`,
         `tabSales Order`.`customer` AS `customer`,
         `tabSales Order`.`customer_name` As `customer_name`,
		 `tabSales Order`.`delivery_date` As `delivery_date`,
         `tabSales Order Item`.`item_code` AS `item_code`,
         `tabSales Order Item`.`item_name` AS `item_name`,
         `tabSales Order Item`.`base_net_amount` AS `base_net_amount`,
         `tabItem`.`gebindegroesse` AS `gebindegroesse`,
         `tabSales Order Item`.`qty` AS `qty`,
         `tabItem Supplier`.`supplier` AS `supplier`,
         ROUND((`tabSales Order Item`.`qty` * (`tabItem`.`last_purchase_rate` + `tabItem`.`last_inbound_charges`)), 2) AS `cost`
         /*CONCAT(`tabSales Order Item`.`item_code`, "-", `tabSales Order`.`customer`) AS `key`*/
        FROM `tabSales Order Item` 
         JOIN `tabSales Order` ON (`tabSales Order`.`name` = `tabSales Order Item`.`parent`)
         LEFT JOIN `tabItem` ON (`tabSales Order Item`.`item_code` = `tabItem`.`name`)
         LEFT JOIN `tabItem Supplier` ON (`tabItem Supplier`.`parent` = `tabSales Order Item`.`item_code` AND `tabItem Supplier`.`parenttype` = "Item")
        WHERE
         `tabSales Order`.`docstatus` = 1
         AND `tabSales Order`.`status` NOT IN ("Stopped", "Closed", "Completed")
         AND IFNULL(`tabSales Order Item`.`delivered_qty`,0) < IFNULL(`tabSales Order Item`.`qty`,0)
         AND `tabSales Order Item`.`item_code` LIKE '{item_code}'
         AND `tabSales Order Item`.`item_name` LIKE '{item_name}'
         AND `tabSales Order`.`customer` LIKE '{customer}'
         AND IFNULL(`tabItem Supplier`.`supplier`, "") LIKE '{supplier}'
        ) AS `raw`
        ORDER BY `delivery_date` ASC;
      """.format(item_code=filters.item_code, item_name=filters.item_name, 
                 supplier=filters.supplier, customer=filters.customer)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
