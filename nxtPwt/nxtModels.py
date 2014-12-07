

#from PyQt4.QtCore import   QObject ,QAbstractTableModel,  pyqtSignal, pyqtSlot, SIGNAL, QModelIndex , Qt

from PyQt4.Qt import *

from PyQt4.QtGui import QColor, QPixmap, QIcon

import time
from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot, SIGNAL
from copy import copy
import numpy as np
from nxtPwt.nxtApiPrototypes import nxtQs
#import logging as lg



from collections import deque as dq


#from FR.nxtApiSigs import nxtApi




class OrdersVerbQMod(QAbstractTableModel):

    def __init__(self, obSide='', sessMan = 0 , parent = None): # no sessMan !?!?!
        super(OrdersVerbQMod, self).__init__( parent = None)
        self.sessMan = sessMan
        if obSide == 'B':
            self.bg = QColor(10,240,0,110)
        elif obSide == 'A':
            self.bg = QColor(240,10,0,110)
        self.obSide = obSide # a or b
        self.tableData = np.zeros((0,5), dtype='uint64')
        self.assetColHeaders =   ['price', 'qty', 'OIssuer','hght', 'OId']
        icon1Col = QColor(10,24,245,150)
        pixmap = QPixmap(11,11)
        pixmap.fill(icon1Col)
        self.icon1 = QIcon(pixmap)

    def flags(self, index):
        return  Qt.ItemIsEnabled  #|  Qt.ItemIsSelectable <- no red bars when clicking

    def rowCount(self, parent):
        return self.tableData.shape[0]

    def columnCount(self, tableData): ## <---check!
        return self.tableData.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < self.tableData.shape[1]:

                    if section == 1:
                        volTot = np.sum(self.tableData[:,1])
                        #print(str(volTot))
                        return (self.assetColHeaders[section] + " = " + str(volTot))
                    else:
                        return self.assetColHeaders[section]

                else:
                    return None
            elif  orientation == Qt.Vertical:
                return None

    def data(self, index, role):
        #
        if role == Qt.BackgroundRole: # Background of the item (QBrush)
            return self.bg

        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            datItem = str(self.tableData[row,col])
            return datItem

        if role == Qt.TextAlignmentRole: # TOOLTIP!
                    return Qt.AlignRight

        if role == Qt.DecorationRole:
            #print(self.sessMan.uc2_accHndlr.accFOC)
            if index.column() == 2:
                if str(self.tableData[index.row(), 2 ]) == self.sessMan.uc2_accHndlr.accFOC: # .data['account']:
                    return self.icon1


    def clear(self):
        self.beginResetModel()
        self.tableData = np.zeros((0,5))
        self.tableData = self.tableData.astype(dtype='uint64')
        self.endResetModel()


    def insertRow( self, position, newOrd = [], parent = QModelIndex()):
        self.beginInsertRows(  QModelIndex(), position , position   )
        self.tableData = np.vstack((     self.tableData[:position,:], newOrd, self.tableData[position:,:]  ))
        self.endInsertRows() # MUST CALL when finished! this emits special inbuilt signals
        return True

    def setData(self):
        pass
    def insertRows(self):
        pass
    def removeRows(self):
        pass
    def sort(self):# unused atm
        sortCol = 2
        self.tableData[self.tableData[:,sortCol].argsort(axis=0)]
        # this sorts in the MODEL!
        # -> emit LAYOUTCHNGED!!!
        # !
        # I dont need insertRows and COls

        # logic: how do I know if Orders ahve been removed?
        # difficult: removed by cancel: I can check TXs
        # removed by trade: I dont get a notifcation,
        # escept when I look for trades and cancle the orders in the trades explicitly
        #
# index where to insert into arry
#         tt2
# Out[122]:
# array([[ 1,  9,  9,  9],
#        [ 2,  5,  9,  4],
#        [ 5,  9,  8,  6],
#        [ 7,  8,  2,  1],
#        [ 8,  4,  1,  4],
#        [ 8,  8,  6,  6],
#        [ 9,  2,  1,  2],
#        [10,  4,  6, 10]])
#
# np.searchsorted(tt2[:,0],6)
# Out[123]: 3
#

        #  replace elements from  ANYWHERE!!
        #
        # for row in range(newDat.shape[0]):
        #                 for col in range(newDat.shape[1]):
        #                     #self.tablemodel.tableData[row][col] = str(newDat[row][col])
        #                     self.tablemodel.tableData[row,col] = newDat[row,col]
        #                     qi1=self.tablemodel.createIndex(row,col,self)
        #                     self.tablemodel.data(qi1   ,Qt.DisplayRole) #qvs)
        #                     self.tablemodel.dataChanged.emit(qi1 ,qi1  )#  ,qvs)





class TradesQMod(QAbstractTableModel):
    """- we can collect ALL data in the tableData, and then return what wwant in the data and row methods!  
    """


    def __init__(self, sessMan, parent = None):
        super(TradesQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = np.zeros((0,3), dtype='uint64')
        self.tradesColHeaders =   ['price','qty',  'time',  ] #headers
        self.sessMan = sessMan
        icon1Col = QColor(150,124,10,250)
        self.bg =  QColor(10,124,245,40)
        pixmap = QPixmap(16,16)
        pixmap.fill(icon1Col)
        self.icon1 = QIcon(pixmap)



        #
        # trades :[{} ]
        # trade['block']   # '10755359623412779102'
        # trade['priceNQT']   # '1111111'
        # trade['quantityQNT']   # '2'
        # trade['bidOrder']   # '14845380811716379448'
        # trade['asset']   # '13294423783048908944'
        # trade['askOrder']   # '11096233899859162613'
        # trade['timestamp']   # 14171075
        #


    def flags(self, index):
        return  Qt.ItemIsEnabled |  Qt.ItemIsSelectable

    def rowCount(self, parent):
        return( self.tableData.shape[0])

    def columnCount(self, parent ):
        return 3


    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < 3:   #self.tableData.shape[1]:

                    if section == 1:
                        volTot = np.sum(self.tableData[:,1])
                        #print(str(volTot))
                        return (self.tradesColHeaders[section] + " = " + str(volTot))
                    else:
                        return self.tradesColHeaders[section]


                    return self.tradesColHeaders[section]
                else:
                    return None
            elif  orientation == Qt.Vertical:
                return None

    def data(self, index, role):

        if role == Qt.BackgroundRole: # Background of the item (QBrush)
            return self.bg
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            datItem = str(self.tableData[row,col])
            return datItem
        if role == Qt.TextAlignmentRole: # TOOLTIP!
            return Qt.AlignRight

        if role == Qt.DecorationRole: # TOOLTIP!
            #print(self.sessMan.uc2_accHndlr.accFOC)
            pass
            #return None



    def clear(self):
        # e.mit
        self.beginResetModel()
        self.tableData = np.zeros((0,3))
        self.tableData = self.tableData.astype(dtype='uint64')
        self.endResetModel()

    def insertRow( self, position, newTrade = [], parent = QModelIndex()):
        self.beginInsertRows(  QModelIndex(), position , position   )
        #print(str(newTrade))
        #self.tableData = np.vstack( (     newTrade, self.tableData ))
        self.tableData = np.vstack( (   self.tableData, newTrade ))

        self.endInsertRows() # MUST CALL when finished! this emits special inbuilt signals
        return True

    def setData(self):
        pass
    def insertRows(self):
        pass
    def removeRows(self):
        pass
    def sort(self):# unused atm
        sortCol=0
        self.tableData[self.tableData[:,sortCol].argsort(axis=0)]
        # this sorts in the MODEL!







class AccAssetsQMod(QAbstractTableModel):

    def __init__(self, sessMan,   parent = None):
        super(AccAssetsQMod, self).__init__( parent = None)
        self.tableData = []
        self.accAssetColHeaders = ['AssetId', 'BalanceQNT','BalUnconf']
        #self.accAssetColHeaders =   ['name','assetId','qtyTot','accQty','accQtyU','numTrd','dec','Issuer','description'] #headers decimals


    def flags(self, index):
        return  Qt.ItemIsEnabled |  Qt.ItemIsSelectable

    def rowCount(self, parent):
        return( len(self.tableData  ) )

    def columnCount(self,  parent = None ):
        return 3 #

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < 3 :
                    return  self.accAssetColHeaders[section]
                else:
                    return("NA!")
            elif  orientation == Qt.Vertical:
                return None #"myCol " + str(section)

    def data(self, index, role):
        if role== Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.tableData[row][column]
            return self.tableData[row][column]


    def clear(self):

        self.beginResetModel()


        self.tableData =  []
        self.endResetModel()


    def insertRow(self):
        pass

    def appendRow( self, position, newRow = [], parent = QModelIndex()):
        self.beginInsertRows(  QModelIndex(), position , position   )
        self.tableData.append( newRow  )
        self.endInsertRows() # MUST CALL when finished! this emits special inbuilt signals
        return True

    def removeRow(self, position  , parent= QModelIndex()): #parent is only for hierRCH EG TREEVIEWS
        self.beginRemoveRows( QModelIndex(), position ,position   ) # must be done!
        value = self.tableData[position]
        self.tableData.remove(value)     # a LIST operation!
        self.endRemoveRows()
        return True



class AssetsQMod(QAbstractTableModel):

    def __init__(self, sessMan,   parent = None):
        super(AssetsQMod, self).__init__( parent = None)
        self.tableData =   []
        self.assetColHeaders =   ['assetId' ,'name','qtyTot','numTrd','dec','Issuer'] #,'description']

    def clear(self):

        self.beginResetModel()
        self.tableData =  []
        self.endResetModel()


    def flags(self, index):
        return  Qt.ItemIsEnabled |  Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled#  | Qt.ItemIsEditable

    def rowCount(self, parent):
        return( len(self.tableData ) )

    def columnCount(self, parent = None ):
        return 6 # 7

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < 6 : #len(self.tableData) +1:
                    return  self.assetColHeaders[section] #"Palette"  # QString("Palette") !!!!
                else:
                    return("NA!")
            elif  orientation == Qt.Vertical:
                return None

    # the data method is called for every index and for every role!!
    # by the view - this is a classical callback is in shader programming
    def data(self, index, role):
        if role== Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.tableData[row][column]#.name()
            return self.tableData[row][column]#.name() #value.name() # "hardcoded" #pass

    def appendRow( self, position, newRow = [], parent = QModelIndex()): # QModelIndex() only for hierarch data, hence empty here
        self.beginInsertRows(  QModelIndex(), position , position   )
        #self.tableData.insert(position, newRow  )
        self.tableData.append(newRow  )
        #
        # ll=[[]]
        # ins=[1,2,3]
        # ll.insert(0,ins) ==  [[1, 2, 3], []] <- this is the reason why using INSERT can't handle an empty list at init:
        # insert shifts the empty list back, and the view can't handle that because it expects the
        #self.tableData.insert(position, newRow  )
        self.endInsertRows() # MUST CALL when finished! this emits special inbuilt signals
        return True


    def removeRow(self, position  , parent= QModelIndex()): #parent is only for hierRCH EG TREEVIEWS
        self.beginRemoveRows( QModelIndex(), position ,position   ) # must be done!
        value = self.tableData[position]
        self.tableData.remove(value)     # a LIST operation!
        self.endRemoveRows()
        return True
        # If your subclassing a QAbstractTableModel you should insert a setData() function for external change of data.
        # In this function use the begin/endInsertRow option. When done emit the signal rowsInserted() and rowsremoved(index). Where ofcourse the index is the position in the table that was altered.




class SimpleListQMod(QAbstractTableModel):

    def __init__(self, sessMan, numRows, headerName,   parent = None):
        super(SimpleListQMod, self).__init__( parent = None)
        self.listData =  dq(numRows * ['0']) #numRows * ['0'] #
        self.header =  headerName
        self.numRows = numRows

    def rowCount(self, parent = None):
        return self.numRows
    def columnCount(self,parent = None):
        return 1

    def data(self, index, role):
         if role== Qt.DisplayRole:
            row = index.row()
            value = self.listData[row]
            return value
    def header(self, section, orientation, role):
         if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < 1 : #len(self.tableData) +1:
                    return  self.header
                else:
                    return("NA!")
            elif  orientation == Qt.Vertical:
                return None
    def enterItem(self, position, item):
        #print(str(position))
        #print(str(item))
        self.beginInsertRows(  QModelIndex(),0 ,0   )
        self.listData.rotate()
        self.listData[0] = item
        self.endInsertRows()












class TXsQMod(QAbstractTableModel):
    """ this TableModel is for colelcting, processing and displying TXs. """


    def __init__(self,    parent = None):
        super(TXsQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers


    def flags(self, index):
        return  Qt.ItemIsEnabled |  Qt.ItemIsSelectable


    def rowCount(self, parent):
        return( len(self.tableData) )#[1]))

    def columnCount(self, tableData):
        return( len(self.tableData[0]))

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation ==   Qt.Horizontal:
                if section < 5 : #len(self.tableData) +1:
                    return  self.assetColHeaders[section] #"Palette"  # QString("Palette") !!!!
                else:
                    return("NA!")
            elif  orientation == Qt.Vertical:
                return None #"myCol " + str(section)

    def data(self, index, role):
        if role== Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.tableData[row][column]#.name()
            return self.tableData[row][column]#.name() #value.name() # "hardcoded" #pass

    def insertRow( self, position, newRow = [], parent = QModelIndex()):
        self.beginInsertRows(  QModelIndex(), position , position   )
        self.tableData.insert(position, newRow  )
        self.endInsertRows() # MUST CALL when finished! this emits special inbuilt signals
        return True


    def removeRow(self, position  , parent= QModelIndex()): #parent is only for hierRCH EG TREEVIEWS
        self.beginRemoveRows( QModelIndex(), position ,position   ) # must be done!
        value = self.tableData[position]
        self.tableData.remove(value)     # a LIST operation!
        self.endRemoveRows()
        return True


    def TX_def(self,): # NOTE:
        TXtypes_0=  {
                    'description': 'Payment',
                     'subtypes': [{'description': 'Ordinary payment', 'value': 0}],
                      'value': 0}

        TXtypes_1 = {
                    'description': 'Messaging',
                    'subtypes': [
                                    {'description': 'Arbitrary message', 'value': 0},
                                    {'description': 'Alias assignment', 'value': 1},
                                    {'description': 'Poll creation', 'value': 2},
                                    {'description': 'Vote casting', 'value': 3}
                                  ],
                     'value': 1
                     }


        TXtypes_2=  {
                        'description': 'Colored coins',
                         'subtypes': [
                                         {'description': 'Asset issuance', 'value': 0},
                                         {'description': 'Asset transfer', 'value': 1},
                              {'description': 'Ask order placement', 'value': 2},
                              {'description': 'Bid order placement', 'value': 3},
                              {'description': 'Ask order cancellation', 'value': 4},
                              {'description': 'Bid order cancellation', 'value': 5}],
                         'value': 2
                         }




        TX_reply = {
              'type': 0,
             'signature': '0ad771d192d18d69f41c07d63685d5594af27afca9f78c4e13b8d61983c64d0f641da5f3f9fd5d203ede6e69717ea9916212beb5e9fd3db4d743f7da442d4fb4',
             'timestamp': 6258939,
             'recipient': '1674414626317090683',
             'block': '15791765164354846927',
             'subtype': 0,
             'amount': 1000,
             'confirmations': 21482,
             'sender': '8905175434161782261',
             'referencedTransaction': '0',
             'deadline': 1440,
             'senderPublicKey': '5697806f72e17ac8ad8603a35df8108f24c87d0c5232d3af0de6f7e7bccf6256',
             'fee': 1
                     }

        t2st3_placebidOrder=     """
                            block - 14745529278103137367
            deadline - 10
            sender - 1738404304940813414
            attachment - {'price': 499, 'asset': '2952478044871531870', 'quantity': 10}
            amount - 0
            type - 2
            referencedTransaction - 0
            confirmations - 1512
            recipient - 1739068987193023818
            timestamp - 8027972
            fee - 1
            subtype - 3
            senderPublicKey - 5f7605dfd9ddba1c7843add87f2afc0b9edb1776ad9ae7c9cce18013fa892471
            signature - 43754df8a723dc724b4fcd1bdaa46e11a22d3ea7d5edab9280e2ef4ce5c95e0cd8c01e0b00fde275d1f334d69f029ecc9e4f54896535e0562922552708ffc172
                    """
        t2st0_issueAsset_attachment = {'quantity': 1347, 'name': 'UniGots', 'description': 'pink' }

        t2st1_transferAsset_attachment = {'asset': '16739598998421896224', 'quantity': 13}
        t2st4_cancelAskOrder_attachment = {'order': '16804729641686889636'}



        t1st0_message_attachment = {'message': 'ffff000000000000000000000000000000000aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
        t1st1_assignAlias_attachment = {'alias': 'xxxxxxxxxxTEST', 'uri': 'www.www.www'}

class AcctsQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(AcctsQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class MXfersQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(MXfersQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class MSGsQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(MSGsQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class BlocksQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(BlocksQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class PeersQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(PeersQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class PollsQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(PollsQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers

class AliasQMod(QAbstractTableModel):

    def __init__(self,    parent = None):
        super(AliasQMod, self).__init__( parent = None)
        #self.assetArray= np.random.random((5,2)).tolist()
        self.tableData = [['0'  ,]]
        self.assetColHeaders =   [' ',] #headers








#    ###############
#    ###############
#    ###############  Qt Models fin
#    ###############        
#    ############### nxt utility models start
#         
#

#
#
# NXT nonTX models
#
#




class nxtMeta(QObject):
    """-"""

    apiCalls = nxtQs() #

    def __init__(self, nxtApiReq_toSend ={}, nxtApiSlot={}   ):
        super(nxtMeta, self).__init__()
        self.apiReq_toSend = nxtApiReq_toSend
        self.nxtApiSlot = nxtApiSlot
    # in case we need many of these - we can still make a class
    # override atm
    def poll1Start(self):
        self.timer1.start(self.time1)
    def poll1Stop(self):
        self.timer1.stop()
    def poll1Single(self, meta = {}):
        self.nxtApiSlot(self.nxtApi, self.apiReq_toSend,self.meta)
    def poll1_CB(self):
        self.checkConditions = True # !! do it here

class Amount(nxtMeta):

    def __init__(self, Nqt):#
        """
        amount is a TUPLE! of ints, NqtS are only Nqt after decimal, and NxtS are only FullNxt
       """
        super(Amount, self).__init__()
        self.NqtRaw = Nqt
        self.amountIntNqt = int(Nqt)
        self.amount = divmod(self.amountIntNqt,100000000) # easy
        self.Nqt = self.amount[1]
        self.Nxt = self.amount[0]
        self.NqtS = str(self.Nqt)
        self.NxtS = str(self.Nxt)
        self.numNqtDigs = len(self.NqtS)
        if self.numNqtDigs < 8: # for display
            self.NqtS = (8-self.numNqtDigs) * '0' + self.NqtS # padding for display

    def checkAmount(self):
        pass



class NRSconn(nxtMeta):
    """ -"""

    NRSconnCHANGED_Sig = pyqtSignal(object) # always last
    connErr_Sig= pyqtSignal(object, object) # always last

    def __init__(self, sessMan, nxxApi,  newComp = {}, logger1=None):#
        """
        create the resident user data here. NRSconn can connect to all other PEERS also!!!
        we need an inital HOST:PORT, but then we can query lost of other PEERS with reqs and see the diffs
       """
        super(NRSconn, self).__init__()
        self.sessMan = sessMan
        self.consLogger = logger1

        self.nxtApi = nxxApi # multiple APIs with diff conns!
        self.timer1 = QTimer()
        self.time1 = 35000
        self.apiReq_getPeers = self.apiCalls.getPeers
        self.apiReq_getPeer = self.apiCalls.getPeer
        #
        self.hallmark = Hallmark()
        self.peers = []  # getPeers and other things for status check CONN HEALTH
        self.comp = {}
        self.comp['protocoll'] = 'http://'
        self.comp['server'] = newComp['host']
        self.comp['port'] =  newComp['port']
        self.comp['serverAddr'] = self.comp['protocoll'] + self.comp['server'] + ":"+self.comp['port']
        self.comp['url'] = self.comp['serverAddr'] + "/nxt?"

        self.state = State(self,self.nxtApi, self.consLogger)
        self.block = Block(self,self.nxtApi, self.consLogger)

        self.consLogger.info('NRSconn init: %s ', str(self) )
        self.consLogger.info('NRSconn init - comp["url"]: %s ', str(self.comp['url']) )

        self.init_Sigs()


    def init_Sigs(self):

        QObject.connect(self.nxtApi, SIGNAL("getPeers_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getPeers_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getPeer_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getPeer_fromApi)
        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.poll1_CB)

    def poll1Start(self,meta):
        self.meta = meta
        self.timer1.start(self.time1)
        self.poll1Single(meta)
    def poll1Stop(self):
        self.timer1.stop()
    def poll1Single(self, meta = {}):
        meta['caller']='NRSconn - getPeers Timer'
        self.nxtApi.getPeers_Slot( self.apiReq_getPeers, meta)

    def poll1_CB(self):
        if True:
            self.poll1Single()

    def getPeers_fromApi(self, reply, meta):
        try:
            self.peers = reply['peers']
        except:
            if 'apiError' in reply.keys():
                self.emit( SIGNAL( "connErr_Sig(PyQt_PyObject,PyQt_PyObject )"), reply, meta )
            else:
                print("uncaught err:  " + str(reply))
        try:
            self.peer = self.peers[0]

        except Exception as inst:
            print(str(inst))

        apiReq_getPeer = self.apiCalls.getPeer
        apiReq_getPeer['peer'] = self.peer
        meta['caller']='NRSconn - getPeer'
        self.nxtApi.getPeer_Slot(self.apiReq_getPeer, meta ) #apiReq_getPeer, meta)

    def getPeer_fromApi(self,peer, meta):
        pass





class Accounts(nxtMeta):

    """ - the  are here, the
    VIEWS for Qt are created and connected where they appear! """




    def __init__(self, sessMan,    ):
        """
        a collector for Account
       """
        super(Accounts, self).__init__()
        self.sessMan = sessMan
        self.accountsDi = {} # pandas table or some kind of dataFrame!
        self.acctsQtM = AcctsQMod()





class Account(nxtMeta): #11
    """
 ---


-"""


    getAccountUpdate_Sig  = pyqtSignal(object, object) #

    def __init__(self, uc2_accountHandler,  sessMan, secretPhrase='0', accID =  '16159101027034403504'   ):
        """
        account instances are always made by the uc2_accountHandler !!!
       """
        super(Account, self).__init__()

        self.sessMan = sessMan
        self.nxtApi = self.sessMan.nxtApi

        self.timer1 = QTimer()
        self.time1 = 30000

        self.apiReq_getAccount = self.apiCalls.getAccount
        self.apiReq_getAccountId = self.apiCalls.getAccountId
        self.apiReq_startForging = self.apiCalls.startForging
        self.apiReq_stopForging = self.apiCalls.stopForging
        self.apiReq_getForging = self.apiCalls.getForging

        self.balance = Amount('0')
        self.balanceU = Amount('0')
        self.balanceEff = 0

        self.forgeDeadline = '0'
        self.forgeRem = '0'


        # use a dict for info container, because the haskey and other dict functions are useful is usefule
        self.data = {}
        self.data['pubKey'] = '0'
        self.data['account'] = accID #'0'

        self.data['secretPhrase'] = secretPhrase
        self.data['accountAssets'] = [] # not sure yet
        self.accountAssets = {}
        self.data['name'] = ''
        self.data['description'] = ''
        self.init_Sigs()


# this can collect all the tings that belong to account - aliases, msgs, asserts, orders pubkey, polls
    def init_Sigs(self):
        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.poll1_CB)
        QObject.connect(self.nxtApi, SIGNAL("getAccount_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAccount_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("getAccountId_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAccountId_fromApi)
        QObject.connect(self.sessMan, SIGNAL("TX_sendMoney_Sig(PyQt_PyObject, PyQt_PyObject)"), self.UC4_TX_sendMoney_CB )
        QObject.connect(self.nxtApi, SIGNAL("getForging_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getForging_fromApi) # all in 1
        QObject.connect(self.nxtApi, SIGNAL("startForging_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getForging_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("stopForging_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getForging_fromApi)


    def poll1Start(self, meta):
        self.meta = meta
        self.timer1.start(self.time1)
        self.poll1Single(meta)

    def poll1_Stop(self):
        self.timer1.stop()

    def poll1Single(self, meta = {}):
        self.apiReq_getAccount['account'] = self.data['account']
        meta['caller']='Account - getAccount'

        self.apiReq_getForging['secretPhrase']  = self.data['secretPhrase']
        #print("call 1+"+str(self.apiReq_getForging))
        # woulkd be enoguh to enter this ONCE only when ACCT is changed!!!!!!
        self.nxtApi.getForging_Slot( self.apiReq_getForging , meta)

        self.nxtApi.getAccount_Slot( self.apiReq_getAccount , meta)

    def poll1_CB(self,  ):
        self.poll1Single(self.meta)

    #def fetchAccountId(self, meta={}):
    def getAccountId(self, meta={}):

        self.apiReq_getAccountId['secretPhrase'] = self.data['secretPhrase']
        self.nxtApi.getAccountId_Slot( self.apiReq_getAccountId , meta)

    def UC4_TX_sendMoney_CB(self, TX, meta):
        self.TXs[TX.crypt1['transaction']] = TX


    def startForging(self):
        print("F ON3")

        self.apiReq_startForging['secretPhrase']  = self.data['secretPhrase']
        self.nxtApi.getAccountId_Slot( self.apiReq_startForging , self.meta)

    def stopForging(self):
        print("F OFF3")
        self.apiReq_stopForging['secretPhrase']  = self.data['secretPhrase']
        self.nxtApi.getAccountId_Slot( self.apiReq_stopForging , self.meta)


        #
        #
        # def stopForging_fromApi(self,reply, meta):
        #     print('stopForging_fromApi')
        #     for k in reply:
        #         print( k + " - " + str(reply[k])  + " - " + str(type(reply[k])))
        #     print(str(meta))
        #
        #     pass
        #
        # def startForging_fromApi(self,reply, meta):
        #     print('startForging_fromApi')
        #
        #     for k in reply:
        #         print( k + " - " + str(reply[k])  + " - " + str(type(reply[k])))
        #     print(str(meta))
        #
        #     pass


    def getForging_fromApi(self,reply, meta):
            # print('getForging_fromApi')
            # for k in reply:
            #     print( k + " - " + str(reply[k])  + " - " + str(type(reply[k])))
            # print(str(meta))




        try:
            self.forgeDeadline = str(reply['deadline'])
            try:
                self.forgeRem = str(reply['remaining'])
            except:
                self.forgeRem = 'started'

        except:
            self.forgeDeadline = 'not Forging'
            self.forgeRem = '0'


        """
            getF - wrong
            errorCode - 5
            errorDescription - Account is not forging

            errorCode - 5
            errorDescription - Account is not forging

            getF good
            remaining - 11430
            deadline - 11454


            startF
            deadline - 13776

            stopF
            foundAndStopped - True
            """





    def getAccountId_fromApi(self, reply, meta):
        #print("getAccountId_fromApi2") #
        for k in reply:
            print( k + " - " + str(reply[k])  + " - " + str(type(reply[k])))
        #print(str(meta))

        try:
            self.data['account'] = reply['accountId']
            self.poll1Single(meta)
        except Exception as inst:
                print(str(inst))
                print("unsepcific account error: "  + str(reply)  )
            # cou=1
            # for k in reply:
            #     print(str(cou) + " - " + k + " - " + str(reply[k])  + " - " + str(type(reply[k])))
            #     cou+=1
            # print(str(meta))

    def getAccount_fromApi(self, reply, meta):


        try:
            self.balance = Amount(reply['balanceNQT'])
            self.balanceU = Amount(reply['unconfirmedBalanceNQT'])
            self.balanceEff = reply['effectiveBalanceNXT']
            try:
                self.publicKey = reply['publicKey']
            except:
                self.publicKey = 'account has no pubKey'
        except:
            try:

                self.balance = Amount(reply['balanceNQT']) # Amount(0)
                self.balanceU = Amount(reply['unconfirmedBalanceNQT']) # Amount(0)
                self.balanceEff = reply['effectiveBalanceNXT'] # 0
                self.publicKey = reply['errorDescription']
                #print(self.publicKey)

            except Exception as inst:
                self.balance.Nqt = '0'
                self.balance.Nxt = '0'

                self.balanceU.Nqt = '0'
                self.balanceU.Nxt = '0'

                self.balanceEff = '0'
                self.publicKey = '0'
                self.name = 'unknown'
                self.description = 'undescript'
                # use premade ZEROACCT obj here
                #print(str(inst))
                #print("unsepcific account error "  + str(reply))

        try:
            self.name = reply['name']
            #print('NAME:' + self.name + "<<-")
        except:
            self.name = 'unknown'
        try:
            self.description = reply['description']
        except:
            self.description = 'undescript' #reply['description']pass # make nice later




        meta['activeAccount'] = self # this WHOLE instance is in meta now and can be used wherever we catch that signal!
        self.emit( SIGNAL( "getAccountUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta )
        pass


    def leaseBalance(self):

        #47
        self.leaseBalance= {
                                        "requestType" : "leaseBalance" , \
                                        "referencedTransaction" : "",\
                                        "publicKey":"",\
                                        "secretPhrase" : "0", \
                                        "deadline" : "DEADLINE",\
                                        "feeNQT" : "100000000" ,\
                                        "recipient" : "" ,\
                                        "period" : "1440"
                                         }
    def foldingHasaBug(self):
        pass




#  STOP nxtGate.py !!!!!!
#  kill -9 `ps x | grep nxtGate.py | grep -v grep | awk '{print $1}'`



class xGateCustomer(object): #nxtMeta):
    """- careful when passing in the 'SIDW' designators for this and other side!"""
    def __init__(self, sessMan, AccId, sideThis, sideOther, ucID ):
        #super(xGateCustomer   , self   ).__init__(sessMan)

        self.sessMan = sessMan
        # other side can make multiple trades, ie can be returning customer even for the same DEAL!

        self.accountThis = AccId
        self.accountOther = '0' # <- will be filled when XFER comes in for red.
        # take care of the perspectives here: ACCT this issued the BIDORDER
        # accountOther is where the coins will be sent to
        # this holds for BOTH sides, that can become confusing but it is correct!
        # accountThis is the account that has to send back the tokens, also on the 'Other' side of the xGate

        self.UC32_ID = ucID
        #self.BOs = [ ]
        self.BOIDs = [ ]
        self.BOdict = { }
        self.this = sideThis # NXT or NFD'this' # or 'other'
        self.other =sideOther
        self.direction =  self.this +'_to_' + self.other #for INITIATOR, self.other+'_to_' + self.this  for xParties!
        self.redeemableTokens = 0
        self.redeemedTokens = 0
        self.Xfers = {} # here we collect the redemption TXs






class XGAccount(nxtMeta): #11
    """
    XGAccount does 5 tests on timers and notifies UC logic of the results
    """
        #
        # prepLogger = ''
        # for k in self.__dict__:
        #     pass#prepLogger+= ('\n'+ str(k)+'::'+str(self.__dict__[k]))

    getAccountUpdate_Sig  = pyqtSignal(object, object) #
    checkBidOrders_Sig  = pyqtSignal(object, object) #
    checkOneBidOrder_CB =  pyqtSignal(object, object) #

    checkXfers_Sig   = pyqtSignal(object, object) #
    checkTrades_Sig  = pyqtSignal(object, object) #
    checkMSGs_Sig  = pyqtSignal(object, object) #

    def __init__(self,  sessMan, xGate_IDs ):
        """
        account instances are always made by the   !!!
       """
        super(XGAccount, self).__init__()

        self.sessMan = sessMan

        self.publicKey = ''  #these are fix for the accounts!
        self.balance = Amount('0')
        self.balanceU = Amount('0')
        self.balanceEff = '0'
        self.xGateTKinAcc = '0' # stock of dedicated token in acct
        self.xGateTKinAccUconf = '0' # stock of dedicated token in acct
        self.name = '0'
        self.description = '0'
        self.blockTime = '0'
        self.NRSTime = '0'

        self.xGate_IDs = xGate_IDs
        self.xGate_thisSide = xGate_IDs[0]
        self.xGate_otherSide = xGate_IDs[1]
        self.xGassetID = xGate_IDs[2]
        self.xGateAccNumNXX = xGate_IDs[3]
        self.xGateAccSecNXX = xGate_IDs[4]
        self.accLogger = xGate_IDs[5]

        # sessMan   has BOTH APIs !! sessMan has TWO API instances!!!! one to nfd one to nxt
        # make the NRSconn pertinent to this acct known here
        if self.xGate_thisSide == 'NXT':
            self.nxxApi = self.sessMan.nxtApi  # make the apiSigs instance here!
            self.connNxx = self.sessMan.connNXT
            self.connNxx.state.poll1Single({'singlePoll':'fomAcctInit'})
            self.blockTime = self.connNxx.block.block['timestamp']

        elif self.xGate_thisSide == 'NFD':
            self.nxxApi = self.sessMan.nfdApi  # make the apiSigs instance here!
            self.connNxx = self.sessMan.connNFD
            self.connNxx.state.poll1Single({'singlePoll':'fromAcctInit'})
            self.blockTime = self.connNxx.block.block['timestamp']

        else:
            print(30*"\nRAISE EXCEPTION" + str(self.__dict__))
        # this is to be able for the TX object to use the proper connectino object
        self.meta = {'xGateAcct':self.xGate_thisSide}
        self.meta['issuer'] = 'accountModel'
        self.meta['purpose'] = 'regularAccPoll'

        self.timer1 = QTimer()
        self.time1 = 35000     # the UC31 IS DRIVEN BY THIS

        # NOTABENE: to access the current state, for some rason we MUST use the full connNxx object!
        #self.connNxx.state.data['time']
        #self.connNxx.state.data <---- use this to access the current State!!!

        # NB: apiCalls is ONE dict that is a class dict. we MUST make copies for use here or we only have ONE
        # REQ object and will overwrite the permanet parms that are reserved for the differnet objects
        self.apiReq_getAccount = copy(self.apiCalls.getAccount)
        self.apiReq_getAccountTransactionIds = copy(self.apiCalls.getAccountTransactionIds)
        self.apiReq_getTransaction = copy(self.apiCalls.getTransaction)
        self.apiReq_getBidOrder = copy(self.apiCalls.getBidOrder) # need that for finding the issuer of a trade
        self.apiReq_getBidOrders = copy(self.apiCalls.getBidOrders)
        self.apiReq_placeAskOrder = copy(self.apiCalls.placeAskOrder)
        self.apiReq_getTrades = copy(self.apiCalls.getTrades)
        self.apiReq_getTime = copy(self.apiCalls.getTime)
        # these call params never change
        self.meta['queriedAssetID']= self.xGassetID
        self.apiReq_getAccountTransactionIds['account'] = self.xGateAccNumNXX # this never changes for this UC
        self.apiReq_getAccount['account'] = self.xGateAccNumNXX # self.data['account'] # this never changes for this UC
        self.apiReq_getBidOrders['asset'] = self.xGassetID
        self.apiReq_getTrades['asset'] = self.xGassetID
        self.apiReq_getTrades['firstIndex'] = ''

        numBOsForBooky = ''#1 # BOs die when the yre filled. at least they are not returned from getBOs any more
        numTradesForBooky = 4      # more later

        self.apiReq_getTrades['lastIndex'] = numTradesForBooky # last 50 - CHECK!! trades is zero based, BOs not !!!!!
        self.apiReq_getBidOrders['limit'] = numBOsForBooky # can make longer when running- but is unlikely to be too short,
        self.iniTime = self.connNxx.state.data['time']

        prepLogger =''
        for key in self.__dict__:
            prepLogger += (key + ": " + str(self.__dict__[key]) )

        self.accLogger.info('create acct object %s - ', prepLogger)
        self.sessMan.consLogger.info('create acct object %s -', prepLogger)


        self.init_Sigs()
        self.poll1Single()

    def init_Sigs(self):
        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.poll1_CB)
        # each account talks to ONE nxxApi instance ONLY! that is either NXT OR NFD
        # the correct one is put into this namespace at init
        QObject.connect(self.nxxApi, SIGNAL("getAccount_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAccount_fromApi)
        QObject.connect(self.nxxApi, SIGNAL("getAccountTransactionIds_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getAccountTransactionIds_fromApi)
        QObject.connect(self.nxxApi, SIGNAL("getTransaction_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTransaction_fromApi)
        QObject.connect(self.nxxApi, SIGNAL("getTrades_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTrades_fromApi)
        QObject.connect(self.nxxApi, SIGNAL("getBidOrders_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getBidOrders_fromApi)
        QObject.connect(self.connNxx.block , SIGNAL("newBlock_Sig(PyQt_PyObject, PyQt_PyObject)"), self.newBlock_fromBlock)
        QObject.connect(self.nxxApi, SIGNAL("getTime_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTime_fromApi)

    def getTime_fromApi(self, reply, meta): # 1
        self.NRSTime = reply['time']
        #self.sessMan.consLogger.info('Acct:  - NRSTime %s  t2  %s  ', str(self.NRSTime) ,    str(self.connNxx.state.data['time']))

    def getBCTime(self):
        self.nxxApi.getTime_Slot( self.apiReq_getTime , self.meta) # 1

    def pollTestStart(self, ):# meta):
        self.sessMan.consLogger.info('START timer  pollTestStart Acct %s', self.xGate_thisSide)
        self.timerTest.start(self.timeTest)
    def pollTest_CB(self,  ):
        self.pollTestSingle() #self.meta) timer for other activites
    def pollTest_Stop(self):
        self.timeTest.stop()
    def pollTestSingle(self):
        self.sessMan.consLogger.info('pollTestSingle %s', self.xGate_thisSide)
        pass

    def poll1Start(self, ):# meta):
        self.accLogger.info('START timer regular account poll from UC31 %s', self.xGate_thisSide)
        self.timer1.start(self.time1)
    def poll1_CB(self,  ):
        self.poll1Single() #self.meta)
    def poll1_Stop(self):
        self.timer1.stop()

    def poll1Single(self, ): #meta = {}): self.NRSTime
        self.sessMan.consLogger.info('Acct:  %s - blockTime %s chainTime %s  ', self.xGate_thisSide ,  self.blockTime, str(self.NRSTime) )
        #self.sessMan.consLogger.info('Acct:  %s - blockTime %s chainTime %s  ', self.xGate_thisSide ,  self.blockTime, self.connNxx.state.data['time'])
        #self.accLogger.info('timer regular account poll %s', self.xGate_thisSide)
        self.nxxApi.getTime_Slot( self.apiReq_getTime , self.meta) # 1
        self.nxxApi.getAccount_Slot( self.apiReq_getAccount , self.meta)
        self.nxxApi.getBidOrders_Slot( self.apiReq_getBidOrders, self.meta) # 2
        self.apiReq_getAccountTransactionIds['timestamp'] = str(int(self.NRSTime)-6000) # or since launch
        # make more elegant later - just always look past 10 minutes for now 10 secs from before the last blocktime
        self.apiReq_getAccountTransactionIds['type'] = '2' # XFERS
        self.apiReq_getAccountTransactionIds['subtype'] = '1' # XFERS
        self.nxxApi.getAccountTransactionIds_Slot( self.apiReq_getAccountTransactionIds , self.meta)  # 4
        self.nxxApi.getTrades_Slot( self.apiReq_getTrades, self.meta)  # 4
        #self.apiReq_getAccountTransactionIds['type'] = '1' # MSG
        #self.apiReq_getAccountTransactionIds['subtype'] = '0' # MSG

    def getTrades_fromApi(self, reply, meta): # 4
        """-"""
        self.emit( SIGNAL( "checkTrades_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta )

    def newBlock_fromBlock(self, reply, meta):
        self.block = reply
        self.metaBlock = meta
        self.blockTime =  (self.block['timestamp']) #
        self.sessMan.consLogger.info('newBlock_fromBlock %s - %s - %s ', self.xGate_thisSide ,  self.blockTime, self.block['height']   )


    def getAccountTransactionIds_fromApi(self, reply, meta): # 3  # this is triggered for each new block

        #self.sessMan.consLogger.info('getTXs - accObj   %s  %s %s  ', self.xGate_thisSide , str(reply), str(meta))

        if 'transactionIds' in reply:
            TXs = reply['transactionIds']
        elif 'errorCode' in reply:
            #self.sessMan.consLogger.info('  XFER errorCode  %s  %s %s  ', self.xGate_thisSide , str(reply), str(meta))
            #self.sessMan.xGateLogger.info(' XFER errorCode  %s  %s %s  ', self.xGate_thisSide , str(reply), str(meta))
            TXs=[] # good! this drops old Xfers! tested!
        else:
            self.sessMan.consLogger.info('UNSPECIFIC TX ERROR %s  %s %s  ', self.xGate_thisSide , str(reply), str(meta))
            self.sessMan.xGateLogger.info('UNSPECIFIC TX ERROR %s  %s %s  ', self.xGate_thisSide , str(reply), str(meta))
            TXs=[]
        for TX in TXs:
            self.apiReq_getTransaction['transaction'] = TX
            meta = {'xGateAcct':self.xGate_thisSide}
            #meta['caller'] = 'acctChecksBlockChainTXs'
            self.nxxApi.getTransaction_Slot( self.apiReq_getTransaction, meta) # 2
 
    def getTransaction_fromApi(self, reply, meta): # 3 a
        #self.sessMan.consLogger.info('\n\n\n\n#####+++***~~~\ngetTransaction_fromApi:  %s from %s   ',str(reply), str(meta) )

        try:

            if (reply['type'] == 1 and reply['subtype']== 0 ):
             #       if 'attachment' in reply.keys(): # check for type and subType!
                MSG = reply['attachment']
                metaThis=copy(meta)
                metaThis['signalType']= 'MSG'
                message = MSG['message']
                self.sessMan.consLogger.debug('new MSG on %s  %s %s  ', self.xGate_thisSide , str('MSG:'), str(message[:10]))
                self.emit( SIGNAL( "checkMSGs_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, metaThis )

            elif (reply['type'] == 2 and reply['subtype'] == 3 ):
                BO = reply['attachment'] # maybe get in some check for the specific BOs
                metaThis=copy(meta)
                metaThis['signalType']= 'BO_TX'
                #print(30*"~~~~~~~~~~ is it with type 3 and subtype3??")
                self.sessMan.consLogger.debug('fetch BO on %s  %s %s  ', self.xGate_thisSide , str(reply), str(metaThis))
                self.emit( SIGNAL( "checkOneBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, metaThis )

            elif (reply['type'] == 2 and reply['subtype'] == 1 ):
                xfer = reply['attachment']
                asset = xfer['asset']

                # HERE WE CAN DO THE CONFCHECK ALREADY!!!!!!

                if asset == self.xGassetID:
                    metaThis=copy(meta)
                    metaThis['signalType']= 'XFER'
                    metaThis['NRStype']=self.xGate_thisSide
                    self.sessMan.consLogger.debug('new XFER on %s  %s %s  ', self.xGate_thisSide , str(xfer), str(asset))
                    self.emit( SIGNAL( "checkXfers_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, metaThis )

        except Exception as inst:
            self.sessMan.consLogger.info('UC32  unspec TX:  %s from %s  %s  ',str(reply), str(meta), str(inst) )


    def getBidOrders_fromApi(self, reply, meta): # 2 a
        """-"""
        meta=copy(meta)
        meta['xGateSide'] = self.xGate_thisSide
        #self.sessMan.consLogger.info('getBidOrders_fromApi %s', str(reply))
        self.emit( SIGNAL("checkBidOrders_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta )


    def fetchTransaction(self, BOID, meta): # call them 'fecthxyz' when we access from elsewhere to discern from the auton methods
        #print( 10*"FETCHBO___2" ,"\n" , BOID, "\n", str(meta) )
        self.apiReq_getTransaction['transaction'] = BOID
        self.nxxApi.getTransaction_Slot( self.apiReq_getTransaction, meta) # 2


    def fetch_getAccount(self, accountToCheck, meta):
        """ fetch_getAccount is used to query api on demand from other objects using teh acct as proxy"""
        apiReq_getAccount = {"requestType" : "getAccount" , "account" :accountToCheck }
        self.nxxApi.getAccount_Slot( apiReq_getAccount , meta)

    def getAccount_fromApi(self, reply, meta):

        if "errorDescription" in reply.keys():
            self.sessMan.xGateLogger.info("\ngetAccount_fromApi ERROR -accountToCheck: \n%s \n%s ", str(reply),  str(meta)) # OK!! ACCT CHECK FAILED!!! FOR OTHER

        if ('issuer' in meta.keys() and  meta['issuer'] == 'accountModel'):
        #meta['purpose'] == 'regularAccPoll'
            #print("regular............................................removePrintAagin")
            try:
                self.balance = Amount(reply['guaranteedBalanceNQT'])
                self.balanceU = Amount(reply['unconfirmedBalanceNQT'])
                self.balanceEff = reply['effectiveBalanceNXT']
            except:
                self.accLogger.info("acc error---------->? %s  " + str(reply) )

            try:
                for asset in reply['assetBalances']:
                    if asset['asset'] == self.xGassetID:
                        #self.accLogger.info("assetBalances %s  " , str(asset) )
                        self.xGateTKinAcc = asset['balanceQNT']

                for asset in reply['unconfirmedAssetBalances']:
                    if asset['asset'] == self.xGassetID:
                        #self.accLogger.info("assetBalances %s  " , str(asset) )
                        self.xGateTKinAccUconf = asset['unconfirmedBalanceQNT']
                #self.accLogger.info("account here:: %s NRSTime: %s blockTime %s  ", str(self.xGate_IDs[0:4]),  str(self.NRSTime),  str(self.blockTime) )
                #self.accLogger.info("xGSide, %s, BalNQT, %s, ucBalNQT, %s, TokBal, %s, ucTokBal, %s", str(self.xGate_IDs[0]), self.balance.NqtRaw , self.balanceU.NqtRaw ,  self.xGateTKinAcc , self.xGateTKinAccUconf )
                return None # this may have been a problem


            except Exception as inst:
                self.sessMan.xGateLogger.info("getAccount_fromApi checking error---------->? %s \n meta: %s \n%s " , str(reply), str(meta) , str(inst))
                meta['ERROR'] = str(reply) #{'errorDescription': 'Incorrect "account"', 'errorCode': 4}
                self.emit( SIGNAL("getAccountUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta )
                return None


        elif ('issuer' in meta.keys() and  meta['issuer'] == 'UC32'):
            self.sessMan.xGateLogger.info("getAccount_fromApi UC32 verify acct %s \n meta: %s  s " , str(reply), str(meta) )
            #if meta['purpose'] == 'verifyThatAcctHasPubkey':
            self.emit( SIGNAL("getAccountUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"), reply, meta )
            return None


        return None

#
# {
#     "errorCode": 4,
#     "errorDescription": "Incorrect \"account\""
# }

# getAccount on NFD ok:
#
# {
#     "publicKey": "58be6060e13815503922acc3f0a9d4524f71b09b4d4a4a7c247907e4432af44c",
#     "assetBalances": [
#         {
#             "asset": "7334941058708816895",
#             "balanceQNT": "671"
#         }
#     ],
#     "guaranteedBalanceNQT": "911898999985",
#     "balanceNQT": "423681898999985",
#     "accountRS": "NFD-EC9N-X49V-8YXM-8RFT7",
#     "unconfirmedAssetBalances": [
#         {
#             "unconfirmedBalanceQNT": "671",
#             "asset": "7334941058708816895"
#         }
#     ],
#     "account": "7126304194855053556",
#     "effectiveBalanceNXT": 9118,
#     "unconfirmedBalanceNQT": "423681898999985",
#     "forgedBalanceNQT": "0"
# }

        # remember DIFF between 1.1.6 and 1.2.0
        # getAccount_fromApi - MOD accountToCheck:
        # getAccount_fromApi - MOD accountToCheck:  {'forgedBalanceNQT': '0', 'balanceNQT': '607112101000015', 'assetBalances': [{'asset': '7334941058708816895', 'balanceQNT': '999999284'}], 'account': '16159101027034403504', 'effectiveBalanceNXT': 4472404, 'guaranteedBalanceNQT': '447240401000000', 'publicKey': 'f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825', 'unconfirmedBalanceNQT': '607112101000015', 'accountRS': 'NFD-L6PJ-SMZ2-5TDB-GA7J2', 'unconfirmedAssetBalances': [{'asset': '7334941058708816895', 'unconfirmedBalanceQNT': '999999284'}]} {'queriedAssetID': '7334941058708816895', 'qqLen': 2, 'xGateAcct': 'NFD'}

        # getAccount_fromApi - MOD accountToCheck:
        # getAccount_fromApi - MOD accountToCheck:  {'forgedBalanceNQT': '503400000000', 'balanceNQT': '4183986983392', 'name': 'name1', 'publicKey': '10eb3c8cb67b4898e2993b1b463448f4f018939022c13892d682073a511ffa4a', 'description': 'description1', 'unconfirmedAssetBalances': [{'asset': '13294423783048908944', 'unconfirmedBalanceQNT': '45'}, {'asset': '13309267173964952697', 'unconfirmedBalanceQNT': '1200'}, {'asset': '13388701969217905199', 'unconfirmedBalanceQNT': '39'}, {'asset': '14576994730285238779', 'unconfirmedBalanceQNT': '4999141802'}, {'asset': '7476479172898689702', 'unconfirmedBalanceQNT': '5000000000'}], 'assetBalances': [{'asset': '13294423783048908944', 'balanceQNT': '45'}, {'asset': '13309267173964952697', 'balanceQNT': '1200'}, {'asset': '13388701969217905199', 'balanceQNT': '39'}, {'asset': '14576994730285238779', 'balanceQNT': '4999141802'}, {'asset': '7476479172898689702', 'balanceQNT': '5000000000'}], 'account': '2865886802744497404', 'effectiveBalanceNXT': 38171, 'guaranteedBalanceNQT': '3817136981180', 'unconfirmedBalanceNQT': '4183986983392', 'accountRS': 'NXT-3P9W-VMQ3-9DRR-4EFKH'} {'queriedAssetID': '14576994730285238779', 'qqLen': 7, 'xGateAcct': 'NXT'}
        #




















class Blocks(nxtMeta):

    def __init__(self, NRSconn):#
        """
        create the resident user data here.  dedicated Block class
       """
        super(Blocks, self).__init__()

        self.nxtApi = NRSconn.sessMan.nxtApi
        self.NRSconn = NRSconn
        future = "this can become a collector class for blockchain traversal and analysis, with a different architecture than the TX collector classes "






class Block(nxtMeta): #7
    """ -""" 

    blockUpdate_Sig = pyqtSignal(object,object)
    newTXs_Sig = pyqtSignal(object,object)
    # can also have the sessMan emit this - BUT- as long as block is single, no prob

    def __init__(self,  NRSconn, nxxApi, logger1=None):#
        """ 
         dedicated Block class . special Block subclasses can be made from this.
         for special TX checks
       """        
        super(Block, self).__init__()

        # maybe it is even better to give ctrl of the GETBLOCK to this block obj itself?

        self.nxtApi = nxxApi #NRSconn.sessMan.nxtApi
        self.NRSconn = NRSconn
        self.consLogger = logger1
        self.timer1 = QTimer()
        self.time1 = 50000
        self.apiReq_getBlock = self.apiCalls.getBlock

        self.block = {} #data
        self.block['version'] = ''
        self.block['baseTarget'] =''
        self.block['nextBlock'] = ''
        self.block['totalAmount'] = ''
        self.block['payloadHash'] = ''
        self.block['blockSignature'] = ''
        self.block['previousBlockHash'] =''
        self.block['totalFee'] = ''
        self.block['generationSignature'] = ''
        self.block['payloadLength'] = ''
        self.block['transactions'] = []
        self.block['generator'] = ''
        self.block['timestamp'] = '0'
        self.block['previousBlock'] = ''
        self.block['numberOfTransactions'] = ''
        self.block['height'] = ''
        self.prevBlockTime = 0
        self.init_Sigs()

    def init_Sigs(self):
        #from API
        QObject.connect(self.nxtApi, SIGNAL("getBlock_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getBlock_fromApi)
        # from State object
        QObject.connect(self.NRSconn.state, SIGNAL("fetchBlock_Sig(PyQt_PyObject, PyQt_PyObject)"),  self.fetchBlock_CB)

    def fetchBlock_CB(self,reply, meta, ):
        self.apiReq_getBlock['block'] = meta['lastBlock']
        self.nxtApi.getBlock_Slot( self.apiReq_getBlock, meta)

    def getBlock_fromApi(self, reply, meta):
        self.prevBlockTime = self.block['timestamp'] # this will assume waiting for TWO blocks to have both inited... can do other later
        self.block = reply
        meta['caller']='blockIsNewBlock'
        self.consLogger.info('block here. fetched new block @ height %s', self.block['height'])
        self.emit( SIGNAL( "newBlock_Sig(PyQt_PyObject, PyQt_PyObject)"), self.block, meta )    #
        #
        # if reply['transactions'] != []:
        #     newTXs = reply['transactions'] #   []
        #     self.lastBlockTime = reply['timestamp']
        #     for newTX in reply['transactions']:
        #         pass
        #     #self.emit( SIGNAL( "newTXs_Sig(PyQt_PyObject, PyQt_PyObject)"), newTXs, meta )    #

        ########## this can be subclassed for more specific TX checks!!!!





class State(nxtMeta):

    stateUpdate_Sig = pyqtSignal(object, object)
    fetchBlock_Sig =  pyqtSignal(object,object )

    def __init__(self, NRSconn , nxxApi, logger1=None):
        """ - """
        super(State, self).__init__()

        self.NRSconn = NRSconn
        self.nxtApi = nxxApi

        self.consLogger = logger1
        self.timer1 = QTimer()
        self.time1 = 45000

        self.apiReq_getState = self.apiCalls.getState
        self.apiReq_getBlock = self.apiCalls.getBlock #TEMP

        self.currentBlockAddr = '0'
        self.currentBlockHeight = '0'

        # 21 !!!
        self.data = {}
        self.data['lastBlock'] = "0" #
        self.data['numberOfPeers'] = "0" #
        self.data['numberOfAssets'] = "0" #
        self.data['numberOfAccounts'] = "0" #
        self.data['numberOfBlocks'] = "0" #
        self.data['numberOfAliases'] = "0" #
        self.data['numberOfOrders'] = "0" #
        self.data['numberOfTransactions'] = "0" #
        self.data['cumulativeDifficulty'] = "0" #
        self.data['lastBlockchainFeeder'] = "0" #
        self.data['maxMemory'] = "0" #
        self.data['time'] = "0" #
        self.data['version'] = "0" #
        self.data['totalMemory'] = "0" #
        self.data['totalEffectiveBalanceNXT'] = "0" #
        self.data['availableProcessors'] = "0" #
        self.data['numberOfUnlockedAccounts']  = "0" #
        self.data['numberOfPolls']  = "0" #
        self.data['numberOfVotes']  = "0" #
        self.data['numberOfTrades']  = "0" #
        self.data['freeMemory']  = "0" #
        self.meta = {'caller':'state'}
        self.init_Sigs()


    def init_Sigs(self):
        QObject.connect(self.nxtApi, SIGNAL("getState_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getState_fromApi)
        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.poll1_CB)


    def poll1Start(self,meta):
        self.meta = meta
        self.timer1.start(self.time1)
        self.poll1Single(meta)

    def poll1Stop(self):
        self.timer1.stop()

    def poll1Single(self, meta):
        #self.consLogger.info('State - getState - : %s ', str(self) )
        meta['caller']='State - getState'
        self.nxtApi.getState_Slot(  self.apiReq_getState , meta)

    def poll1_CB(self, ): # no meta from Timer!
        self.poll1Single(self.meta)

    @pyqtSlot( )
    def getState_fromApi(self, reply, meta):
        self.data = reply # dump the whole new state into here!
        #self.consLogger.info('State - getState  %s ', str(self.data) ) # (30*'\n#############' +str(self.data)) )
        self.emit( SIGNAL( "stateUpdate_Sig(PyQt_PyObject, PyQt_PyObject)"), self.data, self.meta )
        fetchBlock = (  self.currentBlockAddr != self.data['lastBlock'] )

        numberOfBlocks = self.data['numberOfBlocks']
        self.consLogger.info('state here. version %s has numBlocks %s', self.data['version'],  (numberOfBlocks ) )

        if fetchBlock:
            self.consLogger.info('state here.Fetch new Block!  %s ', numberOfBlocks )
            self.currentBlockAddr = self.data['lastBlock']
            meta['lastBlock'] = self.currentBlockAddr
            self.emit( SIGNAL( "fetchBlock_Sig(PyQt_PyObject,PyQt_PyObject )"),reply, meta )






class Peer(nxtMeta): #8
    """ -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan, query={}, data={} ):#
        """
        create the resident user data here.  dedicated Peer class
       """
        super(Peer, self).__init__()
        self.sessMan = sessMan

        self.data = data
        self.query = query
        self.query['PEERNAME']  =  '0'
        self.data =  {
                         "platform":       "PLATFORM",\
                         "application":       "NRS",\
                         "weight":       0,\
                         "hallmark":       "HALLMARK",\
                         "state":       0,\
                         "announcedAddress":       "ANNOUNCED",\
                         "downloadedVolume":       0,\
                         "version":       "VERSION",\
                         "uploadedVolume":       0
                    }

        correctdata=   """
            platform - nxt.now.im
            application - NRS
            weight - 0
            announcedAddress - node9.mynxtcoin.org
            uploadedVolume - 215245
            version - 0.9.5e
            blacklisted - False
            downloadedVolume - 158990
            shareAddress - True
            state - 1
            """



       # TX classes:

class Peers(nxtMeta): #8
    """ -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan,  ):#
        """
        create the resident user data here.  dedicated Peer class
       """
        super(Peers, self).__init__()
        self.sessMan = sessMan

class Hallmark(nxtMeta): #10
    """ -""" 
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, ) 
    
    def __init__(self,  query={}, data={} ):#
        """ 
        create the resident user data here.   
       """        
        super(Hallmark, self).__init__()
        #self.sessMan = sessMan
        
        self.data = data
        self.query = query
        self.query['hallmark'] = 'HEXSTRING'
        self.data['valid'] = '0'    # VALID,
        self.data['"weight'] = '0'  #   WEIGHT,
        self.data['host'] = '0'     #  "HOSTIP",
        self.data['account'] = '0'  #   "ACCOUNT",
        self.data['date'] = '0'     # "DATE"    '2014-02-01' #



class Trades(nxtMeta): #2
    """   no TX_type  -"""
    TradeResponse_Sig = pyqtSignal(dict) # always last
    TradeResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan,   ):#
        """
        create the resident user data here.  dedicated Trade class
       """
        super(Trades, self).__init__()
        self.sessMan = sessMan
        self.tradesQtM = TradesQMod(sessMan)
        self.tradesDi = {}


    def enterTrade(self,):
        #get single trade from UC, enter single
        pass

    def enterTrades(self, reply, meta):
        trades = reply['trades']

        self.tradesQtM.clear()
        for trade in trades:
            tr_Price = np.uint64(trade['priceNQT'])
            tr_Vol = np.uint64(trade['quantityQNT'])
            tr_time = np.uint64(trade['timestamp'])
            newTrade = np.array([tr_Price, tr_Vol, tr_time], dtype='uint64')
            self.tradesQtM.insertRow(0, newTrade)




class Assets(nxtMeta): #1
    """ no TX_type -"""

    def __init__(self, sessMan,  ):#
        """
        create the resident user data here.  dedicated Assets class
        These collector classes also house the QModels for possible widgets

       """
        super(Assets, self,).__init__()
        self.sessMan = sessMan

        self.assetsDi = {} # pandas table or some kind of dataFrame!
        self.allAssetsQtM = AssetsQMod(sessMan)
        # so far this is a container for the QMOdel and a custom asset collections
        self.assetsAccDi = {}
        self.accAssetsQtM = AccAssetsQMod(sessMan)



    def enterAllAssetsTable(self, reply, meta):
        """
                # name - <class 'str'>
                # account - <class 'str'>
                # quantityQNT - <class 'str'>
                # numberOfTrades - <class 'int'>
                # decimals - <class 'int'>
                # asset - <class 'str'>
                # description - <class 'str'>
        """
        # unwrap and enter into local model
        #14136559604731496960

        assetList= reply['assets']
        for asset in assetList:
            self.assetsDi['asset'] = asset
            # TEMP MANUAL EXCLUSION
            if str(asset['account'] ) == '14136559604731496960':
                continue
            if str(asset['account'] ) == '14386024746077933238':
                continue
            try:
                assetName = asset['name']
            except:
                assetName = 'name error'
            try:
                assetQTY = int(asset['quantityQNT'] ) #sys.maxsize -> 9223372036854775807 : 19 digits!
            except:
                assetQTY = 'QTY.error'
            try:
                assetId = int(asset['asset'] )
            except:
                assetId = 'Id error'
            try:
                assetTr = int(asset['numberOfTrades'] )
            except:
                assetTr = 'Tr error'
            try:
                assetDecimals = str(asset['decimals'] )
            except:
                assetDecimals = 'decimals error'
            try:
                assetIss = str(asset['account'] )
            except:
                assetIss = 'Issuer error'
            try:
                assetDesc = asset['description']
            except:
                assetDesc = 'undescript asset'

            newRow = [assetId, assetName, assetQTY, assetTr, assetDecimals, assetIss , assetDesc]

            self.allAssetsQtM.appendRow(0, newRow)



    def enterAccAssetsTable(self, reply, meta):
        """
                # name - <class 'str'>
                # account - <class 'str'>
                # quantityQNT - <class 'str'>
                # numberOfTrades - <class 'int'>
                # decimals - <class 'int'>
                # asset - <class 'str'>
                # description - <class 'str'>
        """ #
        # unwrap and enter into local model

        # check: this ASSUMES that the order of BAL nd BALUNCONF is IDENTICAL IN THE TWO LISTS!

        for a in range(len(reply['assetBalances'])):
            ass=reply['assetBalances'][a]
            assU=reply['unconfirmedAssetBalances'][a]
            aId = ass['asset']
            aB = int(ass['balanceQNT'])
            aBu = int(assU['unconfirmedBalanceQNT'])
            newRow = [aId, aB, aBu]


            #newRow = [0,assetBal, assetId,0,0,0,0,0,0]

            self.accAssetsQtM.appendRow(0, newRow)
#
# balanceNQT - 5553649895791
# unconfirmedAssetBalances - [{'asset': '13294423783048908944', 'unconfirmedBalanceQNT': '1349'}, {'asset': '13309267173964952697', 'unconfirmedBalanceQNT': '147'}, {'asset': '13388701969217905199', 'unconfirmedBalanceQNT': '987605'}]
# publicKey - f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825
# name - activeTes
# unconfirmedBalanceNQT - 5551649895791
# effectiveBalanceNXT - 55536
# description - shouldbactive
# assetBalances - [{'asset': '13294423783048908944', 'balanceQNT': '1349'}, {'asset': '13309267173964952697', 'balanceQNT': '147'}, {'asset': '13388701969217905199', 'balanceQNT': '987605'}]


# {'unconfirmedBalanceNQT': '5551649895791', 'effectiveBalanceNXT': 55536, 'description': 'shouldbactive',
#
# 'unconfirmedAssetBalances':[{'asset': '13294423783048908944', 'unconfirmedBalanceQNT': '1349'}, {'asset': '13309267173964952697', 'unconfirmedBalanceQNT': '147'}, {'asset': '13388701969217905199', 'unconfirmedBalanceQNT': '987605'}],
#
# 'balanceNQT': '5553649895791', 'publicKey': 'f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825',
#
# 'assetBalances': [{'asset': '13294423783048908944', 'balanceQNT': '1349'}, {'asset': '13309267173964952697', 'balanceQNT': '147'}, {'asset': '13388701969217905199', 'balanceQNT': '987605'}],
#  'name': 'activeTes'}

    def bug(self):
        pass



class Orders(nxtMeta): #3
    """    TX_type  -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )
    #
    #Order (placeBidOrder/placeAskOrder/CancelBidOrder/CancelAskOrder)
    def __init__(self, sessMan,    ):#
        """
        create the resident user data here.  dedicated Orderclass
       """
        super(Orders, self).__init__()
        self.sessMan = sessMan

        self.ordersBid_Di = {}
        self.ordersAsk_Di = {}

        self.ordersAsk_QtM = OrdersVerbQMod('A', sessMan)
        self.ordersBid_QtM = OrdersVerbQMod('B', sessMan)


        # just shortcut
        self.tdA=self.ordersAsk_QtM.tableData
        self.tdB=self.ordersBid_QtM.tableData

        # this sorts in the MODEL!
        # -> emit LAYOUTCHNGED!!!
        # !
        # I dont need insertRows and COls

        # logic: how do I know if Orders ahve been removed?
        # difficult: removed by cancel: I can check TXs
        # removed by trade: I dont get a notifcation,
        # escept when I look for trades and cancle the orders in the trades explicitly
        #
        # index where to insert into arry
        #         tt2
        # Out[122]:
        # array([[ 1,  9,  9,  9],
        #        [ 2,  5,  9,  4],
        #        [ 5,  9,  8,  6],
        #        [ 7,  8,  2,  1],
        #        [ 8,  4,  1,  4],
        #        [ 8,  8,  6,  6],
        #        [ 9,  2,  1,  2],
        #        [10,  4,  6, 10]])
        #
        # np.searchsorted(tt2[:,0],6)
        # Out[123]: 3
        #

        # ANYWHERE!!
        #
        # for row in range(newDat.shape[0]):
        #                 for col in range(newDat.shape[1]):
        #                     #self.tablemodel.tableData[row][col] = str(newDat[row][col])
        #                     self.tablemodel.tableData[row,col] = newDat[row,col]
        #                     qi1=self.tablemodel.createIndex(row,col,self)
        #                     self.tablemodel.data(qi1   ,Qt.DisplayRole) #qvs)
        #                     self.tablemodel.dataChanged.emit(qi1 ,qi1  )#  ,qvs)


        # tt=np.zeros((0,5))
        # tti=tt.astype(dtype='int64')
        # tt1=np.random.random_integers(1,10,(1,5))
        # np.vstack((tti,tt1))
        #
        #
        #

        #self.ordersBid_QtM.removeRow( 0, ) # 0 is the index?!
            # account - 1562462127635514638 - <class 'str'>
            # order - 17625438819289004411 - <class 'str'>
            # type - ask - <class 'str'>
            # asset - 4675055515217664932 - <class 'str'>
            # quantityQNT - 300000 - <class 'str'>
            # priceNQT - 100000000 - <class 'str'>
            # height - 78943 - <class 'int'>
            #

            #self.assetColHeaders =   ['price', 'qty',  'OIssuer','hght', 'OId']

            # some_dict.keys() & another_dict.keys()
            #
            # in Python 3.x. This returns the common keys of the two dictionaries as a set.
            #
            # This is also available in Python 2.7, using the method dict.viewkeys().
            #
            # As a closer match of the original code, you could also use a list comprehension:
            #
            # [key for key in some_dict if key in another_dict]
            #
            # An even closer match of original code would be to use dict.__contains__(), which is the magic method corresponding to the in operator:
            #
            # filter(another_dict.__contains__, some_dict.keys())

    def getBidOrder_uc6(self, reply, meta):
        #print("mod bid l386")
        newOrd = np.zeros((1,5), dtype='uint64')

        try:
            price = np.int64(reply['priceNQT'])
            newOrd[0,0] = price
        except Exception as inst:
            print(str(inst))
            return inst
        try:
            orderQTY = np.int64(reply['quantityQNT'])
            newOrd[0,1] = orderQTY
        except Exception as inst:
            print(str(inst))
            return inst
        try:
            oIssuer = np.uint64(reply['account'])

            newOrd[0,2] = oIssuer

        except Exception as inst:
            #print("oIss"+ str(inst))
            return inst
        try:
            oHght = np.uint64(reply['height'])
            newOrd[0,3] = oHght
        except Exception as inst:
            #print("oIss"+ str(inst))
            return inst


        try:
            oId = np.uint64(reply['order'])
            newOrd[0,4] = oId

        except Exception as inst:
            print("oId EXc" +str(inst))
            return inst

        inIndex =  np.searchsorted( self.ordersBid_QtM.tableData[:,0], newOrd[:,0]) #np.flipud

        inIndex = self.ordersBid_QtM.tableData.shape[0] - inIndex
        #print(str( self.ordersBid_QtM.tableData.shape[0]) + " - " + str(inIndex))

        #print(str(self.ordersBid_QtM.obSide) + " - " + str(inIndex))

        #print(str(self.ordersBid_QtM.tableData[:,0]) + " - " + str(newOrd[:,0]))

        self.ordersBid_QtM.insertRow( inIndex, newOrd)

        # self.tdB = np.vstack((     self.tdB[:inIndex,:], newOrd, self.tdB[inIndex:,:]  ))
        # self.ordersBid_QtM.layoutChanged.emit()
        # #
        # # qi1=self.tablemodel.createIndex(row,col,self)
        # self.tablemodel.data(qi1   ,Qt.DisplayRole) #qvs)
        # self.tablemodel.dataChanged.emit(qi1 ,qi1  )#  ,qvs)




    def getAskOrder_uc6(self, reply, meta):
        #print("mod ask l447")
        newOrd = np.zeros((1,5), dtype='uint64')
        try:
            price = np.int64(reply['priceNQT'])
            newOrd[0,0] = price
        except Exception as inst:
            print(str(inst))
            return inst
        try:
            orderQTY = np.int64(reply['quantityQNT'])
            newOrd[0,1] = orderQTY
        except Exception as inst:
            print(str(inst))
            return inst
        try:
            oIssuer = np.uint64(reply['account'])
            newOrd[0,2] = oIssuer
        except Exception as inst:
            #print("oIss"+ str(inst))
            return inst
        try:
            oHght = np.uint64(reply['height'])
            newOrd[0,3] = oHght
        except Exception as inst:
            #print("oIss"+ str(inst))
            return inst


        try:
            oId = np.uint64(reply['order'])
            newOrd[0,4] = oId

        except Exception as inst:
            print("oId EXc" +str(inst))
            return inst

        inIndex =  np.searchsorted(self.tdA[:,0], newOrd[:,0])
        #print(str(self.ordersAsk_QtM.obSide) + " - " + str(inIndex))

        self.ordersAsk_QtM.insertRow( inIndex, newOrd)






class Aliases(nxtMeta):
    """    TX_type  -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )
    #
    #Order (placeBidOrder/placeAskOrder/CancelBidOrder/CancelAskOrder)
    def __init__(self, sessMan,  ):#
        """
        create the resident user data here.  dedicated Orderclass
       """
        super(Aliases, self).__init__()

class MSGs(nxtMeta):
    """    TX_type  -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )
    #
    #Order (placeBidOrder/placeAskOrder/CancelBidOrder/CancelAskOrder)
    def __init__(self, sessMan,   ):#
        """
        create the resident user data here.  dedicated Orderclass
       """
        super(MSGs, self).__init__()

class Polls(nxtMeta):
    """    TX_type  -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )
    #
    #Order (placeBidOrder/placeAskOrder/CancelBidOrder/CancelAskOrder)
    def __init__(self, sessMan,   ):#
        """
        create the resident user data here.  dedicated Orderclass
       """
        super(Polls, self).__init__()

class Transfers(nxtMeta):
    """    TX_type  -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )
    #
    #Order (placeBidOrder/placeAskOrder/CancelBidOrder/CancelAskOrder)
    def __init__(self, sessMan,    ):#
        """
        create the resident user data here.  dedicated Orderclass
       """
        super(Transfers, self).__init__()

# non TX classes fin
###########




###################
#TX classes






####################
# TX classes


class TX(QObject):


    apiCalls = nxtQs()

    def __init__(self, sessMan, TX_ID, meta = {} ):#
        """
        Then, we have t query the TX_specs and the TX_bytes! ?From the TX itself autonomously?!

        two types of actions: for ALL and the issue TX that is differnet

       """
        super(TX, self).__init__()
        self.sessMan = sessMan

        self.meta = meta
        #print(12*"SUPER OF TX HERE")

        if 'xGateAcct' in meta.keys():

            if meta['xGateAcct'] == 'NXT':
                self.nxtApi = sessMan.nxtApi
                self.sessMan.consLogger.info('\n\nTX super: nxxAPI:%s  %s at: %s ', meta['xGateAcct'] ,str(self.nxtApi),str(self.nxtApi.sessUrl))

            elif meta['xGateAcct'] == 'NFD':
                self.nxtApi = sessMan.nfdApi
                self.sessMan.consLogger.info('\n\nTX super: nxxAPI:%s  %s at: %s ', meta['xGateAcct'] ,str(self.nxtApi),str(self.nxtApi.sessUrl))

            else:
                self.sessMan.consLogger.info('ERROR')

        else: # using ONE NRSconn and ONE api only!
            pass                              # later again for gnereal single api useself.nxtApi = sessMan.nxtApi

        self.timer1 = QTimer()
        self.time1 = 35000

        self.apiReq_getTransaction = self.apiCalls.getTransaction
        self.apiReq_getTransactionBytes = self.apiCalls.getTransactionBytes
        self.apiReq_parseTransaction = self.apiCalls.parseTransaction
        self.apiReq_signTransaction =  self.apiCalls.signTransaction
        self.apiReq_broadcastTransaction = self.apiCalls.broadcastTransaction

        # a TX has two embodiments:
        # 1
        # hash receipt
        # hash receipt signed
        # 2
        # blockchain presence w/o confirmations field
        # blockchain presence with 0 confirmations
        # blockchain presence with 1 or more confirmations
        self.meta=meta
        self.confirmations = 0 # cont['confirmations'] = '0'

        self.TX_from_API = {}
        self.TX_from_API['confirmations'] = '0' #- 0
        self.TX_from_API['attachment'] = '0' # - {'message': 'aaaaaa aaaaa'}
        self.TX_from_API['type'] = '0' #- 0
        self.TX_from_API['subtype'] = '0' #- 0
        self.TX_from_API['senderPublicKey'] = '0' #-
        self.TX_from_API['signatureHash'] = '0' #-
        self.TX_from_API['sender'] = '0' #-
        self.TX_from_API['fullHash'] = '0' #-
        self.TX_from_API['block'] = '0' #
        self.TX_from_API['amountNQT'] = '0' #-
        self.TX_from_API['blockTimestamp'] = '0' #-
        self.TX_from_API['deadline'] = '0' #-
        self.TX_from_API['signature'] = '0' #-
        self.TX_from_API['feeNQT']  = '0'#-
        self.TX_from_API['recipient'] = '0' #-
        self.TX_from_API['hash'] = '0' #-
        self.TX_from_API['transaction'] = '0' #-
        self.TX_from_API['referencedTransaction'] = '0' #- 0
        self.TX_from_API['timestamp'] = '0' #- 12970177

        self.TX_from_API['senderRS'] = '0' #  'NXT-C6L6-UQ5W-RBJK-AWDSJ'
        self.TX_from_API['recipientRS'] = '0' #-'NXT-2223-2222-KB8Y-22222'

        #
        self.crypt1={}
        self.crypt1['fullHash'] = '0'
        self.crypt1['transaction'] = '0'
        self.crypt1['transactionBytes'] = '0'
        self.crypt1['signatureHash'] = '0'
        self.crypt1['unsignedTransactionBytes'] = '0'
        self.crypt1['broadcasted'] = '0'
        self.crypt1['hash'] = '0'
        #
        self.crypt2={}
        self.crypt2['fullHash'] = '0' # same as 1!
        self.crypt2['transaction'] = '0'  # same as 1!
        self.crypt2['transactionBytes'] = '0' # same as 1!
        self.crypt2['signatureHash'] = '0'# same as 1!
        self.crypt2['verify'] = '0'

        QObject.connect(self.timer1, SIGNAL("timeout()"),  self.poll1_CB)
        QObject.connect(self.nxtApi, SIGNAL("getTX_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTX_fromApi)
        # keep reminder: for some reason, using self.sessMan.nxtAPI SOMETIMES DOES NOT CONNECT PROPERLY!
        # USE self.nxtApi!!!!
        QObject.connect(self.nxtApi, SIGNAL("getTransactionBytes_Sig(PyQt_PyObject, PyQt_PyObject)"), self.getTransactionBytes_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("parseTransaction_Sig(PyQt_PyObject, PyQt_PyObject)"), self.parseTransaction_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("signTransaction_Sig(PyQt_PyObject, PyQt_PyObject)"), self.signTransaction_fromApi)
        QObject.connect(self.nxtApi, SIGNAL("broadcastTransaction_Sig(PyQt_PyObject, PyQt_PyObject)"), self.broadcastTransaction_fromApi)

        if TX_ID == None: # client generated TX- when creating TXs ourself, we provide TXID=None!!!
            self.TX_direction = 'toBlockCH' # this means that this is a TX that has been sent by the client
            self.meta['caller'] = ['toBlockCH']
            self.sessMan.consLogger.info(' create new toBlockCH TX here: %s  %s   ', str(TX_ID), str(self.meta))

        else: # what we do here is providing TWO ways of TXs: one is fetching TXs form the blockchain, the other is to CREATE TXs
            self.TX_ID = TX_ID
            self.TX_direction = 'fromBlockCH' # if TX is FROM the blockchain to the client
            self.apiReq_getTransaction['transaction']  = TX_ID
            self.meta['caller'] = ['fromBlockCH']
            self.meta['TX_ID'] = TX_ID
            self.sessMan.consLogger.info('fetch TX specs from BC: %s  %s   ', self.TX_ID, str(self.meta))
            #self.nxtApi.getTransaction_Slot(  self.apiReq_getTransaction , self.meta)
            self.nxtApi.getTX_Slot(  self.apiReq_getTX , self.meta)

    # this is self-monitoring of the TX instance!!!
    def getTX_fromApi(self, reply, meta):
        # this is called EVERY time we query a TX from the API! Not only when creating it!
        self.TX_from_API = reply

        try:

            #if meta['TXtype'] =='uc32_cancelAskOrderOther':
                #print("TX poll itself:\n", str(reply),"\n", str(meta))

            if not 'confirmations' in reply.keys():
                return None
            #print("\nCONFS\nCONFS\nCONFS why am I twice?", str(self.TX_from_API) ,"\n", str(self.TX_from_API['confirmations']) ) #> 1 : #  MINCONFS
            if self.TX_from_API['confirmations'] > 1 :       #  MINCONFS
                #prepLogger = 'TX_found_itself_mature THIS SHOULD ONLY BE ONCE --TX_minConfsReached_Sig throw -confirmations] > 1 : #  MINCONFS--self.poll1_Stop---------->' + str(self.TX_from_API) #
                # GOOD:
                #2014-07-28 21:51:30,395 -   TX_found_itself_mature THIS SHOULD ONLY BE ONCE -----self.poll1_Stop---------->{'sender': '2865886802744497404', 'subtype': 2, 'signature': '4418e162be3f1e3de90d1e5ce18b013fb73c7725f2d0e4b0698285abc2e788012ebd3b77949b04f377ae9c2947714721fb4e4553d4bd5767f9b5f63aba16a775', 'recipient': '1739068987193023818', 'blockTimestamp': 21282532, 'timestamp': 21282443, 'signatureHash': 'eb84b7e3de8e69f9784ca9d73276e824e5e426d9e24eb5fbbcf649edb6bccdf2', 'senderPublicKey': '10eb3c8cb67b4898e2993b1b463448f4f018939022c13892d682073a511ffa4a', 'type': 2, 'recipientRS': 'NXT-MRCC-2YLS-8M54-3CMAJ', 'amountNQT': '0', 'attachment': {'priceNQT': '100000', 'asset': '14576994730285238779', 'quantityQNT': '110000'}, 'fullHash': 'c2577da8458ad847c73cbca0e48f39ae9a04a69f169289bcf188a6b0f81505fd', 'feeNQT': '100000000', 'block': '7742008896460240972', 'transaction': '5177039803446548418', 'confirmations': 2, 'deadline': 180, 'senderRS': 'NXT-3P9W-VMQ3-9DRR-4EFKH', 'height': 168432}
                #self.sessMan.consLogger.info('  %s    ', str(prepLogger))
                #print(15*"\nEMITTING TX_minConfsReached_Sig")
                self.sessMan.emit( SIGNAL( "TX_minConfsReached_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
                self.poll1_Stop() # but here we can set conditions as to when to stop the auto-checking!

        except Exception as inst:
            self.sessMan.consLogger.info('TX except %s %s ' ,  str(self.__dict__) , str(inst)    )
            self.sessMan.xGateLogger.info('TX except %s %s ',  str(self.__dict__) , str(inst )  )


    def getTransactionBytes_fromApi(self,   reply, meta):
        pass
    def parseTransaction_fromApi(self, reply, meta):
        pass
    def signTransaction_fromApi(self, reply, meta):
        pass
    def broadcastTransaction_fromApi(self,   reply, meta):
        pass

    def poll1_Start(self, meta):
        self.meta = meta
        self.timer1.start(self.time1)

    def poll1_Stop(self):
        self.timer1.stop()

    def poll1Single(self, meta = {}):
        try:

            #self.sessMan.consLogger.info('+++++>TX poll1_CB ITSELF: %s \n  %s \n %s ',   str(self.meta), str(self.TX_ID), str(self)  )

            self.apiReq_getTransaction['transaction'] = self.TX_ID
            self.sessMan.xGateLogger.info("meta %s",str(meta))

            self.nxtApi.getTX_Slot(self.apiReq_getTransaction, meta ) # this slot has been made extra for theTX itself!

        except Exception as inst:
            self.sessMan.consLogger.info('TX poll1_CB ITSELF ERROR %s\n -  %s %s   ', str(self.__dict__),   str(self.meta), str(self))

    def poll1_CB(self,  ):
        self.poll1Single(self.meta)




class SendMoney(TX): #2
    """   no TX_type  -"""

    # sessMan does tis! TX_sendMoney_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(SendMoney, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'sendMoney'
        self.apiReq_sendMoney = copy(self.apiCalls.sendMoney) # tricky
        self.apiTX_Slot = self.nxtApi.sendMoney_Slot # this is crucial to send to the correct API object here!
        self.init_TX_sendMoney_Sig_fromApi()

    def init_TX_sendMoney_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("sendMoney_Sig(PyQt_PyObject, PyQt_PyObject)"), self.sendMoney_fromApi)

    def sendMoney(self, ):
        self.apiReq_sendMoney['amountNQT'] = self.TXparms['amountNQT']
        self.apiReq_sendMoney['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_sendMoney['deadline'] = self.TXparms['deadline']
        self.apiReq_sendMoney['recipient'] = self.TXparms['recipient']
        self.apiReq_sendMoney['publicKey'] = '' #LATER
        self.apiReq_sendMoney['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_sendMoney['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_sendMoney['secretPhrase']  = self.TXparms['secretPhrase']

        self.sessMan.consLogger.info('PLACING SENDMONEY TX   %s '  ,  str(self.apiReq_sendMoney)    )

        self.apiTX_Slot(  self.apiReq_sendMoney , self.meta)

    def sendMoney_fromApi(self, crypt1, meta):
#self.sessMan.consLogger.info('  SENDMONEY TX   %s '  ,  str(crypt1)    )
        self.sessMan.xGateLogger.info('  SENDMONEY TX  %s \n %s ',  str(crypt1), str(meta)   )

        self.crypt1 = crypt1
        try:
            self.TX_ID = crypt1['transaction']
            self.poll1_Start(meta)
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR sendMoney_fromApi: %s  %s', str(inst), str(crypt1))
        # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!
        self.sessMan.consLogger.info('TX moneySent_RAW crypt1 %s ',  str(crypt1))
        self.sessMan.xGateLogger.info('TX moneySent_RAW %s ',  str(crypt1['transaction']))
        self.sessMan.emit( SIGNAL( "TX_sendMoney_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around




class SendMessage(TX):
    """
 -
    """

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """

        super(SendMessage, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'sendMessage'
        self.apiReq_sendMessage = copy(self.apiCalls.sendMessage)
        self.apiTX_Slot = self.nxtApi.sendMessage_Slot

        self.init_TX_sendMessage_Sig_fromApi()

    def init_TX_sendMessage_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("sendMessage_Sig(PyQt_PyObject, PyQt_PyObject)"), self.sendMessage_fromApi)


    def sendMessage(self, ):
        self.apiReq_sendMessage['recipient'] = self.TXparms['recipient']
        self.apiReq_sendMessage['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_sendMessage['deadline'] = self.TXparms['deadline']
        self.apiReq_sendMessage['publicKey'] = '' #LATER
        self.apiReq_sendMessage['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_sendMessage['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_sendMessage['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_sendMessage['message'] = self.TXparms['message']

        self.apiTX_Slot(  self.apiReq_sendMessage , self.meta)


    def sendMessage_fromApi(self, crypt1, meta):
        self.crypt1 = crypt1
        try:
            self.TX_ID = crypt1['transaction']
            self.sessMan.consLogger.info('sendMessage_fromApi %s    ', str(self.TX_ID) ) #),str(crypt1))
            self.poll1_Start(meta)
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR sendMessage_fromApi:   %s', str(inst))
        #self.sessMan.consLogger.info('TX sendMessage_RAW %s ',  str(crypt1))
        self.sessMan.emit( SIGNAL("TX_sendMessage_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around

        # ##### REMEMBER: the api returns json dicts, not the instances created here!
        # # hence, they must be handled eithrer here, or passed in the meta dict!!!




class PlaceAskOrder(TX): #2
    """   no TX_type  -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it
        """
        super(PlaceAskOrder, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'placeAskOrder'
        self.apiReq_placeAskOrder = copy(self.apiCalls.placeAskOrder)
        self.apiTX_Slot = self.nxtApi.placeAskOrder_Slot
        self.init_placeAskOrder_Sig_fromApi()
        # self.sessMan.consLogger.info('Priming ASK ORDER   %s '  ,  str(self.apiReq_placeAskOrder)    )

    def init_placeAskOrder_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("placeAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.placeAskOrder_fromApi)


    def placeAskOrder(self, ): # THIS USES ACCT HANDLER

        self.apiReq_placeAskOrder['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_placeAskOrder['deadline'] = self.TXparms['deadline']
        self.apiReq_placeAskOrder['publicKey'] = '' #LATER
        self.apiReq_placeAskOrder['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_placeAskOrder['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_placeAskOrder['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_placeAskOrder['asset'] = self.TXparms['asset']
        self.apiReq_placeAskOrder['priceNQT']  = self.TXparms['priceNQT']
        self.apiReq_placeAskOrder['quantityQNT']  = self.TXparms['quantityQNT']
        self.sessMan.consLogger.info('PLACING ASK ORDER   %s '  ,  str(self.apiReq_placeAskOrder)    )

        self.apiTX_Slot(  self.apiReq_placeAskOrder , self.meta)

    def placeAskOrder_fromApi(self, crypt1, meta):

        self.crypt1 = crypt1

        try:
            self.TX_ID = crypt1['transaction']
            #self.sessMan.consLogger.info('PLACED ASK ORDER%s  %s ',      str(self.TX_ID) ,str(crypt1))
            #self.sessMan.xGateLogger.info('PLACED ASK ORDER %s   %s ',   str(self.TX_ID) ,str(crypt1))

        except Exception as inst:

            prepLogger=''
            #for k in self.__dict__:
            #    prepLogger+= ('\n'+ str(k)+':'+str(self.__dict__[k]))
            self.__dict__['TXparms']['secretPhrase'] = 'xxxxxxxx'
            prepLogger+= ('\n'+ str('TXparms')+':'+str(self.__dict__['TXparms']))


            self.sessMan.xGateLogger.info('ERROR placeAskOrder_fromApi:%s %s \n\n %s  ', str(inst), str(crypt1), prepLogger  ) #

# 2014-08-08 08:54:02,299 - ERROR placeAskOrder_fromApi:'transaction' {'errorDescription': 'Incorrect "quantity" (must be in [1..100000000000000000] range)', 'errorCode': 4}
#
#
# sessMan:<nxtPwt.nxtSessionManager.nxtSessionManagerGate object at 0x7f6195a4c318>
# TXparms:{'feeNQT': '100000000', 'publicKey': '', 'referencedTransactionFullHash': '', 'quantityQNT': 0, 'broadcast': '', 'secretPhrase': 'dontWriteToLogFile', 'asset': '14576994730285238779', 'deadline': '180', 'priceNQT': '100000000000'}
# timer1:<PyQt4.QtCore.QTimer object at 0x7f6185064b88>
# apiReq_placeAskOrder:{'publicKey': '', 'asset': '14576994730285238779', 'feeNQT': '100000000', 'referencedTransaction': '', 'quantityQNT': 0, 'secretPhrase': '14oreosetc14oreosetc', 'requestType': 'placeAskOrder', 'deadline': '180', 'priceNQT': '100000000000'}

        self.sessMan.emit( SIGNAL( "TX_placeAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
        self.sessMan.xGateLogger.info('TX_placeAskOrder_Sig  %s %s', (meta['xGateAcct']),     str(crypt1['transaction']))
    # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!

        try:
            self.poll1_Start(meta)
            # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR placeAskOrder_fromApi:   %s', str(inst))

        #self.sessMan.consLogger.info('TX PLACED ASK ORDER   %s %s ',  (meta['xGateAcct']),    str(crypt1['transaction']))

        ##### REMEMBER: the api returns json dicts, not the instances created here!
        # hence, they must be handled eithrer here, or passed in the meta dict!!!





class CancelAskOrder(TX): #2
    """   no TX_type  -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(CancelAskOrder, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'cancelAskOrder'
        self.apiReq_cancelAskOrder = copy(self.apiCalls.cancelAskOrder)
        self.apiTX_Slot = self.nxtApi.cancelAskOrder_Slot
        self.init_cancelAskOrder_Sig_fromApi()

    def init_cancelAskOrder_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("cancelAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.cancelAskOrder_fromApi)



    def cancelAskOrder(self, ):
        self.apiReq_cancelAskOrder['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_cancelAskOrder['deadline'] = self.TXparms['deadline']
        self.apiReq_cancelAskOrder['publicKey'] = '' #LATER
        self.apiReq_cancelAskOrder['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_cancelAskOrder['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_cancelAskOrder['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_cancelAskOrder['order'] = self.TXparms['order']

        self.sessMan.consLogger.info(' cancelING ASK ORDER   %s '  ,  str(self.apiReq_cancelAskOrder)    )
        self.sessMan.xGateLogger.info('cancelING ASK ORDER    %s ',   str(self.apiReq_cancelAskOrder)   )


        self.apiTX_Slot(  self.apiReq_cancelAskOrder , self.meta)


    def cancelAskOrder_fromApi(self, crypt1, meta):

        self.crypt1 = crypt1

        self.sessMan.consLogger.info('----> cancelAskOrder_fromApi %s %s', str(crypt1), str(self))

        try:
            self.TX_ID = crypt1['transaction']
            #self.sessMan.consLogger.info('PLACED ASK ORDER%s  %s ',      str(self.TX_ID) ,str(crypt1))
            #self.sessMan.xGateLogger.info('PLACED ASK ORDER %s   %s ',   str(self.TX_ID) ,str(crypt1))

        except Exception as inst:

            prepLogger=''
            for k in self.__dict__:
                prepLogger+= ('\n'+ str(k)+':'+str(self.__dict__[k]))

            self.sessMan.xGateLogger.info('ERRORERRORERROR cancelAskOrder_fromApi:%s %s \n\n %s  ', str(inst), str(crypt1), prepLogger  ) #

        self.sessMan.emit( SIGNAL( "TX_cancelAskOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
            # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!

        try:
            self.poll1_Start(meta)
            # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR cancelAskOrder_fromApi:   %s', str(inst))

        #self.sessMan.consLogger.info('TX what is cancelAskOrder_fromApi here? cancelAskOrder_fromApi   %s ',      str(crypt1)) #['transaction']))
        #self.sessMan.xGateLogger.info('TX what is cancelAskOrder_fromApi here?cancelAskOrder_fromApi  %s ',      str(crypt1)) #['transaction']))


# maybe trying to cancel the ame one multiple times? the cancel DID WORK!!!!

        ##### REMEMBER: the api returns json dicts, not the instances created here!
        # hence, they must be handled eithrer here, or passed in the meta dict!!!

    #









class PlaceBidOrder(TX):
    """   no TX_type  -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(PlaceBidOrder, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'placeBidOrder'
        self.apiReq_placeBidOrder = copy(self.apiCalls.placeBidOrder)
        self.apiTX_Slot = self.nxtApi.placeBidOrder_Slot
        self.init_placeBidOrder_Sig_fromApi()
        # self.sessMan.consLogger.info('Priming Bid ORDER   %s '  ,  str(self.apiReq_placeBidOrder)    )

    def init_placeBidOrder_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("placeBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.placeBidOrder_fromApi)

    def placeBidOrder(self, ): # THIS USES ACCT HANDLER

        self.apiReq_placeBidOrder['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_placeBidOrder['deadline'] = self.TXparms['deadline']
        self.apiReq_placeBidOrder['publicKey'] = '' #LATER
        self.apiReq_placeBidOrder['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_placeBidOrder['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_placeBidOrder['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_placeBidOrder['asset'] = self.TXparms['asset']
        self.apiReq_placeBidOrder['priceNQT']  = self.TXparms['priceNQT']
        self.apiReq_placeBidOrder['quantityQNT']  = self.TXparms['quantityQNT']
        #self.sessMan.consLogger.info('PLACING Bid ORDER   %s '  ,  str(self.apiReq_placeBidOrder)    )
        #self.sessMan.xGateLogger.info('PLACING Bid ORDER    %s ',   str(self.apiReq_placeBidOrder) )
        self.apiTX_Slot(  self.apiReq_placeBidOrder , self.meta)

    def placeBidOrder_fromApi(self, crypt1, meta):

        self.crypt1 = crypt1

        try:
            self.TX_ID = crypt1['transaction']
            #self.sessMan.consLogger.info('PLACED Bid ORDER%s  %s ',      str(self.TX_ID) ,str(crypt1))
            #self.sessMan.xGateLogger.info('PLACED Bid ORDER %s   %s ',   str(self.TX_ID) ,str(crypt1))

        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR placeBidOrder_fromApi:   %s', str(inst))

        self.sessMan.emit( SIGNAL("TX_placeBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
            # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!
        try:
            self.poll1_Start(meta)
            # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR placeBidOrder_fromApi:   %s', str(inst))


        ##### REMEMBER: the api returns json dicts, not the instances created here!
        # hence, they must be handled eithrer here, or passed in the meta dict!!!





class CancelBidOrder(TX): #2
    """   no TX_type  -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(CancelBidOrder, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'cancelBidOrder'
        self.apiReq_cancelBidOrder = copy(self.apiCalls.cancelBidOrder)
        self.apiTX_Slot = self.nxtApi.cancelBidOrder_Slot
        self.init_cancelBidOrder_Sig_fromApi()

    def init_cancelBidOrder_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("cancelBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self.cancelBidOrder_fromApi)



    def cancelBidOrder(self, ):
        self.apiReq_cancelBidOrder['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_cancelBidOrder['deadline'] = self.TXparms['deadline']
        self.apiReq_cancelBidOrder['publicKey'] = '' #LATER
        self.apiReq_cancelBidOrder['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_cancelBidOrder['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_cancelBidOrder['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_cancelBidOrder['order'] = self.TXparms['order']
        self.apiTX_Slot(  self.apiReq_cancelBidOrder , self.meta)


    def cancelBidOrder_fromApi(self, crypt1, meta):

        self.crypt1 = crypt1

        try:
            self.TX_ID = crypt1['transaction']
            #self.sessMan.consLogger.info('PLACED Bid ORDER%s  %s ',      str(self.TX_ID) ,str(crypt1))
            #self.sessMan.xGateLogger.info('PLACED Bid ORDER %s   %s ',   str(self.TX_ID) ,str(crypt1))

        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR placeBidOrder_fromApi:   %s', str(inst))

        self.sessMan.emit( SIGNAL("TX_cancelBidOrder_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
            # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!
        try:
            self.poll1_Start(meta)
            # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR placeBidOrder_fromApi:   %s', str(inst))

        self.sessMan.consLogger.info('TX cancelBidOrder_fromApi  %s   %s ', str(3),  str(3))
        self.sessMan.xGateLogger.info('TX cancelBidOrder_fromApi  %s   %s ', str(3), str(3))


        ##### REMEMBER: the api returns json dicts, not the instances created here!
        # hence, they must be handled eithrer here, or passed in the meta dict!!!




class IssueAsset(TX):
    """
     #46
        self.issueAsset= {
                                        "requestType" : "issueAsset" , \
                                        "publicKey":"",\
                                        "referencedTransaction" : "",\
                                        "secretPhrase" : "SECRET" ,\
                                        "name" : "ASSETNAME", \
                                        "description" : "DESCRIPTION", \
                                        "quantityQNT" : "QTY" ,\
                                        "deadline" : "DEADLINE",\
                                        "decimals":"0",\
                                        "feeNQT" : "100000000"
                                         }

    """
    # sessMan does tis! TX_sendMoney_Sig = pyqtSignal(object, object) # each TX throws its nw recepit wignal

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(IssueAsset, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'issueAsset'
        self.apiReq_issueAsset = copy(self.apiCalls.issueAsset)
        self.apiTX_Slot = self.nxtApi.issueAsset_Slot
        self.init_TX_issue_Sig_fromApi()

    def init_TX_issue_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("issueAsset_Sig(PyQt_PyObject, PyQt_PyObject)"), self.issueAsset_fromApi)

    def issueAsset(self, ):
        self.apiReq_issueAsset['name'] = self.TXparms['name']
        self.apiReq_issueAsset['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_issueAsset['deadline'] = self.TXparms['deadline']
        self.apiReq_issueAsset['publicKey'] = '' #LATER
        self.apiReq_issueAsset['referencedTransaction']  = '' #LATER

        try:# THIS USES ACCT HANDLER
            self.apiReq_issueAsset['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_issueAsset['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_issueAsset['description']  = self.TXparms['description']
        self.apiReq_issueAsset['quantityQNT']  = self.TXparms['quantityQNT']
        self.apiReq_issueAsset['decimals']  = self.TXparms['decimals']
        self.apiTX_Slot(  self.apiReq_issueAsset , self.meta)


    def issueAsset_fromApi(self, crypt1, meta):
       self.crypt1 = crypt1

       try:
            self.TX_ID = crypt1['transaction']
           # self.sessMan.consLogger.info( 'TXissueAsset_fromApi %s   %s ',      str(self.TX_ID) , str(crypt1))
           # self.sessMan.xGateLogger.info('TXissueAsset_fromApi %s   %s ',      str(self.TX_ID) , str(crypt1))
       except Exception as inst:
           self.sessMan.xGateLogger.info('ERROR TXissueAsset_fromApi:   %s', str(inst))
           self.sessMan.emit( SIGNAL("TX_issueAsset_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
       try:
           self.poll1_Start(meta)
       except Exception as inst:
           self.sessMan.xGateLogger.info('ERROR TXissueAsset_fromApi:   %s', str(inst))
           self.sessMan.consLogger.info('TXissueAsset_fromApi    %s ', str(crypt1))
           self.sessMan.xGateLogger.info('TXissueAsset_fromApi    %s ', str(crypt1))

# ##### REMEMBER: the api returns json dicts, not the instances created here!
# # hence, they must be handled eithrer here, or passed in the meta dict!!!





class TransferAsset(TX):
    """
    #58
        self.transferAsset= {
                                        "requestType" : "transferAsset" , \
                                        "publicKey":"",\
                                        "secretPhrase" : "SECRET", \
                                        "recipient" : "" ,\
                                        "asset" : "ASSETID",\
                                        "quantityQNT" : "QTY" ,\
                                        "deadline" : "DEADLINE",\
                                        "comment" :"TX comment",\
                                        "referencedTransaction" : "",\
                                        "feeNQT" : "100000000"
                                         }

    """

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):#
        """
        special for each tX is its ISSUE slot and the params that go into it

       """

        super(TransferAsset, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'transferAsset'
        self.apiReq_transferAsset = copy(self.apiCalls.transferAsset)
        self.apiTX_Slot = self.nxtApi.transferAsset_Slot

        self.init_TX_transferAsset_Sig_fromApi()

    def init_TX_transferAsset_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("transferAsset_Sig(PyQt_PyObject, PyQt_PyObject)"), self.transferAsset_fromApi)


    def transferAsset(self, ):
        self.apiReq_transferAsset['recipient'] = self.TXparms['recipient']
        self.apiReq_transferAsset['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_transferAsset['deadline'] = self.TXparms['deadline']
        self.apiReq_transferAsset['publicKey'] = '' #LATER
        self.apiReq_transferAsset['referencedTransaction']  = '' #LATER
        try:# THIS USES ACCT HANDLER
            self.apiReq_transferAsset['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']
        except:# THIS USES ACCT HANDLER not
            self.apiReq_transferAsset['secretPhrase']  = self.TXparms['secretPhrase']
        self.apiReq_transferAsset['asset'] = self.TXparms['asset']
        self.apiReq_transferAsset['comment']  = self.TXparms['comment']
        self.apiReq_transferAsset['quantityQNT']  = self.TXparms['quantityQNT']
        self.apiTX_Slot(  self.apiReq_transferAsset , self.meta)


    def transferAsset_fromApi(self, crypt1, meta):

        self.crypt1 = crypt1

        try:
            self.TX_ID = crypt1['transaction']
            #self.sessMan.consLogger.info('transferAsset_fromApi  %s  %s ',      str(self.TX_ID) ,str(crypt1))
            #self.sessMan.xGateLogger.info('transferAsset_fromApi %s   %s ',   str(self.TX_ID) ,str(crypt1))

        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR transferAsset_fromApi:   %s', str(inst))

        self.sessMan.emit( SIGNAL("TX_transferAsset_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
            # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!
        try:
            self.poll1_Start(meta)
            # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            self.sessMan.xGateLogger.info('ERROR transferAsset_fromApi:   %s', str(inst))

        self.sessMan.consLogger.info('TX transferAsset_fromApi   %s ',    str(crypt1))
        self.sessMan.xGateLogger.info('TXtransferAsset_fromApi   %s ',    str(crypt1))

        ##### REMEMBER: the api returns json dicts, not the instances created here!
        # hence, they must be handled eithrer here, or passed in the meta dict!!!



class SetAccountInfo(TX): #6
    """ -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):# setAccountInfo
        """
        special for each tX is its ISSUE slot and the params that go into it

       """
        super(SetAccountInfo, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'SetAccountInfo'
        self.apiReq_setAccountInfo = copy(self.apiCalls.setAccountInfo)
        self.apiTX_Slot = self.sessMan.nxtApi.setAccountInfo_Slot

        for p in TXparms:
            pass#print(str(p) + " - " + str(TXparms[p]))
        self.init_TX_setAccountInfo_Sig_fromApi()

    def init_TX_setAccountInfo_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("setAccountInfo_Sig(PyQt_PyObject, PyQt_PyObject)"), self.setAccountInfo_fromApi)


    def setAccountInfo(self, ):
        self.apiReq_setAccountInfo['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_setAccountInfo['deadline'] = self.TXparms['deadline']
        self.apiReq_setAccountInfo['publicKey'] = '' #LATER
        self.apiReq_setAccountInfo['referencedTransaction']  = '' #LATER
        self.apiReq_setAccountInfo['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']

        self.apiReq_setAccountInfo['name'] = self.TXparms['name']
        self.apiReq_setAccountInfo['description']  = self.TXparms['description']

        for p in self.apiReq_setAccountInfo:
            pass#
            print(str(p) + " - " + str(self.apiReq_setAccountInfo[p]))

        self.apiTX_Slot(  self.apiReq_setAccountInfo , self.meta)

    def setAccountInfo_fromApi(self, crypt1, meta):
        self.crypt1 = crypt1
        try:
            self.TX_ID = crypt1['transaction']

            if self.sessMan.logShort:
                self.sessMan.logFshort.write(self.TX_ID + " - setAccountInfo - " + str(time.asctime()) +  "\n")
                self.sessMan.logFshort.flush()
        except:
            meta['error'] = True
            #for key in crypt1: #
            #    print(key + " - " + str(crypt1[key]))

        self.sessMan.emit( SIGNAL("TX_setAccountInfo_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
        # this sig goes to multiple receivers: e.g. the uc4 class, AND also the win0 class!
        try:
            self.poll1_Start(meta)
            pass # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            print(str(inst))


class LeaseBalance(TX): #6
    """ -"""

    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):
        super(LeaseBalance, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'LeaseBalance'
        self.apiReq_leaseBalance = copy(self.apiCalls.leaseBalance)
        self.apiTX_Slot = self.sessMan.nxtApi.leaseBalance_Slot
        self.init_TX_leaseBalance_Sig_fromApi()


    def init_TX_leaseBalance_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("leaseBalance_Sig(PyQt_PyObject, PyQt_PyObject)"), self.leaseBalance_fromApi)

    def leaseBalance(self): # etc!
        self.apiReq_leaseBalance['feeNQT'] = self.TXparms['feeNQT']
        self.apiReq_leaseBalance['deadline'] = self.TXparms['deadline']
        self.apiReq_leaseBalance['publicKey'] = '' #LATER
        self.apiReq_leaseBalance['referencedTransaction']  = '' #LATER
        self.apiReq_leaseBalance['secretPhrase']  = self.sessMan.uc2_accHndlr.accRes.data['secretPhrase']

        self.apiReq_leaseBalance['recipient'] = self.TXparms['recipient']
        self.apiReq_leaseBalance['period']  = self.TXparms['period']
        self.apiTX_Slot(  self.apiReq_leaseBalance , self.meta)

    def leaseBalance_fromApi(self, crypt1, meta):
        self.crypt1 = crypt1
        try:
            self.TX_ID = crypt1['transaction']

            if self.sessMan.logShort:
                self.sessMan.logFshort.write(self.TX_ID + " - leaseBalance - " + str(time.asctime()) +  "\n")
                self.sessMan.logFshort.flush()
        except:
            meta['error'] = True
        self.sessMan.emit( SIGNAL("TX_leaseBalance_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
        try:
            self.poll1_Start(meta)
            pass # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            print(str(inst))






class AssignAlias(TX): #5
    """ -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan,   query={}, data={}):#
        """
        create the resident user data here.  dedicated Alias class
       """
        super(AssignAlias, self).__init__()
        self.sessMan = sessMan

        self.data = data
        self.query = query
        self.data['WEBSITE']  = 'www.test.com'
        self.data['ALIAS'] = 'Roadmarks'
        self.data['URI'] = '0'
        self.query['aliasId'] = '0'

class CreatePoll(TX): #6
    """ -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan,   query={}, data={}):#
        """
        create the resident user data here.  dedicated MSG class
       """
        super(CreatePoll, self).__init__()
        self.sessMan = sessMan

        self.data = data
        self.query = query
        self.data['MESSAGE_HEXSTRING']= 'aaaaaaaaaaaabbbbbbbbbbbbffffffffff0123456789bcde'
        self.query['TX_id'] = '0'

class CastVote(TX): #6
    """ -"""
    assetResponse_Sig = pyqtSignal(dict) # always last
    assetResponse_Slot = pyqtSlot(dict, )

    def __init__(self, sessMan,   query={}, data={}):#
        """
        create the resident user data here.  dedicated MSG class
       """
        super(CastVote, self).__init__()
        self.sessMan = sessMan

        self.data = data
        self.query = query
        self.data['MESSAGE_HEXSTRING']= 'aaaaaaaaaaaabbbbbbbbbbbbffffffffff0123456789bcde'
        self.query['TX_id'] = '0'

class template(TX):
    def __init__(self, sessMan, TX_ID=None , TXparms=None, meta ={} ):
        super(template, self).__init__(sessMan, TX_ID, meta)
        self.TXparms = TXparms
        self.meta = meta
        self.meta['TXcreator'] = 'template'
        self.apiReq_template1 = self.apiCalls.template1
        self.apiTX_Slot = self.sessMan.nxtApi.template1_Slot
        self.init_TX_template1_Sig_fromApi()


    def init_TX_template1_Sig_fromApi(self): # override from TX
        QObject.connect(self.nxtApi, SIGNAL("template1_Sig(PyQt_PyObject, PyQt_PyObject)"), self.template1_fromApi)

    def template1(self): # etc!
        self.apiReq_template1['t'] = self.TXparms['t']
        self.apiTX_Slot(  self.apiReq_template1 , self.meta)

    def template1_fromApi(self, crypt1, meta):
        self.crypt1 = crypt1
        try:
            self.TX_ID = crypt1['transaction']
        except:
            meta['error'] = True
        self.sessMan.emit( SIGNAL( "TX_template1_Sig(PyQt_PyObject, PyQt_PyObject)"), self, meta )    # throw thyself around
        try:
            self.poll1_Start(meta)
            pass # HERE WE CAN DO ALL KIND OF CHECKS ON THE TX RETURN!NRSreply1
        except Exception as inst:
            print(str(inst))













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
    nxtQueryTest = nxtQuery({},app)    
    nxtQueryTest.stateChanged.connect( Test )
    nxtQueryTest.emitter()
    done = app.exec_()
    sys.exit(done)
 
 

#
#Where:
#
#    WEBSITE is the URL for the web site where authorization was granted. By convention this does not include the "http://" portion of the URL.
#    AUTHSTRING is the encoded authorization string
#
#Response
#
#{
#     "account":       "NXTACCOUNT",
#     "timestamp":       622,
#     "valid":       true




#        self.model = QtGui.QStandardItemModel(self)
#
#
#        for rowName in range(15): # * 5:
#            self.model.invisibleRootItem().appendRow(
#                [   QtGui.QStandardItem("row {0} col {1}".format(rowName, column))
#                    for column in range(3)
#                    ]
#                )
#
#        self.proxy = QtGui.QSortFilterProxyModel(self)
#        self.proxy.setSourceModel(self.model)
#
#        self.view.setModel(self.proxy)
#        self.comboBox.addItems(["Column {0}".format(x) for x in range(self.model.columnCount())])

#
#        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
#        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
#
#        self.horizontalHeader = self.view.horizontalHeader()
#        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)
#


# QStandardItemModel versus QStandardTableModel

# 
#TransactionID = sendMoney(..) //deadline 900
#TransactionBytes = getTransactionBytes(TransactionID)
#broadCastTransaction(TransactionBytes)
#
#Do we do this immediately after sendMoney? Or do we need to wait 1 minute or so?
#
#This is what I send to those who ask how to accept/send nxts:
#
#
#CFB
#
#Here is one of the ways to handle deposits:
#
#1. U generate a string of 50+ chars. This is ur master passphrase, it must be very strong. Let's assume it's "secret".
#2. Each time when a user wants to deposit coins u generate a unique ID, u can use user ID if it's not necessary to create a new address for each deposit.
#3. U use "secret"+ID to generate a passphrase for the deposit account, for example "secret8475347836".
#4. http://localhost:7874/nxt?requestType=getAccountId&secretPhrase=secret8475347836 will return the corresponding account id. U should give it to the user.
#5. Periodically u should check if the address got incoming transactions - http://localhost:7874/nxt?requestType=getAccountTransactionIds&account=6975576163363041725&timestamp=0
#6. For each id in the list u can get transaction info - http://localhost:7874/nxt?requestType=getTransaction&transaction=83492836836338756
#7. When u get enough confirmations (at least 10) u can increase user's balance.
#
#Some very important things:
#
#Blocks can become orphaned and transactions cancelled, so pay attention to timestamp and deadline values of a transaction. Timestamp is measured in seconds since the genesis block (24th of Nov, 2013 12:00:00 UTC). Deadline is measured in minutes. 
#
#A transaction expires when timestamp + deadline * 60 < current time, it can't be included into a block with timestamp > timestamp (of the transaction) + deadline * 60. Current time can be obtained via http://localhost:7874/nxt?requestType=getTime
#
#
#
#
#So, to make sure that u won't lose the transaction u should check that a user uses large deadline and doesn't try to cheat u by setting timestamp too far in the past. Also, until a transaction gets 720 confirmations u should check it's still confirmed and if not (due to blockchain reorg), rebroadcast it to the network using http://localhost:7874/nxt?requestType=broadcastTransaction&transactionBytes=f11234bd3a2fc19c2ba6b7c0d108deea9fcbafda5f544e4648c651ec4ed34ed2. Transaction bytes can be obtained via http://localhost:7874/nxt?requestType=getTransactionBytes&transaction=83492836836338756.
#
#To send coins back to a user:
#
#Do http://localhost:7874/nxt?requestType=sendMoney&secretPhrase=123&recipient=2983475693816&amount=5000&fee=1&deadline=32767
#This request will return transaction id and transaction bytes. Save the both and periodically check that transaction is still in the blockchain. If it becomes unknown or unconfirmed then rebroadcast it via broadcastTransaction. Once it reaches 720 confirmations u can forget about it.
#
#
#
