import json
import os
import glob
from shutil import rmtree
import biplist.biplist as biplist
from device import devices

__metadataplist = ".com.apple.mobile_container_manager.metadata.plist"
__applicationPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Bundle/Application/*/*.app"
__bundlePlistPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Data/Application/*/" + __metadataplist

class Application():
	def __init__(self, bundleDisplayName, bundleID, bundleShortVersion, bundleVersion, path, icons):
	    self.bundleDisplayName = bundleDisplayName
	    self.bundleID = bundleID
	    self.bundleShortVersion = bundleShortVersion
	    self.bundleVersion = bundleVersion
	    self.path = path
	    self.icons = icons if icons is not None else []

	def description(self):
		return "{0}, bundleId: {1}, short version {2}, bundle version {3}, path {4}, icon \n{5}".format(
			self.bundleDisplayName,
			self.bundleID,
			self.bundleShortVersion,
			self.bundleVersion,
			self.path,
			"\n".join((d for d in self.icons)))

def __builtpath(path):
	return os.path.join(os.path.expanduser("~"), path)

def __bundlePathsIndex(deviceId):
	path = __builtpath(__bundlePlistPath.format(deviceId))	
	listMetadata = glob.glob(path)
	bundlePathsIndex = {}

	for metadataPath in listMetadata:
		info = biplist.readPlist(metadataPath)

		if "MCMMetadataIdentifier" in info:
			bundlePath = metadataPath.replace(__metadataplist, "")
			bundlePathsIndex[info["MCMMetadataIdentifier"]] = bundlePath

	return bundlePathsIndex

def __apllication_with_info(info, applicationPath):
	bundleIdentifier = info["CFBundleIdentifier"]
	bundleDisplayName = info["CFBundleIdentifier"] if "CFBundleDisplayName" in info else info["CFBundleName"]
	bundleShortVersion = info["CFBundleShortVersionString"]
	bundleInfoDictionaryVersion = info["CFBundleInfoDictionaryVersion"]

	icons = []
	if "CFBundleIcons" in info:
		if "CFBundlePrimaryIcon" in info["CFBundleIcons"]:
			if "CFBundleIconFiles" in info["CFBundleIcons"]["CFBundlePrimaryIcon"]:
				iconsNames = info["CFBundleIcons"]["CFBundlePrimaryIcon"]["CFBundleIconFiles"]
				iconsNames.reverse()

				for iconName in iconsNames:
					pathGlob = glob.glob("{0}/{1}*.png".format(applicationPath, iconName))
					if pathGlob:
						icons.append(pathGlob[0])

	application = Application(
		bundleDisplayName,
		bundleIdentifier,
		bundleShortVersion,
		bundleInfoDictionaryVersion,
		applicationPath,
		icons)
	return application

def applications_with_device_id(deviceId):
	path = __builtpath(__applicationPath.format(deviceId))
	listApplications = glob.glob(path)

	applications = []
	for applicationPath in listApplications:
		infoplist = "{0}/info.plist".format(applicationPath)
		info = biplist.readPlist(infoplist)
		applications.append(__apllication_with_info(info, applicationPath))

	return applications

def application_with_device_and_bundle(deviceId, bundleId):
	path = __builtpath(__applicationPath.format(deviceId))
	listApplications = glob.glob(path)

	for applicationPath in listApplications:
		infoplist = "{0}/info.plist".format(applicationPath)
		info = biplist.readPlist(infoplist)
		if info["CFBundleIdentifier"] == bundleId:
			return __apllication_with_info(info, applicationPath)

	return None	

def bundle_path(deviceId, bundleId):
	return __bundlePathsIndex(deviceId)[bundleId]

def reset_data(deviceId, bundleId):
	path = bundle_path(deviceId, bundleId)

	def __delete_content(path):
		files = glob.glob("{0}*".format(path)) + glob.glob("{0}.*".format(path)) # special case for hiding files
		for filePath in files:
			if (os.path.exists(filePath)):
				if (os.path.isdir(filePath)):
					rmtree(filePath, True)
				else:
					os.unlink(filePath)

	directoryPath = "{0}/Documents/".format(path)
	libraryPath = "{0}/Library/".format(path)
	tmpPath = "{0}/tmp/".format(path)

	__delete_content(directoryPath)
	__delete_content(libraryPath)
	__delete_content(tmpPath)

def __all_application():
	allDevices = devices()
	applications = []

	for device in allDevices:
		applications = applications + (applications_with_device_id(device.udid))

	return applications

if __name__ == '__main__':
	apps = __all_application();
	print("Applications: {0}".format(len(apps)))
	print("\n".join((a.description() for a in apps)))


