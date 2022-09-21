"""Modified version of
    https://github.com/harupy/snipping-tool/blob/master/snipping_tool.py

Creates a windows snipping tool like UI and allows user to snip a section of the screen

Primary use is to return the bounding box coordinates of this snip, though is easily modifiable"""

import sys

from PyQt5 import QtWidgets, QtCore, QtGui
import tkinter as tk


class Snip(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.bbox = None
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.2)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor(0, 0, 0, 190))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.bbox = [x1, y1, x2, y2]


def get_bbox():
    """
    Gets the bounding box coordinates of a box draw by the user on the screen

    Visually similar to windows snipping tools

    Return format is (x1, y1, x2, y2)
    """
    app = QtWidgets.QApplication(sys.argv)
    window = Snip()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    app.exec_()

    while True:
        # check if bounding box is more than 10x10 pixels
        if abs(window.bbox[2] - window.bbox[0]) > 10 and abs(window.bbox[3] - window.bbox[1]) > 10:
            return window.bbox
        # else restart app and try again
        else:
            print("Bbox was too small!")
            del app, window
            app = QtWidgets.QApplication(sys.argv)
            window = Snip()
            window.show()
            app.aboutToQuit.connect(app.deleteLater)
            app.exec_()


if __name__ == '__main__':

    bbox = get_bbox()

    print(bbox)
