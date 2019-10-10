import pyaudio
import numpy as np
import sys

CHUNK = 2**11
RATE = 48000
LMIC_INDEX = 12
RMIC_INDEX = 13
MAX_VAL = 2**16

def computeEqScalar(lrDifferences):
    avg = np.average(lrDifferences)
    print(avg)
    sys.exit(1)


def getInitialEqScalar(streamL, streamR):
    lrDifferences = []

    for i in range(100):
        dataL = np.fromstring(streamL.read(CHUNK, exception_on_overflow = False),dtype=np.int16)
        dataR = np.fromstring(streamR.read(CHUNK, exception_on_overflow = False),dtype=np.int16)

        peakL = np.average(np.abs(dataL))
        peakR = np.average(np.abs(dataR))

        lrDifference = peakL-peakR

        lrDifferences.append(lrDifference)

    computeEqScalar(lrDifferences)

def main():
    p = pyaudio.PyAudio()

    streamL = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK, input_device_index=LMIC_INDEX)

    streamR = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK, input_device_index=RMIC_INDEX)

    eqScalar = getInitialEqScalar(streamL, streamR)

    while True:

      dataL = np.fromstring(streamL.read(CHUNK, exception_on_overflow = False),dtype=np.int16)
      dataR = np.fromstring(streamR.read(CHUNK, exception_on_overflow = False),dtype=np.int16)

      peakL = eqScalar*np.average(np.abs(dataL))
      peakR = np.average(np.abs(dataR))

      if peakL - peakR > 1000:
          if peakL > peakR:
              print("LEFT")
          else:
              print("RIGHT")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
