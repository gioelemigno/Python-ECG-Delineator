import copy
from typing import Optional
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
from Terminal import *


class EcgCalls:
    def __init__(self, gui, datamanager, terminal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui = gui 
        self.datamanager = datamanager
        self.terminal = terminal
        #
        self.load_data_callbacks = []
        #
        ## temporaly data associated to a file
        self.best_heartbeats = None 
        ## temp data associated to folders
        self.folder_in = None 
        self.folder_out = None
    
    def add_command_load_data_callbacks(self, cmd):
        self.load_data_callbacks.append(cmd)

    def clean_file(self):
        self.best_heartbeats = None 

    def clean_folder(self):
        self.folder_in = None 
        self.folder_out = None


    def restore_heartbeat_from_file(self, hb_idx):
        self.datamanager.make_backup()
        #
        self.datamanager.restore_heartbeat_from_file(hb_idx)
        #
        self.gui.plot_events(self.datamanager.events)
        #
        self.gui.refresh_canvas()


    def set_PQRST_component(self, 
                            heartbeat_idx, 
                            component, 
                            value, 
                            ecg_canvas_ids='all', 
                            datamanager_update=True):

        self.gui.set_PQRST_component(heartbeat_idx, component, value, ecg_canvas_ids=ecg_canvas_ids)
        self.gui.refresh_canvas(ecg_canvas_ids=ecg_canvas_ids)

        if datamanager_update:
            self.datamanager.make_backup()
            #
            self.datamanager.set_PQRST_component(heartbeat_idx, component, value)


    def to_only_R(self, hb_ids):
        return self.to_nan_heartbeats(hb_ids, exceptions_components=['R'])

    def to_nan_heartbeats(self, hb_ids, exceptions_components=[]):
        self.datamanager.make_backup()
        #
        self.datamanager.to_nan_heartbeats(hb_ids, exceptions_components=exceptions_components)                  
        self.gui.to_nan_heartbeats(hb_ids, exceptions_components=exceptions_components)
        #
        self.gui.refresh_canvas()  

    def keep_best_heartbeats(self, n_best):
        self.datamanager.make_backup()
        #

        ## to remove
        best_hbs = self.datamanager.get_best_heartbeats(n_best)
        #self.datamanager.best_hb_ids = best_hbs

        self.best_heartbeats = best_hbs#self.datamanager.get_best_heartbeats(n_best)

        hbs_to_nan = [idx for idx in range(len(self.datamanager.events['R'])) if not idx in best_hbs]
        #
        self.to_nan_heartbeats(hbs_to_nan, exceptions_components=['R'])

    def get_best_heartbeats(self):
        return self.best_heartbeats

    def reload_data(self):
        self.datamanager.make_backup()
        #
        self.clean_file()
        #
        self.datamanager.reload_data()
        #
        self.gui.plot_events(self.datamanager.events)
        #
        self.gui.refresh_canvas()
        #
        self.run_load_data_callbacks()
                                     

    def set_no_nan_missings(self, hb_idx: int):
        R_peak = self.datamanager.events['R'][hb_idx]          

        if np.isnan(R_peak):
            raise Exception(f"R_peak in {hb_idx=} is nan")
        
        for comp in self.datamanager.events.keys():
            if np.isnan(self.datamanager.events[comp][hb_idx]):
                value = R_peak + 0.15
                self.set_PQRST_component(hb_idx, comp, value)
                            
                     
          

    def _load_file_on_gui(self, filepath: str, 
                                current_idx:Optional[str]='-', 
                                max_idx:Optional[str]='-', 
                                refresh:Optional[bool]=False):


        if filepath is None:
            self.gui.clean_canvas()
            self.datamanager.clean()
            self.gui.set_enable_next_lead(False)
            self.gui.refresh_label_check_order(None)
        else:
            data_info = self.get_info()
            signal = np.array(self.datamanager.signal)
            if data_info['is_inverted']:
                signal = (-1) * signal
       
            self.gui.plot_signal(signal, self.datamanager.sampling_rate, title_filepath=filepath)
            self.gui.plot_events(self.datamanager.events)
            #
            self.gui.refresh_info(data_info)
        #       
        info_idx = f"{current_idx}/{max_idx}"
        self.gui.set_title_subwindow(info_idx)
        print(info_idx + "\n")
        #

        #
        if refresh:
            self.gui.refresh_canvas()

    def load_file(self, filepath):
        self.clean_file()
        self.datamanager.load_file(filepath)
        #
        self._load_file_on_gui(filepath)
        '''
        self.gui.plot_signal(self.datamanager.signal, self.datamanager.sampling_rate, title_filepath=filepath)
        self.gui.plot_events(self.datamanager.events)
        #
        self.gui.refresh_canvas()
        '''
        self.run_load_data_callbacks()



    
    def save_on_file(self, filepath):
        self.datamanager.save_on_file(filepath)

    

    def subplot_zoom_in(self, hb_idx, pre_R=0.4, post_R=0.5): 
        R_peak = self.datamanager.events['R'][hb_idx]          

        if np.isnan(R_peak):
            raise Exception(f"R_peak in {hb_idx=} is nan")
        
        min_x = R_peak - pre_R 
        max_x = R_peak + post_R
        self.gui.subplot_zoom_in(hb_idx, min_x, max_x)
        self.gui.refresh_canvas(self.gui.ECG_CANVAS_IDS['SUBPLOT_ECG_CANVAS'])

        self.gui.refresh_label_check_order(hb_idx)



    def subplot_zoom_in_next_hb(self, pre_R=0.4, post_R=0.5):
        current = self.gui.get_subplot_current_hb()
        restrict_list_hbs = self.best_heartbeats#self.datamanager.best_hb_ids
        next_hb = self.datamanager.get_next_hb(current, restrict_list_hbs=restrict_list_hbs)
        if not next_hb is None:
            self.subplot_zoom_in(next_hb, pre_R=pre_R, post_R=post_R)
        return next_hb


    def subplot_zoom_in_prev_hb(self, pre_R=0.4, post_R=0.5):
        current = self.gui.get_subplot_current_hb()
        restrict_list_hbs = self.best_heartbeats#self.datamanager.best_hb_ids
        prev_hb = self.datamanager.get_prev_hb(current, restrict_list_hbs=restrict_list_hbs)
        if not prev_hb is None:
            self.subplot_zoom_in(prev_hb, pre_R=pre_R, post_R=post_R)
        return prev_hb

    def undo(self):
        self.datamanager.restore_backup()
        #
        self.gui.plot_events(self.datamanager.events)
        #
        #self.gui.refresh_canvas()
        self.gui.refresh_canvas()


    def is_valid_component(self, component):
        return component in self.datamanager.events.keys()

    def get_printable_component_values(self, component):
        res =  str(self.datamanager.events[component])
        return res#json.dumps(res, indent=4) 


    def get_printable_hb_idx_values(self, hb_idx):
        res = {}
        for c in self.datamanager.events.keys():
            res[c] = self.datamanager.events[c][hb_idx]

        return json.dumps(res, indent=4) 


    def load_folder(self, folder_in, folder_out):
        self.clean_folder()
        #
        self._load_file_on_gui(None) #self.gui.clean_canvas()
        #
        self.datamanager.load_folder(folder_in, folder_out)
        #
        self.gui.set_enable_next_lead(True)
        self.gui.refresh_canvas()



    def load_folder_index(self, index):
        self.clean_file()
        #
        res = self.datamanager.load_folder_index(index)
        #
        self._load_file_on_gui(**res)
        #
        self.run_load_data_callbacks()
        #
        self.gui.refresh_canvas()
    
 
    def load_folder_prev(self):
        self.clean_file()
        #
        res = self.datamanager.load_folder_prev()
        if res is None:
            self._load_file_on_gui(None)
            self.clean_folder()         
        else:
            self._load_file_on_gui(**res)
            #
            self.run_load_data_callbacks()
        
        self.gui.refresh_canvas()

    def get_best_heatbeats(self):
        if self.best_heartbeats is None:
            return None 
        return copy.deepcopy(self.best_heartbeats)
        
    def load_folder_next(self):
        self.clean_file()
        #
        res = self.datamanager.load_folder_next()
        if res is None:
            self._load_file_on_gui(None)
            self.clean_folder()         
        else:
            self._load_file_on_gui(**res)
            #
            self.run_load_data_callbacks()
        
        self.gui.refresh_canvas()


    def run_load_data_callbacks(self):
        #print("run_load_data_callbacks\n")
        for cmd in self.load_data_callbacks:
            self.terminal.run_command(cmd, echo_command=True, prompt_after=False)

    def add_heartbeat(self, position_R_peak):
        self.datamanager.make_backup()
        #
        self.datamanager.add_heartbeat(position_R_peak)
        self.gui.plot_events(self.datamanager.events)
        #
        self.gui.refresh_canvas()

    def del_heartbeat(self, hb_idx):  
        self.datamanager.make_backup()
        # 
        self.datamanager.del_heartbeat(hb_idx)
        self.gui.plot_events(self.datamanager.events)
        #
        self.gui.refresh_canvas()


    def check_heartbeats(self, hb_ids):
        if type(hb_ids) == str:
            if hb_ids != 'all':
                raise ValueError(f"unknown string for {hb_ids=}")
            hb_ids = list(range(len(self.datamanager.events['R'])))
            wrong_orders = {}
            for idx in hb_ids:
                res = self.datamanager.check_heartbeat(idx) 
                wrong_orders[idx] = res            
        elif type(hb_ids) == list:
            wrong_orders = {}
            for idx in hb_ids:
                res = self.datamanager.check_heartbeat(idx) 
                wrong_orders[idx] = res
        else:
            idx = hb_ids
            wrong_orders = self.datamanager.check_heartbeat(idx) 
        return wrong_orders


    def get_info(self):
        return self.datamanager.get_info()


    def set_info(self, field, value):
        self.datamanager.set_info(field, value)
        data_info = self.datamanager.get_info()
        self.gui.refresh_info(data_info)
        #
        signal = np.array(self.datamanager.signal)
        if data_info['is_inverted']:
            signal = (-1) * signal
        
        current_hb_idx_zooming = self.gui.get_subplot_current_hb()
        filepath = self.datamanager.filepath_loaded
        self.gui.plot_signal(signal, self.datamanager.sampling_rate, 
                                    title_filepath=filepath)
        
        # restore zoomin
        if not current_hb_idx_zooming is None:
            self.subplot_zoom_in(current_hb_idx_zooming)

        self.gui.refresh_canvas()
