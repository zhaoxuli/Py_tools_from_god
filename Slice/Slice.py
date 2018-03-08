# -*- coding:UTF-8 -*-

# from PyQt4.QtGui import *
# from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4 import QtGui
# from pyqtgraph.Qt import QtGui,QtCore;
import sys
import os
import numpy as np
import cv2
import time
import logging
[scriptDir,scriptName]  = os.path.split(os.path.abspath(__file__))
os.chdir(scriptDir)
sys.path.append('./')
sys.path.append('../')
import copy
from functools import wraps
import tkFileDialog

import cProfile

import unpack.ParsePack as ParsePack
import thread
import Queue
import time

def fn_timer(function):
  @wraps(function)
  def function_timer(*args, **kwargs):
    t0 = time.time()
    result = function(*args, **kwargs)
    t1 = time.time()
    print ("Total time running %s: %s seconds" %
        (function.func_name, str(t1-t0))
        )
    return result
  return function_timer


QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf-8"))
class SliceTool(QtGui.QWidget):
    def __init__(self,parent=None):
        super(SliceTool,self).__init__(parent)
        self.setWindowTitle(self.tr("ADAS Slice 工具"))
        self.Logo_img = cv2.imread("./rec/imshow.jpg")             # 读取默认显示文件
        self.image_width = 960
        self.image_height = 540

        #check slice point 
        self.signal_A = 0 
        self.cur_frame_idx = -1 
        self.p_A = -1
        self.p_B = -1
        self.slices = []
        
        #pack section
        self.pack = ParsePack.Pack()
        self.pack_path = ''
        self.pack_length = 0
        self.pack_name = ''

        #draw 
        self.draw = 0
        self.draw_A = -1
        self.draw_B = -1
        self.need_draw = 0
        self.rects = []

        #checkbox
        self.checkboxes = []        
        self.checkboxes_bn = []
        self.slice_interval = []

        #timer setup 
        self.timer = QtCore.QTimer();  # 设置计时器
        self.timer.timeout.connect(self.NextFrame); 

        # UI控件布局管理
        Layout_main = QtGui.QGridLayout(self)                 #主布局管理器
        Layout_imshow = QtGui.QGridLayout(self)               #承载imshow QLabel的布局管理器
        Layout_bar = QtGui.QHBoxLayout(self)                  #承载滑动条的布局管理器
        Layout_button = QtGui.QHBoxLayout(self)               #承载众多button的布局管理器
        self.layout_checkbox = QtGui.QGridLayout(self)
        Layout_main.addLayout(Layout_imshow,0,0)        #布局管理其间的布局
        Layout_main.addLayout(Layout_bar,1,0)
        Layout_main.addLayout(Layout_button, 2, 0)
        Layout_main.addLayout(self.layout_checkbox, 0, 1)
        

        # UI控件初始化
        self.label_image = QtGui.QLabel()                                     #图像显示控件QLabel
        self.label_info = QtGui.QLabel()

        self.label_image.setFixedSize(self.image_width,self.image_height)
        self.button_pre = QtGui.QPushButton(self.tr("||< 上十帧(j)"))                   #上一帧按钮控件
        self.button_play = QtGui.QPushButton(self.tr("播放 >"))                    #播放/暂停按钮控件
        self.button_next = QtGui.QPushButton(self.tr("下一帧 >||(k)"))                  #下一帧按钮控件
        self.button_Load = QtGui.QPushButton(self.tr('载入'))
        self.button_slice = QtGui.QPushButton(self.tr('slice'))
        self.slider = QtGui.QSlider(1)                            #滑动条控件

        # UI控件大小和位置
        self.button_pre.setFixedSize(100, 50)
        self.button_play.setFixedSize(100, 50)
        self.button_next.setFixedSize(100, 50)
        self.button_Load.setFixedSize(100, 50)
        self.button_slice.setFixedSize(100, 50)
        #将控件布局到布局管理器中
        Layout_imshow.addWidget(self.label_image, 0, 0)

        Layout_button.addWidget(self.button_pre)
        Layout_button.addWidget(self.button_play)
        Layout_button.addWidget(self.button_next)
        Layout_button.addWidget(self.button_Load)
        Layout_button.addWidget(self.button_slice)
        Layout_button.addWidget(self.label_info)
        Layout_bar.addWidget(self.slider)

        self.connect(self.button_play, QtCore.SIGNAL("clicked()"), self.Play)
        self.connect(self.button_Load, QtCore.SIGNAL('clicked()'), self.LoadPack)
        self.connect(self.button_next,QtCore.SIGNAL("clicked()"),self.NextFrame)
        self.connect(self.button_pre,QtCore.SIGNAL("clicked()"),self.PreFrame)
        self.connect(self.button_slice,QtCore.SIGNAL("clicked()"),self.SlicePack)
        self.connect(self.slider,QtCore.SIGNAL("sliderReleased()"), self.SliderMove)
        #self.connect(self.slider,QtCore.SIGNAL("valueChanged (int)"), self.SliderStep)
    def SlicePack(self):
        for idx, A_B in enumerate(self.slices):
            self.Pack2Img(A_B[0], A_B[1], idx)

    def Pack2Img(self, start, end, idx):
        if self.pack_name == '':
            print 'no pack loaded'
            return
        if start > end:
            print 'end should be larger than start'
            return
        save_path = self.pack_name + '_' + str(idx)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        i = start
        while i < end:
            a_time = int(time.time())
            pic = self.pack.getImageByIdx(i)
            cv2.imwrite(save_path + '/' + self.pack_name + '_' + str(a_time) + '_' + str(i) + '.png', pic)
            i = i + 1

    #load pack
    #@fn_timer
    def LoadPack(self):
        self.pack_path = str(QtGui.QFileDialog.getOpenFileName(self,'Open Pack', '', '*.*', None, QtGui.QFileDialog.DontUseNativeDialog))
        self.pack.loadFile(self.pack_path)
        self.pack_length = int(self.pack.protoLens[0]) 
        self.pack_name = self.pack_path.split('/')[-1].split('.')[0]

    #@fn_timer
    def Refresh(self):
        if self.cur_frame_idx < 0 or self.cur_frame_idx >= self.pack_length - 1:
            self.cur_frame_idx = 0
            self.timer.stop()
            self.button_play.setText(self.tr("播放"))
            pass 
        pic = self.pack.getImageByIdx(self.cur_frame_idx)
        pic = cv2.resize(pic, (self.image_width, self.image_height))
        image1 = QtGui.QImage(pic.tostring(), self.image_width, self.image_height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.label_image.setPixmap(QtGui.QPixmap(image1))

    #play video
    def Play(self):
        print "play"
        if self.timer.isActive():
            self.timer.stop()
            self.button_play.setText(self.tr("播放"))
        else:
            self.timer.start(1000 / 50.0)
            self.button_play.setText(self.tr("停止"))

    #next frame
    #@fn_timer
    def NextFrame(self):
        self.cur_frame_idx = self.cur_frame_idx + 1
        self.Refresh()

    #pre frame
    def PreFrame(self):
        self.cur_frame_idx = self.cur_frame_idx - 1
        self.Refresh() 

    #slice start point
    def SlicePointA(self):
        print "SlicePointA"
        self.signal_A = 1
        self.p_A = self.cur_frame_idx

    #draw checkboxes dynamically
    def DrawCheckBoxes(self):
        idx = len(self.checkboxes)
        self.checkboxes.append(QtGui.QCheckBox(str(idx)))
        self.checkboxes[-1].setChecked(True)
        self.checkboxes[-1].toggled.connect(lambda: self.CheckBoxState())
        self.checkboxes_bn.append(QtGui.QPushButton('slice interval'))
        self.slice_interval.append(5)
        self.checkboxes_bn[-1].clicked.connect(self.ShowSliceIntervalDialog)
        self.layout_checkbox.addWidget(self.checkboxes[-1])
        self.layout_checkbox.addWidget(self.checkboxes_bn[-1])
       

    def ShowSliceIntervalDialog(self): 
        num,ok = QtGui.QInputDialog.getInt(self,"integer input dualog","enter a number")
        if ok:
            print ok
         

 
    def CheckBoxState(self):
        result_checkboxes = []
        result_rects = []
        result_slices = []
        result_checkboxes_bn = []
        print len(self.rects)
        #delete unchecked boxes
        for idx in range(len(self.checkboxes)):
            if self.checkboxes[idx].isChecked():
                result_checkboxes.append(self.checkboxes[idx])
                result_rects.append(self.rects[idx])
                result_slices.append(self.slices[idx])
                result_checkboxes_bn.append(self.checkboxes_bn[idx])
                continue
            self.checkboxes[idx].setParent(None)
            self.checkboxes_bn[idx].setParent(None)
        self.checkboxes = result_checkboxes
        self.rects = result_rects
        self.slices = result_slices
        self.checkboxes_bn = result_checkboxes_bn
        
    #slice end point
    def SlicePointB(self):
        if self.signal_A < 1:
            print "no start point"
        else:
            print "SlicePointB"
            self.p_B = self.cur_frame_idx
            self.slices.append([self.p_A, self.p_B])
            #self.Pack2Img()
            self.draw = 1
            if self.draw_A != self.p_A or self.draw_B != self.p_B:
                self.need_draw = 1
            self.draw_A = self.p_A
            self.draw_B = self.p_B
            self.p_A = -1
            self.p_B = -1
            self.DrawCheckBoxes()
            self.signal_A = 0

    def SliderStep(self, value):
        if value == self.cur_frame_idx -1 or value == self.cur_frame_idx + 1:
            self.SliderMove()
        else:
            pass

    # @fn_timer
    def SliderMove(self):
        new_frame_idx = self.pack_length * float(self.slider.value()) / 100.0
        self.cur_frame_idx = int(new_frame_idx) 
        self.CheckIndex()
        self.Refresh()
    
    def CheckIndex(self):
        if self.cur_frame_idx >= self.pack_length:
            self.cur_frame_idx = self.pack_length - 1 
        elif self.cur_frame_idx <= 0:
            self.cur_frame_idx = 0

 
    #keyboard event
    @fn_timer
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:
            self.SlicePointA()
        elif event.key() == QtCore.Qt.Key_V:
            self.SlicePointB()
        elif event.key() == QtCore.Qt.Key_J:
            self.PreFrame()
        elif event.key() == QtCore.Qt.Key_K:
            self.NextFrame()
        
    #Painter event
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.DrawRectangle(qp)
        qp.end()

    def DrawRectangle(self, qp):
        if self.draw == 0: return 
        point = self.slider.pos()
        slider_w = self.slider.width()
        x = int(point.x())
        y = int(point.y())
        A_x = x + (float(self.draw_A) / self.pack_length) * int(slider_w) 
        B_x = x + (float(self.draw_B) / self.pack_length) * int(slider_w)  
        w = B_x - A_x
        h = 10
        if self.need_draw == 1: 
            self.rects.append([A_x, y, w, h])
            self.need_draw = 0
        qp.setBrush(QtGui.QColor(200, 0, 0))
        for rect in self.rects: 
            qp.drawRect(*rect)
            
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    obj = SliceTool()
    obj.show()
    app.exec_()
