// Copyright (c) 2019-2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Auswertung DB1"] = {
	"filters": [
        {
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
        {
			"fieldname":"item_name",
			"label": __("Item name"),
			"fieldtype": "Data"
		},
        {
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
			"reqd": 1,
			"width": "60px"
        },
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
        }
	]
};
