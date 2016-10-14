import json
import workflow
import subprocess
import os
import sys

class DeviceType:
    IPhone, IPad, Other = ("iPhone", "iPad", "other")

    @staticmethod
    def type_with_name(name):
      deviceType = name.lower().find("iphone") == 0 and DeviceType.IPhone or DeviceType.Other
      return name.lower().find("ipad") == 0 and DeviceType.IPad or deviceType

class DeviceState:
    Unknown, Shutdown, Booted, Creating = ("unknown", "shutdown", "booted", "creating")

    @staticmethod
    def state_with_name(state):
      if state == "Shutdown":
        return DeviceState.Shutdown
      elif state == "Booted":
        return DeviceState.Booted
      elif state == "Creating":
        return DeviceState.Creating    
      else:
        return DeviceState.Unknown        

class Device:
  def __init__(self, name, udid, state, runtime):
    self.name = name
    self.udid = udid
    self.state = DeviceState.state_with_name(state)
    self.runtime = runtime 
    self.type = DeviceType.type_with_name(name)

  def description(self):
    return "name: %s id: %s state: %s runtime: %s type: %s" % (self.name, self.udid, self.state, self.runtime, self.type)

def __populate_devices():
  devicesJson = subprocess.check_output(["/usr/bin/xcrun", "simctl", "list", "-j", "devices"])
  allDevices = json.loads(devicesJson)["devices"]
  iosDevices = [device for device in allDevices.items() if (device[0].find("iOS") >= 0)]

  devices = []
  for runtime, rawDevices in iosDevices:
    devicesAvailables = (d for d in rawDevices if d["availability"] == "(available)") # only the available devices
    for rawDevice in devicesAvailables:
      device = Device(rawDevice["name"], rawDevice["udid"], rawDevice["state"], runtime)
      devices.append(device);

  return devices

def devices():
  devices = __populate_devices()
  workflowDevices = []

  for device in devices:
    workflowDevices.append(workflow.Item(title=device.name, subtitle=device.runtime, arg=device.udid, autocomplete=device.name, valid=True, uid=device.udid))
  workflow.Item.generate_output(workflowDevices)

def launch_device(udid):
  devices = [d for d in __populate_devices() if d.udid == udid]
  deviceName = devices[0].name if devices else ""

  ads = open(os.devnull, 'w') # hiding the output
  subprocess.call(["xcrun", "instruments", "-w", udid], stdout=ads, stderr=subprocess.STDOUT)

  sys.stdout.write(deviceName)
  sys.stdout.flush()

if __name__ == '__main__':
  devices()  

