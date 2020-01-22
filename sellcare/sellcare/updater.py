# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def cleanup_languages():
    # this function will remove languages after migrate
    print("Removing unnecessary languages...")
    sql_query = """DELETE FROM `tabLanguage` WHERE `language_code` NOT IN ('it', 'fr', 'en-US', 'en', 'fr');"""
    frappe.db.sql(sql_query, as_dict=1)
    return
