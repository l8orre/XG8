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
 

from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot

from PyQt4 import QtCore


import nxtPwt.nxtUseCases as nxtUseCases

#import nxtPwt.nxtUC_jsonrpc as nxtUC_jsonrpc


import nxtPwt.nxtModels as nxtMods
from nxtPwt.nxtApiSigs import nxtApi


#import sqlite3 as sq
import logging as lg

import nxtPwt.nxtDB as nxtDB


# Here we can do some control on whether or not to do testing 
#import nxtPwt.nxtTestCases as nxtTestCases





class nxtSessionManagerGate(QObject):
    """

session management.

container and brokering services for the useCases.

connection management.


  """

    changeConn_Sig = pyqtSignal( object ) # THIS WILL BECOME VERY IMPORTANT FOR PERCOLATIN ANALYSIS

    # these signals MUST be thrown by the sessMan, because the connects can only be done to singletons,
    # not to borg

    # the TX signals are thrown by the sessMan
    TX_status_Sig = pyqtSignal(object, object) # second must have some meta NUMBER OF CONFS REACHED!!!
    #
    TX_sendMoney_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_placeAskOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_cancelAskOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_sendMSG_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_minConfsReached_Sig = pyqtSignal(object, object)

    #TX_TEST_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal



    #
    #TX_receipt_Sig


    def __init__(self, app, args ):# app, self.lastSess
        """
        sessMan can do things himself.
        But most of the things are done in the UC instances which are clollected here.
        So this is a container object for useCases and models


# STOP IT!
# kill -9 `ps x | grep nxtGate.py | grep -v grep | awk '{print $1}'`

       """
        super(nxtSessionManagerGate, self).__init__()
        self.app = app
        self.app.sessMan = self #

        self.createLoggers() # the logging facilities are important for business case documentation

        nxtHost= 'localhost'
        nfdHost = 'localhost'
        testNet = True
        mainNet = False
        if testNet:
            nxtPort= '6876'
            nfdPort = '9876' # !! MAINNET!
        elif mainNet:
            nxtPort= '7876'
            nfdPort = '8876' # !! MAINNET!
        else:
            print("PORT ARG ERROR")

        nxt={'host': nxtHost, 'port':nxtPort}
        nfd={'host': nfdHost, 'port':nfdPort}
        # sessMan DOES get two API names! coz there are TWO api objects!

        self.nxtApi = nxtApi(self, self.apiLoggerNXT) # make the apiSigs instance here!
        self.nfdApi = nxtApi(self, self.apiLoggerNFD) # make the apiSigs instance here!
        #<nxtPwt.nxtApiSigs.nxtApi object at 0x7fdcc35349d8>
        #<nxtPwt.nxtApiSigs.nxtApi object at 0x7fdcc34c9948> TWO diff objects ok!

        self.connNXT = nxtMods.NRSconn(self, self.nxtApi, nxt, self.consLogger )
        self.connNFD = nxtMods.NRSconn(self, self.nfdApi, nfd, self.consLogger)

        self.nxtApi.initSignals(self.connNXT) # leapFrog init: account and NRSconn must be made before connecting their Sigs on nxtApi
        self.nfdApi.initSignals(self.connNFD) # leapFrog init: account and NRSconn must be made before connecting their Sigs on nxtApi

        self.uc31_xGateMain = nxtUseCases.UC31_xGateMain(self,  ) # self = nxtSessionManagerGate




    def createLoggers(self):
        # build the loggers:
        self.xGateLogger = lg.getLogger('xGateLogger')
        self.xGateLogger.setLevel(lg.INFO)
        fh=lg.FileHandler('xGate.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.xGateLogger.addHandler(fh)

        self.apiLoggerNFD = lg.getLogger('apiLogger')
        self.apiLoggerNFD.setLevel(lg.INFO) # INFO DEBUG
        aLhandler = lg.StreamHandler()
        aLhandler.setLevel(lg.INFO)      # INFO DEBUG
        after = lg.Formatter('\n%(asctime)s - %(message)s')
        aLhandler.setFormatter(after)
        self.apiLoggerNFD.addHandler(aLhandler)

        self.apiLoggerNXT = lg.getLogger('apiLogger')
        self.apiLoggerNXT.setLevel(lg.INFO) # INFO DEBUG
        aLhandler = lg.StreamHandler()
        aLhandler.setLevel(lg.INFO)      # INFO DEBUG
        after = lg.Formatter('\n%(asctime)s - %(message)s')
        aLhandler.setFormatter(after)
        self.apiLoggerNXT.addHandler(aLhandler)

        self.consLogger = lg.getLogger('consoleDebugger')
        self.consLogger.setLevel(lg.INFO)
        sh = lg.StreamHandler()
        sh.setLevel(lg.INFO)
        sfter = lg.Formatter('%(asctime)s - %(message)s')
        sh.setFormatter(sfter)
        self.consLogger.addHandler(sh)

        self.accNXTLogger = lg.getLogger('accNXTLogger')
        self.accNXTLogger.setLevel(lg.INFO)
        fh=lg.FileHandler('accNXT.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.accNXTLogger.addHandler(fh)

        self.accNFDLogger = lg.getLogger('accNFDLogger')
        self.accNFDLogger.setLevel(lg.INFO)
        fh=lg.FileHandler('accNFD.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.accNFDLogger.addHandler(fh)






class nxtSessionManagerBridge(QObject):
    """

session management.

container and brokering services for the useCases.

connection management.


  """


    def __init__(self, app, args ):
        """
        sessMan can do things himself.
        But most of the things are done in the UC instances which are clollected here.
        So this is a container object for useCases and models

       """
        super(nxtSessionManagerBridge, self).__init__()
        self.app = app
        self.app.sessMan = self #

        self.nxtApi = nxtApi(self) # make the apiSigs instance here!

        self.activeNRS = nxtMods.NRSconn(self)

        self.nxtApi.initSignals() # leapFrog init: account and NRSconn must be made before connecting their Sigs on nxtApi

        self.qPool=QtCore.QThreadPool.globalInstance()
        self.qPool.setMaxThreadCount(2500) # robustness

        if  args['walletDB_fName'] == None:
            args['walletDB_fName'] = "nxtGateDB.dat"

        walletDB_fName = args['walletDB_fName']

        print("args"+str(args))

        if args['blockChainHostPort'] == 'testNet':
            host = 'localhost'
            port = '6876'
        elif args['blockChainHostPort'] == 'mainNet':
            host = 'localhost'
            port = '7876'

        args['host'] = host
        args['port'] = port

        # build the loggers:
        self.bridgeLogger = lg.getLogger('bridgeLogger')
        self.bridgeLogger.setLevel(lg.INFO)
        fh=lg.FileHandler('bridge.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('\n%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.bridgeLogger.addHandler(fh)
        self.bridgeLogger.info('nxtBridge listening on %s:%s', host, port)

        self.walletLogger = lg.getLogger('walletLogger')
        self.walletLogger.setLevel(lg.INFO)
        fh=lg.FileHandler('wallet.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('\n%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.walletLogger.addHandler(fh)
        self.walletLogger.info('nxtwallet: %s',  walletDB_fName)
        #
        self.consLogger = lg.getLogger('consoleDebugger')
        self.consLogger.setLevel(lg.INFO)
        ch = lg.StreamHandler()
        ch.setLevel(lg.DEBUG)
        ch.setFormatter(fh)
        self.consLogger.addHandler(ch)

        self.walletDB_fName = walletDB_fName # filenmae


        self.walletDB = nxtDB.WalletDB_Handler(self, walletDB_fName,   self.walletLogger, self.consLogger, host, port )

        wallDB = {'walletDB' : self.walletDB}
        wallDB['walletDB_fName'] = walletDB_fName
                                                # self is sessMan!!
        self.uc_bridge = nxtUC_Bridge.UC_Bridge1(self,  host, port, self.bridgeLogger, self.consLogger, wallDB  )







class nxtSessionManager(QObject):
    """ 
    
session management. 

container and brokering services for the useCases. 

connection management.

  
  """

    changeConn_Sig = pyqtSignal( object )

    # these signlas MUST be thrown by the sessMan, because the connects can only be done to singletons,
    # not to bork

    # the TX signals are thrown by the sessMan
    TX_status_Sig = pyqtSignal(object, object) # second must have some meta
    #
    TX_sendMoney_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_issueAsset_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_placeAskOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_placeBidOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_cancelAskOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_cancelBidOrder_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_transferAsset_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_setAccountInfo_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_lease_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    #
    TX_sendMSG_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_assAlias_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_vote_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    TX_poll_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal
    #



    #TX_receipt_Sig
    # sessMan throws all these Signals with the different objects in them!
    # these Signals can only be connected when the identity is known



    def __init__(self, app, args ):# app, self.lastSess
        """
        sessMan can do things himself.
        But most of the things are done in the UC instances which are clollected here.
        So this is a container object for useCases and models

       """
        super(nxtSessionManager, self).__init__()
        self.app = app
        self.app.sessMan = self #
        
        opsMode = args['opsMode']

        self.nxtApi = nxtApi(self) # make the apiSigs instance here!
        self.activeNRS = nxtMods.NRSconn(self)
        self.nxtApi.initSignals() # leapFrog init: account and NRSconn must be made before connecting their Sigs on nxtApi

        self.logShort = True
        self.logLong = False

        self.uc1_pollNRS = nxtUseCases.UC1_pollNRS(self,  ) #
        self.uc2_accHndlr = nxtUseCases.UC2_accountHandler(self,   ) #
        self.uc3_TX_monitor = nxtUseCases.UC3_TX_monitor(self)
        self.uc4_sendMoney = nxtUseCases.UC4_sendMoney(self,  )#
        #todo self.uc4_setName = nxtUseCases.UC4_setName(self,  )#

        self.uc29_changeConn = nxtUseCases.UC29_changeConn(self,  ) #


        self.uc30 = nxtUseCases.nxtUC_apiAccess(self,   ) #
        self.uc30.initSignals()
#
# getAssetsByName is gone       self.uc5_AE = nxtUseCases.UC5_AE(self,  )#
        self.uc6_AO = nxtUseCases.UC6_AO(self,  )#
        self.uc7_ATX = nxtUseCases.UC7_ATX(self,  )#
        self.uc8_Trades = nxtUseCases.UC8_Trades(self,  )#

 
 
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
      
        
        
   
        
if __name__ == "__main__":
    import sys
    sys.path += [os.path.dirname(os.path.dirname(os.path.realpath(__file__))) ]
    argv = sys.argv
    app = QtGui.QApplication(sys.argv) # creation of the app object
    standAloneTest = "needs to be defined here"
    done = app.exec_()
    sys.exit(done)
 
 
 
  
  
  
  
  
