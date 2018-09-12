frappe.ui.form.Dashboard = Class.extend({
	init: function(opts) {
		console.log("opts in Dashboard:");
		console.log(opts);
		$.extend(this, opts);
		//hide form-dashboard section 
		//(code from https://github.com/frappe/frappe/blob/develop/frappe/public/js/frappe/form/layout.js)
			//this.frm.$wrapper.find(".form-dashboard").addClass("empty-section"); //this do not hide section Title
		this.frm.$wrapper.find(".form-dashboard").hide();
	},
	//functions that are used in other places (have to be defined):
	refresh: function() {},
	after_refresh: function() {},
	set_headline_alert: function(text, indicator_color) {
		if (!indicator_color) {
			indicator_color = 'orange';
		}
		if(text) {
			this.set_headline(`<div><span class="indicator ${indicator_color}">${text}</span></div>`);
		} else {
			this.clear_headline();
		}
	},
	set_headline: function(html) {
		this.frm.layout.show_message(html);
	},
	clear_headline: function() {
		this.frm.layout.show_message();
	},
	add_comment: function(text, alert_class, permanent) {
		var me = this;
		this.set_headline_alert(text, alert_class);
		if(!permanent) {
			setTimeout(function() {
				me.clear_headline();
			}, 10000);
		}
	},
	clear_comment: function() {
		this.clear_headline();
	},
})