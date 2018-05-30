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
times_per_sec = 50

#The speed of the song
bpm = 120.0

#The amount of measures in the loop
measures = 4.0

#The time signature
beats_per_measure = 4.0

#Subdivide amount
subdivide = 4

current_run_count = 0

#The delay of the main loop to ensure it doesn't overwrite the other stuff
loop_delay = (60.0/(bpm*subdivide))
loop_delay_timer = time.time()

#The amount of time the previous seconds equate to in recording in seconds
loop_time = (60.0/bpm) * measures * beats_per_measure
loop_timer = time.time()

stream_count = 8

#Opens the audio stream to write to
pa = pyaudio.PyAudio()

#This enables multiple streams at once
streams = []
for i in range(stream_count):
    strm = pa.open(
        format = pyaudio.paInt32,
        channels = 2,
        rate = sample_size,
        output = True)
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
    audio_state = 0

    track = []
    track_str = ''
    track_pos = 0

    is_done = False

    #State 0: Playing
    #State 1: Recording
    #State 2: Playback
    #State 3: Idle

    def __init__(self, track_id, synth, instrument):
        threading.Thread.__init__(self)
        self.track_id = track_id
        self.synth = synth
        self.instrument = instrument

#Originally had this in all of the states but it seemed to glitch the audio out

#Waits to make sure it isn't too fast
# if time.time() - self.last_time < 1.0/times_per_sec:
#     #Sleep for the remaining time
#     time.sleep(1.0/times_per_sec - (time.time() - self.last_time))
#     self.last_time = time.time()


    def run(self):
        while True:
            #Stop the thread
            if self.is_done == True:
                break

            #The playing state
            if self.audio_state == 0:
                s = []
                s = numpy.append(s, self.synth.get_samples(int(sample_size/times_per_sec)))
                samps = fluidsynth.raw_audio_string(s)
                streams[self.track_id].write(samps)

            #The recording state
            elif self.audio_state == 1:
                s = []
                s = numpy.append(s, self.synth.get_samples(int(sample_size/times_per_sec)))
                samps = fluidsynth.raw_audio_string(s)
                streams[self.track_id].write(samps)

                #This adds everything that shows up in s into this track
                self.track = numpy.append(self.track, s)

            #The start playback state
            elif self.audio_state == 2:
                track_pos = 0
                self.audio_state = 3

            #The playback state
            elif self.audio_state == 3:
                if track_pos < len(self.track):
                    track_segment = self.track[track_pos:track_pos + int(len(self.track)/times_per_sec)]

                    #Updates where it is in the track
                    track_pos += int(len(self.track)/times_per_sec)

                    #Converts it into a string that can be outputted
                    self.track_str = fluidsynth.raw_audio_string(track_segment)
                    streams[self.track_id].write(self.track_str)

    def start_recording(self):
        self.audio_state = 1

    #Puts you into the playback state
    def stop_recording(self):
        self.audio_state = 2

    def start_playback(self):
        self.audio_state = 2

    def stop_thread(self):
        self.is_done = True

class MidiInput (threading.Thread):

    is_done = False

    def __init__(self, midi_controller, synth):
        threading.Thread.__init__(self)
        self.midi_controller = midi_controller
        self.synth = synth

    def run(self):
        while True:
            #Stops the thread
            if self.is_done == True:
                break

            m = self.midi_controller.getMessage(1) # some timeout in ms
            if m:
                #print_message(m)
                if m.isNoteOn():
                    is_pressed = True
                    self.synth.noteon(0, m.getNoteNumber(), m.getVelocity())
                elif m.isNoteOff():
                    is_pressed = False
                    self.synth.noteoff(0, m.getNoteNumber())

    def stop_thread(self):
        self.is_done = True


ports = range(midiin.getPortCount())
#m = midiin.getMessage(1) # some timeout in ms

if ports:
    for i in ports:
        print(midiin.getPortName(i))
    print("Opening port 0!")
    midiin.openPort(1)

    audio_players = []

    audio_player = AudioPlayer(0, fl, 'Guitar')
    midi_input = MidiInput(midiin, fl)

    audio_player.start()
    midi_input.start()

    audio_players.append(audio_player)

    print("Started recording...")
    audio_player.start_recording()

    loop_times = 0

    while True:
        #print("Loop ran")
        if current_run_count % subdivide == 0:
            print(int(current_run_count/4))

        if time.time() - loop_timer > loop_time:
            print("Stopped Recording")

            #Restart all of the players
            for player in audio_players:
                player.stop_recording()
                player.start_playback()

            #Create a new player for the next track
            new_player = AudioPlayer(len(audio_players), fl, 'Guitar')
            new_player.start_recording()
            new_player.start()

            audio_players.append(new_player)

            loop_timer = time.time()
            loop_times += 1
            current_run_count = 0

        #Waits to make sure it isn't too fast
        if time.time() - loop_delay_timer < loop_delay:
            #Sleep for the remaining time
            time.sleep(loop_delay - (time.time() - loop_delay_timer))
            loop_delay_timer = time.time()

        if loop_times > 6:
            break

        current_run_count += 1

    for player in audio_players:
        player.stop_thread()
    midi_input.stop_thread()
