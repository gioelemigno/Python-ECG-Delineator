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

from SubWindow import *


def click_show_subplot(self):
    self.sub_window.show()
    self.refresh_canvas()

def clickMethod2(self):
    self.sub_window.show()

    
    self.refresh_canvas()

    self.label.setText("my yyy label!")
    #ic(self)
    self.terminal.show_next_command()
    return

def clickMethod(self):
    self.label.setText("my yyy label!")
    #ic(self)
    self.terminal.show_prev_command()
    return

def click_next_ecg(self):
    self.terminal.run_command("load_folder_next")


class GUI:


    def __init__(self, mainWindow, terminal):#, figure, axes):
        #self.figure = figure
        #self.axes = axes
        self.terminal = terminal
        self.ECG_CANVAS_IDS = {
            'MAIN_ECG_CANVAS': 0,
            'SUBPLOT_ECG_CANVAS': 1
        }

        self.sub_window_amplify_ecg = True 
        self.max_ecg_amplitude = 2.8
        #
        self.ecg_calls = None

        self.sub_window = SubWindow(terminal=terminal, ecg_canvas_id=self.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS'])

        self.interactive_ecg_canvas = InteractiveEcgCanvas(window=mainWindow, 
                                                            terminal=terminal, 
                                                            ecg_canvas_id=self.ECG_CANVAS_IDS['MAIN_ECG_CANVAS'],
                                                            use_toolbar=True)
        self.layout = QtWidgets.QVBoxLayout()
        #self.layout.addWidget(self.toolbar)
        #self.layout.addWidget(self.sc)
        self.layout.addLayout(self.interactive_ecg_canvas.layout)


        self.label = QtWidgets.QLabel(mainWindow)
        self.label.setText("my first label!")
        #self.label.move(50,50)

        self.pybutton = QPushButton('SUBPLOT ZOOM', mainWindow)
        self.pybutton.clicked.connect(lambda: click_show_subplot(self))
        self.layout.addWidget(self.pybutton)


        self.button_next_lead = QPushButton('NEXT ECG', mainWindow)
        self.button_next_lead.clicked.connect(lambda: click_next_ecg(self))
        self.layout.addWidget(self.button_next_lead)
        self.set_enable_next_lead(False)
        #self.button_next_lead.setEnabled(False)

#        self.pybutton2 = QPushButton('Click me next ', mainWindow)
#        self.pybutton2.clicked.connect(lambda: clickMethod2(self))
#        self.layout.addWidget(self.pybutton2)

        #self.pybutton.resize(100,32)
        #self.pybutton.move(50, 50)        
        self.layout.addWidget(self.label)
        #self.terminal.write("clicked")
        #return

    def refresh_label_check_order(self, hb_idx='current'):
        if hb_idx == None:
            self.sub_window.refresh_label_check_order(None)
        elif hb_idx == 'current':
            idx = self.sub_window.hb_zooming
            self.sub_window.refresh_label_check_order(idx)
        else:
            self.sub_window.refresh_label_check_order(hb_idx)



    def refresh_info(self, info_dict):
        self.sub_window.checkBox_info_is_inv.setChecked(info_dict['is_inverted'])


    def set_title_subwindow(self, title):
        self.sub_window.setWindowTitle(title)
    
    def set_is_inverted_check_box(self, is_checked):
        self.sub_window.checkBox_info_is_inv.setChecked(is_checked)

    def set_enable_next_lead(self, enable):
        self.button_next_lead.setEnabled(enable)

    def reset_subplot_zoom_in(self):
        self.sub_window.hb_zooming = None
        self.sub_window.interactive_ecg_canvas.ecg_canvas.axes.set_xlim(-2, -1)


    def clean_canvas(self):
        self.interactive_ecg_canvas.ecg_canvas.clean_canvas()
        self.sub_window.interactive_ecg_canvas.ecg_canvas.clean_canvas()
        self.sub_window.hide()


    def get_subplot_current_hb(self):
        return self.sub_window.hb_zooming

    def subplot_zoom_in(self, hb_idx, min_x, max_x):
        return self.sub_window.zoom_in(hb_idx, min_x, max_x)

    def binding_ecg_calls(self, ecg_calls):
        self.ecg_calls = ecg_calls
        self.sub_window.ecg_calls = ecg_calls

  

    def refresh_canvas(self, ecg_canvas_ids='all'):
        if type(ecg_canvas_ids) == str:
            if ecg_canvas_ids == 'all':
                self.interactive_ecg_canvas.ecg_canvas.figure.canvas.draw_idle()
                self.sub_window.interactive_ecg_canvas.ecg_canvas.figure.canvas.draw_idle()           
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")        
        else:
            if ecg_canvas_ids == self.ECG_CANVAS_IDS['MAIN_ECG_CANVAS']:
                self.interactive_ecg_canvas.ecg_canvas.figure.canvas.draw_idle()
            elif ecg_canvas_ids == self.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS']:
                self.sub_window.interactive_ecg_canvas.ecg_canvas.figure.canvas.draw_idle()           
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")   

    def clickMethod(self):
        #self.label.setText("my yyy label!")
        print("hhh")
    
    def plot_signal(self, ecg, sampling_rate, title_filepath='-'): 
        self.interactive_ecg_canvas.ecg_canvas.plot_ecg(ecg=ecg, sampling_rate=sampling_rate, title_filepath=title_filepath)
        
        ecg_sub_window = ecg 
        if self.sub_window_amplify_ecg:
            abs_max = abs(max(ecg_sub_window, key=abs))
            to_normalize = abs(self.max_ecg_amplitude) / abs_max
            assert(to_normalize > 0)
            ecg_sub_window = to_normalize * np.array(ecg_sub_window)
        self.sub_window.interactive_ecg_canvas.ecg_canvas.plot_ecg(ecg=ecg_sub_window, sampling_rate=sampling_rate, title_filepath=title_filepath)
        self.sub_window.reset()#interactive_ecg_canvas.ecg_canvas.axes.set_xlim(-2, -1)


    def plot_events(self, pqrst):    
        self.interactive_ecg_canvas.ecg_canvas.plot_PQRST(pqrst)
        self.sub_window.interactive_ecg_canvas.ecg_canvas.plot_PQRST(pqrst)
        self.sub_window.reset()#interactive_ecg_canvas.ecg_canvas.axes.set_xlim(-2, -1)


    def set_PQRST_component(self, heartbeat_idx, component, value, ecg_canvas_ids='all'):
        if type(ecg_canvas_ids) == str:
            if ecg_canvas_ids == 'all':
                self.interactive_ecg_canvas.ecg_canvas.set_PQRST_component(heartbeat_idx, component, value)
                self.sub_window.interactive_ecg_canvas.ecg_canvas.set_PQRST_component(heartbeat_idx, component, value)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")        
        else:
            if ecg_canvas_ids == self.ECG_CANVAS_IDS['MAIN_ECG_CANVAS']:
                self.interactive_ecg_canvas.ecg_canvas.set_PQRST_component(heartbeat_idx, component, value)
            elif ecg_canvas_ids == self.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS']:
                self.sub_window.interactive_ecg_canvas.ecg_canvas.set_PQRST_component(heartbeat_idx, component, value)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")  

    # to remove
    def to_remove_move_PQRST_component(self, heartbeat_idx, component, value, ecg_canvas_ids='all'):
        if type(ecg_canvas_ids) == str:                                             
            if ecg_canvas_ids == 'all':
                self.interactive_ecg_canvas.ecg_canvas.move_PQRST_component(heartbeat_idx, component, value)
                self.sub_window.interactive_ecg_canvas.ecg_canvas.move_PQRST_component(heartbeat_idx, component, value)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")        
        else:
            if ecg_canvas_ids == self.ECG_CANVAS_IDS['MAIN_ECG_CANVAS']:
                self.interactive_ecg_canvas.ecg_canvas.move_PQRST_component(heartbeat_idx, component, value)
            elif ecg_canvas_ids == self.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS']:
                self.sub_window.interactive_ecg_canvas.ecg_canvas.move_PQRST_component(heartbeat_idx, component, value)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")   


    def to_nan_heartbeats(self, ids, exceptions_components=[]):
        self.interactive_ecg_canvas.ecg_canvas.to_nan_heartbeats(ids, exceptions_components=exceptions_components)
        self.sub_window.interactive_ecg_canvas.ecg_canvas.to_nan_heartbeats(ids, exceptions_components=exceptions_components)



    def set_visibility_PQRST_component(self, heartbeat_idx, component, visible=False, ecg_canvas_ids='all'):           
        if type(ecg_canvas_ids) == str:
            if ecg_canvas_ids == 'all':
                self.interactive_ecg_canvas.ecg_canvas.set_visibility_PQRST_component(heartbeat_idx, component, visible)
                self.sub_window.interactive_ecg_canvas.ecg_canvas.set_visibility_PQRST_component(heartbeat_idx, component, visible)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")        
        else:
            if ecg_canvas_ids == self.ECG_CANVAS_IDS['MAIN_ECG_CANVAS']:
                self.interactive_ecg_canvas.ecg_canvas.set_visibility_PQRST_component(heartbeat_idx, component, visible)
            elif ecg_canvas_ids == self.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS']:
                self.sub_window.interactive_ecg_canvas.ecg_canvas.set_visibility_PQRST_component(heartbeat_idx, component, visible)
            else:
                raise ValueError(f"invalid argument: {ecg_canvas_ids=}")   