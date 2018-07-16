# -*- coding: utf-8 -*-
# Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Offer(Document):
	pass
    
@frappe.whitelist()
def get_offer_description_details(offer_description_template):
	#""" 
	#accounts = frappe.db.sql_list("""select
	#		idx, name from `tabOffer Description Template Items`
	#	where
	#		parent=%s
	#	order by name idx""", frappe.db.escape(offer_description_template))
	#return [{"category": a, "balance": get_balance_on(a)} for a in accounts]
	#"""
	return frappe.get_all('Offer Description Template Items', filters={'parent': offer_description_template}, fields=['idx','name' ,'category', 'detail', 'type', 'display'], order_by='idx')
