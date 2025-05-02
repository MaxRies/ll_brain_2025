from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QLabel, QSlider, QGridLayout

class UserInterface(object):
    auto_prog_button: QPushButton
    intensity_label: QLabel
    beat_label: QLabel
    bar_label: QLabel
    strobo_button: QPushButton

    main_dimmer_label: QLabel
    main_dimmer: QSlider
    colorsList = ["#a9a9a9", "#f58231", "#ffe119", "#bfef45", "#3cb44b", "#42d4f4", "#4363d8", "#f032e6"]
    beat_color_index = 0
    bar_color_index = 0

    def __init__(self, auto_prog_callback, callback_input_changed, main_dimmer_changed, callback_grid_button, callback_strobo):
        self.callback_auto_prog_clicked = auto_prog_callback
        self.callback_input_changed = callback_input_changed
        self.callback_main_dimmer_changed = main_dimmer_changed
        self.callback_grid_button = callback_grid_button
        self.callback_strobo = callback_strobo
        # Aktuell markierter Grid-Button
        self.current_grid_index = None
        # Timer für Strobo-Funktion
        self.strobo_timer = QTimer()
        self.strobo_timer.setInterval(100)
        self.strobo_timer.timeout.connect(self.callback_strobo)

    def setup_ui(self, win_plot):
        win_plot.setObjectName("win_plot")
        win_plot.resize(800, 350)
        central_widget = QtWidgets.QWidget(win_plot)

        main_hlayout = QtWidgets.QHBoxLayout(central_widget)

        # --- Linke Spalte: Controls ---
        controls_layout = QtWidgets.QVBoxLayout()

        # Input Bereich
        input_widget = QtWidgets.QWidget(central_widget)
        input_widget.setFixedHeight(95)
        vertical_layout_input = QtWidgets.QVBoxLayout(input_widget)

        self.input_label = QtWidgets.QLabel(central_widget)
        self.input_combobox = QtWidgets.QComboBox(central_widget)
        self.input_combobox.setStyleSheet(
            "background-color: #a9a9a9; font-size: 15pt;"
            "selection-background-color: transparent; selection-color: black"
        )
        self.input_combobox.activated.connect(self.callback_input_changed)

        self.input_intensity = QtWidgets.QProgressBar(central_widget)
        self.input_intensity.setStyleSheet(
            "QProgressBar { border: 2px solid grey; border-radius: 0px; text-align: center; }"
            "QProgressBar::chunk {background-color: #3add36; width: 1px;}"
        )
        self.input_intensity.setTextVisible(False)
        self.input_intensity.setFixedHeight(15)
        self.input_intensity.setValue(0)

        vertical_layout_input.addWidget(self.input_label)
        vertical_layout_input.addWidget(self.input_combobox)
        vertical_layout_input.addWidget(self.input_intensity)
        controls_layout.addWidget(input_widget)

        # Auto Prog Button
        self.auto_prog_button = QtWidgets.QPushButton(central_widget)
        self.auto_prog_button.setStyleSheet("background-color: red; font-size: 18pt")
        self.auto_prog_button.clicked.connect(self.callback_auto_prog_clicked)
        controls_layout.addWidget(self.auto_prog_button)


        # Status Labels
        self.intensity_label = QLabel("Intensity", central_widget)
        self.intensity_label.setStyleSheet(
            "padding: 5px; qproperty-alignment: AlignCenter; background-color: #a9a9a9; font-size: 18pt"
        )
        controls_layout.addWidget(self.intensity_label)

        self.beat_label = QLabel("Beat", central_widget)
        self.beat_label.setStyleSheet(
            "padding: 5px; qproperty-alignment: AlignCenter; background-color: #a9a9a9; font-size: 18pt"
        )
        controls_layout.addWidget(self.beat_label)

        self.bar_label = QLabel("BPM", central_widget)
        self.bar_label.setStyleSheet(
            "padding: 5px; qproperty-alignment: AlignCenter; background-color: #a9a9a9; font-size: 18pt"
        )
        controls_layout.addWidget(self.bar_label)

        # Main Dimmer
        self.main_dimmer_label = QLabel("main dimmer", central_widget)
        self.main_dimmer_label.setStyleSheet("padding: 5px; qproperty-alignment: AlignCenter; font-size: 18pt")
        controls_layout.addWidget(self.main_dimmer_label)

        self.main_dimmer = QSlider(Qt.Horizontal)
        self.main_dimmer.setMinimum(0)
        self.main_dimmer.setMaximum(255)
        self.main_dimmer.setValue(128)
        self.main_dimmer.setTickPosition(QSlider.TicksBelow)
        self.main_dimmer.setTickInterval(10)
        self.main_dimmer.setFixedHeight(50)
        self.main_dimmer.valueChanged.connect(self.on_main_dimmer_changed)
        controls_layout.addWidget(self.main_dimmer)


        # Strobo Button (löst alle 100ms callback aus, solange gedrückt)
        self.strobo_button = QtWidgets.QPushButton("Strobo", central_widget)
        self.strobo_button.setCheckable(True)
        self.strobo_button.setFixedHeight(60)
        self.strobo_button.pressed.connect(self.on_strobo_pressed)
        self.strobo_button.released.connect(self.on_strobo_released)
        controls_layout.addWidget(self.strobo_button)


        main_hlayout.addLayout(controls_layout)

        # --- Rechte Spalte: 4x4 Button Grid ---
        grid_widget = QtWidgets.QWidget(central_widget)
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)
        self.grid_buttons = []
        for row in range(4):
            for col in range(4):
                idx = row * 4 + col
                btn = QPushButton(f"B{idx+1}")
                btn.setFixedSize(80, 80)
                btn.clicked.connect(lambda checked, i=idx: self.on_grid_button_clicked(i))
                grid_layout.addWidget(btn, row, col)
                self.grid_buttons.append(btn)
        main_hlayout.addWidget(grid_widget)




        win_plot.setCentralWidget(central_widget)
        self.translate_ui(win_plot)
        QtCore.QMetaObject.connectSlotsByName(win_plot)

    def on_strobo_pressed(self):
        # Starte den Timer, der alle 100ms callback_strobo aufruft
        self.strobo_timer.start()

    def on_strobo_released(self):
        # Stoppe den Strobo-Timer
        self.strobo_timer.stop()

    def on_grid_button_clicked(self, index: int):
        # Callback nach außen
        self.callback_grid_button(index)
        # UI-Highlight aktualisieren
        self.highlight_grid_button(index)

    def highlight_grid_button(self, index: int):
        # vorherigen Reset
        if self.current_grid_index is not None:
            prev = self.grid_buttons[self.current_grid_index]
            prev.setStyleSheet("")
        # neuen Button grün färben
        new = self.grid_buttons[index]
        new.setStyleSheet("background-color: green; font-size: 18pt;")
        self.current_grid_index = index

    # ... Rest der Methoden (translate_ui, callbacks, color-changes, display_*) bleiben unverändert ...


    def on_main_dimmer_changed(self):
        self.callback_main_dimmer_changed (self.main_dimmer.value())

    def translate_ui(self, win_plot):
        win_plot.setWindowTitle(QtWidgets.QApplication.translate("win_plot", "Beat Detector", None))
        self.auto_prog_button.setText(QtWidgets.QApplication.translate("win_plot", "Auto Prog OFF", None))
        self.intensity_label.setText(QtWidgets.QApplication.translate("win_plot", "Intensity", None))
        self.beat_label.setText(QtWidgets.QApplication.translate("win_plot", "Beat", None))
        self.bar_label.setText(QtWidgets.QApplication.translate("win_plot", "BPM", None))
        self.input_label.setText(QtWidgets.QApplication.translate("win_plot", "Audio Source", None))
        self.main_dimmer_label.setText(QtWidgets.QApplication.translate("win_plot", "main dimmer", None))

    def change_auto_prog_state(self, enabled):
        if enabled:
            self.auto_prog_button.setText("Auto Prog ON")
            self.auto_prog_button.setStyleSheet("background-color: green; font-size: 18pt")
        else:
            self.auto_prog_button.setText("Auto Prog OFF")
            self.auto_prog_button.setStyleSheet("background-color: red; font-size: 18pt")

    def change_beat_button_color(self):
        self.beat_color_index += 1
        color = self.colorsList[self.beat_color_index % len(self.colorsList)]
        self.beat_label.setStyleSheet("padding: 5px; qproperty-alignment: AlignCenter; background-color: {:s}; font-size: 18pt".format(color))

    def change_bar_button_color(self):
        self.bar_color_index += 1
        color = self.colorsList[self.bar_color_index % len(self.colorsList)]
        self.bar_label.setStyleSheet("padding: 5px; qproperty-alignment: AlignCenter; background-color: {:s}; font-size: 18pt".format(color))

    def display_intensity(self, intensity):
        if intensity == 1:
            intensity_label = "Intense"
        elif intensity == 0:
            intensity_label = "Normal"
        else:
            intensity_label = "Calm"
        self.intensity_label.setText(intensity_label)

    def display_beat_index(self, beat_index):
        self.beat_label.setText("Beat: {:d}".format(beat_index))

    def display_bpm(self, bpm):
        self.bar_label.setText("BPM: {:d}".format(int(bpm)))

    def display_new_song(self):
        self.beat_label.setText("Beat")
        self.bar_label.setText("BPM: New song")

    def add_audio_source(self, text):
        self.input_combobox.addItem(text)

    def select_audio_source(self, index):
        self.input_combobox.setCurrentIndex(index)

    def display_input_intensity(self, level):
        self.input_intensity.setValue(int(level))
