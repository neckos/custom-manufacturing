// Copyright (c) 2016, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Parent Wise Balance"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		/*{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		*/
		/*
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		*/
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse"
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
		
		/*{
			"fieldname": "show_variant_attributes",
			"label": __("Show Variant Attributes"),
			"fieldtype": "Check"
		},
		*/
	],
	//for v9 (in v10 is used datables!?)
	"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
		/*
		console.log('row');
		console.log(row);
		console.log('cell');
		console.log(cell);
		console.log('columnDef');
		console.log(columnDef);
		console.log('dataContext');
		console.log(dataContext);
		console.log('value');
		console.log(value);	
		*/
		if (columnDef.df.fieldname=="item_code") {
			value = dataContext.item_code;
			columnDef.df.is_tree = true;
		}

		value = default_formatter(row, cell, value, columnDef, dataContext);

		/*
		if (!dataContext.parent_account && dataContext.based_on != 'project') {
			var $value = $(value).css("font-weight", "bold");
			if (dataContext.warn_if_negative && dataContext[columnDef.df.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}
		
		*/

		if (!dataContext.item_parent_code) {
		   value = `<span style='color:black!important;font-weight:bold'>${value}</span>`;
		}
		
		return value;
	},

	"tree": true,
	"name_field": "item_code",
	"parent_field": "item_parent_code",
	"initial_depth": 1,
	
	onload: function(report) {

	}
}



