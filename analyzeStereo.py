import pyaudio
import numpy as np
import sys
from statistics import mode

CHUNK = 2**11 # Look into this param see if affects resolution
RATE = 48000
LMIC_INDEX = 13
RMIC_INDEX = 12
MAX_VAL = 2**16

# Create function that allows user to set l and r

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

def most_frequent(myList):
    return max(set(myList), key = myList.count)

def main():
    # Tunable Parameters
    itersBeforeReInit = 50
    significantDifference = 1.2
    noiseFactor = 1.5
    historicPeaksSize = 5

    historicPeaks = []
    for i in range(historicPeaksSize):
        historicPeaks.append("Center")

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

    peaksCounter = 0

    while True:
      dataL = np.fromstring(streamL.read(CHUNK, exception_on_overflow = False),dtype=np.int16)
      dataR = np.fromstring(streamR.read(CHUNK, exception_on_overflow = False),dtype=np.int16)

      peakL = np.average(np.abs(dataL))
      peakR = np.average(np.abs(dataR))

      spikeL = peakL > averageL*significantDifference
      spikeR = peakR > averageR*significantDifference

      if spikeL or spikeR:
          peaksCounter += 1
          normL = (peakL-averageL)/stdDevL
          normR = (peakR-averageR)/stdDevR
          difference = abs(normL - normR)

          if difference < noiseFactor:
              historicPeaks[peaksCounter%len(historicPeaks)] = "Center"
          elif normL > normR:
              historicPeaks[peaksCounter%len(historicPeaks)] = "Left"
          else:
              historicPeaks[peaksCounter%len(historicPeaks)] = "Right"

          print most_frequent(historicPeaks)

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
