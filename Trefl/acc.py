# -*- coding: utf-8 -*-
from smbus import SMBus
import socket
import struct
from time import time, sleep
import math

##############################
# Akcelerometr
##############################
class Accelerometer():
    busNum = 1
    BUS = SMBus(busNum)

    LSM = 0x1d
    GYRO = 0x6b

    GYRO_ADD = 0.07 # wartosc kalibrowana z ustawieniami zyroskopu
    DT = 1
    MULTIPLY = 0.98
    FILTR_X = 0
    FILTR_Y = 0

    FIRST = False

    # Adresacja rejestrow
    CTRL_0 = 0x20 # Uruchomienie zyroskopu; Uruchomienie i konfiguracja akcelerometru
    CTRL_1 = 0x23 # Konfiguracja zyroskopu
    CTRL_2 = 0x21 # Test akcelerometru

    # Adresacja MSB i LSB odczytow akcelerometru
    ACC_X_LSB = 0x28 # x
    ACC_X_MSB = 0x29
    ACC_Y_LSB = 0x2A # y
    ACC_Y_MSB = 0x2B
    ACC_Z_LSB = 0x2C # z
    ACC_Z_MSB = 0x2D

    # Adresacja MSB i LSB odczytow zyroskopu
    GYRO_X_LSB = 0x28 # x
    GYRO_X_MSB = 0x29
    GYRO_Y_LSB = 0x2A # y
    GYRO_Y_MSB = 0x2B
    GYRO_Z_LSB = 0x2C # z
    GYRO_Z_MSB = 0x2D

    def __init__(self):
	self.setUp()

    def twos_comp_combine(self, msb, lsb):
        twos_comp = 256*msb + lsb
        if twos_comp >= 32768:
            return twos_comp - 65536
        else:
            return twos_comp

    def setUp(self):
        LSM_WHOAMI = 0b1001001 # id MinIMU

        if self.BUS.read_byte_data(self.LSM, 0x0f) == LSM_WHOAMI:
            print 'Device detected successfully.'
        else:
            print 'No device detected on bus '+str(self.busNum)+'.'

        self.BUS.write_byte_data(self.GYRO, self.CTRL_0, 0b00001111) # uruchomienie zyroskopu
        self.BUS.write_byte_data(self.GYRO, self.CTRL_1, 0b00110000) # konfiguracja zyroskopu
        self.BUS.write_byte_data(self.LSM, self.CTRL_0, 0b01000111) # uruchomienie akcelerometru, czestotliwosc pracy 50Hz
        self.BUS.write_byte_data(self.LSM, self.CTRL_2, 0x00) # test akcelerometru

    def getValues(self):        
        accx = self.twos_comp_combine(self.BUS.read_byte_data(self.LSM, self.ACC_X_MSB), self.BUS.read_byte_data(self.LSM, self.ACC_X_LSB))
        accy = self.twos_comp_combine(self.BUS.read_byte_data(self.LSM, self.ACC_Y_MSB), self.BUS.read_byte_data(self.LSM, self.ACC_Y_LSB))
        accz = self.twos_comp_combine(self.BUS.read_byte_data(self.LSM, self.ACC_Z_MSB), self.BUS.read_byte_data(self.LSM, self.ACC_Z_LSB))

        gyrox = self.twos_comp_combine(self.BUS.read_byte_data(self.GYRO, self.GYRO_X_MSB), self.BUS.read_byte_data(self.GYRO, self.GYRO_X_LSB))
        gyroy = self.twos_comp_combine(self.BUS.read_byte_data(self.GYRO, self.GYRO_Y_MSB), self.BUS.read_byte_data(self.GYRO, self.GYRO_Y_LSB))
        gyroz = self.twos_comp_combine(self.BUS.read_byte_data(self.GYRO, self.GYRO_Z_MSB), self.BUS.read_byte_data(self.GYRO, self.GYRO_Z_LSB))

        rate_gyrox = gyrox*self.GYRO_ADD
        rate_gyroy = gyroy*self.GYRO_ADD
        rate_gyroz = gyroz*self.GYRO_ADD

        if (not self.FIRST):
            self.FIRST = True
            self.gyroXangle = rate_gyrox*self.DT
            self.gyroYangle = rate_gyroy*self.DT
            self.gyroZangle = rate_gyroz*self.DT
        else:
            self.gyroXangle += rate_gyrox*self.DT
            self.gyroYangle += rate_gyroy*self.DT
            self.gyroZangle += rate_gyroz*self.DT

        roll = int(round(math.degrees(math.atan2(accx, accz))))
        pitch = int(round(math.degrees(math.atan2(accy, accz))))

        print "Przechylenie: ", int(round(roll,0)), " Pochylenie: ", int(round(pitch,0))

        self.FILTR_X = self.MULTIPLY*(roll)+(1-self.MULTIPLY)*self.gyroXangle
        self.FILTR_Y = self.MULTIPLY*(pitch)+(1-self.MULTIPLY)*self.gyroYangle

        print "Filtr przechylenie: ", int(round(self.FILTR_X,0)), " Filtr pochylenie: ", int(round(self.FILTR_Y,0))

        return str(roll)+';'+str(pitch)

##############################
# Koniec akcelerometr
##############################

##############################
# Transmisja UDP
##############################
class UDP():
    def __init__(self):
        self.sending()

    def sending(self):
        acc = Accelerometer()

        while True:
            self.send_msg(acc.getValues())

    def send_msg(self, coords):
	send = True

        try:
            (ROLL, PITCH) = str(coords).split(';')[:2]
            print "Przechylenie: "+ROLL+" | Pochylenie: "+PITCH
        except ValueError:
            send = False
            print "Błędna wiadomość."

        if (send):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print 'Failed to create socket'

            my_id_bin = struct.pack("B", 60)   #60 - id
            dev_num_bin = struct.pack(">i", 0)
            tstamp_bin = struct.pack(">q", time())
            x_bin = struct.pack(">i", int(ROLL))
            y_bin = struct.pack(">i", int(PITCH))
            v_bin = struct.pack(">i", int(0))
            z_bin = struct.pack(">i", int(0))

            length_bin = struct.pack("B", (len(my_id_bin + tstamp_bin + x_bin + y_bin + z_bin + v_bin + dev_num_bin) + 1))
            msg = (length_bin + my_id_bin + tstamp_bin + x_bin + y_bin + z_bin + v_bin + dev_num_bin)

            host_data = '192.168.210.100'
            port_data = 11000

            try:
                s.sendto(msg, (host_data, port_data))
                print 'Wyslano!'
            except socket.error, msg:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

        startClock = time()
        while (time()-startClock < 1):
            sleep(0.01)
##############################
# Koniec transmisji
##############################

udp = UDP()
udp.sending()
