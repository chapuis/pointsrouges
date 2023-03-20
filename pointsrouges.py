## code by Olivier Chapuis <olivier.chapuis@lisn.upsaclay.fr>
## and public domaine code from the internet
## LICENSE: see LICENSE

import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog

#from PyQt5.QtGui import QPixmap, QPainter, QPen
#from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QApplication

class RectangleDialog(QtWidgets.QDialog):
    def __init__(self, iv):
        super().__init__()
        self.setWindowTitle("Rectangle Dialogue")

        #iv.coucou()
        self.horiz_text = ""
        self.vert_text = ""
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        vblayout = QtWidgets.QVBoxLayout()

        message = QtWidgets.QLabel("enter number of points (x by y)")
        vblayout.addWidget(message)
        #
        validator = QtGui.QIntValidator()
        validator.setRange(0, 1000)
        hblayout = QtWidgets.QHBoxLayout()
        self.horiz = QtWidgets.QLineEdit(self)
        self.horiz.setValidator(validator)
        self.horiz.textChanged.connect(self.htext)
        hblayout.addWidget(self.horiz)
        self.vert = QtWidgets.QLineEdit(self)
        self.vert.setValidator(validator)
        self.vert.textChanged.connect(self.vtext)
        hblayout.addWidget(self.vert)
        vblayout.addLayout(hblayout)
        vblayout.addWidget(self.buttonBox)
        self.setLayout(vblayout)

    def htext(self, s):
        self.horiz_text = s

    def vtext(self, s):
        self.vert_text = s

    def get_result(self):
        return(self.horiz_text, self.vert_text)


class ImageViewer(QtWidgets.QGraphicsView):
    point_added = QtCore.pyqtSignal(QtCore.QPoint)
    rect_added = QtCore.pyqtSignal(QtCore.QRect)
    reset_count_file = QtCore.pyqtSignal(list)
    update_count = QtCore.pyqtSignal(int)
    save_pixmap_to_file = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, parent):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._image = QtWidgets.QGraphicsPixmapItem()
        self._pixmap = QtGui.QPixmap()
        self._scene.addItem(self._image)
        self._count = 0
        self._press = None
        self._points = []
        self._rectangles = []
        self._alls = []
        self._draw_width = 3
        self._rubberband_erase = False
        self._save_drag_mode = None
        self._next_drag = ""
        self._cross_cursor = False

        self._rectangle_enabled = False

        # Créez un QGraphicsPixmapItem pour afficher l'overlay pixmap
        self._overlay = QtWidgets.QGraphicsPixmapItem()
        self._overlay.setZValue(1)
        self._overlay_pixmap = QtGui.QPixmap()
        self._scene.addItem(self._overlay)

        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def has_image(self):
        return not self._empty

    def get_pixmap(self):
        if not self.has_image:
            return None
        result_image = self._pixmap.copy()
        painter = QtGui.QPainter(result_image)
        painter.drawPixmap(0, 0, self._overlay_pixmap)
        painter.end()
        return result_image

    def fit_in_view(self, scale=True):
        rect = QtCore.QRectF(self._image.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_image():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def set_image(self, pixmap=None):
        self._zoom = 0
        self._count = 0
        self._points = []
        self._rectangles = []
        self._alls = []
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._pixmap = pixmap
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._image.setPixmap(pixmap)
            # Créez un pixmap transparent pour dessiner sur le dessus de l'image
            print(pixmap.size())
            self._overlay_pixmap = QtGui.QPixmap(pixmap.size())
            self._overlay_pixmap.fill(QtCore.Qt.transparent)
            self._overlay.setPixmap(self._overlay_pixmap)
        else:
            self._empty = True
            self._image.setPixmap(QtGui.QPixmap())
            self._overlay.setPixmap(QtGui.QPixmap())
        self.fit_in_view()

    def add_points(self, points, redraw=False):
        lineWidth = int(self._draw_width/2)
        ray = self._draw_width
        painter = QtGui.QPainter(self._overlay_pixmap)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(lineWidth)
        brush = QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern)
        for point in points:
            if not redraw:
               self._count += 1
               self._points.append(point)
               self._alls.append(point)
            painter.setPen(pen)
            painter.drawEllipse(point.x()-ray,point.y()-ray,2*ray,2*ray)
            painter.setBrush(brush)
            painter.drawEllipse(point.x()-ray,point.y()-ray,2*ray,2*ray)
        painter.end()
        result_image = self._pixmap.copy()
        painter = QtGui.QPainter(result_image)
        painter.drawPixmap(0, 0, self._overlay_pixmap)
        painter.end()
        # Mettez à jour l'image affichée dans le QGraphicsPixmapItem
        self._image.setPixmap(result_image)
        self.update_count.emit(self._count)

    def add_point(self, point):
        ps = []
        ps.append(point)
        self.add_points(ps)

    def add_rectangles(self, rects, redraw=False):
        if not self._rectangle_enabled:
            return
        lineWidth = int(self._draw_width/2)
        ray = self._draw_width
        painter = QtGui.QPainter(self._overlay_pixmap)
        pen = QtGui.QPen(QtCore.Qt.blue)
        pen.setWidth(ray)
        painter.setPen(pen)
        for rect in rects:
            if not redraw:
               self._rectangles.append(rect)
               self._alls.append(rect)
            painter.drawRect(rect)
        painter.end()
        result_image = self._pixmap.copy()
        painter = QtGui.QPainter(result_image)
        painter.drawPixmap(0, 0, self._overlay_pixmap)
        painter.end()
        # Mettez à jour l'image affichée dans le QGraphicsPixmapItem
        self._image.setPixmap(result_image)

    def add_rectangle(self, rect):
        dlg = RectangleDialog(self)
        if dlg.exec():
            #print("Success!")
            v, h = dlg.get_result()
            if not v.isnumeric() or not h.isnumeric:
                return
            v = int(v)
            h = int(h)
            # print("res:", v, h)
            if (v <= 0 or h <= 0):
                return
            dw = self._draw_width + int(self._draw_width/2)
            sx = rect.x() + dw
            sy = rect.y() + dw
            stepx = 0
            stepy = 0
            if v > 1:
                stepx = max(int((rect.width()-2*dw)/(v-1)),1)
            else:
                sx = rect.x() + int(rect.width()/2)
            if h > 1:
                stepy = max(int((rect.height()-2*dw)/(h-1)),1)
            else:
                sy = rect.y() + int(rect.height()/2)
            ps = []
            for x in range(v):
                cx = sx + x*stepx
                cy = sy
                for y in range(h):
                    cy = sy + y*stepy
                    ps.append(QtCore.QPoint(cx,cy))
            self.add_points(ps)
            if self._rectangle_enabled:
                rs = []
                rs.append(rect)
                self.add_rectangles(rs)
                self.rect_added.emit(rect)


    def erase(self, rect):
        nps = []
        nrs = []
        nas = []
        for pr in self._alls:
            if isinstance(pr, QtCore.QPoint):
                if not (pr.x() >= rect.x() and pr.x() <= rect.x() + rect.width()
                    and pr.y() >= rect.y() and pr.y() <= rect.y() + rect.height()):
                    nps.append(pr)
                    nas.append(pr)
            else:
                #instance of a QtCore.QRect
                if not (pr.x() >= rect.x() and pr.x() <= rect.x() + rect.width()
                    and pr.y() >= rect.y() and pr.y() <= rect.y() + rect.height()
                    and pr.x() + pr.width() >= rect.x() and pr.x() + pr.width() <= rect.x() + rect.width()
                    and pr.y() + pr.height() >= rect.y() and pr.y() + pr.height() <= rect.y() + rect.height()):
                    nrs.append(pr)
                    nas.append(pr)
        # now remove
        self._points = nps
        self._rectangles = nrs
        self._alls = nas
        self._count = len(nps)
        self.redraw()
        self.reset_count_file.emit(self._alls)
        self.update_count.emit(self._count)

    def coucou(self):
        print("coucou")

    def add_undos(self, alls):
       self._alls = alls

    def redraw(self):
       if not self._empty:
          self._overlay_pixmap.fill(QtCore.Qt.transparent)
          self.add_points(self._points, True)
          self.add_rectangles(self._rectangles, True)

    def update_drawing_size(self, w):
       self._draw_width = w
       if not self._empty:
          self.redraw()

    def undo(self):
        l = len(self._alls)
        if l == 0:
            return
        pr = self._alls[l-1]
        del self._alls[-1]
        if isinstance(pr, QtCore.QPoint):
           self._count -= 1
           del self._points[-1]
        else:
           del self._rectangles[-1]
        self.redraw()
        self.reset_count_file.emit(self._alls)
        self.update_count.emit(self._count)

    def remove_point_or_rect(self, pindex, rindex, aindex):
        print("remove_point_or_rect %d %d %d %d" % (pindex, rindex, aindex, len(self._alls)))
        if aindex < 0 or aindex >= len(self._alls):
            return()
        del self._alls[aindex]
        if pindex >= 0 and pindex < len(self._points):
            print("remove point %d" % pindex)
            del self._points[pindex]
            self._count -= 1
        elif rindex >= 0 and rindex < len(self._rectangles):
            del self._rectangles[rindex]
        self.redraw()
        self.reset_count_file.emit(self._alls)
        self.update_count.emit(self._count)

    def pick(self, point):
        point = self.mapToScene(point).toPoint()
        # print("start")
        pindex = -1
        rindex = -1
        aindex = -1
        cp = 0
        cr = 0
        c = 0
        for pr in self._alls:
            if isinstance(pr, QtCore.QPoint):
                d = pow(pow(pr.x()-point.x(), 2) + pow(pr.y()-point.y(), 2), 0.5)
                if (d <= self._draw_width + int(self._draw_width/2)):
                    #print("Picked! %d %d" % (cp, c))
                    pindex = cp
                    aindex = c
                    break
                cp += 1
            else:
                #instance of a QtCore.QRect
                cr += 1
            c += 1
        #print("end Pick", pindex, rindex, aindex)
        return(pindex, rindex, aindex)

    # def toggleDragMode(self):
    #     if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #     elif not self._image.pixmap().isNull():
    #         self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def update_drag_mode(self, str):
        if str == "add_points":
            self._next_drag = "add_points"
            #self.setMouseTracking(True)
            self._cross_cursor = True
        elif str == "erase_points":
            self._next_drag = "erase_points"
            self._cross_cursor = True
        else:
            print("WARN: bad drag_mode")
        # if i == 1:
        #     self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        #     self._rubberband_erase = False
        # elif i == 0 and self.dragMode() == QtWidgets.QGraphicsView.RubberBandDrag:
        #     self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # elif i == 2:
        #     self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        #     self._rubberband_erase = True

    def mouse_click(self, point, button):
        #print("mouse Click", self._next_drag, ":")
        if self._image.isUnderMouse():
            if button == QtCore.Qt.RightButton or self._next_drag == "erase_points": 
                self._next_drag = ""
                pindex, rindex, aindex = self.pick(point)
                # print("get Pick", pindex, rindex, aindex)
                if aindex > -1:
                    self.remove_point_or_rect(pindex, rindex, aindex)
            else:
                point = self.mapToScene(point).toPoint()
                self.add_point(point)
                self.point_added.emit(point)

    # override but not implemented ?
    def enterEvent(self, event):
        print('enter event')

    # override
    def mousePressEvent(self, event):
        self._press = event.pos()
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier or self._next_drag == "add_points":
            #print('Shift-press')
            self._save_drag_mode = self.dragMode()
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._rubberband_erase = False
        elif modifiers == QtCore.Qt.ControlModifier or self._next_drag == "erase_points":
            #print('erase_points press')
            self._next_drag = "erase_points"
            self._save_drag_mode = self.dragMode()
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._rubberband_erase = True
        else:
            #print('press')
            self._save_drag_mode = None

        super(ImageViewer, self).mousePressEvent(event)
        if self.dragMode() == QtWidgets.QGraphicsView.RubberBandDrag:
            self.viewport().setCursor(QtCore.Qt.CrossCursor)
        else:
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)

    # override
    def mouseMoveEvent(self, event):
        p = event.pos()
        if self._press is not None:
            dist =  ((p.x() - self._press.x())**2 + (p.y() - self._press.y())**2)**0.5
            if dist > 3:
               self._press = None
        super(ImageViewer, self).mouseMoveEvent(event)
        #print("mouse")
        if self._cross_cursor: 
            self._cross_cursor = False
            #print("set cross cursor")
            self.viewport().setCursor(QtCore.Qt.CrossCursor)

    # override
    def mouseReleaseEvent(self, event):
        # ensure that the left button was pressed *and* released within the
        # geometry of the widget; if so, emit the signal;
        if self._press is not None:
            # if self.rubberBandRect().isNull():
            #     print("rubberBandRect().isNull()")
            # else:
            #     print(self.rubberBandRect())
            # print("mouse release", self._next_drag, ":")
            self.mouse_click(event.pos(), event.button())
        else:
            rect = self.rubberBandRect()
            if not rect.isNull():
                rect = self.mapToScene(rect).boundingRect().toRect()
                if self._rubberband_erase:
                    self.erase(rect)
                else:
                    self.add_rectangle(rect)
        self._press = None
        self._next_drag = ""
        super(ImageViewer, self).mouseReleaseEvent(event)
        if self._save_drag_mode is not None:
            self.setDragMode(self._save_drag_mode)
            self._save_drag_mode = None
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)

    # override
    def enterEvent(self, event):
        super().enterEvent(event)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)

    # override
    def wheelEvent(self, event):
        if self.has_image():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fit_in_view()
            else:
                self._zoom = 0

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = ImageViewer(self)
        self.viewer.point_added.connect(self.point_added)
        self.viewer.rect_added.connect(self.rect_added)
        self.viewer.reset_count_file.connect(self.reset_count_file)
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Open Image')
        self.btnLoad.clicked.connect(self.open_image)
        # mode
        # self.labelDragMode = QtWidgets.QLabel(self)
        # self.labelDragMode.setText('Drag Mode:')
        # self.cbMode = QtWidgets.QComboBox(self)
        # self.cbMode.addItems(["Pan", "Add Points", "Erase Points"])
        # self.cbMode.currentIndexChanged.connect(self.mode_change)
        #
        self.btnAddPoints = QtWidgets.QToolButton(self)
        self.btnAddPoints.setText('Add Dots')
        self.btnAddPoints.clicked.connect(self.mode_add_points)
        #
        self.btnErasePoints = QtWidgets.QToolButton(self)
        self.btnErasePoints.setText('Erase Dots')
        self.btnErasePoints.clicked.connect(self.mode_erase_points)
        #
        self.pixInfo = QtWidgets.QLineEdit(self)
        self.pixInfo.setReadOnly(True)
        #
        self.btnUndo = QtWidgets.QToolButton(self)
        self.btnUndo.setText('Undo')
        self.btnUndo.clicked.connect(self.undo)
        #
        self.labelCount = QtWidgets.QLabel(self)
        self.labelCount.setText('Count:')
        self.countInfo = QtWidgets.QLineEdit(self)
        self.countInfo.setReadOnly(True)
        self.countInfo.setText('0')
        self.viewer.update_count.connect(self.update_count)
        #
        self.cbDrawSize  = QtWidgets.QComboBox()
        self.cbDrawSize.addItem("1")
        self.cbDrawSize.addItem("2")
        self.cbDrawSize.addItems(["3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"])
        self.cbDrawSize.currentIndexChanged.connect(self.change_drawing_size)
        self.cbDrawSize.setCurrentIndex(5);
        self.viewer.update_drawing_size(6)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        # HBlayout.addWidget(self.labelDragMode)
        # HBlayout.addWidget(self.cbMode)
        HBlayout.addWidget(self.pixInfo)
        HBlayout.addWidget(self.btnAddPoints)
        HBlayout.addWidget(self.btnErasePoints)
        HBlayout.addWidget(self.btnUndo)
        HBlayout.addWidget(self.labelCount)
        HBlayout.addWidget(self.countInfo)
        HBlayout.addWidget(self.cbDrawSize)
        VBlayout.addLayout(HBlayout)
        #
        print_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+P"), self)
        print_shortcut.activated.connect(self.print_image)
        undo_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo)
        # file
        self._count_filename = None
        self._cfile = None

    # def keyPressEvent(self, event):
    #     print("get a key event", event.text())
    #     if event.key() == QtCore.Qt.Key_S:
    #         print("S pressed", event.nativeModifiers())
    
    # def mode_change(self,i):
        #print("mode_change: Items in the list are : %d" % i)
    #    self.viewer.update_drag_mode(i)
    def mode_add_points(self):
        self.viewer.update_drag_mode("add_points")

    def mode_erase_points(self):
        self.viewer.update_drag_mode("erase_points")

    def undo(self):
        self.viewer.undo()

    def change_drawing_size(self,i):
        #print("changeDrawingSize: Items in the list are : %d" % i)
        self.viewer.update_drawing_size(i+1)

    def open_image(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JPEG (*.jpeg);;JPG (*.jpg);;PNG (*.png)", options=options)
        if fileName:
           print("attept to load: " + fileName)
           self.load_image(fileName)

    def load_image(self, fileName):
        print("try to load image", fileName)
        self.viewer.set_image(QtGui.QPixmap(fileName))
        if self.viewer.has_image():
            print("image loaded")
            self.load_create_count_file(fileName)
        else:
            print("failed to load image")
       
    def load_create_count_file(self, fileName):
        db = os.path.splitext(fileName)[0]
        dbc = db + ".count"
        dbd = db + ".dlcount"
        dbn = dbc
        isdl = False
        #print(dbn)
        if not os.path.isfile(dbn):
            dbn = dbd
            isdl = True
        if os.path.isfile(dbn):
            print("dlcount or count file exits: " + dbn)
            self._cfile = open(dbn, 'r')
            c = 0
            points = []
            rects = []
            alls = []
            for line in self._cfile:
               c += 1
               p = line.strip().split(",")
               if len(p) == 2:
                  # print("Line{}: {}".format(c, line.strip()))
                  points.append(QtCore.QPoint(int(p[0]), int(p[1])))
                  alls.append(QtCore.QPoint(int(p[0]), int(p[1])))
                  #self.viewer.add_point(QtCore.QPoint(int(p[0]), int(p[1])))
               if len(p) == 4:
                   rects.append(QtCore.QRect(int(p[0]), int(p[1]), int(p[2]), int(p[3])))
                   alls.append(QtCore.QRect(int(p[0]), int(p[1]), int(p[2]), int(p[3])))
            print("points loaded %d, rects loaded %d" % (len(points), len(rects)))
            if len(points) > 0:
               self.viewer.add_points(points)
            if len(rects) > 0:
               self.viewer.add_rectangles(rects)
            if len(alls) > 0:
               self.viewer.add_undos(alls)
            self._count_filename = dbc
            if isdl:
                self.reset_count_file(alls)
            else:
                self._cfile.close()
                self._cfile = open(dbc, 'a')
        else:
            isdl = False
            print("count file does not exit, create it: " + dbc)
            self._count_filename = dbc
            self._cfile = open(dbc, 'w')
            self.detect_faces(fileName)

    def print_image(self):
        if not self.viewer.has_image():
            return
        pix = self.viewer.get_pixmap()
        #
        db = os.path.splitext(self._count_filename)[0]
        dbn = db + "-print-" + str(self.viewer._count) + ".jpg"
        file = QtCore.QFile(dbn)
        #file.open(QIODevice::WriteOnly)
        pix.save(file, "JPG")
        print("view printed on: ", dbn)
        file.close()

    def point_added(self, pos):
       self.pixInfo.setText('%d, %d' % (pos.x(), pos.y()))
       if self._cfile is not None:
          self._cfile.write('%d,%d\n' % (pos.x(), pos.y()))
          self._cfile.flush()

    def rect_added(self, rect):
       self.pixInfo.setText('%d, %d %d, %d' % (rect.left(), rect.top(), rect.width(), rect.height()))
       if self._cfile is not None:
          self._cfile.write('%d,%d,%d,%d\n' % (rect.left(), rect.top(), rect.width(), rect.height()))
          self._cfile.flush()

    def reset_count_file(self, alls):
        self._cfile.close()
        self._cfile = open(self._count_filename, 'w')
        for pr in alls:
            if isinstance(pr, QtCore.QPoint):
                self._cfile.write('%d,%d\n' % (pr.x(), pr.y()))
            if isinstance(pr, QtCore.QRect):
                self._cfile.write('%d,%d,%d,%d\n' % (pr.left(), pr.top(), pr.width(), pr.height()))
        self._cfile.flush()

    def update_count(self, count):
        self.countInfo.setText('%d' % count) 

    def detect_faces(self, filename):
        try:
            import cv2
        except:
            print("install python3 opencv if you want face detection\n the first time you open an image file")
            return
        # Load the cascade
        face_cascade = cv2.CascadeClassifier('cvface/haarcascade_frontalface_default.xml')
        # Read the input image
        img = cv2.imread(filename)
        # Convert into grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces 
        # see https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Object_Detection_Face_Detection_Haar_Cascade_Classifiers.php
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)  # 4, [20, 20]
        # Draw rectangle around the faces
        qfaces = []
        for (x, y, w, h) in faces:
            qp = QtCore.QPoint(int(x+(w/2)), int(y+(h/2)))
            qfaces.append(qp)
        print("opencv found %d faces" % len(qfaces))
        if len(qfaces) > 0:
           self.viewer.add_points(qfaces)
        for p in qfaces:
            self.point_added(p)

    # stupid
    def detect_contours(self, filename):
        try:
            import cv2
        except:
            print("install python3 opencv if you want face detection\n the first time you open an image file")
            return
        # Read the input image
        img = cv2.imread(filename)
        # Convert into grayscale
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Applying Gaussian Blur to reduce noise
        blur_frame = cv2.GaussianBlur(gray_frame, (11,11), 0)
        # Binarizing frame - Thresholding
        ret, threshold_frame = cv2.threshold(blur_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imwrite("test.png", threshold_frame)
        # Identifying Contours
        (contours, _ ) = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Drawing Boundary Boxes for each Contour
        qfaces = []
        for i in contours:
            x, y, w, h = cv2.boundingRect(i)
            qp = QtCore.QPoint(int(x+(w/2)), int(y+(h/2)))
            qfaces.append(qp)
        print("opencv found %d contour" % len(qfaces))
        if len(qfaces) > 0:
           self.viewer.add_points(qfaces)
        for p in qfaces:
            self.point_added(p)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    c = 0
    for arg in sys.argv:
       #print(sys.argv[c])
       c += 1
    fn = None
    if c >= 2:
        fn = sys.argv[c-1]
    window = Window()
    screen = app.primaryScreen()
    sg = screen.size()
    #sg = QtGui.QDesktopWidget().screenGeometry()
    window.resize(int(sg.width()/2), int(sg.height()/2))
    window.setWindowTitle('pointsrouges')
    window.show()
    if fn is not None:
        window.load_image(fn)
    sys.exit(app.exec_())