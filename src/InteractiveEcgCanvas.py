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

from Terminal import *

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


def button_press_callback(self, event):
    '''
    #print(event.__dict__)
    self.menu = QMenu(self.window)
    self.menu.addMenu("Configuration")
    self.menu.addSeparator()
    self.menu.addMenu("Profile")

    pos = QPoint(event.x, 600-event.y)#
   # pos = self.window.mapToGlobal(QPoint(event.x, event.y))

    print(f"{pos=} --- {event.x}, {event.y}\n")
    self.menu.exec(pos)
    '''
    # avoid to move an event
    if not self.toolbar is None and self.toolbar.mode in ["zoom rect", 'pan/zoom']:
        return
    #self.label.setText("hhl!")
    t = self.sc.axes.transData.inverted()
    #tinv = ax1.transData 
    xy = t.transform([event.x,event.y])
    x_click = xy[0]
    y_click = xy[1]

    res = self.ecg_canvas.get_nearest_event(x_click, y_click)
    #self.terminal.write(f"{str(res)}\n")

    if not res is None:
        self.moving_PQRST = res
    #print("pressed")


def button_release_callback(self, event):
    t = self.sc.axes.transData.inverted()
    #tinv = ax1.transData 
    xy = t.transform([event.x,event.y])
    x_click = xy[0]
    y_click = xy[1]

    if not self.moving_PQRST is None:
        heartbeat_idx = self.moving_PQRST['heartbeat_idx']
        component = self.moving_PQRST['component']
        value = x_click

        cmd = "set"
        command = f"{cmd} {component} {value} {heartbeat_idx}"
        self.terminal.run_command(command, prompt_after=False)
        #self.ecg_canvas.move_PQRST_component(heartbeat_idx, component, value)
        #self.ecg_canvas.figure.canvas.draw_idle()
        #
        if self.callback_moved_PQRST:
            self.callback_moved_PQRST(self, event, self.moving_PQRST)

    self.moving_PQRST = None
    return 

def motion_notify_callback(self, event):
    t = self.sc.axes.transData.inverted()
    #tinv = ax1.transData 
    xy = t.transform([event.x,event.y])
    x_click = xy[0]
    y_click = xy[1]

    if not self.moving_PQRST is None:
        heartbeat_idx = self.moving_PQRST['heartbeat_idx']
        component = self.moving_PQRST['component']
        value = x_click
        cmd = "set_no_datamanager_update"
        command = f"{cmd} {component} {value} {heartbeat_idx} {self.ecg_canvas_id}"
        self.terminal.run_command(command, prompt_after=False)
    return 


class InteractiveEcgCanvas():
    def __init__(self, window, terminal, ecg_canvas_id, 
                                    use_toolbar=False,
                                    fig_width=20, 
                                    fig_height=15,
                                    fix_height=500):
        self.window = window 
        self.terminal = terminal
        self.ecg_canvas_id = ecg_canvas_id

        self.callback_moved_PQRST = None

        self.moving_PQRST = None
        #
        #fig_width, fig_height = 20, 15

        dpi = mpl.rcParams['figure.dpi'] #default
        self.sc = MplCanvas(self.window, width=fig_width, height=fig_height, dpi=dpi)
        self.sc.fig.subplots_adjust(#hspace=0,
                                #wspace=0.04,
                                left=0.04,
                                right=0.96,
                                #bottom=0.5,
                                #top=0.88
                                )
        if not fix_height is None:
            self.sc.setFixedHeight(fix_height)

        #mpl.rcParams['figure.subplot.hspace'] = 0
        #mpl.rcParams['figure.subplot.wspace'] = 0.04

        self.ecg_canvas = EcgCanvas(figure=self.sc.fig, axes=self.sc.axes)

        self.layout = QtWidgets.QVBoxLayout()#self.window)
        if use_toolbar:
            self.toolbar = NavigationToolbar(self.sc, self.window)
            self.layout.addWidget(self.toolbar)
        else:
            self.toolbar = None 

        self.layout.addWidget(self.sc)

        self.sc.fig.canvas.mpl_connect('button_press_event', 
                                        lambda event: button_press_callback(self, event))
        
        self.sc.fig.canvas.mpl_connect('button_release_event', 
                                        lambda event: button_release_callback(self, event))
        
        self.sc.fig.canvas.mpl_connect('motion_notify_event', 
                                        lambda event: motion_notify_callback(self, event))


