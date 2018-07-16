// Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt


frappe.ui.form.on('Project Offer', {
	read: function(frm) {
		console.log("offer_description_template_name");
		/*
		var update_offer_description_details = function(doc, r) {
			$.each(r.message, function(i, d) {
				console.log(d.detail);
				var row = frappe.model.add_child(frm.doc, "Project Offer", "offer_description_template_items");
				row.category = d.category;
				row.detail = d.detail;
				row.type = d.type;
				row.display = d.display;
			});
			refresh_field("offer_description_template_items");
		}
		*/
		return frappe.call({
						type:"GET",
						method: "custom_manufacturing.custom_manufacturing.doctype.project_offer.project_offer.get_offer_description_details",
						args: {
							"offer_description_template_name": frm.doc.offer_description_template_name
						},
						callback: function(r) {
							console.log(r.message)
							frappe.model.clear_table(frm.doc, "project_offer_description_details");
							
							if(r.message) {								
								$.each(r.message, function(i, d) {
									console.log(d.detail);
									var row = frappe.model.add_child(frm.doc, "Offer Description Detail", "project_offer_description_details");
									row.category = d.category;
									row.detail = d.detail;
									row.type = d.type;
									row.display = d.display;
								});
								frm.refresh_field("project_offer_description_details");
								cur_frm.save()
								
							}
							
							
							//frappe.model.clear_table(doc, "accounts");
							//if(r.message) {
							//	update_jv_details(doc, r.message);
								//}
							//cur_frm.set_value("is_opening", "Yes")
						}
					})

	}
});
