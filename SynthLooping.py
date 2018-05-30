import time
import numpy
import pyaudio
import fluidsynth
import sys
from pygame import midi

sample_size = 44100

#Number of times that the voices are played per second
times_per_sec = 100

#The number of separate voices that can exist at any given time
voice_num = 10

#Opens all of the streams to output the audio
pa = pyaudio.PyAudio()
strms = [pa.open(
    format = pyaudio.paInt32,
    channels = 2,
    rate = sample_size,
    output = True),
    for i in range(voice_num)]

#Initializes an array which will be filled with loops
loops = []
for i in range(voice_num):
    loops.append(0)

#Initializing the Midi keyboard
midi.init()
INPUTNO = 3     #Hardcoded this as 3 because that's what I found it to be
input = midi.Input(INPUTNO)

#Prints all of the different midi devices
for i in range(midi.get_count()):
    print(midi.get_device_info(i))

#Initializes the synth and it's different sounds
fl = fluidsynth.Synth()
sfid = fl.sfload(sys.argv[1])
fl.program_select(0, sfid, 0, 0)


'''Functions'''
def play_note(note, velocity, synth, strm_num):
    synth.noteon(0, note, velocity)
    s = []
    s = numpy.append(s, fl.get_samples(int(sample_size/times_per_sec)))
    samps = fluidsynth.raw_audio_string(s)
    strms.write(samps)
    print('Played')

def record():
    for loop in loops:
        if loop != 0:
            
#128 means released 144 means it was just pressed
is_pressed = False
while True:
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
        strms.write(samps)
