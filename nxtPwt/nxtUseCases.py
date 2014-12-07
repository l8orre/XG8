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

 
from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot, SIGNAL, QTimer
import time
import binascii as binas
from copy import copy
from nxtPwt.nxtApiPrototypes import nxtQs
import nxtPwt.nxtModels as nxtMods
#import numpy as np
import logging as lg
from PyQt4.QtGui import QSortFilterProxyModel



class nxtUseCaseMeta(QObject):
    """ This is an abstract meta class that has elemtary sigs and methods defined.
    All use case classes inherit from this, so they know all the signals for emission
    The useCaseClass is tho ONLY one that talks to the api.    

     """
    
    apiCalls = nxtQs() # static! dict of prototypes to be filled with vals for apiReq
    #blinkerCols = [Qt.Qt.darkYellow, Qt.Qt.magenta]
   
   
    
    def __init__(self,  sessMan  ): # 
        """ just call the super init here: QObject.
       """        
        super(nxtUseCaseMeta, self).__init__()
        self.nxtApi = sessMan.nxtApi  # there is only ONE apiSigs instance, and that is in the sessMan.


    
class nxtUC_apiAccess(nxtUseCaseMeta): # this is old style. leave as it is for now - legacy API access
    """ 
    old style - useful legacy
  connect the buttons on Win7 to the reqPrepareCBs on win7, then have that prepared apiReq sent here to the api,
  connect the replies ALL to one catcher that hands them back to win7.
    """
   
    def __init__(self, sessMan,   ):
        super(nxtUC_apiAccess   , self   ).__init__(sessMan)
        self.apiCalls = nxtQs()
        #self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {}
        
    def initWin7(self, nxtWin7, ui7 ):
        """ - these are the activators FROM the widgets""" 
        self.nxtWin7 = nxtWin7
        self.ui7 = ui7
        QObject.connect(self.nxtWin7, SIGNAL("UC30_apiAcc(PyQt_PyObject)"),  self.execUC30_CB) # catch the activator from app.
  
    def initSignals(self,):    
        """   returning FROM the api   """
         # same CB here to return to the widget.
        QObject.connect( self.nxtApi, SIGNAL("catchAll_Sig(PyQt_PyObject, PyQt_PyObject)"), self.catchAll_fromApiSlot ) # all of them
        QObject.connect( self.nxtApi, SIGNAL("queryURL_Sig(PyQt_PyObject)"), self.catchQ ) # all of them
          
    def execUC30_CB(self, apiReq): # hit the apiBroker with these two requests: self.nxtApi,
        self.nxtApi.catchAll_Slot( apiReq, self.meta)


    @pyqtSlot( ) #  
    def catchQ(self, query): #queryURL_Sig
        try:
            self.ui7.lineEdit1_nxtFullQ.setText(query)
        except Exception as inst:
            pass #print(str(inst) + "-? seems no probelm! ---")

    @pyqtSlot( ) # catch reply from api and do s.t. with it
    def catchAll_fromApiSlot(self, reply, meta):
        #print("caught reply back from api: " + str(reply))
        try:
            for key in reply:
                self.ui7.textEdit_NRSRaw1.append( str(key) + " - " + str(reply[key]))

        except Exception as inst:
            pass #print(str(inst))
            #print("nxtWin7 not active")


class UC1_pollNRS(nxtUseCaseMeta):
    """ ___ use case architecture update  """

    def __init__(self, sessMan,   ):
        super(UC1_pollNRS   , self   ).__init__(sessMan)

        #self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'uc1'}

        # activate Timers on nxtModels
        # this is for ONE single nrs
        #self.sessMan.activeNRS.poll1Start(self.meta)
        #self.sessMan.activeNRS.state.poll1Start(self.meta)
        #  so here we use several instances
        self.sessMan.connNXT.poll1Start(self.meta)
        self.sessMan.connNXT.state.poll1Start(self.meta)
        self.sessMan.connNFD.poll1Start(self.meta)
        self.sessMan.connNFD.state.poll1Start(self.meta)






    # STOP IT!
    # kill -9 `ps x | grep nxtGate.py | grep -v grep | awk '{print $1}'`




class UC31_xGateMain(nxtUseCaseMeta): # ONE only

    changeResident_Sig = pyqtSignal(object, object)


    def __init__(self, sessMan, ): # sessMan = nxtSessionManagerGate!!
        super(UC31_xGateMain, self   ).__init__(sessMan)

        self.sessMan = sessMan
        # the UCs are kept in the DB with the orderID of the initial BIDorder as key coz that is unique
        
        self.connNXT = self.sessMan.connNXT
        self.connNFD = self.sessMan.connNFD
        self.meta = {'started_by_controller':'UC31'}
        self.connNXT.state.poll1Start(self.meta)
        self.connNFD.state.poll1Start(self.meta)


        # amount of NXT in exitence
        # 999,996,977
        # 5,000,000,000 NFD

        # 999,996,977
        # qty NXT 99999697700000000 decimals 8
        # qty NFD 500000000000000000 decs 8


        # prepare data for accounts
        # can wrap this neater later! 14576994730285238779   # nxt on nfd  7334941058708816895
        self.nxt_tkn_on_nfd_AE = '7334941058708816895'
        self.nfd_tkn_on_nxt_AE =   '6477891914279744979' # xgnfd3 is current testNet   '14576994730285238779'  #'7476479172898689702' # 6477891914279744979

        self.xGateAccNumNFD = '16159101027034403504'
        self.xGateAccNumNXT = '2865886802744497404'
        self.xGateAccSecNFD = '17oreosetc17oreosetc'
        self.xGateAccSecNXT = '14oreosetc14oreosetc'

        # below is what the ACCOUNT instances need:
        xGate_NXT_IDs = ('NXT','NFD', \
                         self.nfd_tkn_on_nxt_AE, \
                         self.xGateAccNumNXT,\
                         self.xGateAccSecNXT, \
                         self.sessMan.accNXTLogger  )
        xGate_NFD_IDs = ('NFD','NXT', \
                         self.nxt_tkn_on_nfd_AE , \
                         self.xGateAccNumNFD , \
                         self.xGateAccSecNFD, \
                         self.sessMan.accNFDLogger ) # the loggers are created in sessMan

        self.acctNFD = nxtMods.XGAccount(sessMan, xGate_NFD_IDs)
        self.acctNXT = nxtMods.XGAccount(sessMan, xGate_NXT_IDs )

        self.acctNFD.poll1Start()
        self.acctNXT.poll1Start()

        self.allowedXferPrefixes = ['NXT','NFD','can','CAN','Can']
        self.launchSchedule = [] # this is to prevent putting mult orders into NRS in one second
        self.uc32LaunchTimer1 = QTimer()
        time.sleep(0.01) # wait for init api calls
        self.uc32_dictDB = {}
        self.blacklist = [] #for bad clients
        self.init_Sigs()


    def init_Sigs(self):
        """ UseCases do not receive Signals from the api directly. Models talk to the api, nut UseCases """
        QObject.connect(self.uc32LaunchTimer1, SIGNAL("timeout()"),  self.launchUC32) # to not dump them into NRS in the same second
        QObject.connect(self.acctNXT, SIGNAL("checkBidOrders_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkBidOrders_CB)
        QObject.connect(self.acctNFD, SIGNAL("checkBidOrders_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkBidOrders_CB)

        QObject.connect(self.acctNXT, SIGNAL("checkXfers_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkXfers_CB)
        QObject.connect(self.acctNFD, SIGNAL("checkXfers_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkXfers_CB)

        #QObject.connect(self.acctNXT, SIGNAL("checkMSGs_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkMSGs_CB)
        #QObject.connect(self.acctNFD, SIGNAL("checkMSGs_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkMSGs_CB)

        QObject.connect(self.acctNXT, SIGNAL("checkTrades_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkTrades_CB)
        QObject.connect(self.acctNFD, SIGNAL("checkTrades_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkTrades_CB)



    def checkBidOrders_CB(self, bidOrders, meta):
        """ step 1 - new uc32        """
        self.sessMan.consLogger.info('UC31 checks BidOrders: %s', str(bidOrders) )
        self.sessMan.xGateLogger.info('UC31 all current UC32s: %s', str(self.uc32_dictDB.keys()) )


        for BO in bidOrders['bidOrders']: # WILL THROW EXCEPT IF THERE NOT ANY !!! CATCH!!
            # ToDo: check for MINCONFS here!!!!!
            # difficult: getBidOrders - does not contain CONFS! would have to getTX here!

            # this is to start only once for eacxh bidorder
            if BO['order'] in self.uc32_dictDB.keys(): # <---- consult uc32_dictDB
                continue

            # this is to start only once for eacxh bidorder
            # if we dont do this a multifill will trigger fake askOrderOthers others ie start an uc32 which is not really one!
            for  UCid in self.uc32_dictDB:
                checkThisUC32 = self.uc32_dictDB[UCid]
                if BO['order'] in checkThisUC32.bidOrdersLiOther: # = self.uc32_dictDB[UCid]
                    continue
                 #self.bidOrdersLiOther.append(BOID)


            BOblockHeight = BO['height']
            if meta['xGateSide'] == 'NFD':
                currNumBlocks = int(self.acctNFD.connNxx.state.data['numberOfBlocks'])
                if (currNumBlocks - BOblockHeight) < 0:
                    continue
            elif meta['xGateSide'] == 'NXT':
                currNumBlocks = int(self.acctNXT.connNxx.state.data['numberOfBlocks'])
                if (currNumBlocks - BOblockHeight) < 0:
                    continue

            self.launchSchedule.append( (BO, meta) ) # append to right: list of uc32 launches
            print(5*"\n++++++> setting launchSched", str(time.time() ) , str(self.launchSchedule))

            self.uc32LaunchTimer1.start(1500)


    def launchUC32(self):
        """ step 2 - new uc32        """
        print(5*"\n----> launch schedule UC32s: ", str(time.time()), str(self.launchSchedule))
        # ToDo verify correctntness
        BO = self.launchSchedule[0][0]
        meta = self.launchSchedule[0][1]



        self.createNewUC32(BO, meta)
        self.launchSchedule.pop(0) # the first is launched, delete from left
        if len(self.launchSchedule) == 0:
            #print(5*"\n++++++> all launched stop launch sched.", str(time.time()))
            self.uc32LaunchTimer1.stop()


    def createNewUC32(self,bidOrder, meta ):
        """ step 3 - new uc32        """




        self.sessMan.xGateLogger.info('-2-->UC31 bidOrder: new UC32 %s\n', str(bidOrder))
        loggerName = './ucLogs/uc32Logger_' + bidOrder['order'] + '.log'
        uc32Logger = lg.getLogger(loggerName)
        uc32Logger.setLevel(lg.INFO)
        fh=lg.FileHandler(loggerName)
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('\n%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        uc32Logger.addHandler(fh)
        logger = copy(uc32Logger)
        newUC32 = UC32_xGate(self.sessMan, bidOrder, meta, logger )
        # good: uc32_dictDB is:
        ###############'{'16168413129237952656': <nxtPwt.nxtUseCases.UC32_xGateClient object at 0x7fdb3c573f78>, '47072525900290581': <nxtPwt.nxtUseCases.UC32_xGateClient object at 0x7fdb3c573dc8>}
        self.uc32_dictDB[bidOrder['order']] =  newUC32

        prepLogger=''
        for k in newUC32.__dict__:
            prepLogger += (k + " : " + str(newUC32.__dict__[k]) +"\n" )

        newUC32.uc32Logger.info('startUC32: %s \n ', prepLogger)
        # a fresh logger for each UC32



    # check Trades is easy, it is a one-to-one action
    def checkTrades_CB(self, trades, meta):
        #self.sessMan.consLogger.info('UC31 checks Trades----\n%s', str(trades) )

        #self.sessMan.xGateLogger.info('UC31 checkTrades_CB    - %s \nmeta: %s ' , str(trades ), str(meta) )

        popList=[]
        for UCid in self.uc32_dictDB: # <---- consult uc32_dictDB
            checkThisUC32 = self.uc32_dictDB[UCid]

            self.sessMan.consLogger.info('UC31 is checkTrades_CB  uc32 status:::::::::::  %s ', str(checkThisUC32.status))


            # here we will make the chcks if to CLOSE!


            if checkThisUC32.status == 'finalizeThisUC32':
                self.sessMan.xGateLogger.info('UC31 closes UC32  - %s \n  %s ' , str(checkThisUC32.__dict__), str(self.__dict__) )



                prepLogger = '\n#################### CLOSE uc32:\n'
                for k in checkThisUC32.__dict__:
                    prepLogger+= ( "\n"+str(k)+' : '+str(checkThisUC32.__dict__[k]))
                checkThisUC32.uc32Logger.info(prepLogger)
                try:

                    clientDataThis=''
                    for client in checkThisUC32.clientThisDi:

                        clientDataThis += str(checkThisUC32.clientThisDi[client])
                        clientDataThis += str(checkThisUC32.clientThisDi[client].__dict__)

                    checkThisUC32.uc32Logger.info('clientDataThis----------------------\n %s ', clientDataThis )

                    clientDataOther=''
                    for client in checkThisUC32.clientsOtherDi:
                        clientDataOther += str(checkThisUC32.clientsOtherDi[client])
                        clientDataOther += str(checkThisUC32.clientsOtherDi[client].__dict__)

                    self.accountThis.accLogger.info('fees %s NQT to %s uc32_ID %s',   str(checkThisUC32.feeThis)  )
                    self.accountOther.accLogger.info('fees %s NQT to %s uc32_ID %s',   str(checkThisUC32.feeOther)  )

                    checkThisUC32.uc32Logger.info('clientDataOther----------------------\n %s \n+++++++++++++++closed.', clientDataOther )
                    checkThisUC32.uc32Logger.info('fees collected*********************\n%s\n%s\n*********************', str(checkThisUC32.feeOther), str(checkThisUC32.feeThis) )
                    checkThisUC32.sessMan.xGateLogger.info('feesCollected**%s*%s*********************', str(checkThisUC32.feeOther), str(checkThisUC32.feeThis) )

                except Exception as inst:
                    checkThisUC32.uc32Logger.info('logger except- FIXME! %s \n\n %s', str(inst), str(self.__dict__))

                popList.append(checkThisUC32.ucID)
                continue


            for trade in trades['trades']: # for this check TRADES are sorted by ASKORDER; because tat is not unique, but unique for the side

                try:
                    if  checkThisUC32.askOrderThis['askOrderId'] == trade['askOrder']:  # this is auto at init
                        checkThisUC32.trade_This(trade) # this is to trigger placeAskOrderOther

                    elif checkThisUC32.askOrderOther['askOrderId'] == trade['askOrder']: # these can be multiple trades
                        checkThisUC32.trade_Other(trade) # this is for accounting! make accounting for redemtpion for both sides and send messages

                except Exception as inst:
                     self.sessMan.consLogger.info("trades checking error finished. %s %s", str(trades), str(inst))


        for pop in popList:
            self.uc32_dictDB.pop(pop) # or this: RuntimeError: dictionary changed size during iteration
            del pop # to also delete loggers etc




    def checkXfers_CB(self, Xfer, meta): # LATER; WE CAN STILL ONLY PASS NEWEST XFERS FROM THE ACCT TO HERE!




# "attachment": {
#         "message": "testMESSAGEXFER",
#         "version.Message": 1,
#         "asset": "7334941058708816895",
#         "quantityQNT": "13",
#         "version.AssetTransfer": 1,
#         "messageIsText": true
#     },



        XferSender = Xfer['sender']
        for UCid in self.uc32_dictDB: # <---- consult uc32_dictDB
            checkThisUC32 = self.uc32_dictDB[UCid]

            #self.sessMan.consLogger.info('UC31 checks Xfers:  - %s   %s ' , str( checkThisUC32.clientsOtherDi.keys() ) , str(Xfer['sender'])  )
            XferAtt = Xfer['attachment']

            if 'message' not in XferAtt.keys():

                prepLogger=''
                for k in checkThisUC32.__dict__:
                    prepLogger += (k + " : " + str(checkThisUC32.__dict__[k]) )

                checkThisUC32.uc32Logger.info('XFER ERROR! : %s \n ', (prepLogger+"\n Xfer was:"+ str(Xfer)))
                continue


            try:

                #    acctOtherSendCoinsTo = XferAtt['comment'] # target acct number
                acctOtherSendCoinsTo = XferAtt['message'] # target acct number

                if acctOtherSendCoinsTo[0:3] not in self.allowedXferPrefixes:

                    prepLogger=''
                    for k in checkThisUC32.__dict__:
                        prepLogger += (k + " : " + str(checkThisUC32.__dict__[k]) )

                    checkThisUC32.uc32Logger.info('XFER ERROR! : %s \n ', (prepLogger+"\n Xfer was:"+ str(Xfer)))
                    continue
            except:

                    prepLogger=''
                    for k in checkThisUC32.__dict__:
                        prepLogger += (k + " : " + str(checkThisUC32.__dict__[k]) )

                    checkThisUC32.uc32Logger.info('XFER ERROR! : %s \n ', (prepLogger+"\n Xfer was:"+ str(Xfer) ))

            #if XferAtt['comment'][:6] in checkThisUC32.cancelSyntax: # COMMENT CANCEL !!!!!!
            if XferAtt['message'][:6] in checkThisUC32.cancelSyntax: # COMMENT CANCEL !!!!!!

                checkThisUC32.uc32Logger.info("\nRedeemByCancel: ucID %s", str(checkThisUC32.ucID))
                # howto: set the hash to XFERS so we dont do this again!
                checkThisUC32.redeemByCancelThis(Xfer)
                continue

            #if checkThisUC32.otherSide == XferAtt['comment'][0:3] : #  other == NFD , comment == NFD : --> redeemTHIS          whichSide is NFD and NXT?
            if checkThisUC32.otherSide == XferAtt['message'][0:3] : #  other == NFD , comment == NFD : --> redeemTHIS          whichSide is NFD and NXT?



                if checkThisUC32.clientThisAccId == XferSender:
                    #self.sessMan.consLogger.info('\n\n\n++++checkThisUC32.clientThisAccId == XferSender  - %s ==  %s ' , str(checkThisUC32.clientThisAccId)  , str(Xfer['sender'])  )


                    #Xfer['sender']: xfer is selected as being THIS or OTHER by SENDER!!!! this can lead to confusion!
                    # if the SAME sender acct tries to appear on BOTH sides, we get confusion! DO NOT DO THIS!
                    # USER INSTRUCTIONS!

                    try:
                        if  int(Xfer['timestamp'])  < checkThisUC32.UC32_iniTimeThis: ##
                            continue
                    except Exception as inst:
                        self.sessMan.consLogger.info('UC31 timestamp ERROR ignore this Xfer %s ' , str(inst))
                        continue
                    checkThisUC32.redeemTokenThis(Xfer)
                    continue


            #if checkThisUC32.thisSide == XferAtt['comment'][0:3] : #         this == NFD , comment == NFD : --> redeemOTHER
            if checkThisUC32.thisSide == XferAtt['message'][0:3] : #         this == NFD , comment == NFD : --> redeemOTHER

                if XferSender in checkThisUC32.clientsOtherDi.keys():
                    # must introduce timestamp check here. no prob.
                    # NOT ENOUGH! ALSO SENDS OLD XFERS THAT ARE NO LONGER RELEVANT!
                    try:
                        if  int(Xfer['timestamp'])  < checkThisUC32.UC32_iniTimeOther: ##
                            continue
                    except Exception as inst:
                        self.sessMan.consLogger.info('UC31 timestamp ERROR ignore this Xfer %s ' , str(inst))
                        continue
                    checkThisUC32.redeemTokenOther(Xfer)
                    continue




# SUBCLASS UC32_xGate to catch small volumes we do not want to accept for full UseCases

#
#    def trade_This(self, trade):

# change the trade_this Implementation in the end and DON't go placeOrderOther',
# buzt simply shut down the UC here with a special comment!







class UC32_xGate(nxtUseCaseMeta): # for each business case
    """2014-07-21 19:20:34,480 - NEW UC32.__dict__

"""
    changeResident_Sig = pyqtSignal(object, object)

    def __init__(self, sessMan, bidOrderThis, meta , logger ):
        super(UC32_xGate, self   ).__init__(sessMan, )

        self.sessMan=sessMan

        self.uc32Logger = logger

        self.uc32Logger.info('NEW \none only?!\n\n UC32 bidOrder: new UC %s', str(bidOrderThis))

        if meta['xGateSide'] == 'NFD':
            self.UCtype = 'NXT_on_NFD' #  ='7334941058708816895'  xGassetID
            self.accountThis = sessMan.uc31_xGateMain.acctNFD
            self.accountOther = sessMan.uc31_xGateMain.acctNXT
            self.tokenThis = self.accountThis.xGassetID
            self.tokenOther = self.accountOther.xGassetID
            self.thisSide = 'NFD'
            self.otherSide = 'NXT'

        elif meta['xGateSide'] == 'NXT':
            self.UCtype = 'NFD_on_NXT' #    ='7476479172898689702'
            self.accountOther = sessMan.uc31_xGateMain.acctNFD
            self.accountThis = sessMan.uc31_xGateMain.acctNXT
            self.tokenThis = self.accountThis.xGassetID
            self.tokenOther = self.accountOther.xGassetID
            self.thisSide = 'NXT' # 'NXT'
            self.otherSide = 'NFD' # or 'NFD'
        else:
            print("ERRRRROR")


        self.accountThis.getBCTime()
        self.accountOther.getBCTime()

        self.UC32_iniTimeThis = self.accountThis.NRSTime
        self.UC32_iniTimeOther = self.accountOther.NRSTime

        self.bidOrderThisID = bidOrderThis['order']
        self.bidOrdersDiThis = { self.bidOrderThisID : bidOrderThis }

        self.bidOrderThis = bidOrderThis

        self.bidOrdersDiOther = {}
        self.bidOrdersLiOther = []
        # this is important to keep tabs on BOs that have already been registered and not act on them again!

        self.askOrderThis = {'askOrderId':'0'} # there is ONE AO_THIS
        self.askOrderOther = {'askOrderId':'0'} # there is ONE AO_OTHER
        self.askOrderThisID = '000'  # there is ONE AO_THIS
        self.askOrderOtherID = '000' # there is ONE AO_OTHER

        self.ucID = self.bidOrderThisID

        self.clientsOtherDi = {} # the same two data sets, only with different main keys mult: bidOrderIds - bidOrders
        self.clientThisDi = {} # the same two data sets, only with different main keys mult: bidOrderIds - bidOrders

        self.clientThisAccId = bidOrderThis['account']  # issuer # only ONE <-----------------wrong
        self.clientThis = nxtMods.xGateCustomer(self.sessMan,self.clientThisAccId, self.thisSide, self.otherSide,   self.ucID )
        self.clientThis.BOIDs.append(self.bidOrderThisID)
        self.clientThis.BOdict[self.bidOrderThisID] = self.bidOrderThis

        self.clientThisDi[self.clientThis.accountThis] = self.clientThis


        self.TXs = {}
        self.feeThis =[self.otherSide] # fees on NXT will be collected as NFD and vv

        self.feeOther =[self.thisSide] # for now: ['NXT', 0.2, 1.3, ] then summation [1:]

        self.XfersThis = []
        self.XfersOther = []

        self.tradesThis = {} #
        self.tradesOther = {} # TRADES are determined in the BOs !!!
        self.tradesOtherBOLi= [] # see what will be better - li or di
        self.priceOther = 0 # ! rounding errors will occur in one direction, unless we make TWO asset pairsok
        self.priceThis = 0 #
        # maybe use double accounting: for the UC32 total, AND for the individual clients

        self.tokensThis = 0 # don't change. we use this for order other calc!
        self.tokensOther = 0 # don't change. we use this for order other calc!

        self.tokensRedeemableOther = 0 # change
        self.tokensRedeemableThis = 0

        self.tokensRedeemedThis = 0
        self.tokensRedeemedOther = 0

        self.cancelSyntax=['cancel','Cancel','CANCEL']
        self.minConfsWanted = 1 # CRANK IT UP

        self.status = '0' # vol of bidOrder1


        self.makeUC32InfoPak()

        self.uc32Logger.info('NEW UC32   %s ',  self.uc32_InfoPak )
        self.uc32Logger.info('clientThis   %s  ',  str(self.clientThisAccId))
        self.catchSmallVolBidOrder = False
        self.minVol_NXT = 10
        self.minVol_NFD = 10000


        self.init_Sigs()
        self.placeAskOrderThis()

        # test was good!
        #AOtoCancel = '4414240768924750292' # put in here
        #print("trying to cancel", str(self.__dict__))
        #self.cancelTest(AOtoCancel)




    def init_Sigs(self):
        # first api feedback that TX HAS been issued
        QObject.connect(self.sessMan, SIGNAL("TX_minConfsReached_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.TX_minConfsReached_CB)
        QObject.connect(self.sessMan, SIGNAL("TX_placeAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.TX_placeAskOrder_CB)
        QObject.connect(self.sessMan, SIGNAL("TX_sendMoney_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.TX_sendMoney_CB)
        QObject.connect(self.sessMan, SIGNAL("TX_cancelAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.TX_cancelAskOrder_CB)
        QObject.connect(self.sessMan, SIGNAL("TX_sendMSG_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.TX_sendMSG_CB)
        QObject.connect(self.accountOther, SIGNAL("checkOneBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.checkOneBidOrder_CB)
        QObject.connect(self.accountThis, SIGNAL(" getAccountUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.getAccountThis_CB)
        QObject.connect(self.accountOther, SIGNAL(" getAccountUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.getAccountOther_CB)

        #
        #
        # def cancelTest(self, AOtoCancel):
        #
        #     print(5*"\n+++++enter cancelTest: ucID", str(self.ucID))
        #     # 1 cancelAskOrderOther!
        #
        #     TXparms = {}
        #     TXparms['order'] = AOtoCancel # self.askOrderThisID
        #     TXparms['feeNQT'] = '100000000'
        #     TXparms['deadline'] = '180'
        #     TXparms['publicKey'] = ''
        #     TXparms['referencedTransaction']  = '' #LATER for cancel this is sensitive: we must use OTHER not THIS, although the cancel comes from this!
        #     TXparms['secretPhrase']  = self.accountOther.xGateAccSecNXX #send WITH THIS  IS RIEGHT when looking at OTHER tokne
        #
        #     meta={}
        #     meta['uc32_ID'] = self.ucID
        #
        #     # we COULD also file this in the UC32DICT!!!
        #     meta['TXtype']='uc32_cancelAskOrderOther'
        #     meta['UC32_side']=  self.thisSide  + "_to_"  +  self.thisSide
        #     meta['xGateAcct'] = self.otherSide # do not forget this == NXT we must cancel on NFD, when this==NFD then cancel BXT
        #
        #     TX = nxtMods.CancelAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        #     TX.cancelAskOrder() #make TX instance, rest is autonomous
        #
        #     time.sleep(0.01)
        #     TXID = TX.crypt1['transaction']
        #     self.TXs[TXID] = TX
        #
        #
        #     print("SEND CANCLE SHOUDL NEOT BE A PROBLEM!")
        #
        #     TXparms['secretPhrase'] = 'dontWriteToLogFile'
        #     #self.sessMan.consLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID)    )
        #     self.sessMan.xGateLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms),  str( self.ucID)    )
        #     self.uc32Logger.info('redeemTokenThis: cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID) )
        #
        #     return None

    def makeUC32InfoPak(self):



        self.uc32_InfoPak = "self.ucID: " + self.ucID +"\n" +\
                            "self.UCtype: " + self.UCtype  + "\n" +\
                            "self.tokenThis: " + self.tokenThis  + "\n" +\
                            "self.tokenOther: " + self.tokenOther  + "\n" +\
                            "self.thisSide: " + self.thisSide  + "\n" +\
                            "self.otherSide: " + self.otherSide  + "\n" +\
                            "self.UC32_iniTimeThis: " + str(self.UC32_iniTimeThis)  + "\n" +\
                            "self.UC32_iniTimeOther: " + str(self.UC32_iniTimeOther)  + "\n" +\
                            "self.bidOrderThisID: " + str(self.bidOrderThisID)  + "\n" +\
                            "self.bidOrdersDiThis: " + str(self.bidOrdersDiThis)  + "\n" +\
                            "self.bidOrderThis: " + str(self.bidOrderThis)  + "\n" +\
                            "self.bidOrdersDiOther: " + str(self.bidOrdersDiOther)  + "\n" +\
                            "self.bidOrdersLiOther: " + str(self.bidOrdersLiOther)  + "\n" +\
                            "self.askOrderThis: " + str(self.askOrderThis)  + "\n" +\
                            "self.askOrderOther: " + str(self.askOrderOther)  + "\n" +\
                            "self.askOrderThisID: " + str(self.askOrderThisID)  + "\n" +\
                            "self.askOrderOtherID: " + str(self.askOrderOtherID)  + "\n" +\
                            "self.clientsOtherDi: " + str(self.clientsOtherDi)  + "\n" +\
                            "self.clientThisDi: " + str(self.clientThisDi)  + "\n" +\
                            "self.clientThisAccId: " +  str(self.clientThisAccId) + "\n" +\
                            "self.clientThis: " + str(self.clientThis)  + "\n" +\
                            "self.TXs: " + str(self.TXs)  + "\n" +\
                            "self.feeThis: " + str(self.feeThis)  + "\n" +\
                            "self.feeOther: " + str(self.feeOther)  + "\n" +\
                            "self.XfersThis: " + str(self.XfersThis)  + "\n" +\
                            "self.XfersOther: " + str(self.XfersOther)  + "\n" +\
                            "self.tradesThis: " + str(self.tradesThis)  + "\n" +\
                            "self.tradesOtherBOLi: " + str(self.tradesOtherBOLi)  + "\n" +\
                            "self.priceOther: " + str(self.priceOther)  + "\n" +\
                            "self.priceThis: " + str(self.priceThis)  + "\n" +\
                            "self.tokensThis: " + str(self.tokensThis)  + "\n" +\
                            "self.tokensOther: " +str(self.tokensOther)   + "\n" +\
                            "self.tokensRedeemableOther: " + str(self.tokensRedeemableOther)  + "\n" +\
                            "self.tokensRedeemableThis: " + str(self.tokensRedeemableThis)  + "\n" +\
                            "self.tokensRedeemedThis: " + str(self.tokensRedeemedThis)  + "\n" +\
                            "self.tokensRedeemedOther: " + str(self.tokensRedeemedOther)  + "\n" +\
                            "self.minConfsWanted: " + str(self.minConfsWanted)  + "\n" +\
                            "self.status: " + str(self.status)  + "\n"
        return None



    def placeAskOrderThis(self,  ):

        TXparms  = {}
        TXparms['asset'] = self.tokenThis
        TXparms['quantityQNT'] =  int(self.bidOrderThis['quantityQNT']) #self.bidOrderThis['quantityQNT']
        TXparms['priceNQT'] =  self.bidOrderThis['priceNQT']
        TXparms['secretPhrase'] = self.accountThis.xGateAccSecNXX
        TXparms['publicKey'] =  ''
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['referencedTransactionFullHash'] =  ''
        TXparms['broadcast'] =  ''

        meta = {} # this may become really important and handy here
        meta['TXtype']='uc32_askOrderThis'
        meta['uc32_ID']= self.ucID
        meta['xGateAcct'] = self.thisSide# do not forget this

        self.status = '1'
        TX = nxtMods.PlaceAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.placeAskOrder() #make TX instance, rest is autonomous
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # NB: leave this exactly like this! if this is omitted, BIZARRE behaviour results
        # ie in the mods.TX-object the singlas are NOT connected from the API!!!

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX

        # THIS IS NOT RIGHT HERE BUT KEEP IN MIND THIS IS A BIT BIZARRE BEHAVIOUR!

        TXID = TX.crypt1['transaction'] # this has a zero!
        self.TXs[TXID] = TX  # ToDo make right BOOKKEEPING HERE # wrong here because TXID is zero '0'

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.uc32Logger.info('placeAskOrderThis: \n\n %s\n  ',    str(TXparms)  )

        if self.thisSide == 'NXT':
            if TXparms['quantityQNT'] < self.minVol_NFD:
                self.catchSmallVolBidOrder = True
        elif self.thisSide == 'NFD':
            if TXparms['quantityQNT'] < self.minVol_NXT:
                self.catchSmallVolBidOrder = True




    def placeAskOrderOther(self, ):
        #self.sessMan.consLogger.info("\n******************* placeAskOrderOther")
        TXparms  = {}



        TXparms['asset'] = self.tokenOther
        TXparms['quantityQNT'] =   int(self.tokensOther)#str(self.tokensOther)#   THE SWAP OF QNT AND NQT IS DONE IN TRADETHIS!! OBACHT PRICE IS FOR ONE OTHER ONLY!!!!!                      10 NXT tokens on NFD for 10,000 NFD
        TXparms['priceNQT'] =   str(self.priceOther )                # sell for 10,000 NFD tokens on NXT for 10 NXT
        TXparms['secretPhrase'] = self.accountOther.xGateAccSecNXX
        TXparms['publicKey'] =  ''
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['referencedTransactionFullHash'] =  ''
        TXparms['broadcast'] =  ''

        meta = {} # this may become really important and handy here
        meta['TXtype']='uc32_askOrderOther'
        meta['uc32_ID']= self.ucID
        meta['xGateAcct'] = self.otherSide # do not forget this

        self.status = '3'
        TX = nxtMods.PlaceAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.placeAskOrder() #make TX instance, rest is autonomous

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # NB: leave this exactly like this! if this is omitted, BIZARRE behaviour results
        # ie in the mods.TX-object the singlas are NOT connected from the API!!!

        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX
        time.sleep(0.05)

        # THIS IS NOT RIGHT HERE BUT KEEP IN MIND THIS IS A BIT BIZARRE BEHAVIOUR!
        # todo drop this when issue settled
        self.sessMan.xGateLogger.info('UC32 askOrderThis   %s   ', str(self.askOrderThis) )
        self.sessMan.xGateLogger.info('UC32 askOrderOther  ---prelim--trash--->   %s', str(self.askOrderOther))

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.uc32Logger.info('UC32 askOrderThis   %s   ', str(self.askOrderThis) )
        self.uc32Logger.info('placeAskOrderOther:  %s - AOid not yet known, will be logged when available from NRS: ',    str(TXparms)  )

        return None


    def trade_This(self, trade):
        """ - """
        if self.tradesThis !={}: # this must have ONE trade only!
            return None
        self.tradesThis[trade['bidOrder']] = trade # trades are designated by their BIDORDER!!!!!! because there can be mult. trades for ONE ASKORDER
        # THIS IS CORRECT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #
        #  make the accounintg here
        #
        #
        self.priceThis = int(trade['priceNQT']) # THIS IS VALID FOR BOTH SIDES!
        self.priceOther = round(   ( 100000000.0 / self.priceThis) * 100000000.0  )

        self.tokensThis = int(trade['quantityQNT'])
        self.tokensOther = int(   ( int(trade['quantityQNT'])  *     int(self.priceThis))  / 100000000.0   )        # factor for price of Tokens in NQT
        self.tokensRedeemableThis = 0
        self.tokensRedeemedThis = 0
        self.clientThis.redeemedTokens = 0
        self.status = '2'
        self.askOrderThisId = trade['askOrder']
        self.uc32Logger.info('trade_This:------------------------------\n  %s \n ',    str(trade)  )

        if self.catchSmallVolBidOrder == False:
            self.placeAskOrderOther()
        if self.catchSmallVolBidOrder:
            self.status = 'finalizeThisUC32'
            self.uc32Logger.info('ABORTED UC32- Volume smaller than minimal VOlume!\n  %s \n ',    str(trade)  )



    def trade_Other(self, trade):
        """
        here we open the uc32 for redemption. when the BO has been booked. and the clientOther also.
        # in the case of MULTITRADES this is called for all trades OTHER because the BO of MULTITRADES is only ONE of course
        # so we have to filter out by ASKORDEROTHER later to direct to the proper UC32 only!
        """
        if trade['bidOrder'] in self.tradesOtherBOLi: # ref:  ignorelist

            #self.sessMan.consLogger.info("trade checked: %s is already in: %s ", str(trade) ,str(self.tradesOtherBOLi))

            return None

        # list trades by BO onlöy - less error prone

        self.sessMan.consLogger.info("trade checked: %s is NOT in: %s \n\n\n", str(trade) ,str(self.tradesOtherBOLi))

        # add this trade to the dict of the tradesOther in this UC32!
        self.tradesOther[trade['bidOrder']] = trade # other trades are listed by their BID orders of course,
        bidOrderIdOther = trade['bidOrder'] # local var only! why is this? hitter is a bo

        meta = {} # this may become really important and handy here
        meta['TXtype']='uc32_bidOrderOther'
        meta['useFor'] = 'fetchBidOrderOther'
        meta['uc32_ID']= self.ucID
        meta['xGateAcct'] = self.otherSide # do not forget this
        meta['bidOrderIdOther'] = bidOrderIdOther
        meta['trade'] = trade
        self.accountOther.fetchTransaction(bidOrderIdOther,meta) # we need to have the ORDERACCOUNT!
        return None

    # double step - fecth order via Acct object. query here, catch sig in next func
    def checkOneBidOrder_CB(self,reply, meta):
        """ we need to identify the ACCOUNT that has isseud this Bidorder
        # hint: keep here: in this case, we deal with a TX not a bidOrder. this can be confused easily, so we name it bidOrderTX
        # and extract the bidorder part that is in the attachment"""
        trade = meta['trade']
        bidOrderTX = reply   # BID ORDER OTHER!!!
        # safety checks
        if self.askOrderOtherID != trade['askOrder']:      # CHECK BEFORE RUNNING. askOrderOtherID is unique for each uc32 this is for MULTITRADES!
            # safety check. print("checkOneBidOrder_CB ", str(trade))
            return None # dont go for this doen apply
        # THIS IS IMPORTANT TO WAIT FOR CONFS!!!
        if reply['confirmations'] < self.minConfsWanted: # <<<<------------------ HERE WE CHECK FOR MINCONFS BEFORE PROCEEEDING!!! {'confirmations': 0,
            print("BAIL - checkOneBidOrder_CB: confs bid for trade other: ", str(reply['confirmations']))
            return None


        BOblockHeight = bidOrderTX['height'] # we explicitly look at accountOther!!!

        # we are ONLY delaing with BO other here!
        currNumBlocks = int(self.accountOther.connNxx.state.data['numberOfBlocks'])

        if (currNumBlocks - BOblockHeight) < 0:
            print("(currNumBlocks - BOblockHeight) < 0: bail3")
            return None

        # only NOW do tokens become redeemable !
        self.sessMan.xGateLogger.info('UC32 - check if trade applies to this UC32 %s =?= %s \n\n%s ', str(self.askOrderOtherID), str(trade['askOrder']) ,str(trade))
        self.sessMan.xGateLogger.info('UC32 BOtrade_Other SHOULD BE ONLY ONCE IN self.tradesOtherBOLi %s -?- %s ', str(trade['bidOrder']) ,str(self.tradesOtherBOLi)      ) #<---UC32 trade_Other  tradesOther {} !


        self.uc32Logger.info( 'UC32 NEW trade OTHER: %s \n', str(trade))
        self.uc32Logger.info('UC32 trade_Other  tradesOther %s ', str(self.tradesOther)) #<---UC32 trade_Other  tradesOther {} !


        try:
            BOIssuer = reply['sender']
            BOID = reply['transaction']  # BO OTHER

            #self.bidOrdersDiOther[] = {}
            self.bidOrdersLiOther.append(BOID)

        except Exception as inst:
            # ToDo shutdown uc32
            print((15*"EXECPT:"), str(reply), str(inst))

        if BOIssuer not in self.clientsOtherDi.keys():
        # this clientOther is new for this UC32 -
        #               -------------------------------------------------->>> be careful with the sides here! This should be right!
            newClientOther = nxtMods.xGateCustomer(self.sessMan, BOIssuer, self.otherSide, self.thisSide,    self.ucID )
            newClientOther.BOIDs.append(BOID)
            newClientOther.BOdict[BOID] = reply
            newClientOther.redeemableTokens = int(trade['quantityQNT'])                                                        #    +=1
            self.tokensRedeemableOther += int(trade['quantityQNT']) #self.tokensThis # this is the OTHER COIN THAT HAS TO BE PAID ON REDEMTPION i.e. 100NXT tokens

            prepLogger=''
            for k in newClientOther.__dict__:
                    prepLogger += ('\n'+ str(k)+':'+str(newClientOther.__dict__[k]) )
            self.uc32Logger.info('NEW clientOther.__dict__  %s \n',  prepLogger)
            self.clientsOtherDi[newClientOther.accountThis] = copy(newClientOther) # <--------------------- INSERT newClient HERE!

        elif BOIssuer  in self.clientsOtherDi.keys():  # returning customer IN THE SAME UC32!!!
            self.clientsOtherDi[BOIssuer].BOIDs.append(BOID)
            self.clientsOtherDi[BOIssuer].BOdict[BOID] = reply
            self.clientsOtherDi[BOIssuer].redeemableTokens += int(trade['quantityQNT'])   #  <------------------ +=1
            self.tokensRedeemableOther += int(trade['quantityQNT']) #self.tokensThis # this is the OTHER COIN THAT HAS TO BE PAID ON REDEMTPION i.e. 100NXT tokens

            prepLogger=''
            for k in self.clientsOtherDi[BOIssuer].__dict__:
                    prepLogger += ('\n'+ str(k)+' : '+str(self.clientsOtherDi[BOIssuer].__dict__[k]) )
            self.uc32Logger.info('clientsOtherDi[BOIssuer]: %s', prepLogger  )



        self.uc32Logger.info('ALL clientsOther:\n %s', str(self.clientsOtherDi))
        # wrong! that are tokens this - ie NFD not NXT how many?  int( qty*price) oh shit!

        # for tiny amounts this is wrong!


        self.clientThis.redeemableTokens +=  round( int(trade['quantityQNT']) * 0.00000001 * int(trade['priceNQT'])   ) #    int(trade['quantityQNT']) # clientThis can redeem tokens from every trade that s added here
        # eg round( int(8000) * 0.00000001 * int(100000)   ) = 8
        # eg round( int(800) * 0.00000001 * int(100000)   ) = 1 wromg
        # eg round( int(80) * 0.00000001 * int(100000)   ) = 0


        self.tokensRedeemableThis += round( int(trade['quantityQNT']) * 0.00000001 * int(trade['priceNQT'])   ) #self.tokensThis # this is the OTHER COIN THAT HAS TO BE PAID ON REDEMTPION i.e. 100NXT tokens







        for k in self.clientsOtherDi:
            prepLogger+= ('\nclientsOtherDi '+ str(k)+':'+str(self.clientsOtherDi[k]))

        tokenTab =   str(self.clientsOtherDi[BOIssuer].redeemableTokens) + " = self.clientsOtherDi[BOIssuer].redeemableTokens\n" +\
                     str(self.tokensRedeemableOther) +  " = self.tokensRedeemableOther\n"+\
                     str(self.clientThis.redeemableTokens) + " = self.clientThis.redeemableTokens\n"+ \
                     str(self.tokensRedeemableThis) + " = self.tokensRedeemableThis\n"



        self.uc32Logger.info('trade_Other. clientThis. tokenTab. %s \n\n%s\n\n', prepLogger , tokenTab )

        self.tradesOtherBOLi.append(trade['bidOrder']    ) # now it is in the IGNORE list ref:  ignorelist
        self.tradesOther[trade['bidOrder']] = trade  # now it is in the IGNORE list ref:  ignorelist

        self.sessMan.xGateLogger.info("new tradeOther REGISTERED: tradesOtherBOLi: BOs: %s \n tradesOther %s " ,str(self.tradesOtherBOLi), str( self.tradesOther))



        try:
            self.uc32Logger.info('             clientThis :' + str(self.clientThis.__dict__) + "\n" )
            self.uc32Logger.info('             clientOther on this Trade:'+ str(self.clientsOtherDi[BOIssuer].__dict__) + "\n" )

        except Exception as inst:
            print(5*"\nloggerErr",str(self.__dict__), str(inst))

        self.status = '4'
        self.sendMSGtoThis()



    def sendMSGtoThis(self):

        messageToThisClient = 'This is a MSG from xGate. \nYou can now redeem a maximum of ' + str(self.clientThis.redeemableTokens) + ' ' + \
                              self.otherSide + ' tokens to receive ' + str(self.clientThis.redeemableTokens) + ' ' + self.otherSide + ' coins.\n' + \
                            'Please transfer tokens to the xGate account ' + self.accountThis.xGateAccNumNXX + '.\nPlease make sure to correctly include your ' + \
                              self.otherSide + ' account number to receive your coins!'

        self.uc32Logger.info('sendMessageThis:   %s -  %s- %s ', messageToThisClient,     str(self.clientThis.accountThis) ,str( self.ucID))


        # not needed > 1.2.6
        #messageToThisClient = messageToThisClient.encode()
        #messageToThisClient = binas.hexlify(messageToThisClient)
        #messageToThisClient = messageToThisClient.decode()

        TXparms = {}
        TXparms['message'] = messageToThisClient
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['recipient'] = str(self.clientThis.accountThis) # Todo _: str or int???
        TXparms['publicKey'] = ''
        TXparms['referencedTransaction']  = '' #LATER
        TXparms['secretPhrase']  = self.accountThis.xGateAccSecNXX #send to OTEHR IS RIEGHT


        meta={}
        meta['uc32_ID'] = self.ucID
        meta['TXtype']='uc32_sendMessageThis'
        meta['UC32_side']= self.thisSide + "_to_"  + self.otherSide
        meta['xGateAcct'] = self.thisSide
        # do not forget this this is inverted: send NXT when redeeming nst_token_on_nfd
        # do not forget this this is inverted: send NFD when redeeming nfd_token_on_nxt

        TX = nxtMods.SendMessage(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.sendMessage() #make TX instance, rest is autonomous

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX

        try:

            self.TXs[TXID] = TX #
        except Exception as inst:   #       nope - was trivial!
            self.sessMan.xGateLogger.info('bizarre ERROR sendMSGtoThis : %s %s %s ',str(inst), str(TX), str(TX.TX_from_API))
        TXparms['secretPhrase'] = 'dontWriteToLogFile'




    def redeemTokenThis(self, Xfer):

        #print(12*"\nXFERTHIS",str(Xfer))
        try:
            if int(Xfer['timestamp'])  < self.UC32_iniTimeThis: ##
                return None # ignore old stuff
        except Exception as inst:
            self.sessMan.xGateLogger.info('UC32 redeemTokenThis type error: from %s -  %s- %s- %s except: %s', str(Xfer), str(self.UC32_iniTimeThis), \
                                          str(type(Xfer['timestamp'])) ,str(type(self.UC32_iniTimeThis)), str(inst))
            # ToDo SHUTDOWN HERE

        XferConfs = int(Xfer['confirmations'])
        if XferConfs < self.minConfsWanted: # TODO
            return None
        if Xfer['fullHash'] in self.XfersThis:
            return None




        xferAtt = Xfer['attachment']
        #acctOtherSendCoinsTo = xferAtt['comment'] # target acct number
        acctOtherSendCoinsTo = xferAtt['message'] # target acct number

        asset = xferAtt['asset'] # nxt_token_on_nfd - check: asset = assetThis??
#
# "attachment": {
#         "message": "testMESSAGEXFER",
#         "version.Message": 1,
#         "asset": "7334941058708816895",
#         "quantityQNT": "13",
#         "version.AssetTransfer": 1,
#         "messageIsText": true
#     },


        try:
            if asset != self.tokenThis:
                self.uc32Logger.info('redeemTokenThis: Error clientThis: XFer %s but token: %s \n %s ' , str(Xfer),  self.tokenThis, str(self.__dict__))
                self.status ='finalizeThisUC32'
                #ToDo: shutdown client has sent the WROOOONG ASSET! cheating attempt or error.
                return None

        except Exception as inst:
            self.uc32Logger.info('redeemTokenThis: clientThis Error : XFer %s but except: %s %s ' , str(Xfer), str(inst), str(self.__dict__) )
            #ToDo: shutdown client has sent the WROOOONG ASSET! cheating attempt or error.

        #      IN THE NEXT STEP         self.clientThis.Xfers['transaction'] = Xfer # ???? DID THIS GO RIGHT HERE???????????
        self.sessMan.xGateLogger.info('UC32 redeemTokenThis XFER %s  ',str(Xfer)   )






        # this has worked here ok!
        #
        # if acctOtherSendCoinsTo[:6] in self.cancelSyntax: # COMMENT CANCEL !!!!!!
        #     self.uc32Logger.info("\nRedeemByCancel: ucID %s", str(self.ucID))
        #     # howto: set the hash to XFERS so we dont do this again!
        #     self.redeemByCancelThis(Xfer)
        #     return None






        meta = {}
        meta['uc32_ID']= self.ucID
        meta['purpose']='verifyThatAcctHasPubkey'
        meta['issuer'] = 'UC32'
        meta['xGside'] = 'checkExistsAccountOther'
        meta['Xfer'] = Xfer

        self.uc32Logger.info('redeemTokenThis clientThis: red-able: %s - red-ed: %s xferred: %s ' , str(self.clientThis.redeemableTokens),str(self.clientThis.redeemedTokens), \
                             str( int(xferAtt['quantityQNT'])) )

        self.accountOther.fetch_getAccount(acctOtherSendCoinsTo  , meta) # to check if it has oubKey
        # twisted: to redeemTHIS we have to verify accountOtHER because accountTHIS will get the cons!
        return None
    #
    def getAccountOther_CB(self,reply,meta):
        """ - verify that acct exists. """

        if meta['xGside'] != 'checkExistsAccountOther':
            print(5*"\n should not see this getAccountOther_CB ##########but " , str(meta))
            return None

        self.sessMan.xGateLogger.info('getAccountOther_CB -reply: reply: %s \nmeta:  %s ' , str(reply),     str(meta)   )

        try:

            if 'errorDescription' in reply.keys():
                self.uc32Logger.info("ERROR! the redeem account does not exist! %s\n %s\n%s" , str(self.__dict__) , str(reply), str(self.clientThis.__dict__))
                # ToDo: only when the other trader has been paid
                self.status = 'finalizeThisUC32' ################### TODO: check for clientOther! send MSG to return tokens or so?!?!?!
                return None
            if 'guaranteedBalanceNQT' in reply.keys():
                self.uc32Logger.info("accountOther sent by clientThis has  " + reply['guaranteedBalanceNQT']  )
            if 'publicKey' in reply.keys():
                publicKey = reply['publicKey']
                self.uc32Logger.info("accountOther has pubKey: %s " , publicKey)
        except Exception as inst:
            print(10*"\nERROR", str(inst), " - ", str(self.__dict__))
            return None




        Xfer = meta['Xfer']

        xferAtt = Xfer['attachment']
        #acctOtherSendCoinsTo = xferAtt['comment'] # target acct number
        acctOtherSendCoinsTo = xferAtt['message'] # target acct number

        numTokensToRedeem = int(xferAtt['quantityQNT'])


#
# "attachment": {
#         "message": "testMESSAGEXFER",
#         "version.Message": 1,
#         "asset": "7334941058708816895",
#         "quantityQNT": "13",
#         "version.AssetTransfer": 1,
#         "messageIsText": true
#     },



        self.clientThis.Xfers['transaction'] = Xfer # ???? DID THIS GO RIGHT HERE???????????


        if self.clientThis.redeemableTokens <= 0:
            self.clientThis.Xfers['transaction'] = Xfer
            self.uc32Logger.info('Acct :No Tokens to Redeem: %s',  str(self.clientThis.__dict__) )
            self.status = 'finalizeThisUC32'
            return None # see what we do here

        if numTokensToRedeem > self.clientThis.redeemableTokens:
            prepLogger = ''
            for k in self.__dict__:
                prepLogger+= ('\n'+ str(k)+':'+str(self.__dict__[k]))
            self.uc32Logger.info("uc32 numTokensToRedeem > self.clientThis..redeemableTokens \n\n ERROR\n\n %s \n %s \n %s  ", str(reply), str(meta), prepLogger  )
            self.status = 'finalizeThisUC32'
            return None

        if self.tokensRedeemableThis < 0:
            self.uc32Logger.info(" redeemTokenThis accountg ERROR " + str(self.__dict__))
            self.status = 'finalizeThisUC32'
            return None

        # update the Xfer if it is not for the full amount of tokens
        tokensRemainingFromThisXfer =     int(Xfer['attachment']['quantityQNT']) -      numTokensToRedeem # this will be ZERO if all tokens have been sent, but some may be left
        Xfer['attachment']['quantityQNT'] = str(tokensRemainingFromThisXfer) # update this Xfer because it can be used in multipleredeems
        # update the number of tokens redeemable from the xfer!
        # this sems important!!!

        # marker: BOOK KEEPING use this comment marker to find topics!
        self.tokensRedeemedThis += numTokensToRedeem
        self.tokensRedeemableThis -= numTokensToRedeem

        self.clientThis.redeemableTokens -= numTokensToRedeem
        self.clientThis.redeemedTokens += numTokensToRedeem

        coinsOtherNQT = numTokensToRedeem * 100000000 # price in NQT of TOKEN on other!

        fee =  int( round(    float(coinsOtherNQT) * 0.01   ) ) # check details later

        coinsToSendOtherNQT = coinsOtherNQT - fee

        self.feeThis.append(str(fee))
        # KEEP TRACK OF FEE ALSO!!

        self.uc32Logger.info("redeemThisToAccountOther")
        self.uc32Logger.info("coinsOtherNQT %s ",str(coinsOtherNQT))
        self.uc32Logger.info("numTokensToRedeem %s ",str(numTokensToRedeem))
        self.uc32Logger.info("fee %s ",str(fee))
        self.uc32Logger.info("coinsToSendOtherNQT %s ",str(coinsToSendOtherNQT))

        self.uc32Logger.info("self.tokensRedeemedThis %s ",str(self.tokensRedeemedThis))
        self.uc32Logger.info("self.tokensRedeemableThis %s ",str(self.tokensRedeemableThis))
        self.uc32Logger.info("self.clientThis.redeemableTokens %s ",str(self.clientThis.redeemableTokens))
        self.uc32Logger.info("self.clientThis.redeemedTokens %s ",str(self.clientThis.redeemedTokens))


        TXparms = {}
        TXparms['amountNQT'] = str(coinsToSendOtherNQT)
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['recipient'] = acctOtherSendCoinsTo
        TXparms['publicKey'] = ''
        TXparms['referencedTransaction']  = '' #LATER
        TXparms['secretPhrase']  = self.accountOther.xGateAccSecNXX #send to OTEHR IS RIEGHT

        meta={}
        meta['uc32_ID'] = self.ucID
        meta['TXtype']='uc32_sendMoneyRedThis'
        meta['UC32_side']= self.thisSide + "_to_"  + self.otherSide
        meta['xGateAcct'] = self.otherSide
        # do not forget this this is inverted: send NXT when redeeming nst_token_on_nfd
        # do not forget this this is inverted: send NFD when redeeming nfd_token_on_nxt


        TX = nxtMods.SendMoney(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.sendMoney() #make TX instance, rest is autonomous

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.uc32Logger.info('clientThis Redeemed %s  ' ,str(TXparms) )

        print(15*"\nfinalize? redeemTokenThis ",str(self.tokensRedeemableOther <= 0 and self.tokensRedeemableThis <=0))
        if (self.tokensRedeemableOther <= 0 and self.tokensRedeemableThis <=0 ):
            self.status = 'finalizeThisUC32'

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.accountOther.accLogger.info('redeemTokenOther: sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID))



        self.uc32Logger.info('redeemTokenThis: sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID)   )

        self.uc32Logger.info('redeemTokenThis: clientThis redeemable: %s: redeemed %s numTokensToRedeem: %s  ' , \
                                                                         str(self.clientThis.redeemableTokens),\
                                                                          str(self.clientThis.redeemedTokens),\
                                                                          str(numTokensToRedeem))




        self.XfersThis.append(Xfer['fullHash']) # redeem THIS is an XFER on THIS

        #self.uc32Logger.info('XfersThis registered: %s\n', Xfer['fullHash'])

        self.makeUC32InfoPak()

        self.uc32Logger.info('redeemTokenThis   %s ',  self.uc32_InfoPak )

        return None


    def redeemByCancelThis(self, Xfer):
        #ToDO there is room for error here when the Xfer and a trade overlap. fix later.
        print(5*"\n+++++enter RedeemByCancel: ucID", str(self.ucID))

        xferAtt = Xfer['attachment']
        try:
            if int(Xfer['timestamp']) < self.UC32_iniTimeThis: ##
                return None # ignore old stuff
        except:
            self.sessMan.xGateLogger.info('UC32 redeemTokenOther type ERROR: from %s -  %s- %s- %s', str(Xfer), str(self.UC32_iniTimeOther), \
                                          str(type( Xfer['timestamp']))  ,str(type(self.UC32_iniTimeOther)))

        if Xfer['fullHash'] in self.XfersThis:
            self.sessMan.consLogger.info('UC32 redeemByCancelThis: HAVE BEEN HERE ALREADY from %s   ', str(Xfer),str(self.clientThis.__dict__ ))
            return None

        XferConfs = int(Xfer['confirmations'])
        if XferConfs < self.minConfsWanted: # ToDO enter confs check number here
        #     # this works good!print("redeemTokenOther RCD XFER BUT XferCons" + str(XferConfs))
             return None

        # ToDo check for toknsRedeemableOther == 0 !!!!!!!!11
        # this will be what determines if it can be cancelled!

        try:

            if self. tokensredeemableOther != 0:
                self.sessMan.xGateLogger.info('UC32 redeemByCancelThis e ERROR: from %s    %s ', str(Xfer), str(self.__dict__) )
                self.uc32Logger.info('redeemTokenThis: ERROR: from %s -  %s- %s ', str(Xfer), str(self.__dict__)   )

                return None
        except Exception as inst:
            print(  str(self.__dict__) , str(inst) )

        self.sessMan.xGateLogger.info('UC32 redeemByCancelThis: THIS MUST OCCUR ONLY ONCE from %s  %s ', str(Xfer),str(self.clientThis.__dict__ ))
        self.clientThis.redeemableTokens = int(xferAtt['quantityQNT'])

        self.sessMan.xGateLogger.info("XferConfs = int(Xfer['confirmations']):: %s", XferConfs)

        TXparms = {}
        TXparms['order'] = self.askOrderOtherID # self.askOrderThisID
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['publicKey'] = ''
        TXparms['referencedTransaction']  = '' #LATER for cancel this is sensitive: we must use OTHER not THIS, although the cancel comes from this!
        TXparms['secretPhrase']  = self.accountOther.xGateAccSecNXX #send WITH THIS  IS RIEGHT when looking at OTHER tokne

        meta={}
        meta['uc32_ID'] = self.ucID

        meta['Xfer'] = Xfer
        # we COULD also file this in the UC32DICT!!!
        meta['TXtype']='uc32_cancelAskOrderOther'
        meta['UC32_side']=  self.thisSide  + "_to_"  +  self.otherSide
        meta['xGateAcct'] = self.otherSide # do not forget this == NXT we must cancel on NFD, when this==NFD then cancel BXT


        TX = nxtMods.CancelAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.cancelAskOrder() #make TX instance, rest is autonomous

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX

        self.XfersThis.append(Xfer['fullHash']) # redeem THIS is an XFER on THIS
        self.uc32Logger.info('XferThis registered: %s\n', Xfer['fullHash'])

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        #self.sessMan.consLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID)    )
        self.sessMan.xGateLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms),  str( self.ucID)    )
        self.uc32Logger.info('redeemTokenThis: cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID) )

        return None


    def cancelAskConfirmed(self, reply, meta):

        #Xfer = meta['Xfer']

        print(20*"\n#####  sendMoneyBack after CANCEL")
        if self.tokensRedeemableThis < 0:
            self.uc32Logger.info(" redeemTokenThis accountg ERROR " + str(self.__dict__))
            # ToDo shutdown w/ error
            return None

        tokensThis = min(int(self.bidOrderThis['quantityQNT']),self.clientThis.redeemableTokens)
        # never send back more than paid in, even when more tokens are sent!

        # marker: BOOK KEEPING use this comment marker to find topics!
        self.tokensRedeemableThis = 0
        self.tokensRedeemableOther = 0
        self.clientThis.redeemableTokens = 0

        priceThis = int(self.bidOrderThis['priceNQT'])
        thisAcctCancelTo = self.bidOrderThis['account']
        coinsThis = tokensThis * priceThis

        fee =  int( round(    float(coinsThis) * 0.01   ) ) # check details later
        coinsToSendThisNQT = coinsThis - fee # should be in NQT

        self.feeThis.append(str(fee))
        # KEEP TRACK OF FEE ALSO!!

        TXparms = {}
        TXparms['amountNQT'] = str(coinsToSendThisNQT)
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['recipient'] = thisAcctCancelTo
        TXparms['publicKey'] = ''
        TXparms['referencedTransaction']  = '' #LATER
        TXparms['secretPhrase']  = self.accountThis.xGateAccSecNXX #send to OTEHR IS RIEGHT

        meta={}
        meta['uc32_ID'] = self.ucID
        meta['TXtype']='uc32_sendMoneyCancelThis'
        meta['UC32_side']= self.thisSide + "_to_"  + self.thisSide
        meta['xGateAcct'] = self.thisSide
        # do not forget this this is inverted: send NXT when redeeming nst_token_on_nfd

        TX = nxtMods.SendMoney(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.sendMoney() #make TX instance, rest is autonomous

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX

        self.uc32Logger.info('SENTmoney redeemTokenThis: ONLY FOR ONE UC at a time! cancelAskConfirmed sendingMoney: %s  %s  %s', str(TXparms)  , str(TXparms['recipient']) ,str( self.ucID)   )
        self.status = 'finalizeThisUC32'

        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.uc32Logger.info('clientThis Redeemed %s  ' ,str(TXparms) )
        self.accountOther.accLogger.info('redeemTokenOther:cancelAskConfirmed sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID))
        self.uc32Logger.info('redeemTokenThis: cancelAskConfirmed sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID)   )

        self.makeUC32InfoPak()

        self.uc32Logger.info('redeemTokenThis   %s ',  self.uc32_InfoPak )
        return None








    def redeemTokenOther(self, Xfer):

        try:
            if int(Xfer['timestamp']) < self.UC32_iniTimeOther: ##
                return None # ignore old stuff
        except:
            self.sessMan.xGateLogger.info('UC32 redeemTokenOther type ERROR: from %s -  %s- %s- %s', str(Xfer), str(self.UC32_iniTimeOther), \
                                          str(type( Xfer['timestamp']))  ,str(type(self.UC32_iniTimeOther)))
        # redeemTokenOther means that on the OTHER acct the token has been sent, and the coins have to be aent on the THIS account.
        # but the transfer is on the OTHER side  #22222222222222222222222222222222
        if Xfer['fullHash'] in self.XfersOther: # ok now
            return None

        XferConfs = int(Xfer['confirmations'])
        if XferConfs < self.minConfsWanted: # ToDO enter confs check number here
            return None




        xferAtt = Xfer['attachment']
        #acctThisSendCoinsTo = xferAtt['comment'] # target acct number
        acctThisSendCoinsTo = xferAtt['message'] # target acct number

        asset = xferAtt['asset'] # nxt_token_on_nfd - check: asset = assetThis??
#
# "attachment": {
#         "message": "testMESSAGEXFER",
#         "version.Message": 1,
#         "asset": "7334941058708816895",
#         "quantityQNT": "13",
#         "version.AssetTransfer": 1,
#         "messageIsText": true
#     },


        try:
            if asset != self.tokenOther:
                self.uc32Logger.info('redeemTokenOther: Error clientThis: XFer %s but token: %s \n %s ' , str(Xfer),  self.tokenOther, str(self.__dict__))
                self.status ='finalizeThisUC32'
                return None
        except Exception as inst:
            self.uc32Logger.info('redeemTokenThis: clientThis Error : XFer %s but except: %s %s ' , str(Xfer), str(inst), str(self.__dict__) )

#
# "attachment": {
#         "asset": "14576994730285238779",
#         "quantityQNT": "120",
#         "comment": "NFD-EC9N-X49V-8YXM-8RFT7"
#
#
        self.sessMan.xGateLogger.info('UC32 redeemTokenOther  XFER %s  ',str(Xfer)   )

        meta = {}
        meta['uc32_ID']= self.ucID
        meta['purpose']='verifyThatAcctHasPubkey'
        meta['issuer'] = 'UC32'
        meta['xGside'] = 'checkExistsAccountThis'
        meta['Xfer'] = Xfer

        print(5*"\ncheck of acct ok: acctThisSendCoinsTo ", str(acctThisSendCoinsTo), "\nmeta:", str(meta))
        self.uc32Logger.info('redeemTokenThis clientThis: redable: %s - redded: %s xferred: %s ' , str(self.clientThis.redeemableTokens),str(self.clientThis.redeemedTokens), \
                             str( int(xferAtt['quantityQNT'])) )

        self.accountThis.fetch_getAccount(acctThisSendCoinsTo  , meta) # to check if it has oubKey
        #self.accountOther.fetch_getAccount(acctThisSendCoinsTo  , meta) # to check if it has oubKey

        # twisted: to redeemOTHER we have to verify accountTHIS because accountTHIS will get the cons!

    # getAccountThis belongs to redeemTokenOrher!

    def getAccountThis_CB(self,reply,meta):


        if meta['xGside'] != 'checkExistsAccountThis':
            print(5*"\n should not see this getAccountThis_CB ##########but " , str(meta))
            return None


        self.sessMan.xGateLogger.info('getAccountThis_CB -reply: reply: %s \nmeta:  %s ' , str(reply),     str(meta)   )

        try:

            if 'errorDescription' in reply.keys():
                self.uc32Logger.info("ERROR! the redeem account does not exist! " + str(self.__dict__) + str(reply))

                self.status = 'finalizeThisUC32'
                return None

            if 'guaranteedBalanceNQT' in reply.keys():
                self.uc32Logger.info("accountOther has  " + reply['guaranteedBalanceNQT']  )


            if 'publicKey' in reply.keys():
                publicKey = reply['publicKey']
                self.uc32Logger.info("accountOther has pubKey: " + publicKey)



        except Exception as inst:
            print(10*"\nERROR", str(inst), " - ", str(self.__dict__))
            return None


        Xfer = meta['Xfer']




        xferAtt = Xfer['attachment']
        #acctThisSendCoinsTo = xferAtt['comment'] # this and other exchanged!
        acctThisSendCoinsTo = xferAtt['message'] # this and other exchanged!

        numTokensToRedeem = int(xferAtt['quantityQNT'])
#
# "attachment": {
#         "message": "testMESSAGEXFER",
#         "version.Message": 1,
#         "asset": "7334941058708816895",
#         "quantityQNT": "13",
#         "version.AssetTransfer": 1,
#         "messageIsText": true
#     },


        # marker: BOOK KEEPING use this comment marker to find topics!
        # identify who sent them - which clientOther?
        tokenSender = Xfer['sender']
        clientOtherToRedeem = self.clientsOtherDi[tokenSender]
        clientOtherToRedeem.Xfers['transaction'] = Xfer # ???? DID THIS GO RIGHT HERE???????????

        # this is for when clientOther tries to send MORE tokens than in our Book
        if clientOtherToRedeem.redeemableTokens <= 0:
            clientOtherToRedeem.Xfers['transaction'] = Xfer
            self.uc32Logger.info('Acct :No TOkens to Redeem: %s',  str(clientOtherToRedeem.__dict__) )
            #self.status = 'finalizeThisUC32'
            return None # see what we do here

        if numTokensToRedeem > clientOtherToRedeem.redeemableTokens:
            prepLogger = ''
            for k in self.__dict__:
                prepLogger+= ('\n'+ str(k)+':'+str(self.__dict__[k]))
            self.uc32Logger.info("uc32 numTokensToRedeem > clientOtherToRedeem.redeemableTokens ERROR %s \n %s \n %s  ", str(reply), str(meta), prepLogger  )
            #self.status = 'finalizeThisUC32'
            return None

        if self.tokensRedeemableOther < 0:
            self.uc32Logger.info(" redeemTokenThis accountg ERROR " + str(self.__dict__))
            self.status = 'finalizeThisUC32'
            return None

        # update the Xfer if it is not for the full amount of tokens
        tokensRemainingFromThisXfer =     int(Xfer['attachment']['quantityQNT']) -      numTokensToRedeem # this will be ZERO if all tokens have been sent, but some may be left
        Xfer['attachment']['quantityQNT'] = str(tokensRemainingFromThisXfer) # update this Xfer because it can be used in multipleredeems
        # update the number of tokens redeemable from the xfer!
        # this sems important!!!

        # this is for the total UC32
        # marker BOOK KEEPING
        self.tokensRedeemableOther -= numTokensToRedeem
        self.tokensRedeemedOther += numTokensToRedeem

        clientOtherToRedeem.redeemableTokens -= numTokensToRedeem
        clientOtherToRedeem.redeemedTokens += numTokensToRedeem

        coinsThisNQT = numTokensToRedeem * 100000000
        fee =  int( round(  float(coinsThisNQT) * 0.01  ) ) # check details later
        coinsToSendThisNQT = coinsThisNQT - fee
        self.feeOther.append(str(fee))


        self.uc32Logger.info("redeemOtherToAccountThis")
        self.uc32Logger.info("coinsThisNQT %s ",str(coinsThisNQT))
        self.uc32Logger.info("numTokensToRedeem %s ",str(numTokensToRedeem))
        self.uc32Logger.info("fee %s ",str(fee))
        self.uc32Logger.info("coinsToSendThisNQT %s ",str(coinsToSendThisNQT))

        self.uc32Logger.info("self.tokensRedeemedThis %s ",str(self.tokensRedeemedThis))
        self.uc32Logger.info("self.tokensRedeemableThis %s ",str(self.tokensRedeemableThis))
        self.uc32Logger.info("clientOtherToRedeem.redeemableTokens %s ",str(clientOtherToRedeem.redeemableTokens))
        self.uc32Logger.info("clientOtherToRedeem.redeemedTokens %s ",str(clientOtherToRedeem.redeemedTokens))


        TXparms = {}
        TXparms['amountNQT'] = str(coinsToSendThisNQT)
        TXparms['feeNQT'] = '100000000'
        TXparms['deadline'] = '180'
        TXparms['recipient'] = acctThisSendCoinsTo
        TXparms['publicKey'] = ''
        TXparms['referencedTransaction']  = '' #LATER
        TXparms['secretPhrase']  = self.accountThis.xGateAccSecNXX #send WITH THIS  IS RIEGHT when looking at OTHER tokne

        meta={}
        meta['uc32_ID'] = self.ucID
        meta['TXtype']='uc32_sendMoneyRedOther'
        meta['UC32_side']=  self.otherSide  + "_to_"  +  self.thisSide
        meta['xGateAcct'] = self.thisSide # do not forget this
        # do not forget this this is inverted: send NFD when redeeming nfd_token_on_nxt


        if self.status == 'finalizeThisUC32':
            self.uc32Logger.info('ACCOUNTING ERROR!!! abort sendMoney %s \n %s ',  str(self.__dict__), str(clientOtherToRedeem))
            return None

        # OK: sendMoney {'deadline': '180', 'amountNQT': '8910000000', 'referencedTransaction': '', 'recipient': 'NXT-5M58-J722-2QWB-3F2AJ', 'publicKey': '', 'secretPhrase': '14oreosetc14oreosetc', 'feeNQT': '100000000'}


        # WE NEED TO CHECK FOR THE CONFIRMATIONS OF THE XFER ANYWAY! EG WE NEED A MINIMUM OF CONFS
        TX = nxtMods.SendMoney(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
        TX.sendMoney() #make TX instance, rest is autonomous

        time.sleep(0.01)
        TXID = TX.crypt1['transaction']
        self.TXs[TXID] = TX


        print(15*"\nfinalize? redeemTokenOther ",str(self.tokensRedeemableOther <= 0 and self.tokensRedeemableThis <=0))
        if (self.tokensRedeemableOther <= 0 and self.tokensRedeemableThis <=0 ):
            self.status = 'finalizeThisUC32'


        TXparms['secretPhrase'] = 'dontWriteToLogFile'
        self.accountThis.accLogger.info('redeemTokenOther: sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID))
        self.uc32Logger.info('redeemTokenOther: sendingMoney:   %s NQt to %s uc32_ID %s',   str(TXparms['amountNQT']), str(TXparms['recipient']) ,str( self.ucID))
        self.uc32Logger.info('redeemToOther: clientOther redable: %s: redeemed %s numTokensToRedeem: %s  ' , \
                                                                         str(clientOtherToRedeem.redeemableTokens),\
                                                                          str(clientOtherToRedeem.redeemedTokens),\
                                                                          str(numTokensToRedeem))
        self.uc32Logger.info('XferOther registered: %s\n',  Xfer['fullHash'])



        self.XfersOther.append(Xfer['fullHash']) # redeem other is an XFER on OTHER
        #self.uc32Logger.info('XferOther registered: %s\n', Xfer['fullHash'])


        self.makeUC32InfoPak()

        self.uc32Logger.info('redeemTokenThis   %s ',  self.uc32_InfoPak )


        return None




    # this is a distributor for all kinds of TXs that first are supposed to have numConfs
    def TX_minConfsReached_CB(self, reply, meta):
        #print(10*"\nTX_minConfsReached_Sig ARRIVED")
        if meta['TXtype'] == 'uc32_askOrderOther':
            self.uc32Logger.info('uc32_askOrderOther: TX_minConfsReached_CB   %s \n  %s\n', str(reply),str(meta) )

        if meta['TXtype'] == 'uc32_askOrderThis':
            self.uc32Logger.info('uc32_askOrderThis:  TX_minConfsReached_CB:   %s \n  %s\n', str(reply),str(meta) )

        if meta['TXtype'] == 'uc32_sendMoneyRedOther':
            pass#self.uc32Logger.info('uc32_sendMoneyRedOther: TX_minConfsReached_CB:   %s \n  %s \n', str(reply),str(meta) )

        if meta['TXtype'] == 'uc32_sendMoneyRedThis':
            pass# self.uc32Logger.info('uc32_sendMoneyRedThis: TX_minConfsReached_CB   %s \n  %s \n', str(reply),str(meta) )

        if meta['TXtype'] == 'uc32_cancelAskOrderOther':
            #print(10*"\nTX_minConfsReached_Sig ARRIVED 22222222222")
            self.uc32Logger.info('uc32_cancelAskOrderOther:  TX_minConfsReached_CB   %s \n  %s \n', str(reply),str(meta) )
            self.cancelAskConfirmed(reply, meta) # this is actionable



    def TX_cancelAskOrder_CB(self, reply, meta):

        try: # ok so far
            self.sessMan.xGateLogger.info("TX_cancelAskOrder_CB has been placed. See this only once!  %s\n %s \n%s", str(reply.__dict__), str(self.TXs),str(reply.TX_from_API))

        except Exception as inst:
            print("cant print TX_cancelAskOrder_CB ", str(inst))

        self.XfersThis.append(reply.crypt1['fullHash']) # redeem THIS is an XFER on THIS WHEN CANCELBYXFER!!!!
        self.uc32Logger.info('redeemTokenByCancelThis: TX_cancelAskOrder_CB has been placed:   %s -  %s- ', str(reply),str(meta) )
        self.uc32Logger.info('XferThis registered: %s\n', reply.crypt1['fullHash'])
        return None



    def TX_sendMoney_CB(self, reply, meta): # We CAN use this to catch the callback from the api?!?!?!
        try:
            self.TXs[reply.crypt1['transaction']] = reply
        except Exception as inst:
            print("TX_sendMoney_CB 2- ",str(inst))  # <----------------_THIS GOES WRONG!!!! also
        self.uc32Logger.info('TX_sendMoney_CB: %s %s' , reply  , str(meta)    )
        self.sessMan.consLogger.info('UC32:TX_sendMoney_CB   : %s\n %s', reply  , str(meta)  )
        self.sessMan.xGateLogger.info('UC32:TX_sendMoney_CB   : %s\n %s', reply  , str(meta)  )
        return None


    def TX_sendMSG_CB(self, reply, meta):
        try:
            self.TXs[reply.crypt1['transaction']] = reply
        except Exception as inst:
            print("TX_sendMSG_CB 2- ",str(inst))
        self.sessMan.consLogger.info('UC32 TX_sendMSG_CB: from %s -  %s ', str(reply),str(meta))
        self.uc32Logger.info('TX_sendMSG_CB: TX_sendMSG_CB: from %s -  %s \n ', str(reply),str(meta) )


    def TX_placeAskOrder_CB(self, reply, meta): # We CAN use this to catch the callback from the api?!?!?!
        """                     #2014-07-27 16:19:45,747 - UC32 TX_placeAskThis_CB:super-class __init__() of type PlaceAskOrder was never called <nxtPwt.nxtModels.PlaceAskOrder object at 0x7fb6a0c5a5e8> - {'TXtype': 'uc32_askOrderThis', 'qqLen': 9, 'uc32_ID': '3517006574519425692', 'TXcreator': 'placeAskOrder', 'caller': ['toBlockCH'], 'xGateAcct': 'NFD'}
                    # It does. The object was actually created before and was used fine. I could have also used setParent() without problems in the initial stage. It was then inserted into a list and the static method I described above "found" it within the list, and then returned it to another static method. When the latter tried to use setParnet() on it, the error was returned. Anyways, the __init__() custom function of the subclass is: –  Tomer Sep 5 '12 at 11:40
                    #Edit: In your case you are trying to deepcopy a QWidget, but this is not possible. Python may be able to copy the wrapper of the QWidget, but the QWidget itself is a C++ object that python cannot handle with the default implementation of copy.deepcopy, hence whenever you call a method of the copied instance you get the RuntimeError because the underlying C++ object wasn't initialized properly.
                    #The same is true for pickling these objects. Python is able to pickle the wrapper, not the C++ object itself, hence when unpickling the instance the result is a corrupted instance.


        # we must assign the askOrderThis and askOrderother here when it gets back rom NRS
        """

        print(1*"\nhere we are self.askOrderOtherID ",self.askOrderOtherID)

        try:

            self.sessMan.xGateLogger.info('UC32:TX_placeAskOrder_CB: %s *****\n**** %s', str(reply.crypt1['transaction']), str(meta) )
            self.sessMan.xGateLogger.info('UC32:self.askOrderOtherID self.askOrderOther : %s *****\n**** %s', str(self.askOrderOtherID  ), str(self.askOrderOther) )
        except Exception as inst:
            print(str(inst))

        print(1*"\nmeta['uc32_ID'] == self.ucID:", str(self.ucID))
        print(1*"\nmeta['TXtype']  :", str(meta['TXtype']))


        ######## TODO check TX wrong here
        if meta['uc32_ID'] == self.ucID:
            try:

                if meta['TXtype'] == 'uc32_askOrderThis':
                    self.askOrderThisID = reply.crypt1['transaction']
                    self.askOrderThis['askOrderId'] = reply.crypt1['transaction']
                    self.askOrderThis[reply.crypt1['transaction']] = reply  # there is ONE AO_THIS
                    self.TXs[self.askOrderThisID] = reply # OK!
                    prepLogger = '\nthere should only be one askOrderThis for UC32:    ' +str(self.askOrderThis)
                    self.sessMan.xGateLogger.info('UC32 TX_placeAskOrder_CB:%s %s - %s',prepLogger, str(reply.crypt1['transaction']) ,str(meta)   )
                    self.uc32Logger.info('uc32_askOrderThis: %s  ' , str(self.askOrderThis)     )

            except Exception as inst:
                self.sessMan.xGateLogger.info('UC32 TX_placeAskThis_CB: ExceptionExceptionException Exception Exception %s %s - %s', str(inst), str(reply) ,str(meta)   )

            try:
                if meta['TXtype'] == 'uc32_askOrderOther':
                    self.askOrderOtherID = reply.crypt1['transaction']
                    self.askOrderOther['askOrderId'] = reply.crypt1['transaction']
                    self.askOrderOther[reply.crypt1['transaction']] = reply  # there is ONE AO_THIS
                    self.TXs[self.askOrderThisID] = reply
                    prepLogger = 'there should only be one askOrderOther for UC32\n' +str(self.askOrderOther)
                    self.sessMan.xGateLogger.info('UC32 TX_placeAskOrder_CB:%s %s - %s',prepLogger, str(reply.crypt1['transaction']) ,str(meta)   )
                    self.uc32Logger.info('askOrderOther: %s  ' , str(self.askOrderOther)     )

            except Exception as inst:
                self.sessMan.xGateLogger.info('UC32 TX_placeAskOrder_CB: ExceptionExceptionExceptionException Exception %s %s - %s', str(inst), str(reply) ,str(meta)   )

            self.sessMan.xGateLogger.info('AFTER UC32:TX_placeAskOrder_CB: %s *****\n**** %s', str(reply.crypt1['transaction']), str(meta) )
            # still got the zeros in here-
            # self.sessMan.xGateLogger.info('AFTER UC32:self.askOrderOtherID self.askOrderOther : %s *****\n**** %s', str(self.askOrderOtherID  ), str(self.askOrderOther) )


            return None




######################################
#
# {
#     "fullHash": "83896d766859c2547b54faa0a1b3e6c7137cbb1bfa640a680e65dd710676e7b0",
#     "signatureHash": "5543913f3d80300ed7d03b1b4c556f65123da0cb8224853ef3384f9a2f21464c",
#     "transactionBytes": "021129c17b00b40058be6060e13815503922acc3f0a9d4524f71b09b4d4a4a7c247907e4432af44cb01209fec4a840e0000000000000000000e1f5050000000000000000000000000000000000000000000000000000000000000000000000003f549fd9c0fefd28d19d8d597cd088cd8b939e8fa6835e73d284fd1d4cf83d06a93feb63264fd4b2fa868076eadb655f58acbac2a6c82d15efb4f09f1ffa3cfc010000001acd000026f8165d2f56bfc701ff43c4dc07f2ca650d00000000000000010f000080746573744d45535341474558464552",
#     "transaction": "6107542349866174851",
#     "transactionJSON": {
#         "fullHash": "83896d766859c2547b54faa0a1b3e6c7137cbb1bfa640a680e65dd710676e7b0",
#         "signatureHash": "5543913f3d80300ed7d03b1b4c556f65123da0cb8224853ef3384f9a2f21464c",
#         "transaction": "6107542349866174851",
#         "amountNQT": "0",
#         "ecBlockHeight": 52506,
#         "attachment": {
#             "message": "testMESSAGEXFER",
#             "version.Message": 1,
#             "asset": "7334941058708816895",
#             "quantityQNT": "13",
#             "version.AssetTransfer": 1,
#             "messageIsText": true
#         },
#         "recipientRS": "NFD-L6PJ-SMZ2-5TDB-GA7J2",
#         "type": 2,
#         "feeNQT": "100000000",
#         "recipient": "16159101027034403504",
#         "version": 1,
#         "sender": "7126304194855053556",
#         "timestamp": 8110377,
#         "ecBlockId": "14393317695524632614",
#         "height": 2147483647,
#         "subtype": 1,
#         "senderPublicKey": "58be6060e13815503922acc3f0a9d4524f71b09b4d4a4a7c247907e4432af44c",
#         "deadline": 180,
#         "senderRS": "NFD-EC9N-X49V-8YXM-8RFT7",
#         "signature": "3f549fd9c0fefd28d19d8d597cd088cd8b939e8fa6835e73d284fd1d4cf83d06a93feb63264fd4b2fa868076eadb655f58acbac2a6c82d15efb4f09f1ffa3cfc"
#     },
#     "broadcasted": true,
#     "unsignedTransactionBytes": "021129c17b00b40058be6060e13815503922acc3f0a9d4524f71b09b4d4a4a7c247907e4432af44cb01209fec4a840e0000000000000000000e1f50500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000001acd000026f8165d2f56bfc701ff43c4dc07f2ca650d00000000000000010f000080746573744d45535341474558464552"
# }


    # was good!
    #
    #
    # def cancelTest(self, AOtoCancel):
    #
    #     print(5*"\n+++++enter cancelTest: ucID", str(self.ucID))
    #     # 1 cancelAskOrderOther!
    #
    #     TXparms = {}
    #     TXparms['order'] = AOtoCancel # self.askOrderThisID
    #     TXparms['feeNQT'] = '100000000'
    #     TXparms['deadline'] = '180'
    #     TXparms['publicKey'] = ''
    #     TXparms['referencedTransaction']  = '' #LATER for cancel this is sensitive: we must use OTHER not THIS, although the cancel comes from this!
    #     TXparms['secretPhrase']  = self.accountOther.xGateAccSecNXX #send WITH THIS  IS RIEGHT when looking at OTHER tokne
    #
    #     meta={}
    #     meta['uc32_ID'] = self.ucID
    #
    #     # we COULD also file this in the UC32DICT!!!
    #     meta['TXtype']='uc32_cancelAskOrderOther'
    #     meta['UC32_side']=  self.thisSide  + "_to_"  +  self.thisSide
    #     meta['xGateAcct'] = self.otherSide # do not forget this == NXT we must cancel on NFD, when this==NFD then cancel BXT
    #
    #     TX = nxtMods.CancelAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = meta )
    #     TX.cancelAskOrder() #make TX instance, rest is autonomous
    #
    #     time.sleep(0.01)
    #     TXID = TX.crypt1['transaction']
    #     self.TXs[TXID] = TX
    #
    #
    #     print("SEND CANCLE SHOUDL NEOT BE A PROBLEM!")
    #
    #     TXparms['secretPhrase'] = 'dontWriteToLogFile'
    #     #self.sessMan.consLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID)    )
    #     self.sessMan.xGateLogger.info('UC32 cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms),  str( self.ucID)    )
    #     self.uc32Logger.info('redeemTokenThis: cancelAskOrderOther: from %s -  %s- %s ', str(TXID), str(TXparms ),  str( self.ucID) )
    #
    #     return None
    #















class UC2_accountHandler(nxtUseCaseMeta):

    changeResident_Sig = pyqtSignal(object, object)

    def __init__(self, sessMan, ):
        super(UC2_accountHandler   , self   ).__init__(sessMan)


        #self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'uc2'}

        self.allAccs = nxtMods.Accounts(sessMan)

        # persistence later
        defPass14 = '14oreosetc14oreosetc'
        defPass15 = '15oreosetc15oreosetc'
        defPass16 = '16oreosetc16oreosetc'
        defPass17 = '17oreosetc17oreosetc'

        acctSecKey = defPass17

        self.accRes = nxtMods.Account(self, sessMan, acctSecKey,  )
        self.accRes.getAccountId(self.meta )

        self.accFOC = self.accRes.data['account']

        self.accSLT =  nxtMods.Account(self, sessMan, '0',)
        self.accOIss =  nxtMods.Account(self, sessMan, '0',)

        self.pollaccRes()

# acct handler needs own methods!


    def changeResidAccount(self, acctSecKey):
        # move resident to list
        # make new one. check if new is in list already, else totally new<

        self.allAccs.accountsDi[self.accRes.data['account']] = self.accRes

        # create new account instance
        self.accRes = nxtMods.Account(self, self.sessMan, acctSecKey,   )
        self.accRes.getAccountId( self.meta )
        # announce new accRes
        self.meta['caller'] = ['uc2_accRes']
        self.emit( SIGNAL( "changeResident_Sig(PyQt_PyObject, PyQt_PyObject)"), self.accRes, self.meta)
        #print(str(self.allAccs.accountsDi))
        self.pollaccRes()

    # this starts polling the resident account
    def pollaccRes(self):
        self.accRes.poll1Start(self.meta)
    # here we can poll any account we want
    def pollAccStop(self):
        self.accRes.poll1Stop(self.meta)

    def startForge(self):
        self.accRes.startForging()

    def stopForge(self):
        self.accRes.stopForging()


    def getAccount(self):
        pass

    # TX creation API calls done by this UC

    def setAccountInfo(self, TXparms):
        self.TX = nxtMods.SetAccountInfo(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta)
        self.TX.setAccountInfo() #make TX instance, rest is autonomous

    def leaseBalance(self, TXparms):
        self.TX = nxtMods.LeaseBalance(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta)
        self.TX.leaseBalance() #make TX instance, rest is autonomous
    #################
    def assignAlias(self):
        pass

    #############################
    # retro TXs:  get activity from past
    def getAliases(self):
        pass
    def MSGs(self): # including Polls
        pass
    def getNxtXfers(self):
        pass



class UC29_changeConn(nxtUseCaseMeta):
    """
    UC29 does not communicate with api
    """

    def __init__(self, sessMan,  ):
        super(UC29_changeConn   , self   ).__init__(sessMan)
        self.apiCalls = nxtQs()
        #self.app = app # we need to know app
        self.sessMan = sessMan


    def changeConn(self, newConn):

        #self.sessMan.uc29_newConn.newUrl(newUrl)
        del self.sessMan.activeNRS

        print(str(newConn))
        self.sessMan.activeNRS = nxtMods.NRSconn(self, newConn)

        self.nxtApi.initSignals()




class UC3_TX_monitor(nxtUseCaseMeta):

    """- """

    newAsset_Sig = pyqtSignal(object, object)
    newMXfer_Sig = pyqtSignal(object, object)
    newAskOrder_Sig = pyqtSignal(object, object)
    newBidOrder_Sig = pyqtSignal(object, object)
    newTrade_Sig = pyqtSignal(object, object)
    newBidOrderCancel_Sig = pyqtSignal(object, object)
    newAskOrderCancel_Sig = pyqtSignal(object, object)
    newMSG_Sig = pyqtSignal(object, object)
    newAlias_Sig = pyqtSignal(object, object)
    newLease_Sig = pyqtSignal(object, object)
    newAcctInfo_Sig = pyqtSignal(object, object)
    newPoll_Sig = pyqtSignal(object, object)
    newVote_Sig = pyqtSignal(object, object)


    def __init__(self, sessMan,  ):
        super(UC3_TX_monitor   , self   ).__init__(sessMan)
        self.apiCalls = nxtQs()
        #self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'UC_TXchecker'}
        #print(str(self.sessMan.activeNRS.block))
        self.TXs = {}
        self.init_Sigs()

    def init_Sigs(self):
        QObject.connect(self.sessMan.activeNRS.block, SIGNAL("newTXs_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.newTXs_CB)
        QObject.connect(self.sessMan.nxtApi, SIGNAL("getTransaction_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTransaction_fromApi)


    def newTXs_CB(self, newTXs_inBlock, meta):
        #print("NEW TXS!\n")
        for TX in newTXs_inBlock:
            self.TXs[TX] = nxtMods.TX(self.sessMan, TX )
            print( str(TX) + str(meta))

    def getTransaction_fromApi(self, TX, meta): # TX is a dict returned from the API! NOT the TX INSTANCE ITSELF!
        print("getTransaction_fromApi in uc3: " + str(TX) + " --- " + str(meta) + "\n")
        # in principle this works, it is only a bit bit ugly.
        # has been tested, these appear once in the new block!
        if 'caller' in meta.keys():

            if meta['caller'] == 'fromBlockCH':
                pass
                #print("TX fromBlockCH,   TX detect")
                #for m in meta:
                #    print(str(m) + " - " + str(meta[m]) )
                #for k in TX:
                #    print(str(k) + " - " + str(TX[k]) )
            elif  meta['caller'] == 'toBlockCH':
                print("TX toBlockCH, not a TX detect")


    # later - for detailed TX monitoring eg new asset emission
    def newAsset(self):
        self.emit( SIGNAL( "newAsset_Sig(PyQt_PyObject, PyQt_PyObject)"), self.cont, self.meta )







class UC4_sendMoney(nxtUseCaseMeta):
    """ UC classes do the TX handling- TX is an object itself """

    def __init__(self, sessMan,   ):
        super(UC4_sendMoney   , self   ).__init__(sessMan)
        #self.apiCalls = nxtQs()
        # self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'uc4_sendMoney'}

    # TX creation API calls done by this UC
    # these functions are called to create TX instances
    def sendMoney(self, TXparms):
        self.TX = nxtMods.SendMoney(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.sendMoney() #make TX instance, rest is autonomous
        # todo: check : the TX instance may be overwritten when new TXs are sent too fast

    # def setAccountInfo(self, TXparms):
    #     self.TX = nxtMods.SetAccountInfo(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta)
    #     self.TX.setAccountInfo() #make TX instance, rest is autonomous
    #








class UC5_AE(nxtUseCaseMeta):

    """ api comm. can be handled by the UC OR by the model - try this: hanlde here by model _"""
    # more specific Sigs are throen by the UCs themselves
    uc5_getAllAssets_Sig = pyqtSignal(object, object)
    uc5_getAssets_Sig = pyqtSignal(object, object)
    uc5_getAsset_Sig = pyqtSignal(object, object)
    uc5_getAssetIds_Sig = pyqtSignal(object, object)

    uc5_getAssetsByName_Sig = pyqtSignal(object, object)

    uc5_getAccountResid_Sig = pyqtSignal(object, object)
    uc5_getAccountSlated_Sig = pyqtSignal(object, object)

    uc5_focusAsset_Sig = pyqtSignal(object, object) # emit by AE_assets to send assetId to Orderbook!


    def __init__(self, sessMan,):
        super(UC5_AE   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.meta={'caller':'uc5'}
        self.nxtApi = self.sessMan.nxtApi
        # these are just for collection and overview of what happens here.
        self.apiReq_getAsset = self.apiCalls.getAsset
        self.apiReq_getAllAssets = self.apiCalls.getAllAssets
        self.apiReq_getAssetIds = self.apiCalls.getAssetIds
        self.apiReq_getAssets = self.apiCalls.getAssets
        self.apiReq_getAssetsByName = self.apiCalls.getAssetsByName
        #
        self.apiReq_getAccount = self.apiCalls.getAccount
        #
        self.assets = nxtMods.Assets(sessMan)
        self.uc5_allAssets_proxy = QSortFilterProxyModel(self)
        self.uc5_allAssets_proxy.setSourceModel(self.assets.allAssetsQtM)
        #
        self.uc5_accAssets_proxy = QSortFilterProxyModel(self)
        self.uc5_accAssets_proxy.setSourceModel(self.assets.accAssetsQtM)


        self.orders= nxtMods.Orders(sessMan)
        self.uc5_askO_single_proxy = QSortFilterProxyModel(self)
        self.uc5_askO_single_proxy.setSourceModel(self.orders.ordersAsk_QtM)

        self.uc5_bidO_single_proxy = QSortFilterProxyModel(self)
        self.uc5_bidO_single_proxy.setSourceModel(self.orders.ordersBid_QtM)

        self.uc5_assetShortList = nxtMods.SimpleListQMod(sessMan, 10, 'noHeader')

        self.uc5_acctShortList = nxtMods.SimpleListQMod(sessMan, 10, 'noHeader')





        QObject.connect(self.nxtApi, SIGNAL("getAllAssets_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAllAssets_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getAccount_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAccount_fromApi)


    # request to api and return of result
    def getAllAssets(self): # toApi
        self.assets.allAssetsQtM.clear()
        self.nxtApi.getAllAssets_Slot( self.apiReq_getAllAssets , self.meta)

    def getAllAssets_fromApi(self, reply, meta):
        self.assets.enterAllAssetsTable(reply, meta)

    def getAccount(self, accountToFetch, caller):
        self.meta['usedFor'] = 'getAccountAssets'
        self.meta['whichAcc'] = caller
        self.assets.accAssetsQtM.clear()
        self.apiReq_getAccount['account'] = accountToFetch
        self.nxtApi.getAccount_Slot( self.apiReq_getAccount , self.meta)

    def getAccount_fromApi(self, reply, meta):
        if meta['caller']=='uc5':
            self.assets.enterAccAssetsTable(reply, meta) # <--- DIRECTLY INTO THE MODEL HERE!
            if meta['whichAcc'] == 'accRes':
                self.emit( SIGNAL( "uc5_getAccountResid_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta)
            elif meta['whichAcc'] == 'accSLT':
                self.emit( SIGNAL( "uc5_getAccountSlated_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta)



class UC6_AO(nxtUseCaseMeta):

    def __init__(self, sessMan,):
        super(UC6_AO   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.meta={'caller':'uc6'}
        self.nxtApi = self.sessMan.nxtApi

        self.apiReq_getAskOrderIds = self.apiCalls.getAskOrderIds
        self.apiReq_getBidOrderIds = self.apiCalls.getBidOrderIds

        self.apiReq_getAskOrder = self.apiCalls.getAskOrder
        self.apiReq_getBidOrder = self.apiCalls.getBidOrder

        self.orders= nxtMods.Orders(sessMan)
        self.uc6_askO_single_proxy = QSortFilterProxyModel(self)
        self.uc6_askO_single_proxy.setSourceModel(self.orders.ordersAsk_QtM)

        self.uc6_bidO_single_proxy = QSortFilterProxyModel(self)
        self.uc6_bidO_single_proxy.setSourceModel(self.orders.ordersBid_QtM)

        QObject.connect(self.nxtApi, SIGNAL("getAskOrderIds_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAskOrderIds_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getBidOrderIds_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getBidOrderIds_fromApi)

        QObject.connect(self.nxtApi, SIGNAL("getAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAskOrder_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getBidOrder_fromApi)


    def getOrders(self, assetID):
        self.assetID = assetID
        self.meta['usedFor'] = 'getOrderIds'
        self.apiReq_getBidOrderIds['asset'] = self.assetID
        self.nxtApi.getBidOrderIds_Slot( self.apiReq_getBidOrderIds , self.meta)
        self.apiReq_getAskOrderIds['asset'] = self.assetID
        self.nxtApi.getAskOrderIds_Slot( self.apiReq_getAskOrderIds , self.meta)

    def getAskOrder(self,askO):
        self.meta['usedFor'] = 'getAskOrder'
        self.apiReq_getAskOrder['order'] = askO
        self.nxtApi.getAskOrder_Slot( self.apiReq_getAskOrder , self.meta)
    def getBidOrder(self, bidO):
        self.meta['usedFor'] = 'getBidOrder'
        self.apiReq_getBidOrder['order'] = bidO
        self.nxtApi.getBidOrder_Slot( self.apiReq_getBidOrder , self.meta)

    def getAskOrder_fromApi(self, reply, meta):

        self.orders.getAskOrder_uc6(reply, meta)

    def getBidOrder_fromApi(self, reply, meta):
        self.orders.getBidOrder_uc6(reply, meta) # <--- DIRECTLY INTO THE MODEL HERE!

    def getAskOrderIds_fromApi(self, reply, meta):
        askOrderIds=reply['askOrderIds']
        self.orders.ordersAsk_QtM.clear()
        for askO in askOrderIds:
            self.getAskOrder(askO)

    def getBidOrderIds_fromApi(self, reply, meta):
        bidOrderIds=reply['bidOrderIds']
        self.orders.ordersBid_QtM.clear()
        for bidO in bidOrderIds:
            self.getBidOrder(bidO)

    def getAllOpenOrders(self):
        pass




class UC7_ATX(nxtUseCaseMeta):

    def __init__(self, sessMan,):
        super(UC7_ATX   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.meta={'caller':'uc7'}
        self.nxtApi = self.sessMan.nxtApi
        # todo: check : the TX instance may be overwritten when new TXs are sent too fast

    # AE TX creation
    # these functions are called to create TX instances

    # this is s.t. the resident account does
    def issueAsset(self, TXparms):
        self.TX = nxtMods.IssueAsset(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.issueAsset()
    def transferAsset(self, TXparms):
        self.TX = nxtMods.TransferAsset(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.transferAsset()

    def placeAskOrder(self, TXparms):
        self.TX = nxtMods.PlaceAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.placeAskOrder() #make TX instance, rest is autonomous
    def placeBidOrder(self, TXparms):
        self.TX = nxtMods.PlaceBidOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.placeBidOrder()
    def cancelAskOrder(self, TXparms):
        self.TX = nxtMods.CancelAskOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.cancelAskOrder()
    def cancelBidOrder(self, TXparms):
        #print("cancel bid")
        self.TX = nxtMods.CancelBidOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.cancelBidOrder()

    def sendMessage(self,TXparms):
        #print("cancel bid")
        self.TX = nxtMods.CancelBidOrder(self.sessMan, TX_ID=None, TXparms=TXparms, meta = self.meta )
        self.TX.cancelBidOrder() # etc





class UC8_Trades(nxtUseCaseMeta):



    def __init__(self, sessMan,):
        super(UC8_Trades   , self   ).__init__(sessMan)
        #self.apiCalls = nxtQs()
        self.sessMan = sessMan
        self.meta = {'caller':'UC8_Trades'}


        self.nxtApi = self.sessMan.nxtApi

        self.apiReq_getTrades = self.apiCalls.getTrades
        self.apiReq_getAllTrades = self.apiCalls.getAllTrades

        QObject.connect(self.nxtApi, SIGNAL("getTrades_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTrades_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getAllTrades_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAllTrades_fromApi)


        self.trades = nxtMods.Trades(sessMan)

        self.uc8_allTrades_proxy = QSortFilterProxyModel(self)
        self.uc8_allTrades_proxy.setSourceModel(self.trades.tradesQtM)


    def getTrades(self, selAssetId, firstIndex, lastIndex):
        self.meta['usedFor'] = 'getTrades'
        #print("getTrades_fromApi: "  +  str(selAssetId) +" - " +  firstIndex + " - " + lastIndex)
        self.apiReq_getTrades['asset'] = selAssetId # )
        self.apiReq_getTrades['lastIndex'] = '' # lastIndex
        self.apiReq_getTrades['firstIndex'] = '' # firstIndex
        self.nxtApi.getTrades_Slot( self.apiReq_getTrades , self.meta)

    def getAllTrades_fromApi(self, reply, meta):
        #print("getTrades_fromApi ---- ")# +str(reply) + " - " + str(meta))
        pass

    def getTrades_fromApi(self, reply, meta):
        #print("getTrades_fromApi - " +str(reply) + " - " + str(meta))
        self.trades.enterTrades( reply, meta)




class UC9_MSGer_handler(nxtUseCaseMeta):

    def __init__(self, sessMan,  app,):
        super(UC9_MSG_handler   , self   ).__init__(sessMan)
        self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'UC9_MSG_handler'}

    # these functions are called to create TX instances
    def sendMessage(self):
        pass
    def createPoll(self):
        pass
    def castVote(self):
        pass


class UC_BlockchainTraversal(nxtUseCaseMeta):

    """- """

    def __init__(self, sessMan,  app):
        super(UC_BlockchainTraversal   , self   ).__init__(sessMan)
        self.apiCalls = nxtQs()
        self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'UC_BlockhainTraversal'}


class UC_shopKeeper(nxtUseCaseMeta):



    def __init__(self, sessMan,  app):
        super(UC_shopKeeper   , self   ).__init__(sessMan)
        self.apiCalls = nxtQs()
        self.app = app # we need to know app
        self.sessMan = sessMan
        self.meta = {'caller':'ucShopKeeper'}








#######################################################################
##############  
############## THIS IS A TEMPLATE FOR MAKING NEW USE CASES KEEP THIS HERE! 
##############                OLD TEMPLATE
#######################################################################

   
  
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
 
   
   
        
if __name__ == "__main__":
    import sys
    sys.path += [ os.path.dirname(os.path.dirname(os.path.realpath(__file__))) ]
    argv = sys.argv
    app = QtGui.QApplication(sys.argv) # creation of the app object
    done = app.exec_()
    sys.exit(done)
 
 
 
# 
## subclass QApplication and slap on whatever you want:
#class XCPApplication(QApplication):
#        """
#    A basic subclass of the QApplication object that provides us with some app-wide state
#    """
#    def __init__(self, *args, **kwargs):
#        super(XCPApplication, self).__init__(*args, **kwargs)
#        self.wallet = Wallet()
#        self.xcp_client = XCPAsyncAppClient()
#        self.btc_client = BTCAsyncAppClient()
#        self.LAST_BLOCK = None
#
#    def examine_local_wallet(self, after):
#        def cb(res):
#            self.wallet.update_addresses(res)
#            after()
#        self.btc_client.get_wallet_addresses(cb)
#
#    def fetch_initial_data(self, update_wallet_callback_func):
#        pass
#        
#   old docstring
# 1.) in WinCtrl.py
#
#     - register activator signal to be emitted from WinCtrl as:
#         UC_test1_activate = pyqtSignal(object)
#
#     - in WinCTrl __init__(), register sessMan:uc instance as:
#         self.app.sessMan.ucTest1.initWin6(self.app.nxtWin6, ui)
#
#     - connect activator widget in win to activator CB on Win as:
#         QtCore.QObject.connect(ui.pb_test1Start , SIGNAL("clicked()"), self.UC_test1_activateCB )
#
#     - in activator callback prepare signal and emit as:
#
#         def UC_test2_activateCB(self,):
#             do_something_Flash_a_LED_or_so()
#             self.emit( SIGNAL( "UC_test2_activate(PyQt_PyObject)"),  {'uc':'test2'} )    #
#
# 2.) in nxtSessionManager.py
#
#     - instantiate UC as:
#
#         self.ucTest1 = nxtUseCases.nxtUCTest1(self, self.app ) #
#         self.ucTest1.initSignals()
#
# 3.) in nxtUseCase.py
#
#     - construct UC class as per this example
#     - do what the use case is supposed to do







# use qPool threads. to activate:

    #
    # def activate(self):
    #     self.init()
    #     self.app.sessMan.uc_bridge.mm.jsonServ_Slot()
    #
    #

#
#
#
# class nxtUseCaseMeta(QObject):
#     """ This is an abstract meta class that has elemtary sigs and methods defined.
#     All use case classes inherit from this, so they know all the signals for emission
#     The useCaseClass is tho ONLY one that talks to the api.
#
#      """
#
#     apiCalls = nxtQs() # static! dict of prototypes to be filled with vals for apiReq
#     blinkerCols = [Qt.Qt.darkYellow, Qt.Qt.magenta]
#
#
#     def __init__(self,  sessMan  ): #
#         """ just call the super init here: QObject.
#        """
#         super(nxtUseCaseMeta, self).__init__()
#         self.nxtApi = sessMan.nxtApi  # there is only ONE apiSigs instance, and that is in the sessMan.
#
#
#
#
#
#
# class UC_Bridge1(nxtUseCaseMeta):
#
#     def __init__(self, sessMan, host = 'localhost', port = '6876',bridgeLogger=None , consLogger=None, wallDB=None  ):
#         super(UC_Bridge1   , self   ).__init__(sessMan)
#         self.sessMan = sessMan
#         self.qPool = sessMan.qPool
#         self.meta = {'caller':'Bridge1'}
#         self.bridgeLogger = bridgeLogger
#         self.consLogger = consLogger
#         self.walletDB = wallDB['walletDB']
#         self.walletDB_fName = wallDB['walletDB_fName']
#         self.mm = BridgeThread( self.qPool, host  , port ,  bridgeLogger,  consLogger ,wallDB )
#
#
# class BridgeThread(QObject):
#     """ 2680262203532249785 nxt genesis block """
#     def __init__(self, qPool, host, port, bridgeLogger, consLogger, wallDB ):
#         # check : is this the same as calling super(BridgeThread, etc) ???????
#         super(QObject, self).__init__( parent = None)
#         self.qPool = qPool
#         self.host = host
#         self.port = port
#         self.bridgeLogger = bridgeLogger
#         self.consLogger = consLogger
#         self.wallDB = wallDB
#         #self.walletDB = wallDB['walletDB']
#         #self.walletDB_fName = wallDB['walletDB_fName']
#
#     @pyqtSlot() # 61
#     def jsonServ_Slot(self, ):
#         """-"""
#         self.json_Runner = JSON_Runner( self.host, self.port, self.bridgeLogger, self.consLogger , self.qPool, self.wallDB) # json_Emitter, self to THIS !!!!!!
#         self.json_Runner.setAutoDelete(False)
#         self.qPool.start(self.json_Runner)
#         self.consLogger.info('  self.qPool.activeThreadCount() = %s ', str(   self.qPool.activeThreadCount()) )
#
#
# class JSON_Runner(QtCore.QRunnable):
#     """- This is what needs to be put into the QThreadpool """
#     nxtApi = nxtApi
#
#     def __init__(self,   host = 'localhost', port = '6876', fileLogger = None, consLogger = None , qPool=None, wallDB=None ): #emitter,
#         super(QtCore.QRunnable, self).__init__()
#         global session # this must be global to be accessible from the dispatcher methods
#         session = Session()
#         headers = {'content-type': 'application/json'}
#         sessUrl = 'http://' + host + ':' + port + '/nxt?'
#         global NxtReq
#
#         self.walletDB = wallDB['walletDB']
#         self.walletDB_fName = wallDB['walletDB_fName']
#         NxtReq = Req( method='POST', url = sessUrl, params = {}, headers = headers        )
#
#         # ToDo here we can also include a walletLogger to snd encrypted emails to a safe location as backup!
#         self.bridgeLogger = fileLogger
#         self.consLogger = consLogger
#         self.qPool = qPool
#
#
#
# ############################
#  # 2 generic Nxt APIs
#     @dispatcher.add_method
#     def getState(**kwargs):
#         payload = { "requestType" : "getState" }
#         NxtApi = {}
#         NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
#         NxtReq.params=NxtApi # same obj, only replace params
#         preppedReq = NxtReq.prepare()
#         response = session.send(preppedReq)
#         NxtResp = response.json()
#         return NxtResp
#
#     @dispatcher.add_method
#     def getTime( **kwargs):
#         payload = { "requestType" : "getTime" } #getTime"   }
#         NxtApi = {}
#         NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
#         NxtReq.params=NxtApi # same obj, only replace params
#         preppedReq = NxtReq.prepare()
#         response = session.send(preppedReq)
#         NxtResp = response.json()
#         return NxtResp
#
#
#
#
#     @Request.application
#     def application(self, request ):
#
#
#     def run(self,):
#         run_simple('localhost', 7879, self.application,  ) # WERKZEUG !!!!
#
#


#######################