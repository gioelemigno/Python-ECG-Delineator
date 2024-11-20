from cv2 import transform

#from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib as mpl
#from matplotlib import pyplot as plt
import numpy as np
from sympy import comp

from termcolor import colored
#import NeuroKit.neurokit2 as nk

from icecream import ic

import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.ticker import AutoMinorLocator
import os
from math import ceil 
import json


from EcgCanvas import *
from GUI import *

##############
import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
###############

from MainWindow import *



def lead_convertion_to_millivolt(lead, to_millivolt):
    res = [v*to_millivolt for v in lead]
    return res

def PQRST_to_seconds(data, sampling_rate):
    step = 1/sampling_rate
    res = dict()
    for comp in data.keys():
        values = [step*v for v in data[comp]]
        res[comp] = values
    return res

'''
file_in = '22q11_22_003_ECG_MDC_ECG_LEAD_II.json'

with open(file_in, 'r') as f:
    data_loaded = json.load(f)

to_millivolt = data_loaded['raw_ECG']['to_millivolt']
sampling_rate = data_loaded['raw_ECG']['sampling_rate']


ecg = lead_convertion_to_millivolt(data_loaded['raw_ECG']['signal'], to_millivolt=to_millivolt)
pqrst = PQRST_to_seconds(data_loaded['PQRST'], sampling_rate)

'''
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
