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
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 100},
        {"label": _("Total revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 150},
        {"label": _("Total transport charges"), "fieldname": "total_transport_charges", "fieldtype": "Currency", "width": 150},
        {"label": _("Total cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 150},
        {"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 150},
        {"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 150}
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
    
    sql_query = """SELECT
         `customer`,
         `customer_name`,
         `year`,
         `item_code`,
         `item_name`,
         SUM(`net_amount`) AS `total_revenue`,
         SUM(`transport_charges`)  AS `total_transport_charges`,
         SUM(`cost`) AS `total_cost`,
         (SUM(`net_amount`) - SUM(`transport_charges`) - SUM(`cost`)) AS `margin`,
         ROUND((100 * ((SUM(`net_amount`) - SUM(`transport_charges`) - SUM(`cost`))/(SUM(`net_amount`)))), 2) AS `margin_percent`
        FROM (SELECT 
          `tabSales Invoice`.`customer` AS `customer`,
          `tabSales Invoice`.`customer_name` AS `customer_name`,
          `tabSales Invoice`.`name` AS `document`,
          YEAR(`tabSales Invoice`.`posting_date`) AS `year`,
          `tabSales Invoice Item`.`item_code` AS `item_code`,
          `tabSales Invoice Item`.`item_name` AS `item_name`,
          ROUND(`tabSales Invoice Item`.`base_net_amount`, 2) AS `net_amount`,
          ROUND(`tabSales Invoice Item`.`transport_charges`, 2) AS `transport_charges`,
          ROUND((`tabSales Invoice Item`.`qty` * `tabItem`.`last_purchase_rate`), 2) AS `cost`,
          CONCAT(`tabSales Invoice`.`customer`,YEAR(`tabSales Invoice`.`posting_date`),`tabSales Invoice Item`.`item_code`) AS `key`
        FROM `tabSales Invoice Item`
        LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabSales Invoice Item`.`item_code`
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        WHERE `tabSales Invoice`.`customer` LIKE '{customer}'
          AND `tabSales Invoice Item`.`item_name` LIKE '{item_name}'
          AND `tabSales Invoice`.`posting_date` >= '{from_date}'
          AND `tabSales Invoice`.`posting_date` <= '{to_date}'
          AND YEAR(`tabSales Invoice`.`posting_date`) LIKE '{year}'
        ) AS `raw`
        GROUP BY `key`;
      """.format(customer=filters.customer, item_name=filters.item_name, year=filters.year, 
        from_date=filters.from_date, to_date=filters.to_date)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
