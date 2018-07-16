# -*- coding: utf-8 -*-
# Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

@frappe.whitelist()
def get_offer_description_details(offer_description_template):
	return frappe.get_all('Offer Description Template Items', filters={'parent': offer_description_template}, fields=['idx','name' ,'category', 'detail', 'type', 'display'], order_by='idx')