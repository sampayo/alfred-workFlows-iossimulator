import json
import os
import glob
from shutil import rmtree
import biplist.biplist as biplist

__metadataplist = ".com.apple.mobile_container_manager.metadata.plist"
__applicationPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Bundle/Application/*/*.app"
__bundlePlistPath = "Library/Developer/CoreSimulator/Devices/{0}/data/Containers/Data/Application/*/" + __metadataplist


class Application():
    def __init__(self, bundleDisplayName, bundleID, bundleShortVersion, bundleVersion, path, size, icons):
        self.bundleDisplayName = bundleDisplayName
        self.bundleID = bundleID
        self.bundleShortVersion = bundleShortVersion
        self.bundleVersion = bundleVersion
        self.path = path
        self.size = size
        self.icons = icons if icons is not None else []

    def application_detail(self):
        return "{0}, v{1} ({2}), {3}".format(
            self.bundleID,
            self.bundleShortVersion,
            self.bundleVersion,
            self.size_formatted(),
        )

    def size_formatted(self):
        units = ("B.", "KB.", "MB.", "GB")

        def __get_size(size, unitIndex):
            if size >= 1024.0 and (len(units) - 1) > unitIndex:
                size = size / 1024.0
                return __get_size(size, unitIndex + 1)

            return (size, unitIndex)

        t = __get_size(self.size, 0)
        return "{0:,.2f} {1}".format(t[0], units[t[1]])

    def description(self):
        return "{0}, bundleId: {1}, short version {2}({3}), path {4}, size:{5} icon \n{6}".format(
            self.bundleDisplayName,
            self.bundleID,
            self.bundleShortVersion,
            self.bundleVersion,
            self.path,
            self.size_formatted(),
            "\n".join((d for d in self.icons)))


def __get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


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


def __application_with_info(info, applicationPath):
    bundleIdentifier = info["CFBundleIdentifier"]
    bundleDisplayName = info["CFBundleDisplayName"] if "CFBundleDisplayName" in info else info["CFBundleName"]
    bundleShortVersion = info["CFBundleShortVersionString"] if "CFBundleShortVersionString" in info else "Unknown"
    BundleVersion = info["CFBundleVersion"] if "CFBundleVersion" in info else "Unknown"

    icons = []
    if "CFBundleIcons" in info:
        if "CFBundlePrimaryIcon" in info["CFBundleIcons"]:
            if "CFBundleIconFiles" in info["CFBundleIcons"]["CFBundlePrimaryIcon"]:
                iconsNames = info["CFBundleIcons"]["CFBundlePrimaryIcon"]["CFBundleIconFiles"]
                iconsNames.reverse()

                for iconName in iconsNames:
                    pathGlob = glob.glob(
                        "{0}/{1}*.png".format(applicationPath, iconName))
                    if pathGlob:
                        icons.append(pathGlob[0])

    application = Application(
        bundleDisplayName,
        bundleIdentifier,
        bundleShortVersion,
        BundleVersion,
        applicationPath,
        __get_size(applicationPath),
        icons)
    return application


def applications_with_device_id(deviceId):
    path = __builtpath(__applicationPath.format(deviceId))
    listApplications = glob.glob(path)

    applications = []
    for applicationPath in listApplications:
        infoplist = "{0}/info.plist".format(applicationPath)
        info = biplist.readPlist(infoplist)
        applications.append(__application_with_info(info, applicationPath))

    return applications


def number_of_applications(deviceId):
    path = __builtpath(__applicationPath.format(deviceId))
    listApplications = glob.glob(path)
    return len(listApplications)


def application_with_device_and_bundle(deviceId, bundleId):
    path = __builtpath(__applicationPath.format(deviceId))
    listApplications = glob.glob(path)

    for applicationPath in listApplications:
        infoplist = "{0}/info.plist".format(applicationPath)
        info = biplist.readPlist(infoplist)
        if info["CFBundleIdentifier"] == bundleId:
            return __application_with_info(info, applicationPath)

    return None


def bundle_path(deviceId, bundleId):
    return __bundlePathsIndex(deviceId)[bundleId]


def reset_data(deviceId, bundleId):
    path = bundle_path(deviceId, bundleId)

    def __delete_content(path):
        # special case for hiding files
        files = glob.glob("{0}*".format(path)) + \
            glob.glob("{0}.*".format(path))
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


if __name__ == '__main__':
    apps = applications_with_device_id("3A6CC338-F3AF-4AE9-8E4E-8F6DCC7706DD")
    print("Applications: {0}".format(len(apps)))
    print("\n".join((a.description() for a in apps)))
