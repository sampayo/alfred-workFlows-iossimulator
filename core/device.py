import json
import subprocess
from application import number_of_applications


class DeviceType:
    IPhone, IPad, Other = ("iPhone", "iPad", "other")


def __device_type_with_name(name):
    deviceType = name.lower().find(
        "iphone") == 0 and DeviceType.IPhone or DeviceType.Other
    return name.lower().find("ipad") == 0 and DeviceType.IPad or deviceType


class DeviceState:
    Unknown, Shutdown, Booted, Creating = (
        "unknown", "shutdown", "booted", "creating")


def __device_is_available(device):
    return (
        ('availability' in device and device['availability'] == "(available)")
        # XCode 11^
        or ('isAvailable' in device and device['isAvailable'] == True)
    )


def __prepare_runtime(runtime):
    return runtime.split(".")[-1].replace("-", " ", 1).replace("-", ".")


def __device_state_with_name(state):
    if state == "Shutdown":
        return DeviceState.Shutdown
    elif state == "Booted":
        return DeviceState.Booted
    elif state == "Creating":
        return DeviceState.Creating
    else:
        return DeviceState.Unknown


class Device:
    def __init__(self, name, udid, state, runtime, deviceType):
        self.name = name
        self.udid = udid
        self.state = state
        self.runtime = runtime
        self.type = deviceType
        self.numberOfApplications = number_of_applications(udid)

    def description(self):
        return "name: {0} id: {1} state: {2} runtime: {3} type: {4} number of applications: {5}".format(
            self.name,
            self.udid,
            self.state,
            self.runtime,
            self.type,
            self.numberOfApplications,
        )

    def applications_description(self):
        if self.numberOfApplications == 0:
            return "No applications installed"
        elif self.numberOfApplications == 1:
            return "1 application installed"
        else:
            return "{} applications installed".format(self.numberOfApplications)


def devices():
    devicesJson = subprocess.check_output(
        ["/usr/bin/xcrun", "simctl", "list", "-j", "devices"])
    allDevices = json.loads(devicesJson)["devices"]
    iosDevices = [device for device in allDevices.items() if (
        device[0].find("iOS") >= 0)]

    devices = []
    for runtime, rawDevices in iosDevices:
        devicesAvailables = (d for d in rawDevices if __device_is_available(d))
        for rawDevice in devicesAvailables:
            device = Device(
                rawDevice["name"],
                rawDevice["udid"],
                __device_state_with_name(rawDevice["state"]),
                __prepare_runtime(runtime),
                __device_type_with_name(rawDevice["name"])
            )
            devices.append(device)

    return devices


def device_with_id(udid):
    filteredDevices = [d for d in devices() if d.udid == udid]
    return filteredDevices[0] if filteredDevices else None


if __name__ == '__main__':
    allDevices = devices()
    print("\n".join((d.description() for d in allDevices)))

    if allDevices:
        individualDevice = device_with_id(allDevices[0].udid)
        if individualDevice:
            print("\n{0}".format(individualDevice.description()))
