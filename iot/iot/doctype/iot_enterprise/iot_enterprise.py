# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document

class IOTEnterprise(Document):
	def remove_all_groups(self):
		self.set("groups", list(set(d for d in self.get("groups") if d.grp_name == "Guest")))

	def append_groups(self, *groups):
		"""Add groups to user"""
		current_groups = [d.grp_name for d in self.get("groups")]
		for group in groups:
			if group.grp_name in current_groups:
				continue
			self.append("groups", group)

	def add_groups(self, *groups):
		"""Add groups to user and save"""
		self.append_groups(*groups)
		self.save()

	def remove_groups(self, *groups):
		existing_groups = dict((d.grp_name, d) for d in self.get("groups"))
		for group in groups:
			if group.grp_name in existing_groups:
				self.get("groups").remove(existing_groups[group.grp_name])

		self.save()

	def group_exists(self, group_name):
		existing_groups = dict((d.grp_name, d) for d in self.get("groups"))
		return group_name in existing_groups

	def get_groups(self):
		"""Returns list of groups selected for that user"""
		return self.groups or []


def get_user_doc(user):
	user_doc = frappe.get_doc("IOT User", user)
	if not user_doc:
		throw(_("User {0} is not an IOT User").format(user))
	return user_doc

def get_ent_doc(enterprise=None):
	"""Get Enterprise Document for current user"""
	user = frappe.session.user
	if not user:
		throw(_("Authorization error"))

	user_doc = get_user_doc(user)

	"""Check Enterprise permission"""
	if enterprise and user_doc.get("enterprise") != enterprise:
		if 'IOT Manager' not in frappe.get_roles(user):
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))
	if not enterprise:
		enterprise = user_doc.get("enterprise")

	ent_doc = frappe.get_doc("IOT Enterprise", enterprise)
	if not ent_doc:
		throw(_("IOT Enterprise {0} does not exists!").format(enterprise))

	"""
	if ent_doc.get('admin') != user:
		if 'IOT Manager' not in frappe.get_roles(user):
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))
	"""

	return ent_doc

@frappe.whitelist()
def get_groups(enterprise=None):
	"""
	ent_doc = get_ent_doc(enterprise)
	return ent_doc.get("groups")
	"""
	user = frappe.session.user
	user_doc = get_user_doc(user)

	if enterprise and user_doc.get("enterprise") != enterprise:
		if 'IOT Manager' not in frappe.get_roles(user):
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))
	if not enterprise:
		enterprise = user_doc.get("enterprise")

	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name, description
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups

@frappe.whitelist()
def get_enterprise(enterprise=None):
	"""Get Enterprise for current user"""
	return get_ent_doc(enterprise)
