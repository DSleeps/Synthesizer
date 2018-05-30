#include "MIDI.h"

MIDI_CREATE_DEFAULT_INSTANCE();

//The number of buttons
int button_count = 12;

//The number of the main keys
int main_button_count = 6;

//The array index corresponds to the index in the fingerings string
//The last ones should be the auxiallary keys i.e The G# key, D# key, ect

//For now 6th is biss key, 7th is G# key, 8th is D# key, 9th is side Bb key, 10th is side C key, and 11th is alternate F#
int button_pins [12] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

//All of the sax fingerings. 0 means the key is down
String fingerings = String("111111\n") +
                    String("101111\n") +
                    String("011111\n") +
                    String("011011\n") +
                    String("001111\n") +
                    String("000111\n") +
                    String("000101\n") +
                    String("000011\n") +
                    String("000001\n") +
                    String("000000\n");

//The number of different fingerings
int fingering_count = 10;

//These notes correspond to the line the fingering is on
int notes [10] = {37, 36, 35, 34, 33, 31, 30, 29, 28, 26};

int previous_note = 0;

void setup() {
    MIDI.begin(1);
    Serial.begin(115200);

    //Initializes all of the buttons
    for (int i = 0; i < button_count; i++) {
        pinMode(button_pins[i], INPUT_PULLUP);
    }
}

void loop() {
    String current_fingering = "";
    for (int i = 0; i < main_button_count; i++) {
        current_fingering += String(digitalRead(button_pins[i]));
    }

    MIDI.read();

    //Now check which fingering this is
    String f_list = fingerings;
    int index = 0;

    //For now 6th is biss key, 7th is G# key, 8th is D# key, 9th is side A# key, 10th is side C key, and 11th is alternate F#
    while (true) {
        String fingering_test = f_list.substring(0, f_list.indexOf("\n"));
        if (fingering_test == current_fingering) {
            int current_note = notes[index];
            
            //Special cases for alternate fingerings
            if (fingering_test == String("011111") && digitalRead(button_pins[6]) == 0) {
                current_note += -1;
            } else if (fingering_test == String("011111") && digitalRead(button_pins[10]) == 0) {
                current_note += 1;
            } else if (fingering_test == String("001111") && digitalRead(button_pins[9]) == 0) {
                current_note += 1;
            } else if (fingering_test == String("000111") && digitalRead(button_pins[7]) == 0) {
                current_note += 1;
            } else if (fingering_test == String("000000") && digitalRead(button_pins[8]) == 0) {
                current_note += 1;
            } else if (fingering_test == String("000011") && digitalRead(button_pins[11]) == 0) {
                current_note += 1;
            }

            if (current_note != previous_note) {
                //Serial.println(String(current_note) + " ON!");
                //Serial.println(String(previous_note) + " OFF!");
                noteOn(current_note, 100, 1);
                noteOff(previous_note, 0, 1);
            }
            previous_note = current_note;
            
            break;
        } else {
            index += 1;

            //If it's none of the fingerings just break
            if (index >= fingering_count) {
                previous_note = -1;
                break;
            }
            f_list = f_list.substring(f_list.indexOf("\n") + 1);
        }
    }
    
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
