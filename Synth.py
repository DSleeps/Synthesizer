import time
import fluidsynth
import sys

fs = fluidsynth.Synth()
fs.start()

print(sys.argv)
sfid = fs.sfload(sys.argv[2][0])
fs.program_select(0, sfid, 0, 0)

fs.noteon(0, 60, 30)
fs.noteon(0, 67, 30)
fs.noteon(0, 76, 30)

time.sleep(1.0)

fs.noteoff(0, 60)
fs.noteoff(0, 67)
fs.noteoff(0, 76)

time.sleep(1.0)

fs.delete()
