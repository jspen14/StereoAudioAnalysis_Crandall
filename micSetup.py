import pyaudio

p = pyaudio.PyAudio()

micIndices = []

for index in range(p.get_device_count()):
    if "USB PnP Audio Device" in p.get_device_info_by_index(index)['name']:
        micIndices.append(index)

for index in micIndices:
    print p.get_device_info_by_index(index)

# Check to make sure these devices have atleast one input channel
