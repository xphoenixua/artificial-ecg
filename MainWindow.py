from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import CycleModel as cm
import SequenceWindow as sw

class MainWindow(QMainWindow):
    def __init__(self, ecg_init, parent=None):
        super().__init__(parent)
        self.wid = QWidget(self)
        self.setCentralWidget(self.wid)
        self.setWindowTitle('Модель кардіоцикла')
        self.ecg_cycle = ecg_init

        # plot widgets

        grid = QGridLayout()

        self.wid.setLayout(grid)
                
        self.wid.graphWidget = pg.PlotWidget()
        self.wid.graphWidget.setTitle('Цикл серцевого скорочення', color='black', size='18pt')
        self.wid.graphWidget.setLabel(axis='bottom', text='Час (мс)', color='black')
        self.wid.graphWidget.setLabel(axis='left', text='Амплітуда (мВ)', color='black')
        self.wid.graphWidget.setMenuEnabled()
        self.wid.graphWidget.setBackground('w')
        self.wid.graphWidget.showButtons()
        self.wid.graphWidget.showGrid(x=True, y=True, alpha=1)
        pen = pg.mkPen(color="k", width=2.5, style=Qt.PenStyle.SolidLine)
        self.points = self.wid.graphWidget.plot(pen=pen)

        grid.addWidget(self.wid.graphWidget, 0, 0, 3, 1)

        # generation button

        self.wid.button = QPushButton('Генерація')
        self.wid.button.clicked.connect(self.show_new_window)
        grid.addWidget(self.wid.button, 0, 1, Qt.AlignmentFlag.AlignTop)

        # waves radio buttons

        self.wid.radio_group = QGroupBox()
        self.wid.radio_layout = QVBoxLayout()
        self.wid.radio_group.setLayout(self.wid.radio_layout)
        self.wid.radio_group.setTitle('Зубець')
        self.wid.radio_group.setFixedHeight(250)

        self.wid.radiobutton = QRadioButton('P')
        self.wid.radiobutton.wave = 'P'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)

        self.wid.radiobutton = QRadioButton('Q')
        self.wid.radiobutton.wave = 'Q'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)

        self.wid.radiobutton = QRadioButton('R')
        self.wid.radiobutton.wave = 'R'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)
        
        self.wid.radiobutton = QRadioButton('S')
        self.wid.radiobutton.wave = 'S'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)
        
        self.wid.radiobutton = QRadioButton('ST')
        self.wid.radiobutton.wave = 'ST'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)
        
        self.wid.radiobutton = QRadioButton('T')
        self.wid.radiobutton.wave = 'T'
        self.wid.radiobutton.toggled.connect(self.on_clicked)
        self.wid.radiobutton.setChecked(True)
        self.wid.radio_layout.addWidget(self.wid.radiobutton)

        grid.addWidget(self.wid.radio_group, 1, 1, Qt.AlignmentFlag.AlignVCenter)

        # Fh spinbox
        
        self.wid.fh_group = QGroupBox()
        self.wid.fh_layout = QHBoxLayout()
        self.wid.fh_group.setLayout(self.wid.fh_layout)
        self.wid.fh_group.setFixedWidth(70)
        self.wid.fh_group.setFixedHeight(60)
        self.wid.fh_group.setTitle('FH [уд./хв]')

        self.wid.fh_input = QSpinBox()
        self.wid.fh_input.setMinimum(30)
        self.wid.fh_input.setMaximum(150)
        self.wid.fh_input.setValue(self.ecg_cycle.Fh)
        self.wid.fh_input.valueChanged.connect(self.update_fh)
        self.wid.fh_input.setKeyboardTracking(False)
        self.wid.fh_layout.addWidget(self.wid.fh_input)
        
        grid.addWidget(self.wid.fh_group, 2, 1, Qt.AlignmentFlag.AlignHCenter)
        
        # a and mu grid

        self.wid.slider_a_mu_hlayout = QHBoxLayout()

        # amplitude slider

        self.wid.slider_a = QSlider(Qt.Orientation.Horizontal)
        
        self.wid.slider_a_group = QGroupBox()
        self.wid.slider_a_group.setTitle('Амплітуда (мВ)')
        
        self.wid.slider_a_vlayout = QVBoxLayout()
        self.wid.slider_a_group.setLayout(self.wid.slider_a_vlayout)
        self.wid.slider_a_hlayout = QHBoxLayout()
        self.wid.slider_a_vlayout.addLayout(self.wid.slider_a_hlayout)

        self.wid.slider_a_label1 = QLabel()
        self.wid.slider_a_label1.setText('-1')
        self.wid.slider_a_hlayout.addWidget(self.wid.slider_a_label1)
        
        self.wid.slider_a.setMinimum(-100)
        self.wid.slider_a.setMaximum(100)
        self.wid.slider_a.setSingleStep(1)
        self.wid.slider_a.setValue(np.ceil(self.get_wave_data(0) * 100).astype(int))
        self.wid.slider_a.valueChanged.connect(self.update_a)
        self.wid.slider_a_hlayout.addWidget(self.wid.slider_a)
        
        self.wid.slider_a_label2 = QLabel()
        self.wid.slider_a_label2.setText('1')
        self.wid.slider_a_hlayout.addWidget(self.wid.slider_a_label2)

        self.wid.slider_a_value = QLabel()
        self.wid.slider_a_value.setText(f'[{np.ceil(self.get_wave_data(0) * 100).astype(int)}]')
        self.wid.slider_a_vlayout.addWidget(self.wid.slider_a_value, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.wid.slider_a_mu_hlayout.addWidget(self.wid.slider_a_group)

        # mean slider

        self.wid.slider_mu = QSlider(Qt.Orientation.Horizontal)
        
        self.wid.slider_mu_group = QGroupBox()
        self.wid.slider_mu_group.setTitle('Середнє (мс)')

        self.wid.slider_mu_vlayout = QVBoxLayout()
        self.wid.slider_mu_group.setLayout(self.wid.slider_mu_vlayout)
        self.wid.slider_mu_hlayout = QHBoxLayout()
        self.wid.slider_mu_vlayout.addLayout(self.wid.slider_mu_hlayout)

        self.wid.slider_mu_label1 = QLabel()
        self.wid.slider_mu_hlayout.addWidget(self.wid.slider_mu_label1)
        
        self.wid.slider_mu.setSingleStep(1)
        self.wid.slider_mu.setValue(np.ceil(self.get_wave_data(1)).astype(int))
        self.wid.slider_mu.valueChanged.connect(self.update_mu)
        self.wid.slider_mu_hlayout.addWidget(self.wid.slider_mu)
        
        self.wid.slider_mu_label2 = QLabel()
        self.wid.slider_mu_hlayout.addWidget(self.wid.slider_mu_label2)

        self.wid.slider_mu_value = QLabel()
        self.wid.slider_mu_value.setText(f'[{np.ceil(self.get_wave_data(1)).astype(int)}]')
        self.wid.slider_mu_vlayout.addWidget(self.wid.slider_mu_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.wid.slider_a_mu_hlayout.addWidget(self.wid.slider_mu_group)

        # a and mu grid

        grid.addLayout(self.wid.slider_a_mu_hlayout, 3, 0, 1, 2)

        # b group

        self.wid.slider_b_group = QGroupBox()
        self.wid.slider_b_hlayout = QHBoxLayout()
        self.wid.slider_b_group.setLayout(self.wid.slider_b_hlayout)
        self.wid.slider_b_group.setTitle('Середньоквадратичне (мс)')

        # b1 slider
        
        self.wid.slider_b1_group = QGroupBox()
        self.wid.slider_b1_group.setTitle('b1')

        self.wid.slider_b1_vlayout = QVBoxLayout()
        self.wid.slider_b1_group.setLayout(self.wid.slider_b1_vlayout)
        self.wid.slider_b1_hlayout = QHBoxLayout()
        self.wid.slider_b1_vlayout.addLayout(self.wid.slider_b1_hlayout)

        self.wid.slider_b1_label1 = QLabel()
        self.wid.slider_b1_hlayout.addWidget(self.wid.slider_b1_label1)
        
        self.wid.slider_b1 = QSlider(Qt.Orientation.Horizontal)
        self.wid.slider_b1.setSingleStep(1)
        self.wid.slider_b1.valueChanged.connect(self.update_b1)
        self.wid.slider_b1_hlayout.addWidget(self.wid.slider_b1)
        
        self.wid.slider_b1_label2 = QLabel()
        self.wid.slider_b1_hlayout.addWidget(self.wid.slider_b1_label2)

        self.wid.slider_b1_value = QLabel()
        self.wid.slider_b1_vlayout.addWidget(self.wid.slider_b1_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.wid.slider_b_hlayout.addWidget(self.wid.slider_b1_group)

        # b2 slider
        
        self.wid.slider_b2_group = QGroupBox()
        self.wid.slider_b2_group.setTitle('b2')

        self.wid.slider_b2_vlayout = QVBoxLayout()
        self.wid.slider_b2_group.setLayout(self.wid.slider_b2_vlayout)
        self.wid.slider_b2_hlayout = QHBoxLayout()
        self.wid.slider_b2_vlayout.addLayout(self.wid.slider_b2_hlayout)

        self.wid.slider_b2_label1 = QLabel()
        self.wid.slider_b2_hlayout.addWidget(self.wid.slider_b2_label1)
        
        self.wid.slider_b2 = QSlider(Qt.Orientation.Horizontal)
        self.wid.slider_b2.setSingleStep(1)
        self.wid.slider_b2.valueChanged.connect(self.update_b2)
        self.wid.slider_b2_hlayout.addWidget(self.wid.slider_b2)
        
        self.wid.slider_b2_label2 = QLabel()
        self.wid.slider_b2_hlayout.addWidget(self.wid.slider_b2_label2)

        self.wid.slider_b2_value = QLabel()
        self.wid.slider_b2_vlayout.addWidget(self.wid.slider_b2_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.wid.slider_b_hlayout.addWidget(self.wid.slider_b2_group)
        
        grid.addWidget(self.wid.slider_b_group, 4, 0, 1, 2)
        
        self.update_sliders()
        self.on_update()

    def get_wave_data(self, index):
        return self.ecg_cycle.waves[self.active_radio.wave][index]

    def set_wave_data(self, data, index):
        self.ecg_cycle.waves[self.active_radio.wave][index] = data

    def on_update(self):
        """ Update the plot with the current input values """

        self.ecg_cycle.construct_cycle()
        self.points.setData(self.ecg_cycle.time, self.ecg_cycle.amplitude)

        if hasattr(self, 'w_new'):
            self.w_new.ecg_cycle = self.ecg_cycle
            self.w_new.on_update()

    def update_fh(self):
        Fh_new = self.wid.fh_input.value()
        self.ecg_cycle.fh_normalization(Fh_new)
        waves_new = self.ecg_cycle.waves
        self.ecg_cycle = cm.CycleModel(Fh_new, waves_new)
        self.update_sliders()
        self.on_update()

    def update_a(self):
        self.set_wave_data(self.wid.slider_a.value() / 100, 0)
        self.wid.slider_a_value.setText(f'[{self.wid.slider_a.value() / 100}]')
        self.on_update()
    
    def update_mu(self):
        self.set_wave_data(self.wid.slider_mu.value(), 1)
        self.set_b_range()
        self.wid.slider_mu_value.setText(f'[{self.wid.slider_mu.value()}]')
        self.on_update()
    
    def update_b1(self):
        self.set_wave_data(self.wid.slider_b1.value(), 2)
        self.set_mu_range()
        self.wid.slider_b1_value.setText(f'[{self.wid.slider_b1.value()}]')
        self.on_update()
    
    def update_b2(self):
        self.set_wave_data(self.wid.slider_b2.value(), 3)
        self.set_mu_range()
        self.wid.slider_b2_value.setText(f'[{self.wid.slider_b2.value()}]')
        self.on_update()

    def update_sliders(self):
        if hasattr(self.wid, 'slider_a'):
            self.block_signals(True)
            self.wid.slider_a.setValue(np.ceil(self.get_wave_data(0) * 100).astype(int))
            self.wid.slider_a_value.setText(f'[{self.wid.slider_a.value() / 100}]')
            self.set_mu_range()
            self.wid.slider_mu.setValue(np.ceil(self.get_wave_data(1)).astype(int))
            self.wid.slider_mu_value.setText(f'[{self.wid.slider_mu.value()}]')
            self.set_b_range()
            self.wid.slider_b1.setValue(np.ceil(self.get_wave_data(2)).astype(int))
            self.wid.slider_b1_value.setText(f'[{self.wid.slider_b1.value()}]')
            self.wid.slider_b2.setValue(np.ceil(self.get_wave_data(3)).astype(int))
            self.wid.slider_b2_value.setText(f'[{self.wid.slider_b2.value()}]')
            self.block_signals(False)
        else:
            return

    def set_mu_range(self):
        if hasattr(self.wid, 'slider_mu'):
            m_b, m_e = self.ecg_cycle.find_range_mu(self.active_radio.wave)
            self.wid.slider_mu.setMinimum(m_b)
            self.wid.slider_mu.setMaximum(m_e)
            self.wid.slider_mu_label1.setText(f'{m_b}')
            self.wid.slider_mu_label2.setText(f'{m_e}')
        else:
            return

    def set_b_range(self):
        if hasattr(self.wid, 'slider_b1'):
            b1_b, b1_e = self.ecg_cycle.find_range_b1(self.active_radio.wave)
            b2_b, b2_e = self.ecg_cycle.find_range_b2(self.active_radio.wave)
            
            self.wid.slider_b1.setMinimum(b1_b)
            self.wid.slider_b1.setMaximum(b1_e)
            self.wid.slider_b1_label1.setText(f'{b1_b}')
            self.wid.slider_b1_label2.setText(f'{b1_e}')
            
            self.wid.slider_b2.setMinimum(b2_b)
            self.wid.slider_b2.setMaximum(b2_e)
            self.wid.slider_b2_label1.setText(f'{b2_b}')
            self.wid.slider_b2_label2.setText(f'{b2_e}')
        else:
            return

    def on_clicked(self):
        radio = self.sender()
        if radio.isChecked():
            self.active_radio = radio
            self.update_sliders()

    def block_signals(self, block):
        if block:
            self.wid.slider_mu.blockSignals(True)
            self.wid.slider_b1.blockSignals(True)
            self.wid.slider_b2.blockSignals(True)
        elif not block:
            self.wid.slider_mu.blockSignals(False)
            self.wid.slider_b1.blockSignals(False)
            self.wid.slider_b2.blockSignals(False)

    def show_new_window(self, checked):
        self.w_new = sw.SequenceWindow(self.ecg_cycle)
        self.w_new.show()