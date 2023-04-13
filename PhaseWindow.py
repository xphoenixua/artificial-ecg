from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import CycleSequence as cs

class PhaseWindow(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setGeometry(500, 200, 700, 600)
        self.setWindowTitle('Фазові портрети відкритої ЕКГ')
        self.amp_seq = data

        # plot widgets

        grid = QGridLayout()
        self.setLayout(grid)

        self.graphLayout = pg.GraphicsLayoutWidget()
        self.graphLayout.setBackground('w')
        self.pen = pg.mkPen(color="k", width=2, style=Qt.PenStyle.SolidLine)
        
        self.time_domain_plot = self.graphLayout.addPlot(row=0, col=0)
        self.time_domain_plot.setTitle('ЕКГ', color='black')
        self.time_domain_plot.setLabel(axis='bottom', text='Час (с)', color='black')
        self.time_domain_plot.setLabel(axis='left', text='Амплітуда (мВ)', color='black')
        self.time_domain_plot.showGrid(x=True, y=True, alpha=1)
        # self.time_domain_plot.setMouseEnabled(y=False)

        self.phase_plot = self.graphLayout.addPlot(row=1, col=0)
        self.phase_plot.setTitle('Фазовий портрет ЕКГ', color='black')
        self.phase_plot.setLabel(axis='bottom', text='z(t)', color='black')
        self.phase_plot.setLabel(axis='left', text="z '(t)", color='black')
        self.phase_plot.showGrid(x=True, y=True, alpha=1)

        self.pseudophase_plot = self.graphLayout.addPlot(row=2, col=0)
        self.pseudophase_points = self.pseudophase_plot.plot(pen=self.pen)
        self.pseudophase_plot.setTitle('Псевдофазовий портрет ЕКГ', color='black')
        self.pseudophase_plot.setLabel(axis='bottom', text='z(t)', color='black')
        self.pseudophase_plot.setLabel(axis='left', text="z(t-𝜏)", color='black')
        self.pseudophase_plot.showGrid(x=True, y=True, alpha=1)

        # self.graphLayout.setMenuEnabled()
        # self.graphLayout.showButtons()
        # self.graphLayout.showGrid(x=True, y=True, alpha=1)
        # self.graphLayout.setMouseEnabled(y=False)

        grid.addWidget(self.graphLayout, 0, 0)

        # tau slider

        self.slider_tau = QSlider(Qt.Orientation.Horizontal)
        
        self.slider_tau_group = QGroupBox()
        self.slider_tau_group.setTitle('Параметр 𝜏')
        self.slider_tau.setMinimumWidth(200)
        
        self.slider_tau_vlayout = QVBoxLayout()
        self.slider_tau_group.setLayout(self.slider_tau_vlayout)
        self.slider_tau_hlayout = QHBoxLayout()
        self.slider_tau_vlayout.addLayout(self.slider_tau_hlayout)

        self.slider_tau_label1 = QLabel()
        self.slider_tau_label1.setText('1')
        self.slider_tau_hlayout.addWidget(self.slider_tau_label1)
        
        self.tau = 8
        self.slider_tau.setMinimum(1)
        self.slider_tau.setMaximum(50)
        self.slider_tau.setSingleStep(1)
        self.slider_tau.setValue(self.tau)
        self.slider_tau.valueChanged.connect(self.update_tau)
        self.slider_tau_hlayout.addWidget(self.slider_tau)
        
        self.slider_tau_label2 = QLabel()
        self.slider_tau_label2.setText('50')
        self.slider_tau_hlayout.addWidget(self.slider_tau_label2)

        self.slider_tau_value = QLabel()
        self.slider_tau_value.setText(f'[{self.slider_tau.value()}]')
        self.slider_tau_vlayout.addWidget(self.slider_tau_value, alignment=Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(self.slider_tau_group, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.plot_time_domain()
        self.plot_phase_domain()
        self.update_pseudophase()

    def plot_time_domain(self):
        Fs = 500
        Ts = 1/Fs
        N = self.amp_seq.shape[0]
        time_seq = np.arange(0, N) * Ts
        self.ecg_sequence = cs.CycleSequence(time_seq=time_seq,
                                            amp_seq=self.amp_seq)
        self.time_domain_points = self.time_domain_plot.plot(self.ecg_sequence.time_seq,
                                                        self.ecg_sequence.amp_seq, 
                                                        pen=self.pen)
    
    def plot_phase_domain(self):
        t = self.ecg_sequence.time_seq
        z = self.ecg_sequence.amp_seq
        N = z.shape[0]
        # dt = np.diff(t)
        # dz = np.diff(z)
        # dzdt = dz / dt
        # dzdt = np.concatenate((dzdt, np.array([0])))
        dt = np.gradient(t)
        dz = np.gradient(z)
        dzdt = dz / dt
        self.phase_points = self.phase_plot.plot(z, dzdt, pen=self.pen)
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
        
    def update_pseudophase(self):
        t = self.ecg_sequence.time_seq
        z = self.ecg_sequence.amp_seq
        N = z.shape[0]
        zt = z[0:N-self.tau]
        z_tau = z[self.tau:N]
        self.pseudophase_points.setData(zt, z_tau)

    def update_tau(self):
        self.tau = self.slider_tau.value()
        self.slider_tau_value.setText(f'[{self.slider_tau.value()}]')
        self.update_pseudophase()

            

