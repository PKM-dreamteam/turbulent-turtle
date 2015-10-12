# -*- coding: utf8 -*-
__author__ = 'mikhael'
"""
Module of ISA Dialogs
"""
from PyQt4.QtGui import *
from PyQt4 import uic
from xml.dom import minidom
from trainConnection import trainClient
from terminal import *
import os
from objectsISA import *
import codecs
import sys


def str2lst(st):
        """
        Converting from string contained list of ints to list of ints
        '[1,0,0,0,1]' -> [1,0,0,0,1]
        :return : list of int
        """
        s = st[st.find('[') + 1:st.find(']')]
        lst = []
        for el in s.split(','):
            lst.append(int(el))
        return lst


class AboutDialog(QDialog, object):
    """
    About dialog
    """
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi('.//Forms//AboutDialog.ui', self)
        self.aboutPix = QPixmap('.//imags//tracks.png')
        self.ksdrPix = QPixmap('.//imags//logo//ksdir.png')
        self.wetiPix = QPixmap('.//imags//logo//weti.png')
        self.pgnPix = QPixmap('.//imags//logo//pg_n.png')
        self.pgPix = QPixmap('.//imags//logo//pg.png')

        self.ui.aboutImageLabel.setPixmap(self.aboutPix)
        self.ui.eti.setPixmap(self.wetiPix)
        self.ui.ksdir.setPixmap(self.ksdrPix)
        self.ui.pg.setPixmap(self.pgnPix)
        self.ui.closeDlgButton.clicked.connect(self.close)

    def keyPressEvent(self, e):
        """
        Key to unlocked virtual terminal - Alt
        """
        if e.key() == Qt.Key_Alt:
            self.ui.pg.setPixmap(self.pgPix)


class HelpDialog(QDialog, object):
    """
    About dialog
    """
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi('.//Forms//HelpDialog.ui', self)
        self.ui.closeDlgButton.clicked.connect(self.close)

class ConfigDialog(QDialog, object):
    """
    Configuration dialog
    """
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi('.//Forms//ConfigDialog.ui', self)
        # Setting up configuration path
        self.ui.pathLineEdit.setText(os.getcwd() + '/config.xml')
        if os.path.isfile(os.getcwd() + '/config.xml'):
            self.ui.pathLoadButton.setEnabled(True)
        else:
            self.ui.pathLoadButton.setEnabled(False)
        self.ui.pathSaveButton.setEnabled(True)
        # Connecting load path
        self.ui.pathLineEdit.textChanged.connect(self.loadPathCheck)
        # Connecting Load button
        self.ui.pathLoadButton.clicked.connect(self.loadBtnClicked)
        self.ui.pathSaveButton.clicked.connect(self.saveBtnClicked)
        self.ui.closeDlgButton.clicked.connect(self.close)
        self.ui.stateLoadCheckBox.stateChanged.connect(self.setStateLoad)
        self.stateLoad = False
        self.switchersLst = []
        self.wigwagsLst = []
        self.balisesLst = []

    def setStateLoad(self):
        """
        Setting state load
        """
        if self.ui.stateLoadCheckBox.checkState() == Qt.Checked:
            self.stateLoad = True
        else:
            self.stateLoad = False

    def loadPathCheck(self, st):
        """
        Checking xml file
        :param st: QString of path
        """
        if os.path.isfile(str(st)) and (self.balisesLst or self.switchersLst
                                        or self.wigwagsLst):
            self.ui.pathLoadButton.setEnabled(True)
        else:
            self.ui.pathLoadButton.setEnabled(False)

    def loadBtnClicked(self, st):
        """
        Loading xml config file
        """
        self.reject()
        if not st:
            filePath = str(self.ui.pathLineEdit.text())
        else:
            filePath = os.getcwd() + st
        sys.stdout.write('Opening file ' + filePath + '<br>')
        xmlTree = minidom.parse(filePath)#, encoding='utf-8')
        tags = ['switcher', 'wigwag', 'balisa']
        lst = [[], [], []]
        sys.stdout.write('Parsing data <br>')
        msw = Multiswitcher()
        msw.zone = u'Kiełpinek'
        msw.deviceNo = 1
        msw.mapPosition = (5310, 370)
        for i in range(3):
            for pkmChild in xmlTree.getElementsByTagName(tags[i]):
                if i == 0:
                    element = Switcher()
                    orie = str(pkmChild.getAttribute('orientation'))
                    if orie:
                        element.orientation = int(orie)
                    else:
                        element.orientation = 0
                elif i == 1:
                    element = Wigwag()
                elif i == 2:
                    element = Balisa()
                element.deviceNo = int(str(pkmChild.getAttribute('address')))
                element.zone = unicode(pkmChild.getAttribute('zone'))
                # Multiswitcher
                if element.deviceNo in [1, 2, 11, 12] and element.zone == u'Kiełpinek':
                    msw.swLst.append(element)
                if i == 2:
                    ints = str2lst(pkmChild.getAttribute('state'))
                    element.int0 = ints[0]
                    element.int1 = ints[1]
                else:
                    element.state = pkmChild.getAttribute('state')

                element.mapPosition = (int(pkmChild.getAttribute('mapX')),
                                       int(pkmChild.getAttribute('mapY')))
                element.description = pkmChild.childNodes[0].nodeValue
                lst[i].append(element)
        sys.stdout.write('Data read <br>')
        lst[0].append(msw)
        self.switchersLst, self.wigwagsLst, self.balisesLst = lst
        self.accept()

    def saveBtnClicked(self):
        """
        Saving configuration to xml
        """
        path = str(self.ui.pathLineEdit.text())
        sys.stdout.write('Preparing to write configuration to file <br>')
        doc = minidom.Document()
        root = doc.createElement('root')
        root.setAttribute('date', strftime("%c"))
        switchersXML = doc.createElement('Switchers')
        switchersXML.setAttribute('quantity', str(len(self.switchersLst)))
        wigwagsXML = doc.createElement('Wigwags')
        wigwagsXML.setAttribute('quantity', str(len(self.wigwagsLst)))
        balisesXML = doc.createElement('Balises')
        balisesXML.setAttribute('quantity', str(len(self.balisesLst)))
        nodeLst = [switchersXML, wigwagsXML, balisesXML]
        elLst = [self.switchersLst, self.wigwagsLst, self.balisesLst]
        tags = ['switcher', 'wigwag', 'balisa']
        for i in range(3):
            for el in sorted(elLst[i]):
                # Create switcher Element
                pkmChild = doc.createElement(tags[i])
                pkmChild.setAttribute('address', unicode(el.deviceNo))
                pkmChild.setAttribute('zone', unicode(el.zone))
                if i == 0:
                    pkmChild.setAttribute('orientation', unicode(el.orientation))
                if i == 2:
                    stat = [el.int0, el.int1]
                    pkmChild.setAttribute('state', unicode(stat))
                else:
                    if not el.state == 'Unknown':
                        pkmChild.setAttribute('state', unicode(el.state))
                pkmChild.setAttribute('mapX', str(el.mapPosition[0]))
                pkmChild.setAttribute('mapY', str(el.mapPosition[1]))
                pkmChild.appendChild(doc.createTextNode(unicode(el.description)))
                nodeLst[i].appendChild(pkmChild)
            # Write Text
            root.appendChild(nodeLst[i])
        doc.appendChild(root)
        sys.stdout.write('Writing file: ' + path + '<br>')
        doc.writexml(codecs.open(path, 'wb', 'utf-8'), indent='\t', addindent='\t', newl='\n', encoding='utf-8')
        doc.unlink()
        sys.stdout.write('Configuration has been saved <br>')
        self.reject()
        self.close()


class SimDialog(QDialog, object):
    """
    Configuration dialog
    """
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi('.//Forms//SimDialog.ui', self)
        self.comLst = []
        # Setting up configuration path
        self.ui.pathLineEdit.setText(os.getcwd() + '/simulation.xml')
        if os.path.isfile(os.getcwd() + '/simulation.xml'):
            self.ui.pathLoadButton.setEnabled(True)
        else:
            self.ui.pathLoadButton.setEnabled(False)
        # Connecting load path
        self.ui.pathLineEdit.textChanged.connect(self.loadPathCheck)
        # Connecting Load button
        self.ui.pathLoadButton.clicked.connect(self.loadBtnClicked)
        self.ui.closeDlgButton.clicked.connect(self.close)

    def loadPathCheck(self, st):
        """
        Checking xml file
        :param st: QString of path
        """
        if os.path.isfile(str(st)):
            self.ui.pathLoadButton.setEnabled(True)
        else:
            self.ui.pathLoadButton.setEnabled(False)

    def loadBtnClicked(self):
        """
        Loading xml simulation file
        """
        self.reject()
        filePath = str(self.ui.pathLineEdit.text())
        sys.stdout.write('Opening simulation file ' + filePath + '<br>')
        xmlTree = minidom.parse(filePath)
        tags = [u'train', u'switcher', u'wigwag', u'sleep', u'multiswitcher']
        sys.stdout.write('Parsing simulation data <br>')
        lst = []
        for simChild in xmlTree.childNodes[0].childNodes:
            if not (simChild.nodeName == '#text' or simChild.nodeName == '#comment'):
                if simChild.tagName == tags[0]:
                    tr = Train(int(simChild.getAttribute('address')))
                    cmd = tr.changeVelocity(int(simChild.getAttribute('velocity')),
                                            bool(int(simChild.getAttribute('direction'))))
                    lst.append('self.client.sendMsg(\"\"\"' + cmd + '\"\"\")')
                    lst.append('sleep(.2)')
                elif simChild.tagName == tags[1]:
                    sw = Switcher()
                    sw.deviceNo = int(simChild.getAttribute('address'))
                    sw.zone = unicode(simChild.getAttribute('zone'))
                    cmd = ''
                    if simChild.getAttribute('state') == 'Left':
                        cmd = sw.switchLeft()
                    elif simChild.getAttribute('state') == 'Right':
                        cmd = sw.switchRight()
                    lst.append('self.term.writeCommand(' + str(cmd) + ')')
                    lst.append('sleep(.2)')
                    cmd = sw.powerOff()
                    lst.append('self.term.writeCommand(' + str(cmd) + ')')
                elif simChild.tagName == tags[2]:
                    ww = Wigwag()
                    ww.deviceNo = int(simChild.getAttribute('address'))
                    ww.zone = str(simChild.getAttribute('zone'))
                    led = str2lst(simChild.getAttribute('led'))
                    cmd = ww.setLed(led)
                    lst.append('self.term.writeCommand(' + str(cmd) + ')')
                    if simChild.getAttribute('aled'):
                        aled = str2lst(simChild.getAttribute('aled'))
                        cmd = ww.setAlarmsLed(aled)
                        lst.append('self.term.writeCommand(' + str(cmd) + ')')
                        lst.append('sleep(.2)')
                elif simChild.tagName == tags[3]:
                    t = simChild.getAttribute('time')
                    lst.append('sleep(' + t + ')')
                elif simChild.tagName == tags[4]:
                    sw = Multiswitcher()
                    sw.deviceNo = int(simChild.getAttribute('address'))
                    sw.zone = unicode(simChild.getAttribute('zone'))
                    cmd = ''
                    if simChild.getAttribute('state') == 'Straight':
                        for cmd in [['>01020001 31 \r\n'], ['>01020002 32 \r\n'], ['>0102000b 32 \r\n'], ['>0102000c 31 \r\n']]:
                            lst.append('self.term.writeCommand(' + str(cmd) + ')')
                        lst.append('sleep(.2)')
                        for cmd in [['>01020001 30 \r\n'], ['>01020002 30 \r\n'], ['>0102000b 30 \r\n'], ['>0102000c 30 \r\n']]:
                            lst.append('self.term.writeCommand(' + str(cmd) + ')')
                    elif simChild.getAttribute('state') == 'Cross':
                        for cmd in [['>01020001 32 \r\n'], ['>01020002 31 \r\n'], ['>0102000b 31 \r\n'], ['>0102000c 32 \r\n']]:
                            lst.append('self.term.writeCommand(' + str(cmd) + ')')
                        lst.append('sleep(.2)')
                        for cmd in [['>01020001 30 \r\n'], ['>01020002 30 \r\n'], ['>0102000b 30 \r\n'], ['>0102000c 30 \r\n']]:
                            lst.append('self.term.writeCommand(' + str(cmd) + ')')
        sys.stdout.write('Simulation read <br>')
        self.comLst = lst
        self.accept()


class ConnectDialog(QDialog, object):
    """
    Configuration dialog
    """
    def __init__(self, log):
        QDialog.__init__(self)
        self.term = None
        self.logger = log
        self.ui = uic.loadUi('.//Forms//ConnectDialog.ui', self)
        # Setting up serial port comboBox
        for p in CommunicationModule.getPortList():
            self.ui.portComboBox.addItem(p)

        # Connect button: - serial port form list
        self.ui.portConnectButton.clicked.connect(self.createTerminal)
        self.ui.portDisconnectButton.clicked.connect(self.closeTerminal)
        self.ui.closeDlgButton.clicked.connect(self.close)
        # Disable button
        if self.term:
            self.ui.portConnectButton.setEnabled(False)
            self.ui.portDisconnectButton.setEnabled(True)
        else:
            self.ui.portConnectButton.setEnabled(True)
            self.ui.portDisconnectButton.setEnabled(False)

    def createTerminal(self):
        """
        Creating terminal
        """
        try:
            port = str(self.ui.portComboBox.currentText())
            self.term = CommunicationModule(port=port, baudRate=500000,
                                            parity='N')
            self.term.xlogger = self.logger
            self.term.start()
            self.accept()
        except serial.SerialException, e:
            sys.stderr.write(str(e) + '<br>')
            self.term = None
            self.reject()

    def getTerminal(self):
        """
        Getting a terminal
        :return: opened terminal, or None
        """
        if self.term:
            return self.term
        else:
            sys.stderr.write('Try to open terminal, but failed <br>')
            return None

    def closeTerminal(self):
        """
        Closing terminal
        """
        self.term.alive = False
        self.close()


class TrainDialog(QDialog, object):
    """
    Configuration dialog
    """
    def __init__(self, log):
        QDialog.__init__(self)
        self.client = trainClient()
        self.ui = uic.loadUi('.//Forms//TrainDialog.ui', self)
        self.client.logger = log
        # IP mask
        self.regex = QRegExp("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        self.validator = QRegExpValidator(self.regex, self.ui.ipLineEdit)
        self.ui.ipLineEdit.setValidator(self.validator)
        self.ui.ipLineEdit.setText('127.0.0.1')

        # Connect button
        self.ui.trainConButton.clicked.connect(self.createClient)
        self.ui.trainDisButton.clicked.connect(self.disconnectClient)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.localhostCheckBox.stateChanged.connect(self.localhost)

    def createClient(self):
        """
        Creating TCP/IP client
        """
        state, pos = self.validator.validate(self.ui.ipLineEdit.text(), 0)
        if state == QValidator.Acceptable:
            self.client.connect(str(self.ui.ipLineEdit.text()))
            self.accept()
        else:
            sys.stderr.write('Address ' + self.ipLineEdit.text() + ' is invalid <br>')
            self.reject()

    def getClient(self):
        """
        Getting an IP Client
        :return: opened IP client, or None
        """
        if self.client.connected:
            return self.client
        else:
            sys.stderr.write('Try to get Train Client, but failed <br>')
            return None

    def localhost(self):
        if self.ui.localhostCheckBox.checkState() == Qt.Checked:
            self.ui.ipLineEdit.setText('127.0.0.1')
        else:
            self.ui.ipLineEdit.setText('192.168.210.200')

    def disconnectClient(self):
        """
        Closing terminal
        """
        if self.client.connected:
            self.client.disconnect()
        self.close()


class LogDialog(QDialog, object):
    """
    Configuration dialog
    """
    def __init__(self):
        QDialog.__init__(self)
        self.ui = uic.loadUi('.//Forms//logger.ui', self)