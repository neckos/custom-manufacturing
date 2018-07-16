// Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('The Offer', {
	"offer_description_template": function(frm) {
		console.log("offer_description_template");
		var update_offer_description_details = function(doc, r) {
			$.each(r, function(i, d) {
				console.log(d.category);
				//var row = frappe.model.add_child(doc, "Offer", "offer_description_detail");
				//row.category = d.category;
				//row.detail = d.detail;
				//row.type = d.type;
				//row.display = d.display;
			});
			//refresh_field("offer_description_detail");
		}
		return frappe.call({
						type:"GET",
						method: "custom_manufacturing.custom_manufacturing.doctype.the_offer.the_offer.get_offer_description_details",
						args: {
							"offer_description_template": frm.doc.offer_description_template
						},
						callback: function(r) {

							frappe.model.clear_table(frm.doc, "offer_description_detail");
							if(r.message) {
															console.log(r.message)
								//update_offer_description_details(frm.doc,[r.message]);
								$.each(r.message, function(i, d) {
									console.log(d.detail);
									var row = frappe.model.add_child(frm.doc, "Offer", "offer_description_detail");
									row.category = d.category;
									row.detail = d.detail;
									row.type = d.type;
									row.display = d.display;
								});
								refresh_field("offer_description_detail");
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
