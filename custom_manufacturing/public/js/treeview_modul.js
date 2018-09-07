frappe.provide('frappe.ui');
frappe.ui.TreeInModal = class {
	constructor({
		parent, label, icon_set, toolbar, expandable, with_skeleton=1, 	// eslint-disable-line

		args, method, get_label, on_render, on_click 		// eslint-disable-line
	}) {
		$.extend(this, arguments[0]);
		this.setup_treenode_class();
		this.nodes = {};
		this.wrapper = $('<div class="tree">').appendTo(this.parent);
		if(with_skeleton) this.wrapper.addClass('with-skeleton');

		if(!icon_set) {
			this.icon_set = {
				open: 'fa fa-fw fa-folder-open',
				closed: 'fa fa-fw fa-folder',
				leaf: 'octicon octicon-primitive-dot'
			};
		}

		this.setup_root_node();
	}

	get_nodes(value, is_root) {
		var args = Object.assign({}, this.args);
		args.parent = value;
		args.is_root = is_root;

		return new Promise(resolve => {
			frappe.call({
				method: this.method,
				args: args,
				callback: (r) => {
					resolve(r.message);
				}
			});
		});
	}

	get_all_nodes(value, is_root) {
		var args = Object.assign({}, this.args);
		args.parent = value;
		args.is_root = is_root;

		args.tree_method = this.method;

		return new Promise(resolve => {
			frappe.call({
				method: 'frappe.desk.treeview.get_all_nodes',
				args: args,
				callback: (r) => {
					resolve(r.message);
				}
			});
		});
	}

	setup_treenode_class() {
		let tree = this;
		this.TreeNode = class {
			constructor({
				parent, label, parent_label, expandable, is_root, data // eslint-disable-line
			}) {
				$.extend(this, arguments[0]);
				this.loaded = 0;
				this.expanded = 0;
				if(this.parent_label){
					this.parent_node = tree.nodes[this.parent_label];
				}

				tree.nodes[this.label] = this;
				tree.make_node_element(this);
				tree.on_render && tree.on_render(this);
			}
		}
	}

	setup_root_node() {
		this.root_node = new this.TreeNode({
			parent: this.wrapper,
			label: this.label,
			parent_label: null,
			expandable: true,
			is_root: true,
			data: {
				value: this.label
			}
		});
		this.expand_node(this.root_node, false);
	}

	refresh() {
		this.selected_node.parent_node &&
			this.load_children(this.selected_node.parent_node, true);
	}

	make_node_element(node) {
		node.$tree_link = $('<span class="tree-link">')
			.attr('data-label', node.label)
			.data('node', node)
			.appendTo(node.parent);

		node.$ul = $('<ul class="tree-children">')
			.hide().appendTo(node.parent);

		this.make_icon_and_label(node);
		if(this.toolbar) {
			node.$toolbar = this.get_toolbar(node).insertAfter(node.$tree_link);
		}
	}

	add_node(node, data) {
		var $li = $('<li class="tree-node">');

		return new this.TreeNode({
			parent: $li.appendTo(node.$ul),
			parent_label: node.label,
			label: data.value,
			title: data.title,
			expandable: data.expandable,
			data: data
		});
	}

	reload_node(node) {
		this.load_children(node);
	}

	toggle() {
		this.get_selected_node().toggle();
	}

	get_selected_node() {
		return this.selected_node;
	}

	set_selected_node(node) {
		this.selected_node = node;
	}

	load_children(node, deep=false) {
		let value = node.data.value, is_root = node.is_root;

		if(!deep) {
			frappe.run_serially([
				() => {return this.get_nodes(value, is_root);},
				(data_set) => { this.render_node_children(node, data_set); },
				() => { this.set_selected_node(node); }
			]);
		} else {
			frappe.run_serially([
				() => {return this.get_all_nodes(value, is_root);},
				(data_list) => { this.render_children_of_all_nodes(data_list); },
				() => { this.set_selected_node(node); }
			]);
		}
	}

	render_children_of_all_nodes(data_list) {
		data_list.map(d => { this.render_node_children(this.nodes[d.parent], d.data); });
	}

	render_node_children(node, data_set) {
		node.$ul.empty();
		if (data_set) {
			$.each(data_set, (i, data) => {
				var child_node = this.add_node(node, data);
				child_node.$tree_link
					.data('node-data', data)
					.data('node', child_node);
			});
		}

		node.expanded = false;

		// As children loaded
		node.loaded = true;
		this.expand_node(node);
	}

	on_node_click(node) {
		this.expand_node(node);
		//frappe.dom.activate(this.wrapper, node.$tree_link, 'tree-link');
		this.wrapper.find(`.${'tree-link'}.${'active'}`).removeClass('active');
		node.$tree_link.addClass('active');
		if(node.$toolbar) this.show_toolbar(node);
		/*		
		activate: function($parent, $child, common_class, active_class='active') {
			$parent.find(`.${common_class}.${active_class}`).removeClass(active_class);
			$child.addClass(active_class);
		},
		*/
	}

	expand_node(node, click = true) {
		this.set_selected_node(node);

		if(click) {
			this.on_click && this.on_click(node);
		}

		if(node.expandable) {
			this.toggle_node(node);
		}
		this.select_link(node);

		node.expanded = !node.expanded;
		node.parent.toggleClass('opened', node.expanded);
	}

	toggle_node(node) {
		if(node.expandable && this.get_nodes && !node.loaded) {
			return this.load_children(node);
		}

		// expand children
		if(node.$ul) {
			if(node.$ul.children().length) {
				node.$ul.toggle(!node.expanded);
			}

			// open close icon
			if(this.icon_set) {
				node.$tree_link.find('i').removeClass();
				if(!node.expanded) {
					node.$tree_link.find('i').addClass(`${this.icon_set.open} node-parent`);
				} else {
					node.$tree_link.find('i').addClass(`${this.icon_set.closed} node-parent`);
				}
			}
		}
	}

	select_link(node) {
		this.wrapper.find('.selected')
			.removeClass('selected');
		node.$tree_link.toggleClass('selected');
	}

	show_toolbar(node) {
		if(this.cur_toolbar)
			$(this.cur_toolbar).hide();
		this.cur_toolbar = node.$toolbar;
		node.$toolbar.show();
	}

	get_node_label(node) {
		if(this.get_label) {
			return this.get_label(node);
		}
		if (node.title && node.title != node.label) {
			return __(node.title) + ` <span class='text-muted'>(${node.label})</span>`;
		} else {
			return __(node.title || node.label);
		}
	}

	make_icon_and_label(node) {
		let icon_html = '';
		if(this.icon_set) {
			if(node.expandable) {
				icon_html = `<i class="${this.icon_set.closed} node-parent"></i>`;
			} else {
				icon_html = `<i class="${this.icon_set.leaf} node-leaf"></i>`;
			}
		}

		$(icon_html).appendTo(node.$tree_link);
		$(`<a class="tree-label grey h6"> ${this.get_node_label(node)}</a>`).appendTo(node.$tree_link);

		node.$tree_link.on('click', () => {
			setTimeout(() => {this.on_node_click(node);}, 100);
		});
		
		node.$tree_link.on('dblclick', () => {
			setTimeout(() => {console.log("This is double clikc");}, 100);
		});
	}

	get_toolbar(node) {
		let $toolbar = $('<span class="tree-node-toolbar btn-group"></span>').hide();

		Object.keys(this.toolbar).map(key => {
			let obj = this.toolbar[key];
			if(!obj.label) return;
			if(obj.condition && !obj.condition(node)) return;

			var label = obj.get_label ? obj.get_label() : obj.label;
			var $link = $("<button class='btn btn-default btn-xs'></button>")
				.html(label)
				.addClass('tree-toolbar-button ' + (obj.btnClass || ''))
				.appendTo($toolbar);
			$link.on('click', () => {
				obj.click(node);
				this.refresh();
			});
		});

		return $toolbar;
	}
}

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

		this.children_level = opts.children_level;
		
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
		this.tree = new frappe.ui.TreeInModal({
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
		console.log("This is node object:");
		console.log(me);
		/*
		Some variable to check is it single-doctype (Item Group) select or multi-doctype (Item Group and Items)
		if single-doctype then on select node
		*/
		
		console.log('This is select node');
		console.log('children_level:');
		console.log(me.children_level);	
		
		if(me.children_level){
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
					//console.log(r.message);
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
		}
		
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
		console.log("me.doctype:");
		console.log(me.doctype);
		//by default accept that this have to be only tree view
		me.tree_level = me.doctype;
		me.children_level = "";
		//check is this multi-doctype tree case (doctype is in children_level, for example, "Item" is in relationship "Item Group-> Item")
		new Promise(resolve => frappe.call({
			type:"GET",
			method: "frappe.client.get_list",
			args: {
				doctype: "Multi Doctype Tree Manager",
				filters:{children_level: me.doctype},
				fields: ["name", "tree_level", "children_level"]
			},
			callback: resolve
		})).then(r => {
			console.log(r);
			if(r.message){ //if is found, then get tree doctype and children view doctype
				console.log("have response from Multi Doctype Tree Manager");
				console.log(r.message[0]['tree_level']);
				console.log(r.message[0]['children_level']);
				me.tree_level = r.message[0]['tree_level'];
				me.children_level = r.message[0]['children_level'];
			}else{
				console.log("have NO response from Multi Doctype Tree Manager");
			}
			console.log("me.tree_level:");
			console.log(me.tree_level);
			// me.opts.doctype
			//$('<h1>Virsraksts</h1>').appendTo(this.dialog.fields_dict.results.$wrapper);
			var tree_wrapper = this.dialog.fields_dict.tree.$wrapper;
			var options = {
				doctype: me.tree_level, //"Item Group", //me.tree_level,
				children_level: me.children_level,
				parent: $('<div class = "row"></div>').appendTo(tree_wrapper),
				parent_target: me.target,
				dialog:this.dialog,
			};
			frappe.views.trees[options.doctype] = new frappe.views.TreeViewInModal(options);
			//console.log('frappe.views.trees:');
			//console.log(frappe.views.trees);
			//console.log(frappe.views.trees[options.doctype].node_view);
		});

	},
});

