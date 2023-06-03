# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def check_so_margin(sales_order):
    sql_query = """SELECT *, `base_amount` - `base_cost` AS `margin` FROM (SELECT
       `tabSales Order Item`.`idx` AS `idx`,
       `tabSales Order Item`.`item_name` AS `item_name`,
       ROUND(`tabSales Order Item`.`base_amount`, 2) AS `base_amount`,
       ROUND(((`tabItem`.`last_purchase_rate` + `tabItem`.`last_inbound_charges`) * `tabSales Order Item`.`qty` + `tabSales Order Item`.`transport_charges`), 2) AS `base_cost`
      FROM `tabSales Order Item`
      LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabSales Order Item`.`item_code`
      WHERE `tabSales Order Item`.`parent` = '{sales_order}') AS `items`
      ORDER BY `idx` ASC;
    """.format(sales_order=sales_order)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    
    return data
       
@frappe.whitelist()
def get_batch_info(item_code):
    sql_query = """SELECT 
          `batches`.`item_code`, 
          `batches`.`batch_no`, 
          `batches`.`qty`, 
          `batches`.`valuation_rate`, 
          `batches`.`min_rate`, 
          `batches`.`max_rate`, 
          (`batches`.`max_rate` + `tabItem`.`last_inbound_charges`) AS `full_rate`
        FROM (
          SELECT 
            `tabStock Ledger Entry`.`item_code`, 
            `tabStock Ledger Entry`.`batch_no`, 
            SUM(`tabStock Ledger Entry`.`actual_qty`) AS `qty`, 
            AVG(`tabStock Ledger Entry`.`valuation_rate`) AS `valuation_rate`,
            ROUND((SELECT MIN(`tabSLEin`.`incoming_rate`) 
             FROM `tabStock Ledger Entry` AS `tabSLEin`
             WHERE `tabSLEin`.`batch_no` = `tabStock Ledger Entry`.`batch_no`
               AND `tabSLEin`.`item_code` = `tabStock Ledger Entry`.`item_code`
               AND `tabSLEin`.`incoming_rate` > 0), 2) AS `min_rate`,
            ROUND(MAX(`tabStock Ledger Entry`.`incoming_rate`), 2) AS `max_rate`
          FROM `tabStock Ledger Entry`        
          WHERE `item_code` = '{item_code}'
          GROUP BY `batch_no`) AS `batches`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `batches`.`item_code`
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
            matching_rules = get_matching_pricing_rules(customer, item.item_code, item.qty, item.item_price_valid_from)
            if matching_rules:
                # update rule
                rule = frappe.get_doc("Pricing Rule", matching_rules[0]['name'])
                rule.rate = item.rate
                rule.valid_from = item.item_price_valid_from
                rule.priority = find_priority(customer, item.item_code, int(item.qty))
                rule.save()
                frappe.db.commit()
            else:
                set_upto_in_earlier_pricing_rule(customer, item.item_code, item.qty, item.item_price_valid_from)
                valid_upto = get_upto_from_later_pricing_rule(customer, item.item_code, item.qty, item.item_price_valid_from)
                # create new rule
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
                    'valid_from': item.item_price_valid_from,
                    'valid_upto': valid_upto,
                    'priority': prio,
                    'title': "{0} {1} {2}kg {3}".format(customer, item.item_code, item.qty, item.item_price_valid_from)
                })
                rule.insert()
                frappe.db.commit()
    return
            
def get_matching_pricing_rules(customer, item_code, qty, valid_from):
    sql_query = """SELECT 
          `tabPricing Rule`.`name`,
          `tabPricing Rule`.`customer`,
          `tabPricing Rule`.`min_qty`,
          `tabPricing Rule`.`priority`,
          `tabPricing Rule`.`valid_from`,
          `tabPricing Rule`.`rate`,
          `tabPricing Rule Item Code`.`item_code`
        FROM `tabPricing Rule Item Code`
        LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
        WHERE 
          `tabPricing Rule Item Code`.`item_code` = '{item_code}'
          AND `tabPricing Rule`.`customer` = '{customer}'
          AND `tabPricing Rule`.`valid_from` = '{valid_from}'
          AND `tabPricing Rule`.`min_qty` = {qty};""".format(item_code=item_code, qty=qty, customer=customer, valid_from=valid_from)
    data = frappe.db.sql(sql_query, as_dict=1)
    return data
    
def set_upto_in_earlier_pricing_rule(customer, item_code, qty, valid_from):
    sql_query = """SELECT 
          `tabPricing Rule`.`name`
        FROM `tabPricing Rule Item Code`
        LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
        WHERE 
          `tabPricing Rule Item Code`.`item_code` = '{item_code}'
          AND `tabPricing Rule`.`customer` = '{customer}'
          AND `tabPricing Rule`.`valid_from` < '{valid_from}'
          AND `tabPricing Rule`.`min_qty` = {qty}
        ORDER BY `tabPricing Rule`.`valid_from` DESC
        LIMIT 1;""".format(item_code=item_code, qty=qty, customer=customer, valid_from=valid_from)
    earlier_pricing_rules = frappe.db.sql(sql_query, as_dict=1)
    if earlier_pricing_rules and len(earlier_pricing_rules) > 0:
        earlier_pricing_rule = frappe.get_doc("Pricing Rule", earlier_pricing_rules[0]['name'])
        earlier_pricing_rule.valid_upto = valid_from - timedelta (days = 1)
        earlier_pricing_rule.save()
    return

def get_upto_from_later_pricing_rule(customer, item_code, qty, valid_from):
    sql_query = """SELECT 
          `tabPricing Rule`.`valid_from`
        FROM `tabPricing Rule Item Code`
        LEFT JOIN `tabPricing Rule` ON `tabPricing Rule`.`name` = `tabPricing Rule Item Code`.`parent`
        WHERE 
          `tabPricing Rule Item Code`.`item_code` = '{item_code}'
          AND `tabPricing Rule`.`customer` = '{customer}'
          AND `tabPricing Rule`.`valid_from` > '{valid_from}'
          AND `tabPricing Rule`.`min_qty` = {qty}
        ORDER BY `tabPricing Rule`.`valid_from` ASC
        LIMIT 1;""".format(item_code=item_code, qty=qty, customer=customer, valid_from=valid_from)
    later_pricing_rules = frappe.db.sql(sql_query, as_dict=1)
    if later_pricing_rules and len(later_pricing_rules) > 0:
        return later_pricing_rules[0]['valid_from'] - timedelta (days = 1)
    else:
        return None
    
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
    #if no prio found, create one
    else:
        prio = 1
    return prio

""" This function is used to suggest the next item code when creating a new item """
@frappe.whitelist()
def get_next_item_code():
    sql_query = """SELECT SUBSTRING(`item_code`, 1, 5) AS `last`
                   FROM `tabItem`
                   ORDER BY `item_code` DESC
                   LIMIT 1;"""
    try:
        last_item_code = int(frappe.db.sql(sql_query, as_dict=1)[0]['last'])
    except:
        last_item_code = 0
    next_item_code = "{0}.0".format(last_item_code + 1)
    return next_item_code

""" This function is used to update the item master data with inbound charges (per kg) from purchase invoices """
@frappe.whitelist()
def update_inbound_charges(purchase_invoice):
    pinv = frappe.get_doc("Purchase Invoice", purchase_invoice)
    if pinv.total_inbound_charges > 0:
        # update individual inbound charges per item
        charge_per_unit = round(pinv.total_inbound_charges / pinv.total_qty, 2)
        for item in pinv.items:
            item.inbound_charges = charge_per_unit
            # update item master data
            i = frappe.get_doc("Item", item.item_code)
            if not i.last_inbound_charges or i.last_inbound_charges <= 0:
                # apply current last value
                i.last_inbound_charges = charge_per_unit
            else:
                # apply floating average
                i.last_inbound_charges = round((i.last_inbound_charges + charge_per_unit) / 2, 2)
            i.save()
        pinv.save()
        frappe.db.commit()
    return

@frappe.whitelist()
def get_blanket_orders(item_code):
    sql_query = """SELECT
		`tabBlanket Order`.`name` AS `blanket_order`,
		`tabBlanket Order`.`to_date` AS `to_date`,
		`tabBlanket Order`.`customer_name` AS `customer_name`,
		`tabBlanket Order Item`.`qty` AS `qty`,
		`tabBlanket Order Item`.`ordered_qty` AS `bo_ordered_qty`,
		(`tabBlanket Order Item`.`qty` - `tabBlanket Order Item`.`ordered_qty`) AS `bo_outstanding_qty`
       FROM `tabBlanket Order`
       LEFT JOIN `tabBlanket Order Item` ON `tabBlanket Order`.`name` = `tabBlanket Order Item`.`parent`
        WHERE `tabBlanket Order`.`docstatus` = 1 AND (`tabBlanket Order Item`.`qty` - `tabBlanket Order Item`.`ordered_qty`) > 0 AND `tabBlanket Order Item`.`item_code` = '{item_code}'
        ORDER BY `tabBlanket Order`.`to_date` ASC""".format(item_code=item_code)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    return data

"""
This function will compute the CoGS based on a delivery note item or sales order+item
"""
def get_cogs(sales_order=None, item_code=None, delivery_note_item=None):
    if delivery_note_item:
	# find batch from delivery note, look up all incoming rates and find average rate
        sql_query = """
            SELECT IFNULL(AVG(`tabStock Ledger Entry`.`valuation_rate`), 0) AS `valuation_rate`
            FROM `tabStock Ledger Entry`
            WHERE
                `tabStock Ledger Entry`.`batch_no` = (SELECT `batch_no` FROM `tabDelivery Note Item` WHERE `name` = "{dn_detail}")
                AND `tabStock Ledger Entry`.`actual_qty` > 0
            ;
        """.format(dn_detail=delivery_note_item)
    elif sales_order:
	# map delivery note from sales order
        sql_query = """
            SELECT IFNULL(AVG(`tabStock Ledger Entry`.`valuation_rate`), 0) AS `valuation_rate`
            FROM `tabDelivery Note Item` 
            LEFT JOIN `tabStock Ledger Entry` ON `tabStock Ledger Entry`.`batch_no` = `tabDelivery Note Item`.`batch_no`
            WHERE
                `tabStock Ledger Entry`.`actual_qty` > 0
                AND `tabDelivery Note Item`.`item_code` = "{item_code}"
                AND `tabDelivery Note Item`.`against_sales_order` = "{sales_order}"
            ;
        """.format(item_code=item_code, sales_order=sales_order)
        
    else:
        sql_query = None
    if sql_query:
        data = frappe.db.sql(sql_query, as_dict=True)
        cogs = data[0]['valuation_rate']
    else:
        cogs = None
    if not cogs:
        # fallback to last purchase rate
        cogs = frappe.get_value("Item", item_code, "last_purchase_rate")
    return cogs

"""
This function will validate cogs against last_purchase rates (output display)

Run from bench using 
 $ bench execute sellcare.sellcare.utils.test_validate_cogs
"""
def test_validate_cogs():
    sinvs = frappe.get_all("Sales Invoice", filters={'docstatus': 1}, fields=['name'])
    for sinv in sinvs:
        doc = frappe.get_doc("Sales Invoice", sinv['name'])
        for i in doc.items:
            if i.sales_order:
                if i.dn_detail:
                    cogs = get_cogs(delivery_note_item=i.dn_detail)
                else:
                    cogs = get_cogs(sales_order=i.sales_order, item_code=i.item_code)
                
                print("{0}#{1}: rate: {2}, last_purchase: {3}, cogs: {4}".format(doc.name, i.item_code,
                    i.rate, i.last_purchase_rate, cogs))
    return

"""
This function can be used to recursively compute and update cogs value (migration)

Run from bench using:
 $ bench execute sellcare.sellcare.utils.compute_sinv_cogs
"""
def compute_sinv_cogs():
    sinvs = frappe.get_all("Sales Invoice", filters={'docstatus': 1}, fields=['name'])
    for sinv in sinvs:
        store_cogs(sinv['name'], debug=True)
    return

"""
This function allows to store the cogs after submit of a sales invoice
"""
@frappe.whitelist()
def store_cogs(sinv, debug=False):
    doc = frappe.get_doc("Sales Invoice", sinv)
    for i in doc.items:
        if i.dn_detail:
            cogs = get_cogs(delivery_note_item=i.dn_detail)
        elif i.sales_order:
            cogs = get_cogs(sales_order=i.sales_order, item_code=i.item_code)
        else:
            cogs = get_cogs(item_code=i.item_code)
        if debug:
            print("{0}#{1}: rate: {2}, last_purchase: {3}, cogs: {4}".format(doc.name, i.item_code,
                i.rate, i.last_purchase_rate, cogs))
        try:
            frappe.db.sql("""UPDATE `tabSales Invoice Item`
                         SET `cogs_rate` = {cogs}
                         WHERE `name` = "{name}";""".format(cogs=cogs, name=i.name))
        except Exception as err:
            frappe.log_error( err, "Store COGS failed: {0}".format(sinv))
    frappe.db.commit()

"""
This function allows to switch a sales order to delivered/completed (so that blanket orders can be closed with different items)
"""
@frappe.whitelist()
def deliver_and_close_sales_order(sales_order):
    if frappe.db.exists("Sales Order", sales_order):
        frappe.db.sql("""
            UPDATE `tabSales Order` 
            SET `per_delivered` = 100, `status` = "Completed" 
            WHERE `name` = "{sales_order}";
        """.format(sales_order=sales_order))
        frappe.db.commit()
    return
