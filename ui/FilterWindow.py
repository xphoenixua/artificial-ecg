from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt

import calculations.CycleSequence as cs
import calculations.FilteringAlgorithms as fa

# window of ECG signal filtering
class FilterWindow(QWidget):
    def __init__(self, ecg_sequence, Ts, parent=None):
        super().__init__(parent)

        # window styling
        self.setGeometry(500, 200, 700, 400)
        self.setWindowTitle('Filtration of random noise')
        self.setStyleSheet('''
        QWidget {
            background-color: #FFFFFF;
        }''')
        
        # receiving parameters from the sequence window
        self.noisy_ecg_sequence = ecg_sequence
        self.Ts = Ts

        # initialize grid for the window
        grid = QGridLayout()
        self.setLayout(grid)

        # initialize graph
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel(axis='bottom', text='Time (s)', color='black')
        self.graphWidget.setLabel(axis='left', text='Amplitude (mV)', color='black')
        self.graphWidget.setMenuEnabled()
        self.graphWidget.setBackground('w')
        self.graphWidget.showButtons()
        self.graphWidget.showGrid(x=True, y=True, alpha=1)
        self.graphWidget.setMouseEnabled(y=False)

        pen = pg.mkPen(color="k", width=2, style=Qt.PenStyle.SolidLine)
        self.points = self.graphWidget.plot(pen=pen)

        grid.addWidget(self.graphWidget, 0, 0, 1, 3)

        # initialize alpha value slider (exponential filtering)
        self.slider_alpha = QSlider(Qt.Orientation.Horizontal)
        
        self.alpha_group = QGroupBox()
        self.alpha_group.setTitle('Parameter α')

        self.alpha_vlayout = QVBoxLayout()
        self.alpha_group.setLayout(self.alpha_vlayout)
        self.alpha_hlayout = QHBoxLayout()
        self.alpha_vlayout.addLayout(self.alpha_hlayout)

        self.alpha_label1 = QLabel()
        self.alpha_label1.setText('0')
        self.alpha_hlayout.addWidget(self.alpha_label1)
        
        self.slider_alpha.setMinimum(1)
        self.slider_alpha.setMaximum(99)
        self.slider_alpha.setSingleStep(1)
        self.slider_alpha.setValue(0)
        self.slider_alpha.setEnabled(False)
        self.slider_alpha.valueChanged.connect(self.update_alpha)
        self.alpha_hlayout.addWidget(self.slider_alpha)
        
        self.alpha_label2 = QLabel()
        self.alpha_label2.setText('1')
        self.alpha_hlayout.addWidget(self.alpha_label2)

        self.slider_alpha_value = QLabel()
        self.slider_alpha_value.setText(f'[{self.slider_alpha.value() / 100}]')
        self.alpha_vlayout.addWidget(self.slider_alpha_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.alpha_group, 1, 0)

        # initialize window (filtering) width slider (sliding average filtering)
        self.slider_winwidth = QSlider(Qt.Orientation.Horizontal)
        
        self.winwidth_group = QGroupBox()
        self.winwidth_group.setTitle('Window width (ms)')

        self.winwidth_vlayout = QVBoxLayout()
        self.winwidth_group.setLayout(self.winwidth_vlayout)
        self.winwidth_hlayout = QHBoxLayout()
        self.winwidth_vlayout.addLayout(self.winwidth_hlayout)

        self.winwidth_label1 = QLabel()
        self.winwidth_label1.setText('1')
        self.winwidth_hlayout.addWidget(self.winwidth_label1)
        
        self.slider_winwidth.setMinimum(1)
        self.slider_winwidth.setMaximum(100)
        self.slider_winwidth.setSingleStep(1)
        self.slider_winwidth.setValue(1)
        self.slider_winwidth.setEnabled(False)
        self.slider_winwidth.valueChanged.connect(self.update_winwidth)
        self.winwidth_hlayout.addWidget(self.slider_winwidth)
        
        self.winwidth_label2 = QLabel()
        self.winwidth_label2.setText('100')
        self.winwidth_hlayout.addWidget(self.winwidth_label2)

        self.slider_winwidth_value = QLabel()
        self.slider_winwidth_value.setText(f'[{self.slider_winwidth.value()}]')
        self.winwidth_vlayout.addWidget(self.slider_winwidth_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.winwidth_group, 1, 1)

        # initializing radio buttons for switching types of filtering
        self.filter_group = QGroupBox()
        self.filter_group.setTitle('Filtering method')

        self.filter_vlayout = QVBoxLayout()
        self.filter_group.setLayout(self.filter_vlayout)

        self.exp_filter = QRadioButton('Exponential')
        self.exp_filter.type = 'exponential'
        self.exp_filter.toggled.connect(self.on_clicked)
        self.filter_vlayout.addWidget(self.exp_filter)

        self.moving_avg = QRadioButton('Sliding average')
        self.moving_avg.type = 'sliding_average'
        self.moving_avg.toggled.connect(self.on_clicked)
        self.filter_vlayout.addWidget(self.moving_avg)

        self.filter_vlayout.addWidget(self.moving_avg)

        grid.addWidget(self.filter_group, 1, 2)

        self.on_update(self.noisy_ecg_sequence)

    # update points of the graph every time any slider/radiobutton emitted a Qt signal
    def on_update(self, ecg_sequence):
        """ Update the plot with the current input values """
        self.points.setData(ecg_sequence.time_seq / 1000, ecg_sequence.amp_seq)

    # perform sliding average filtering based on scrapped parameters from window width slider
    def update_winwidth(self):
        winwidth = self.slider_winwidth.value()
        self.slider_winwidth_value.setText(f'[{winwidth}]')
        filtered_amp_seq = fa.sliding_average(self.noisy_ecg_sequence, winwidth)
        filtered_ecg_sequence = cs.CycleSequence(time_seq=self.noisy_ecg_sequence.time_seq,
                                                 amp_seq=filtered_amp_seq)
        self.on_update(filtered_ecg_sequence)

    # perform exponential filtering based on scrapped parameters from alpha value slider
    def update_alpha(self):
        alpha = self.slider_alpha.value() / 100
        self.slider_alpha_value.setText(f'[{alpha}]')
        filtered_amp_seq = fa.exp_filter(self.noisy_ecg_sequence, alpha)
        filtered_ecg_sequence = cs.CycleSequence(time_seq=self.noisy_ecg_sequence.time_seq,
                                                 amp_seq=filtered_amp_seq)
        self.on_update(filtered_ecg_sequence)

    # set the only active radiobutton with self.active_radio attribute for the window
    def on_clicked(self):
        radio = self.sender()
        if radio.isChecked():
            self.active_radio = radio
            self.set_slider_modes()

    # activate neccessary filtering method and set the other one as disabled
    def set_slider_modes(self):
        if self.active_radio.type == 'exponential':
            self.slider_alpha.setEnabled(True)
            self.slider_winwidth.setEnabled(False)
            self.update_alpha()
        elif self.active_radio.type == 'sliding_average':
            self.slider_winwidth.setEnabled(True)
            self.slider_alpha.setEnabled(False)
            self.update_winwidth()
