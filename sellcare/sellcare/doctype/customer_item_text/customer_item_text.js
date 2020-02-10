// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Item Text', {
    before_save(frm) {
        cur_frm.set_value("title", frm.doc.customer_name + " - " + frm.doc.item_code);
    }
});
