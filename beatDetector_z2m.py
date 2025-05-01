import random

import osc
import artnet
# pip install paho-mqtt
# import z2mLamps
from z2mLamps import BeatLampController

import ui
import sys
from PyQt5 import QtCore, QtWidgets
from bpm import SignalGenerator, AudioAnalyzer
from recorder import *


class BeatDetector:
    ui: ui.UserInterface
    # osc_client: osc.OscClient
    # artnet_client: artnet.ArtnetClient
    # beat_controller: z2mLamps.z2mLamps
    

    input_recorder: InputRecorder
    timer_period = int(round(1000 / (180 / 60) / 16))  # 180bpm / 16

    min_program_beats = 8
    max_program_beats = 8 * 4

    current_intensity = 0
    current_program = 0
    current_program_beats = 0
    change_program = False
    calm_programs = [
        2,  # Full Color Slow
        5,  # Retro
        8,  # Wipe Noise
    ]
    normal_programs = [
        1,  # Full Color Moving
        3,  # Fill Up Once
        6,  # Kitt
    ]
    intense_programs = [
        4,  # Fill Up Repeat
        7,  # Flash Noise
    ]

    def __init__(self, window) -> None:
        self.ui = ui.UserInterface(self.on_auto_prog_button_clicked, self.on_input_changed, self.on_main_dimmer_changed)
        self.ui.setup_ui(window)
        # self.osc_client = osc.OscClient("localhost", 7701)
        # self.artnet_client = artnet.ArtnetClient('192.168.2.52',0,120)

        BROKER = "192.168.178.50"
        PORT = 1883
        lamp_topics = [
            "zigbee2mqtt/WSP_A3/set",
            "zigbee2mqtt/WSP_A5/set",
            "zigbee2mqtt/WSP_B2/set",
            "zigbee2mqtt/WSP_B8/set",
            "zigbee2mqtt/WSP_C6/set",
            "zigbee2mqtt/WSP_C7/set",
            # "zigbee2mqtt/WSP_C8/set",
            "zigbee2mqtt/WSP_C9/set",
            "zigbee2mqtt/WSP_C10/set",
            "zigbee2mqtt/WSP_C11/set",
            # "zigbee2mqtt/WSP_C12/set",
            "zigbee2mqtt/WSP_C13/set"
        ]

        # lamp_topics = ['WSP_A3', 'WSP_A5', 'WSP_B2', 'WSP_B8', 'WSP_C6', 'WSP_C7', 'WSP_C9', 'WSP_C10', 'WSP_C11', 'WSP_C13']

        self.beat_controller = BeatLampController(BROKER, PORT, lamp_topics, blink_duration=0.2)

        self.auto_prog = False

        # Wire up beat detector and signal generation
        self.input_recorder = InputRecorder(self)
        self.audio_analyzer = AudioAnalyzer(self.input_recorder)
        signal_generator = SignalGenerator(self.audio_analyzer)


       

        # Wire up callbacks
        signal_generator.on_beat(self.on_beat)
        signal_generator.on_bar(self.on_bar)
        signal_generator.on_new_song(self.on_new_song)
        signal_generator.on_bpm_change(self.on_bpm_change)
        signal_generator.on_intensity_change(self.on_intensity_change)

        # signal_generator.callback_beat_track(self.artnetBeat)


        # Start beat detection
        self.timer = QtCore.QTimer()
        self.timer.start(self.timer_period)

        self.timer.timeout.connect(self.audio_analyzer.analyze_audio)
        self.input_recorder.start()
        
        self.on_auto_prog_button_clicked()


    def change_program_if_needed(self):
        if self.change_program and self.current_program_beats >= self.min_program_beats:
            new_program = self.choose_program_by_intensity()
            # self.artnet_client.changeColorScroll(new_program)
            self.beat_controller.select_pattern(new_program)

            if new_program != self.current_program:
                # print("Change program to {:d} for intensity {:d}".format(new_program, self.current_intensity))
                self.current_program = new_program
                # self.osc_client.send_prog_signal(new_program)
            self.current_program_beats = 1
            self.change_program = False

    def choose_program_by_intensity(self):
        if self.current_intensity == 1:
            program_list = self.intense_programs
        elif self.current_intensity == -1:
            program_list = self.calm_programs
        else:
            program_list = self.normal_programs
        return random.choice(program_list)

    def on_auto_prog_button_clicked(self):
        self.auto_prog = not self.auto_prog
        self.current_program = 0
        self.current_program_beats = 0
        if self.auto_prog:
            self.change_program = True
        self.ui.change_auto_prog_state(self.auto_prog)

    def on_input_changed(self, index):
        self.input_recorder.change_input(index)

    def on_main_dimmer_changed(self, value):
        # self.artnet_client.mainDimmer = value
        # self.beat_controller.update_on_beat()
        # print("Maindimmer {}".format(value))
        self.beat_controller.apply_dimmer(value/255.0)        
        # pass

    def artnetBeat(self):
        # self.artnet_client.artNetShow()
        self.beat_controller.update_on_beat()

    def on_beat(self, beat_index):
        # print("beat")
        # self.osc_client.send_beat_signal()      
        # self.artnet_client.artNetShow(beat_index)
        self.beat_controller.update_on_beat()

        # self.ui.change_beat_button_color()
        self.ui.display_beat_index(beat_index + 1)  # Starts with 0

        if beat_index % 2 == 0:
            beat_index /= 2
            # Keep track how long current program is running
            if self.auto_prog:
                self.current_program_beats += 1
                if self.current_program_beats > self.max_program_beats:
                    self.change_program = True

    def on_bar(self):
        # print("bar")
        self.change_program_if_needed()
        # self.osc_client.send_bar_signal()
        self.ui.change_bar_button_color()

    def on_new_song(self):
        # print("next song")
        self.change_program = True
        self.ui.display_new_song()

    def on_bpm_change(self, bpm):
        # print("bpm changed")
        self.ui.display_bpm(bpm)

    def on_intensity_change(self, intensity):
        self.current_intensity = intensity
        if self.auto_prog:
            self.change_program = True
        self.ui.display_intensity(intensity)

    def close(self):
        self.input_recorder.close()
        # self.artnet_client.artNetNode.close()
        self.beat_controller.disconnect()


if __name__ == "__main__":
    # Setup UI
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # Start beat tracking
    beat_detector = BeatDetector(window)

    # Display window
    window.show()
    code = app.exec_()

    # Clean up
    beat_detector.close()
    
    sys.exit(code)
