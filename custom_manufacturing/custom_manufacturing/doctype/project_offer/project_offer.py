# -*- coding: utf-8 -*-
# Copyright (c) 2018, kaspars.zemiitis@gmail.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, pdfkit
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
import json
from frappe.utils import scrub_urls

class ProjectOffer(Document):
	pass

@frappe.whitelist()
def get_offer_description_details(offer_description_template_name):
	return frappe.get_all('Offer Description Template Items', filters={'parent': offer_description_template_name}, fields=['idx','name' ,'category', 'detail', 'sub_detail', 'type', 'display'], order_by='idx')

@frappe.whitelist()
def get_master_items_from_estimate(estimate):
	return frappe.get_all('Quotation Master BOM', filters={'parent': estimate}, fields=['item'], order_by='idx')

@frappe.whitelist()
def get_raw_items_from_estimate(estimate):
	return frappe.get_all('Quotation Item', filters={'parent': estimate}, fields=['item_code', 'material_embedded_in', 'master_item'], order_by='idx') 

def prepare_header_footer(doc):
	options = {}
	#footer:
	html = frappe.render_template("templates/includes/project_offer_footer.html", {"doc": doc})
	fname = os.path.join("/tmp", "frappe-pdf-footer-{0}.html".format(frappe.generate_hash()))
	with open(fname, "wb") as f:
		f.write(html.encode("utf-8"))
	options['footer-html'] = fname   		
	#header:
	html = frappe.render_template("templates/includes/project_offer_header.html", {"doc": doc})
	fname = os.path.join("/tmp", "frappe-pdf-header-{0}.html".format(frappe.generate_hash()))
	with open(fname, "wb") as f:
		f.write(html.encode("utf-8"))
	options['header-html'] = fname
	return options

def get_pdf_custom(html, doc, options=None, output = None):
	html = scrub_urls(html)
	fname = os.path.join("/tmp", "custom-pdf-{0}.pdf".format(frappe.generate_hash()))
	options = {
		'page-size': 'A4',
		'margin-top': '3mm', #to have some top margin in new-page breaks inside table have to set some margin top
		'margin-right': '0mm',
		'margin-bottom': '5mm',
		'margin-left': '0mm',
		'encoding': "UTF-8",
	}
	#update with header and footer:
	options.update(prepare_header_footer(doc))
	print(options)
	try:
		pdfkit.from_string(html, fname, options=options or {})
		#no need for append in our case:
		#if output:
		#	append_pdf(PdfFileReader(file(fname,"rb")),output)
		#else:
		with open(fname, "rb") as fileobj:
			filedata = fileobj.read()

	except IOError as e:
		if ("ContentNotFoundError" in e.message
			or "ContentOperationNotPermittedError" in e.message
			or "UnknownContentError" in e.message
			or "RemoteHostClosedError" in e.message):

			# allow pdfs with missing images if file got created
			if os.path.exists(fname):
				#if output:
				#	append_pdf(PdfFileReader(file(fname,"rb")),output)
				#else:
				with open(fname, "rb") as fileobj:
					filedata = fileobj.read()

			else:
				frappe.throw(_("PDF generation failed because of broken image links"))
		else:
			raise

	finally:
		cleanup(fname, options)

	if output:
		return output

	return filedata

def cleanup(fname, options):
	if os.path.exists(fname):
		os.remove(fname)

	for key in ("header-html", "footer-html"):
		if options.get(key) and os.path.exists(options[key]):
			os.remove(options[key])
    
@frappe.whitelist()
def print_project_offer_pdf(doc):
	doc = frappe._dict(json.loads(doc))
	"""
    some example from attendance tool:
	doc.students = [doc.student]
	if not (doc.student_name and doc.student_batch):
		program_enrollment = frappe.get_all("Program Enrollment", fields=["student_batch_name", "student_name"],
			filters={"student": doc.student, "docstatus": ('!=', 2), "academic_year": doc.academic_year})
		if program_enrollment:
			doc.batch = program_enrollment[0].student_batch_name
			doc.student_name = program_enrollment[0].student_name

	# get the assessment result of the selected student
	values = get_formatted_result(doc, get_course=True, get_all_assessment_groups=doc.include_all_assessment)
	assessment_result = values.get("assessment_result").get(doc.student)
	courses = values.get("course_dict")
	course_criteria = get_courses_criteria(courses)

	# get the assessment group as per the user selection
	if doc.include_all_assessment:
		assessment_groups = get_child_assessment_groups(doc.assessment_group)
	else:
		assessment_groups = [doc.assessment_group]

	# get the attendance of the student for that peroid of time.
	doc.attendance = get_attendance_count(doc.students[0], doc.academic_year, doc.academic_term)
	"""
	template = "custom_manufacturing/templates/includes/project_offer_template.html"
	#base_template_path = "frappe/www/printview.html"

	#from frappe.www.printview import get_letter_head
	#letterhead = get_letter_head(frappe._dict({"letter_head": doc.letterhead}), not doc.add_letterhead)

	_lang = frappe.local.lang
	#set lang as specified in project offer doc
	lang = doc.language
	if lang: frappe.local.lang = lang

	html = frappe.render_template(template,
		{
			"doc": doc,
			"title": "Project Offer"
		})
	#final_template = frappe.render_template(base_template_path, {"body": html, "title": "Project Offer"})
	#print(html)
	#reset lang to original local lang
	frappe.local.lang = _lang
	#create response
	frappe.response.filename = "Project_Offer_" + doc.name + ".pdf"
	frappe.response.filecontent = get_pdf_custom(html, doc)
	frappe.response.type = "download"
