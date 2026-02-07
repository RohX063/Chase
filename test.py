import sounddevice as sd

device_info = sd.query_devices(18)
print(device_info)