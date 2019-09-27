import workflow
import subprocess
import os
import sys
import core.device as Device
import core.application as Application


def __icon(device):
    ipadon = "assets/ipadon.png"
    ipadoff = "assets/ipadoff.png"
    iphoneon = "assets/iphoneon.png"
    iphoneoff = "assets/iphoneoff.png"

    if device.type == Device.DeviceType.IPhone:
        return iphoneon if device.state == Device.DeviceState.Booted else iphoneoff
    else:
        return ipadon if device.state == Device.DeviceState.Booted else ipadoff


def devices(name=None):
    devices = Device.devices()
    devices = devices if name is None else [
        d for d in devices if d.name.lower().find(name.lower()) >= 0]

    workflowDevices = []

    for device in devices:

        modifierSubtitles = {
            workflow.ItemMod.Ctrl: device.runtime,
            workflow.ItemMod.Shift: device.applications_description()
        }
        workflowDevices.append(workflow.Item(
            title=device.name,
            subtitle=device.runtime + " (" + device.udid + ")",
            icon=__icon(device),
            arg=device.udid,
            autocomplete=device.name,
            valid=True,
            uid=device.udid,
            modifierSubtitles=modifierSubtitles))
    workflow.Item.generate_output(workflowDevices)


def launch_device(udid):
    device = Device.device_with_id(udid)
    deviceName = device.name if device is not None else ""

    devnull = open(os.devnull, 'w')  # hiding the output
    subprocess.call(["xcrun", "instruments", "-w", udid],
                    stdout=devnull, stderr=subprocess.STDOUT)

    if deviceName:
        sys.stdout.write("Launching {0}.".format(deviceName))
        sys.stdout.flush()


def erase_device(udid):
    device = Device.device_with_id(udid)
    deviceName = device.name if device is not None else ""

    devnull = open(os.devnull, 'w')  # hiding the output
    subprocess.call(["xcrun", "simctl", "erase", udid],
                    stdout=devnull, stderr=subprocess.STDOUT)

    if deviceName:
        sys.stdout.write("{0} was reset".format(deviceName))
        sys.stdout.flush()


def applications_with_device_id(name=None):
    deviceId = workflow.get_variable('deviceId')

    applications = Application.applications_with_device_id(deviceId)
    applications = applications if name is None else [
        d for d in applications if d.bundleDisplayName.lower().find(name.lower()) >= 0]

    workflowApplications = []
    for application in applications:
        modifierSubtitles = {
            workflow.ItemMod.Shift: application.application_detail()
        }
        workflowApplications.append(workflow.Item(
            title=application.bundleDisplayName,
            subtitle="Reveal content in Finder",
            icon=application.icons[0] if application.icons else "assets/noicon.png",
            arg=application.bundleID,
            autocomplete=application.bundleDisplayName,
            valid=True,
            uid=application.bundleID,
            modifierSubtitles=modifierSubtitles)
        )
    workflow.Item.generate_output(workflowApplications)


def bundle_path(bundleId):
    deviceId = workflow.get_variable('deviceId')
    path = Application.bundle_path(deviceId, bundleId)
    subprocess.call(["open", "-R", path])


def launch_application(bundleId):
    deviceId = workflow.get_variable('deviceId')

    # Launch simulator
    devnull = open(os.devnull, 'w')  # hiding the output
    subprocess.call(["xcrun", "instruments", "-w", deviceId],
                    stdout=devnull, stderr=subprocess.STDOUT)

    # Launch app in simulator
    subprocess.call(["xcrun", "simctl", "launch", "-w", deviceId,
                     bundleId], stdout=devnull, stderr=subprocess.STDOUT)

    application = Application.application_with_device_and_bundle(
        deviceId, bundleId)
    if application is not None:
        sys.stdout.write("Launching {0}.".format(
            application.bundleDisplayName))
        sys.stdout.flush()


def uninstall_application(bundleId):
    deviceId = workflow.get_variable('deviceId')
    application = Application.application_with_device_and_bundle(
        deviceId, bundleId)

    # Launch simulator
    devnull = open(os.devnull, 'w')  # hiding the output
    subprocess.call(["xcrun", "instruments", "-w", deviceId],
                    stdout=devnull, stderr=subprocess.STDOUT)

    # Launch app in simulator
    subprocess.call(["xcrun", "simctl", "uninstall", deviceId, bundleId])

    if application is not None:
        sys.stdout.write("{0} was deleted.".format(
            application.bundleDisplayName))
        sys.stdout.flush()


def reset_data_application(bundleId):
    deviceId = workflow.get_variable('deviceId')
    application = Application.application_with_device_and_bundle(
        deviceId, bundleId)
    Application.reset_data(deviceId, bundleId)

    if application is not None:
        sys.stdout.write(application.bundleDisplayName)
        sys.stdout.flush()


if __name__ == '__main__':
    devices()
