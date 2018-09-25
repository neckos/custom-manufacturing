# -*- coding: utf-8 -*-
# Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BOMGen(Document):
	pass

@frappe.whitelist()
def generate_items_and_boms(name):
    #frappe.msgprint(name)
    bom_gen = frappe.get_doc("BOM Gen", name)
    bom = frappe.get_doc("BOM", bom_gen.bom)
    item = frappe.get_doc("Item", bom.item)
    #get panels info:
    panels = frappe.get_list('Panel Blueprints', filters={'parent':bom_gen.name})
    #each panel will be item with BOM
    l = []
    info = {}
    for panel in panels:
        p = frappe.get_doc("Panel Blueprints", panel.name)
        print(p.name)
        new_item = create_new_item(bom, bom_gen, item, p) #'Ārsiena - Māja'
        new_bom = create_new_bom(new_item, bom, p)
        info[panel.name] = {"new_item" : new_item, "new_bom":new_bom}
    return info
    #b = []
    #for new_item in l:
    #    b.append(create_new_bom(new_item, bom))
    #message = {}
    #return {"new_items":l, "new_boms":b}
        

#create panels:    
@frappe.whitelist()
def create_new_item(bom, bom_gen, item,  panel_info):
    #new item code name will contain different parts:
    item_code = bom_gen.project + " " + panel_info.tot + "-" + panel_info.combination_no + " " + item.name
    #create and return new item name:
    if not frappe.get_all('Item', filters={'name': item_code}, fields=['name']):
        item = frappe.get_doc({
    		'doctype':'Item',
            'item_name':item_code,
            'item_code':item_code,
            'item_group':item.item_group,
            'stock_uom':item.stock_uom,
            'width':panel_info.width,
            'height':panel_info.height,
            'length':panel_info.length,
            'grossa':panel_info.grossa,    
            'neta':panel_info.neta            
        })
        item.insert()
        frappe.db.commit()
        print("created new item")
        return item.name
    else: #or return already existing name
        print("already exist item")
        return item_code #False

@frappe.whitelist()
def create_new_bom(new_item, copy_from_bom, panel):
    #if such BOM does not exist already, then create it
    #if not frappe.get_all('BOM', filters={'name': copy_from_bom}, fields=['name']):
    #    #for new BOM no need for new name (as BOM names are created automatically)
    #bom = frappe.get_doc("BOM", copy_from_bom)
    qty = round((float(panel.height)/1000)*(float(panel.length)/1000),2) #new bom qty is calculated from panel dimensions
    items = []
    if copy_from_bom.items:
        for i in copy_from_bom.items:
            items.append(dict(
                item_code= i.item_code,
                item_name= i.item_name,
                material_embedded_in=i.material_embedded_in,
                base_qty=i.base_qty,
                volume_factor=i.volume_factor,
                reserve_factor=i.reserve_factor,
                qty = round((float(i.qty) * float(qty)),2), #raw material qty has to be multiplied by bom qty 
                stock_uom = i.stock_uom,
                uom = i.uom,
                rate = i.rate
            ))
    new_bom = frappe.get_doc({
		'doctype':'BOM',
		'item':new_item,
        'quantity':float(qty),
        'currency':'EUR',
        'conversion_rate': 1,
        'items':items,
        'project':copy_from_bom.project,
        'type':'Uz ražošanu',
        'country':copy_from_bom.country
    })
    new_bom.insert()
    frappe.db.commit()
    print('created new BOM')
    return new_bom.name
    #else:
    #    print('already exist BOM')
    #    return copy_from_bom.name
    	
        
@frappe.whitelist()
def copy_bom(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc

	def update_status(source, target, parent):
		target.maintenance_type = "Scheduled"

	doclist = frappe.model.mapper.get_mapped_doc("BOM", "BOM-Ārsiena - Māja-002", {"BOM": {"doctype": "BOM",},"BOM Item": {"doctype": "BOM Item",}}, target_doc = None)

	return doclist


"""
  			"postprocess": update_status  
    
    
"""