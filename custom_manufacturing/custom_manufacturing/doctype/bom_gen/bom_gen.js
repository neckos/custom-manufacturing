// Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Gen', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("BOM Gen", "project", function(frm) {
    cur_frm.set_query("bom", function() {
        return {
            "filters": {
                "project": frm.doc.project
            }
        };
    });
});
frappe.ui.form.on("BOM Gen", "generate_items_and_boms",
    function(frm) {
		console.log("test");
		/*
	    //lets use run_serially to be able to show changes normally: 
   		frappe.run_serially([
			() => cur_frm.save(),
   			() => frappe.timeout(1),	
   			() => cur_frm.reload_doc(),	
   			() => frappe.timeout(1),		
   			() => {
				console.log('after timeout');
				//console.log(cur_frm.doc.name);
				///*
		*/
		        frappe.call({
		            "method": "custom_manufacturing.custom_manufacturing.doctype.bom_gen.bom_gen.generate_items_and_boms",
		             args: {
						name: cur_frm.doc.name,
		             },
		            callback: function (r) {
		               console.log(r);
					   $.each(r.message, function(key, value) {
						   console.log(key);
						   console.log(value);
						   frappe.model.set_value("Panel Blueprints", key, "item", value.new_item);
						   frappe.model.set_value("Panel Blueprints", key, "bom", value.new_bom);
					   })
					   //get row:
					   //?
					   //grid_row = cur_frm.fields_dict['panel_blueprints'].grid.grid_rows_by_docname['1cef9011a6'] 
					   //field = frappe.utils.filter_dict(grid_row.docfields, {fieldname: "bom")[0];
					   //?
						//cur_frm.get_field("items").grid.grid_rows[0].doc.price_list_rate = 1
						//cur_frm.get_field("items").grid.grid_rows[0].refresh_field("price_list_rate")
					   
					   //frappe.model.set_value("Panel Blueprints", "1cef9011a6", "Item", "P0001 1W-002 Ārsiena - Māja");
		            }
		        })
		/*
			}
   		]);
		*/
		

});