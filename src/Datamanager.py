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

import copy
#import NeuroKit.neurokit2 as nk


import random

# -----------------------------------------------------------
def lead_convertion_to_millivolt(lead, to_millivolt):
    res = [v*to_millivolt for v in lead]
    return res
# -----------------------------------------------------------

def seconds_to_index(seconds, sampling_rate):
    step = sampling_rate
    v = seconds
    return int(step*v) if not np.isnan(v) else np.nan

def index_to_seconds(idx, sampling_rate):
    step = 1/sampling_rate
    v = idx
    return step*v
# -----------------------------------------------------------

def PQRST_to_seconds(data, sampling_rate):
    step = 1/sampling_rate
    res = dict()
    for comp in data.keys():
        values = [step*v for v in data[comp]]
        res[comp] = values
    return res

def PQRST_to_index(data, sampling_rate):
    step = sampling_rate
    res = dict()
    for comp in data.keys():
        values = [int(step*v) if not np.isnan(v) else np.nan for v in data[comp]]
        res[comp] = values
    return res
# -----------------------------------------------------------

class Datamanager:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal = None
        self.sampling_rate = None
        self.events = None
        self.data_loaded = None
        #
        self.backups_size = 32
        self.backups_index = -1
        self.backups = [None]*self.backups_size
        #
        self.folder_in = None
        self.list_files_in = None
        self.list_files_index = None
        self.folder_out = None
        #
        self.hb_ids_to_use = None
        #
        self.quality_signal = None
        #
        #self.best_hb_ids = None
        #
        self.upon_load_data_cmds = []
        #
        self.filepath_loaded = None



    def add_cmd_upon_load_data(self, cmd):
        self.upon_load_data_cmds.append(cmd)


    def get_info(self):
        if self.data_loaded is None:
            return None 

        return self.data_loaded['info']            

    def set_info(self, field, value):
        self.data_loaded['info'][field] = value       

    def load_data(self, data):
        self.data_loaded = data
        self._load_data_loaded()

    def _load_data_loaded(self):
        to_millivolt = self.data_loaded['info']['to_millivolt']
        self.sampling_rate = self.data_loaded['info']['sampling_rate']

        ecg = lead_convertion_to_millivolt(self.data_loaded['signal'], to_millivolt=to_millivolt)
        pqrst = PQRST_to_seconds(self.data_loaded['PQRST'], self.sampling_rate)

        self.signal = ecg 
        self.events = pqrst

        #try:
        #    self.quality_signal = nk.ecg_quality(self.signal, sampling_rate=self.sampling_rate,
        #                                                  method='averageQRS', 
        #                                                  approach=None)
        #except:
        #    print("Error occurred during nk.ecg_quality()\n")
        #    self.quality_signal = [0]*len(ecg)

    def clean(self):
        self.signal = None
        self.sampling_rate = None
        self.events = None
        self.data_loaded = None
        #
        self.backups_size = 32
        self.backups_index = -1
        self.backups = [None]*self.backups_size
        #
        self.folder_in = None
        self.list_files_in = None
        self.list_files_index = None
        self.folder_out = None
        #
        self.hb_ids_to_use = None
        #
        self.filepath_loaded = None
        #self.best_hb_ids = None



    def get_hb_quality(self, heartbeat_idx):
        # seconds
        prev_R = 0.4
        post_R = 0.4

        R = self.events['R'][heartbeat_idx]
        if np.isnan(R):
            return None 
        
        len_signal_s = index_to_seconds(len(self.signal)-1, self.sampling_rate)

        start_s = max(0, R-prev_R)
        end_s = min(len_signal_s, R+post_R)

        start = seconds_to_index(start_s, self.sampling_rate)
        end = seconds_to_index(end_s, self.sampling_rate)
        return sum(self.quality_signal[start:end])


    def get_next_hb(self, current, avoid_nan=True, restrict_list_hbs=None):
        if current is None:
            current = -1
        elif current < 0 or current > len(self.events['R']):
            raise ValueError(f"invalid {current=} heartbeat index")
        

        if current == len(self.events['R'])-1: # end array
            return None 

        for idx in range(current+1, len(self.events['R'])):            
            # ignore ids outside `restrict_list_hbs`
            if not restrict_list_hbs is None and not idx in restrict_list_hbs:
                continue 

            if not np.isnan(self.events['R'][idx]) or not avoid_nan:
                return idx

        
        return None


    def get_prev_hb(self, current, avoid_nan=True, restrict_list_hbs=None):
        if current is None:
            return None
            #current = len(self.events['R']) 
        elif current < 0 or current > len(self.events['R']):
            raise ValueError(f"invalid {current=} heartbeat index")
        
        if current == 0: # end array
            return None 

        for idx in range(current-1, -1, -1): # current = 3 -> [2, 1, 0]
            # ignore ids outside `restrict_list_hbs`
            if not restrict_list_hbs is None and not idx in restrict_list_hbs:
                continue 

            if not np.isnan(self.events['R'][idx]) or not avoid_nan:
                return idx 

        return None


    def load_file(self, filepath):
        self.backups_size = 32
        self.backups_index = -1
        self.backups = [None]*self.backups_size
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.filepath_loaded = filepath
        self.load_data(data)
  

    def reload_data(self):
        self._load_data_loaded()
    

    def set_PQRST_component(self, heartbeat_idx, component, value):
        self.events[component][heartbeat_idx] = value


    # to delete
    def set_value(self, heartbeat, component, value):
        self.events[component][heartbeat] = value


    def load_folder(self, folder_in, folder_out):
        assert(os.path.isdir(folder_in))
        assert(os.path.isdir(folder_out))
        #
        list_files = sorted(os.listdir(folder_in))
        self.clean()
        self.list_files_in = list_files
        self.folder_in = folder_in
        self.folder_out = folder_out
        self.list_files_index = -1

    def load_folder_index(self, index, save_current=True):
        if index >= len(self.list_files_in):
            raise ValueError(f"{index=} exceeds limit of {len(self.list_files_in)}")
        
        if save_current and self.list_files_index >= 0:
            filename = self.list_files_in[self.list_files_index]
            filepath = os.path.join(self.folder_out, filename)
            self.save_on_file(filepath, avoid_overwrite=False)

        self.list_files_index = index 
        filename = self.list_files_in[self.list_files_index]
        filepath = self.get_filepath_input(filename)#self.folder_in, #os.path.join(self.folder_in, filename)
        self.load_file(filepath)

        res = {
            'filepath': filepath,
            'current_idx': self.list_files_index,
            'max_idx': len(self.list_files_in)-1,
        }
        return res #filepath


    def load_folder_next(self, save_current=True):
        next_idx = self.list_files_index + 1
        if next_idx == len(self.list_files_in):
            # save current data
            filename = self.list_files_in[self.list_files_index]
            filepath = os.path.join(self.folder_out, filename)
            self.save_on_file(filepath, avoid_overwrite=False)

            return None
        else:
            return self.load_folder_index(next_idx, save_current=save_current)

    def load_folder_prev(self, save_current=True):
        prev_idx = self.list_files_index - 1
        if prev_idx < 0:
            return None
        else:
            return self.load_folder_index(prev_idx, save_current=save_current)



    def save_on_file(self, filepath, avoid_overwrite=True):
        self.set_info('human_checked', True)
        
        to_json = copy.deepcopy(self.data_loaded)

        pqrst_ids = PQRST_to_index(self.events, self.sampling_rate)
        for component in to_json['PQRST'].keys():
            to_json['PQRST'][component] = pqrst_ids[component]

        filepath = os.path.join(filepath)

        if os.path.isfile(filepath):
            print("Warning! Overwritten a file \n")
            if avoid_overwrite:
                raise FileExistsError("Export file already exist")

        with open(filepath, "w") as f:
            json.dump(to_json, f, indent=4)
        return 0

    def restore_heartbeat_from_file(self, hb_idx):
        position_R_secs = self.events['R'][hb_idx]

        # search index in `data_loaded`, could be different from `hb_idx`
        hb_idx_dl = None
        for idx, R in enumerate(self.data_loaded['PQRST']['R']):
            R_sec = index_to_seconds(R, self.sampling_rate)
            if np.abs(R_sec-position_R_secs) < 0.01:
                hb_idx_dl = idx
                break 
        if hb_idx_dl is None:
            raise Exception(f"Impossible to load PQRST from file with {position_R_secs=}")
        
        for component in self.events.keys():
            from_file = self.data_loaded['PQRST'][component][hb_idx_dl]
            self.events[component][hb_idx] = index_to_seconds(from_file, self.sampling_rate)


    def get_filepath_input(self, filename, check_in_folder_out=True):
        if check_in_folder_out:
            if filename in os.listdir(self.folder_out):
                return os.path.join(self.folder_out, filename)
        return os.path.join(self.folder_in, filename)

    def _compute_distances_R(self, hb_idx):
        components = list(self.events.keys())
        
        res = dict()
        reference = self.events['R'][hb_idx]
        for c in components:
            res[c] = self.events[c][hb_idx] - reference
        res['R'] = 0.0 if not np.isnan(reference) else np.nan
        return res

        
    def compute_PQRST_qualities(self):
        distances = dict()
        for hb_idx in range(len(self.events['R'])):
            distances[hb_idx] = self._compute_distances_R(hb_idx)

        distances_c = dict()        
        for c in self.events.keys():
            distances_c[c] = list()
            for hb_idx in range(len(self.events['R'])):
                dis = distances[hb_idx][c]
                if not np.isnan(dis):
                    distances_c[c].append(dis)
        mean_distances = dict()
        for c in self.events.keys():
            if len(distances_c[c]) > 0:
                mean_distances[c] = np.mean(distances_c[c])
            else:
                mean_distances[c] = np.nan

        qualities_PQRST = []#dict()
        for hb_idx in range(len(self.events['R'])):
            q = 0
            for c in self.events.keys():
                m = mean_distances[c]
                d = distances[hb_idx][c]
                diff = abs(m-d)
                if np.isnan(diff):
                    q -= 5
                else:
                    q += diff 
            qualities_PQRST.append(q) #[hb_idx] = q

        # translate all values in [0, +inf]
        qualities_PQRST = np.array(qualities_PQRST) 
        min_quality = min(qualities_PQRST)
        qualities_PQRST = qualities_PQRST + abs(min_quality)
        #qualities_PQRST = np.array(qualities_PQRST) 
        #qualities_PQRST = qualities_PQRST / sum(qualities_PQRST)

        return qualities_PQRST

    def get_best_heartbeats(self, best_n):
        hb_ids = list(range(len(self.events['R'])))#self.data_loaded['PQRST']['R'])))

        if len(hb_ids) > best_n+3:# and len(hb_ids) > 6:
            hb_ids = hb_ids[1:-3] # remove first and last two hbs

        results = {}
        for i in hb_ids:
            n_unordered = len(self.check_heartbeat(i))
            if not n_unordered in results.keys():
                results[n_unordered] = []
            results[n_unordered].append(i)

        levels = []
        for i, ns_unordered in enumerate([[0, 1], [2, 3, 4], [5, 6, 7, 8], [9, 10]]):
            candidates = []
            for nu in ns_unordered:
                if nu in results.keys():
                    candidates.extend(results[nu])
            
            if len(candidates) > 0:
                levels.append(candidates)

        #ic(levels)
        
        qualities = self.compute_PQRST_qualities()
        best_hb_ids = []
        for level in levels:
            candidates = {}
            for i in level:
                quality = qualities[i]#self.get_hb_quality(i)
                if quality is None:
                    quality = 0
                quality = int(quality*100) # in future quality coulld be 0-1
                if not quality in candidates:
                    candidates[quality] = []
                candidates[quality].append(i)

            for q in sorted(list(candidates.keys())):
                if best_n == 0:
                    return sorted(best_hb_ids)
                ids = candidates[q]
                if len(ids) > best_n:
                    random.shuffle(ids)
                    to_add = ids[:best_n]
                else:
                    to_add = ids
                
                best_hb_ids.extend(to_add)
                best_n -= len(to_add)
        return sorted(best_hb_ids)    

 

    def del_heartbeat(self, hb_index):
        for component in self.events.keys():
            self.events[component].pop(hb_index)

    def to_nan_heartbeats(self, ids, exceptions_components=[]):
        for hb_idx in ids:
            for component in self.events.keys():
                if component in exceptions_components:
                    continue
                self.events[component][hb_idx] = np.nan

    # to delete
    def to_nan_heartbeat(self, hb_index, exceptions_components=[]):
        for component in self.events.keys():
            if component in exceptions_components:
                continue
            self.events[component][hb_index] = np.nan

    def add_heartbeat(self, position_R):
        # get position heartbeat
        index_new_hb = 0

        if len(self.events['R']) > 0:
            # iteration from end to start
            # pos_R = 3.4
            # [0.1, 1.2, 2.2, 4.6, 7.8]
            for i in range(len(self.events['R'])-1, -1, -1):
                if position_R > self.events['R'][i]:
                    index_new_hb = i+1
                    break
                
        self.events['R'].insert(index_new_hb, position_R)
        
        step = 0.05
        # before R
        self.events['Q'].insert(index_new_hb, position_R-step*1)
        self.events['QRS_on'].insert(index_new_hb, position_R-step*2)
        self.events['P_off'].insert(index_new_hb, position_R-step*3)
        self.events['P'].insert(index_new_hb, position_R-step*4)
        self.events['P_on'].insert(index_new_hb, position_R-step*5)

        # after R
        self.events['S'].insert(index_new_hb, position_R+step*1)
        self.events['QRS_off'].insert(index_new_hb, position_R+step*2)
        self.events['T_on'].insert(index_new_hb, position_R+step*3)
        self.events['T'].insert(index_new_hb, position_R+step*4)
        self.events['T_off'].insert(index_new_hb, position_R+step*5)


    def check_heartbeat(self, heartbeat_index):
        order_comp = ['P_on', 'P', 'P_off',
                        'QRS_on', 'Q', 'R', 'S', 'QRS_off',
                        'T_on', 'T', 'T_off']
        
        wrong_order = []
        prev = -1
        for comp in order_comp:
            current = self.events[comp][heartbeat_index]
            if prev < current: # fail if current is np.nan
                # correct
                prev = current 
            else: # prev >= current or current == np.nan
                wrong_order.append(comp)
        return wrong_order


    def make_backup(self):
        self.backups_index = (self.backups_index + 1) % self.backups_size
        self.backups[self.backups_index] = copy.deepcopy(self.events)
    
    def restore_backup(self):
        backups = self.backups[self.backups_index]
        if backups is None:
            return
        self.events = backups
        self.backups_index = (self.backups_index - 1) % self.backups_size
