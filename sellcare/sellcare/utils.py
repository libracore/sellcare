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
       
@frappe.whitelist()
def get_batch_info(item_code):
    sql_query = """SELECT `item_code`, `batch_no`, `qty`, `valuation_rate`
        FROM (SELECT `item_code`, `batch_no`, SUM(`actual_qty`) AS `qty`, AVG(`valuation_rate`) AS `valuation_rate`
        FROM `tabStock Ledger Entry`
        WHERE `item_code` = '{item_code}'
        GROUP BY `batch_no`) AS `batches`
        WHERE `qty` > 0;""".format(item_code=item_code)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    return data

""" This function allows to automatically create pricing rules (e.g. for staggered pricing) from Quotations """
@frappe.whitelist()
def create_pricing_rules_from_qtn(quotation):
    # get original document
    qtn = frappe.get_doc("Quotation", quotation)
    customer = qtn.party_name
    if customer:
        # loop through items
        for item in qtn.items:
            # check if there is already a matching pricing rule
            matching_rules = get_matching_pricing_rules(customer, item.item_code, item.qty)
            if matching_rules:
                # update rule
                rule = frappe.get_doc("Pricing Rule", matching_rules[0]['name'])
                rule.rate = item.rate
                rule.priority = find_priority(customer, item.item_code, int(item.qty))
                rule.save()
                frappe.db.commit()
            else:
                # create rule
                prio = find_priority(customer, item.item_code, int(item.qty))
                rule = frappe.get_doc({
                    'doctype': 'Pricing Rule',
                    'apply_on': 'Item Code',
                    'items': [{'item_code': item.item_code}],
                    'selling': 1,
                    'applicable_for': 'Customer',
                    'customer': customer,
                    'min_qty': item.qty,
                    'rate_or_discount': 'Rate',
                    'rate': item.rate,
                    'priority': prio,
                    'title': "{0} {1} {2}kg".format(customer, item.item_code, item.qty)
                })
                rule.insert()
                frappe.db.commit()
    return
            
def get_matching_pricing_rules(customer, item_code, qty):
    sql_query = """SELECT 
          `tabPricing Rule`.`name`,
          `tabPricing Rule`.`customer`,
          `tabPricing Rule`.`min_qty`,
          `tabPricing Rule`.`priority`,
          `tabPricing Rule`.`rate`,
          `tabPricing Rule Item Code`.`item_code`
        FROM `tabPricing Rule Item Code`
        LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
        WHERE 
          `tabPricing Rule Item Code`.`item_code` = '{item_code}'
          AND `tabPricing Rule`.`customer` = '{customer}'
          AND `tabPricing Rule`.`min_qty` = {qty};""".format(item_code=item_code, qty=qty, customer=customer)
    data = frappe.db.sql(sql_query, as_dict=1)
    return data

def find_priority(customer, item_code, qty):
    sql_query = """SELECT MAX(`tabPricing Rule`.`priority`) AS `max`
        FROM `tabPricing Rule Item Code`
        LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
        WHERE 
          `tabPricing Rule Item Code`.`item_code` = '{item_code}'
          AND `tabPricing Rule`.`customer` = '{customer}'
          AND `tabPricing Rule`.`min_qty` < {qty};""".format(item_code=item_code, qty=qty, customer=customer)
    data = frappe.db.sql(sql_query, as_dict=1)
    if data and data[0]['max']:
        if int(data[0]['max']) > 19:
            prio = 20
        else:
            prio = int(data[0]['max']) + 1
    else:
        prio = 1
    return prio
