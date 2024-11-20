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

from PyQt5.QtWidgets import QPushButton

from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget

from Terminal import *

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from InteractiveEcgCanvas import *

from EcgCalls import *

from functools import partial
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton



class CustomDialog(QDialog):
    # https://www.pythonguis.com/tutorials/pyqt-dialogs/
    def __init__(self, wind, title, desc):
        super().__init__(wind)

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(desc)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def callback_moved_PQRST(interactive_ecg_canvas, event, moving_PQRST, sub_window):
    hb_idx = moving_PQRST['heartbeat_idx']
    #cmd = f"check {hb_idx}"
    #res = sub_window.terminal.run_command(cmd)
    res = sub_window.ecg_calls.check_heartbeats(hb_idx)
    if len(res) == 0:
        sub_window.label.setText(f"hb_idx={hb_idx}: OK")
        #print("OK\n")
    else:
        sub_window.label.setText(f"hb_idx={hb_idx}: error in {res}")
        #print(f"hb_idx={hb_idx}: error in {res}\n")

class SubWindow(QWidget):

    def refresh_label_check_order(self, hb_idx):
        if hb_idx is None:
            self.label.setText(f"---")
            return

        res = self.ecg_calls.check_heartbeats(hb_idx)

        if len(res) == 0:
            self.label.setText(f"hb_idx={hb_idx}: OK")
            #print("OK\n")
        else:
            self.label.setText(f"hb_idx={hb_idx}: error in {res}")
            #print(f"hb_idx={next_hb}: error in {res}\n")

    def _confirmed_change_lead(self):
        res = self.ecg_calls.check_heartbeats(self.ecg_calls.get_best_heartbeats())
        #res = self.terminal.run_command("check all")
        wrong_order = {}
        for k in res.keys():
            if len(res[k]) > 0:
                wrong_order[k] = res[k]
        if len(list(wrong_order.keys())) > 0:
            title = f"WRONG ORDER IN CURRENT LEAD"
            desc = wrong_order
            desc = json.dumps(desc, indent=4) 
            dlg = CustomDialog(self, title, desc)
            if dlg.exec(): #press OK
                return True
            else: # PRESS CANCEL
                return False 
        return True


    def click_subplot_zoom_in_next(self):
        #cmd = 'subplot_next_hb'
        #next_hb = self.terminal.run_command(cmd)
        next_hb = self.ecg_calls.subplot_zoom_in_next_hb()
        if not next_hb is None:
            self.refresh_label_check_order(next_hb)
        else:
            if self.auto_switch_lead and self._confirmed_change_lead(): # move to next lead
                cmd = "load_folder_next"
                self.terminal.run_command(cmd)#"load_folder_next")
        return

    def click_subplot_zoom_in_prev(self):
        #cmd = 'subplot_prev_hb'
        #prev_hb = self.terminal.run_command(cmd)
        prev_hb = self.ecg_calls.subplot_zoom_in_prev_hb()
        if not prev_hb is None:
            self.refresh_label_check_order(prev_hb)
        else:
            if self.auto_switch_lead and self._confirmed_change_lead(): # move to prev                                                       lead
                cmd = "load_folder_prev"
                self.terminal.run_command(cmd)
                #
                best_hbs = self.ecg_calls.get_best_heatbeats()
                if not best_hbs is None:
                    self.ecg_calls.subplot_zoom_in(best_hbs[-1])
        return

    def location_on_the_screen(self):
        # https://stackoverflow.com/questions/39046059/pyqt-location-of-the-window
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = ag.width() - widget.width()
        y = 2 * ag.height() - sg.height() - widget.height()
        self.move(x, y)

    def reset(self):
        self.hb_zooming = None
        self.interactive_ecg_canvas.ecg_canvas.axes.set_xlim(-2, -1)

    def checked_handler(self, checked):
        if checked:
            self.auto_switch_lead = True
        else:
            self.auto_switch_lead = False
        #print(self.auto_switch_lead)

    def checkBox_info_is_inv_handler(self, checked):
        #print(f"sssss - {checked}\n")
        if checked:
            self.ecg_calls.set_info('is_inverted', True)
        else:
            self.ecg_calls.set_info('is_inverted', False)

    def __init__(self, terminal, ecg_canvas_id):
        super(SubWindow, self).__init__()
        self.auto_switch_lead = False
        self.terminal= terminal
        self.hb_zooming = None
        self.ecg_calls = None
        #self.resize(400, 300)
        self.interactive_ecg_canvas = InteractiveEcgCanvas(window=self, 
                                                            terminal=terminal, 
                                                            ecg_canvas_id=ecg_canvas_id, 
                                                            use_toolbar=True,
                                                            fig_height=100,
                                                            fig_width=5,
                                                        fix_height=None)
        
        self.interactive_ecg_canvas.callback_moved_PQRST = partial(callback_moved_PQRST, sub_window=self)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        #self.layout.addWidget(self.toolbar)
        #self.layout.addWidget(self.sc)
        
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setText("Auto Lead swicth")
        self.checkBox.setGeometry(QtCore.QRect(170, 120, 81, 20))
        self.checkBox.stateChanged.connect(self.checked_handler)
        self.layout.addWidget(self.checkBox)

        self.layout.addLayout(self.interactive_ecg_canvas.layout)
        #self.show()

        self.checkBox_info_is_inv = QtWidgets.QCheckBox(self)
        self.checkBox_info_is_inv.setText("Is inverted?")
        self.checkBox_info_is_inv.setGeometry(QtCore.QRect(170, 120, 81, 20))
        self.checkBox_info_is_inv.stateChanged.connect(self.checkBox_info_is_inv_handler)
        self.layout.addWidget(self.checkBox_info_is_inv)     

        self.label = QtWidgets.QLabel(self)
        self.label.setText("---")
        self.layout.addWidget(self.label)

        # to read: https://stackoverflow.com/questions/59175008/qhboxlayout-size-resize-move
        self.layout_buttons = QtWidgets.QHBoxLayout()
        #self.layout_buttons.setGeometry(QtCore.QRect(20, 20, 30, 30))
        #
        self.pybutton = QPushButton('prev', self)
        #self.pybutton.resize(50, 50)

        self.pybutton.clicked.connect(lambda: self.click_subplot_zoom_in_prev())#self))
        self.layout_buttons.addWidget(self.pybutton)
        #
        self.pybutton2 = QPushButton('next', self)
        #self.pybutton2.resize(50, 50)

        self.pybutton2.clicked.connect(lambda: self.click_subplot_zoom_in_next())#self))
        self.layout_buttons.addWidget(self.pybutton2)
        #
        self.layout.addLayout(self.layout_buttons)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.location_on_the_screen()
        w, h = 732, 960
        self.setFixedSize(w, h)

        #self.show()

    def zoom_in(self, hb_idx, min_x, max_x):
        self.hb_zooming = hb_idx
        self.interactive_ecg_canvas.ecg_canvas.axes.set_xlim(min_x, max_x)
        self.interactive_ecg_canvas.ecg_canvas.set_visibility_PQRST_index(hb_idx, True, other_hb_ids_visible=False)


