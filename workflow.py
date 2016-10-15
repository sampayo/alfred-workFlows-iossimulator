import xml.etree.ElementTree as ET
import sys
from os import environ
from plistlib import readPlist, writePlist

class ItemMod:
	  Cmd, Ctrl, Alt, Shift, Fn = ('cmd', 'ctrl', 'alt', 'shift', 'fn')

class Item:
	def __init__(self, title, subtitle="", icon=None, arg=None, autocomplete=None, valid=False, uid=None, modifierSubtitles=None):
		self.title = title
		self.subtitle = subtitle
		self.icon = icon
		self.arg = arg
		self.autocomplete = autocomplete
		self.valid = valid
		self.uid = uid
		self.modifierSubtitles = modifierSubtitles if modifierSubtitles is not None else {}

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

		mods = (ItemMod.Cmd, ItemMod.Ctrl, ItemMod.Alt, ItemMod.Shift, ItemMod.Fn)
		for mod in mods:
			if mod in self.modifierSubtitles:
				subtitle = ET.SubElement(item, "subtitle", { "mod": mod })
				subtitle.text = self.modifierSubtitles[mod]

		if self.icon:
			icon = ET.SubElement(item, "icon")
			icon.text = self.icon

		return item

	@staticmethod
	def generate_output(items):
		root = ET.Element('items')
		for item in items:
			root.append(item.item_xml())
        
		sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')
		sys.stdout.write(ET.tostring(root).encode('utf-8'))
		sys.stdout.flush()

def set_variable(name, value):
	info = readPlist('info.plist')
	# Set a variable
	info['variables'][name] = value

	# Save changes
	writePlist(info, 'info.plist')

def get_variable(name):
	if name in environ:
		return environ[name]
	else:
		return None

