import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import MainWindow as mw
import CycleModel as cm

if __name__ == "__main__":

    # initialize ecg signal
    waves_default = {'P': [0.1, 395, 20, 20, 0, 0],
                    'Q': [-0.1, 489, 9, 1, 0, 0],
                    'R': [1, 500, 3, 3, 0, 0],
                    'S': [-0.2, 511, 1, 22, 0, 0],
                    'ST': [0, 583, 1, 1, 0, 0], 
                    'T': [0.2, 660, 25, 25, 0, 0]}
    
    ecg_init = cm.CycleModel(60, waves_default)
    ecg_init.construct_cycle()
    
    app = QApplication(sys.argv)
    w = mw.MainWindow(ecg_init)
    w.show()
    sys.exit(app.exec())
