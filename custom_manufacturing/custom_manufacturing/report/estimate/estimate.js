// Copyright (c) 2016, kaspars.zemiitis@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Estimate"] = {
	//console.log('beofre'),
	"filters": [
		{
			"fieldname":"quotation",
			"label":__("Quotation"),
			"fieldtype":"Link",
			"options":"Quotation",
			"reqd": 1
		}, 
	],
	/*
	//"formatter": erpnext.financial_statements.formatter,
	"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
		//"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
		console.log('inside report formatter');		
			if (columnDef.df.fieldname=="item") {
				value = dataContext.item_name;

                columnDef.df.is_tree = true;	
			}
			//Debugging purposes:
            console.log("row:"+ String(row));
			console.log("cell: \n"+String(cell));
			console.log("value: \n"+String(value));
			console.log("columnDef: \n"+JSON.stringify(columnDef));
			console.log("dataContext: \n"+JSON.stringify(dataContext));
			console.log("default_formatter: \n"+String(default_formatter));
			
			value = default_formatter(row, cell, value, columnDef, dataContext);
            //add some style (bold..) for parent:
			if (!dataContext.parent) {
				var $value = $(value).css("font-weight", "bold");
				value = $value.wrap("<p></p>").parent().html();
			}else{
				//add some style to childelements:
				var $value = $(value).css("font-style", "italic");
				value = $value.wrap("<p></p>").parent().html();
				
			}
			return value;
		},
		"tree": true,
		"name_field": "item",
		"parent_field": "parent",
		"initial_depth": 2,
		*/
}