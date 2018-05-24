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
INPUTNO = 20     #Hardcoded this as 3 because that's what I found it to be
input = midi.Input(INPUTNO)

print(midi.get_count())
for i in range(midi.get_count()):
    print(midi.get_device_info(i))

s = []

fl = fluidsynth.Synth()

# Initial silence is 1 second
s = numpy.append(s, fl.get_samples(sample_size * 1))

sfid = fl.sfload(sys.argv[1])
fl.program_select(0, sfid, 0, 0)

fl.noteon(0, 60, velocity)
fl.noteon(0, 67, velocity)
fl.noteon(0, 76, velocity)


print('Starting playback 1')
#128 means released 144 means it was just pressed
is_pressed = False
for i in range(1000):
    if input.poll():
        #This is either 128 or 144
        action = input.read(1000)[0][0][0]
        if action == 144:
            is_pressed = True
        elif action == 128:
            is_pressed = False

    if is_pressed == False:
        time.sleep(1.0/times_per_sec)
    else:
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

input.close()
