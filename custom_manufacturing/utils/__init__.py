import frappe
from frappe import _
from frappe.utils.csvutils import getlink
from six import string_types
import json
import random
import frappe
from frappe import _
from frappe.utils.csvutils import getlink
from six import string_types
import json
import random

from frappe.utils import (cint, cstr, flt, formatdate, get_timestamp, getdate, now_datetime, random_string, strip)

@frappe.whitelist()
def check_multi_doctype_tree(doctype):
	return frappe.db.sql(
		"""
			select name, tree_level, children_level
			from `tabMulti Doctype Tree Manager`
		    where (tree_level=%s or children_level=%s) order by name asc
		""", (doctype, doctype), as_dict=1) or ''

@frappe.whitelist()
def check_is_set_item_group_parent_item(item_group, item_code):
	#item_group = "Raw Material"
	return frappe.db.sql(
		"""
			select item_code, item_name, item_group
			from `tabItem`
		    where (item_group=%s and is_group_parent_item=1 and item_code<>%s) order by item_name asc
		""", (item_group, item_code), as_dict=1) or ''


@frappe.whitelist()
def custom_item_autoname(doctype, event_name):
	from erpnext.stock.doctype.item.item import Item
	def autoname(self):
		if self.naming_by == 'Naming Series':
		#frappe.db.get_default("item_naming_by") == "Naming Series":
			if self.variant_of:
				if not self.item_code:
					template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
					self.item_code = make_variant_item_code(self.variant_of, template_item_name, self)
			else:
				from frappe.model.naming import set_name_by_naming_series
				set_name_by_naming_series(self)
				self.item_code = self.name
		elif not self.item_code:
			frappe.msgprint(_("Item Code is mandatory because Item is not automatically numbered"), raise_exception=1)

		self.item_code = strip(self.item_code)
		self.name = self.item_code
	Item.autoname = autoname
	"""
	if frappe.db.get_default("item_naming_by") == "Naming Series":
		if self.variant_of:
			if not self.item_code:
				template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
				self.item_code = make_variant_item_code(self.variant_of, template_item_name, self)
		else:
			from frappe.model.naming import set_name_by_naming_series
			set_name_by_naming_series(self)
			self.item_code = self.name
	elif not self.item_code:
		msgprint(_("Item Code is mandatory because Item is not automatically numbered"), raise_exception=1)

	self.item_code = strip(self.item_code)
	self.name = self.item_code
	"""


@frappe.whitelist()
def get_item_group_items(item_group):
	#item_group = "Raw Material"
	return frappe.db.sql(
		"""
			select item_code, item_name
			from `tabItem`
		    where item_group=%s order by item_name asc
		""", (item_group), as_dict=1)

@frappe.whitelist()
def get_frappe_render():
	return frappe.render_template(template, context)

@frappe.whitelist()
def get_alternative_items(item_code):
	return frappe.db.sql(
		"""
			select alternative_item_code as alt_item, alternative_item_name as name
			from `tabItem Alternative`
		    where item_code=%s order by idx
		""", (item_code), as_dict=1)

@frappe.whitelist()
def create_random_color_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


@frappe.whitelist()
def create_work_order_tasks2():
    return 'in process'
    
def joined_quotation_item_query(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import build_match_conditions, get_filters_cond

	match_conditions = build_match_conditions("Quotation Item")
	match_conditions = "and {}".format(match_conditions) if match_conditions else ""
	
	if filters:
		filter_conditions = get_filters_cond(doctype, filters, [])
		match_conditions += "{}".format(filter_conditions)
		#frappe.msgprint(match_conditions)

	txt = "%{}%".format(txt)
	return frappe.db.sql("""select name, item_code, master_item
		from `tabQuotation Item`
		where {key} like %(txt)s
			{match_conditions}
		limit %(start)s, %(page_len)s""".format(key=searchfield, match_conditions=match_conditions),
			dict(start=start, page_len=page_len, txt=txt))

@frappe.whitelist()
def create_work_order_tasks(doc, method):
    #frappe.msgprint("This is create tasks" + doc.name)
    #return doc.name
    #frappe.msgprint(str(frappe.as_json(doc)))
    items = []
    ##for item in doc.required_items:
        #frappe.msgprint(item.item_code)
        ##items.append(item.item_code)
    #frappe.msgprint(items)
    bom_list = [doc.bom_no]
    #frappe.msgprint(bom_list)
    #get bom of work order:
    bom = frappe.get_doc("BOM", doc.bom_no)
    #take from bom only 'services' items:
    if bom.items:
        for i in bom.items:
            item = frappe.get_doc("Item", i.item_code)
            if item.item_group == "Services":
                items.append(dict(
                    item_code= i.item_code,
                    qty = i.qty, #raw material qty has to be multiplied by bom qty 
                    stock_uom = i.uom,
                    uom = i.uom,
                    rate = i.rate
                )) # stock_qty = float(i.qty),
    tasks = []
    for item in items:
        task = save_in_db_as_task(item, bom, doc.name)
        tasks.append(getlink("Task", task.name) + " " + str(task.subject))
    frappe.msgprint(_("Task created:") + "\n <br>" + "\n <br>".join(tasks))                
                
    '''
    operations = frappe.db.sql(
    """
	select 
		bo.item as finished_item, bomop.bom_item_code, bomop.operation, bomop.description, bomop.workstation, bomop.idx,
		bomop.base_hour_rate as hour_rate, bomop.time_in_mins, 
		'Pending' as status, bomop.parent as bom
	from
		`tabBOM Operation` bomop
    left join
         `tabBOM` bo on bomop.parent = bo.name
	where
		 bomop.parent in (%s) order by bomop.idx
    """     % ", ".join(["%s"]*len(bom_list)), tuple(bom_list), as_dict=1)
    #frappe.msgprint(operations)
    
    tasks = []
    for operation in operations:
        for i in range(doc.qty):
            task = save_in_db_as_task(operation, doc, str(i+1))
            tasks.append(getlink("Task", task.name) + " " + str(task.subject))
    frappe.msgprint(_("Task created:") + "\n <br>" + "\n <br>".join(tasks))
    '''

@frappe.whitelist()      
def save_in_db_as_task(item_obj, bom_obj, work_order_name):
    task = frappe.new_doc("Task")
    task.project = bom_obj.project
    subject = bom_obj.item_name + " | " + item_obj['item_code']
    task.update({"subject": subject,
         "status": "Open",
         "work_order": work_order_name,
         #"production_order": production_order.name,
         #"bom": production_order.bom_no,
         #"raw_material":operation.bom_item_code,
         #"production_operation": operation.operation,
         #"expected_time": round(operation.time_in_mins/60,2),
         #"created_from_production_order":1, #this is only for mapping purpose with timesheet (used in timesheet js) 
         #"quantity_order_number":sequence_no,
         #"exp_start_date": t.start_date,
         #"exp_end_date": t.end_date,
         #"description": t.description,
    })
    task.save(ignore_permissions = True)
    #frappe.msgprint(subject)
    return task
    
@frappe.whitelist()
def make_quotation_from_bom(source_name, target_doc=None):

	#no easy way how to set source doc value in mapped docs child item? 
	#can't be used as contains source doc (BOM) and target doc (Quotation), but no old Quotation
	#def postprocess(source, doc):
	
	#can't be used as has no target_parent???!
	#def update_item(source, target, source_parent):
		#source - BOM Item
		#target - Quotation Item
		#source_parent BOM
		#master_item = frappe.get_value("Quotation Master BOM",  source_parent.last_master_bom_get_items, 'item')
		#target.master_item = source_parent.last_master_bom_get_items

	from frappe.model.mapper import get_mapped_doc

	#target_doc @erpnext.utils.map_current_doc is cur_frm (called from Quotation) ->  frappe.call | method: 'frappe.model.mapper.map_docs' | "source_names": opts.source_name, | "target_doc": cur_frm.doc,
	if isinstance(target_doc, string_types):
		target_doc_temp = frappe.get_doc(json.loads(target_doc))
	#frappe.msgprint(target_doc)
	master_item = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'item')
	master_qty = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'qty')
	master_color = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'color_picker')
	#if form was not saved then last_master_bom_get_items was new and therefore no values for mastet_item and master_qty
	if not master_item or not master_qty:
		frappe.throw(_("You must save before getting items for this Master BOM Item"))        

	doc = get_mapped_doc("BOM", source_name, {
		"BOM": {
			"doctype": "Quotation", #doc will be Quotation
			#"validation": {
			#	#"docstatus": ["=", 1]
			#}
		},
		"BOM Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"rate": "price_list_rate",
				"qty":"factor"
			},
	        #"postprocess":update_item
		}
	}, target_doc, ) #postprocess
	#set master items for Quotation Item
	for item in doc.items:
		#frappe.msgprint(item.item_code)
		item_doc = frappe.get_doc('Item', item.item_code)
		if not item.master_item:
			item.update({'master_item':master_item})
			item.update({'qty':float(master_qty*item.factor)})
			item.update({'color_picker':master_color})
			if item_doc:
				#frappe.msgprint('having item_doc')
				item.update({'conductivity':item_doc.conductivity})
				item.update({'peculiar_mass':item_doc.peculiar_mass})
				item.update({'factor_rez':item_doc.factor_rez})
				if item_doc.thickness:
					#frappe.msgprint(str(item_doc.thickness))  
					#frappe.msgprint(str(master_qty))  
					m3 = round((item_doc.thickness*master_qty),2)                 
					item.update({'m3':m3})
					item.update({'thickness':item_doc.thickness})
					if item_doc.conductivity:
						resistance = round((float(item_doc.thickness)/float(item_doc.conductivity)), 4) 
						item.update({'resistance':resistance})
						#we can set all resistances, in case of joined items these will be reseted
						item.update({'heat_zone_1_res':resistance})
						item.update({'heat_zone_2_res':resistance})
						item.update({'heat_zone_3_res':resistance})
						item.update({'heat_zone_4_res':resistance})
						item.update({'resistance_calculated':resistance})
				factor_rez = float(1) + round(float(item_doc.factor_rez)/100, 4) #for example 30% will be 1+(30/100) => 1+0.3=> 1.3
				mass = round((item.factor * master_qty * factor_rez * item_doc.peculiar_mass),4)/factor_rez
				item.update({'mass':mass})
	return doc

		
@frappe.whitelist()
def make_boms_from_quotations(quotation):
	q_doc = frappe.get_doc('Quotation',quotation)
	items = q_doc.items
	#get master_items
	master_items = []
	for item in items:
		master_items.append(item.master_item)
	master_items = list(set(master_items)) #get uniques (converting list to set and back to list)
	#for each master_item create BOM
	for master_item in master_items:
		#create new or update BOM
		#toDO - remove BOM if not found master_item anymore in any BOM of this Quotation
		if frappe.get_list('BOM', filters={'quotation': quotation, 'item': master_item}, fields=['name']):
			#toDO - update BOM
			print('Have to update BOM') #update
			frappe.msgprint("Have to update BOM")
		else:
			#print('Create new BOM') #create new
			frappe.msgprint("Create new BOM")
			target = frappe.new_doc("BOM")
			target.item = master_item
			target.quotation = quotation
			target.project = q_doc.project
			target.type = "Tāmes"
			for item in items:
				if item.master_item == master_item:
					#frappe.msgprint(item.item_code)
					target.append('items',{'item_code':item.item_code, 'qty': item.factor,'uom': item.uom, 'rate':item.rate})
					#ToDo - fix needed! Get master_qty from Quotation Master Item not by calculating
					master_qty = round(float(item.qty/item.factor),2)
			target.quantity = master_qty
			target.save(ignore_permissions=True)
			frappe.db.commit()
	
	"""
	from frappe.model.mapper import get_mapped_doc
	from frappe.model.mapper import get_mapped_doc
	q_doc = frappe.get_doc('Quotation',quotation)
	items = q_doc.items
	master_items = []
	for item in items:
		master_items.append(item.master_item)
	master_items = list(set(master_items)) #get uniques (converting list to set and back to list)
	for master_item in master_items:
		target = frappe.new_doc("BOM")
		target.item = master_item
		target.item_code = master_item
		#for item in items:
		#    if item.master_item == master_item:
		#target.append("items", 
		return get_mapped_doc("Quotation", quotation, {
    		"Quotation": {
    			"doctype": "BOM",
    			#"validation": {
    			#	#"docstatus": ["=", 1]
    			#}
				#"field_map": {
				#    "rate": "base_rate",
				#},
    		},
            "Quotation Item": {
				"doctype": "BOM Item",
				"validation": {
					"master_item": ["like", master_item]
				}
				#"field_map": {
				#    "rate": "base_rate",
				#    "name": "time_log_batch",
				#    "total_hours": "qty",
				#},
			}
		}, target) 
		#)

	return target

	doc = get_mapped_doc("BOM", source_name, {
		"BOM": {
			"doctype": "Quotation",
			#"validation": {
			#	#"docstatus": ["=", 1]
			#}
		},
		"BOM Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"rate": "price_list_rate"
			},
		}
	}, target_doc)
	return doc
    
    
    target = frappe.new_doc("Sales Invoice")
    target.append("entries", get_mapped_doc("Time Log Batch", source_name, {
        "Time Log Batch": {
            "doctype": "Sales Invoice Item",
            "field_map": {
                "rate": "base_rate",
                "name": "time_log_batch",
                "total_hours": "qty",
            },
            "postprocess": update_item
        }
    }))
frappe.ui.form.on("Quotation", {
	refresh: function(frm) {
			frm.add_custom_button(__('Estimate BOMs'), function() {
				erpnext.utils.map_current_doc({
					method: "custom_manufacturing.utils.make_quotation_from_bom",
					source_doctype: "BOM",
					target: frm,
					date_field: "posting_date",
					setters: {
						project: frm.doc.project || undefined,
					},
					get_query_filters: {
						docstatus: 1
					}
				})
			}, __("Create"));
	}, 
});
"""
from frappe.utils import (cint, cstr, flt, formatdate, get_timestamp, getdate, now_datetime, random_string, strip)

@frappe.whitelist()
def check_multi_doctype_tree(doctype):
	return frappe.db.sql(
		"""
			select name, tree_level, children_level
			from `tabMulti Doctype Tree Manager`
		    where (tree_level=%s or children_level=%s) order by name asc
		""", (doctype, doctype), as_dict=1) or ''

@frappe.whitelist()
def check_is_set_item_group_parent_item(item_group, item_code):
	#item_group = "Raw Material"
	return frappe.db.sql(
		"""
			select item_code, item_name, item_group
			from `tabItem`
		    where (item_group=%s and is_group_parent_item=1 and item_code<>%s) order by item_name asc
		""", (item_group, item_code), as_dict=1) or ''


@frappe.whitelist()
def custom_item_autoname(doctype, event_name):
	from erpnext.stock.doctype.item.item import Item
	def autoname(self):
		if self.naming_by == 'Naming Series':
		#frappe.db.get_default("item_naming_by") == "Naming Series":
			if self.variant_of:
				if not self.item_code:
					template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
					self.item_code = make_variant_item_code(self.variant_of, template_item_name, self)
			else:
				from frappe.model.naming import set_name_by_naming_series
				set_name_by_naming_series(self)
				self.item_code = self.name
		elif not self.item_code:
			frappe.msgprint(_("Item Code is mandatory because Item is not automatically numbered"), raise_exception=1)

		self.item_code = strip(self.item_code)
		self.name = self.item_code
	Item.autoname = autoname
	"""
	if frappe.db.get_default("item_naming_by") == "Naming Series":
		if self.variant_of:
			if not self.item_code:
				template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
				self.item_code = make_variant_item_code(self.variant_of, template_item_name, self)
		else:
			from frappe.model.naming import set_name_by_naming_series
			set_name_by_naming_series(self)
			self.item_code = self.name
	elif not self.item_code:
		msgprint(_("Item Code is mandatory because Item is not automatically numbered"), raise_exception=1)

	self.item_code = strip(self.item_code)
	self.name = self.item_code
	"""


@frappe.whitelist()
def get_item_group_items(item_group):
	#item_group = "Raw Material"
	return frappe.db.sql(
		"""
			select item_code, item_name
			from `tabItem`
		    where item_group=%s order by item_name asc
		""", (item_group), as_dict=1)

@frappe.whitelist()
def get_frappe_render():
	return frappe.render_template(template, context)

@frappe.whitelist()
def get_alternative_items(item_code):
	return frappe.db.sql(
		"""
			select alternative_item_code as alt_item, alternative_item_name as name
			from `tabItem Alternative`
		    where item_code=%s order by idx
		""", (item_code), as_dict=1)

@frappe.whitelist()
def create_random_color_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


@frappe.whitelist()
def create_work_order_tasks2():
    return 'in process'
    
def joined_quotation_item_query(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import build_match_conditions, get_filters_cond

	match_conditions = build_match_conditions("Quotation Item")
	match_conditions = "and {}".format(match_conditions) if match_conditions else ""
	
	if filters:
		filter_conditions = get_filters_cond(doctype, filters, [])
		match_conditions += "{}".format(filter_conditions)
		#frappe.msgprint(match_conditions)

	txt = "%{}%".format(txt)
	return frappe.db.sql("""select name, item_code, master_item
		from `tabQuotation Item`
		where {key} like %(txt)s
			{match_conditions}
		limit %(start)s, %(page_len)s""".format(key=searchfield, match_conditions=match_conditions),
			dict(start=start, page_len=page_len, txt=txt))

@frappe.whitelist()
def create_work_order_tasks(doc, method):
    #frappe.msgprint("This is create tasks" + doc.name)
    #return doc.name
    #frappe.msgprint(str(frappe.as_json(doc)))
    items = []
    ##for item in doc.required_items:
        #frappe.msgprint(item.item_code)
        ##items.append(item.item_code)
    #frappe.msgprint(items)
    bom_list = [doc.bom_no]
    #frappe.msgprint(bom_list)
    #get bom of work order:
    bom = frappe.get_doc("BOM", doc.bom_no)
    #take from bom only 'services' items:
    if bom.items:
        for i in bom.items:
            item = frappe.get_doc("Item", i.item_code)
            if item.item_group == "Services":
                items.append(dict(
                    item_code= i.item_code,
                    qty = i.qty, #raw material qty has to be multiplied by bom qty 
                    stock_uom = i.uom,
                    uom = i.uom,
                    rate = i.rate
                )) # stock_qty = float(i.qty),
    tasks = []
    for item in items:
        task = save_in_db_as_task(item, bom, doc.name)
        tasks.append(getlink("Task", task.name) + " " + str(task.subject))
    frappe.msgprint(_("Task created:") + "\n <br>" + "\n <br>".join(tasks))                
                
    '''
    operations = frappe.db.sql(
    """
	select 
		bo.item as finished_item, bomop.bom_item_code, bomop.operation, bomop.description, bomop.workstation, bomop.idx,
		bomop.base_hour_rate as hour_rate, bomop.time_in_mins, 
		'Pending' as status, bomop.parent as bom
	from
		`tabBOM Operation` bomop
    left join
         `tabBOM` bo on bomop.parent = bo.name
	where
		 bomop.parent in (%s) order by bomop.idx
    """     % ", ".join(["%s"]*len(bom_list)), tuple(bom_list), as_dict=1)
    #frappe.msgprint(operations)
    
    tasks = []
    for operation in operations:
        for i in range(doc.qty):
            task = save_in_db_as_task(operation, doc, str(i+1))
            tasks.append(getlink("Task", task.name) + " " + str(task.subject))
    frappe.msgprint(_("Task created:") + "\n <br>" + "\n <br>".join(tasks))
    '''

@frappe.whitelist()      
def save_in_db_as_task(item_obj, bom_obj, work_order_name):
    task = frappe.new_doc("Task")
    task.project = bom_obj.project
    subject = bom_obj.item_name + " | " + item_obj['item_code']
    task.update({"subject": subject,
         "status": "Open",
         "work_order": work_order_name,
         #"production_order": production_order.name,
         #"bom": production_order.bom_no,
         #"raw_material":operation.bom_item_code,
         #"production_operation": operation.operation,
         #"expected_time": round(operation.time_in_mins/60,2),
         #"created_from_production_order":1, #this is only for mapping purpose with timesheet (used in timesheet js) 
         #"quantity_order_number":sequence_no,
         #"exp_start_date": t.start_date,
         #"exp_end_date": t.end_date,
         #"description": t.description,
    })
    task.save(ignore_permissions = True)
    #frappe.msgprint(subject)
    return task
    
@frappe.whitelist()
def make_quotation_from_bom(source_name, target_doc=None):

	#no easy way how to set source doc value in mapped docs child item? 
	#can't be used as contains source doc (BOM) and target doc (Quotation), but no old Quotation
	#def postprocess(source, doc):
	
	#can't be used as has no target_parent???!
	#def update_item(source, target, source_parent):
		#source - BOM Item
		#target - Quotation Item
		#source_parent BOM
		#master_item = frappe.get_value("Quotation Master BOM",  source_parent.last_master_bom_get_items, 'item')
		#target.master_item = source_parent.last_master_bom_get_items

	from frappe.model.mapper import get_mapped_doc

	#target_doc @erpnext.utils.map_current_doc is cur_frm (called from Quotation) ->  frappe.call | method: 'frappe.model.mapper.map_docs' | "source_names": opts.source_name, | "target_doc": cur_frm.doc,
	if isinstance(target_doc, string_types):
		target_doc_temp = frappe.get_doc(json.loads(target_doc))
	#frappe.msgprint(target_doc)
	master_item = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'item')
	master_qty = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'qty')
	master_color = frappe.get_value("Quotation Master BOM", target_doc_temp.last_master_bom_get_items, 'color_picker')
	#if form was not saved then last_master_bom_get_items was new and therefore no values for mastet_item and master_qty
	if not master_item or not master_qty:
		frappe.throw(_("You must save before getting items for this Master BOM Item"))        

	doc = get_mapped_doc("BOM", source_name, {
		"BOM": {
			"doctype": "Quotation", #doc will be Quotation
			#"validation": {
			#	#"docstatus": ["=", 1]
			#}
		},
		"BOM Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"rate": "price_list_rate",
				"qty":"factor"
			},
	        #"postprocess":update_item
		}
	}, target_doc, ) #postprocess
	#set master items for Quotation Item
	for item in doc.items:
		#frappe.msgprint(item.item_code)
		item_doc = frappe.get_doc('Item', item.item_code)
		if not item.master_item:
			item.update({'master_item':master_item})
			item.update({'qty':float(master_qty*item.factor)})
			item.update({'color_picker':master_color})
			if item_doc:
				#frappe.msgprint('having item_doc')
				item.update({'conductivity':item_doc.conductivity})
				item.update({'peculiar_mass':item_doc.peculiar_mass})
				item.update({'factor_rez':item_doc.factor_rez})
				if item_doc.thickness:
					#frappe.msgprint(str(item_doc.thickness))  
					#frappe.msgprint(str(master_qty))  
					m3 = round((item_doc.thickness*master_qty),2)                 
					item.update({'m3':m3})
					item.update({'thickness':item_doc.thickness})
					if item_doc.conductivity:
						resistance = round((float(item_doc.thickness)/float(item_doc.conductivity)), 4) 
						item.update({'resistance':resistance})
						#we can set all resistances, in case of joined items these will be reseted
						item.update({'heat_zone_1_res':resistance})
						item.update({'heat_zone_2_res':resistance})
						item.update({'heat_zone_3_res':resistance})
						item.update({'heat_zone_4_res':resistance})
						item.update({'resistance_calculated':resistance})
				factor_rez = float(1) + round(float(item_doc.factor_rez)/100, 4) #for example 30% will be 1+(30/100) => 1+0.3=> 1.3
				mass = round((item.factor * master_qty * factor_rez * item_doc.peculiar_mass),4)/factor_rez
				item.update({'mass':mass})
	return doc

		
@frappe.whitelist()
def make_boms_from_quotations(quotation):
	q_doc = frappe.get_doc('Quotation',quotation)
	items = q_doc.items
	#get master_items
	master_items = []
	for item in items:
		master_items.append(item.master_item)
	master_items = list(set(master_items)) #get uniques (converting list to set and back to list)
	#for each master_item create BOM
	for master_item in master_items:
		#create new or update BOM
		#toDO - remove BOM if not found master_item anymore in any BOM of this Quotation
		if frappe.get_list('BOM', filters={'quotation': quotation, 'item': master_item}, fields=['name']):
			#toDO - update BOM
			print('Have to update BOM') #update
			frappe.msgprint("Have to update BOM")
		else:
			#print('Create new BOM') #create new
			frappe.msgprint("Create new BOM")
			target = frappe.new_doc("BOM")
			target.item = master_item
			target.quotation = quotation
			target.project = q_doc.project
			target.type = "Estimate"
			for item in items:
				if item.master_item == master_item:
					#frappe.msgprint(item.item_code)
					target.append('items',{'item_code':item.item_code, 'qty': item.factor,'uom': item.uom, 'rate':item.rate})
					#ToDo - fix needed! Get master_qty from Quotation Master Item not by calculating
					master_qty = round(float(item.qty/item.factor),2)
			target.quantity = master_qty
			target.save(ignore_permissions=True)
			frappe.db.commit()
	
	"""
	from frappe.model.mapper import get_mapped_doc
	from frappe.model.mapper import get_mapped_doc
	q_doc = frappe.get_doc('Quotation',quotation)
	items = q_doc.items
	master_items = []
	for item in items:
		master_items.append(item.master_item)
	master_items = list(set(master_items)) #get uniques (converting list to set and back to list)
	for master_item in master_items:
		target = frappe.new_doc("BOM")
		target.item = master_item
		target.item_code = master_item
		#for item in items:
		#    if item.master_item == master_item:
		#target.append("items", 
		return get_mapped_doc("Quotation", quotation, {
    		"Quotation": {
    			"doctype": "BOM",
    			#"validation": {
    			#	#"docstatus": ["=", 1]
    			#}
				#"field_map": {
				#    "rate": "base_rate",
				#},
    		},
            "Quotation Item": {
				"doctype": "BOM Item",
				"validation": {
					"master_item": ["like", master_item]
				}
				#"field_map": {
				#    "rate": "base_rate",
				#    "name": "time_log_batch",
				#    "total_hours": "qty",
				#},
			}
		}, target) 
		#)

	return target

	doc = get_mapped_doc("BOM", source_name, {
		"BOM": {
			"doctype": "Quotation",
			#"validation": {
			#	#"docstatus": ["=", 1]
			#}
		},
		"BOM Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"rate": "price_list_rate"
			},
		}
	}, target_doc)
	return doc
    
    
    target = frappe.new_doc("Sales Invoice")
    target.append("entries", get_mapped_doc("Time Log Batch", source_name, {
        "Time Log Batch": {
            "doctype": "Sales Invoice Item",
            "field_map": {
                "rate": "base_rate",
                "name": "time_log_batch",
                "total_hours": "qty",
            },
            "postprocess": update_item
        }
    }))
frappe.ui.form.on("Quotation", {
	refresh: function(frm) {
			frm.add_custom_button(__('Estimate BOMs'), function() {
				erpnext.utils.map_current_doc({
					method: "custom_manufacturing.utils.make_quotation_from_bom",
					source_doctype: "BOM",
					target: frm,
					date_field: "posting_date",
					setters: {
						project: frm.doc.project || undefined,
					},
					get_query_filters: {
						docstatus: 1
					}
				})
			}, __("Create"));
	}, 
});
"""