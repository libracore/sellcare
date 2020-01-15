# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def check_so_margin(sales_order):
    sql_query = """SELECT *, `base_amount` - `base_cost` AS `margin` FROM (SELECT
       `tabSales Order Item`.`idx` AS `idx`,
       `tabSales Order Item`.`item_name` AS `item_name`,
       ROUND(`tabSales Order Item`.`base_amount`, 2) AS `base_amount`,
       ROUND((`tabItem`.`last_purchase_rate` * `tabSales Order Item`.`qty` + `tabSales Order Item`.`transport_charges`), 2) AS `base_cost`
      FROM `tabSales Order Item`
      LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabSales Order Item`.`item_code`
      WHERE `tabSales Order Item`.`parent` = '{sales_order}') AS `items`
      ORDER BY `idx` ASC;
    """.format(sales_order=sales_order)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    
    return data
       
