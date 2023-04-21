from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt

import CycleSequence as cs
import FilterWindow as fw

class SequenceWindow(QWidget):
    def __init__(self, ecg_cycle, parent=None):
        super().__init__(parent)
        self.setGeometry(300, 300, 700, 400)
        self.setWindowTitle('Послідовність кардіоциклів')
        self.setStyleSheet('''
        QMainWindow {
            background-color: #FFFFFF;
        }''')
        self.raw_ecg_sequence = cs.CycleSequence(ecg_cycle, 30)
        self.noisy_ecg_sequence = self.raw_ecg_sequence

        # plot widgets

        grid = QGridLayout()
        self.setLayout(grid)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel(axis='bottom', text='Час (с)', color='black')
        self.graphWidget.setLabel(axis='left', text='Амплітуда (мВ)', color='black')
        self.graphWidget.setMenuEnabled()
        self.graphWidget.setBackground('w')
        self.graphWidget.showButtons()
        self.graphWidget.showGrid(x=True, y=True, alpha=1)
        self.graphWidget.setMouseEnabled(y=False)

        pen = pg.mkPen(color="k", width=2, style=Qt.PenStyle.SolidLine)
        self.points = self.graphWidget.plot(pen=pen)

        grid.addWidget(self.graphWidget, 0, 0, 1, 4)

        # n spinbox
        
        self.n_group = QGroupBox()
        self.n_layout = QHBoxLayout()
        self.n_group.setLayout(self.n_layout)
        self.n_group.setTitle('Кількість циклів')

        self.n_input = QSpinBox()
        self.n_input.setMinimum(1)
        self.n_input.setValue(30)
        self.n_input.valueChanged.connect(self.update_n)
        self.n_input.setKeyboardTracking(False)
        self.n_layout.addWidget(self.n_input)
        
        grid.addWidget(self.n_group, 1, 0)

        # alternation slider

        self.slider_alt = QSlider(Qt.Orientation.Horizontal)
        
        self.alt_group = QGroupBox()
        self.alt_group.setTitle('Рівень альтерації (мВ)')

        self.alt_vlayout = QVBoxLayout()
        self.alt_group.setLayout(self.alt_vlayout)
        self.alt_hlayout = QHBoxLayout()
        self.alt_vlayout.addLayout(self.alt_hlayout)

        self.alt_label1 = QLabel()
        self.alt_label1.setText('-1')
        self.alt_hlayout.addWidget(self.alt_label1)
        
        self.slider_alt.setMinimum(-100)
        self.slider_alt.setMaximum(100)
        self.slider_alt.setSingleStep(1)
        self.slider_alt.setValue(0)
        self.slider_alt.valueChanged.connect(self.update_alt)
        self.alt_hlayout.addWidget(self.slider_alt)
        
        self.alt_label2 = QLabel()
        self.alt_label2.setText('1')
        self.alt_hlayout.addWidget(self.alt_label2)

        self.slider_alt_value = QLabel()
        self.slider_alt_value.setText('0')
        self.alt_vlayout.addWidget(self.slider_alt_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.alt_group, 1, 1)

        # amplitude slider

        self.slider_noise = QSlider(Qt.Orientation.Horizontal)
        
        self.slider_noise_group = QGroupBox()
        self.slider_noise_group.setTitle('Рівень шуму')

        self.slider_noise_vlayout = QVBoxLayout()
        self.slider_noise_group.setLayout(self.slider_noise_vlayout)
        self.slider_noise_hlayout = QHBoxLayout()
        self.slider_noise_vlayout.addLayout(self.slider_noise_hlayout)

        self.slider_noise_label1 = QLabel()
        self.slider_noise_label1.setText('0')
        self.slider_noise_hlayout.addWidget(self.slider_noise_label1)
        
        self.slider_noise.setMinimum(0)
        self.slider_noise.setMaximum(100)
        self.slider_noise.setSingleStep(1)
        self.slider_noise.setValue(0)
        self.slider_noise.valueChanged.connect(self.update_noise)
        self.slider_noise_hlayout.addWidget(self.slider_noise)
        
        self.slider_noise_label2 = QLabel()
        self.slider_noise_label2.setText('1')
        self.slider_noise_hlayout.addWidget(self.slider_noise_label2)

        self.slider_noise_value = QLabel()
        self.slider_noise_value.setText('0')
        self.slider_noise_vlayout.addWidget(self.slider_noise_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.slider_noise_group, 1, 2)

        # filter button

        self.button = QPushButton('Згладжування')
        self.button.setStyleSheet('''
        QPushButton {
            background-color: #007AD9;
            font-size: 14px;
            font-weight: bold;
            color: #FFFFFF;
            border: 2px solid;
            border-color: #007AD9;
            padding: 5px;
            padding-top: 2px;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
            color: #007AD9;
        }
        ''')
        self.button.clicked.connect(self.show_new_window)
        grid.addWidget(self.button, 1, 3)

        self.on_update(self.raw_ecg_sequence)

    def on_update(self, ecg_sequence):
        """ Update the plot with the current input values """

        self.points.setData(ecg_sequence.time_seq / 1000, ecg_sequence.amp_seq)

    def update_n(self):
        n_new = int(self.n_input.value())
        self.raw_ecg_sequence = cs.CycleSequence(self.raw_ecg_sequence.ecg_cycle, n_new)
        self.update_alt()

    def update_alt(self):
        alt = self.slider_alt.value() / 100
        self.slider_alt_value.setText(f'[{alt}]')
        self.raw_ecg_sequence.alternate_t(alt)
        self.update_noise()
    
    def update_noise(self):
        noise_level = self.slider_noise.value() / 100
        self.slider_noise_value.setText(f'[{noise_level}]')
        noisy_amp_seq = self.raw_ecg_sequence.amp_seq + self.raw_ecg_sequence.generate_noise(noise_level)
        self.noisy_ecg_sequence = cs.CycleSequence(time_seq=self.raw_ecg_sequence.time_seq,
                                                 amp_seq=noisy_amp_seq)
        self.on_update(self.noisy_ecg_sequence)

    def to_sequence(self, ecg_cycle):
        self.raw_ecg_sequence = cs.CycleSequence(ecg_cycle, self.raw_ecg_sequence.n)
        self.update_alt()
    
    def show_new_window(self, checked):
        Ts = self.raw_ecg_sequence.ecg_cycle.Ts
        self.w_new = fw.FilterWindow(self.noisy_ecg_sequence, Ts)
        self.w_new.show()
