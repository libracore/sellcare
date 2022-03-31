frappe.ui.form.on('Sales Invoice', {
	on_submit(frm) {
        // store CoGS
        frappe.call({
            'method': 'sellcare.sellcare.utils.store_cogs',
            'args': {
                'sinv': frm.doc.name
            }
        });
    }
});
        
