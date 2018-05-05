import time
import numpy
import pyaudio
import fluidsynth
import sys
from pygame import midi

sample_size = 44100
#sample_size = 22000

velocity = 100
times_per_sec = 100

pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt32,
    channels = 2,
    rate = sample_size,
    output = True)


#Initializing the Midi keyboard
midi.init()
INPUTNO = midi.get_default_input_id()
input = midi.Input(INPUTNO)

s = []

fl = fluidsynth.Synth()

# Initial silence is 1 second
s = numpy.append(s, fl.get_samples(sample_size * 1))

sfid = fl.sfload(sys.argv[1])
fl.program_select(0, sfid, 0, 0)

fl.noteon(0, 60, velocity)
fl.noteon(0, 67, velocity)
fl.noteon(0, 76, velocity)

# Chord is held for 2 seconds
print('Starting playback 1')
for i in range(1000):
    print(input.read(100))
    s = []
    s = numpy.append(s, fl.get_samples(int(sample_size/times_per_sec)))
    samps = fluidsynth.raw_audio_string(s)
    strm.write(samps)


fl.noteoff(0, 60)
fl.noteoff(0, 67)
fl.noteoff(0, 76)

# Decay of chord is held for 1 second
s = numpy.append(s, fl.get_samples(sample_size * 1))

fl.delete()

samps = fluidsynth.raw_audio_string(s)

print(len(samps))
print('Starting playback')
strm.write(samps)
