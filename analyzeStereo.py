import pyaudio
import numpy as np
import sys

CHUNK = 2**11 # Look into this param see if affects resolution
RATE = 48000
LMIC_INDEX = 12
RMIC_INDEX = 13
MAX_VAL = 2**16

def getInitialVolumes(streamL, streamR, iterations):

    historicL = []
    historicR = []

    for i in range(iterations):
        dataL = np.fromstring(streamL.read(CHUNK, exception_on_overflow = False),dtype=np.int16)
        dataR = np.fromstring(streamR.read(CHUNK, exception_on_overflow = False),dtype=np.int16)

        peakL = np.average(np.abs(dataL))
        peakR = np.average(np.abs(dataR))

        historicL.append(peakL)
        historicR.append(peakR)

    return historicL, historicR

def main():
    itersBeforeReInit = 100
    significantDifference = 1.5
    noiseFactor = 0

    # Test to see if one mic can have multiple streams

    p = pyaudio.PyAudio()

    streamL = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK, input_device_index=LMIC_INDEX)

    streamR = p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK, input_device_index=RMIC_INDEX)

    print "\nInitializing ..."
    historicL, historicR = getInitialVolumes(streamL, streamR, itersBeforeReInit)
    averageL = np.average(historicL)
    stdDevL = np.std(historicL)
    averageR = np.average(historicR)
    stdDevR = np.std(historicR)
    historicL = []
    historicR = []
    print "\nInitialization Complete."

    while True:
      dataL = np.fromstring(streamL.read(CHUNK, exception_on_overflow = False),dtype=np.int16)
      dataR = np.fromstring(streamR.read(CHUNK, exception_on_overflow = False),dtype=np.int16)

      peakL = np.average(np.abs(dataL))
      peakR = np.average(np.abs(dataR))

      spikeL = peakL > averageL*significantDifference
      spikeR = peakR > averageR*significantDifference

      if spikeL and spikeR:
          normL = (peakL-averageL)/stdDevL
          normR = (peakR-averageR)/stdDevR

          if abs(normL - normR) < noiseFactor:
              print("")
          elif normL > normR:
              print("L")
          else:
              print("R")

      else:
          historicL.append(peakL)
          historicR.append(peakR)

      if len(historicL) > itersBeforeReInit or len(historicR) > itersBeforeReInit:
          averageL = np.average(historicL)
          stdDevL = np.std(historicL)
          averageR = np.average(historicR)
          stdDevR = np.std(historicR)
          historicL = []
          historicR = []
          print("ReINIT")



    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
