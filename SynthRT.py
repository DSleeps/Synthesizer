import rtmidi
import time
import numpy
import pyaudio
import fluidsynth
import sys
import threading

sample_size = 44100
#sample_size = 22000

#Times per second that it checks the midi thing
times_per_sec = 100

#Opens the audio stream to write to
pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt32,
    channels = 2,
    rate = sample_size,
    output = True)

#This enables multiple streams at once
streams = []
streams.append(strm)

midiin = rtmidi.RtMidiIn()

fl = fluidsynth.Synth()

#This specifies the type of instrument
sfid = fl.sfload(sys.argv[1])
fl.program_select(0, sfid, 0, 0)

def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())

class AudioPlayer (threading.Thread):

    last_time = time.time()

    def __init__(self, track_id, synth, instrument):
        threading.Thread.__init__(self)
        self.track_id = track_id
        self.synth = synth
        self.instrument = instrument

    def run(self):
        while True:
            s = []
            s = numpy.append(s, self.synth.get_samples(int(sample_size/times_per_sec)))
            samps = fluidsynth.raw_audio_string(s)
            streams[self.track_id].write(samps)
            while time.time() - self.last_time < 1.0/times_per_sec:
                pass

class MidiInput (threading.Thread):

    def __init__(self, midi_controller, synth):
        threading.Thread.__init__(self)
        self.midi_controller = midi_controller
        self.synth = synth

    def run(self):
        while True:
            m = self.midi_controller.getMessage(1) # some timeout in ms
            if m:
                print_message(m)
                if m.isNoteOn():
                    is_pressed = True
                    self.synth.noteon(0, m.getNoteNumber(), m.getVelocity())
                elif m.isNoteOff():
                    is_pressed = False
                    self.synth.noteoff(0, m.getNoteNumber())


ports = range(midiin.getPortCount())
#m = midiin.getMessage(1) # some timeout in ms

if ports:
    for i in ports:
        print(midiin.getPortName(i))
    print("Opening port 0!")
    midiin.openPort(1)

    audio_player = AudioPlayer(0, fl, 'Guitar')
    midi_input = MidiInput(midiin, fl)

    audio_player.start()
    midi_input.start()

    audio_player.join()
    midi_input.join()
    
