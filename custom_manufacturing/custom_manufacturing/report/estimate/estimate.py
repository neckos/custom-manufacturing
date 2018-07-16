# Copyright (c) 2013, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        return [],[]
    columns = get_columns()
    data = []
    records = get_data(filters)
    #return records
    ### WHAT DOES MEAN ALL THIS COMMENT BELOW ???
    #To be able to have the same names in table (slickgrid view) for parent fields and childfields then for relations are used
    #..fields, for example, 'item' and that means that for parent will have to be one name and for children another (for example, children is 'item'
    #but parent 'item-parent'). But field 'item_name' for parent will be named the same as for children item_name='item'. And in JavaScript:
    """
	if (columnDef.df.fieldname=="item") {
		value = dataContext.item_name;
        ...
	}
    """
    #not working if using list style:
    #data.append([record['item'], record['project'],record['production_order'], record['bom_name'], record['qty'], record['uom'], record['item_name'], record['parent']])
    #ok if useing dictionary style:
    #data.append({"item":"item1-child","item_name":"item1-name", "project":"SB/3743","production_order":"PRO-00026", "bom":"BOM-SB/3743-002", "qty":"1","uom":"kg","parent":"item1-parent"})
    
    #use data from get_data(), uncomment for cycle below:
    for record in records:
       # print(record)
        data.append({\
                    "item":record['item'],\
                    "item_name":record['item_name'],\
                    "factor":record['factor'],\
                    "uom":record['uom'],\
                    "price_list_rate":record['price_list_rate'],\
                    "rate":round(record['rate'],2),\
                    "qty": float(record['qty']),\
                    "amount": round(float(record['amount']),2),\
                    "parent":record['parent'],\
                    "material_embedded_in":record['material_embedded_in'],\
                    "material_embedded_in_markup":record['material_embedded_in_markup'],\
                    "material_embedded_in_markup_amount":record['material_embedded_in_markup_amount'],\
                    "factory_markup":record['factory_markup'],\
                    "factory_markup_amount":record['factory_markup_amount'],\
                    "construction_markup":record['construction_markup'],\
                    "construction_markup_amount":record['construction_markup_amount'],\
                    "delivery_markup":record['delivery_markup'],\
                    "thickness":record['thickness'],\
                    "peculiar_mass":record['peculiar_mass'],\
                    "factor_rez":record['factor_rez'],\
                    "conductivity":record['conductivity'],\
                    "m3":record['m3'],\
                    "mass":record['mass'],\
                    "resistance":record['resistance'],\
                    "resistance_calculated":record['resistance_calculated'],\
                    "heat_zone_1_res":record['heat_zone_1_res'],\
                    "heat_zone_2_res":record['heat_zone_2_res'],\
                    "heat_zone_3_res":record['heat_zone_3_res'],\
                    "heat_zone_4_res":record['heat_zone_4_res'],\
                    "joined_item":record['joined_item'],\
                    "joined_item_name":record['joined_item_name']
                    })
    """
    #data for testing purposes (comment all till return statement to get real data):
    data.append({\
                "item":'Jumts - Māja',\
                "item_name":'Jumts - Māja',\
                "qty": '',\
                "amount": '',\
                "parent":'',\
                "material_embedded_in":'',\
                "material_embedded_in_markup":'',\
                "material_embedded_in_markup_amount":'',\
                "factory_markup":'',\
                "factory_markup_amount":'',\
                "construction_markup":'',\
                "construction_markup_amount":'',\
                "delivery_markup":'',\
                "delivery_markup_amount":''
                })
    data.append({\
                "item":'Osb plāksne 18 mm',\
                "item_name":'Osb plāksne 18 mm',\
                "qty": '',\
                "amount": '',\
                "parent":'Jumts - Māja',\
                "material_embedded_in":'',\
                "material_embedded_in_markup":'',\
                "material_embedded_in_markup_amount":'',\
                "factory_markup":'',\
                "factory_markup_amount":'',\
                "construction_markup":'',\
                "construction_markup_amount":'',\
                "delivery_markup":'',\
                "delivery_markup_amount":''
                })
    data.append({\
                "item":'D0502 OSB - Skrūvēts 6 - 18 mm',\
                "item_name":'D0502 OSB - Skrūvēts 6 - 18 mm',\
                "qty": '',\
                "amount": '',\
                "parent":'Jumts - Māja',\
                "material_embedded_in":'',\
                "material_embedded_in_markup":'',\
                "material_embedded_in_markup_amount":'',\
                "factory_markup":'',\
                "factory_markup_amount":'',\
                "construction_markup":'',\
                "construction_markup_amount":'',\
                "delivery_markup":'',\
                "delivery_markup_amount":''
                })
    #column for testing purposes:
    columns = [
        {
            "fieldname": "item",
            "label": _("Raw Material"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 200
        }
        ]
    """
    return columns, data
    
def get_columns():
	columns = [
        {
            "fieldname": "item",
            "label": _(""),
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "fieldname": "factor",
            "label": _("F"),
            "fieldtype": "Float",
            "width": 50
        },
        {
            "fieldname": "uom",
            "label": _("uom"),
            "fieldtype": "Link",
            "options": "Uom",
            "width": 30
        },
        {
            "fieldname": "price_list_rate",
            "label": _("Standart <br> Rate"),
            "fieldtype": "Currency",
            "width": 20
        },
        {
            "fieldname": "rate",
            "label": _("Rate"),
            "fieldtype": "Currency",
            "width": 60,
            "precision": 2
        },
        {
            "fieldname": "qty",
            "label": _("Qty"),
            "fieldtype": "Float",
            "width": 50
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 70,
            "precision": 2
        },
        {
            "fieldname": "material_embedded_in",
            "label": _("Embedded"),
            "fieldtype": "Link",
            "options": "Material Embedded In Types",
            "width": 100
        },
        {
            "fieldname": "material_embedded_in_markup",
            "label": _("Embedded <br>Markup %"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "material_embedded_in_markup_amount",
            "label": _("Embedded <br>Markup $"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "factory_markup",
            "label": _("Factory <br>Markup %"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "factory_markup_amount",
            "label": _("Factory <br>Markup $"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "construction_markup",
            "label": _("Construction <br>Markup %"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "construction_markup_amount",
            "label": _("Construction <br>Markup $"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "delivery_markup",
            "label": _("Delivery <br>Markup %"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "delivery_markup_amount",
            "label": _("Delivery <br>Markup $"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "thickness",
            "label": _("Thickness"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "peculiar_mass",
            "label": _("Peculiar <br>mass"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "factor_rez",
            "label": _("Factor <br>Rez."),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "conductivity",
            "label": _("Conductivity"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "m3",
            "label": _("m3"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "mass",
            "label": _("Mass"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "resistance",
            "label": _("Resistance"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "resistance_calculated",
            "label": _("Resistance<br>calculated"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "heat_zone_1_res",
            "label": _("HT1"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "heat_zone_2_res",
            "label": _("HT2"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "heat_zone_3_res",
            "label": _("HT3"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "heat_zone_4_res",
            "label": _("HT4"),
            "fieldtype": "Float",
            "width": 40
        },
        {
            "fieldname": "joined_item",
            "label": _("Joined <br>With Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "fieldname": "joined_item_name",
            "label": _("Joined With <br>Item Name "),
            "fieldtype": "Data",
            "width": 150
        },
	]
	return columns
    

@frappe.whitelist()
def get_data(filters):
     #in sql is fetched only detailed data (childrecords)
     #totals (parent) are calculated in python
     #ToDo fetch details and subtotals inside sql -> with 'with rollup'?
     #ToDo - map srray keys using -> ict.fromkeys(my_csv_dict.keys(),[])
     raw_items_detailed = frappe.db.sql("""
        select 
                qi.master_item as item,
                qi.factor,
                qi.uom,
                qi.price_list_rate,
                qi.rate,
                qi.qty,
                qi.amount,
                qi.item_code as item_name,
                qi.material_embedded_in,
                qi.material_embedded_in_markup,
                qi.material_embedded_in_markup_amount,
                qi.factory_markup,
                qi.factory_markup_amount,
                qi.construction_markup,
                qi.construction_markup_amount,
                qi.delivery_markup,
                qi.delivery_markup_amount,
                qi.thickness,
                qi.peculiar_mass,
                qi.factor_rez,
                qi.conductivity,
                qi.m3,
                qi.mass,
                qi.resistance,
                qi.resistance_calculated,
                qi.heat_zone_1_res,
                qi.heat_zone_2_res,
                qi.heat_zone_3_res,
                qi.heat_zone_4_res,
                qi.joined_item,
                qi.joined_item_name
            from
              `tabQuotation` q 
            left join
              `tabQuotation Item` qi on qi.parent = q.name
              where q.name = %(quotation)s
     """, filters, as_dict=1, as_list=0)
     #return raw_items_detailed
     #return raw_items_detailed
     raw_items_subtotals = {} #subtotal object
     raw_items_all = [] #final object (totals and detailed records)
     #create subtotals
     for raw_item in raw_items_detailed:
        parent_name = raw_item.item
        #add or create parent qty:
        if parent_name not in raw_items_subtotals.keys(): #if is not dictionary key then set
            raw_items_subtotals[parent_name] = float(raw_item.amount)
        else: #if is set dictionary key then add value
           raw_items_subtotals[parent_name] += float(raw_item.amount)
        #set parent for detailed record:
        raw_item.update({"parent": raw_item.item})
        #raw_items_with_parents.update(raw_item)
     #create final object (totals and detailed records)
     #return raw_items_subtotals, raw_items_detailed
     for raw_item, total_amount  in raw_items_subtotals.items(): #
         raw_items_all.append({"item":"",\
                                 "parent":"",\
                                 "item_name":raw_item,\
                                 "factor":"",\
                                 "uom":"",\
                                 "price_list_rate":"",\
                                 "rate":float(0.00),\
                                 "qty":float(0.00),\
                                 "amount": total_amount,\
                                 "material_embedded_in":"",\
                                 "material_embedded_in_markup":"",\
                                 "material_embedded_in_markup_amount":"",\
                                 "factory_markup":"",\
                                 "factory_markup_amount":"",\
                                 "construction_markup":"",\
                                 "construction_markup_amount":"",\
                                 "delivery_markup":"",\
                                 "delivery_markup_amount":"",\
                                 "thickness":"",\
                                 "peculiar_mass":"",\
                                 "factor_rez":"",\
                                 "conductivity":"",\
                                 "m3":"",\
                                 "mass":"",\
                                 "resistance":"",\
                                 "resistance_calculated":"",\
                                 "heat_zone_1_res":"",\
                                 "heat_zone_2_res":"",\
                                 "heat_zone_3_res":"",\
                                 "heat_zone_4_res":"",\
                                 "joined_item":"",\
                                 "joined_item_name":""
                              })
         for d in raw_items_detailed:
             if d.item == raw_item:
                 raw_items_all.append(d)
     #for raw_items in raw_items_all:
     #    print(raw_items)
     return raw_items_all

