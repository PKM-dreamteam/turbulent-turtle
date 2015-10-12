# coding=utf-8
__author__ = 'mikhael'
# !/usr/bin/env python

from logging.config import fileConfig
from tableModel import *
from altTerminal import *
from dailogs import *
from res import Res
import threading
from graphicView import *
from objectsISA import *
from xLogger import *


class ISAMainWindow(QMainWindow, object):
    """
    Main Window of ISA - QT GUI by QT Designer
    """
    def __init__(self):
        QMainWindow.__init__(self)
        # Init variables
        self.balisesLst = []
        self.wigwagsLst = []
        self.switchersLst = []
        self.allDataLst = []
        self.selectedItem = None
        self.selectedRow = 0
        self.term = None
        self.client = None
        self.res = Res()
        self.simulationComLst = []
        self.simulationRunning = False
        self.simPause = False
        self.e = threading.Event()
        self.t = threading.Thread(name='ISA Simulation',
                                  target=self.__simulation__,
                                  args=(self.e,))



        # Loading ui from file
        self.ui = uic.loadUi('.//Forms//mainwindow.ui', self)

        XStream.stdout().messageWritten.connect(self.ui.logEdit.insertHtml)
        XStream.stderr().messageWritten.connect(self.ui.logEdit.insertHtml)
        self.logger = XLogger('Log')
        self.logger.type = False

        self.aboutDlg = AboutDialog()
        self.connectDlg = ConnectDialog(self.logger)
        self.configDlg = ConfigDialog()
        self.simDlg = SimDialog()
        self.trainDlg = TrainDialog(self.logger)

        # Virtual & Simulation
        self.ui.virtualButton.setVisible(False)
        self.ui.runSimButton.setVisible(False)
        self.ui.loadSimButton.setVisible(False)
        self.ui.pauseSimButton.setVisible(False)
        self.ui.runSimButton.clicked.connect(self.runSim)
        self.ui.pauseSimButton.clicked.connect(self.pauseSim)

        # Led boxy
        self.ledBox = [self.ui.led0CheckBox, self.ui.led1CheckBox,
                       self.ui.led2CheckBox, self.ui.led3CheckBox,
                       self.ui.led4CheckBox]
        self.ledAlBox = [self.ui.led0AlCheckBox, self.ui.led1AlCheckBox,
                         self.ui.led2AlCheckBox, self.ui.led3AlCheckBox,
                         self.ui.led4AlCheckBox]

        self.trainsLst = []
        self.trainIconLst = [self.ui.trImageLabel_1, self.ui.trImageLabel_2, self.ui.trImageLabel_3,
                             self.ui.trImageLabel_4, self.ui.trImageLabel_5, self.ui.trImageLabel_6, self.ui.trImageLabel_7]
        self.trainVeloLst = [self.ui.trVelocitySlider_1, self.ui.trVelocitySlider_2, self.ui.trVelocitySlider_3,
                             self.ui.trVelocitySlider_4, self.ui.trVelocitySlider_5, self.ui.trVelocitySlider_6, self.ui.trVelocitySlider_7]
        self.trainDscLst = [self.ui.trDesLineEdit_1, self.ui.trDesLineEdit_2, self.ui.trDesLineEdit_3,
                            self.ui.trDesLineEdit_4, self.ui.trDesLineEdit_5, self.ui.trDesLineEdit_6, self.ui.trDesLineEdit_7]
        for i in range(7):
            self.trainsLst.append(Train(i + 1))
            self.trainIconLst[i].setPixmap(self.res.trainIco[i])

        # Logger


        # Scan Btn & Turn Elements Off Btn
        if self.term:
            self.ui.scanNetworkButton.setEnabled(True)
            self.ui.powerOffElementsButton.setEnabled(True)
            self.ui.magistralDisconnectButton.setEnabled(True)
        else:
            self.ui.scanNetworkButton.setEnabled(False)
            self.ui.powerOffElementsButton.setEnabled(False)
            self.ui.magistralDisconnectButton.setEnabled(False)
        self.ui.pauseSimButton.setEnabled(False)
        self.ui.runSimButton.setEnabled(False)

        self.ui.magistralDisconnectButton.setIcon(self.res.mushroomB)

        if self.client:
            self.ui.trainDisconnectButton.setEnabled(True)
            self.ui.trainMushroomButton.setEnabled(True)
            self.ui.trainMushroomButton.setIcon(self.res.mushroomBG)
            self.ui.trainScanButton.setEnabled(True)
        else:
            self.ui.trainDisconnectButton.setEnabled(False)
            self.ui.trainMushroomButton.setEnabled(False)
            self.ui.trainMushroomButton.setIcon(self.res.mushroomB)
            self.ui.trainScanButton.setEnabled(False)

        self.ui.trainScanButton.clicked.connect(self.scanTrains)

        self.ui.configDialogButton.setEnabled(False)
        self.connectionLabel.setPixmap(self.res.disconnectedPix)
        self.connectionLabel_2.setPixmap(self.res.disconnectedBPix)

        # Connecting signals - Dialogs
        self.ui.aboutDialogButton.clicked.connect(self.showAboutDlg)
        self.ui.configDialogButton.clicked.connect(self.showConfigDlg)
        self.ui.loadSimButton.clicked.connect(self.showSimDlg)
        self.ui.simDlg.finished.connect(self.getSim)
        self.ui.configDlg.finished.connect(self.getLoadedParams)

        # Bus connection
        self.ui.connectDialogButton.clicked.connect(self.showConnectDlg)
        self.ui.connectDlg.finished.connect(self.getTermFromDlg)

        # Train connection
        self.ui.trainConnectButton.clicked.connect(self.showTrainDlg)
        self.ui.trainDlg.finished.connect(self.getClientFromDlg)

        # Connecting signals - other buttons
        self.ui.scanNetworkButton.clicked.connect(self.scanNetClicked)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.virtualButton.clicked.connect(self.virtualClicked)
        self.ui.powerOffElementsButton.clicked.connect(self.turnOffGlobalClicked)

        # Changing parameters
        self.ui.changeElParamsButton.clicked.connect(self.changeParamsClicked)
        self.ui.pointXElLineEdit.textChanged.connect(self.changeParams)
        self.ui.pointYElLineEdit.textChanged.connect(self.changeParams)
        self.ui.descElLineEdit.textChanged.connect(self.changeParams)
        self.ui.addressElLineEdit.textChanged.connect(self.changeParams)
        self.ui.zoneComboBox.currentIndexChanged.connect(self.changeParams)

        self.ui.turnElOffButton.clicked.connect(self.turnOffElementClicked)
        self.ui.checkElStateButton.clicked.connect(self.checkElStateClicked)

        # TableView configuration
        self.tableConfig()

        # Zone combo list
        self.ui.zoneComboBox.addItems([u'None', u'Strzyża', u'Kiełpinek',
                                       u'Rębiechowo', u'Banino', u'Wrzeszcz'])

        # Disabling state buttons
        self.ui.changeElParamsButton.setEnabled(False)
        self.ui.turnElOffButton.setEnabled(False)
        self.ui.checkElStateButton.setEnabled(False)
        self.ui.leftSwitcherButton.setEnabled(False)
        self.ui.rightSwitcherButton.setEnabled(False)
        self.ui.leftSwLimCheckBox.setEnabled(False)
        self.ui.rightSwLimCheckBox.setEnabled(False)
        self.ui.changeStateButton.setEnabled(False)

        # Scrolling log
        self.ui.logEdit.textChanged.connect(self.scrollLog)

        # Switcher buttons
        self.ui.leftSwitcherButton.clicked.connect(self.switcherChangeBtnClicked)
        self.ui.rightSwitcherButton.clicked.connect(self.switcherChangeBtnClicked)

        # Wigwags checkboxes
        for i in range(5):
            self.ledBox[i].stateChanged.connect(self.changeWigwagParameters)
            self.ledAlBox[i].stateChanged.connect(self.changeWigwagParameters)
            self.ledBox[i].setIcon(self.res.wigwagOffIco[i])
            self.ledAlBox[i].setIcon(self.res.wigwagOffIco[i])

        # Wigwag button
        self.ui.changeStateButton.clicked.connect(self.wigwagChangeBtnClicked)

        # Balisa button
        self.ui.changeINTButton.clicked.connect(self.changeBalisaINT)

        # Map view
        self.mapScene = GraphicsSceneISA()
        self.mapScene.addPixmap(self.res.mapPix.scaledToHeight(500, Qt.SmoothTransformation))
        self.ui.mapGraphicsView = GraphicsViewISA(self.ui.tabMap)
        self.ui.horizontalLayout.addWidget(self.ui.mapGraphicsView)
        self.ui.mapGraphicsView.setScene(self.mapScene)

        # Ozdobniki
        self.ui.imageLabel_2.setPixmap(self.res.fall)
        self.ui.imageLabel_2.setScaledContents(True)
        self.setStyleSheet("""#centralWidget {background-image: url(.//imags//background.png)}
                              #tabMain {background-image: url(.//imags//background.png)}
                              #logScrollArea {background-image: url(.//imags//background.png)}
                              #tabAll {background-image: url(.//imags//background.png)}
                              #tabSwitchers {background-image: url(.//imags//background.png)}
                              #tabWigwags {background-image: url(.//imags//background.png)}
                              #tabBalises {background-image: url(.//imags//background.png)}
                              #tabTrains {background-image: url(.//imags//background.png)}
                           """)
        self.ui.tabWidget.currentChanged.connect(self.changeTab)
        self.ui.imageLabel.setPixmap(self.res.icons[0])

    def keyPressEvent(self, e):
        """
        Key to unlocked virtual terminal - Alt
        """
        if e.key() == Qt.Key_F10:
            if self.ui.virtualButton.isVisible():
                self.ui.virtualButton.setVisible(False)
                self.ui.runSimButton.setVisible(False)
                self.ui.loadSimButton.setVisible(False)
                self.ui.pauseSimButton.setVisible(False)
                self.logger.info('Disposed additional buttons')
            else:
                self.ui.virtualButton.setVisible(True)
                self.ui.runSimButton.setVisible(True)
                self.ui.loadSimButton.setVisible(True)
                self.ui.pauseSimButton.setVisible(True)
                self.logger.info('Founded additional buttons')
        if e.key() == Qt.Key_V:
            self.runTest()

        # Train control

        if self.client and self.client.connected:
            if e.key() == Qt.Key_Q or e.key() == Qt.Key_A:
                if e.key() == Qt.Key_Q:
                    self.client.sendMsg(self.trainsLst[0].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[0].changeSpeed(0))
                self.trainVeloLst[0].setValue(self.trainsLst[0].getSpeed())
                self.trainDscLst[0].text = self.trainsLst[0].getSpeed()
            if e.key() == Qt.Key_W or e.key() == Qt.Key_S:
                if e.key() == Qt.Key_W:
                    self.client.sendMsg(self.trainsLst[1].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[1].changeSpeed(0))
                self.trainVeloLst[1].setValue(self.trainsLst[1].getSpeed())
                self.trainDscLst[1].text = self.trainsLst[1].getSpeed()
            if e.key() == Qt.Key_E or e.key() == Qt.Key_D:
                if e.key() == Qt.Key_E:
                    self.client.sendMsg(self.trainsLst[2].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[2].changeSpeed(0))
                self.trainVeloLst[2].setValue(self.trainsLst[2].getSpeed())
                self.trainDscLst[2].text = self.trainsLst[2].getSpeed()
            if e.key() == Qt.Key_R or e.key() == Qt.Key_F:
                if e.key() == Qt.Key_R:
                    self.client.sendMsg(self.trainsLst[3].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[3].changeSpeed(0))
                self.trainVeloLst[3].setValue(self.trainsLst[3].getSpeed())
                self.trainDscLst[3].text = self.trainsLst[3].getSpeed()
            if e.key() == Qt.Key_T or e.key() == Qt.Key_G:
                if e.key() == Qt.Key_T:
                    self.client.sendMsg(self.trainsLst[4].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[4].changeSpeed(0))
                self.trainVeloLst[4].setValue(self.trainsLst[4].getSpeed())
                self.trainDscLst[4].text = self.trainsLst[4].getSpeed()
            if e.key() == Qt.Key_Y or e.key() == Qt.Key_H:
                if e.key() == Qt.Key_Y:
                    self.client.sendMsg(self.trainsLst[5].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[5].changeSpeed(0))
                self.trainVeloLst[5].setValue(self.trainsLst[5].getSpeed())
                self.trainDscLst[5].text = self.trainsLst[5].getSpeed()
            if e.key() == Qt.Key_U or e.key() == Qt.Key_J:
                if e.key() == Qt.Key_U:
                    self.client.sendMsg(self.trainsLst[6].changeSpeed(1))
                else:
                    self.client.sendMsg(self.trainsLst[6].changeSpeed(0))
                self.trainVeloLst[6].setValue(self.trainsLst[6].getSpeed())
                self.trainDscLst[6].text = self.trainsLst[6].getSpeed()
            if e.key() == Qt.Key_Z:
                for i in range(7):
                    self.client.sendMsg(self.trainsLst[i].changeVelocity(0, 0))

        if e.key() == Qt.Key_C:
            self.logger.info('Auto run config')
            i = self.connectDlg.ui.portComboBox.count()
            self.connectDlg.ui.portComboBox.setCurrentIndex(i - 1)
            self.connectDlg.createTerminal()
            self.scanNetClicked()
            self.configDlg.ui.loadBtnClicked(None)
        if e.key() == Qt.Key_B:
            self.trainDlg.createClient()

    def changeTab(self, current):
        """
        Changing tab
        :param current: currently clicked tab
        """
        self.ui.imageLabel.setPixmap(self.res.icons[current])

    def prepareMap(self):
        """
        Preparing map view
        """
        if self.term:
            self.logger.info('Preparing map')
            qObj = QObj()
            for sw in self.switchersLst:
                if not sw.mapPosition == (0, 0):
                    it = GraphicItemISA(sw, qObj)
                    self.ui.mapGraphicsView.scene().addItem(it)
                    QObject.connect(it.qObj, SIGNAL("map_signal"), self.writeCommand)
            for b in self.balisesLst:
                if not b.mapPosition == (0, 0):
                    it = GraphicItemISA(b, qObj)
                    self.ui.mapGraphicsView.scene().addItem(it)
            for wi in self.wigwagsLst:
                if not wi.mapPosition == (0, 0):
                    it = GraphicItemISA(wi, qObj)
                    self.ui.mapGraphicsView.scene().addItem(it)
                    QObject.connect(it.qObj, SIGNAL("map_signal"), self.writeCommand)
            self.ui.mapGraphicsView.scene().update()
            self.logger.info('The map has been prepared')

    def writeCommand(self, cmd):
        """
        Writting command
        :param cmd: command
        """
        if self.term:
            self.term.writeCommand(cmd)
            self.ui.mapGraphicsView.scene().update()

    def scanNetClicked(self):
        """
        Method of scanning network
        """
        self.allDataLst = []
        self.switchersLst = []
        self.wigwagsLst = []
        self.balisesLst = []
        if self.term:
            (self.switchersLst, self.wigwagsLst, self.balisesLst) = \
                self.term.scanElements()
            self.allDataLst.extend(self.switchersLst)
            self.allDataLst.extend(self.wigwagsLst)
            self.allDataLst.extend(self.balisesLst)
            self.tableConfig()
            self.logger.info('Tables has been set')
        else:
            self.logger.error('There is no terminal')
        if self.allDataLst:
            self.ui.configDialogButton.setEnabled(True)
        else:
            self.ui.configDialogButton.setEnabled(False)

    def scanTrains(self):
        """
        Scanning trains
        """
        if self.client.connected:
            for train in self.trainsLst:
                train.setState(self.client.sendMsg(train.checkState()))
                if train.state:
                    self.ui.trImageLabel.setPixmap(self.res.trainGIco[train.address])
                else:
                    self.ui.trImageLabel.setPixmap(self.res.trainIco[train.address])

    def tableConfig(self):
        header = ['Zone', 'Address', 'Status', 'Point', 'Description']

        self.ui.switchersTableView.setModel(TableModel(self.switchersLst,
                                                       header))
        self.ui.wigwagsTableView.setModel(TableModel(self.wigwagsLst, header))
        self.ui.balisesTableView.setModel(TableModel(self.balisesLst, header))
        self.ui.generalTableView.setModel(TableModel(self.allDataLst, header))

        # Selection linking
        self.ui.generalTableView.selectionModel().currentRowChanged.connect(
            self.generalRowSelected)
        self.ui.switchersTableView.selectionModel().currentRowChanged.connect(
            self.switcherRowSelected)
        self.ui.wigwagsTableView.selectionModel().currentRowChanged.connect(
            self.wigwagRowSelected)
        self.ui.balisesTableView.selectionModel().currentRowChanged.connect(
            self.balisesRowSelected)

        # self.ui.wigwagsTableView
        # self.ui.balisesTableView

    def generalRowSelected(self, selected, deselected):
        """
        General tableView method - setting general parameters
        :param selected: selected row
        :param deselected:
        """
        self.selectedRow = int(selected.row())
        self.selectedItem = selected.model().tableData[int(selected.row())]
        self.setGeneralParameters(self.selectedItem)

    def switcherRowSelected(self, selected, deselected):
        """
        Switchers tableView method - setting specific parameters of switcher,
        especially imags and direction
        :param selected: selected row
        """
        self.selectedRow = int(selected.row())
        self.selectedItem = selected.model().tableData[int(selected.row())]
        self.setGeneralParameters(self.selectedItem)
        self.setSwitcherParameters(self.selectedItem)

    def wigwagRowSelected(self, selected, deselected):
        """
        Wigwags tableView method - setting specific parameters of wigwag,
        especially imags and checkboxes
        :param selected: selected row
        """
        self.selectedRow = int(selected.row())
        self.selectedItem = selected.model().tableData[int(selected.row())]
        self.setGeneralParameters(self.selectedItem)
        self.setWigwagParameters(self.selectedItem)

    def balisesRowSelected(self, selected, deselected):
        """
        Balisa tableView method - setting specific parameters of balisa,
        :param selected: selected row
        """
        self.selectedRow = int(selected.row())
        self.selectedItem = selected.model().tableData[int(selected.row())]
        self.setGeneralParameters(self.selectedItem)
        element = self.selectedItem
        self.ui.int0LineEdit.setText(str(element.int0))
        self.ui.int1LineEdit.setText(str(element.int1))
        if element.logInt0:
            self.ui.int0TimeValueLabel.setText(str(element.logInt0[-1][0]))
        if element.logInt1:
            self.ui.int1TimeValueLabel.setText(str(element.logInt1[-1][0]))

    def setWigwagParameters(self, element):
        """
        Setting parameters of wigwag
        :param element: selected wigwag
        """
        for i in range(5):
            if element.state[i]:
                self.ledBox[i].setCheckState(Qt.Checked)
                self.ledBox[i].setIcon(self.res.wigwagOnIco[i])
            else:
                self.ledBox[i].setCheckState(Qt.Unchecked)
                self.ledBox[i].setIcon(self.res.wigwagOffIco[i])
                self.ledAlBox[i].setCheckState(Qt.Unchecked)
                self.ledAlBox[i].setIcon(self.res.wigwagOffIco[i])
            if element.alarm[i]:
                self.ledBox[i].setCheckState(Qt.Checked)
                self.ledBox[i].setIcon(self.res.wigwagOnIco[i])
                self.ledAlBox[i].setCheckState(Qt.Checked)
                self.ledAlBox[i].setIcon(self.res.wigwagBlinkIco[i])

    def changeWigwagParameters(self):
        """
        Changing led selections
        """
        ledLst = []
        ledAlLst = []
        for i in range(5):
            if self.ledBox[i].checkState() == Qt.Checked:
                ledLst.append(1)
                self.ledBox[i].setIcon(self.res.wigwagOnIco[i])
            else:
                ledLst.append(0)
                self.ledBox[i].setIcon(self.res.wigwagOffIco[i])
            if self.ledAlBox[i].checkState() == Qt.Checked:
                ledAlLst.append(1)
                self.ledAlBox[i].setIcon(self.res.wigwagBlinkIco[i])
            else:
                ledAlLst.append(0)
                self.ledAlBox[i].setIcon(self.res.wigwagOffIco[i])
        if self.selectedItem:
            if not (ledLst == self.selectedItem.state and ledAlLst ==
                    self.selectedItem.alarm):
                self.ui.changeStateButton.setEnabled(True)
            else:
                self.ui.changeStateButton.setEnabled(False)

    def setSwitcherParameters(self, element):
        """
        Setting parameters of switcher
        :param element: selected switcher
        """
        # self.ui.leftSwLimCheckBox.setCheckable(True)
        # self.ui.rightSwLimCheckBox.setCheckable(True)
        if element.state == switcherState[0]:
            self.ui.rightSwitcherButton.setEnabled(True)
            self.ui.leftSwitcherButton.setEnabled(True)
            self.ui.leftSwLimCheckBox.setEnabled(False)
            self.ui.rightSwLimCheckBox.setEnabled(False)
        elif element.state == switcherState[1]:
            # Left
            self.ui.rightSwitcherButton.setEnabled(True)
            self.ui.leftSwitcherButton.setEnabled(False)
            self.ui.leftSwLimCheckBox.setEnabled(True)
            self.ui.rightSwLimCheckBox.setEnabled(True)
            self.ui.leftSwLimCheckBox.setChecked(Qt.Checked)
            self.ui.leftSwLimCheckBox.setIcon(self.res.switcherLightPix[1])
            self.ui.rightSwLimCheckBox.setChecked(Qt.Unchecked)
            self.ui.rightSwLimCheckBox.setIcon(self.res.switcherLightPix[0])
            self.ui.switcherStateImageLabel.setPixmap(self.res.switcherPix[0])
        elif element.state == switcherState[-1]:
            # Right
            self.ui.rightSwitcherButton.setEnabled(False)
            self.ui.leftSwitcherButton.setEnabled(True)
            self.ui.leftSwLimCheckBox.setEnabled(True)
            self.ui.rightSwLimCheckBox.setEnabled(True)
            self.ui.leftSwLimCheckBox.setChecked(Qt.Unchecked)
            self.ui.leftSwLimCheckBox.setIcon(self.res.switcherLightPix[0])
            self.ui.rightSwLimCheckBox.setChecked(Qt.Checked)
            self.ui.rightSwLimCheckBox.setIcon(self.res.switcherLightPix[1])
            self.ui.switcherStateImageLabel.setPixmap(self.res.switcherPix[1])
        # self.ui.leftSwLimCheckBox.setCheckable(False)
        # self.ui.rightSwLimCheckBox.setCheckable(False)

    def setGeneralParameters(self, element):
        """
        Setting general parameters of selected PKMObject such as Zone, Address,
        Description, Point
        """
        self.ui.zoneComboBox.setCurrentIndex(int(zoneDict[element.zone]))
        self.ui.addressElLineEdit.setText(str(element.deviceNo))
        self.ui.descElLineEdit.setText(element.description)
        self.ui.pointXElLineEdit.setText(str(element.mapPosition[0]))
        self.ui.pointYElLineEdit.setText(str(element.mapPosition[1]))
        self.ui.turnElOffButton.setEnabled(True)
        self.ui.checkElStateButton.setEnabled(True)

    def changeParams(self):
        """
        Changing parameters of PKMObject
        """
        it = self.selectedItem
        if self.ui.addressElLineEdit.text():
            addText = int(self.ui.addressElLineEdit.text())
        else:
            addText = 0
        zone = unicode(self.ui.zoneComboBox.currentText())
        desc = unicode(self.ui.descElLineEdit.toPlainText())
        point = None
        if self.ui.pointXElLineEdit.text() and self.ui.pointYElLineEdit.text():
            x = int(self.ui.pointXElLineEdit.text())
            y = int(self.ui.pointYElLineEdit.text())
            point = (x, y)
        if it:
            if not(it.zone == zone and it.deviceNo == addText) or \
                    not(it.description == desc and it.mapPosition == point):
                # self.term.writeCommand(it.setAddress(zone, addText))
                self.ui.changeElParamsButton.setEnabled(True)
            else:
                self.ui.changeElParamsButton.setEnabled(False)
            # if not(it.description == desc and it.mapPosition == point):
            #     it.mapPosition = point
            #     it.description = desc

    def changeParamsClicked(self):
        """
        Changing params on click
        """
        addText = int(self.ui.addressElLineEdit.text())
        zText = unicode(self.ui.zoneComboBox.currentText())
        zone = zoneDict[zText]
        desc = unicode(self.ui.descElLineEdit.toPlainText())
        point = None
        if self.ui.pointXElLineEdit.text() and self.ui.pointYElLineEdit.text():
            x = int(self.ui.pointXElLineEdit.text())
            y = int(self.ui.pointYElLineEdit.text())
            point = (x, y)
        if not(self.selectedItem.zone == zoneDict[zone] and
           self.selectedItem.deviceNo == addText):
            self.term.writeCommand(self.selectedItem.setAddress(zone, addText))
        if not(self.selectedItem.description == desc and
           self.selectedItem.mapPosition == point):
            self.selectedItem.mapPosition = point
            self.selectedItem.description = desc
        self.ui.changeElParamsButton.setEnabled(False)
        self.ui.generalTableView.model().changeData()
        self.ui.switchersTableView.model().changeData()
        self.ui.wigwagsTableView.model().changeData()
        self.ui.balisesTableView.model().changeData()

    def switcherChangeBtnClicked(self):
        """
        Change switcher state
        """
        if self.sender().text() == 'Left':
            self.term.writeCommand(self.selectedItem.switchLeft())
            sleep(0.1)
            self.term.writeCommand(self.selectedItem.powerOff())
        elif self.sender().text() == 'Right':
            self.term.writeCommand(self.selectedItem.switchRight())
            sleep(0.1)
            self.term.writeCommand(self.selectedItem.powerOff())
        self.ui.switchersTableView.model().changeData()
        self.setSwitcherParameters(self.selectedItem)

    def wigwagChangeBtnClicked(self):
        """
        Change wigwag state
        """
        ledLst = []
        ledAlLst = []
        for i in range(5):
            if self.ledBox[i].checkState() == Qt.Checked:
                ledLst.append(1)
            else:
                ledLst.append(0)
            if self.ledAlBox[i].checkState() == Qt.Checked:
                ledAlLst.append(1)
            else:
                ledAlLst.append(0)
        if not ledAlLst == self.selectedItem.alarm:
            self.term.writeCommand(self.selectedItem.setAlarmsLed(ledAlLst))
        else:
            self.term.writeCommand(self.selectedItem.setLed(ledLst))
        self.ui.wigwagsTableView.model().changeData()

    def changeBalisaINT(self):
        int0 = 0
        int1 = 0
        try:
            int0 = int(self.ui.int0LineEdit.text())
            int1 = int(self.ui.int1LineEdit.text())
        finally:
            if int0:
                self.term.writeCommand(self.selectedItem.setINT0(int0))
            if int1:
                self.term.writeCommand(self.selectedItem.setINT1(int1))

    def balisaInt(self, b):
        """
        Reading balisa int
        """
        for bal in self.balisesLst:
            if bal.compare(b):
                #self.logger.info('Balisa ' + str(b.deviceNo) + ' int ')
                bal.state = b.state
                self.ui.mapGraphicsView.scene().update()

    def turnOffElementClicked(self):
        """
        Turning off currently selected element
        """
        self.term.writeCommand(self.selectedItem.powerOff())

    def checkElStateClicked(self):
        """
        Checking state
        """
        self.term.writeCommand(self.selectedItem.testState())

    def turnOffGlobalClicked(self):
        """
        Turning off elements
        """
        self.term.turnAgentsOff()

    def showAboutDlg(self):
        """
        Showing about dialog
        """
        self.aboutDlg.show()

    def showConnectDlg(self):
        """
        Showing connect dialog
        """
        self.connectDlg.show()

    def showTrainDlg(self):
        """
        Showing train dialog
        """
        self.trainDlg.show()

    def showSimDlg(self):
        """
        Showing train dialog
        """
        self.simDlg.show()

    def getClientFromDlg(self, sign):
        """
        On closing train connect dialog get the opened client
        """
        if sign:
            self.client = self.trainDlg.getClient()
            self.logger.info('Connected with Lenz USB/Lan Interface')
            self.connectionLabel_2.setPixmap(self.res.connectedBPix)
            self.ui.trainScanButton.setEnabled(True)
        else:
            self.logger.error('Could not find Lenz USB/Lan Interface')
            self.connectionLabel_2.setPixmap(self.res.disconnectedBPix)
            self.ui.trainScanButton.setEnabled(False)
        if self.client:
            self.ui.trainDisconnectButton.setEnabled(True)
            self.ui.trainMushroomButton.setEnabled(True)
        else:
            self.ui.trainDisconnectButton.setEnabled(False)
            self.ui.trainMushroomButton.setEnabled(False)

    def getTermFromDlg(self, sign):
        """
        On closing connect dialog get the opened terminal
        """
        if sign:
            self.term = self.connectDlg.getTerminal()
            self.ui.scanNetworkButton.setEnabled(True)
            self.ui.powerOffElementsButton.setEnabled(True)
            self.logger.info('Connected with ISA')
            self.connectionLabel.setPixmap(self.res.connectedPix)
            QObject.connect(self.term, SIGNAL("balisa_int"), self.balisaInt)
        else:
            self.logger.error('Could not find terminal')
            self.ui.scanNetworkButton.setEnabled(False)
            self.ui.powerOffElementsButton.setEnabled(False)
            self.connectionLabel.setPixmap(self.res.disconnectedPix)

    def getLoadedParams(self, sign):
        """
        Matching read parameters from file
        """
        flag = self.configDlg.stateLoad and self.term
        if sign:
            for el in self.configDlg.wigwagsLst:
                for x in self.wigwagsLst:
                    if x.compare(el):
                        x.description = el.description
                        x.mapPosition = el.mapPosition
                        if flag:
                            self.term.writeCommand(x.setState(el.state))
                            self.term.writeCommand(x.setAlarmsLed(el.alarm))
                        break
            for el in self.configDlg.switchersLst:
                if el.type == '04':
                    self.switchersLst.append(el)
                for x in self.switchersLst:
                    if x.compare(el):
                        x.description = el.description
                        x.mapPosition = el.mapPosition
                        x.orientation = el.orientation
                        if flag:
                            self.term.writeCommand(x.setState(el.state))
                        break
            for el in self.configDlg.balisesLst:
                balisa = None
                for x in self.balisesLst:
                    if x.compare(el):
                        x.description = el.description
                        x.mapPosition = el.mapPosition
                        if flag:
                            balisa.setState(el.state)
                        break
            self.prepareMap()

    def getSim(self, sign):
        if sign:
            self.simulationComLst = self.simDlg.comLst
            self.ui.pauseSimButton.setEnabled(True)
            self.ui.runSimButton.setEnabled(True)
        else:
            self.ui.pauseSimButton.setEnabled(False)
            self.ui.runSimButton.setEnabled(False)

    def showConfigDlg(self):
        """
        Configuration dialog
        """
        self.configDlg.show()
        self.configDlg.switchersLst = self.switchersLst
        self.configDlg.wigwagsLst = self.wigwagsLst
        self.configDlg.balisesLst = self.balisesLst

    def virtualClicked(self):
        """
        Virtual terminal created
        """
        self.term = AltTerm()
        self.term.xlogger = self.logger
        self.logger.info('Virtual terminal has been created')
        self.ui.scanNetworkButton.setEnabled(True)
        self.connectionLabel.setPixmap(self.res.virconnectedPix)

    def scrollLog(self):
        """
        Scrolling of log
        """
        self.ui.logEdit.moveCursor(QTextCursor.End)

    def runSim(self):
        """
        Running simulation
        """
        self.simulationRunning = True
        self.t.start()

    def __simulation__(self, e):
        """
        Simulation thread
        """
        self.logger.info('Running simulation')
        while self.simulationRunning:
            for el in self.simulationComLst:
                #self.logger.info('Simulation command: ' + el)
                com = compile(el, '<string>', 'exec')
                exec(com)
                if self.simPause:
                    e.wait()
                e.clear()
            self.simulationRunning = False

    def pauseSim(self):
        """
        Pausing simulation
        """
        self.simulationRunning = False
        self.t = threading.Thread(name='ISA Simulation',
                                  target=self.__simulation__,
                                  args=(self.e,))
        # if not self.simPause:
        #     self.simPause = True
        #     self.ui.pauseSimButton.setText('Resume Simulation')
        #     self.client.mushroomStop()
        # else:
        #     self.e.set()
        #     self.ui.pauseSimButton.setText('Pause Simulation')
        #     self.client.mushroomStart()

    def runTest(self):
        """
        Basic test simulation run by 'v' button
        """
        # if self.term:
        #     self.logger.info('Running test')
        #     for sw in self.switchersLst:
        #         if sw.zone == u'Kiełpinek':
        #             self.term.writeCommand(sw.switchLeft())
        #     for sw in self.switchersLst:
        #         self.term.writeCommand(sw.switchRight())
        # else:
        #     self.logger.info('Test can not be run, there is no terminal')

if __name__ == '__main__':
    fileConfig(''.join([os.getcwd(), '/logging.conf']))
    app = QApplication(sys.argv)
    mainWindow = ISAMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())