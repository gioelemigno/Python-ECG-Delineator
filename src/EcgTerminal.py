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
from EcgCalls import *


class EcgTerminal(Terminal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.gui = None 
        #self.datamanager = None
        self.ecg_calls = None
        #
        self.PROMPT = '> '
        
    def binding_ecg_calls(self, ecg_calls):
        self.ecg_calls = ecg_calls

    #def binding_GUI(self, gui):
    #    self.gui = gui

    def binding_Datamanager(self, datamanager):
        self.datamanager = datamanager

    def run_command(self, command, echo_command=False, prompt_after=True):
        if echo_command:
            self.write(command + '\n')
        
        self.register_command(command)

        args = self.preprocess_command(command)

        cmd = args[0]
  
        #
        if cmd in ['set']:
            #self.datamanager.make_backup()
            res = self.cmd_set(args)
        elif cmd in ['set_no_datamanager_update']:
            res = self.cmd_set_no_datamanager_update(args)
        elif cmd in ['load']:
            res = self.cmd_load(args)
        elif cmd in ['save']:
            res = self.cmd_save(args)
        #elif cmd in ['show', 'hide']:
        #    res = self.cmd_show_hide(args)
        elif cmd in ['add']:
            #self.datamanager.make_backup()
            res = self.cmd_add_heartbeat(args)
        elif cmd in ['del']:
            #self.datamanager.make_backup()
            res = self.cmd_del_heartbeat(args)
        elif cmd in ['nan']:
            #self.datamanager.make_backup()
            res = self.cmd_to_nan_heartbeat(args)
        elif cmd in ['check']:
            res = self.cmd_check_heartbeat(args)
        elif cmd in ['reload']:
            #self.datamanager.make_backup()
            res = self.cmd_reload(args)
        elif cmd in ['load_folder']:
            #self.datamanager.make_backup()
            res = self.cmd_load_folder(args)
        elif cmd in ['load_folder_next']:
            #self.datamanager.make_backup()
            res = self.cmd_load_folder_next(args)
        elif cmd in ['load_folder_prev']:
            res = self.cmd_load_folder_prev(args)
        elif cmd in ['load_folder_index']:
            res = self.cmd_load_folder_index(args)
        elif cmd in ['print']:
            #self.datamanager.make_backup()
            res = self.cmd_print(args)
        elif cmd in ['set_info']:
            #self.datamanager.make_backup()
            res = self.cmd_set_info(args)
        elif cmd in ['subplot_zoom_in']:
            #self.datamanager.make_backup()
            res = self.cmd_subplot_zoom_in(args)
        elif cmd in ['subplot_next_hb']:
            res = self.cmd_subplot_next_hb(args)
        elif cmd in ['subplot_prev_hb']:
            res = self.cmd_subplot_prev_hb(args)
        elif cmd == 'help':
            res = self.cmd_help(args)
        elif cmd in ['keep_best_hbs']:
            #self.datamanager.make_backup()
            res = self.cmd_keep_best_hbs(args)
        elif cmd in ['undo']:
            res = self.cmd_undo(args)
        elif cmd in ['restore_hb']:
            res = self.cmd_restore_heartbeat_from_file(args)
        elif cmd in ['to_only_R']:
            res = self.cmd_to_only_R_heartbeat(args)
        elif cmd == '':
            res = None
        elif cmd in ['set_no_nan_missings', 'set_nnan']:
            res = self.cmd_set_no_nan_missings(args)
        else:
            res = self.write("invalid command\n")
            #print(colored("invalid command", 'red'), flusg=True)
        
        
        if prompt_after:
            self.show_prompt()  
        return res
   


    def cmd_set_no_nan_missings(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'set_no_nan_missings',
                'examples': [
                    "set_no_nan_missings 4  // set no nan value to all nan components of hb_idx=4",                                                               
                ]
            }

        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 2:
            hb_idx = int(args[1])
            self.ecg_calls.set_no_nan_missings(hb_idx)
    
    
    def cmd_help(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'help',
                'examples': [
                    "help  // print all info about available commands",                                                               
                ]
            }

        if not len(args) in [1, 2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 1:
            to_print = ''
            attributes = dir(self)
            for attr in sorted(attributes):
                if len(attr) > 4 and attr[:4] == 'cmd_':
                    method = getattr(self, attr)
                    to_print += '-'*180 + '\n'
                    docs = method(None)
                    to_print += json.dumps(docs, indent=4) + '\n' 
                    to_print += '-'*180 + '\n'
            self.write(to_print)

        if len(args) == 2:
            name_command = args[1]
            to_print = "command no defined"
            attributes = dir(self)
            for attr in sorted(attributes):
                if len(attr) > 4 and attr[:4] == 'cmd_':
                    method = getattr(self, attr)
                    docs = method(None)
                    if docs['name'] == name_command:
                        to_print = '-'*180 + '\n'
                        to_print += json.dumps(docs, indent=4) + '\n' 
                        to_print += '-'*180 + '\n'
                        break
            self.write(to_print)





    def cmd_set(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'set',
                'examples': [
                        "set Q 3.4 1 // set Q component to 3.4 of the heartbeat 1",       
                    ]
            }
        if not len(args) in [4]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 4:
            # set Q 3.4 1
            component = args[1]
            value = float(args[2])
            heartbeat_idx = int(args[3])
            #
            ecg_canvas_ids='all'
            datamanager_update = True 

            self.ecg_calls.set_PQRST_component(heartbeat_idx, 
                                                component, 
                                                value, 
                                                ecg_canvas_ids=ecg_canvas_ids, 
                                                datamanager_update=datamanager_update)


    def cmd_set_no_datamanager_update(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'set_no_datamanager_update',
                'examples': [
                    "set_no_datamanager P_on 0.7 1  // datamaneger remains unchanged. set P_on component of beat 1 to 0.7 in all plots",                                                               
                    "set_no_datamanager P_on 0.7 1 0 // datamaneger remains unchanged. set P_on component of beat 1 to 0.7 only in plot 0",
                ]
            }

        if not len(args) in [4, 5]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 4:
            # set Q 3.4 1
            component = args[1]
            value = float(args[2])
            heartbeat_idx = int(args[3])
            #
            ecg_canvas_ids='all'
            datamanager_update = True 

            self.ecg_calls.set_PQRST_component(heartbeat_idx, 
                                                component, 
                                                value, 
                                                ecg_canvas_ids=ecg_canvas_ids, 
                                                datamanager_update=datamanager_update)

        elif len(args) == 5:
            # set Q 3.4 1 0
            component = args[1]
            value = float(args[2])
            heartbeat_idx = int(args[3])
            #
            ecg_canvas_ids=int(args[4])
            datamanager_update = False 

            self.ecg_calls.set_PQRST_component(heartbeat_idx, 
                                                component, 
                                                value, 
                                                ecg_canvas_ids=ecg_canvas_ids, 
                                                datamanager_update=datamanager_update)




    def cmd_subplot_zoom_in(self, args):
        # NOTE:
        # args[0] = command_name

        x1 = 0.4
        x2 = 0.5
        
        if args == None: # required documentation
            return {
                'name': 'subplot_zoom_in',
                'examples': [
                    f"subplot_zoom_in 2         // zoom in in beat 2 from R[2]-x1 to R[2]+x2 ({x1=}, {x2=} are default values)",
                    "subplot_zoom_in 0.2 0.5 2  // zoom in in beat 2 from R[2]-0.2 to R[2]+0.5 ",                                                                            
                ]
            }


        if not len(args) in [2, 4]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 2:
            hb_idx = int(args[1])
            self.ecg_calls.subplot_zoom_in(hb_idx, pre_R=x1, post_R=x2)

        if len(args) == 4:
            x1 = float(args[1])
            x2 = float(args[2])
            hb_idx = int(args[3])
            self.ecg_calls.subplot_zoom_in(hb_idx, pre_R=x1, post_R=x2)


    def cmd_subplot_next_hb(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'subplot_next_hb',
                'examples': [
                    "subplot_next_hb // move to the next non-nan peak",
                ]
            }

        if not len(args) in [1]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 1:
            return self.ecg_calls.subplot_zoom_in_next_hb()

    def cmd_keep_best_hbs(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'keep_best_hbs',
                'examples': [
                        "keep_best_hbs 5  // keeps the best 5 heartbeats. The other heartbeats are set to nan, expect the R peaks",       
                    ]
            }

        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 2:
            n_best = int(args[1])
            self.ecg_calls.keep_best_heartbeats(n_best)


    def cmd_subplot_prev_hb(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'subplot_prev_hb',
                'examples': [
                        "subplot_prev_hb // move to the next non-nan peak",       
                    ]
            }

        if not len(args) in [1]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return   

        if len(args) == 1:
            return self.ecg_calls.subplot_zoom_in_prev_hb()



    def cmd_load(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'load',
                'examples': [
                        "load ./ecg_file.json // load the file ./ecg_file.json",       
                    ]
            }

        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            # load ./ecg_file.json
            filepath = args[1]
            self.ecg_calls.load_file(filepath)

            

    def cmd_save(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'save',
                'examples': [
                        "save ./ecg_out.json // save the changes on the current open file on another file called ./ecg_out.json",       
                    ]
            }      
        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            # save ./ecg_out.json
            filepath = args[1]
            self.ecg_calls.save_on_file(filepath)

    
            
    def cmd_add_heartbeat(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'add',
                'examples': [
                        "add 0.5 //add heartbeat with R peak at t=0.5s"
                    ],
                'warnings': [
                    "This command changes the mapping heartbeat <-> index, so automatically readraw canvas from scratch"
                ]
            }   
 
        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            position_R_peak = float(args[1])
            self.ecg_calls.add_heartbeat(position_R_peak)

    def cmd_del_heartbeat(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'del',
                'examples': [
                        "del 1 //delete heartbeat at index 1",
                    ],
                'warnings': [
                    "This command changes the mapping heartbeat <-> index, so automatically readraw canvas from scratch"
                ]
            }   

        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            hb_index = int(args[1])
            self.ecg_calls.del_heartbeat(hb_index)

    def cmd_to_nan_heartbeat(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'nan',
                'examples': [
                    "nan 1          //set to nan heartbeat at index 1 (i.e. all component of heartbeat 1",
                    "nan [0,1,6]    //set to nan heartbeat at indexes 0, 1, 6",
                ],
                'warnings': [
                    "This command automatically readraw canvas from scratch"
                ]
            }   


        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            if '[' in args[1] and ']' in args[1]: # nan [0,1,6]
                ids = args[1].strip()[1:-1].split(',')
                ids = [int(idx.strip()) for idx in ids]
                #for idx in ids:
                #    hb_index = int(idx.strip())
                #    self.datamanager.to_nan_heartbeat(hb_index)                  
            else: # nan 1 
                hb_index = int(args[1])
                #self.datamanager.to_nan_heartbeat(hb_index)
                ids = [hb_index]
        
            self.ecg_calls.to_nan_heartbeats(ids, exceptions_components=[])

    def cmd_to_only_R_heartbeat(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'to_only_R',
                'examples': [
                    "to_only_R 1          //set to nan heartbeat at index 1 expect R (i.e. all component of heartbeat 1",
                    "to_only_R [0,1,6]    //set to nan heartbeat at indexes 0, 1, 6 expect R", 
                ],
                'warnings': [
                    "This command automatically readraw canvas from scratch"
                ]
            }   


        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    
        
        if len(args) == 2:
            if '[' in args[1] and ']' in args[1]: # nan [0,1,6]
                ids = args[1].strip()[1:-1].split(',')
                ids = [int(idx.strip()) for idx in ids]
                #for idx in ids:
                #    hb_index = int(idx.strip())
                #    self.datamanager.to_nan_heartbeat(hb_index)                  
            else: # nan 1 
                hb_index = int(args[1])
                #self.datamanager.to_nan_heartbeat(hb_index)
                ids = [hb_index]
        
            self.ecg_calls.to_only_R(ids)




    def cmd_check_heartbeat(self, args):
        # NOTE:
        # args[0] = command_name
        if args == None: # required documentation
            return {
                'name': 'check',
                'examples': [
                    "check 1            //check order in heartbeat at index 1",
                    "check [0,1,6]      //check order in heartbeat at indexes 0, 1, 6",
                    "check all          // check all heartbeats",                
                ],
            }   
  
        if not len(args) in [2]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 2:
            if '[' in args[1] and ']' in args[1]: # check [0,1,6]
                ids = args[1].strip()[1:-1].split(',')
                ids = [int(i) for i in ids]
            else: # check 1 or check all
                if args[1] == 'all':
                    ids = 'all'                        
                else: 
                    ids = [int(args[1])]

            res = self.ecg_calls.check_heartbeats(ids)
            for idx in res.keys():
                if len(res[idx]) > 0:
                    to_print = f"Heartbeat at index {idx} not ordered: \n\t{res[idx]=}\n"             
                else:
                    to_print = f"Heartbeat at index {idx} ORDERED\n"
                self.write(to_print)   
            return res

    def cmd_reload(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'del',
                'examples': [
                    "reload            //reload data_loaded"
                ],
                'warnings': [
                    "This command automatically readraw canvas from scratch"
                ]
            }     

        if not len(args) in [1]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 1:
            self.ecg_calls.reload_data()



    def cmd_undo(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'undo',
                'examples': [
                    "undo            //undo last command",
                ],
                'warnings': [
                    "This command automatically readraw canvas from scratch",
                    "It could not work with some commands"
                ]
            }    


        if not len(args) in [1]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 1:
            self.ecg_calls.undo()
 


    def cmd_load_folder(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'load_folder',
                'examples': [
                    "load_folder  ./ecg_in ./ecg_out      //load the first folder as ecg source, load the second as destination for changes",
                ],
            } 

     
        if not len(args) in [3]:
            self.write("Invalid input")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 3:
            folder_in = args[1].strip()
            folder_out = args[2].strip()
            #
            self.ecg_calls.load_folder(folder_in, folder_out)
 

    def cmd_load_folder_next(self, args):
        # NOTE:
        # args[0] = command_name
    
        if args == None: # required documentation
            return {
                'name': 'load_folder_next',
                'examples': [
                    "load_folder_next      //load next file in folder_in",                
                    ],
                'warnings': [
                    "This command can be executed only after `load_folder",
                ]
            }
         
        if not len(args) in [1]:
            self.write("Invalid input\n")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 1:
            self.ecg_calls.load_folder_next()

    def cmd_load_folder_prev(self, args):
        # NOTE:
        # args[0] = command_name
    
        if args == None: # required documentation
            return {
                'name': 'load_folder_prev',
                'examples': [
                    "load_folder_prev      //load prev file in folder_in",                
                    ],
                'warnings': [
                    "This command can be executed only after `load_folder",
                ]
            }
         
        if not len(args) in [1]:
            self.write("Invalid input\n")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 1:
            self.ecg_calls.load_folder_prev()

    def cmd_load_folder_index(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'load_folder_index',
                'examples': [
                   "load_folder_index 32      // load the 32th file from `folder_in`",                ],
            }
   
        if not len(args) in [2]:
            self.write("Invalid input\n")
            return    

        if len(args) == 2: 
            idx = int(args[1])
            return self.ecg_calls.load_folder_index(idx)

    def cmd_print(self, args):
        # NOTE:
        # args[0] = command_name

        if args == None: # required documentation
            return {
                'name': 'print',
                'examples': [
                   "print info      //print `info` field of dataloader",                ],
            }
   
        if not len(args) in [2]:
            self.write("Invalid input\n")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 2:
            if args[1] == 'info':
                info = self.ecg_calls.get_info()
                to_print = '-'*180 + '\n'
                to_print += json.dumps(info, indent=4) + '\n' 
                to_print += '-'*180 + '\n'
                self.write(to_print)
            elif self.ecg_calls.is_valid_component(args[1]):
                info = self.ecg_calls.get_printable_component_values(args[1])
                to_print = '-'*180 + '\n'
                to_print += info + '\n' 
                to_print += '-'*180 + '\n'
                self.write(to_print)
            elif args[1].isdigit():
                hb_idx = int(args[1])
                info = self.ecg_calls.get_printable_hb_idx_values(hb_idx)
                to_print = '-'*180 + '\n'
                to_print += info + '\n' 
                to_print += '-'*180 + '\n'
                self.write(to_print)
            else:
                self.write("unknown\n")

    def cmd_set_info(self, args):
        # NOTE:
        # args[0] = command_name
    
        if args == None: # required documentation
            return {
                'name': 'set_info',
                'examples': [
                    "set_info is_inverted false      // set field `info.is_inverted` of datamanager to `false`",                ],
            }

        if not len(args) in [3]:
            self.write("Invalid input\n")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 3:
            attr = args[1]
            value = args[2]
            if not attr in ['is_inverted']:
                self.write(f"info.{attr} cannot be modified\n") 
                return 
            
            if value.lower() in ['false', 'true']:
                value = value.lower() == 'true'
        
            self.ecg_calls.set_info(attr, value)


    def cmd_restore_heartbeat_from_file(self, args):
        # NOTE:
        # args[0] = command_name
    
        if args == None: # required documentation
            return {
                'name': 'restore_hb',
                'examples': [
                    "restore_hb 5      // restore PQRST of heartbeat 5 from file",
                ],
            }

        if not len(args) in [2]:
            self.write("Invalid input\n")
            #print(colored("Invalid input", "red"), flush=True)
            return    

        if len(args) == 2:
            hb_idx = int(args[1])
            self.ecg_calls.restore_heartbeat_from_file(hb_idx)
