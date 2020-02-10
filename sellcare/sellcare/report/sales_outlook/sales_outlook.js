// Copyright (c) 2016-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Outlook"] = {
	"filters": [
        {
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
        {
			"fieldname":"item_name",
			"label": __("Item name"),
			"fieldtype": "Data"
		},
        {
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
            "options": "Customer"
		},
        {
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
            "options": "Supplier"
		}
	]
};
