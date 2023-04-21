from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np

class DominantCycleWindows:
    def __init__(self, z, dz):
        self.z = z
        self.dz = dz

        # grid = QGridLayout()
        # self.setLayout(grid)

        # table widget
        
        self.table_subwindow = QWidget()
        self.table_subwindow.setWindowTitle('Відстані')
        self.table_subwindow.setStyleSheet('''
        QWidget {
            background-color: #FFFFFF;
        }''')
        vlayout = QVBoxLayout()
        self.table_subwindow.setLayout(vlayout)

        table_title = QLabel()
        table_title.setText('Відстані Гаусдорфа між циклами')
        table_title.setStyleSheet('''
        QLabel {
            font-size: 14px;
            font-weight: bold;
        }
        ''')
        vlayout.addWidget(table_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.tableWidget = QTableWidget()
        self.M = len(z)
        labels = np.arange(1, self.M+1).astype('str')
        self.tableWidget.setRowCount(self.M)
        self.tableWidget.setColumnCount(self.M)
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.setVerticalHeaderLabels(labels)
        vlayout.addWidget(self.tableWidget)

        # plot widget
        
        self.graph_subwindow = QWidget()
        self.graph_subwindow.setContentsMargins(10, 10, 10, 10)
        self.graph_subwindow.setWindowTitle('Фазові портрети циклів')
        self.graph_subwindow.setStyleSheet('''
        QWidget {
            background-color: #FFFFFF;
        }''')
        vlayout = QVBoxLayout()
        self.graph_subwindow.setLayout(vlayout)
    
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel(axis='bottom', text='z(t)', color='black')
        self.graphWidget.setLabel(axis='left', text="z '(t)", color='black')
        self.graphWidget.setMenuEnabled()
        self.graphWidget.setBackground('w')
        self.graphWidget.showButtons()
        self.graphWidget.showGrid(x=True, y=True, alpha=1)
        self.pen = pg.mkPen(color="k", width=2, style=Qt.PenStyle.SolidLine)
        vlayout.addWidget(self.graphWidget)

        # grid.addWidget(self.graphWidget, 0, 1)

        self.analyze_cycle_phase(self.z, self.dz, self.M)

    def euclidean_distance(self, x_i, x_j, y_i, y_j):
        rho = np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
        return rho

    def hausdorff_distance(self, x_i, x_j, y_i, y_j, inverted=0):
        if not inverted:
            h = (self.euclidean_distance(x_i, x_j, y_i, y_j)).min(axis=1).max(axis=0)
        elif inverted:
            h = (self.euclidean_distance(x_i, x_j, y_i, y_j)).min(axis=0).max(axis=0)
        return h

    def linerar_normalization(self, z, dz, M):
        z_norm = [0] * M
        dz_norm = [0] * M
        self.phase_plots = [0] * M
        for m in range(M):
            z_min, dz_min = z[m].min(), dz[m].min()
            z_max, dz_max = z[m].max(), dz[m].max()
            z_norm[m] = (z[m] - z_min) / (z_max - z_min)
            dz_norm[m] = (dz[m] - dz_min) / (dz_max - dz_min)
            self.phase_plots[m] = self.graphWidget.plot(z_norm[m], dz_norm[m], pen=self.pen)
        return z_norm, dz_norm
    
    def analyze_cycle_phase(self, z, dz, M):
        z_norm, dz_norm = self.linerar_normalization(z, dz, M)
        H = np.zeros((M, M))
        for i in range(H.shape[0]):
            x_i = z_norm[i].reshape(-1, 1)
            y_i = dz_norm[i].reshape(-1, 1)
            for j in range(H.shape[1]):
                x_j = z_norm[j]
                y_j = dz_norm[j]
                h_ij = self.hausdorff_distance(x_i, x_j, y_i, y_j, 0)
                h_ji = self.hausdorff_distance(x_i, x_j, y_i, y_j, 1)
                H[i, j] = max(h_ij, h_ji)
                self.tableWidget.setColumnWidth(j, 55)
                self.tableWidget.setItem(i, j, QTableWidgetItem(f'{round(H[i,j], 6)}'))
        H_min = np.argmin(np.sum(H, axis=0))

        highlight_pen = pg.mkPen(color="red", width=3, style=Qt.PenStyle.SolidLine)
        self.phase_plots[H_min].clear()
        self.phase_plots.pop(H_min)
        self.phase_plots.append(self.graphWidget.plot(z_norm[H_min], dz_norm[H_min], pen=highlight_pen))
        for m in range(self.M):
            self.tableWidget.item(m, H_min).setBackground(QColor(255,143,143))
            self.tableWidget.item(H_min, m).setBackground(QColor(255,143,143))
        self.graph_subwindow.show()
        self.table_subwindow.show()

        



