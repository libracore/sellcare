// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Musterliste"] = {
	"filters": [
{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": new Date(new Date().getFullYear(), new Date().getMonth(), 1),
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
        },
        {
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
        },
         {
			"fieldname":"responsible",
			"label": __("Responsible"),
			"fieldtype": "Data"	
        },
         {
			"fieldname":"item_name",
			"label": __("Item Name"),
			"fieldtype": "Data"
        },
          {
			"fieldname":"follow_up",
			"label": __("Nachfassen"),
			"fieldtype": "Select",
			"options": "\nYes\nNo\nCustomer Representative will do it"
        },
              
	]
};


