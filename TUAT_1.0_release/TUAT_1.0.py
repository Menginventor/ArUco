"""
Thank for gretest code
https://github.com/TutorProgramacion/pyqt-tutorial/blob/master/10-opencv/main.py
V1.0
"""

import sys
import time
import cv2
from cv2 import aruco
import yaml
import csv
import numpy as np
import csv
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

import os
import winsound
import threading
import math

def eulerAnglesToRotationMatrix(theta):
    R_x = np.array([[1, 0, 0],
                    [0, math.cos(theta[0]), -math.sin(theta[0])],
                    [0, math.sin(theta[0]), math.cos(theta[0])]
                    ])

    R_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                    [0, 1, 0],
                    [-math.sin(theta[1]), 0, math.cos(theta[1])]
                    ])

    R_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                    [math.sin(theta[2]), math.cos(theta[2]), 0],
                    [0, 0, 1]
                    ])

    R = np.matmul(R_z, np.matmul(R_y, R_x))
    return R


def rotationMatrixToEulerAngles(R):
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])
class CV_Thread(QtCore.QThread):
    cv_update_signal = pyqtSignal()
    beep_flag = False
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
    def __del__(self):
        self.wait()

    def beep_thread(self):
        winsound.Beep(2000, 100)
        self.beep_flag = False
    def run(self):

        while True:
            self.ret, self.frame = cap.read()
            self.rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            self.frame = cv2.undistort(self.frame, mtx, dist,None, newcameramtx)

            # Our operations on the frame come here
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            aruco.drawDetectedMarkers(self.frame, corners, ids)

            self.index_id_0 = None
            self.index_id_1 = None
            self.ref_rvec = None
            self.ref_tvec = None
            self.tag_rvec = None
            for i in range(len(corners)):
                if ids[i][0] == 0:
                    self.index_id_0 = i

                elif ids[i][0] == 1:
                    self.index_id_1 = i

            if self.index_id_0 != None:


                rvec1, tvec1, obj1 = aruco.estimatePoseSingleMarkers(corners[self.index_id_0], markerLength, newcameramtx,(0,0,0,0))
                aruco.drawAxis(self.frame, newcameramtx, dist, rvec1, tvec1, 0.075)
                H_Line = np.float32([[-1, 0, 0], [1, 0, 0]])

                imgpts, jac = cv2.projectPoints(H_Line, rvec1, tvec1, newcameramtx, dist)
                imgpts = np.int32(imgpts).reshape(-1, 2)

                cv2.line(self.frame, tuple(imgpts[0]), tuple(imgpts[1]), (255, 0, 0), 1)
                self.ref_rvec = rvec1
            if self.index_id_1 != None:
                rvec2, tvec2, obj2 = aruco.estimatePoseSingleMarkers(corners[self.index_id_1], markerLength,
                                                                     newcameramtx, dist)
                aruco.drawAxis(self.frame, newcameramtx, dist, rvec2, tvec2, 0.075)
                if not REF_RVEC is None:

                    self.ref_tvec = np.copy(tvec2)
                    self.tag_rvec = np.copy(rvec2)

                    rmat1 = np.identity(3)
                    cv2.Rodrigues(REF_RVEC, rmat1)
                    rmat1_inv = np.transpose(rmat1)


                    if not (REF_TVEC is None):# if REF_TVEC had set
                        relate_REF_TVEC = np.matmul(rmat1_inv, REF_TVEC[0][0])
                        relate_moving_TVEC = np.matmul(rmat1_inv, tvec2[0][0])

                        relate_moving_TVEC[1] = relate_REF_TVEC[1]
                        relate_moving_TVEC = np.matmul(rmat1, relate_moving_TVEC)
                        self.ref_tvec[0][0] = np.copy(relate_moving_TVEC)



                    #print(REF_TVEC)



                    upper_H_offest = np.float32([[-1, 0.05, 0], [1, 0.05, 0]])
                    lower_H_offest = np.float32([[-1, -0.05, 0], [1, -0.05, 0]])
                    imgpts_up, jac_up = cv2.projectPoints(upper_H_offest, REF_RVEC, self.ref_tvec, newcameramtx, (0,0,0,0))
                    imgpts_lw, jac_lw = cv2.projectPoints(lower_H_offest, REF_RVEC, self.ref_tvec, newcameramtx, (0,0,0,0))
                    imgpts_up = np.int32(imgpts_up).reshape(-1, 2)
                    imgpts_lw = np.int32(imgpts_lw).reshape(-1, 2)

                    cv2.line(self.frame, tuple(imgpts_up[0]), tuple(imgpts_up[1]), (0, 0, 255), 2)
                    cv2.line(self.frame, tuple(imgpts_lw[0]), tuple(imgpts_lw[1]), (0, 0, 255), 2)

                    if self.parent.running_state == 'Recording':
                        global TAG_RVEC
                        rmat2 = np.identity(3)
                        cv2.Rodrigues(rvec2, rmat2)
                        tag_ref_mat = np.identity(3)
                        cv2.Rodrigues(TAG_RVEC, tag_ref_mat)
                        tag_ref_mat_inv = np.transpose(tag_ref_mat)
                        tag_orientation_mat = np.matmul(tag_ref_mat_inv,rmat2)
                        # rmat2 = np.matmul(eulerAnglesToRotationMatrix([math.pi*0.5,0,0]),rmat2)
                        euler = rotationMatrixToEulerAngles(tag_orientation_mat)

                        #print('recording')
                        relate_tvec = np.matmul(rmat1_inv, np.subtract(tvec2[0][0], REF_TVEC[0][0]))
                        #print(relate_tvec)
                        if abs(relate_tvec[1]) > 0.05:

                            try:
                                print('over limit!')
                                if not self.beep_flag:
                                    beep = threading.Thread(target=self.beep_thread)
                                    beep.start()
                                    self.beep_flag = True
                            except Exception as e:
                                print(e)

                        with open(prog_dir+'/log/' + str(temp_log_filename) + '.csv', 'a', newline='') as csvfile:
                            #['time stamp', 'pos x', 'pos y', 'pos z','rot x', 'rot y', 'rot z']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            global start_time
                            crr_time = time.clock() - start_time
                            writing_data = {
                                'time stamp': crr_time,
                                'pos x': relate_tvec[0],
                                'pos y': relate_tvec[1],
                                'pos z': relate_tvec[2],
                                'rot x': euler[0],
                                'rot y': euler[1],
                                'rot z': euler[2]
                            }
                            writer.writerow(writing_data)
                            #print(relate_tvec)
            self.cv_update_signal.emit()

class main_widget(QWidget):
    running_state = 'Idle'
    def cv_update(self):
        self.image = self.CV_Thread.frame
        self.displayImage()
        if self.CV_Thread.index_id_0 != None and self.running_state == 'Idle':
            self.setup_btn.setEnabled(True)
        else:
            self.setup_btn.setEnabled(False)
        if self.CV_Thread.index_id_1 != None and (not REF_RVEC is None) and  self.running_state == 'Idle':
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
        if self.running_state == 'Recording':
            global start_time
            crr_time = time.clock() - start_time
            millis = str(int(crr_time*1000)%1000)
            secs = str(int(crr_time ) % 60)
            min = str(int(crr_time/60))
            self.Timer_label.setText(min+':'+secs+':'+millis)
            self.stop_btn.setEnabled(True)
        elif self.running_state == 'Idle':
            self.Timer_label.setText('00:00:000')
            self.stop_btn.setEnabled(False)
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.image = None
        self.image_disp_label = QLabel()
        self.initUI()
        self.CV_Thread = CV_Thread(self)
        self.CV_Thread.start()
        self.CV_Thread.cv_update_signal.connect(self.cv_update)
    def initUI(self):

        root = QHBoxLayout(self)
        cam_latout = QVBoxLayout(self)
        self.Timer_label = QLabel()
        self.Timer_label.setText('00:00:000')
        font = QtGui.QFont()
        font.setPointSize(36)
        self.Timer_label.setFont(font)
        cam_latout.addWidget(self.Timer_label)
        cam_latout.addWidget(self.image_disp_label)

        root.addLayout(cam_latout)
        root.addLayout(self.create_panel())
        #self.resize(1028, 720)
    def create_panel(self):
        self.setup_btn = QPushButton('Setup', self)
        self.start_btn = QPushButton('Start', self)

        self.stop_btn = QPushButton('Stop', self)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.setup_btn.setFont(font)
        self.start_btn.setFont(font)
        self.start_btn.setEnabled(False)

        self.stop_btn.setEnabled(False)
        self.start_btn.setFont(font)

        self.stop_btn.setFont(font)
        ####
        self.setup_btn.clicked.connect(self.setup_oreintation)
        self.start_btn.clicked.connect(self.start_record)
        self.stop_btn.clicked.connect(self.stop_record)


        ###
        panel = QVBoxLayout(self)
        panel.addWidget(self.setup_btn)
        panel.addWidget(self.start_btn)

        panel.addWidget(self.stop_btn)
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        panel.addItem(verticalSpacer)
        return panel

    def setup_oreintation(self):
        print('setup!')
        global REF_RVEC
        REF_RVEC = self.CV_Thread.ref_rvec
        print(REF_RVEC)

    def start_record(self):
        print('start_record')
        self.running_state = 'Recording'
        global REF_TVEC
        global TAG_RVEC

        REF_TVEC = self.CV_Thread.ref_tvec
        TAG_RVEC = self.CV_Thread.tag_rvec
        global temp_log_filename

        file_name_err = True
        while file_name_err:
            temp_log_filename = time.strftime("%d-%b-%Y-%H-%M-%S", time.localtime())
            print(temp_log_filename)
            try:
                with open(prog_dir+'/log/'+str(temp_log_filename)+'.csv', 'w', newline='') as csvfile:

                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    file_name_err = False
            except Exception as e:
                print(e)
                file_name_err = True

        global start_time
        start_time = time.clock()
    def stop_record(self):
        print('stop_record')
        self.running_state = 'Pause'

        ret = self.showdialog()
        if ret == 2048:#saving
            print('saving')
            self.saveFile()
        os.remove(prog_dir+'/log/' + str(temp_log_filename) + '.csv')
        print('deleted file')

        self.running_state = 'Idle'
        global REF_RVEC
        global REF_TVEC

        REF_TVEC = None

    def saveFile(self):
        writen_file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", temp_log_filename,
                                              "CSV Files (*.csv)")
        if writen_file_name == '':
            return
        global fieldnames
        #fieldnames = ['time stamp', 'pos x', 'pos y', 'pos z','rot x', 'rot y', 'rot z']


        with open(writen_file_name, 'w', newline='') as writen_file:
            writer = csv.DictWriter(writen_file, fieldnames=fieldnames)
            writer.writeheader()
            with open(prog_dir+'/log/' + str(temp_log_filename) + '.csv', newline='') as original_file:
                reader = csv.reader(original_file)
                reader_lst = list(reader)
                for row in reader_lst[1:]:
                    data = {
                        'time stamp': row[0],
                        'pos x': row[1],
                        'pos y': row[2],
                        'pos z': row[3],
                        'rot x': row[4],
                        'rot y': row[5],
                        'rot z': row[6]
                    }
                    writer.writerow(data)


    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Do you want to save your log?")
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Message")



        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard);
        msg.setDefaultButton(QMessageBox.Save);
        #msg.buttonClicked.connect(msgbtn)

        retval = msg.exec_()
        print("value of pressed message box button:", retval)
        return retval

    def displayImage(self):
        size = self.image.shape
        step = self.image.size / size[0]
        qformat = QImage.Format_Indexed8
        if len(size) == 3:
            if size[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(self.image, size[1], size[0], step, qformat)
        img = img.rgbSwapped()
        self.image_disp_label.setPixmap(QPixmap.fromImage(img))
        self.resize(self.image_disp_label.pixmap().size())
def load_camera_calib():
    dir = os.path.dirname(os.path.abspath(__file__))
    global calib_data
    with open(dir+"/calib/src/calib_data.yml", 'r') as stream:
        try:
            calib_data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    ret, frame = cap.read()
    h, w = frame.shape[:2]
    global mtx
    global dist
    mtx = calib_data['cameraMatrix']
    dist = calib_data['distCoeffs']
    global newcameramtx
    global markerLength
    global aruco_dict
    global parameters
    global REF_RVEC
    global REF_TVEC
    global TAG_RVEC
    global temp_log_filename
    global fieldnames
    fieldnames = ['time stamp', 'pos x', 'pos y', 'pos z','rot x', 'rot y', 'rot z']
    temp_log_filename = ''
    REF_RVEC = None
    REF_TVEC = None
    TAG_RVEC = None
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    markerLength = 0.15
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
class main_window(QMainWindow):
    def __init__(self ):
        super(QMainWindow, self).__init__()
        #QMainWindow.__init__(self)
        self.initUI()
    def initUI(self):
        self.setGeometry(100, 100, 1500, 720)
        self.setWindowTitle("Thammasat University ArUco Tracker")
        self.setWindowIcon(QtGui.QIcon('py_logo.png'))
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        impMenu = QMenu('Import', self)
        imp_txt_Act = QAction('Import text file', self)
        imp_csv_Act = QAction('Import CSV file', self)
        imp_byte_Act = QAction('Import Protocol file', self)
        impMenu.addAction(imp_txt_Act)
        impMenu.addAction(imp_csv_Act)
        impMenu.addAction(imp_byte_Act)

        expMenu = QMenu('Export', self)
        exp_txt_Act = QAction('Export text file', self)
        exp_csv_Act = QAction('Export CSV file', self)
        exp_byte_Act = QAction('Export Protocol file', self)
        expMenu.addAction(exp_txt_Act)
        expMenu.addAction(exp_csv_Act)
        expMenu.addAction(exp_byte_Act)

        fileMenu.addMenu(impMenu)
        fileMenu.addMenu(expMenu)

        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')
        self.main_widget = main_widget(self)
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        clean_junk()
        print('closing')



def clean_junk():
    global prog_dir
    dir = prog_dir+'/log/'

    try:
        filelist = [f for f in os.listdir(dir)]
        try:
            for f in filelist:
                os.remove(os.path.join(dir, f))
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    print('clean junk')
def main():
    global cap
    global prog_dir
    prog_dir = dir = os.path.dirname(os.path.abspath(__file__))
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    global start_time
    load_camera_calib()
    app = QApplication(sys.argv)
    w = main_window()
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

