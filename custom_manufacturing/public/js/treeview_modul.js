frappe.provide('frappe.views.trees');
frappe.views.TreeViewInModal = Class.extend({
	init: function(opts) {
		var me = this;

		this.opts = {};
		this.opts.get_tree_root = true;
		this.opts.show_expand_all = true;
		$.extend(this.opts, opts);
		this.doctype = opts.doctype;
		this.args = {doctype: me.doctype};
		this.page_name = frappe.get_route_str();
		this.get_tree_nodes =  me.opts.get_tree_nodes || "frappe.desk.treeview.get_children";

		//this.get_permissions();
		//this.make_page();
		//this.make_filters();

		if (me.opts.get_tree_root) {
			this.get_root();
		}

		//this.onload();
		//this.set_menu_item();
		//this.set_primary_action();
	},
	get_root: function() {
		var me = this;
		frappe.call({
			method: me.get_tree_nodes,
			args: me.args,
			callback: function(r) {
				if (r.message) {
					me.root_label = r.message[0]["value"];
					console.log(r.message);
					me.make_tree();
				}
			}
		})
	},
	make_tree: function() {
		$(this.parent).find(".tree").remove();
		console.log('this is this:');
		//$('<div class = "row"><div class="col-sm-6 hidden-xs" id="group_tree" style="background-color:grey;height:20px;"></div></div>').appendTo(this.opts.parent);
		var html_parent = this.opts.parent;
		this.tree = new frappe.ui.Tree({
			parent: html_parent, //this.opts.parent, //CUSTOM!!!
			label: this.args[this.opts.root_label] || this.root_label || this.opts.root_label,
			expandable: true,
			args: this.args,
			method: this.get_tree_nodes,
			on_click: (node) => { this.select_node(node); },
		});		
		this.node_view = $('<div class="col-sm-12 hidden-xs" style="background-color:;"></div>').appendTo(html_parent);// CUSTOM!!!  this.opts.results
		//cur_tree = this.tree;
	},
	select_node: function(node) {
		var me = this;		
		//this.wrapper = $('<h1>Here will be results</h1>').appendTo(this.opts.results);
		this.node_view.empty();		
		//get data:
		new Promise(resolve => frappe.call({
			type:"GET",
			method: "custom_manufacturing.utils.get_item_group_items",
			args: {
				"item_group": node.data.value
			},
			callback: resolve
		})).then(r => {
			//show data and add functionality:
			if(r.message) {
				//this.opts.view_template = "items_in_item_groups";
				//$(frappe.render_template('items_in_item_groups', {data:data_template})).appendTo(this.node_view);		//could use render_template but how then add setting back in parent grid?	
				$.each(r.message, function(i, d) {
					var row = $(repl('<div class="row link-select-row">\
						<div class="col-xs-12">\
							<b><a href="#"> %(name)s </a></b></div>\
						</div>', {
							name: d.item_name,
						})).appendTo(me.node_view);
					//add functionality to set picked (via <a>) in grid:
					row.find("a")
						.attr('data-value', d.item_code)
						.click(function () {
							var value = $(this).attr("data-value");
							var $link = this;
							
							if (me.opts.parent_target.is_grid) {
								// set in grid
								me.opts.parent_target.set_in_grid(value);
							} else {
								if (me.opts.parent_target.doctype)
									me.opts.parent_target.parse_validate_and_set_in_model(value);
								else {
									me.opts.parent_target.set_input(value);
									me.opts.parent_target.$input.trigger("change");
								}
								me.opts.dialog.hide();
							}
							return false;
						})
				});		
			}
		});
		
	},	
})

frappe.ui.form.LinkTreeSelector = Class.extend({
	init: function (opts) {
		/* help: Options: doctype, get_query, target */
		$.extend(this, opts);
		var me = this;
		if (this.doctype != "[Select]") {
			frappe.model.with_doctype(this.doctype, function (r) {
				me.make();
			});
		} else {
			this.make();
		}
	},
	make: function () {
		var me = this;
		this.dialog = new frappe.ui.Dialog({
			title: __("Select {0}", [(this.doctype == '[Select]') ? __("value") : __(this.doctype)]),
			fields: [
				{
					fieldtype: "HTML", fieldname: "tree"
				},
			],
		});
		this.dialog.show();
		this.search();
	},
	search: function () {
		var me = this;
		//$('<h1>Virsraksts</h1>').appendTo(this.dialog.fields_dict.results.$wrapper);
		var tree_wrapper = this.dialog.fields_dict.tree.$wrapper;
		var options = {
			doctype: 'Item Group',
			parent: $('<div class = "row"></div>').appendTo(tree_wrapper),
			parent_target: me.target,
			dialog:this.dialog,
		};
		frappe.views.trees[options.doctype] = new frappe.views.TreeViewInModal(options);
		//console.log('frappe.views.trees:');
		//console.log(frappe.views.trees);
		//console.log(frappe.views.trees[options.doctype].node_view);
		
	},
});