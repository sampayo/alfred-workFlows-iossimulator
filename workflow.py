import xml.etree.ElementTree as ET

class Item:
	def __init__(self, title, subtitle="", icon=None, arg=None, autocomplete=None, valid=False, uid=None):
		self.title = title
		self.subtitle = subtitle
		self.icon = icon
		self.arg = arg
		self.autocomplete = autocomplete
		self.valid = valid
		self.uid = uid

	def item_xml(self):
		attrib = { "valid": "yes" if self.valid else "no" }
		if self.autocomplete is not None:
			attrib["autocomplete"] = self.autocomplete
		if self.uid is not None:
			attrib["uid"] = self.uid  
		if self.arg is not None:
			attrib["arg"] = self.arg    		

		item = ET.Element('item', attrib)

		title = ET.SubElement(item, "title")
		title.text = self.title

		if self.subtitle:
			subtitle = ET.SubElement(item, "subtitle")
			subtitle.text = self.subtitle

		if self.icon:
			icon = ET.SubElement(item, "icon")
			icon.text = self.icon

		return item

	@staticmethod
	def generate_output(items):
		root = ET.Element('items')
		for item in items:
			root.append(item.item_xml())

		print('<?xml version="1.0" encoding="utf-8"?>\n')
		print(ET.tostring(root).encode('utf-8'))
