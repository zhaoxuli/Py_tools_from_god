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
import os
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

#struct for saving slice info
class SliceInfo(QtGui.QWidget):
    def __init__(self, idx, p_A, p_B, rect, slice_interval, 
                 checkbox, checkbox_bn):
        self.idx = idx
        self.p_A = p_A
        self.p_B = p_B
        self.rect = rect
        self.slice_interval = slice_interval
        self.checkbox = checkbox
        self.checkbox_bn = checkbox_bn

QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf-8"))
class SliceTool(QtGui.QWidget):
    def __init__(self,parent=None):
        super(SliceTool,self).__init__(parent)
        self.setWindowTitle(self.tr("ADAS Slice 工具"))
        self.Logo_img = cv2.imread("./rec/imshow.jpg")             # 读取默认显示文件
        self.image_width = 1200
        self.image_height = 800

        #test slices 
        self.test_info = []
        self.mapper = QtCore.QSignalMapper(self) 
        #check slice point 
        self.signal_A = 0 
        self.cur_frame_idx = -1
        self.frame_jump = 5
        self.p_A = -1
        self.p_B = -1
        self.initial_slice_interval = 5
        self.slice_obj_idx = 0
        self.draw = 0

        #pack section
        self.pack = ParsePack.Pack()
        self.pack_path = ''
        self.pack_length = 0
        self.pack_name = ''

        #timer setup 
        self.timer = QtCore.QTimer();  # 设置计时器
        self.timer.timeout.connect(self.NextFrame); 
        self.pack_file_list = []
        self.pack_file_idx = 0

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
        self.button_pre = QtGui.QPushButton(self.tr("上十帧"))                   #上一帧按钮控件
        self.button_play = QtGui.QPushButton(self.tr("播放"))                    #播放/暂停按钮控件
        self.button_next = QtGui.QPushButton(self.tr("下一帧"))                  #下一帧按钮控件
        self.button_Load = QtGui.QPushButton(self.tr('载入'))
        self.button_slice = QtGui.QPushButton(self.tr('slice'))
        self.button_load_packlist = QtGui.QPushButton(self.tr('载入pack列表'))
        self.button_pre_in_packlist = QtGui.QPushButton(self.tr('上个pack'))
        self.button_next_in_packlist = QtGui.QPushButton(self.tr('下个pack'))
        self.slider = QtGui.QSlider(1)                            #滑动条控件

        # UI控件大小和位置
        self.button_pre.setFixedSize(100, 50)
        self.button_play.setFixedSize(100, 50)
        self.button_next.setFixedSize(100, 50)
        self.button_Load.setFixedSize(100, 50)
        self.button_slice.setFixedSize(100, 50)
        self.button_load_packlist.setFixedSize(100, 50)
        self.button_pre_in_packlist.setFixedSize(100, 50)
        self.button_next_in_packlist.setFixedSize(100, 50)

        #将控件布局到布局管理器中
        Layout_imshow.addWidget(self.label_image, 0, 0)

        Layout_button.addWidget(self.button_pre)
        Layout_button.addWidget(self.button_play)
        Layout_button.addWidget(self.button_next)
        Layout_button.addWidget(self.button_Load)
        Layout_button.addWidget(self.button_slice)
        Layout_button.addWidget(self.label_info)
        Layout_button.addWidget(self.button_load_packlist)
        Layout_button.addWidget(self.button_pre_in_packlist)
        Layout_button.addWidget(self.button_next_in_packlist)
        Layout_bar.addWidget(self.slider)


        self.connect(self.button_play, QtCore.SIGNAL("clicked()"), self.Play)
        self.connect(self.button_Load, QtCore.SIGNAL('clicked()'), self.LoadPack)
        self.connect(self.button_next,QtCore.SIGNAL("clicked()"),self.NextFrame)
        self.connect(self.button_pre,QtCore.SIGNAL("clicked()"),self.PreFrame)
        self.connect(self.button_slice,QtCore.SIGNAL("clicked()"),self.SlicePack)
        self.connect(self.slider,QtCore.SIGNAL("sliderReleased()"), self.SliderMove)
        self.connect(self.button_load_packlist, QtCore.SIGNAL("clicked()"), self.LoadPackList)
        self.connect(self.button_pre_in_packlist, QtCore.SIGNAL("clicked()"), self.PreInPackList)
        self.connect(self.button_next_in_packlist, QtCore.SIGNAL("clicked()"), self.NextInPackList)
        #self.connect(self.slider,QtCore.SIGNAL("valueChanged (int)"), self.SliderStep)

    def SlicePack(self):
        for idx, obj in enumerate(self.test_info):
            A_B = [obj.p_A, obj.p_B]
            slice_interval = obj.slice_interval
            self.Pack2Img(A_B[0], A_B[1], idx, slice_interval)
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Done")
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()

    def Pack2Img(self, start, end, idx, slice_interval):
        if slice_interval == 0:
            return
        if self.pack_name == '':
            print 'no pack loaded'
            return
        if start > end:
            print 'end should be larger than start'
            return
        save_path = os.path.join(os.getcwd(), self.pack_name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        i = start
        while i < end:
            a_time = int(time.time())
            pic = self.pack.getImageByIdx(i)
            cv2.imwrite(save_path + '/' + self.pack_name + '_' + str(i) + '.png', pic)
            i = i + slice_interval

    def reset(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button_play.setText(self.tr("播放"))
        #reset all parameters
        self.mapper = QtCore.QSignalMapper(self)
        self.signal_A = 0
        self.cur_frame_idx = -1
        self.frame_jump = 5
        self.p_A = -1
        self.p_B = -1
        self.initial_slice_interval = 5
        self.slice_obj_idx = 0
        self.draw = 0
        self.slider.setValue(0)
        #reset checkboxes and checkbox button
        for obj in self.test_info:
            self.layout_checkbox.removeWidget(obj.checkbox)
            self.layout_checkbox.removeWidget(obj.checkbox_bn)
            obj.checkbox.deleteLater()
            obj.checkbox_bn.deleteLater()
        self.test_info = []

    #load pack list
    def LoadPackList(self):
        pack_list = str(QtGui.QFileDialog.getOpenFileName(self, 'Open Pack', '', '*.*', None,
                                                          QtGui.QFileDialog.DontUseNativeDialog))
        fin = open(pack_list).readlines()
        self.pack_file_list = []
        for line in fin:
            self.pack_file_list.append(line.strip())
        self.LoadPackFromList()

    def NextInPackList(self):
        if self.pack_file_idx >= len(self.pack_file_list) - 1:
            self.pack_file_idx = len(self.pack_file_list) - 1
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText("end of pack list")
            msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            retval = msg.exec_()
            return
        self.pack_file_idx += 1
        self.LoadPackFromList()

    def PreInPackList(self):
        if self.pack_file_idx <= 0:
            self.pack_file_idx = 0
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText("top of pack list")
            msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            retval = msg.exec_()
            return
        self.pack_file_idx -= 1
        self.LoadPackFromList()

    def LoadPackFromList(self):
        self.reset()
        self.pack.loadFile(self.pack_file_list[self.pack_file_idx])
        self.pack_length = int(self.pack.protoLens[0])
        self.pack_name = self.pack_file_list[self.pack_file_idx].split('/')[-1].split('.')[0]
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Loaded")
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()

    #load pack
    def LoadPack(self):
        self.reset()
        self.pack_path = str(QtGui.QFileDialog.getOpenFileName(self,'Open Pack', '', '*.*', None, QtGui.QFileDialog.DontUseNativeDialog))
        self.pack.loadFile(self.pack_path)
        self.pack_length = int(self.pack.protoLens[0]) 
        self.pack_name = self.pack_path.split('/')[-1].split('.')[0]
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Loaded")
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()

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
        self.cur_frame_idx = self.cur_frame_idx + self.frame_jump
        slider_value = int(100.0 * float(self.cur_frame_idx) / self.pack_length)
        if slider_value > self.slider.value():
            self.slider.setValue(slider_value)
        self.Refresh()

    #pre frame
    def PreFrame(self):
        self.cur_frame_idx = self.cur_frame_idx - self.frame_jump
        self.Refresh() 

    #slice start point
    def SlicePointA(self):
        print "SlicePointA"
        self.signal_A = 1
        self.p_A = self.cur_frame_idx

    #draw checkboxes dynamically
    def DrawCheckBoxes(self):
        idx = self.slice_obj_idx 
        self.slice_obj_idx += 1
        checkbox = QtGui.QCheckBox(str(idx))
        checkbox.setChecked(True)
        checkbox.toggled.connect(self.CheckBoxState)
        checkbox_bn = QtGui.QPushButton('slice interval')
        checkbox_bn.clicked.connect(self.mapper.map)
        self.mapper.setMapping(checkbox_bn, idx)
        #checkbox_bn.clicked.connect(self.ShowSliceIntervalDialog)
        self.mapper.mapped['int'].connect(self.ShowSliceIntervalDialog)
        self.layout_checkbox.addWidget(checkbox)
        self.layout_checkbox.addWidget(checkbox_bn)
        return checkbox, checkbox_bn, idx 

       
    def ShowSliceIntervalDialog(self, idx): 
        num,ok = QtGui.QInputDialog.getInt(self,"integer input dualog","enter a number")
        if ok:
            for obj in self.test_info:
                if obj.idx == idx:
                    obj.slice_interval = num
                    print (obj.slice_interval, idx)
            return

    def CheckBoxState(self):
        result = []
        for obj in self.test_info:
            if obj.checkbox.isChecked():
                result.append(obj)
                continue
            self.layout_checkbox.removeWidget(obj.checkbox)
            self.layout_checkbox.removeWidget(obj.checkbox_bn)
            obj.checkbox.deleteLater()
            obj.checkbox_bn.deleteLater()
        self.test_info = result

    #slice end point
    def SlicePointB(self):
        if self.signal_A < 1:
            print "no start point"
        else:
            print "SlicePointB"
            self.p_B = self.cur_frame_idx
            self.draw = 1
            #create checkbox and checkbox_bn
            checkbox, checkbox_bn, idx = self.DrawCheckBoxes()
            #create rectangle for drawing
            rect = self.CreateRectangle(self.p_A, self.p_B)
            #create single slice object
            print (self.p_A, self.p_B)
            single_slice = SliceInfo(idx=idx, p_A=self.p_A, p_B=self.p_B, rect=rect, 
                                     slice_interval=self.initial_slice_interval, checkbox=checkbox,
                                     checkbox_bn=checkbox_bn) 
            self.test_info.append(single_slice)
            self.signal_A = 0
            self.p_A = -1
            self.p_B = -1

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

    def CreateRectangle(self, draw_A, draw_B):
        point = self.slider.pos()
        slider_w = self.slider.width()
        x = int(point.x())
        y = int(point.y())
        A_x = x + (float(draw_A) / self.pack_length) * int(slider_w)
        B_x = x + (float(draw_B) / self.pack_length) * int(slider_w)
        w = B_x - A_x
        h = 10
        return [A_x, y, w, h]
 
    def DrawRectangle(self, qp):
        if self.draw == 0: return
        qp.setBrush(QtGui.QColor(200, 0, 0))
        for obj in self.test_info: 
            rect = obj.rect
            qp.drawRect(*rect)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    obj = SliceTool()
    obj.show()
    app.exec_()
