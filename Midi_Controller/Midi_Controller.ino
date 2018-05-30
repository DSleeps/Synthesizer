#include "MIDI.h"

MIDI_CREATE_DEFAULT_INSTANCE();

//Previous values of the buttons
int p_1 = 1;
int p_2 = 1;

void setup() {
    MIDI.begin(1);
    Serial.begin(115200);
    pinMode(2,INPUT_PULLUP);
    pinMode(3,INPUT_PULLUP);
}

void loop() {
    int button_val_1 = digitalRead(2);
    int button_val_2 = digitalRead(3);

    byte a = (byte)button_val_1;

    MIDI.read();
    
    if (button_val_1 == 0 && p_1 == 1) {
        noteOn(48, 100, 1);
    }
    if (button_val_2 == 0 && p_2 == 1) {
        noteOn(56, 100, 1);
    }

    if (p_1 == 0 && button_val_1 == 1) {
        noteOff(48, 0, 1);
    }
    if (p_2 == 0 && button_val_2 == 1) {
        noteOff(56, 0, 1);
    }

    p_1 = button_val_1;
    p_2 = button_val_2;
}

void noteOn(int note, int velocity, int channel) {
    MIDI.sendNoteOn(note, velocity, channel);
}

void noteOff(int note, int velocity, int channel) {
    MIDI.sendNoteOff(note, velocity, channel);
}

//These are the functions for the MIDIUSB library which doesn't need the separate app

//void noteOn(int note, int velocity, int channel) {
//  midiEventPacket_t noteOn = {0x09, 0x90 | (byte)channel, (byte)note, (byte)velocity};
//  MidiUSB.sendMIDI(noteOn);
//}
//
//void noteOff(int note, byte velocity, int channel) {
//  midiEventPacket_t noteOff = {0x08, 0x80 | (byte)channel, (byte)note, (byte)velocity};
//  MidiUSB.sendMIDI(noteOff);
//}
//void controlChange(int conrol, int value, int channel) {
//  midiEventPacket_t event = {0x0B, 0xB0 | (byte)channel, (byte)control, (byte)value};
//  MidiUSB.sendMIDI(event);
//}
