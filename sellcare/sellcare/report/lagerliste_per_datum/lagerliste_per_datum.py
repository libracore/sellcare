# Copyright (c) 2020, libracore and contributors
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
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group",  "width": 120},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "width": 50},
        {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "fieldtype": "Data", "width": 75},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Currency", "width": 100}
    ]

def get_data(filters):
    if not filters.warehouse:
        filters.warehouse = "%"

    sql_query = """SELECT
                   `item_code`,
                   `item_name`,
                   `item_group`,
                   `gebindegroesse`,
                    (SELECT
                        IFNULL(SUM(`sle1`.`stock_value_difference`), 0)
                     FROM `tabStock Ledger Entry` AS `sle1`
                     WHERE `sle1`.`item_code` = `tabItem`.`item_code`
                           AND `sle1`.`posting_date` <= '2019-12-31'
                           AND `sle1`.`warehouse` LIKE '{warehouse}') AS `value`,
                    (SELECT
                        IFNULL(SUM(`sle2`.`actual_qty`), 0)
                     FROM `tabStock Ledger Entry` AS `sle2`
                     WHERE `sle2`.`item_code` = `tabItem`.`item_code`
                           AND `sle2`.`posting_date` <= '2019-12-31'
                           AND `sle2`.`warehouse` LIKE '{warehouse}') AS `qty`
                    FROM `tabItem`
                    WHERE `is_stock_item` = 1;""".format(date=filters.date, warehouse=filters.warehouse)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
