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

class EcgCanvas:
    def __init__(self, figure, axes):
        self.figure = figure
        self.axes = axes
        #
        self.vlines_y_limits = None
        self.text_bbox = None
        self.text_y_coords = None
        self._init_appearance()
        #
        self.lwidth = 1
        self.amplitude_ecg = 3#1.8
        self.time_ticks = 0.2
        self.line2D_ecg = None
        self._setup_grid()
        # 
        self.components_keys = list()
        self.lines_objs = dict()
        self.texts_objs = dict()
        #
        self.text_index_hb_objs = list()
        #



    def plot_ecg(self, ecg, sampling_rate, title_filepath='-'):
        self.figure.suptitle(title_filepath)
        seconds = len(ecg)/sampling_rate    
        step = 1.0/sampling_rate
        #
        x = np.arange(0, len(ecg)*step, step)
        y = ecg
        self.axes.set_xlim(0, seconds)

        if self.line2D_ecg is None:
            self.line2D_ecg, = self.axes.plot(x, y, linewidth=self.lwidth)
        else:
            self.line2D_ecg.set_data(x, y)
            self.line2D_ecg.set(visible=True)
        

    def to_nan_heartbeats(self, ids, exceptions_components=[]):
        for c in self.components_keys:
            if c in exceptions_components:
                continue
            for hb_idx in ids:
                self.set_PQRST_component(hb_idx, c, np.nan)

    def get_nearest_event(self, x, y):

        res = None

        near_diff = list()
        near_event = list()
        for component in self.components_keys:
            for i, text_obj in enumerate(self.texts_objs[component]):
                if not text_obj.get_visible():
                    continue
                
                xy = text_obj.xyann 
                x_text_data = xy[0]
                y_text_axis_percentage = xy[1]
                
                if np.abs(x-x_text_data) < 0.05:
                    #print(f"{x}_{x_text_data}")
                    line_obj = {'component': component, 'index': i}#data[component]['lines_objs'][i]
                    near_diff.append(np.abs(x-x_text_data))
                    near_event.append({
                                        'heartbeat_idx': i,
                                        'component': component,
                                        })
                    #print(f"{component}-{i}")
        
        if len(near_diff) > 0:
            idx = near_diff.index(min(near_diff))
            res = near_event[idx]
        return res
                                    

    def set_PQRST_component(self, heartbeat_idx, component, value, auto_hide_nan=True, auto_reshow_no_nan=True):
        if not component in self.components_keys:
            raise ValueError(f"`{component}` is not a valid PQRST component")

        was_nan = self.isnan_PQRST_component(heartbeat_idx, component)

        vline = self.lines_objs[component][heartbeat_idx]
        text = self.texts_objs[component][heartbeat_idx]

        #ic(text.xycoords)
        #
        x = value
        ymin = self.vlines_y_limits[component]['ymin']
        ymax = self.vlines_y_limits[component]['ymax']
        vline.set_data([x, x], [ymin, ymax])
        #
        text.set(x=x)
        #
        if was_nan and auto_reshow_no_nan:
            self.set_visibility_PQRST_component(heartbeat_idx, component, True)
        if np.isnan(value) and auto_hide_nan:
            self.set_visibility_PQRST_component(heartbeat_idx, component, False)

    # to delete
    def to_delete_move_PQRST_component(self, heartbeat_idx, component, value):
        if not component in self.components_keys:
            raise ValueError(f"`{component}` is not a valid PQRST component")
        

        vline = self.lines_objs[component][heartbeat_idx]
        text = self.texts_objs[component][heartbeat_idx]

        #ic(text.xycoords)
        #
        x = value
        ymin = self.vlines_y_limits[component]['ymin']
        ymax = self.vlines_y_limits[component]['ymax']
        vline.set_data([x, x], [ymin, ymax])
        #
        text.set(x=x)
        #

        if np.isnan(value):
            self.set_visibility_PQRST_component(heartbeat_idx, component, False)

    def isnan_PQRST_component(self, heartbeat_idx, component):
        if not component in self.components_keys:
            raise ValueError(f"{component} is not a valid PQRST component")
        
        text = self.texts_objs[component][heartbeat_idx]      
        # check if is nan
        xy = text.xyann 
        x_text_data = xy[0]
        y_text_axis_percentage = xy[1]
        #
        return np.isnan(x_text_data)


    

    def _set_visibility_PQRST_index(self, heartbeat_idx, visible, exceptions_components=[], keep_nan_to_false=True):
        for component in self.components_keys:       
            if component in exceptions_components:          
                continue 
            vline = self.lines_objs[component][heartbeat_idx]
            text = self.texts_objs[component][heartbeat_idx]
            #
            visible_to_set = visible
            if keep_nan_to_false:
                xy = text.xyann 
                x_text_data = xy[0]
                y_text_axis_percentage = xy[1]
                if np.isnan(x_text_data):
                    visible_to_set = False 
        
            vline.set_visible(visible_to_set)
            text.set_visible(visible_to_set)    
    
    def set_visibility_PQRST_index(self, heartbeat_idx, visible, other_hb_ids_visible=None):
        if other_hb_ids_visible is None:                                                                                                    
            self._set_visibility_PQRST_index(heartbeat_idx, visible)
        else:
            for idx in range(len(self.lines_objs['R'])):
                if idx == heartbeat_idx:
                    self._set_visibility_PQRST_index(idx, visible)
                else:
                    self._set_visibility_PQRST_index(idx, other_hb_ids_visible)


    def set_visibility_PQRST_component(self, heartbeat_idx, component, visible, keep_nan_to_false=True):
        if not component in self.components_keys:
            raise ValueError(f"{component} is not a valid PQRST component")

        vline = self.lines_objs[component][heartbeat_idx]                               
        text = self.texts_objs[component][heartbeat_idx]
        if keep_nan_to_false:
            xy = text.xyann 
            x_text_data = xy[0]
            y_text_axis_percentage = xy[1]
            if np.isnan(x_text_data):
                visible = False 
        #
        vline.set_visible(visible)
        text.set_visible(visible)


    def plot_PQRST(self, data):
        self._destroy_PQRST() # clean memory

        #ic(data.keys())
        tt = self.axes.get_xaxis_transform()
        for component in data.keys():
            #ic(component)
            self.components_keys.append(component)
            self.lines_objs[component] = list()
            self.texts_objs[component] = list()
            for i, v in enumerate(data[component]):
                if np.isnan(v):
                    visible = False
                else:
                    visible = True 
                color = self.text_bbox[component]['ec']
                vline = self.axes.axvline(v, **self.vlines_y_limits[component], 
                                            visible=visible, color=color)

                self.lines_objs[component].append(vline)
    
                y_text = self.text_y_coords[component]['y']
                text = self.axes.annotate(component, (v, y_text),  xycoords=tt, size=10,
                                            ha="center", va="top",
                                            bbox=dict(boxstyle="square",
                                                        **self.text_bbox[component]
                                                    #ec=(1., 0.5, 0.5),
                                                    #fc=(1., 0.8, 0.8),

                                                    ),
                                                    visible=visible
                                            )
                self.texts_objs[component].append(text)
                #
                if component == 'R':
                    text_index_hb = self.axes.annotate(str(i), (v, 0.09),  xycoords=tt, size=15,
                        ha="center", va="top",
                            bbox=dict(boxstyle="square",
                                # **text_bbox[component]
                                ec=(1., 0.5, 0.5),
                                fc=(1., 0.8, 0.8),
                            ),
                            visible=visible
                        )
                    self.text_index_hb_objs.append(text_index_hb)
        '''
        #
        #text = self.texts_objs['R'][0]
        #
        # The x-direction is in data coordinates and the y-direction is in axis coordinates.
        #t = self.axes.transData#.inverted()
        #tinv = ax1.transData 
        #xy = text.xyann 

        t = self.axes.transData.inverted()
        #t = self.axes.transAxes#get_xaxis_transform().inverted()
        #t = self.figure.transFigure
        #t = self.axes.transData
        #xy = text.xyann
        
        xy = [56, 251]
        ic(xy)

        r = t.transform(xy)#[0,0])#xy[0], xy[1]])
        ic(r)
        '''

    def clean_canvas(self):
        if self.line2D_ecg is None:
            return 
        
        self._destroy_PQRST()
        #
        x,y = np.nan, np.nan
        self.line2D_ecg.set_data(x, y)
        self.line2D_ecg.set(visible=False)
        self.figure.suptitle('-')


    def _destroy_PQRST(self):
        for comp in self.components_keys:
            for index in range(len(self.lines_objs[comp])):#len(data['R']['x_values'])):
                self.lines_objs[comp][index].remove()
                self.lines_objs[comp][index] = None
                #
                self.texts_objs[comp][index].remove()
                self.texts_objs[comp][index] = None

            self.lines_objs[comp] = list()
            self.texts_objs[comp] = list()

            
        for index in range(len(self.text_index_hb_objs)):#len(data['R']['x_values'])):
            self.text_index_hb_objs[index].remove()
            self.text_index_hb_objs[index] = None

        self.text_index_hb_objs = list()



    def _init_appearance(self):
        vlines_y_limits = { 
            'P_on': {
                'ymin': 0.2,
                'ymax': 0.6,
            #    'color':'k',
            }, 
            'P': {
                'ymin': 0.3,
                'ymax': 0.6,
            #    'color':'k',
            }, 
            'P_off': {
                'ymin': 0.2,
                'ymax': 0.6,
            #    'color':'k',
            }, 
            #
            'QRS_on': {
                'ymin': 0.2,
                'ymax': 0.7,
            #    'color':'g',
            }, 
            'Q': {
                'ymin': 0.3,
                'ymax': 0.8,
            #    'color':'g',
            }, 
            'R': {
                'ymin': 0.4,
                'ymax': 0.9,
            #    'color':'g',
            },
            'S': {
                'ymin': 0.3,
                'ymax': 0.8,
            #    'color':'g',
            }, 
            'QRS_off': {
                'ymin': 0.2,
                'ymax': 0.7,
            #    'color':'g',
            }, 
            #
            'T_on': {
                'ymin': 0.2,
                'ymax': 0.6,
            #    'color':'k',
            }, 
            'T': {
                'ymin': 0.3,
                'ymax': 0.7,
            #    'color':'k',
            },
            'T_off': {
                'ymin': 0.2,
                'ymax': 0.6,
            #    'color':'k',
            },
        }

        text_bbox = {
            'P_on': {
                'ec': (1., 0.5, 0),
                'fc': (1., 0.8, 0.6),
            },
            'P': {
                'ec': (1., 0.5, 0),
                'fc': (1., 0.8, 0.6),
            },
            'P_off': {
                'ec': (1., 0.5, 0),
                'fc': (1., 0.8, 0.6),
            },
            #
            'QRS_on': {
                'ec': (0.73, 0.2, 1),
                'fc': (0.84, 0.5, 1),
            },
            'Q': {
                'ec': (1., 0., 0.75),
                'fc': (1., 0.6, 0.93),
            },
            'R': {
                'ec': (1., 0., 0.75),
                'fc': (1., 0.6, 0.93),
            },
            'S': {
                'ec': (1., 0., 0.75),
                'fc': (1., 0.6, 0.93),
            },
            'QRS_off': {
                'ec': (0.73, 0.2, 1),
                'fc': (0.84, 0.5, 1),
            },
            #
            'T_on': {
                'ec': (1., 0.5, 0.5),
                'fc': (1., 0.8, 0.8),
            },
            'T': {
                'ec': (1., 0.5, 0.5),
                'fc': (1., 0.8, 0.8),
            },
            'T_off': {
                'ec': (1., 0.5, 0.5),
                'fc': (1., 0.8, 0.8),
            }, 
        }

        text_y_coords = {
            'P_on': {
                'y': vlines_y_limits['P_on']['ymin']
            },
            'P': {
                'y': vlines_y_limits['P']['ymin']
            },
            'P_off': {
                'y': vlines_y_limits['P_off']['ymin']
            },
            #
            'QRS_on': {
                'y': vlines_y_limits['QRS_on']['ymax']
            },
            'Q': {
                'y': vlines_y_limits['Q']['ymax']
            },
            'R': {
                'y': vlines_y_limits['R']['ymax']
            },
            'S': {
                'y': vlines_y_limits['S']['ymax']
            },
            'QRS_off': {
                'y': vlines_y_limits['QRS_off']['ymax']
            },
            #
            'T_on': {
                'y': vlines_y_limits['T_on']['ymin']
            },
            'T': {
                'y': vlines_y_limits['T']['ymin']
            },
            'T_off': {
                'y': vlines_y_limits['T_off']['ymin']
            },
        }
        self.vlines_y_limits = vlines_y_limits
        self.text_bbox = text_bbox
        self.text_y_coords = text_y_coords       


    def _setup_grid(self):
        # https://github.com/dy1901/ecg_plot/blob/master/ecg_plot/ecg_plot.py
        ax = self.axes

        secs = 10
        ax.set_xticks(np.arange(0,11,self.time_ticks))    
        ax.set_yticks(np.arange(-ceil(self.amplitude_ecg),ceil(self.amplitude_ecg),1.0))

        #ax.set_yticklabels([])
        #ax.set_xticklabels([])

        ax.minorticks_on()
        
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))

        ax.set_ylim(-self.amplitude_ecg, self.amplitude_ecg)
        ax.set_xlim(0, secs)

        c_major = (0.6, 0.6, 0.6)#'red'
        c_minor = (0.9, 0.9, 0.9)#(1, 0.7, 0.7)
        ax.grid(which='major', linestyle='-', linewidth='0.5', color=c_major)
        ax.grid(which='minor', linestyle='-', linewidth='0.5', color=c_minor)

