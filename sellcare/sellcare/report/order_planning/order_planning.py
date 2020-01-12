# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast      # to parse str to dict (from JS calls)

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_planning_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
        {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "width": 100},
        {"label": _("Default Supplier"), "fieldname": "default_supplier", "fieldtype": "Link", "options": "Supplier", "width": 140},
        #{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"label": _("Actual Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Reserved Qty"), "fieldname": "reserved_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Ordered Qty"), "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Projected Qty"), "fieldname": "projected_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Safety Stock"), "fieldname": "safety_stock", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("Projected Safety Qty"), "fieldname": "projected_safety_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
    ]

@frappe.whitelist()
def get_planning_data(filters, only_reorder=0):
    conditions = []
    if int(only_reorder) == 1:
        conditions.append("(`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) < 0")
    if type(filters) is str:
        filters = ast.literal_eval(filters)
        try:
            if filters['warehouse']:
                conditions.append("`tabBin`.`warehouse` = '{0}'".format(filters['warehouse']))
        except:
            pass
        if filters['supplier']:
            conditions.append("`tabItem Default`.`default_supplier` = '{0}'".format(filters['supplier']))
    else:
        if filters.warehouse:
            conditions.append("`tabBin`.`warehouse` = '{0}'".format(filters.warehouse))
        if filters.supplier:
            conditions.append("`tabItem Default`.`default_supplier` = '{0}'".format(filters.supplier))
    
    sql_query = """SELECT
        `tabBin`.`item_code` AS `item_code`, 
        `tabItem`.`item_name` AS `item_name`, 
        `tabItem`.`item_group` AS `item_group`,
        `tabItem`.`gebindegroesse` AS `gebindegroesse`,
        `tabItem Default`.`default_supplier` AS `default_supplier`,
        `tabBin`.`warehouse` AS `warehouse`, 
        `tabBin`.`actual_qty` AS `actual_qty`, 
        `tabBin`.`reserved_qty` AS `reserved_qty`,
        `tabBin`.`ordered_qty` AS `ordered_qty`,
        `tabBin`.`projected_qty` AS `projected_qty`,
        `tabItem`.`safety_stock` AS `safety_stock`,
        (`tabBin`.`projected_qty` - `tabItem`.`safety_stock`) AS `projected_safety_qty`
      FROM `tabBin`
      LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBin`.`item_code`
      LEFT JOIN `tabItem Default` ON 
        (`tabItem Default`.`parenttype` = 'Item' AND `tabItem Default`.`parent` = `tabBin`.`item_code`)
      {conditions} 
      ORDER BY `tabBin`.`projected_qty` ASC
      """.format(conditions=" WHERE " + " AND ".join(conditions) if conditions else "")

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
