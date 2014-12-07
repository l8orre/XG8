#!/usr/bin/python3
# -*- coding: utf-8 -*- 
"""
 Copyright (c) 2014 l8orre
 .

"""

import sys
import os
from PyQt4 import QtGui
 
#import nxtPwt
from nxtPwt.nxtSessionManager import nxtSessionManagerGate
from nxtPwt import nxtGateCtrl

#import argparse
#import configparser



class MainApplication:
    """  Win """
    
    def __init__(self, app, args): # = None):
        self.app = app
        self.args = args
        self.sessMan = nxtSessionManagerGate(app, args ) # self = app
        self.startGate()


    # these are controllers
    def startGate(self):
        """ This means that PowerTools can also be run WITHOUT windows!   """
        self.nxtGateCtrl = nxtGateCtrl.GateCtrl(self) # bridge is what the WinCtrl would be
        self.nxtGateCtrl.activate()# to have it more clean we could also activate the object timers here, not int the object inits themsilves

 


def main(argv):
    
    sys.path += [ os.path.dirname(os.path.dirname(os.path.realpath(__file__))) ]
    argv = sys.argv


    # todo : arg parse

    if len(argv) <2:
        argv.append('W')

    # make better arg parse here
    opsMode = argv[1]

    # ä ports
    #
    # 6876 NXT testN
    # 8876 NFD testN
    # main Net? hardcode for startesr

    app = QtGui.QApplication(sys.argv) # creation of the app object
    main = MainApplication(app, argv )
    
    main.startGate( )
    done = app.exec_()
    print(done )
    sys.exit(done)

        
if __name__ == "__main__":

    main(sys.argv)
    







