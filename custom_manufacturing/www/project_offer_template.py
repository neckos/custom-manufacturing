from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt, has_common
from frappe.utils.user import is_website_user

from frappe.utils import cint, quoted
from frappe.website.render import resolve_path
from frappe.model.document import get_controller, Document


base_template_path = "custom_manufacturing/templates/includes/project_offer_template.html"

def get_context(context, **dict_params):
	""" You can set context here """
	context.update({"doc":frappe.get_doc("Project Offer", "288860bcf0")})