// Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt
frappe.ui.form.on('Material Requests To Purchase Invoices Manager', {
	onload: function(frm) {
		//hide Delete and Add Row buttons:
		cur_frm.fields_dict['mr_items'].grid.wrapper.find(".grid-add-row, .grid-add-multiple-rows").addClass('hide');
		cur_frm.fields_dict['mr_items'].grid.remove_rows_button.hide()
	},
	get_items_from_mr: function(frm) {
		console.log('this is get items');
			new Promise(resolve => frappe.call({
				type:"GET",
				method: "custom_manufacturing.custom_manufacturing.doctype.material_requests_to_purchase_invoices_manager.material_requests_to_purchase_invoices_manager.get_items_from_mr",
				args: {
					"item_code": frm.doc.item_code,
					"from_date": frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"warehouse": frm.doc.warehouse,
					"project": frm.doc.project,
					"supplier": frm.doc.supplier,
					"mr_name": frm.doc.mr_name,
					"requested_by": frm.doc.requested_by,
					"from_schedule_date": frm.doc.from_schedule_date,
					"to_schedule_date": frm.doc.to_schedule_date
				},
				callback: resolve
			})).then(r => {
				frappe.model.clear_table(frm.doc, "mr_items");
				//console.log(r.message);
				if(r.message) {
					$.each(r.message, function(i, d) {
						//console.log(d);
						var row = frappe.model.add_child(frm.doc, "Material Requests To Purchase Invoices Manager Items", "mr_items");
						row.mr_item_name = d.mritemname;
						row.item_code = d.item_code;
						row.item_name = d.item_name;
						row.uom = d.uom;
						row.qty = d.qty;
						row.stock_uom = d.stock_uom;
						row.stock_qty = d.stock_qty;
						row.warehouse = d.warehouse;
						row.project = d.project;
						row.supplier = d.supplier;
						row.order_document = d.order_document;
						row.material_request = d.name;
					});
					frm.refresh_field("mr_items");
					//Button 'Add Row' is shown after refresh_field, so lets hide it
					//cur_frm.fields_dict['mr_items'].grid.wrapper.find(".grid-add-row, .grid-add-multiple-rows").addClass('hide');
					
					//to hide check box for row	that has already been added into order document			
					frm.doc.mr_items.forEach(function(item){
						if (item.order_document) {
							console.log('This has order document');
							//disable/hide/remove in DOM
							cur_frm.fields_dict['mr_items'].grid.grid_rows[item.idx-1].wrapper.find('.grid-row-check').remove(); //prop("disabled", true); //remove();//.empty(); //hide()
							//remove in doc by setting cur_frm.fields_dict['childtable'].grid.grid_rows[n].doc.__checked = 0
							cur_frm.fields_dict['mr_items'].grid.grid_rows_by_docname[item.name].select(false);
						}else{
							console.log('This has no order doc');
						}
					});
				}else{
					frappe.msgprint(__('Nothing found'))
				}

		
			});
		
	},
	create_order_document_for_selected_rows: function(frm) {
		//lets diselect items that have already order_document		
		///*
		frappe.run_serially([
			() => cur_frm.set_select_to_false({frm:frm}),
			() => frappe.timeout(0.3),
			() => cur_frm.create_order_document({frm:frm}),
		]);
		//*/
		
		/*
		a) take info from 
		*/
	}
});

//reset selected in doc:
cur_frm.set_select_to_false = function(frm){
	cur_frm.doc.mr_items.forEach(function(item){
		if (item.order_document) {
			//remove in doc by setting cur_frm.fields_dict['childtable'].grid.grid_rows[n].doc.__checked = 0
			cur_frm.fields_dict['mr_items'].grid.grid_rows_by_docname[item.name].select(false);
		}else{
			console.log('This has no order doc');
		}
	});
}

//create order document:
cur_frm.create_order_document = function(frm){
	var selected = cur_frm.fields_dict['mr_items'].grid.get_selected_children();
	if(selected.length > 0){
		if(!cur_frm.doc.for_supplier){
			frappe.throw(__('Please, select Supplier in below field'))
		}else{
			new Promise(resolve => frappe.call({
				type:"GET",
				method: "custom_manufacturing.custom_manufacturing.doctype.material_requests_to_purchase_invoices_manager.material_requests_to_purchase_invoices_manager.create_order_document_for_selected_rows",
				args: {
					"selected_row_info": selected,
					"for_supplier": cur_frm.doc.for_supplier,
					"warehouse": cur_frm.doc.warehouse,
					"project": cur_frm.doc.project,
				},
				callback: resolve
			})).then(r => {
				console.log(r.message);
				/*
				frappe.model.clear_table(frm.doc, "mr_items");
				//console.log(r.message);
				if(r.message) {
					$.each(r.message, function(i, d) {
						//console.log(d);
						var row = frappe.model.add_child(frm.doc, "Material Requests To Purchase Invoices Manager Items", "mr_items");
						row.mr_item_name = d.mritemname;
						row.item_code = d.item_code;
						row.item_name = d.item_name;
						row.uom = d.uom;
						row.qty = d.qty;
						row.stock_uom = d.stock_uom;
						row.stock_qty = d.stock_qty;
						row.warehouse = d.warehouse;
						row.project = d.project;
						row.supplier = d.supplier;
						row.order_document = d.order_document;
						row.material_request = d.name;
					});
					frm.refresh_field("mr_items");
					//Button 'Add Row' is shown after refresh_fiel, so lets hide it
					cur_frm.fields_dict['mr_items'].grid.wrapper.find(".grid-add-row, .grid-add-multiple-rows").addClass('hide');	
			
				}else{
					frappe.msgprint(__('Nothing found'))
				}
				*/

			});
		}
	}else{
		frappe.throw(__('Please, select some row'))
	}
}


