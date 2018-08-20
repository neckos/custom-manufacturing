// Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt


frappe.ui.form.on('Project Offer', {
	refresh: function(frm) {
		//frm.disable_save();
		//frm.page.clear_indicator();
		//set_primary_action
		frm.page.set_secondary_action(__('Print'), () => {
			let url = "/api/method/custom_manufacturing.custom_manufacturing.doctype.project_offer.project_offer.print_project_offer_pdf";
			open_url_post(url, {"doc": frm.doc}, true);
		});
		doctype = 'Customer';
		frappe.dynamic_link = {doc: frm.doc, fieldname: doctype.toLowerCase(), doctype: doctype};
		frm.set_query('contact_person', erpnext.queries.contact_query);
	},
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
									row.sub_detail = d.sub_detail;
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

	},
	get_master_items_from_estimate: function(frm) {
		/*
		return frappe.call({
		    method: 'frappe.client.get_list',
		    args: {
		        'doctype': 'Quotation Master BOM',
		        'filters': {"parent": frm.doc.estimate},
		        'fields': [
		            'item'
		        ]
		    },
			callback: function(res){
					if (res.message){ console.log(res.message); }
			}
			
		});
		*/	
		/* delay helper in promises https://stackoverflow.com/questions/38956121/how-to-add-delay-to-promise-inside-then  */
		function sleeper(ms) {
		  return function(x) {
		    return new Promise(resolve => setTimeout(() => resolve(x), ms));
		  };
		}
		
		new Promise(resolve => frappe.call({
		    method: 'custom_manufacturing.custom_manufacturing.doctype.project_offer.project_offer.get_master_items_from_estimate',
		    args: {
		        'estimate': cur_frm.doc.estimate
		    },
			callback: resolve
		})).then(r => {
			console.log('first then');
			//var embedded_in_values  = r.message;
			console.log('master items:');
			console.log(r.message);
			if(r.message) {
				frappe.model.clear_table(frm.doc, "project_offer_master_bom_list");								
				$.each(r.message, function(i, d) {
					console.log(d.item);
					var row = frappe.model.add_child(frm.doc, "Project Offer Master Bom List", "project_offer_master_bom_list");
					row.item = d.item;
				});
				frm.refresh_field("project_offer_master_bom_list");
				//cur_frm.save()
				
			}
			
		});
		///*
		new Promise(resolve => frappe.call({
		    method: 'custom_manufacturing.custom_manufacturing.doctype.project_offer.project_offer.get_raw_items_from_estimate',
		    args: {
		        'estimate': cur_frm.doc.estimate
		    },
			callback: resolve
		})).then(r => {
			console.log('second then');
			//var embedded_in_values  = r.message;
			console.log('raw items:');
			console.log(r.message);
			if(r.message) {
				frappe.model.clear_table(frm.doc, "project_offer_technical_raw_material_list");									
				$.each(r.message, function(i, d) {
					console.log(d.item_code);
					var row = frappe.model.add_child(frm.doc, "Project Offer Technical Raw Material List", "project_offer_technical_raw_material_list");
					row.item = d.item_code;
					row.master_item = d.master_item;
					row.material_embedded_in_types = d.material_embedded_in;
				});
				frm.refresh_field("project_offer_technical_raw_material_list");			
			}
			
		}).then(() => {cur_frm.save();console.log('after save');}).then(sleeper(1000)).then(() => {console.log('before scroll');frappe.utils.scroll_to(cur_frm.$wrapper.find("[data-fieldname='get_master_items_from_estimate']"), true);})
		
		//*/
		/*
			
		console.log("offer_description_template_name");
		frappe.call({
			"method": "frappe.client.get_values",
			"args": {
				"doctype": "Quotation Master BOM",
				"filters": {"parent": cur_frm.doc.estimate},
				"fieldname": ["name"]
			}, 
			callback: function(r) { 
			}
		});
		
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
		/*
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
									row.sub_detail = d.sub_detail;
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
		})*/
	},
	
	update_raw_material_pdf_locations_from_master_items: function(frm) {
		/* delay helper in promises https://stackoverflow.com/questions/38956121/how-to-add-delay-to-promise-inside-then  */
		function sleeper(ms) {
		  return function(x) {
		    return new Promise(resolve => setTimeout(() => resolve(x), ms));
		  };
		}
		
		new Promise(resolve => {
				//console.log(frm.doc.project_offer_master_bom_list);
				//console.log('resolve');
				$.each(cur_frm.doc.project_offer_technical_raw_material_list, function(index, row){
					//console.log(row['master_item']);
					$.each(cur_frm.doc.project_offer_master_bom_list, function(index_master, row_master){
						if(row_master.item == row.master_item){
							console.log(row_master.pdf_location);
							cur_frm.doc.project_offer_technical_raw_material_list[index].pdf_location = row_master.pdf_location;
						}
					});
				});
				frm.refresh_field("project_offer_technical_raw_material_list");
				return resolve();				
			}
		).then(() => {cur_frm.save();console.log('after save');}).then(sleeper(1000)).then(() => {console.log('before scroll');frappe.utils.scroll_to(cur_frm.$wrapper.find("[data-fieldname='update_raw_material_pdf_locations_from_master_items']"), true);})
	},
	
	test_scroll: function(frm){
		// delay helper in promises https://stackoverflow.com/questions/38956121/how-to-add-delay-to-promise-inside-then 
		function sleeper(ms) {
		  return function(x) {
		    return new Promise(resolve => setTimeout(() => resolve(x), ms));
		  };
		}
		///*
		//new Promise(() => {console.log('promise');}).then(()=>console.log("then");) //.then(()=>console.log('then');)
		new Promise(resolve => {console.log('promise'); return resolve();}).then(sleeper(1000)).then(()=>{console.log('then');})
		//frappe.utils.scroll_to(cur_frm.$wrapper.find("[data-fieldname='get_master_items_from_estimate']"), true);
		//*/
	}
	//*/
});
