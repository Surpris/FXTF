#-*- coding: utf-8 -*-

import os
import struct
import datetime

class TestHstLoad(object):
    """ mt4 .hst load test """
    
    def __init__(self, filename):
        with open(filename, 'rb') as fh:
            headersize = 148
            barsize = 60
            cmd  = ['Q','d','d','d','d','Q','L','Q']
            byte = [  8,  8,  8,  8,  8,  8,  4,  8]
            # read header
            self.ver       = struct.unpack('<L'  , fh.read( 4))[0]
            print(self.ver)
            self.copyright = struct.unpack('<64s', fh.read(64))[0].replace('\0', '')
            self.symbol    = struct.unpack('<12s', fh.read(12))[0].replace('\0', '')
            self.period    = struct.unpack('<L'  , fh.read( 4))[0]
            self.digits    = struct.unpack('<L'  , fh.read( 4))[0]
            self.timesign  = struct.unpack('<L'  , fh.read( 4))[0]
            self.last_sync = struct.unpack('<L'  , fh.read( 4))[0]
            self.unused    = struct.unpack('<13L', fh.read(52))[0]
            # calc data size
            filesize = os.path.getsize(filename)
            datasize = filesize - headersize
            self.bars = datasize / barsize
            # read data
            fh.seek(headersize)
            self.data = [[struct.unpack(i, fh.read(j))[0] \
                        for i,j in zip(cmd,byte)] for k in range(self.bars)]
    
    def printHeader(self):
        """ view header data """
        print('ver       ', self.ver)
        print('copyright ', self.copyright)
        print('symbol    ', self.symbol)
        print('period    ', self.period)
        print('digits    ', self.digits)
        print('timesign  ', self.timesign)
        print('last_sync ', self.last_sync)
        print('unused    ', self.unused)
        print('----------')
        print('bars      ', self.bars)
    
    def printData(self):
        """ view history data """
        for i in self.data:
            print(i)
    
    def outputHstTest(self, outputfilename = "outputtest.hst"):
        """ .hst output test """
        with open(outputfilename,'wb') as fh:
            fh.write(struct.pack('L', self.ver))
            fh.write(struct.pack('64s', self.copyright))
            fh.write(struct.pack('12s', self.symbol))
            fh.write(struct.pack('L', self.period))
            fh.write(struct.pack('L', self.digits))
            fh.write(struct.pack('L', self.timesign))
            fh.write(struct.pack('L', self.last_sync))
            fh.write(struct.pack('52s', ""))
            cmd  = 'q4d2qi'
            for i, v in enumerate(self.data):
                fh.write(struct.pack(cmd, self.data[i][0], float(self.data[i][1]),
                        float(self.data[i][2]), float(self.data[i][3]),
                        float(self.data[i][4]), int(self.data[i][5]), 0, 0))
            
        return outputfilename