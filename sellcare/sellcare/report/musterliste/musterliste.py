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
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 75},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 140},
        {"label": _("Responsible"), "fieldname": "responsible", "fieldtype": "Data", "width": 50},
        {"label": _("Delivery date"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 100},
        {"label": _("Contact Person"), "fieldname": "contact_person", "fieldtype": "Data", "width": 120},              
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 75},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 150},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "width": 60, "precision": 3},
        {"label": _("Gebindegrösse"), "fieldname": "gebindegroesse", "fieldtype": "Data", "width": 75},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 75},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 100},
        {"label": _("Nachfassen"), "fieldname": "follow_up", "fieldtype": "Data", "width": 120},      
        {"label": _("Feedback"), "fieldname": "feedback", "fieldtype": "Data", "width": 300},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 120},

    ]
    
def get_data(filters):
    if not filters.customer:
        filters.customer = "%"
    if not filters.responsible:
        filters.responsible = "%"
    if not filters.delivery_date:
        filters.delivery_date = "%"
    if not filters.item_name:
        filters.item_name = "%"
    else:
        filters.item_name = "%{0}%".format(filters.item_name)
    if not filters.follow_up or filters.follow_up == "":
        filters.follow_up = "%"
    if not filters.supplier:
        filters.supplier = "%"
        
    sql_query = """SELECT  
         `customer`,
         `customer_name`,
         `delivery_note`,
         `responsible`,
		 `follow_up`,
         `feedback`,
		 `contact_person`,
         `delivery_date`, 
		 `qty`,
         `gebindegroesse`,
         `item_code`,
         `item_name`,
         `rate`,
         `item_group`,
         `supplier`
        FROM (SELECT 
          `tabDelivery Note`.`customer` AS `customer`,
          `tabDelivery Note`.`customer_name` AS `customer_name`,
		  `tabDelivery Note`.`contact_person` AS `contact_person`,
          `tabDelivery Note`.`name` AS `delivery_note`,
		  `tabDelivery Note`.`follow_up` AS `follow_up`,
		  `tabDelivery Note`.`feedback`  AS `feedback`,
          `tabCustomer`.`responsible` AS `responsible`,
          `tabDelivery Note`.`delivery_date` AS `delivery_date`,
          ROUND(`tabDelivery Note Item`.`qty`, 2) AS `qty`,
          `tabItem`.`gebindegroesse` AS `gebindegroesse`,
          `tabDelivery Note Item`.`item_code` AS `item_code`,
          `tabDelivery Note Item`.`item_name` AS `item_name`,
          ROUND(`tabDelivery Note Item`.`rate`, 2) AS `rate`,
          `tabItem`.`item_group` AS `item_group`,
          `tabItem Supplier`.`supplier` AS `supplier`
        FROM `tabDelivery Note Item`
        LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabDelivery Note Item`.`item_code`
        LEFT JOIN `tabDelivery Note` ON `tabDelivery Note`.`name` = `tabDelivery Note Item`.`parent`
        LEFT JOIN `tabItem Supplier` ON (`tabItem Supplier`.`parent` = `tabDelivery Note Item`.`item_code` AND `tabItem Supplier`.`parenttype` = "Item")
        LEFT JOIN `tabCustomer` ON `tabDelivery Note`.`customer` =  `tabCustomer`.`name`
        WHERE `tabDelivery Note`.`customer` LIKE '{customer}'
          AND `tabDelivery Note Item`.`item_name` LIKE '{item_name}'    
          AND IFNULL(`tabCustomer`.`responsible`, "") LIKE '{responsible}' 
          AND IFNULL(`tabDelivery Note`.`follow_up`, "") LIKE '{follow_up}' 
          AND `tabDelivery Note Item`.`item_code` LIKE '%.M'
          AND `tabDelivery Note`.`posting_date` >= '{from_date}'
          AND `tabDelivery Note`.`posting_date` <= '{to_date}'
          AND `tabDelivery Note`.`docstatus` = 1
          AND IFNULL(`tabItem Supplier`.`supplier`, "") LIKE '{supplier}'
        ) AS `raw`
        ORDER BY `delivery_date` DESC;
      """.format(customer=filters.customer, item_name=filters.item_name,
         from_date=filters.from_date, responsible=filters.responsible, follow_up=filters.follow_up, to_date=filters.to_date, supplier=filters.supplier)
    
    data = frappe.db.sql(sql_query, as_dict=1)

    return data
