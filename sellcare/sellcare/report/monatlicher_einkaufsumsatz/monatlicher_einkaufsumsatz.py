# Copyright (c) 2013, libracore and contributors
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
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 55},
        {"label": _("Jan"), "fieldname": "Jan", "fieldtype": "Int", "width": 65},
        {"label": _("Feb"), "fieldname": "Feb", "fieldtype": "Int", "width": 65},
        {"label": _("Mar"), "fieldname": "Mar", "fieldtype": "Int", "width": 65},
        {"label": _("Apr"), "fieldname": "Apr", "fieldtype": "Int", "width": 65},
        {"label": _("May"), "fieldname": "May", "fieldtype": "Int", "width": 65},
        {"label": _("Jun"), "fieldname": "Jun", "fieldtype": "Int", "width": 65},
        {"label": _("Jul"), "fieldname": "Jul", "fieldtype": "Int", "width": 65},
        {"label": _("Aug"), "fieldname": "Aug", "fieldtype": "Int", "width": 65},
        {"label": _("Sep"), "fieldname": "Sep", "fieldtype": "Int", "width": 65},
        {"label": _("Oct"), "fieldname": "Oct", "fieldtype": "Int", "width": 65},
        {"label": _("Nov"), "fieldname": "Nov", "fieldtype": "Int", "width": 65},
        {"label": _("Dec"), "fieldname": "Dec", "fieldtype": "Int", "width": 65},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 75}
    ]
    
def get_data(filters):
    if not filters.supplier:
        filters.supplier = "%"
    if not filters.year:
        filters.year = "%"

    sql_query = """SELECT *, (`raw`.`Jan` + `raw`.`Feb` + `raw`.`Mar` + `raw`.`Apr` + `raw`.`May` + `raw`.`Jun` + `raw`.`Jul` + `raw`.`Aug` +`raw`.`Sep` + `raw`.`Oct` + `raw`.`Nov` + `raw`.`Dec` )  AS `year`

        FROM (SELECT 
          `name` AS `supplier`, 
          IFNULL(`default_currency`, "CHF") AS `currency`,
          IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier` 
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-01-01" 
                  AND `bill_date` < "{year}-02-01")), 0) AS `Jan`,
          IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-02-01" 
                  AND `bill_date` < "{year}-03-01")), 0) AS `Feb`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier` 
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-03-01" 
                  AND `bill_date` < "{year}-04-01")), 0) AS `Mar`,
        IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-04-01" 
                  AND `bill_date` < "{year}-05-01")), 0) AS `Apr`,
        IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier` 
                  AND `bill_date` >= "{year}-05-01" 
                  AND `bill_date` < "{year}-06-01")), 0) AS `May`,
        IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-06-01" 
                  AND `bill_date` < "{year}-07-01")), 0) AS `Jun`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-07-01" 
                  AND `bill_date` < "{year}-08-01")), 0) AS `Jul`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-08-01" 
                  AND `bill_date` < "{year}-09-01")), 0) AS `Aug`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-09-01" 
                  AND `bill_date` < "{year}-10-01")), 0) AS `Sep`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-10-01" 
                  AND `bill_date` < "{year}-11-01")), 0) AS `Oct`,
         IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-11-01" 
                  AND `bill_date` < "{year}-12-01")), 0) AS `Nov`,
        IFNULL((SELECT SUM(`net_total`)
           FROM `tabPurchase Invoice` 
           WHERE (`tabSupplier`.`name` = `tabPurchase Invoice`.`supplier`
                  AND `docstatus` = 1 
                  AND `bill_date` >= "{year}-12-01" 
                  AND `bill_date` <= "{year}-12-31")), 0) AS `Dec`
                  
        FROM `tabSupplier` WHERE `name` LIKE '{supplier}') AS `raw`;
         """.format(year=filters.year, supplier=filters.supplier)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
