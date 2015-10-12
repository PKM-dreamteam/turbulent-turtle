# coding=utf-8
__author__ = 'mikhael'
# !/usr/bin/env python

from logging.config import fileConfig
from xLogger import *
from time import time
from dailogs import *
from res import Res
import threading
from graphicView import *
from objectsISA import *


class ISASimpleWindow(QMainWindow, object):
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
        self.term = None
        self.client = None
        self.res = Res()
        self.simulationComLst = []
        self.simulationRunning = False
        self.simPause = False
        self.timeStamp = 0
        self.e = threading.Event()
        self.t = threading.Thread(name='ISA Simulation',
                                  target=self.__simulation__,
                                  args=(self.e,))
        self.t2 = threading.Thread(name='ISA Simulation',
                                  target=self.__skm__,
                                  args=(self.e,))

        # Loading ui from file
        self.ui = uic.loadUi('.//Forms//SimpleWindow.ui', self)
        self.aboutDlg = AboutDialog()
        self.configDlg = ConfigDialog()
        self.simDlg = SimDialog()
        self.logDlg = LogDialog()
        self.helpDlg = HelpDialog()

        # Virtual & Simulation
        self.ui.runSimButton.clicked.connect(self.runSim)
        self.ui.pauseSimButton.clicked.connect(self.pauseSim)

        self.trainsLst = []
        for i in range(7):
            self.trainsLst.append(Train(i + 1))

        # Logger
        # XStream.stdout().messageWritten.connect(self.ui.logEdit.insertHtml)
        # XStream.stderr().messageWritten.connect(self.ui.logEdit.insertHtml)
        self.logger = XLogger('Log')
        self.logger.type = False
        XStream.stdout().messageWritten.connect(self.logDlg.textEdit.insertHtml)
        XStream.stderr().messageWritten.connect(self.logDlg.textEdit.insertHtml)

        self.connectDlg = ConnectDialog(self.logger)
        self.trainDlg = TrainDialog(self.logger)

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
        else:
            self.ui.trainDisconnectButton.setEnabled(False)
            self.ui.trainMushroomButton.setEnabled(False)
            self.ui.trainMushroomButton.setIcon(self.res.mushroomB)

        self.ui.configDialogButton.setEnabled(False)
        self.connectionLabel.setPixmap(self.res.disconnectedPix)
        self.connectionLabel_2.setPixmap(self.res.disconnectedBPix)

        # Connecting signals - Dialogs
        self.ui.aboutDialogButton.clicked.connect(self.aboutDlg.show)
        self.ui.configDialogButton.clicked.connect(self.showConfigDlg)
        self.ui.loadSimButton.clicked.connect(self.simDlg.show)
        self.ui.helpButton.clicked.connect(self.helpDlg.show)

        self.ui.simDlg.finished.connect(self.getSim)
        self.ui.configDlg.finished.connect(self.getLoadedParams)

        # Bus connection
        self.ui.connectDialogButton.clicked.connect(self.connectDlg.show)
        self.ui.connectDlg.finished.connect(self.getTermFromDlg)

        # Train connection
        self.ui.trainConnectButton.clicked.connect(self.trainDlg.show)
        self.ui.trainDlg.finished.connect(self.getClientFromDlg)

        # Connecting signals - other buttons
        self.ui.scanNetworkButton.clicked.connect(self.scanNetClicked)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.powerOffElementsButton.clicked.connect(self.turnOffGlobalClicked)

        # Map view
        self.mapScene = GraphicsSceneISA()
        self.mapScene.addPixmap(self.res.mapPixFull.scaledToHeight(920, Qt.SmoothTransformation))
        self.ui.mapGraphicsView = GraphicsViewISA(self.ui.mapWidget)
        self.ui.horizontalLayout.addWidget(self.ui.mapGraphicsView)
        self.ui.mapGraphicsView.setScene(self.mapScene)

        # Ozdobniki
        self.setStyleSheet("""#centralWidget {background-image: url(.//imags//background.png)}
                           """)

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
        self.logger.info('Time from last click ' + str(time() - self.timeStamp))
        self.timeStamp = time()
        vel = 5
        if self.client and self.client.connected:
            if e.key() == Qt.Key_Q or e.key() == Qt.Key_A or e.key() == Qt.Key_Z:
                if e.key() == Qt.Key_Q:
                    self.client.sendMsg(self.trainsLst[0].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_A:
                    self.client.sendMsg(self.trainsLst[0].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[0].changeVelocity(vel, 0))
            if e.key() == Qt.Key_W or e.key() == Qt.Key_S or e.key() == Qt.Key_X:
                if e.key() == Qt.Key_W:
                    self.client.sendMsg(self.trainsLst[1].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_S:
                    self.client. sendMsg(self.trainsLst[1].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[1].changeVelocity(vel, 0))
            if e.key() == Qt.Key_E or e.key() == Qt.Key_D or e.key() == Qt.Key_C:
                if e.key() == Qt.Key_E:
                    self.client.sendMsg(self.trainsLst[2].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_D:
                    self.client.sendMsg(self.trainsLst[2].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[2].changeVelocity(vel, 0))
            if e.key() == Qt.Key_R or e.key() == Qt.Key_F or e.key() == Qt.Key_V:
                if e.key() == Qt.Key_R:
                    self.client.sendMsg(self.trainsLst[3].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_F:
                    self.client.sendMsg(self.trainsLst[3].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[3].changeVelocity(vel, 0))
            if e.key() == Qt.Key_T or e.key() == Qt.Key_G or e.key() == Qt.Key_B:
                if e.key() == Qt.Key_T:
                    self.client.sendMsg(self.trainsLst[4].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_G:
                    self.client.sendMsg(self.trainsLst[4].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[4].changeVelocity(vel, 0))
            if e.key() == Qt.Key_Y or e.key() == Qt.Key_H or e.key() == Qt.Key_N:
                if e.key() == Qt.Key_Y:
                    self.client.sendMsg(self.trainsLst[5].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_H:
                    self.client.sendMsg(self.trainsLst[5].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[5].changeVelocity(vel, 0))
            if e.key() == Qt.Key_U or e.key() == Qt.Key_J or e.key() == Qt.Key_M:
                if e.key() == Qt.Key_U:
                    self.client.sendMsg(self.trainsLst[6].changeVelocity(vel, 1))
                elif e.key() == Qt.Key_J:
                    self.client.sendMsg(self.trainsLst[6].changeVelocity(0, 0))
                else:
                    self.client.sendMsg(self.trainsLst[6].changeVelocity(vel, 0))

        if e.key() == Qt.Key_F1:
            self.helpDlg.show()
        if e.key() == Qt.Key_F2:
            self.logger.info('Auto run config')
            i = self.connectDlg.ui.portComboBox.count()
            self.connectDlg.ui.portComboBox.setCurrentIndex(i - 1)
            self.connectDlg.createTerminal()
            self.scanNetClicked()
            self.configDlg.ui.loadBtnClicked('/config2.xml')
        if e.key() == Qt.Key_F3:
            self.trainDlg.createClient()
        if e.key() == Qt.Key_F4:
            self.logDlg.show()
        if e.key() == Qt.Key_F5:
            for wig in self.wigwagsLst:
                if wig.deviceNo in (1, 2, 3, 4) and wig.zone == u'Wrzeszcz':
                    self.term.writeCommand(wig.setLed([1, 1, 1, 1, 1]))
                    #self.term.writeCommand(wig.setAlarmsLed([0, 0, 0, 0, 0]))
        if e.key() == Qt.Key_F6:
            for wig in self.wigwagsLst:
                if wig.deviceNo in (1, 2, 3, 4) and wig.zone == u'Wrzeszcz':
                    self.term.writeCommand(wig.setLed([0, 0, 0, 0, 0]))
                    #self.term.writeCommand(wig.setAlarmsLed([0, 0, 0, 0, 0]))

        if e.key() == Qt.Key_F7:
            for bal in self.balisesLst:
                if bal.deviceNo == 1 and bal.zone == u'Wrzeszcz':
                    self.term.writeCommand(bal.setINT0(1))

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
            self.logger.info('Tables has been set')
        else:
            self.logger.error('There is no terminal')
        if self.allDataLst:
            self.ui.configDialogButton.setEnabled(True)
        else:
            self.ui.configDialogButton.setEnabled(False)

    def balisaInt(self, b):
        """
        Reading balisa int
        """
        for bal in self.balisesLst:
            if bal.compare(b):
                bal.state = b.state
                self.ui.mapGraphicsView.scene().update()

    def turnOffGlobalClicked(self):
        """
        Turning off elements
        """
        self.term.turnAgentsOff()

    def getClientFromDlg(self, sign):
        """
        On closing train connect dialog get the opened client
        """
        if sign:
            self.client = self.trainDlg.getClient()
            self.logger.info('Connected with Lenz USB/Lan Interface')
            self.connectionLabel_2.setPixmap(self.res.connectedBPix)
        else:
            self.logger.error('Could not find Lenz USB/Lan Interface')
            self.connectionLabel_2.setPixmap(self.res.disconnectedBPix)
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
                        if flag and el.state:
                            self.term.writeCommand(x.setState(el.state))
                            self.term.writeCommand(x.setAlarmsLed(el.alarm))
                        break
            for el in self.configDlg.switchersLst:
                if el.type == '04':
                    self.switchersLst.append(el)
                for x in self.switchersLst:
                    if x.compare(el):
                        x.orientation = el.orientation
                        x.description = el.description
                        x.mapPosition = el.mapPosition
                        if flag and el.state:
                            self.term.writeCommand(x.setState(el.state))
                        break
            for el in self.configDlg.balisesLst:
                balisa = None
                for x in self.balisesLst:
                    if x.compare(el):
                        x.description = el.description
                        x.mapPosition = el.mapPosition
                        if flag and el.state:
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

    def runSim(self):
        """
        Running simulation
        """
        self.simulationRunning = False
        self.t = threading.Thread(name='ISA Simulation',
                                  target=self.__simulation__,
                                  args=(self.e,))
        self.simulationRunning = True
        self.t.start()
        self.t2 = threading.Thread(name='ISA Simulation',
                                  target=self.__skm__,
                                  args=(self.e,))
        self.t2.start()

    def __skm__(self, e):
        while self.simulationRunning:
            self.client.sendMsg(self.trainsLst[6].changeVelocity(10, 0))
            sleep(43)
            self.client.sendMsg(self.trainsLst[6].changeVelocity(0, 0))
            sleep(5)
            self.client.sendMsg(self.trainsLst[6].changeVelocity(10, 1))
            sleep(42)
            self.client.sendMsg(self.trainsLst[6].changeVelocity(0, 0))
            sleep(5)

    def __simulation__(self, e):
        """
        Simulation thread
        """
        self.logger.info('Running simulation')
        while self.simulationRunning:
            for element in self.simulationComLst:
                self.logger.info('Simulation command: ' + unicode(element))
                if '>' in element:
                    el = (element.split('>'))[1].split('\\r')[0]
                    typo = typeDict[el[0:2]]
                    zone = zoneDict[el[2:4]]
                    address = int(el[4:8], 16)
                    if typo == 'Switcher':
                        sw = Switcher()
                        sw.zone = zone
                        sw.deviceNo = address
                        sw.getWrittenState(el[el.find(' ')+1:])
                        for swl in self.switchersLst:
                            if swl.compare(sw):
                                if sw.state == 'Left':
                                    swl.switchLeft()
                                elif sw.state == 'Right':
                                    swl.switchRight()
                com = compile(element, '<string>', 'exec')
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
        self.t._Thread__stop()
        self.t2._Thread__stop()
        self.logger.info('Simulation has been stopped')
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
    mainWindow = ISASimpleWindow()
    mainWindow.show()
    sys.exit(app.exec_())