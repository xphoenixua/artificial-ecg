from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt

import CycleSequence as cs

class SequenceWindow(QWidget):
    def __init__(self, ecg_cycle, parent=None):
        super().__init__(parent)
        self.setGeometry(300, 300, 700, 400)
        self.setWindowTitle('Послідовність кардіоциклів')
        self.ecg_cycle = ecg_cycle
        self.ecg_sequence = cs.CycleSequence(ecg_cycle, 30)

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

        grid.addWidget(self.graphWidget, 0, 0, 1, 3)

        # n spinbox
        
        self.n_group = QGroupBox()
        self.n_layout = QHBoxLayout()
        self.n_group.setLayout(self.n_layout)
        self.n_group.setTitle('Кількість циклів')

        self.n_input = QSpinBox()
        self.n_input.setMinimum(1)
        self.n_input.setValue(self.ecg_sequence.n)
        self.n_input.valueChanged.connect(self.update_n)
        self.n_input.setKeyboardTracking(False)
        self.n_layout.addWidget(self.n_input)
        
        grid.addWidget(self.n_group, 1, 0)

        # alternation slider

        self.slider_alt = QSlider(Qt.Orientation.Horizontal)
        
        self.slider_alt_group = QGroupBox()
        self.slider_alt_group.setTitle('Рівень альтерації (мВ)')

        self.slider_alt_vlayout = QVBoxLayout()
        self.slider_alt_group.setLayout(self.slider_alt_vlayout)
        self.slider_alt_hlayout = QHBoxLayout()
        self.slider_alt_vlayout.addLayout(self.slider_alt_hlayout)

        self.slider_alt_label1 = QLabel()
        self.slider_alt_hlayout.addWidget(self.slider_alt_label1)
        
        self.slider_alt.setSingleStep(1)
        # self.slider_alt.setValue(np.ceil(self.get_wave_data(1)).astype(int))
        # self.slider_alt.valueChanged.connect(self.update_mu)
        self.slider_alt_hlayout.addWidget(self.slider_alt)
        
        self.slider_alt_label2 = QLabel()
        self.slider_alt_hlayout.addWidget(self.slider_alt_label2)

        self.slider_alt_value = QLabel()
        # self.slider_alt_value.setText(f'[{np.ceil(self.get_wave_data(1)).astype(int)}]')
        self.slider_alt_vlayout.addWidget(self.slider_alt_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.slider_alt_group, 1, 1)

        # amplitude slider

        self.slider_noise = QSlider(Qt.Orientation.Horizontal)
        
        self.slider_noise_group = QGroupBox()
        self.slider_noise_group.setTitle('Рівень шуму')

        self.slider_noise_vlayout = QVBoxLayout()
        self.slider_noise_group.setLayout(self.slider_noise_vlayout)
        self.slider_noise_hlayout = QHBoxLayout()
        self.slider_noise_vlayout.addLayout(self.slider_noise_hlayout)

        self.slider_noise_label1 = QLabel()
        self.slider_noise_hlayout.addWidget(self.slider_noise_label1)
        
        self.slider_noise.setSingleStep(1)
        # self.slider_noise.setValue(np.ceil(self.get_wave_data(1)).astype(int))
        # self.slider_noise.valueChanged.connect(self.update_mu)
        self.slider_noise_hlayout.addWidget(self.slider_noise)
        
        self.slider_noise_label2 = QLabel()
        self.slider_noise_hlayout.addWidget(self.slider_noise_label2)

        self.slider_noise_value = QLabel()
        # self.slider_noise_value.setText(f'[{np.ceil(self.get_wave_data(1)).astype(int)}]')
        self.slider_noise_vlayout.addWidget(self.slider_noise_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.slider_noise_group, 1, 2)

        self.on_update()

    def on_update(self):
        """ Update the plot with the current input values """

        self.ecg_sequence.construct_sequence()
        self.points.setData(self.ecg_sequence.time_seq / 1000, self.ecg_sequence.amp_seq)

    def update_n(self):
        n_new = int(self.n_input.value())
        self.ecg_sequence = cs.CycleSequence(self.ecg_cycle, n_new)
        self.on_update()
