# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "custom_manufacturing"
app_title = "Custom Manufacturing"
app_publisher = "kaspars.zemiitis@gmail.com"
app_description = "Custom Manufacturing"
app_icon = "octicon octicon-file-directory"
app_color = "Orange"
app_email = "kaspars.zemiitis@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_manufacturing/css/custom_manufacturing.css"

app_include_js = "/assets/js/custom_manufacturing.js"
#app_include_js = "/assets/js/treeview_modul.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_manufacturing/css/custom_manufacturing.css"
# web_include_js = "/assets/custom_manufacturing/js/custom_manufacturing.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "custom_manufacturing.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_manufacturing.install.before_install"
# after_install = "custom_manufacturing.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_manufacturing.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
    "Item": {
        "autoname": "custom_manufacturing.utils.custom_item_autoname"
    },
}

#doc_events = {
#    "Work Order": {
#                "after_insert": "custom_manufacturing.utils.create_work_order_tasks",
# 	}
#}

#jenv = {
#	"methods": {
#		"random_color": ["custom_manufacturing.utils.create_random_color_hex"],
#	}
#}

standard_queries = {
	"Quotation Item": "custom_manufacturing.utils.joined_quotation_item_query"
}

fixtures = ['Multi Doctype Tree Manager', {'doctype': 'Address Template', 'filters': [{'name': 'Latvia'}]}, {'doctype': 'Print Format', 'filters': [{'name': 'Project Offer'}]},{'doctype': 'Custom Script', 'filters': [['name', 'in',['Quotation-Client', 'Quotation Item-Client', 'Project Offer-Client', 'BOM-Client', 'Item-Client', 'Customer-Client', 'Multi Doctype Tree Manager-Client']]]}, {'doctype': 'Custom Field', 'filters': [['dt', 'in',['BOM', 'BOM Item', 'Quotation', 'Quotation Item', 'Item', 'Customer', 'Address', 'Contact', 'Item Group', 'Quotation Master BOM', 'Item Price']]]}, {'doctype': 'Property Setter', 'filters': [['doc_type', 'in',['BOM', 'BOM Item', 'Quotation', 'Quotation Item', 'Item', 'Customer', 'Address', 'Contact', 'Item Group', 'Quotation Master BOM', 'Item Price']]]}, ]

website_route_rules = [{"from_route":"/lala", "to_route": "project_offer_template"},]

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_manufacturing.tasks.all"
# 	],
# 	"daily": [
# 		"custom_manufacturing.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_manufacturing.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_manufacturing.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_manufacturing.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_manufacturing.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_manufacturing.event.get_events"
# }

