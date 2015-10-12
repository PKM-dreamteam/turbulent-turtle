__author__ = 'mikhael'
from objectsISA import *


class AltTerm(object):
    def __init__(self):
        self.xlogger = None

    def writeCommand(self, command):
        for c in command:
            self.xlogger.warning(c)

    def getPortList(self):
        return ['None']

    def turnAgentsOff(self):
        return None

    def scanElements(self):
        log = '''>02010002 00 00 00 00
>02010001 00 00 00 00
>010001FE 30 00 00 00
>010001FF 30 00 00 00
>0300020A 30 00 C0 00
>0300020B 30 00 C7 00
>0200012A 00 00 00 00
>0200013A 00 00 00 00
>0200014A 00 00 00 00
>0200015A 00 00 00 00
>0200017A 00 00 00 00
>0200018A 00 00 00 00
>0200019A 00 00 00 00
>0200012B 00 00 00 00
>0200013B 00 00 00 00
>0200014B 00 00 00 00
>0200015B 00 00 00 00
>0200017B 00 00 00 00
>0200018B 00 00 00 00
>0200019B 00 00 00 00
>01050001 30 00 80 00
>01010001 30 00 40 00
>01050026 30 00 80 00
>010001FD 30 00 00 00
>01050028 30 00 40 00
>0105001A 30 00 80 00
>0105000E 30 00 80 00
>01050002 30 00 40 00
>01010002 30 00 40 00
>01050025 30 00 80 00
>01050027 31 00 40 00
>01050029 30 00 80 00
>01050019 30 00 40 00
>0105000D 30 00 80 00
>0300012A 30 00 00 00
>0300013A 30 00 00 00
>0300014A 30 00 40 00
>0300015A 30 00 00 00
>0300017A 30 00 40 00
>0300018A 30 00 00 00
>0300019A 30 00 00 00
>0300012B 30 00 C7 00
>0300013B 30 00 47 00
>0300014B 30 00 C7 00
>0300015B 30 00 C7 00
>0300017B 30 00 C7 00
>0300018B 30 00 C7 00
>0300019B 30 00 C7 00'''.split('\n')
        self.xlogger.warning('<br>'.join(log))
        log = list(set(log))
        log.sort()
        switchersLst = []
        wigwagsLst = []
        balisesLst = []
        for el in log:
            if len(el) >= 20:
                typo = typeDict[el[1:3]]
                zone = zoneDict[el[3:5]]
                address = int(el[5:9], 16)
                if typo == 'Switcher':
                    sw = Switcher()
                    sw.zone = zone
                    sw.deviceNo = address
                    sw.checkState(el[el.find(' ')+1:])
                    switchersLst.append(sw)
                elif typo == 'Wigwag':
                    ww = Wigwag()
                    ww.zone = zone
                    ww.deviceNo = address
                    ww.checkState(el[el.find(' ')+1:])
                    wigwagsLst.append(ww)
                elif typo == 'Balisa':
                    ba = Balisa()
                    ba.zone = zone
                    ba.deviceNo = address
                    #ba.checkState(el[el.find(' ')])
                    balisesLst.append(ba)
        self.xlogger.info('Elements has been read')
        return switchersLst, wigwagsLst, balisesLst
