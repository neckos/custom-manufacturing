# -*- coding: utf-8 -*-
# Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe import _

class MaterialRequestsToPurchaseInvoicesManager(Document):
	pass


#@frappe.whitelist()
#def update_material_request_item(selected_row_info, for_supplier, warehouse = '', project = ''):

#frappe.get_doc('Purchase Invoice Item', filters={'material_request_item':'dd861af995'})
#frappe.get_all('Purchase Invoice Item', filters={'material_request_item':'dd861af995'}, fields=['name'])
#frappe.get_all('Purchase Invoice Item', filters={'material_request_item':row['mr_item_name']}, fields=['name'])

@frappe.whitelist()
def create_order_document_for_selected_rows(selected_row_info, for_supplier, warehouse = '', project = ''):
	selected_row_info = json.loads(selected_row_info)
	if ['already in pi' for row in selected_row_info if row['order_document'] or frappe.get_all('Purchase Invoice Item', filters={'material_request_item':row['mr_item_name']}, fields=['name'])]:
		frappe.throw(_("Some of selected items are already set in some Purchase Invoice"))
	purchase_invoice = frappe.new_doc("Purchase Invoice")
	purchase_invoice.supplier = for_supplier
	if warehouse:
		purchase_invoice.warehouse = warehouse
	if project:
		purchase_invoice.project = project
	#set info for Purchase Invoice Items:
	for row in selected_row_info:
		purchase_invoice.append('items', {
			'item_code': row['item_code'],
			'item_name': row['item_name'],
			'uom': row['uom'],
			'qty': row['qty'],
			'stock_qty': row['stock_qty'],
			'stock_uom': row['stock_uom'],
			'material_request_item': row['mr_item_name']
		})
	#target.run_method("calculate_billing_amount_for_timesheet")
	purchase_invoice.flags.ignore_permissions = True
	purchase_invoice.run_method("set_missing_values")
	purchase_invoice.insert()
	frappe.db.commit() #othwerwise is not saved in bd (?)
	frappe.msgprint(_("Has been created order document:"))
	frappe.msgprint(purchase_invoice.name)
	frappe.msgprint(_("Reload this document and/or check order document"))
	#update Material Request Items with Purchase Invoice name
	for row in selected_row_info:
		mri = frappe.get_doc('Material Request Item', row['mr_item_name'])
		if mri:
			frappe.db.sql("update `tabMaterial Request Item` set order_document = %s where name=%s", (purchase_invoice.name,mri.name))
			frappe.db.commit() #othwerwise is not saved in bd (?)
			#mri.order_document = purchase_invoice.name
			#mri.save()
			#frappe.msgprint(mri.name)

	
	""""
	doc = frappe.new_doc("Job Card")
	doc.update({
		'work_order': work_order.name,
		'operation': row.operation,
		'workstation': row.workstation,
		'posting_date': nowdate(),
		'for_quantity': qty or work_order.get('qty', 0),
		'operation_id': row.name,
		'bom_no': work_order.bom_no,
		'project': work_order.project,
		'company': work_order.company,
		'wip_warehouse': work_order.wip_warehouse
	})
	
	doc = frappe.get_doc('Work Order', self.get('work_order'))

		for d in doc.required_items:
			if not d.operation:
				frappe.throw(_("Row {0} : Operation is required against the raw material item {1}")
					.format(d.idx, d.item_code))

			if self.get('operation') == d.operation:
				child = self.append('items', {
					'item_code': d.item_code,
					'source_warehouse': d.source_warehouse,
					'uom': frappe.db.get_value("Item", d.item_code, 'stock_uom'),
					'item_name': d.item_name,
					'description': d.description,
					'required_qty': (d.required_qty * flt(self.for_quantity)) / doc.qty
				})
	"""


@frappe.whitelist()
def get_items_from_mr(item_code = False, from_date = False, to_date = False, warehouse = False, project = False, supplier = False, \
	mr_name = False, requested_by = False, from_schedule_date = False, to_schedule_date = False,):
	#return 'some info from backend'
	""" Pull Material Requests that are pending based on criteria selected"""
	mr_filter = item_filter = ""
	if from_date:
		mr_filter += " and mr.transaction_date >= %(from_date)s"
	if to_date:
		mr_filter += " and mr.transaction_date <= %(to_date)s"
	if warehouse:
		mr_filter += " and mr_item.warehouse = %(warehouse)s"
	if project:
		mr_filter += " and mr_item.project = %(project)s"
	if supplier:
		mr_filter += " and mr_item.supplier = %(supplier)s"
	if mr_name:
		mr_filter += " and mr.name = %(mr_name)s"
	if requested_by:
		mr_filter += " and mr.requested_by = %(requested_by)s"
	if from_schedule_date:
		mr_filter += " and mr.schedule_date >= %(from_schedule_date)s"
	if to_schedule_date:
		mr_filter += " and mr.schedule_date <= %(to_schedule_date)s"


	if item_code:
		item_filter += " and mr_item.item_code = %(item_code)s"
	print(mr_filter)
	print(item_filter)
	pending_mr = frappe.db.sql("""
		select 
			mr_item.name as mritemname,
			mr_item.item_code,
			mr_item.item_name,
			mr_item.uom,
			mr_item.qty,
			mr_item.stock_uom,
			mr_item.stock_qty,
			mr_item.warehouse,
			mr_item.project,
			mr_item.supplier,
			mr_item.order_document,
			mr.name, 
			mr.transaction_date,
			mr.requested_by,
			mr.schedule_date
		from 
			`tabMaterial Request` mr,
			`tabMaterial Request Item` mr_item
		where 
			mr_item.parent = mr.name
			and mr.docstatus = 1
			{0} {1}
		""".format(mr_filter, item_filter), {
			"from_date": from_date,
			"to_date": to_date,
			"warehouse": warehouse,
			"project": project,
			"supplier": supplier,
			"item_code": item_code,
			"mr_name": mr_name,
			"requested_by": requested_by,
			"from_schedule_date": from_schedule_date,
			"to_schedule_date": to_schedule_date
		}, as_dict=1)
	return pending_mr or []
	#self.add_mr_in_table(pending_mr)
	#and mr.material_request_type = "Manufacture"et 
	#			"item": fg_item