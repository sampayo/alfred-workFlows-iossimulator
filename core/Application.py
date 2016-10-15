import json
import os
import glob
import biplist.biplist as biplist
from device import devices

__metadataplist = ".com.apple.mobile_container_manager.metadata.plist"
__applicationPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Bundle/Application/*/*.app"
__bundlePlistPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Bundle/Application/*/" + __metadataplist

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
	print path
	bundlePathsIndex = {}

	for metadataPath in listMetadata:
		info = biplist.readPlist(metadataPath)

		if "MCMMetadataIdentifier" in info:
			bundlePath = metadataPath.replace(__metadataplist, "")
			bundlePathsIndex[info["MCMMetadataIdentifier"]] = bundlePath

	return bundlePathsIndex

def application_with_device_id(deviceId):
	path = __builtpath(__applicationPath.format(deviceId))
	listApplications = glob.glob(path)

	applications = []
	for applicationPath in listApplications:
		infoplist = "{0}/info.plist".format(applicationPath)
		info = biplist.readPlist(infoplist)
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

		applications.append(Application(
			bundleDisplayName,
			bundleIdentifier,
			bundleShortVersion,
			bundleInfoDictionaryVersion,
			applicationPath,
			icons))

	return applications

def bundle_path(deviceId, bundleId):
	return __bundlePathsIndex(deviceId)[bundleId]

def __all_application():
	allDevices = devices()
	applications = []

	for device in allDevices:
		applications = applications + (application_with_device_id(device.udid))

	return applications

if __name__ == '__main__':
	apps = __all_application();
	print("Applications: {0}".format(len(apps)))
	print("\n".join((a.description() for a in apps)))


