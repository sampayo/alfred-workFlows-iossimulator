import json
import subprocess

class DeviceType:
  IPhone, IPad, Other = ("iPhone", "iPad", "other")

def __device_type_with_name(name):
  deviceType = name.lower().find("iphone") == 0 and DeviceType.IPhone or DeviceType.Other
  return name.lower().find("ipad") == 0 and DeviceType.IPad or deviceType

class DeviceState:
  Unknown, Shutdown, Booted, Creating = ("unknown", "shutdown", "booted", "creating")

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

  def description(self):
    return "name: {0} id: {1} state: {2} runtime: {3} type: {4}".format(
      self.name, 
      self.udid, 
      self.state, 
      self.runtime, 
      self.type)

def devices():
  devicesJson = subprocess.check_output(["/usr/bin/xcrun", "simctl", "list", "-j", "devices"])
  allDevices = json.loads(devicesJson)["devices"]
  iosDevices = [device for device in allDevices.items() if (device[0].find("iOS") >= 0)]

  devices = []
  for runtime, rawDevices in iosDevices:
    devicesAvailables = (d for d in rawDevices if d["availability"] == "(available)") # only the available devices
    for rawDevice in devicesAvailables:
      device = Device(rawDevice["name"], rawDevice["udid"], 
        __device_state_with_name(rawDevice["state"]), runtime,
        __device_type_with_name(rawDevice["name"]))
      devices.append(device);

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
