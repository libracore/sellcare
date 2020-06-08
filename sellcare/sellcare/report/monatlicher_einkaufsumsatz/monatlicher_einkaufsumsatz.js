// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monatlicher Einkaufsumsatz"] = {
	"filters": [
        {
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"default": (new Date()).getFullYear()
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
	]
};
