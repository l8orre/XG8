# -*- coding: utf-8 -*-
"""
 Copyright (c) 2014 l8orre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

 
from PyQt4 import  Qt ,  QtCore # QtGui,
from PyQt4.QtCore import  SIGNAL , QObject, pyqtSignal, pyqtSlot


 
class GateCtrl(QObject):
    """ Bridge Control - container and controller for useCase logic
        """
    
    
    def __init__(self, app ):
        super(QObject, self, ).__init__()
        
        self.app = app
        self.app.nxtGate = self
        # make this
        # Control1  known  in the app namespace.
        # When the Module controlled by this Ctrl throws sigs,
        # they can be recvd anywhere where this is known.
        self.time1 = 45000
        self.timer1 = Qt.QTimer()


    def init(self):  
        """ Here QT signals must be connected """  
        pass
        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.timer1_CB)


    def timer1_CB(self):
        pass #
        print("HERTBEAT nxtGateCtrl")
 
###########################
  
############################
############################        
############################
########## Window Maintenance

    def activate(self):
        self.init()
        #self.timer1.start(self.time1)

        # start the use cases here!
        #self.app.sessMan.uc_bridge.mm.jsonServ_Slot()


        
    def quitApp(self):
        print("QUITTING - not!?!?!")
        self.app.app.flush()
        self.app.app.emit(SIGNAL("aboutToQuit()") )
        self.app.app.exit(0)
        
        

 


 