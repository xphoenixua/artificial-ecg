from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np

import calculations.CycleModel as cm
import ui.SequenceWindow as sw
import calculations.CycleSequence as cs
import ui.PhaseWindow as pw

# main window of ECG cycle
class MainWindow(QMainWindow):
    def __init__(self, ecg_init, parent=None):
        super().__init__(parent)

        # window styling
        self.setStyleSheet('''
        QMainWindow {
            background-color: #FFFFFF;
        }
        QMenuBar {
            border-bottom: 3px solid #007AD9;
        }
        QMenuBar::item {
            background-color: #007AD9;
            color: #FFFFFF;
        }
        QMenuBar::item:selected {
            background-color: #005FA8;
        }
        QMenuBar::item:pressed {
            background-color: #007AD9;
        }
        QMenu::indicator {
            background-color: #007AD9;
            color: #FFFFFF;
        }
        ''')
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('Cardiocycle model')

        # initialize ECG cycle
        self.ecg_cycle = ecg_init

        # initialize menu bar
        menu = QMenuBar(self)
        menu.setFixedHeight(21)
        menu.setMouseTracking(True)
        self.setMenuBar(menu)
        menu_file = QMenu('&File', self)
        menu.addMenu(menu_file)

        menu_open = QMenu("&Open...", self)
        menu_file.addMenu(menu_open)

        open_cycle_action = QAction("&Cycle", self)
        menu_open.addAction(open_cycle_action)
        open_cycle_action.cycle_flag = True
        open_cycle_action.triggered.connect(self.open_phase_window)

        open_sequence_action = QAction("&Sequence", self)
        menu_open.addAction(open_sequence_action)
        open_sequence_action.cycle_flag = False
        open_sequence_action.triggered.connect(self.open_phase_window)

        exit_action = QAction("&Exit", self)
        menu_file.addAction(exit_action)
        exit_action.triggered.connect(self.exit_window)

        # initialize grid for the window
        grid = QGridLayout()
        self.widget.setLayout(grid)
        
        # initialize graph
        pg.setConfigOptions(antialias=True) # True for fancy, False for fast graphs
        self.widget.graphWidget = pg.PlotWidget()
        self.widget.graphWidget.setTitle('Heart contraction cycle', color='black')
        self.widget.graphWidget.setLabel(axis='bottom', text='Time (ms)', color='black')
        self.widget.graphWidget.setLabel(axis='left', text='Amplitude (mV)', color='black')
        self.widget.graphWidget.setMenuEnabled()
        self.widget.graphWidget.setBackground('w')
        self.widget.graphWidget.showButtons()
        self.widget.graphWidget.showGrid(x=True, y=True, alpha=1)
        pen = pg.mkPen(color="k", width=2.5, style=Qt.PenStyle.SolidLine)
        self.points = self.widget.graphWidget.plot(pen=pen)

        grid.addWidget(self.widget.graphWidget, 0, 0, 3, 1)

        # intiialize button for generating a sequence from the created cycle
        self.widget.button = QPushButton('Generate')
        self.widget.button.setStyleSheet('''
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
        self.widget.button.clicked.connect(self.show_sequence_window)
        grid.addWidget(self.widget.button, 0, 1, Qt.AlignmentFlag.AlignTop)

        # initializing radio buttons for switching which ECG wave to configure

        self.widget.radio_group = QGroupBox()
        self.widget.radio_layout = QVBoxLayout()
        self.widget.radio_group.setLayout(self.widget.radio_layout)
        self.widget.radio_group.setTitle('Wave')
        self.widget.radio_group.setFixedHeight(250)

        self.widget.radiobutton = QRadioButton('P')
        self.widget.radiobutton.wave = 'P'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)

        self.widget.radiobutton = QRadioButton('Q')
        self.widget.radiobutton.wave = 'Q'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)

        self.widget.radiobutton = QRadioButton('R')
        self.widget.radiobutton.wave = 'R'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)
        
        self.widget.radiobutton = QRadioButton('S')
        self.widget.radiobutton.wave = 'S'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)
        
        self.widget.radiobutton = QRadioButton('ST')
        self.widget.radiobutton.wave = 'ST'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)
        
        self.widget.radiobutton = QRadioButton('T')
        self.widget.radiobutton.wave = 'T'
        self.widget.radiobutton.toggled.connect(self.on_clicked)
        self.widget.radiobutton.setChecked(True)
        self.widget.radio_layout.addWidget(self.widget.radiobutton)

        grid.addWidget(self.widget.radio_group, 1, 1, Qt.AlignmentFlag.AlignVCenter)

        # initialize heart rate spinbox
        
        self.widget.fh_group = QGroupBox()
        self.widget.fh_layout = QHBoxLayout()
        self.widget.fh_group.setLayout(self.widget.fh_layout)
        self.widget.fh_group.setFixedWidth(70)
        self.widget.fh_group.setFixedHeight(60)
        self.widget.fh_group.setTitle('Fh [beats/minute]')

        self.widget.fh_input = QSpinBox()
        self.widget.fh_input.setMinimum(30)
        self.widget.fh_input.setMaximum(150)
        self.widget.fh_input.setValue(self.ecg_cycle.Fh)
        self.widget.fh_input.valueChanged.connect(self.update_fh)
        self.widget.fh_input.setKeyboardTracking(False)
        self.widget.fh_layout.addWidget(self.widget.fh_input)
        
        grid.addWidget(self.widget.fh_group, 2, 1, Qt.AlignmentFlag.AlignHCenter)
        
        # initialize grid for amplitude and mu value
        self.widget.slider_a_mu_hlayout = QHBoxLayout()

        # intiialize amplitude slider

        self.widget.slider_a = QSlider(Qt.Orientation.Horizontal)
        
        self.widget.slider_a_group = QGroupBox()
        self.widget.slider_a_group.setTitle('Amplitude (mV)')
        
        self.widget.slider_a_vlayout = QVBoxLayout()
        self.widget.slider_a_group.setLayout(self.widget.slider_a_vlayout)
        self.widget.slider_a_hlayout = QHBoxLayout()
        self.widget.slider_a_vlayout.addLayout(self.widget.slider_a_hlayout)

        self.widget.slider_a_label1 = QLabel()
        self.widget.slider_a_label1.setText('-1')
        self.widget.slider_a_hlayout.addWidget(self.widget.slider_a_label1)
        
        self.widget.slider_a.setMinimum(-100)
        self.widget.slider_a.setMaximum(100)
        self.widget.slider_a.setSingleStep(1)
        self.widget.slider_a.setValue(np.ceil(self.get_wave_data(0) * 100).astype(int))
        self.widget.slider_a.valueChanged.connect(self.update_a)
        self.widget.slider_a_hlayout.addWidget(self.widget.slider_a)
        
        self.widget.slider_a_label2 = QLabel()
        self.widget.slider_a_label2.setText('1')
        self.widget.slider_a_hlayout.addWidget(self.widget.slider_a_label2)

        self.widget.slider_a_value = QLabel()
        self.widget.slider_a_value.setText(f'[{np.ceil(self.get_wave_data(0) * 100).astype(int)}]')
        self.widget.slider_a_vlayout.addWidget(self.widget.slider_a_value, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.widget.slider_a_mu_hlayout.addWidget(self.widget.slider_a_group)

        # initialize mu (mean) slider

        self.widget.slider_mu = QSlider(Qt.Orientation.Horizontal)
        
        self.widget.slider_mu_group = QGroupBox()
        self.widget.slider_mu_group.setTitle('Mean (ms)')

        self.widget.slider_mu_vlayout = QVBoxLayout()
        self.widget.slider_mu_group.setLayout(self.widget.slider_mu_vlayout)
        self.widget.slider_mu_hlayout = QHBoxLayout()
        self.widget.slider_mu_vlayout.addLayout(self.widget.slider_mu_hlayout)

        self.widget.slider_mu_label1 = QLabel()
        self.widget.slider_mu_hlayout.addWidget(self.widget.slider_mu_label1)
        
        self.widget.slider_mu.setSingleStep(1)
        self.widget.slider_mu.setValue(np.ceil(self.get_wave_data(1)).astype(int))
        self.widget.slider_mu.valueChanged.connect(self.update_mu)
        self.widget.slider_mu_hlayout.addWidget(self.widget.slider_mu)
        
        self.widget.slider_mu_label2 = QLabel()
        self.widget.slider_mu_hlayout.addWidget(self.widget.slider_mu_label2)

        self.widget.slider_mu_value = QLabel()
        self.widget.slider_mu_value.setText(f'[{np.ceil(self.get_wave_data(1)).astype(int)}]')
        self.widget.slider_mu_vlayout.addWidget(self.widget.slider_mu_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.widget.slider_a_mu_hlayout.addWidget(self.widget.slider_mu_group)

        # add amplitude and mu grid to layout

        grid.addLayout(self.widget.slider_a_mu_hlayout, 3, 0, 1, 2)

        # initialize group of sliders for configuring standard deviation to the left and right of the mean value

        self.widget.slider_b_group = QGroupBox()
        self.widget.slider_b_hlayout = QHBoxLayout()
        self.widget.slider_b_group.setLayout(self.widget.slider_b_hlayout)
        self.widget.slider_b_group.setTitle('Standard deviation (ms)')

        # initialize left (b1) std side slider
        
        self.widget.slider_b1_group = QGroupBox()
        self.widget.slider_b1_group.setTitle('b1')

        self.widget.slider_b1_vlayout = QVBoxLayout()
        self.widget.slider_b1_group.setLayout(self.widget.slider_b1_vlayout)
        self.widget.slider_b1_hlayout = QHBoxLayout()
        self.widget.slider_b1_vlayout.addLayout(self.widget.slider_b1_hlayout)

        self.widget.slider_b1_label1 = QLabel()
        self.widget.slider_b1_hlayout.addWidget(self.widget.slider_b1_label1)
        
        self.widget.slider_b1 = QSlider(Qt.Orientation.Horizontal)
        self.widget.slider_b1.setSingleStep(1)
        self.widget.slider_b1.valueChanged.connect(self.update_b1)
        self.widget.slider_b1_hlayout.addWidget(self.widget.slider_b1)
        
        self.widget.slider_b1_label2 = QLabel()
        self.widget.slider_b1_hlayout.addWidget(self.widget.slider_b1_label2)

        self.widget.slider_b1_value = QLabel()
        self.widget.slider_b1_vlayout.addWidget(self.widget.slider_b1_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.widget.slider_b_hlayout.addWidget(self.widget.slider_b1_group)

        # initialize right (b2) std side slider
        
        self.widget.slider_b2_group = QGroupBox()
        self.widget.slider_b2_group.setTitle('b2')

        self.widget.slider_b2_vlayout = QVBoxLayout()
        self.widget.slider_b2_group.setLayout(self.widget.slider_b2_vlayout)
        self.widget.slider_b2_hlayout = QHBoxLayout()
        self.widget.slider_b2_vlayout.addLayout(self.widget.slider_b2_hlayout)

        self.widget.slider_b2_label1 = QLabel()
        self.widget.slider_b2_hlayout.addWidget(self.widget.slider_b2_label1)
        
        self.widget.slider_b2 = QSlider(Qt.Orientation.Horizontal)
        self.widget.slider_b2.setSingleStep(1)
        self.widget.slider_b2.valueChanged.connect(self.update_b2)
        self.widget.slider_b2_hlayout.addWidget(self.widget.slider_b2)
        
        self.widget.slider_b2_label2 = QLabel()
        self.widget.slider_b2_hlayout.addWidget(self.widget.slider_b2_label2)

        self.widget.slider_b2_value = QLabel()
        self.widget.slider_b2_vlayout.addWidget(self.widget.slider_b2_value, alignment=Qt.AlignmentFlag.AlignCenter)

        self.widget.slider_b_hlayout.addWidget(self.widget.slider_b2_group)
        
        grid.addWidget(self.widget.slider_b_group, 4, 0, 1, 2)
        
        # update sliders based on intitial conditions of the cycle (from Run.py)
        self.update_sliders()
        # update graph based on all parameters from sliders
        self.on_update()

    # getter for cycle wave
    def get_wave_data(self, index):
        return self.ecg_cycle.waves[self.active_radio.wave][index]

    # setter for cycle wave
    def set_wave_data(self, data, index):
        self.ecg_cycle.waves[self.active_radio.wave][index] = data

    # update points of the graph every time any slider/radiobutton emitted a Qt signal
    def on_update(self):
        """ Update the plot with the current input values """
        self.ecg_cycle.construct_cycle()
        self.points.setData(self.ecg_cycle.time, self.ecg_cycle.amplitude)

        # we want to mirror any changes to the cycle to the generated sequence
        if hasattr(self, 'window_sequence'):
            self.window_sequence.to_sequence(self.ecg_cycle)

    # rebuild cycle based on scrapped parameters from heart rate spinbox
    def update_fh(self):
        Fh_new = self.widget.fh_input.value()
        self.ecg_cycle.fh_normalization(Fh_new)
        waves_new = self.ecg_cycle.waves
        self.ecg_cycle = cm.CycleModel(Fh_new, waves_new)
        self.update_sliders()
        self.on_update()

    # rebuild cycle based on scrapped parameters from amplitude slider
    def update_a(self):
        self.set_wave_data(self.widget.slider_a.value() / 100, 0)
        self.widget.slider_a_value.setText(f'[{self.widget.slider_a.value() / 100}]')
        self.on_update()
    
    # rebuild cycle based on scrapped parameters from mean slider
    def update_mu(self):
        self.set_wave_data(self.widget.slider_mu.value(), 1)
        # because we changed mean, we also need to recalculate possible std range for the wave
        self.set_b_range()
        self.widget.slider_mu_value.setText(f'[{self.widget.slider_mu.value()}]')
        self.on_update()
    
    # rebuild cycle based on scrapped parameters from left side std slider
    def update_b1(self):
        self.set_wave_data(self.widget.slider_b1.value(), 2)
        # because we changed std, we also need to recalculate possible mean range for the wave
        self.set_mu_range()
        self.widget.slider_b1_value.setText(f'[{self.widget.slider_b1.value()}]')
        self.on_update()
    
    # rebuild cycle based on scrapped parameters from right side std slider
    def update_b2(self):
        self.set_wave_data(self.widget.slider_b2.value(), 3)
        # because we changed std, we also need to recalculate possible mean range for the wave
        self.set_mu_range()
        self.widget.slider_b2_value.setText(f'[{self.widget.slider_b2.value()}]')
        self.on_update()

    # reflect changes to sliders to labels and internal signal data
    def update_sliders(self):
        if hasattr(self.widget, 'slider_a'):
            # block signals to stop calls to updating functions
            self.block_signals(True)
            self.widget.slider_a.setValue(np.ceil(self.get_wave_data(0) * 100).astype(int))
            self.widget.slider_a_value.setText(f'[{self.widget.slider_a.value() / 100}]')
            self.set_mu_range()
            self.widget.slider_mu.setValue(np.ceil(self.get_wave_data(1)).astype(int))
            self.widget.slider_mu_value.setText(f'[{self.widget.slider_mu.value()}]')
            self.set_b_range()
            self.widget.slider_b1.setValue(np.ceil(self.get_wave_data(2)).astype(int))
            self.widget.slider_b1_value.setText(f'[{self.widget.slider_b1.value()}]')
            self.widget.slider_b2.setValue(np.ceil(self.get_wave_data(3)).astype(int))
            self.widget.slider_b2_value.setText(f'[{self.widget.slider_b2.value()}]')
            # let Qt listen to signals from UI elements again
            self.block_signals(False)
        else:
            return

    # update possible range for mean value slider
    def set_mu_range(self):
        if hasattr(self.widget, 'slider_mu'):
            m_b, m_e = self.ecg_cycle.find_range_mu(self.active_radio.wave)
            self.widget.slider_mu.setMinimum(m_b)
            self.widget.slider_mu.setMaximum(m_e)
            self.widget.slider_mu_label1.setText(f'{m_b}')
            self.widget.slider_mu_label2.setText(f'{m_e}')
        else:
            return

    # update possible range for std value sliders
    def set_b_range(self):
        if hasattr(self.widget, 'slider_b1'):
            b1_b, b1_e = self.ecg_cycle.find_range_b1(self.active_radio.wave)
            b2_b, b2_e = self.ecg_cycle.find_range_b2(self.active_radio.wave)
            
            self.widget.slider_b1.setMinimum(b1_b)
            self.widget.slider_b1.setMaximum(b1_e)
            self.widget.slider_b1_label1.setText(f'{b1_b}')
            self.widget.slider_b1_label2.setText(f'{b1_e}')
            
            self.widget.slider_b2.setMinimum(b2_b)
            self.widget.slider_b2.setMaximum(b2_e)
            self.widget.slider_b2_label1.setText(f'{b2_b}')
            self.widget.slider_b2_label2.setText(f'{b2_e}')
        else:
            return

    # set the only active radiobutton with self.active_radio attribute for the window
    def on_clicked(self):
        radio = self.sender()
        if radio.isChecked():
            self.active_radio = radio
            # make sure everything is updated to prevent any data leaps
            self.update_sliders()

    # helper function for stopping Qt from listening to emitted signals
    def block_signals(self, block):
        if block:
            self.widget.slider_mu.blockSignals(True)
            self.widget.slider_b1.blockSignals(True)
            self.widget.slider_b2.blockSignals(True)
        elif not block:
            self.widget.slider_mu.blockSignals(False)
            self.widget.slider_b1.blockSignals(False)
            self.widget.slider_b2.blockSignals(False)

    # exit program
    def exit_window(self):
        QApplication.closeAllWindows()
    
    # when opened a .txt signal file in menu
    def open_phase_window(self):
        data = self.open_file()
        if data is not None:
            self.show_phase_window(data, self.sender().cycle_flag)

    # open a .txt signal file
    def open_file(self):
        file, check = QFileDialog.getOpenFileName(self, "Прочитати сигнал ЕКГ", "", "Текстовий файл (*.txt)")
        if check:
            f = open(file, 'r')
            with f:
                data = f.read()
            data = data.replace('\n', '').split(' ')
            data = [s.replace(' ', '') for s in data]
            data = [s for s in data if s!='']
            data = np.asarray(data).astype(float) / 10000
            return data

    # create sequence window when pressed Generate button
    def show_sequence_window(self):
        self.window_sequence = sw.SequenceWindow(self.ecg_cycle)
        self.window_sequence.show()

    # create phase window when opened a .txt signal file in menu
    def show_phase_window(self, data, cycle_flag):
        self.window_phase = pw.PhaseWindow(data, cycle_flag)
        self.window_phase.show()
