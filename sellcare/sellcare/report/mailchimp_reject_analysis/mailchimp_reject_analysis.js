// Copyright (c) 2019-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MailChimp Reject Analysis"] = {
    "filters": [
        {
            "fieldname":"date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
     ]
};
