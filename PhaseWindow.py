from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np

import MainWindow as mw
import CycleSequence as cs
import DominantCycleWindows as dcw

class PhaseWindow(QMainWindow):
    def __init__(self, data, cycle_flag, parent=None):
        super().__init__(parent)
        self.setGeometry(500, 200, 700, 600)
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
        QMenuBar::separator {
            background-color: #FFFFFF;
            border: 2px solid;
        }
        ''')
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('Фазові портрети відкритої ЕКГ')
        self.z = [data]
        self.z_flattened = data
        self.cycle_flag = cycle_flag

        # menu bar

        menu = QMenuBar(self)
        menu.setFixedHeight(21)
        self.setMenuBar(menu)
        menu_file = QMenu('&Файл', self)
        menu.addMenu(menu_file)
        menu.addSeparator()
        menu_analyze = QMenu('&Аналізувати', self)
        menu.addMenu(menu_analyze)

        cycle_action = QAction("&Визначити опорний цикл", menu)
        menu_analyze.addAction(cycle_action)
        cycle_action.setEnabled(self.cycle_flag)
        cycle_action.triggered.connect(self.show_dominant_cycle_windows)

        # plot widgets

        grid = QGridLayout()
        self.widget.setLayout(grid)

        self.widget.graphLayout = pg.GraphicsLayoutWidget()
        self.widget.graphLayout.setBackground('w')
        self.widget.pen = pg.mkPen(color="k", width=2, style=Qt.PenStyle.SolidLine)
        
        self.widget.time_domain_plot = self.widget.graphLayout.addPlot(row=0, col=0, rowspan=3, colspan=1)
        self.widget.time_domain_points = self.widget.time_domain_plot.plot(pen=self.widget.pen)
        self.widget.time_domain_plot.setTitle('ЕКГ', color='black')
        self.widget.time_domain_plot.setLabel(axis='bottom', text='Час (с)', color='black')
        self.widget.time_domain_plot.setLabel(axis='left', text='Амплітуда (мВ)', color='black')
        self.widget.time_domain_plot.showGrid(x=True, y=True, alpha=1)

        # add cycle button
        
        add_cycle_button = QPushButton('+')
        add_cycle_button.setMaximumWidth(25)
        add_cycle_button.setMaximumHeight(25)
        add_cycle_button.setStyleSheet('''
        QPushButton {
            background-color: #007AD9;
            font-size: 20px;
            font-weight: bold;
            color: #FFFFFF;
            border: 2px solid;
            border-color: #007AD9;
            padding-bottom: 5px;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
            color: #007AD9;
        }
        QPushButton:disabled,
        QPushButton[disabled] {
            background-color: #E7E7E7;
            color: #555555;
            border-color: #555555;
        }
        ''')
        add_cycle_button.setToolTip('Додати цикл')
        add_cycle_button.clicked.connect(self.add_cycle)
        add_cycle_button.setEnabled(self.cycle_flag)

        proxy = QGraphicsProxyWidget()
        proxy.setWidget(add_cycle_button)
        self.widget.graphLayout.addItem(proxy, 1, 1)

        # ---

        self.widget.phase_plot = self.widget.graphLayout.addPlot(row=3, col=0, colspan=2)
        self.widget.phase_points = self.widget.phase_plot.plot(pen=self.widget.pen)
        self.widget.phase_plot.setTitle('Фазовий портрет ЕКГ', color='black')
        self.widget.phase_plot.setLabel(axis='bottom', text='z(t)', color='black')
        self.widget.phase_plot.setLabel(axis='left', text="z '(t)", color='black')
        self.widget.phase_plot.showGrid(x=True, y=True, alpha=1)

        self.widget.pseudophase_plot = self.widget.graphLayout.addPlot(row=4, col=0, colspan=2)
        self.widget.pseudophase_points = self.widget.pseudophase_plot.plot(pen=self.widget.pen)
        self.widget.pseudophase_plot.setTitle('Псевдофазовий портрет ЕКГ', color='black')
        self.widget.pseudophase_plot.setLabel(axis='bottom', text='z(t)', color='black')
        self.widget.pseudophase_plot.setLabel(axis='left', text="z(t-𝜏)", color='black')
        self.widget.pseudophase_plot.showGrid(x=True, y=True, alpha=1)

        grid.addWidget(self.widget.graphLayout, 0, 0)

        # tau slider

        self.widget.slider_tau = QSlider(Qt.Orientation.Horizontal)
        self.widget.slider_tau.setMinimumWidth(200)
        
        slider_tau_group = QGroupBox()
        slider_tau_group.setTitle('Параметр 𝜏')
        
        slider_tau_vlayout = QVBoxLayout()
        slider_tau_group.setLayout(slider_tau_vlayout)
        slider_tau_hlayout = QHBoxLayout()
        slider_tau_vlayout.addLayout(slider_tau_hlayout)

        slider_tau_label1 = QLabel()
        slider_tau_label1.setText('1')
        slider_tau_hlayout.addWidget(slider_tau_label1)
        
        self.tau = 8
        self.widget.slider_tau.setMinimum(1)
        self.widget.slider_tau.setMaximum(50)
        self.widget.slider_tau.setSingleStep(1)
        self.widget.slider_tau.setValue(self.tau)
        self.widget.slider_tau.valueChanged.connect(self.update_tau)
        slider_tau_hlayout.addWidget(self.widget.slider_tau)
        
        slider_tau_label2 = QLabel()
        slider_tau_label2.setText('50')
        slider_tau_hlayout.addWidget(slider_tau_label2)

        self.widget.slider_tau_value = QLabel()
        self.widget.slider_tau_value.setText(f'[{self.widget.slider_tau.value()}]')
        slider_tau_vlayout.addWidget(self.widget.slider_tau_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(slider_tau_group, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.on_update()

    def on_update(self):
        self.update_time_domain()
        self.update_phase_domain()
        self.update_pseudophase_domain()

    def update_time_domain(self):
        Fs = 500
        Ts = 1 / Fs
        N = self.z_flattened.shape[0]
        time_seq = np.arange(0, N) * Ts
        self.widget.time_domain_points.setData(time_seq,
                                               self.z_flattened)
    
    def update_phase_domain(self):
        # t = self.ecg_sequence.time_seq
        # N = z.shape[0]

        # dt = np.diff(t)
        # dz = np.diff(z)
        # dzdt = dz / dt
        # dzdt = np.concatenate((dzdt, np.array([0])))
        
        # dt = np.gradient(t)
        # dz = np.gradient(z)
        # dzdt = dz / dt
        
        self.dz = self.compute_derivative(self.z)
        self.dz_flattened = np.hstack(np.asarray(self.dz, dtype='object')).astype('float64')
        self.widget.phase_points.setData(self.z_flattened, self.dz_flattened)

        # Lagrange 1st order derivative, raw implementation, needs much fixing
        # z_derivative = np.zeros(N)
        # for i in range(N):
        #     sum_1 = np.zeros(N)
        #     product_1, product_2 = np.ones(N), np.ones(N)
        #     for k in range(N):
        #         t_temp_1, t_temp_2 = t.copy(), t.copy()
        #         for j in range(N):
        #             if j!=k:
        #                 product_1[j] = i - t_temp_1[j]
        #         sum_1[k] = np.prod(product_1)
        #         if k!=i:
        #             product_2[k] = t[i] - t_temp_2[k]
        #     z_derivative[i] = np.sum(sum_1) / np.prod(product_2)

    def update_pseudophase_domain(self):
        N = self.z_flattened.shape[0]
        zt = self.z_flattened[0:N-self.tau]
        z_tau = self.z_flattened[self.tau:N]
        self.widget.pseudophase_points.setData(zt, z_tau)
    
    def compute_derivative(self, z):
        safe_border = np.array([0, 0, 0])
        M = len(z)
        dz = [0] * M
        for m in range(M):
            temp_z = np.concatenate([safe_border, z[m], safe_border])
            K = len(z[m])
            dz[m] = np.zeros(K)
            for k in range(3, K-3):
                dz[m][k-3] = (1 / 60) * (temp_z[k+3] - 9*temp_z[k+2] + 45*temp_z[k+1] // 
                                        - 45*temp_z[k-1] + 9*temp_z[k-2] - temp_z[k-3])
        return dz

    def update_tau(self):
        self.tau = self.widget.slider_tau.value()
        self.widget.slider_tau_value.setText(f'[{self.widget.slider_tau.value()}]')
        self.update_pseudophase_domain()
        
    def show_dominant_cycle_windows(self):
        self.w_new = dcw.DominantCycleWindows(self.z, self.dz)
    
    def add_cycle(self):
        cycle = mw.MainWindow.open_file(self=self)
        self.z.append(cycle)
        self.z_flattened = np.hstack(np.asarray(self.z, dtype='object')).astype('float64')
        self.on_update()
