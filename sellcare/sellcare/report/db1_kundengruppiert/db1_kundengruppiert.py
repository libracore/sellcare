## Copyright (c) 2019-2022, libracore and contributors
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

      
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 75},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 130},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 50},
        {"label": _("Customer Group"), "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group",  "width": 120},
        {"label": _("Responsible"), "fieldname": "responsible", "fieldtype": "Data", "width": 50},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "precision": 2, "width": 75},
        {"label": _("Total revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 100},
        {"label": _("Total transport charges"), "fieldname": "total_transport_charges", "fieldtype": "Currency", "width": 100},
        {"label": _("Total cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin"), "fieldname": "margin", "fieldtype": "Currency", "width": 100},
        {"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 75},
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
         `customer`,
         `customer_name`,
		 `customer_group`,
         SUM(`qty`)  AS `qty`,
         `territory`,
         `responsible`,
         SUM(`net_amount`) AS `total_revenue`,
         SUM(`transport_charges`)  AS `total_transport_charges`,
         (SUM(`cost`) - SUM(`inbound_charges`)) AS `total_cost`,
         (SUM(`net_amount`) - SUM(`transport_charges`) - SUM(`cost`) - SUM(`inbound_charges`)) AS `margin`,
         ROUND((100 * ((SUM(`net_amount`) - SUM(`transport_charges`) - SUM(`cost`) - SUM(`inbound_charges`))/(SUM(`net_amount`)))), 2) AS `margin_percent`,
         SUM(`inbound_charges`) AS `inbound_charges`
        FROM (SELECT 
          `tabSales Invoice`.`customer` AS `customer`,
          `tabSales Invoice`.`customer_name` AS `customer_name`,
		  `tabCustomer`.`customer_group` AS `customer_group`,
          `tabSales Invoice`.`name` AS `document`,
          YEAR(`tabSales Invoice`.`posting_date`) AS `year`,
          ROUND(`tabSales Invoice Item`.`qty`, 2) AS `qty`,
          `tabCustomer`.`territory` AS `territory`,
          `tabCustomer`.`responsible` AS `responsible`,
          ROUND(`tabSales Invoice Item`.`base_net_amount`, 2) AS `net_amount`,
          ROUND(`tabSales Invoice Item`.`transport_charges`, 2) AS `transport_charges`,
          ROUND((`tabSales Invoice Item`.`qty` * (SELECT AVG(`tabBin`.`valuation_rate`) FROM `tabBin` WHERE `tabBin`.`item_code` = `tabSales Invoice Item`.`item_code`)), 2) AS `cost`,
          ROUND((`tabSales Invoice Item`.`qty` * `tabItem`.`last_inbound_charges`), 2) AS `inbound_charges`
        FROM `tabSales Invoice Item`
        LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabSales Invoice Item`.`item_code`
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem Supplier` ON (`tabItem Supplier`.`parent` = `tabSales Invoice Item`.`item_code` AND `tabItem Supplier`.`parenttype` = "Item")
        LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `tabSales Invoice`.`customer`
        WHERE `tabSales Invoice`.`posting_date` >= '{from_date}'
          AND `tabSales Invoice`.`posting_date` <= '{to_date}'
          AND `tabSales Invoice`.`docstatus` = 1
        ) AS `raw`
        GROUP BY `customer`
        ORDER BY `total_revenue` DESC;
      """.format(customer=filters.customer, item_name=filters.item_name, year=filters.year, 
        from_date=filters.from_date, to_date=filters.to_date, supplier=filters.supplier)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
