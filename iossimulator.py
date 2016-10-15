import workflow
import subprocess
import os
import sys
import core.device as Device

def devices(name=None):
  devices = Device.devices()
  devices = devices if name is None else [d for d in devices if d.name.lower().find(name.lower()) >= 0]

  workflowDevices = []

  for device in devices:
    workflowDevices.append(workflow.Item(title=device.name, subtitle=device.runtime, arg=device.udid, autocomplete=device.name, valid=True, uid=device.udid))
  workflow.Item.generate_output(workflowDevices)

def launch_device(udid):
  device = Device.device_with_id(udid)
  deviceName = device.name if device is not None else ""

  devnull = open(os.devnull, 'w') # hiding the output
  subprocess.call(["xcrun", "instruments", "-w", udid], stdout=devnull, stderr=subprocess.STDOUT)

  sys.stdout.write(deviceName)
  sys.stdout.flush()

def erase_device(udid):
  device = Device.device_with_id(udid)
  deviceName = device.name if device is not None else ""

  devnull = open(os.devnull, 'w') # hiding the output
  subprocess.call(["xcrun", "simctl", "erase", udid], stdout=devnull, stderr=subprocess.STDOUT)

  sys.stdout.write(deviceName)
  sys.stdout.flush()

if __name__ == '__main__':
  devices()
