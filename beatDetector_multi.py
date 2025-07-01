#!/usr/bin/env python3

import random
#import lightshow2
import ui
import sys
import logging
from PyQt5 import QtCore, QtWidgets
from bpm import SignalGenerator, AudioAnalyzer
from recorder import *
from protocol import send_beat_message

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

#TODO: BPM Button als beat Sender
#TODO

class BeatDetector:
    ui: ui.UserInterface
    # osc_client: osc.OscClient
    # artnet_client: artnet.ArtnetClient
    #lightshow_client: lightshow2.lightshow

    input_recorder: InputRecorder
    timer_period = int(round(1000 / (180 / 60) / 16))  # 180bpm / 16

    min_program_beats = 8
    max_program_beats = 64 * 4  # 64 Bars = Programmwechsel etwa alle 2 min

    current_intensity = 0
    current_program = 0
    current_program_beats = 0
    change_program = False
    calm_programs = [
        2,  # Full Color Slow
        5,  # Retro
        8,  # Wipe Noise
        10,
        11
    ]
    normal_programs = [
        1,  # Full Color Moving
        3,  # Fill Up Once
        6,  # Kit
        12,
        13,
    ]
    intense_programs = [
        4,  # Fill Up Repeat
        7,  # Flash Noise
        9,  # Flash Noise
        14,
        15
    ]

    def __init__(self, window) -> None:
        self.ui = ui.UserInterface(self.on_auto_prog_button_clicked,
                                   self.on_input_changed,
                                   self.on_main_dimmer_changed,
                                   self.on_grid_button_clicked,
                                   self.on_strobo 
                                   )

        self._bpm = 120
        
        self.ui.setup_ui(window)
        # self.osc_client = osc.OscClient("localhost", 7701)
        # self.artnet_client = artnet.ArtnetClient('192.168.2.52',0,120)
        #self.lightshow_client = lightshow2.lightshow()
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

        # Start beat detection
        self.timer = QtCore.QTimer()
        self.timer.start(self.timer_period)

        self.timer.timeout.connect(self.audio_analyzer.analyze_audio)
        self.input_recorder.start()
        
        self.on_auto_prog_button_clicked()

    def on_strobo(self):
        """
        Wird alle 100 ms aufgerufen, solange der Strobo-Button gedrückt ist.
        Hier kannst du z. B. einen Blitz-Effekt oder dein Lightshow-Strobo-Signal auslösen.
        """
        # Beispiel: schicke ein Strobe-Signal an den Client
        # self.lightshow_client.send_strobe_signal()

    def on_grid_button_clicked(self, index: int):
        # wenn einer der 16 Buttons gedrückt wird, führe Programm-Wechsel aus
        # schalte Auto-Prog aus

        self.auto_prog = False
        self.ui.change_auto_prog_state(False)
        # setze das neue Programm
        self.current_program = index
        self.current_program_beats = 0
        self.ui.highlight_grid_button(index)
        # sende das Programm-Signal an den Lightshow-Client
        # self.lightshow_client.send_prog_signal(index)
        # optional: UI-Feedback, z.B. Label aktualisieren
        logger.info(f"Programm gewechselt auf {index}")

    def change_program_if_needed(self):
        if self.change_program and self.current_program_beats >= self.min_program_beats:
            new_program = self.choose_program_by_intensity()
            # self.artnet_client.changeColorScroll(new_program)
            if new_program != self.current_program:
                logger.info("Change program to {:d} for intensity {:d}".format(new_program, self.current_intensity))
                self.current_program = new_program
                # self.osc_client.send_prog_signal(new_program)
                # self.lightshow_client.send_prog_signal(new_program)
            self.current_program_beats = 1
            self.change_program = False
            self.ui.highlight_grid_button(new_program)

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
        pass # self.lightshow_client.setMainDimmer(value)

    def on_beat(self, beat_index):
        # self.lightshow_client.send_beat_signal()     
        # self.artnet_client.artNetShow(beat_index)

        # self.ui.change_beat_button_color()
        beat_period_millis = int(60 / self._bpm * 1000)
        send_beat_message(beat_period_millis)

        self.ui.display_beat_index(beat_index + 1)  # Starts with 0
        self.ui.change_beat_button_color()
        # Keep track how long current program is running
        if self.auto_prog:
            self.current_program_beats += 1
            if self.current_program_beats > self.max_program_beats:
                self.change_program = True

    def on_bar(self):
        logger.info("bar")
        self.change_program_if_needed()
        #TODO Hier Hook um tatsächlich bar animationen zu starten!
        # self.lightshow_client.send_bar_signal()
        self.ui.change_bar_button_color()

    def on_new_song(self):
        logger.info("next song")
        #self.change_program = True
        #self.ui.display_new_song()

    def on_bpm_change(self, bpm):
        logger.info(f"bpm changed: {bpm}")
        self._bpm = bpm
        self.ui.display_bpm(bpm)

    def on_intensity_change(self, intensity):
        self.current_intensity = intensity
        if self.auto_prog:
            self.change_program = True
        self.ui.display_intensity(intensity)

        # self.lightshow_client.intensityChange(intensity)

    def close(self):
        self.input_recorder.close()
        # self.lightshow_client.close()


if __name__ == "__main__":
    # Setup UI
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    # Start beat tracking
    beat_detector = BeatDetector(window)

    # Display window
    # window.show()
    window.showMaximized()
    code = app.exec_()

    # Clean up
    beat_detector.close()
    
    sys.exit(code)
