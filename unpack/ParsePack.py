# -*- coding:UTF-8 -*-
#Author:Tony
#Company:Horizon Robot
#Time:Jun 5 2017
#Example:

import sys
import os
import Frame_pb2 as adas_input
import struct
import numpy as np
import cv2


################# class #####################
class Pack():
    def __init__(self):
        self.frameids = []
        self.version = ""
        self.idxs = []
        self.laneInfos = []
        self.protoLens = []
        self.protoOffsets = []
        self.imgLens = []
        self.imgOffsets = []
        self.filePath = ""
        self.fd = file

    def reset(self):
        pass

    def loadFile(self, fpath):
        """
        :param fpath:
        :return: 0: keep pack file load last
                 1: load new pack
                 -1: can't open the pack
        """
        if file:
            if self.fd.name == fpath and (not self.fd.closed):
                # print "pack file is the same to Last, don't load again"
                return 0
        self.filePath = fpath
        try:
            if not self.fd.closed:
                self.fd.close()
            print fpath
            self.fd = file(fpath, 'rb')
            fd = self.fd
        except IOError:
            print "WARN: open results file failed:", fpath
            return -1
        print "AdasData: parsing results file: ", fpath
        resLens = []
        resOffsets = []
        self.fd.seek(0, os.SEEK_END)
        fsize = self.fd.tell() - 1
        self.fd.seek(0, os.SEEK_SET)
        buf = self.fd.read(4)
        version = struct.unpack("i", buf)
        print "Pack.Parsing: proto version ", version
        offset = 4
        self.frame_cnt_res = 0
        while offset <= fsize:
            buf = fd.read(4)
            if not buf:
                print 'EOF'
                break
            tmp = struct.unpack("i", buf)
            size = tmp[0]
            resLens.append(size)
            offset += 4
            resOffsets.append(offset)
            offset += size
            self.frame_cnt_res += 1
            fd.seek(0)
            fd.seek(offset)

        self.protoLens = resLens[::2]
        self.protoOffsets = resOffsets[::2]
        self.imgLens = resLens[1::2]
        self.imgOffsets = resOffsets[1::2]
        self.frameids = []
        print "len : ", len(self.protoLens)
        '''
        for i in range(len(self.protoLens)):
            fd.seek(self.protoOffsets[i])
            inputPack = adas_input.Frame()
            buf = fd.read(self.protoLens[i])
            if len(buf) == self.protoLens[i]:
                inputPack.ParseFromString(buf)
                self.frameids.append(inputPack.frame_id)
                print inputPack.frame_id
        '''
        return 1

    def getFrameByFrameid(self, frameid):
        if frameid in self.frameids:
            i = self.frameids.index(frameid)
        else:
            raise ValueError('frameid is no in pack!')
        return self.getFrameByIdx(i)

    def getFrameByIdx(self, i):
        if i > len(self.protoOffsets) - 1:
            raise IndexError("This is the frame out of pack")
        self.fd.seek(self.protoOffsets[i])
        frame = adas_input.Frame()
        buf = self.fd.read(self.protoLens[i])
        if len(buf) == self.protoLens[i]:
            frame.ParseFromString(buf)
            return frame

    def getImageByIdx(self, i):
        self.fd.seek(self.imgOffsets[i])
        buf = self.fd.read(self.imgLens[i])
        abuf = np.asarray(bytearray(buf), dtype='uint8')
        if len(buf) == self.imgLens[i]:
            pic = cv2.imdecode(abuf, cv2.IMREAD_COLOR)
            return pic

    def getImageByFrameid(self, frameid):
        if frameid in self.frameids:
            i = self.frameids.index(frameid)
        else:
            raise ValueError('frameid is no in pack!')
        return self.getImageByIdx(i)

    def getIdxNum(self):
        """
         Idx : 0 ~  len(Idx[]) - 1
        :return:
        """
        return len(self.imgOffsets)

    def getFrameIdList(self):
        return self.frameids

    def closeFile(self):
        if not self.fd.closed:
            self.fd.close()

############### main test ###################
if __name__ == "__main__":
    # fpath = raw_input("Please input your file path:")
    fpath = "/home/qilu-dong/Share/test.pack"
    pack = Pack()
    pack.loadFile(fpath)
    test = 1
