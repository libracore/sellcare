# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def get_available_batches(item_code, warehouse):
    sql_query = """
      SELECT
         `batch_id`, `qty`, `expiry_date` 
      FROM
          (SELECT 
            `tabBatch`.`batch_id`, 
            SUM(`actual_qty`) AS `qty`,
            `tabBatch`.`expiry_date`
          FROM `tabBatch` 
          JOIN `tabStock Ledger Entry` ON `tabBatch`.`batch_id` = `tabStock Ledger Entry`.`batch_no`
          WHERE `tabStock Ledger Entry`.`item_code` = '{item_code}' AND  `tabStock Ledger Entry`.`warehouse` = '{warehouse}'
            AND (`tabBatch`.`expiry_date` >= CURDATE() OR `tabBatch`.`expiry_date` IS NULL)
          GROUP BY `batch_id`
          ORDER BY `tabBatch`.`expiry_date` ASC, `tabBatch`.`creation` ASC) AS `raw`
      WHERE `qty` > 0;
    """.format(item_code=item_code, warehouse=warehouse)    
    data = frappe.db.sql(sql_query, as_dict=1)
    
    return data
