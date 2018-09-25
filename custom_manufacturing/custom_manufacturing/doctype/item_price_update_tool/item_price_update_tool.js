frappe.ui.form.on("Item Price Update Tool",{ 
	"new_rate": function(frm) {
		cur_frm.get_items();
		console.log('touching new_rate');
	},
	"item_group": function(frm) {
		console.log('touching item_group');	
		cur_frm.get_items();
	},
	"parent_item": function(frm) {
		cur_frm.get_items();
		console.log('touching parent_item');
	},
	"price_list": function(frm) {
		cur_frm.get_items();
		console.log('touching price_list');
	},
	"recalculate_prices_by_item_group_hour_price": function(frm) {
		cur_frm.get_items();
		console.log('touching recalculate_prices_by_item_group_hour_price');
	},
	"onload" : function(frm) {
		console.log('onload');
		cur_frm.disable_save();
		//cur_frm.set_value("item_group", "");
		//cur_frm.set_value("parent_item", "");
		//cur_frm.set_value("price_list", "");
		//cur_frm.set_value("new_rate", "");
		//frappe.model.clear_table(cur_frm.doc, "items");
		//refresh_field("items");
	},
	"refresh" : function(frm) {
		console.log('refresh');
		//show only these items that are type of parent item:
		cur_frm.set_query("parent_item", function() {
			if(frm.doc.item_group) {
				return {
					"filters": {
						"is_group_parent_item": 1,
						"item_group": cur_frm.doc.item_group,
					}
				};
			}else{
				return {
					"filters": {
						"is_group_parent_item": 1,
					}
				}
			}
	    });
		//show only these groups that are leafs:
		cur_frm.set_query("item_group", function() {
			return {
				"filters": {
					"is_group": 0,
				}
			};
	    });				
	},
	"update":function(frm){
		console.log('staring update..');
		cur_frm.update_item_prices();
	},

});

frappe.ui.form.on("Item Price Update Tool Items",{ 
	view_versions: function(frm, doctype, name) {
		//console.log(doctype);
		//console.log(name);
		//console.log(locals[doctype][name]['item_price'])
		frappe.route_options = {
			docname: locals[doctype][name]['item_price']
		};
		frappe.set_route("List", "Version");
	},
})

cur_frm.get_items = function() {
	console.log('inside get_items function');
	frappe.model.clear_table(cur_frm.doc, "items");
	refresh_field("items");
	if(cur_frm.doc.recalculate_prices_by_item_group_hour_price == 0){
		var recalculate_prices_by_item_group_hour_price = '';
	}else{
		var recalculate_prices_by_item_group_hour_price = 'Hour' ;		
	}
	if(cur_frm.doc.price_list || cur_frm.doc.item_group || cur_frm.doc.parent_item){ //if at least one filter is selected then get prices
		console.log("Has enough filters");
		new Promise(resolve => frappe.call({
			method: 'custom_manufacturing.utils.get_item_prices',
			freeze: true,
			args: {
				price_list: cur_frm.doc.price_list,
				item_group: cur_frm.doc.item_group,
				parent_item: cur_frm.doc.parent_item,
				recalculate_by_hour_rate: recalculate_prices_by_item_group_hour_price 
			},
			callback: resolve
		})).then(r => {
			var items  = r.message;
			console.log('filtered items:');
			console.log(items);
			if(items){
				$.each(items || [], function(i, d) {
					 var new_row = cur_frm.add_child("items");
					 new_row.item_code = d.item_code;
					 new_row.item_name = d.item_name;
					 new_row.rate_old = d.price_list_rate;
					 new_row.rate_new = cur_frm.doc.new_rate;
					 new_row.price_list = d.price_list;
					 new_row.item_group = d.item_group;
					 new_row.parent_item_code = d.parent_item;
					 new_row.item_price = d.item_price;
					 new_row.conversion_factor = d.conversion_factor;
					 new_row.uom = d.uom;
				});
			}
			refresh_field("items")		
		}); //end of Promise then
	}
}

cur_frm.update_item_prices = function() {
	console.log('inside update_item_prices function');
	console.log('Will do update_item_prices for items:');
	console.log(cur_frm.doc.items);
	new Promise(resolve => frappe.call({
		method: 'custom_manufacturing.utils.update_item_prices',
		freeze: true,
		args: {
			items: cur_frm.doc.items,
		},
		callback: resolve
	})).then(r => {
		console.log(r.message);
		cur_frm.get_items();
		/*
		frappe.model.clear_table(cur_frm.doc, "items");
		var items  = r.message;
		console.log('filtered items:');
		console.log(items);
		if(items){
			$.each(items || [], function(i, d) {
				 var new_row = cur_frm.add_child("items");
				 new_row.item_code = d.item_code;
				 new_row.item_name = d.item_name;
				 new_row.rate_old = d.price_list_rate;
				 new_row.rate_new = cur_frm.doc.new_rate;
				 new_row.price_list = d.price_list;
				 new_row.item_group = d.item_group;
				 new_row.parent_item_code = d.parent_item;
			});
		}
		refresh_field("items")	
		*/	
	}); //end of Promise then
}