// Copyright (c) 2019-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Dispo-Report"] = {
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
		}
	]
};
