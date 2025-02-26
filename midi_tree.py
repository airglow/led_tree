
"""
Requirements:
    pip install python-rtmidi serial numpy mido pyfluidsynth
Run like:
    python midi_tree.py
"""

import sys
import math
import numpy as np
import time
#from matplotlib import pyplot as plt
import mido
import rtmidi
from rtmidi import midiutil
from ledcontroller import LEDController
import fluidsynth
import colors


class MidiObject(object):
    """Docstring for MidiObject """

    def __init__(self):
        """@todo: to be defined """
        self.colors = colors.discriminative_colors
        self.list = []
        self.fader_value = 127
        self.notes = np.zeros((30, 3), dtype=np.uint8)
        self.ledcontroller = LEDController(30, port="/dev/led_tree")
        self.ledcontroller.all_off()
        self.mode = "COLOR"

    def set_note_by_color(self, color, brightness=128):
        self.notes[:, 0] = min(np.uint8(color[0] * brightness * 2), 254)
        self.notes[:, 1] = min(np.uint8(color[1] * brightness * 2), 254)
        self.notes[:, 2] = min(np.uint8(color[2] * brightness * 2), 254)

        print(self.notes)
        self.ledcontroller.set_config(self.notes)


class MidiHandler(MidiObject):
    """Docstring for MidiHandler """

    def __init__(self):
        super().__init__() 
#    def set_color_by_note(self, note):

    def __call__(self, event, data=None):
        event, deltatime = event
        command = event[0]
        note = event[1]

        note = note % len(self.notes)
        velocity = event[2] #  [0 ... 127]
        if command == 176:
            self.fader_value = velocity
        if command == 144:
            print("note pressed")
            self.set_note_by_color(self.colors[note])
            #  print(event, self.colors[note], velocity, deltatime)
            self.list.append({"time": deltatime, "event": event})
                #self.set_color_by_note()

            print(self.notes[note])
        if command == 128:
            print("note off")
            self.set_note_by_color([0,0,0])
            #self.ledcontroller.set_config(self.notes)

        #if command == 128 or command == 144:
        #    self.ledcontroller.set_config(self.notes)


class MidiPlayer(MidiObject):

    def __init__(self):
        super().__init__()
        self.synth = fluidsynth.Synth()
        self.synth.start(driver="alsa")
        sfid = self.synth.sfload("example.sf2")
        self.synth.program_select(0, sfid, 0, 0)

    def play(self, filename):
        mid = mido.MidiFile(filename)
        for msg in mid.play():
            if msg.type == "note_on":
                #print(msg.note)
                if msg.channel == 0:
                    #self.set_note_by_color(self.colors[msg.note])
                    self.set_note_by_color(self.colors[msg.note])
                    self.synth.noteon(0, msg.note, msg.velocity)
                    print(msg.note, msg.channel, msg.velocity)
            if msg.type == "note_off":
                if msg.channel == 0:
                    self.set_note_by_color([0, 0, 0])
                    self.synth.noteoff(0, msg.note)


mode = "midi_player"
#mode = "midi_controller"
if mode == "midi_controller":
    midi_in = rtmidi.MidiIn()
    midiutil.list_input_ports()

    midiin, port = midiutil.open_midiinput()

    midihandler = MidiHandler()
    midiin.set_callback(midihandler)

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print()
    finally:
        midiin.close_port()
        print(midihandler.list)
else:

    #ledcontroller = LEDController(60, port="/dev/led_tree")
    #for i in range(100):
    #    ledcontroller.all_off()
    #    time.sleep(2.0)
    #    ledcontroller.all_on()
    #    time.sleep(2.0)
    midi_player = MidiPlayer()
    midi_filename = sys.argv[1]
    print(midi_filename)
    midi_player.play(midi_filename)
