#include "MIDI.h"

MIDI_CREATE_DEFAULT_INSTANCE();

//Previous values of the buttons
int p_1 = 0;
int p_2 = 0;

void setup() {
    Serial.begin(115200);
    pinMode(2,INPUT_PULLUP);
    pinMode(3,INPUT_PULLUP);

    MIDI.begin(MIDI_CHANNEL_OMNI);
}

void loop() {
    int button_val_1 = digitalRead(2);
    int button_val_2 = digitalRead(3);
    Serial.println(button_val_1);
    Serial.println(button_val_2);

    if (button_val_1 == 0) {
        MIDI.sendNoteOn(48, 100, 0);
    }
    if (button_val_2 == 0) {
        MIDI.sendNoteOn(56, 100, 0);
    }

    if (p_1 == 0 && button_val_1 == 1) {
        MIDI.sendNoteOff(48, 0);
    }
    if (p_2 == 0 && button_val_2 == 1) {
        MIDI.sendNoteOff(56, 0);
    }

    MIDI.read();

    p_1 = button_val_1;
    p_2 = button_val_2;
}
