from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now
#from erpnext.stock.utils import update_included_uom_in_report
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition

from six import iteritems
import pprint

def execute(filters=None):
	pp = pprint.PrettyPrinter(indent=4)
	if not filters: filters = {}

	#if item or warehouse not selected then select all from `tabStock Ledger Entry` (up to 500'000 records)
	validate_filters(filters)

	#? allow to filter by differen uom ?
	include_uom = filters.get("include_uom")

	columns = get_columns()

	#filter (if set) by - items by item_code, item_brand, item_group:
	items = get_items(filters)
	print('items:')
	pp.pprint(items)
	#get stock ledger entries by items and filters
	#!!!! Add here sum by parent?
	sle = get_stock_ledger_entries(filters, items)
	print('sle:')
	pp.pprint(sle)

	# if no stock ledger entry found return
	if not sle:
		return columns, []

	#get value for each item in companys warehouse iwb_map = {('T', 'Ārsiena - Māja', 'Finished Goods - T'):{'bal_qty': 130.0, 'bal_val': 7800.0,'in_qty': 130.0,'in_val': 7800.0,'opening_qty': 0.0,'opening_val': 0.0,'out_qty': 0.0,'out_val': 0.0,'val_rate': 60.0}}
	iwb_map = get_item_warehouse_map(filters, sle)
	print('iwb_map:')
	pp.pprint(iwb_map)

	#get item details: item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom, ucd.conversion_factor (if asked) .. and variant attribute values (if asked)
	#example: {'Ārsiena - Māja': {'brand': None,'description': 'Ārsiena - Māja','item_group': 'Products','item_name': 'Ārsiena - Māja','name': 'Ārsiena - Māja','stock_uom': 'm2'}}
	item_map = get_item_details(items, sle, filters)
	print('item_map:')
	pp.pprint(item_map)

	#take reorder levels from `tabItem Reorder`
	#example: (keys??? item_code+warehouse)
	"""
	{
		'Ārsiena - MājaFinished Goods - T': 
		{	
			'parent': 'Ārsiena - Māja',
			'warehouse': 'Finished Goods - T',
			'warehouse_reorder_level': 100.0,
			'warehouse_reorder_qty': 200.0
		},
		'Ārsiena - MājaStores - T': 
		{
			'parent': 'Ārsiena - Māja',
			'warehouse': 'Stores - T',
			'warehouse_reorder_level': 60.0,
			'warehouse_reorder_qty': 100.0
		}
	}
	"""

	item_reorder_detail_map = get_item_reorder_details(item_map.keys())
	print('item_reorder_detail_map:')
	pp.pprint(item_reorder_detail_map)


	data = []
	conversion_factors = []

	list_of_parents_dict = []
	parents_dict = {}
	#join item_warehouse_amounts with item_details and item_reorder information
	#for (company, item, warehouse) in sorted(iwb_map):
	for (company, warehouse, item) in sorted(iwb_map):
		if item_map.get(item):
			#qty_dict = iwb_map[(company, item, warehouse)]
			qty_dict = iwb_map[(company, warehouse, item)]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

			report_data = [item, item_map[item]["item_name"],
				item_map[item]["item_group"],
				item_map[item]["brand"],
				item_map[item]["description"],
				item_map[item]["item_parent_code"],
				item_map[item]["item_parent_name"],
				warehouse,
				item_map[item]["stock_uom"], qty_dict.opening_qty,
				qty_dict.opening_val, qty_dict.in_qty,
				qty_dict.in_val, qty_dict.out_qty,
				qty_dict.out_val, qty_dict.bal_qty,
				qty_dict.bal_val, qty_dict.val_rate,
				item_reorder_level,
				item_reorder_qty,
				company
			]

			#if has parent then set/ sum values
			if item_map[item]["item_parent_code"]:
				#key = (company, item_map[item]["item_parent_code"], warehouse)
				key = (company, warehouse, item_map[item]["item_parent_code"])
				#print(key)
				if parents_dict.get(key): #if is already set (in some previous record)
					#then add values:
					parents_dict[key]['opening_qty']+= qty_dict.opening_qty
					parents_dict[key]['opening_val']+= qty_dict.opening_val
					parents_dict[key]['in_qty']+= qty_dict.in_qty
					parents_dict[key]['in_val']+= qty_dict.in_val
					parents_dict[key]['out_qty']+= qty_dict.out_qty
					parents_dict[key]['out_val']+= qty_dict.out_val
					parents_dict[key]['bal_qty']+= qty_dict.bal_qty
					parents_dict[key]['bal_val']+= qty_dict.bal_val
				else:#if is not set in parents_dict then insert values (values of first child-item):
					parents_dict[key] = parents_dict.get(key, \
					{'item_code':item_map[item]["item_parent_code"], \
					'item_name':item_map[item]["item_parent_name"], \
					'item_group':'', \
					'brand': '', \
					'description': '', \
					'item_parent_code': '', \
					'item_parent_name': '', \
					'warehouse': warehouse, \
					'stock_uom': '', \
					'opening_qty': qty_dict.opening_qty, \
					'opening_val': qty_dict.opening_val, \
					'in_qty': qty_dict.in_qty, \
					'in_val': qty_dict.in_val, \
					'out_qty': qty_dict.out_qty, \
					'out_val': qty_dict.out_val, \
					'bal_qty': qty_dict.bal_qty, \
					'bal_val': qty_dict.bal_val, \
					'val_rate': '', \
					'reorder_level': '', \
					'reorder_qty': '', \
					'company': company, \
					'indent': 0, \
					}) 
			"""
			#if has parent then set/ sum values
			if item_map[item]["item_parent_code"]:
				key = (company, item_map[item]["item_parent_code"], warehouse)
				if parents_dict.get(item_map[item]["item_parent_code"]): #if is already set (in some previous record)
					#then add values:
					parents_dict[item_map[item]["item_parent_code"]]['opening_qty']+= qty_dict.opening_qty
					parents_dict[item_map[item]["item_parent_code"]]['opening_val']+= qty_dict.opening_val
					parents_dict[item_map[item]["item_parent_code"]]['in_qty']+= qty_dict.in_qty
					parents_dict[item_map[item]["item_parent_code"]]['in_val']+= qty_dict.in_val
					parents_dict[item_map[item]["item_parent_code"]]['out_qty']+= qty_dict.out_qty
					parents_dict[item_map[item]["item_parent_code"]]['out_val']+= qty_dict.out_val
					parents_dict[item_map[item]["item_parent_code"]]['bal_qty']+= qty_dict.bal_qty
					parents_dict[item_map[item]["item_parent_code"]]['bal_val']+= qty_dict.bal_val
				else:#if is not set in parents_dict then insert values (values of first child-item):
					parents_dict[item_map[item]["item_parent_code"]] = parents_dict.get(item_map[item]["item_parent_code"], \
					{'item_code':item_map[item]["item_parent_code"], \
					'item_name':item_map[item]["item_parent_name"], \
					'item_group':'', \
					'brand': '', \
					'description': '', \
					'item_parent_code': '', \
					'item_parent_name': '', \
					'warehouse': warehouse, \
					'stock_uom': '', \
					'opening_qty': qty_dict.opening_qty, \
					'opening_val': qty_dict.opening_val, \
					'in_qty': qty_dict.in_qty, \
					'in_val': qty_dict.in_val, \
					'out_qty': qty_dict.out_qty, \
					'out_val': qty_dict.out_val, \
					'bal_qty': qty_dict.bal_qty, \
					'bal_val': qty_dict.bal_val, \
					'val_rate': '', \
					'reorder_level': '', \
					'reorder_qty': '', \
					'company': company, \
					'indent': 0, \
					}) 
			"""

			if filters.get('show_variant_attributes', 0) == 1:
				variants_attributes = get_variants_attributes()
				report_data += [item_map[item].get(i) for i in variants_attributes]

			if include_uom:
				conversion_factors.append(item_map[item].conversion_factor)
			print('report_data:')
			pp.pprint(report_data)
			data.append(report_data)

	if filters.get('show_variant_attributes', 0) == 1:
		columns += ["{}:Data:100".format(i) for i in get_variants_attributes()]

	#ToDo: check what does this do exactly:
	update_included_uom_in_report(columns, data, include_uom, conversion_factors)

	print('parents_dict:')
	pp.pprint(parents_dict)

	print('---data:')
	list_of_dicts = []
	for d in data:
		print(d)
		#key = (d[20], d[5], d[7]) #(company, item_parent_code, warehouse)
		key = (d[20], d[7], d[5]) #(company, item_parent_code, warehouse)
		if d[5] and parents_dict.get(key):#if has parent and parent's information is still in parents_dict (has not yet popped out)
			list_of_dicts.append(parents_dict.pop(key)) #add parent record to list_of_dicts and remove (with pop) from parents_dict to ensure it is appended only once to list_of_dicts
		indent = 1 if d[5] else 0
		#append current record:
		list_of_dicts.append({\
			'item_code': d[0], \
			'item_name': d[1], \
			'item_group': d[2], \
			'brand': d[3], \
			'description': d[4], \
			'item_parent_code': d[5], \
			'item_parent_name': d[6], \
			'warehouse': d[7], \
			'stock_uom': d[8], \
			'opening_qty': d[9], \
			'opening_val': d[10], \
			'in_qty': d[11], \
			'in_val': d[12], \
			'out_qty': d[13], \
			'out_val': d[14], \
			'bal_qty': d[15], \
			'bal_val': d[16], \
			'val_rate': d[17], \
			'reorder_level': d[18], \
			'reorder_qty': d[19], \
			'company': d[20], \
			'indent': indent, \
		})


	return columns, list_of_dicts #data


def get_columns():
	columns = [
		{"label": _("Item"), "fieldname": "item_code", "width": 100}, # "fieldtype": "Link", "options": "Item",
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		#{"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 90},
		#{"label": _("Description"), "fieldname": "description", "width": 140},
		#{"label": _("Parent Code"), "fieldname": "item_parent_code", "width": 100},
		#{"label": _("Parent Name"), "fieldname": "item_parent_name", "width": 140},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 100},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
		{"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Opening Value"), "fieldname": "opening_val", "fieldtype": "Float", "width": 110},
		{"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("In Value"), "fieldname": "in_val", "fieldtype": "Float", "width": 80},
		{"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float", "width": 80, "conversion_factortible": "qty"},
		{"label": _("Out Value"), "fieldname": "out_val", "fieldtype": "Float", "width": 80},
		{"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Balance Value"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 100},
		{"label": _("Valuation Rate"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 90, "convertible": "rate"},
		{"label": _("Reorder Level"), "fieldname": "reorder_level", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Reorder Qty"), "fieldname": "reorder_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 100}
	]

	"""
	columns = [{
		"fieldname": "item_gro",
		"label": _("Account"),
		"fieldtype": "Link",
		"options": "Account",
		"width": 300
	}]

	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Currency",
				"width": 150
			})
	"""
	return columns

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items]))
			#CONONDRUM - why not working due to ' ?! .format(', '.join([frappe.db.escape(i, percent=False) for i in items]))

	#check is from_date; to sql statement add to_date and warehouses from filters 
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.name""" %
		(item_conditions_sql, conditions), as_dict=1)


def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters.get("to_date"))
		#CONONDRUM - why not working, due to ' ?! conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse",
			filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)

	return conditions

def get_item_warehouse_map(filters, sle):
	#NB!customized: changed key from company, item, warehouse to company, warehouse, item as we wan't to sort by warehouses
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	for d in sle:
		#key = (d.company, d.item_code, d.warehouse)
		key = (d.company, d.warehouse, d.item_code)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})

		#qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]
		qty_dict = iwb_map[(d.company, d.warehouse, d.item_code)]

		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date:
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if qty_diff > 0:
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
	print('iwb_map before sorted:')
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(iwb_map)
	iwb_map = filter_items_with_no_transactions(iwb_map)

	return iwb_map

def filter_items_with_no_transactions(iwb_map):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]

		no_transactions = True
		float_precision = cint(frappe.db.get_default("float_precision")) or 3
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if filters.get("include_uom"):
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom='%s'" \
			% frappe.db.escape(filters.get("include_uom"))

	item_codes = ', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])
	#customized: added parent_item info
	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item_parent.name as item_parent_code, item_parent.item_name as item_parent_name, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item
		left join
			`tabItem` item_parent on item.parent_item = item_parent.name
			{cf_join}
		where
			item.name in ({item_codes}) and ifnull(item.disabled, 0) = 0
	""".format(cf_field=cf_field, cf_join=cf_join, item_codes=item_codes), as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	if filters.get('show_variant_attributes', 0) == 1:
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

	return item_details

def get_variant_values_for(items):
	'''Returns variant values for items.'''
	attribute_map = {}
	for attr in frappe.db.sql('''select parent, attribute, attribute_value
		from `tabItem Variant Attribute` where parent in (%s)
		''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
			attribute_map.setdefault(attr['parent'], {})
			attribute_map[attr['parent']].update({attr['attribute']: attr['attribute_value']})

	return attribute_map

def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql("""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])), as_dict=1)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

#copied from v11's, v12's stock.utils.py
def update_included_uom_in_report(columns, result, include_uom, conversion_factors):
	if not include_uom or not conversion_factors:
		return

	convertible_cols = {}
	for col_idx in reversed(range(0, len(columns))):
		col = columns[col_idx]
		if isinstance(col, dict) and col.get("convertible") in ['rate', 'qty']:
			convertible_cols[col_idx] = col['convertible']
			columns.insert(col_idx+1, col.copy())
			columns[col_idx+1]['fieldname'] += "_alt"
			if convertible_cols[col_idx] == 'rate':
				columns[col_idx+1]['label'] += " (per {})".format(include_uom)
			else:
				columns[col_idx+1]['label'] += " ({})".format(include_uom)

	for row_idx, row in enumerate(result):
		new_row = []
		for col_idx, d in enumerate(row):
			new_row.append(d)
			if col_idx in convertible_cols:
				if conversion_factors[row_idx]:
					if convertible_cols[col_idx] == 'rate':
						new_row.append(flt(d) * conversion_factors[row_idx])
					else:
						new_row.append(flt(d) / conversion_factors[row_idx])
				else:
					new_row.append(None)

		result[row_idx] = new_row