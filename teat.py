'''
Thank for gretest code
https://github.com/TutorProgramacion/pyqt-tutorial/blob/master/10-opencv/main.py

'''
import sys
import cv2
import numpy

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
class CV_Thread(QtCore.QThread):
    cv_update_signal = pyqtSignal()

    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
    def __del__(self):
        self.wait()
    def run(self):
        while True:
            self.ret, self.frame = cap.read()
            self.rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.cv_update_signal.emit()
class Example(QWidget):
    def cv_update(self):
        print('cv_update')
        self.image = self.CV_Thread.frame
        self.mostrarImagen()
    def __init__(self):
        super().__init__()
        self.image = None
        self.label = QLabel()
        self.initUI()
        self.CV_Thread = CV_Thread(self)
        self.CV_Thread.start()
        self.CV_Thread.cv_update_signal.connect(self.cv_update)

    def initUI(self):
        self.label.setText('OpenCV Image')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('border: gray; border-style:solid; border-width: 1px;')

        btn_open = QPushButton('Abir Imagen...')
        btn_open.clicked.connect(self.abrirImagen)

        btn_procesar = QPushButton('Processar Imagen')
        btn_procesar.clicked.connect(self.procesarImagen)

        top_bar = QHBoxLayout()
        top_bar.addWidget(btn_open)
        top_bar.addWidget(btn_procesar)

        root = QVBoxLayout(self)
        root.addLayout(top_bar)
        root.addWidget(self.label)

        self.resize(540, 574)
        self.setWindowTitle('OpenCV & PyQT 5 by Tutor de Programacion')

    def abrirImagen(self):
        filename, _ = QFileDialog.getOpenFileName(None, 'Buscar Imagen', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
        if filename:
            with open(filename, "rb") as file:
                data = numpy.array(bytearray(file.read()))

                self.image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
                # self.image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                self.mostrarImagen()

    def procesarImagen(self):
        if self.image is not None:
            # self.image = cv2.GaussianBlur(self.image, (5, 5), 0)
            # self.image = cv2.Canny(self.image, 100, 200)

            gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY) \
                if len(self.image.shape) >= 3 else self.image

            blur = cv2.GaussianBlur(gray, (21, 21), 0, 0)

            self.image = cv2.divide(gray, blur, scale=256)
            self.mostrarImagen()

    def mostrarImagen(self):
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

        self.label.setPixmap(QPixmap.fromImage(img))
        self.resize(self.label.pixmap().size())

if __name__ == '__main__':
    global cap
    cap = cv2.VideoCapture(0)
    app = QApplication(sys.argv)
    win = Example()
    win.show()
sys.exit(app.exec_())