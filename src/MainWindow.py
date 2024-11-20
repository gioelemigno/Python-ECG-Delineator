from cv2 import transform

from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
from sympy import comp

from termcolor import colored
#import NeuroKit.neurokit2 as nk

from icecream import ic

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import os
from math import ceil 
import json

from EcgCanvas import *

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
###############
from EcgCanvas import *
from GUI import *
from EcgTerminal import *

from Datamanager import *

from PyQt5.QtGui import QIcon
from EcgCalls import *


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        terminal = EcgTerminal()
        gui = GUI(self, terminal)#figure=sc.fig, axes=sc.axes)
        datamanager = Datamanager()

        ecg_calls = EcgCalls(gui=gui, datamanager=datamanager, terminal=terminal)


        gui.binding_ecg_calls(ecg_calls)
        #terminal.binding_Datamanager(datamanager)
        #terminal.binding_GUI(gui)
        terminal.binding_ecg_calls(ecg_calls)
    

                # Cheap hack to estimate what 80x25 should be in pixels and resize to it
        #terminal.resizeApp(app)

        # Launch DEFAULT_TTY_CMD in the terminal
        #terminal.spawn(DEFAULT_TTY_CMD)

        # Take advantage of how Qt lets any widget be a top-level window
        #mainwin.show()
        layout = QtWidgets.QVBoxLayout()
        
        #layout.addWidget(gui.toolbar)
        #layout.addWidget(gui.sc)

        layout.addLayout(gui.layout)
        layout.addWidget(terminal)

        ecg_calls.add_command_load_data_callbacks("keep_best_hbs 5")
        #datamanager.add_cmd_upon_load_data("keep_best_hbs 5")
        #
        #terminal.run_command("load 22q11_22_114_ECG_MDC_ECG_LEAD_II.json", echo_command=True)
        #terminal.run_command("load ecg.json", echo_command=True)
        terminal.run_command("load_folder ecg_in ecg_out", echo_command=True)

        #
        #l = datamanager.get_best_heartbeats(5)
        #l = datamanager.compute_PQRST_qualities()#get_best_heartbeats(5)
        #ic(l)
        #for hb_idx in range(len(datamanager.events['R'])):
        #    print(f"{hb_idx=}  - quality = {datamanager.get_hb_quality(hb_idx)}")
        #terminal.run_command("reduce 5", echo_command=True)
        #
        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        #widget.setFixedWidth(20)
        widget.setLayout(layout)

        self.setWindowIcon(QIcon('icon.jpg'))  
        #gui.plot_signal(ecg, sampling_rate)
        #gui.plot_events(pqrst)
        self.setCentralWidget(widget)

        self.show()
