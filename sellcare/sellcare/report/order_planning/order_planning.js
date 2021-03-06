// Copyright (c) 2016-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Order Planning"] = {
	"filters": [
        {
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		}, 
		{
			"fieldname":"hide_samples",
			"label": __("Hide samples"),
			"fieldtype": "Check",
			"default": 1
		},
	]
};
