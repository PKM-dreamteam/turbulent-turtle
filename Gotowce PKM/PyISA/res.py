__author__ = 'Mikhael'

from PyQt4.QtGui import QPixmap, QIcon


class Res(object):
    def __init__(self):
        #self.mapPix = QPixmap('.//imags//maps//Strzyza_tmp_map.png')
        self.mapPix = QPixmap('.//imags//maps//Wrzeszcz_map.png')
        self.mapPixFull = QPixmap('.//imags//maps//Full_map.jpg')
        self.connectedPix = QPixmap('.//imags//connection//connected.png')
        self.virconnectedPix = QPixmap('.//imags//connection//virconnected.png')
        self.disconnectedPix = QPixmap('.//imags//connection//disconnected.png')

        self.connectedBPix = QPixmap('.//imags//connection//connectedB.png')
        self.disconnectedBPix = QPixmap('.//imags//connection//disconnectedB.png')

        self.switcherPix = [QPixmap('.//imags//switchers//left.png'),
                            QPixmap('.//imags//switchers//right.png')]
        self.switcherLightPix = [QIcon(QPixmap('.//imags//switchers//red.png')),
                                 QIcon(QPixmap('.//imags//switchers//green.png'))]
        self.wigwagOnIco = [
            QIcon(QPixmap('.//imags//wigwag//top_green_on.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_yellow_on.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_red_on.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_yellow_on.png')),
            QIcon(QPixmap('.//imags//wigwag//dow_white_on.png'))]
        self.wigwagBlinkIco = [
            QIcon(QPixmap('.//imags//wigwag//top_green_blink.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_yellow_blink.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_red_blink.png')),
            QIcon(QPixmap('.//imags//wigwag//mid_yellow_blink.png')),
            QIcon(QPixmap('.//imags//wigwag//dow_white_blink.png'))]
        self.wigwagOffIco = [QIcon(QPixmap('.//imags//wigwag//top_off.png')),
                             QIcon(QPixmap('.//imags//wigwag//mid_off.png')),
                             QIcon(QPixmap('.//imags//wigwag//mid_off.png')),
                             QIcon(QPixmap('.//imags//wigwag//mid_off.png')),
                             QIcon(QPixmap('.//imags//wigwag//dow_off.png'))]
        self.background = QPixmap('.//imags//background.png')
        self.fall = QPixmap('.//imags//fall.png')

        self.icons = [QPixmap('.//imags//icons//train.png'),
                      QPixmap('.//imags//icons//train.png'),
                      QPixmap('.//imags//icons//switcher.png'),
                      QPixmap('.//imags//icons//wigwag.png'),
                      QPixmap('.//imags//icons//eurobalisa.png'),
                      QPixmap('.//imags//icons//train.png'),
                      QPixmap('.//imags//icons//train.png')]

        self.trainIco = [QPixmap('.//imags//trains//tr1.png'),
                         QPixmap('.//imags//trains//tr1.png'),
                         QPixmap('.//imags//trains//tr2.png'),
                         QPixmap('.//imags//trains//tr2.png'),
                         QPixmap('.//imags//trains//tr3.png'),
                         QPixmap('.//imags//trains//tr4.png'),
                         QPixmap('.//imags//trains//tr5.png')]

        self.trainGIco = [QPixmap('.//imags//trains//tr1.png'),
                          QPixmap('.//imags//trains//tr1.png'),
                          QPixmap('.//imags//trains//tr2.png'),
                          QPixmap('.//imags//trains//tr2.png'),
                          QPixmap('.//imags//trains//tr3.png'),
                          QPixmap('.//imags//trains//tr4.png'),
                          QPixmap('.//imags//trains//tr5.png')]

        self.mushroomA = QIcon(QPixmap('.//imags//mush//mushA.png'))
        self.mushroomB = QIcon(QPixmap('.//imags//mush//mushB.png'))
        self.mushroomBG = QIcon(QPixmap('.//imags//mush//mushBG.png'))

