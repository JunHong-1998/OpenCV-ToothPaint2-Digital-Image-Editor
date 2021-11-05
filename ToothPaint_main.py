import sys
import os
from ToothPaint_CV import*
from ToothPaint_UI import*

CV = Paint_CV()

class Paint(QMainWindow):
    def __init__(self):
        self.new = True
        self.selection = False
        self.Move = False
        self.toolSelected = 0
        self.complete_selection = False
        self.init_coords = []
        self.color = (0,0,0)
        self.color_bg = (255,255,255)
        self.color_backdrop = None
        self.thickness = 1
        self.point = False
        self.zoom = [1,1]
        self.Aspc_ratio = True
        self.resize_value=[100,100,0,0]
        self.grid = 0
        self.font = [0, 1.0]
        self.filtered = False
        self.collection = []
        self.filterINDEX = 0
        self.mergeINDbtn = []
        self.splitINDbtn = []
        self.image_BACKDROP = [None, None]
        self.image_SPLIT = [None, None]
        super(Paint,self).__init__()
        self.UI = WidgetUI()
        self.resize(1225, 770)
        self.setWindowIcon(QIcon("TP_assets/icon.png"))
        self.setWindowTitle("TOOTH PAINT by Low Jun Hong BS18110173")
        self.UI.SplashScreen()
        self.initUI()

    def closeEvent(self, event):
        event.ignore()
        self.UI.QuitDialog(sys)

    def initUI(self):
        tracker = MouseTracker(self.UI.canvas)
        tracker.positionChanged.connect(self.DetectPOS)
        self.zoom_slider = self.UI.SliderWidget(Qt.Horizontal, 100, 1, 500, 150, lambda :self.zoomTool(1))
        self.zoom_percentage = self.UI.Label_TextOnly("\t100%", ('Calibri', 10))
        plus_btn = self.UI.PushBtnIcon("TP_assets/plus.png", lambda :self.zoomTool(2))
        minus_btn = self.UI.PushBtnIcon("TP_assets/minus.png", lambda :self.zoomTool(3))
        self.pixel_dim = self.UI.Label_TextOnly("Dimension :      -      ", ('Calibri', 10))
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.UI.canvas)
        self.setCentralWidget(self.scrollArea)
        self.dockProperties = self.Dock_Details(True)
        self.dockPreview = self.Dock_Details(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockProperties)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockPreview)
        self.statusBar()
        self.UI.StatusBAR(self.statusBar(), [None, self.pixel_dim, None, self.zoom_percentage, minus_btn, self.zoom_slider, plus_btn])
        self.Menubars()
        self.Toolbars()
        self.TextEdit = QLineEdit(self)
        self.TextEdit.setText("Please Enter Here")
        self.TextEdit.textChanged.connect(self.UpdateText)
        self.TextEdit.hide()

    def DetectPOS(self, pos):
        if 1<=self.toolSelected<=7:
            if self.toolSelected == 1 and self.complete_selection:
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.cursorINregion((mouse_x, mouse_y)):
                    self.UI.canvas.setCursor(QCursor(Qt.SizeAllCursor))
                else:
                    self.UI.canvas.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.UI.canvas.setCursor(QCursor(Qt.CrossCursor))
        elif self.toolSelected==8 and not self.point:
            self.UI.canvas.setCursor(QCursor(Qt.IBeamCursor))
        elif self.toolSelected==9:
            self.UI.canvas.setCursor(QCursor(Qt.ClosedHandCursor))
        elif self.toolSelected==10:
            self.UI.canvas.setCursor(QCursor(Qt.PointingHandCursor))
        self.statusBar().showMessage(str(pos.x()) + ", " + str(pos.y()) + "px")

    def keyPressEvent(self, event):
        if self.toolSelected==1 and self.complete_selection and event.key()==Qt.Key_Delete:     #Delete selected image
            self.selection = self.Move = self.complete_selection = self.manual_selection = False
            image = self.image_backup.copy()
            image = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
            image[:] = self.color_bg
            self.image = CV.OverlayImage(image, self.image, self.toolCoords)
            self.image_CVT = CV.OverlayImage(image, self.image_CVT, self.toolCoords)
            self.Render(self.image)
        elif self.toolSelected==8 and self.point:
            if event.key()==Qt.Key_Escape:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.point = False
                self.TextEdit.hide()
                self.Render(self.image)

    def mousePressEvent(self, event):
        if self.toolSelected!=0:
            if event.button()==1:
                pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if not self.selection:
                        self.image_backup = self.image.copy()  # creating image backup
                        self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.selection = True
                    else:
                        if self.cursorINregion((mouse_x, mouse_y)):
                            self.Move = True
                            LR, UD, dst = CV.calcRegion((mouse_x, mouse_y, self.toolCoords[0], self.toolCoords[1]))
                            self.init_coords = (dst[0] * LR, dst[1] * UD)       # distance parameter instead of fixed point #moving de coord
                        else:
                            self.selection = self.Move = self.complete_selection = self.manual_selection = False
                            self.image = CV.OverlayImage(self.image_backup.copy(), self.image, self.toolCoords)
                            self.image_CVT = CV.OverlayImage(self.image_CVT_backup.copy(), self.image_CVT, self.toolCoords)
                            self.Render(self.image)
                elif self.toolSelected == 2 or self.toolSelected == 9:
                    self.init_coords = (mouse_x, mouse_y)
                elif 3<=self.toolSelected<= 7:
                    self.image_backup = self.image.copy()           # creating image backup
                    self.image_CVT_backup = self.image_CVT.copy()   # creating image backup for GrayScale
                    self.init_coords = (mouse_x, mouse_y)
                elif self.toolSelected==8:
                    if not self.point:
                        self.image_backup = self.image.copy()  # creating image backup
                        self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.point = True
                        self.TextEdit.move(self.init_coords[0], self.init_coords[1])
                        self.TextEdit.setText("Please Enter Here")
                        self.TextEdit.show()
                        self.UpdateText()
                    else:
                        self.point = False
                        CV.drawText(self.image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        CV.drawText(self.image_CVT, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        self.TextEdit.hide()
                elif self.toolSelected == 10:
                    color = self.image[mouse_y, mouse_x]
                    self.color = (int(color[0]),int(color[1]), int(color[2]))
                    CV.Color_picker(self.color)
                    self.colorBtn.setIcon(QIcon("TP_assets/color.png"))

    def mouseReleaseEvent(self, event):
        if self.toolSelected != 0:
            if event.button()==1:
                pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if self.selection:
                        if not self.Move and not self.complete_selection:
                            self.toolCoords = CV.ReLocateCoords([self.init_coords[0], self.init_coords[1], mouse_x, mouse_y])
                            image = self.image_backup.copy()
                            CV.drawPrimitive(image, self.toolCoords, 1, None, int(2/max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp
                            self.Render(image)
                            self.image_backup = CV.CropImage(self.image.copy(), self.toolCoords)
                            self.image_CVT_backup = CV.CropImage(self.image_CVT.copy(), self.toolCoords)
                            CV.drawPrimitive(self.image, self.toolCoords, 5, (255, 255, 255), -1)       # make empty to selected region on base image
                            self.image_backup2 = self.image.copy()
                            CV.drawPrimitive(self.image_CVT, self.toolCoords, 5, (255, 255, 255), -1)  # make empty to selected region on base image
                            self.complete_selection = self.manual_selection = True
                        else:   #moving cropped image
                            self.Move = False
                elif 3 <= self.toolSelected <= 7:
                    if self.thickness == -1 and 6 <= self.toolSelected <= 7:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                    else:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                    self.Render(self.image)
                    self.image_backup = self.image.copy()  # creating image backup
                    self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale

    def mouseMoveEvent(self, event):
        pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
        mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
        if self.toolSelected==1:
            if self.selection:
                image = self.image_backup.copy()
                if not self.Move and not self.complete_selection:
                    CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 1, None, int(1/max(self.zoom[0], self.zoom[1])))  # only using backup image to render since temp
                    self.Render(image)
                else:
                    self.moveImage((mouse_x, mouse_y), image)
        elif self.toolSelected==2:
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
        elif 3<=self.toolSelected<=7:
            image = self.image_backup.copy()
            if self.thickness==-1 and 6<=self.toolSelected<=7:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected+2, self.color)
            else:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
            self.Render(image)
        elif self.toolSelected==9:
            width = abs(self.thickness*2)
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
            self.image_backup = self.image.copy()  # creating image backup
            self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale

    def cursorINregion(self, mousepos):
        inregion = False
        if self.toolCoords[2] < self.toolCoords[0]:
            if self.toolCoords[2] <= mousepos[0]<=self.toolCoords[0]:
                inregion = True
        elif self.toolCoords[2] > self.toolCoords[0]:
            if self.toolCoords[0] <= mousepos[0] <= self.toolCoords[2]:
                inregion = True
        if inregion:
            inregion = False
            if self.toolCoords[3] < self.toolCoords[1]:
                if self.toolCoords[3] <= mousepos[1]<=self.toolCoords[1]:
                    inregion = True
            elif self.toolCoords[3] > self.toolCoords[1]:
                if self.toolCoords[1] <= mousepos[1] <= self.toolCoords[3]:
                    inregion = True
        return inregion

    def sharpenKernelUPDATE(self):
        value = self.spinSharpenKernel.value() * self.spinSharpenKernel.value()
        self.spinSharpenLevel.setMinimum(value)
        self.spinSharpenLevel.setValue(value)

    def ROWCOL_update(self, flag):
        spinRow = spinCol = currentROWCOL = table = None
        if flag == 1:
            spinRow, spinCol = self.spinROW.value(), self.spinCOL.value()
            currentROWCOL = self.currentROWCOL
            table = self.customTable
        elif flag == 2:
            spinRow, spinCol = self.spinMergeROW.value(), self.spinMergeCOL.value()
            currentROWCOL = self.currentMRC
            table = self.mergeTABLE
        elif flag == 3:  # flag 3
            spinRow, spinCol = self.spinSplitROW.value(), self.spinSplitCOL.value()
            currentROWCOL = self.currentSRC
            table = self.splitTABLE
        if spinRow > currentROWCOL[0]:
            table.insertRow(table.rowCount())
            if flag == 1:
                for col in range(spinCol):
                    table.setItem(table.rowCount() - 1, col, QTableWidgetItem("0"))
        elif currentROWCOL[0] > spinRow:
            table.removeRow(table.rowCount() - 1)
        if spinCol > currentROWCOL[1]:
            table.insertColumn(table.columnCount())
            if flag == 1:
                for row in range(spinRow):
                    table.setItem(row, table.columnCount() - 1, QTableWidgetItem("0"))
        elif currentROWCOL[1] > spinCol:
            table.removeColumn(table.columnCount() - 1)
        if flag == 1:
            self.currentROWCOL = [spinRow, spinCol]
        else:
            if flag == 2:
                self.mergeINDbtn.clear()
            elif flag == 3:
                self.splitINDbtn.clear()
            for row in range(spinRow):
                buttons = []
                for col in range(spinCol):
                    if flag == 2:
                        buttons.append([self.UI.PushBtnIcon("TP_assets/plus.png", None, True), None, None])
                    elif flag == 3:
                        buttons.append(self.UI.PushBtnIcon("TP_assets/split.png", None, True))
                if flag == 2:
                    self.mergeINDbtn.append(buttons)
                elif flag == 3:
                    self.splitINDbtn.append(buttons)
            for row in range(spinRow):
                for col in range(spinCol):
                    if flag == 2:
                        table.setCellWidget(row, col, self.mergeINDbtn[row][col][0])
                        self.mergeINDbtn[row][col][0].clicked.connect(lambda _, shape=(row, col): self.viewAvailableImage(shape))
                    elif flag == 3:
                        table.setCellWidget(row, col, self.splitINDbtn[row][col])
                        self.splitINDbtn[row][col].clicked.connect(lambda _, shape=(row, col): self.collectionDialog(shape))
            if flag == 2:
                self.currentMRC = [spinRow, spinCol]
            elif flag == 3:
                self.currentSRC = [spinRow, spinCol]

    def Dock_Details(self, flag):
        dock_container = QWidget()
        dock_container_layout = QVBoxLayout()
        if flag:
            self.taby = QTabWidget()
            tab_HIST = QWidget()
            tab_FILTER = QScrollArea()
            tab_MERGE = QScrollArea()
            tab_SPLIT = QScrollArea()
            self.taby.addTab(tab_HIST, "Histogram")
            self.taby.addTab(tab_FILTER, "Filter")
            self.taby.addTab(tab_MERGE, "Merge")
            self.taby.addTab(tab_SPLIT, "Split")
            content_FILTER = QWidget()
            tab_FILTER.setWidget(content_FILTER)
            FilterLay = QVBoxLayout(content_FILTER)
            tab_FILTER.setWidgetResizable(True)
            content_MERGE = QWidget()
            tab_MERGE.setWidget(content_MERGE)
            MergeLay = QVBoxLayout(content_MERGE)
            tab_MERGE.setWidgetResizable(True)
            content_SPLIT = QWidget()
            tab_SPLIT.setWidget(content_SPLIT)
            SplitLay = QVBoxLayout(content_SPLIT)
            tab_SPLIT.setWidgetResizable(True)
            tab_HIST.layout = QVBoxLayout()
            HIST_btn_lay = QHBoxLayout()
            self.hist = HistogramPlot()
            tab_HIST.layout.addWidget(self.hist)
            HIST_btn_lay.addWidget(self.UI.PushBtnText("Equalize", lambda: self.HistEqualize(1)))
            HIST_btn_lay.addWidget(self.UI.PushBtnText("CLAHE", lambda: self.HistEqualize(2)))
            tab_HIST.layout.addLayout(HIST_btn_lay)
            tab_HIST.setLayout(tab_HIST.layout)
            FilterLay.addLayout(self.FilterLayout())
            MergeLay.addLayout(self.MergeLayout())
            SplitLay.addLayout(self.SplitLayout())
            dock_container_layout.addWidget(self.taby)
            dock_container.setLayout(dock_container_layout)
            dock = QDockWidget("Filtration", self)
        else:
            dock_container_layout.addWidget(self.UI.prevImg)
            dock_Bottom = QHBoxLayout()
            dock_Bottom.addWidget(self.UI.PushBtnText("APPLY", lambda: self.ApplyRestore(1)))
            dock_Bottom.addWidget(self.UI.PushBtnIcon('TP_assets/love.png', lambda: self.collectionDialog(2), None, (25, 25)))
            dock_Bottom.addWidget(self.UI.PushBtnText("RESTORE", lambda: self.ApplyRestore(3)))
            dock_container_layout.addLayout(dock_Bottom)
            dock_container.setLayout(dock_container_layout)
            dock = QDockWidget("Preview", self)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dock.setWidget(dock_container)
        dock.setEnabled(False)
        return dock

    def SplitLayout(self):
        layout = QVBoxLayout()
        SPLIT_RC_lay = QHBoxLayout()
        split_lay = QHBoxLayout()
        self.currentSRC = [2, 2]
        self.spinSplitROW = self.UI.SpinBox(True, 1, 100, 2, 40, action=lambda: self.ROWCOL_update(3))
        self.spinSplitCOL = self.UI.SpinBox(True, 1, 100, 2, 40, action=lambda: self.ROWCOL_update(3))
        self.splitTABLE = self.UI.TableWIDGET(2, 2, (285, 285))
        self.ROWCOL_update(3)
        self.split_image = self.UI.PushBtnIcon("TP_assets/image.png", self.viewAvailableImage, None, size=(150, 150))
        SPLIT_RC_lay.addStretch(1)
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.spinSplitROW)
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.spinSplitCOL)
        SPLIT_RC_lay.addStretch(1)
        layout.addWidget(self.UI.Label_TextOnly("IMAGE", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        split_lay.addWidget(self.split_image)
        layout.addLayout(split_lay)
        layout.addWidget(self.UI.Label_TextOnly("GRID", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(SPLIT_RC_lay)
        layout.addWidget(self.splitTABLE)
        layout.addWidget(self.UI.PushBtnText("REFRESH", self.SplitFunc, ('Calibri', 12)))
        return layout

    def viewAvailableImage(self, shape=None):
        self.imageList_dlg = QDialog(self)
        self.imageList_dlg.setWindowTitle("Image Source")
        dlg_lay = QHBoxLayout()
        list_lay = QVBoxLayout()
        button_lay2 = QVBoxLayout()
        button_lay1 = QHBoxLayout()
        self.ImageSource = QListWidget(self)
        self.ImageSource.setViewMode(QListView.IconMode)
        self.ImageSource.setIconSize(QSize(157, 157))
        self.ImageSource.setFixedSize(190, 250)
        self.ImageSource.itemClicked.connect(lambda: self.ACTIONImageFROMlist(1))
        self.ImageSource_selected = QLabel()
        self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap("TP_assets/image.png"), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        for img in self.collection:
            self.AddImageTOlist(img)
        button_lay1.addWidget(self.UI.PushBtnText("INSERT", lambda: self.fileDialog(3)))
        button_lay1.addWidget(self.UI.PushBtnText("COLOR", lambda: self.colorDialog(3)))
        list_lay.addWidget(self.ImageSource)
        list_lay.addLayout(button_lay1)
        button_lay2.addStretch(2)
        button_lay2.addWidget(self.UI.PushBtnText("APPLY", lambda: self.ACTIONImageFROMlist(5, shape)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.UI.PushBtnText("REMOVE", lambda: self.ACTIONImageFROMlist(2)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.UI.PushBtnText("CLEAR", lambda: self.ACTIONImageFROMlist(3)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.ImageSource_selected)
        dlg_lay.addLayout(list_lay)
        dlg_lay.addLayout(button_lay2)
        self.imageList_dlg.setLayout(dlg_lay)
        self.imageList_dlg.exec_()

    def AddImageTOlist(self, img):
        image_RGBA = cv2.cvtColor(img[0], cv2.COLOR_BGR2BGRA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        item = QListWidgetItem(img[1])
        item.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), 157, 157, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.ImageSource.addItem(item)

    def ACTIONImageFROMlist(self, flag, shape=None):
        if flag == 1:  # insert
            collection = self.collection[self.ImageSource.currentRow()]
            image_RGBA = cv2.cvtColor(collection[0], cv2.COLOR_BGR2BGRA)
            QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
            self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap.fromImage(QtImg), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.color_backdrop = None  # Not choosing color as backdrop
        elif flag == 2:  # remove
            if self.ImageSource.count() == 0:
                return
            self.collection.pop(self.ImageSource.currentRow())
            self.ImageSource.takeItem(self.ImageSource.currentRow())
        elif flag == 3:  # clear
            self.collection.clear()
            self.ImageSource.clear()
        elif flag == 4:  # Color
            image = np.zeros((100, 100, 3), np.uint8)
            image[:] = self.color_backdrop
            image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
            self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap.fromImage(QtImg), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.ImageSource.clearSelection()
        elif flag == 5:  # apply to backdrop
            if not self.color_backdrop and self.ImageSource.selectedIndexes() == []:
                return
            else:
                if self.color_backdrop:
                    image = np.zeros((1000, 1000, 3), np.uint8)
                    image[:] = self.color_backdrop
                else:
                    collection = self.collection[self.ImageSource.currentRow()]
                    image = collection[0]
                image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
                QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
                if not shape:
                    if self.taby.currentIndex() == 2:
                        self.backdrop_image.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), 150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                        self.image_BACKDROP = [image, True]
                    elif self.taby.currentIndex() == 3:
                        self.split_image.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), 150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                        self.image_SPLIT = [image, True]
                        self.SplitFunc()
                else:
                    if type(shape) == tuple:
                        btn = self.mergeINDbtn[shape[0]][shape[1]][0]
                        btn.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), btn.width(), btn.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
                        btn.setIconSize(QSize(btn.size()))
                        self.mergeINDbtn[shape[0]][shape[1]][1], self.mergeINDbtn[shape[0]][shape[1]][2] = image, True
                    else:
                        self.CleanSelectedRegion()
                        self.image_backup = image
                        self.toolSelected = 1
                        self.complete_selection = self.selection = True
                        self.toolCoords = [0, 0, self.image_backup.shape[1], self.image_backup.shape[0]]
                        image = CV.OverlayImage(self.image_backup.copy(), self.image.copy(), self.toolCoords)
                        CV.drawPrimitive(image, self.toolCoords, 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp
                        self.Render(image)
                self.imageList_dlg.close()
        if 2 <= flag <= 3:
            if self.collection:
                self.ACTIONImageFROMlist(1)
            else:
                self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap("TP_assets/image.png"), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def SplitFunc(self):
        if not self.image_SPLIT[1]:
            return
        self.sliced_image = []
        h, w, _ = self.image_SPLIT[0].shape
        gapW, gapH = int(w / self.spinSplitCOL.value()), int(h / self.spinSplitROW.value())
        for row in range(self.spinSplitROW.value()):
            sliced_img = []
            for col in range(self.spinSplitCOL.value()):
                image = self.image_SPLIT[0].copy()
                image = CV.CropImage(image, (col * gapW, row * gapH, col * gapW + gapW, row * gapH + gapH))
                sliced_img.append(image)
                image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
                QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
                btn = self.splitINDbtn[row][col]
                btn.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), btn.width(), btn.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
                btn.setIconSize(QSize(btn.size()))
            self.sliced_image.append(sliced_img)

    def MergeFunc(self):
        self.filterINDEX = 15
        w, h = int(self.MergeWIDTH.text()), int(self.MergeHEIGHT.text())
        if not self.image_BACKDROP[1]:
            background = np.zeros((w, h, 3), np.uint8)
            background[:] = (255, 255, 255)
        else:
            background = self.image_BACKDROP[0]
        background = CV.ResizeImage(background, (w, h))
        gapW, gapH = int(w / self.spinMergeCOL.value()), int(h / self.spinMergeROW.value())
        for row in range(self.spinMergeROW.value()):
            for col in range(self.spinMergeCOL.value()):
                if self.mergeINDbtn[row][col][2]:
                    coord = col * gapW, row * gapH
                    image = self.mergeINDbtn[row][col][1]
                    image = CV.ResizeImage(image, (gapW, gapH))
                    background = CV.OverlayImage(image, background, coord)
        self.RenderPreviewIMG(background)
        return background

    def MergeLayout(self):
        layout = QVBoxLayout()
        MERGE_RC_lay = QHBoxLayout()
        MERGE_DIM_lay = QHBoxLayout()
        self.currentMRC = [1, 1]
        self.spinMergeROW = self.UI.SpinBox(True, 1, 100, 1, 40, action=lambda: self.ROWCOL_update(2))
        self.spinMergeCOL = self.UI.SpinBox(True, 1, 100, 1, 40, action=lambda: self.ROWCOL_update(2))
        self.MergeWIDTH = self.UI.LineEdit("1280", size=(55, 25), valid=QIntValidator())
        self.MergeHEIGHT = self.UI.LineEdit("720", size=(55, 25), valid=QIntValidator())
        MERGE_RC_lay.addStretch(1)
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.spinMergeROW)
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.spinMergeCOL)
        MERGE_RC_lay.addStretch(1)
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("WIDTH", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.MergeWIDTH)
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("HEIGHT", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.MergeHEIGHT)
        layout.addWidget(self.UI.Label_TextOnly("BACKDROP", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        backdrop_lay = QHBoxLayout()
        self.backdrop_image = self.UI.PushBtnIcon("TP_assets/image.png", self.viewAvailableImage, None, size=(150, 150))
        backdrop_lay.addWidget(self.backdrop_image)
        layout.addLayout(backdrop_lay)
        layout.addWidget(self.UI.Label_TextOnly("DIMENSION", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(MERGE_DIM_lay)
        layout.addWidget(self.UI.Label_TextOnly("GRID", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(MERGE_RC_lay)
        self.mergeTABLE = self.UI.TableWIDGET(1, 1, (285, 285))
        self.ROWCOL_update(2)
        layout.addWidget(self.mergeTABLE)
        layout.addWidget(self.UI.PushBtnText("MERGE", self.MergeFunc, ('Calibri', 12)))
        return layout

    def FilterLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Smoothing", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinKERNEL = self.UI.SpinBox(True, 3, 1000, 3, 40, True)  # restrict even number
        self.spinDEPTH = self.UI.SpinBox(True, 1, 1000, 1, 40)
        self.spinCOLSPACE = self.UI.SpinBox(True, 1, 1000, 1, 40)
        opt_overall = QVBoxLayout()  # add 4 row together
        opt_kernel = QHBoxLayout()
        opt_kernel.addStretch(1)
        opt_kernel.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_kernel.addWidget(self.spinKERNEL)
        opt_kernel.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("ALL", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_kernel)
        opt_overall.addLayout(self.FilterLIST(1))
        opt_other = QHBoxLayout()
        opt_other.addWidget(self.UI.Label_TextOnly("Depth", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinDEPTH)
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("Color|Space", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinCOLSPACE)
        opt_overall.addWidget(self.UI.Label_TextOnly("Bilateral Filter", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(2))
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Sharpening", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinContrast = self.UI.SpinBox(False, 0, 100, 0, 55)
        self.spinSharpenKernel = self.UI.SpinBox(True, 3, 100, 3, 40, True, self.sharpenKernelUPDATE)  # restrict even number
        self.spinSharpenLevel = self.UI.SpinBox(True, 9, 100, 9, 40)  # Limit lower bound
        opt_kernel = QHBoxLayout()
        opt_kernel.addStretch(1)
        opt_kernel.addWidget(self.UI.Label_TextOnly("Contrast LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_kernel.addWidget(self.spinContrast)
        opt_kernel.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("Contrasting", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_kernel)
        opt_overall.addLayout(self.FilterLIST(3))
        opt_other = QHBoxLayout()
        opt_other.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinSharpenKernel)
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinSharpenLevel)
        opt_overall.addWidget(self.UI.Label_TextOnly("Sharpening", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(4))
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Effects", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinBitLevel = self.UI.SpinBox(True, 0, 7, 0, 30)  # 0-7
        opt_overall.addLayout(self.FilterLIST(5))
        opt_other = QHBoxLayout()
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("Bit LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinBitLevel)
        opt_other.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("Bit Plane Slicing", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(6))
        layout.addLayout(opt_overall)
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Customization", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.currentROWCOL = [3, 3]
        self.spinROW = self.UI.SpinBox(True, 1, 100, 3, 40, action=lambda: self.ROWCOL_update(1))
        self.spinCOL = self.UI.SpinBox(True, 1, 100, 3, 40, action=lambda: self.ROWCOL_update(1))
        self.customTable = self.UI.TableWIDGET(3, 3, (285, 285))
        delegate = DelegateTable_SpinBox()
        self.customTable.setItemDelegate(delegate)
        self.customTable.setItem(0, 0, QTableWidgetItem("3"))
        self.customTable.setItem(0, 1, QTableWidgetItem("-2"))
        self.customTable.setItem(0, 2, QTableWidgetItem("-3"))
        self.customTable.setItem(1, 0, QTableWidgetItem("-4"))
        self.customTable.setItem(1, 1, QTableWidgetItem("8"))
        self.customTable.setItem(1, 2, QTableWidgetItem("-6"))
        self.customTable.setItem(2, 0, QTableWidgetItem("5"))
        self.customTable.setItem(2, 1, QTableWidgetItem("-1"))
        self.customTable.setItem(2, 2, QTableWidgetItem("0"))
        opt_RowCol = QHBoxLayout()
        opt_RowCol.addStretch(1)
        opt_RowCol.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.spinROW)
        opt_RowCol.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.spinCOL)
        opt_RowCol.addStretch(1)
        opt_overall.addLayout(opt_RowCol)
        opt_overall.addWidget(self.customTable)
        opt_overall.addLayout(self.FilterLIST(7))
        layout.addLayout(opt_overall)
        return layout

    def FilterLIST(self, flag):
        layout = QVBoxLayout()
        if flag == 1:
            layout.addWidget(self.UI.PushBtnText("Gaussian-Blur", lambda: self.FilterFunc(3), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Median-Blur", lambda: self.FilterFunc(4), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Average-Blur", lambda: self.FilterFunc(5), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Box-Filter", lambda: self.FilterFunc(6), ('Calibri', 12)))
        elif flag == 2:
            layout.addWidget(self.UI.PushBtnText("Bilateral-Filter", lambda: self.FilterFunc(7), ('Calibri', 12)))
        elif flag == 3:
            layout.addWidget(self.UI.PushBtnText("Contrast", lambda: self.FilterFunc(8), ('Calibri', 12)))
        elif flag == 4:
            layout.addWidget(self.UI.PushBtnText("Sharpen", lambda: self.FilterFunc(9), ('Calibri', 12)))
        elif flag == 5:
            layout.addWidget(self.UI.PushBtnText("Emboss", lambda: self.FilterFunc(10), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Sepia", lambda: self.FilterFunc(11), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("MexicanHat", lambda: self.FilterFunc(12), ('Calibri', 12)))
        elif flag == 6:
            layout.addWidget(self.UI.PushBtnText("Bit-Plane Slice", lambda: self.FilterFunc(13), ('Calibri', 12)))
        elif flag == 7:  # Customize
            layout.addWidget(self.UI.PushBtnText(">>> Customize <<<", lambda: self.FilterFunc(14), ('Calibri', 12)))
        return layout

    def FilterFunc(self, flag):
        self.CleanSelectedRegion()
        if not self.filtered:  # create filter backup image
            self.filtered = True
            self.image_FLT = self.image_CVT.copy()
        self.filterINDEX = flag
        if 3 <= flag <= 6:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, Ksize=self.spinKERNEL.value())
        elif flag == 7:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, depth=self.spinDEPTH.value(), colspace=self.spinCOLSPACE.value())
        elif flag == 8:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, contrast=self.spinContrast.value())
        elif flag == 9:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, Ksize=self.spinSharpenKernel.value(), sharpen=self.spinSharpenLevel.value())
        elif 10 <= flag <= 12:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX)
        elif flag == 13:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, bitLevel=self.spinBitLevel.value())
        elif flag == 14:
            customFilter = []
            for row in range(self.spinROW.value()):
                newrow = []
                for col in range(self.spinCOL.value()):
                    newrow.append(float(self.customTable.item(row, col).text()))
                customFilter.append(newrow)
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, customFilter=customFilter)
        self.RenderPreviewIMG(image)
        return image

    def ApplyRestore(self, flag):
        if flag == 1:  # Apply
            if self.filterINDEX == 15:
                self.image = self.MergeFunc()
                self.image_CVT = self.image.copy()
                self.filtered = False
                self.filterINDEX = 0
                self.collection.append((self.image, "Merge image"))
                self.zoomTool(4)
            else:
                if 1 <= self.filterINDEX <= 2:
                    self.image_FLT = self.HistEqualize(self.filterINDEX)
                elif 3 <= self.filterINDEX <= 14:
                    self.image_FLT = self.FilterFunc(self.filterINDEX)
                self.image_FLT = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_FLT.copy())
                self.image = self.image_FLT
            self.hist.Plot(self.image)
            self.Render(self.image)
        elif flag == 2:  # Collection
            if 1 <= self.filterINDEX <= 2:
                image = self.HistEqualize(self.filterINDEX)
            elif 3 <= self.filterINDEX <= 14:
                image = self.FilterFunc(self.filterINDEX)
            elif self.filterINDEX == 15:
                image = self.MergeFunc()
            else:
                image = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_CVT.copy())
            self.collection.append((image, self.collection_name.text()))
        elif flag == 3:  # Restore
            self.image_FLT = self.image_CVT.copy()
            image_filtering = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_CVT.copy())
            self.RenderPreviewIMG(image_filtering)
            self.hist.Plot(image_filtering)
            self.filterINDEX = 0  ###########
        elif flag == 4:
            if self.toolSelected == 1 and self.complete_selection:
                image = self.image_backup.copy()
            else:
                image = self.image.copy()
            self.collection.append((image, self.collection_name.text()))
        elif type(flag) == tuple:
            image = self.sliced_image[flag[0]][flag[1]].copy()
            self.collection.append((image, self.collection_name.text()))

    def HistEqualize(self, flag):
        self.CleanSelectedRegion()
        if not self.filtered:  # create filter backup image
            self.filtered = True
            self.image_FLT = self.image_CVT.copy()
        self.filterINDEX = flag
        image = CV.Histogram(self.image_FLT.copy(), self.ColCvt_combo.currentIndex(), self.filterINDEX)
        self.RenderPreviewIMG(image)
        self.hist.Plot(image)
        return image

    def zoomTool(self, zoom):
        if self.new:
            self.zoom_slider.setValue(100)
            return
        self.scrollArea.setWidgetResizable(False)
        self.CleanSelectedRegion()
        if zoom==1:
            self.zoom[0] = self.zoom_slider.value() / 100
        else:
            if zoom==2:
                if self.zoom[0]<5:
                    self.zoom[0] += 0.01
            elif zoom==3:
                if self.zoom[0]>0.01:
                    self.zoom[0] -= 0.01
            elif zoom==4:   # actual size
                self.zoom[0] = 1
            self.zoom_slider.setValue(int(self.zoom[0] * 100))
        self.zoom_percentage.setText("\t" + str(int(self.zoom[0] * 100)) + "%")
        self.zoom[1] = self.zoom[0]
        if zoom==5: # fitscreen
            self.scrollArea.setWidgetResizable(True)
            img_w, img_h = self.image.shape[1], self.image.shape[0]
            screen_w, screen_h = self.UI.canvas.size().width(), self.UI.canvas.size().height()
            if img_w>screen_w:
                self.zoom[0] = screen_w/img_w
            elif img_w<screen_w:
                self.zoom[0] = img_w/screen_w
            if img_h>screen_h:
                self.zoom[1] = screen_h/img_h
            elif img_h<screen_h:
                self.zoom[1] = img_h/screen_h
            self.zoom_slider.setValue(100)
            self.zoom_percentage.setText("\t" + str(100) + "%")
        self.Render(self.image)

    def moveImage(self, mousepos, image):
        new_coord = (mousepos[0]+self.init_coords[0], mousepos[1]+self.init_coords[1])
        self.toolCoords = [new_coord[0], new_coord[1], new_coord[0]+image.shape[1], new_coord[1]+image.shape[0]]
        CV.drawPrimitive(image, (0,0,image.shape[1]-1, image.shape[0]-1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
        if self.manual_selection:
            temp_image = self.image_backup2.copy()
        else:
            temp_image = self.image.copy()
        temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(temp_image)

    def Menubars(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')
        viewMenu = menu.addMenu('&View')
        helpMenu = menu.addMenu('&Help')
        self.UI.MenuDetail(fileMenu, '&New', 'New Page', lambda: self.resizeDialog(True), 'Ctrl+N', 'TP_assets/new.jpg')  # New
        self.UI.MenuDetail(fileMenu, '&Open', 'Open New Project', lambda: self.fileDialog(1), 'Ctrl+O', 'TP_assets/open.jpg')  # Open
        self.UI.MenuDetail(fileMenu, '&Save', 'Save Project', lambda: self.fileDialog(2), 'Ctrl+S', 'TP_assets/save.png')  # Save
        self.UI.MenuDetail(fileMenu, '&Exit', 'Quit Application', lambda: self.UI.QuitDialog(sys), 'Shift+Esc', 'TP_assets/exit.png')  # Exit
        screenMenu = viewMenu.addMenu('Screen')
        self.UI.MenuDetail(screenMenu, 'Actual Size', 'Zoom to 100%', lambda: self.zoomTool(4))
        self.UI.MenuDetail(screenMenu, 'Fit Screen', 'Zoom to fit screen', lambda: self.zoomTool(5))
        gridMenu = viewMenu.addMenu('Gridlines')
        self.grid_list = [self.UI.MenuDetail(gridMenu, 'None', 'default without gridline', lambda: self.grid_option(0), checked=True),
                          self.UI.MenuDetail(gridMenu, 'Standard', '3x3 grid', lambda: self.grid_option(1)),
                          self.UI.MenuDetail(gridMenu, 'Detailed', '10x10 pixels', lambda: self.grid_option(2))]
        self.filtration_show = self.UI.MenuDetail(viewMenu, 'Filtration', 'show / hide Filtration panel', lambda : self.ShowHide(3), checked=True)
        self.toolbar_show = self.UI.MenuDetail(viewMenu, 'Toolbar', 'show / hide toolbar', lambda : self.ShowHide(2), checked=True)
        self.status_show = self.UI.MenuDetail(viewMenu, 'Status bar', 'show / hide status bar', lambda : self.ShowHide(1), checked=True)
        self.UI.MenuDetail(helpMenu, 'About v_1', 'About the application', lambda : self.UI.about(1))
        self.UI.MenuDetail(helpMenu, 'About v_2', 'About the application', lambda: self.UI.about(2))

    def Toolbars(self):
        Rot_combo_str = ["Rotate","Rot_Right90"+u'\N{DEGREE SIGN}', "Rot_Left  90"+u'\N{DEGREE SIGN}', "Rotate 180"+u'\N{DEGREE SIGN}', "Flip Vertical", "Flip Horizontal"]
        Rot_combo_icon = ["TP_assets/rot.png", "TP_assets/rot_right.png", "TP_assets/rot_left.png", "TP_assets/rot_half.png", "TP_assets/flip_v.png", "TP_assets/flip_h.png"]
        font_combo_str = ["HersheyComplex", "Her_Complex(S)", "HersheyDuplex", "HersheyPlain", "HersheyScript(C)", "HersheyScript(S)", "HersheyTriplex", "Italic"]
        size_combo_str = ["1px", "2px", "3px", "4px", "5px", "6px", "7px", "8px", "9px", "10px"]
        size_combo_icon = ["TP_assets/1px.png", "TP_assets/2px.png", "TP_assets/3px.png", "TP_assets/4px.png", "TP_assets/5px.png", "TP_assets/6px.png", "TP_assets/7px.png", "TP_assets/8px.png", "TP_assets/9px.png", "TP_assets/10px.png"]
        ColCvt_combo_str = ["RGB image", "Grayscale image", "HSV image", "Hue channel", "Saturation channel", "Value channel", "HSL image", "Light channel", "CIE_L*A*B image", "LUV image", "YCrCb JPEG", "CIE_XYZ image"]
        ColCvt_combo_icon = ["TP_assets/rgb.png", "TP_assets/gray.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png"]
        self.fontSize = self.UI.SpinBox(False, 0.1, 100, 1, 55, height=30, action=self.FontStyle_Update)
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)
        self.SelectionTool = self.UI.ToolButton(self.toolbar, 'TP_assets/selection.png', 'Selection', lambda :self.ToolSelection(1))    #Selection
        self.UI.ToolDetail(self.toolbar, 'TP_assets/crop.jpg', 'Crop', self.CropTool),  # Crop
        self.UI.ToolDetail(self.toolbar, 'TP_assets/resize.png', 'Resize', self.resizeDialog) # Resize
        comboRot = self.UI.ComboBoxDetail(self.toolbar, True, Rot_combo_str, Rot_combo_icon, "Rotation", (115,30), lambda :self.ComboRotation(comboRot))
        self.toolbar.addSeparator()
        self.UI.ToolButton(self.toolbar, 'TP_assets/draw.png', 'Draw', lambda: self.ToolSelection(2))  # Draw
        self.UI.ToolButton(self.toolbar, 'TP_assets/eraser.png', 'Eraser', lambda: self.ToolSelection(9))  # Eraser
        self.UI.ToolButton(self.toolbar, 'TP_assets/dropper.png', 'Color Picker', lambda: self.ToolSelection(10))  # Dropper
        self.UI.ToolButton(self.toolbar, 'TP_assets/text.png', 'Text', lambda: self.ToolSelection(8))  # Text
        self.fontStyle = self.UI.ComboBoxDetail(self.toolbar, False, font_combo_str, None, "Font Style", (120,30), self.FontStyle_Update)
        self.toolbar.addWidget(self.fontSize)
        self.toolbar.addSeparator()
        self.UI.ToolButton(self.toolbar, 'TP_assets/line.png', 'Line', lambda: self.ToolSelection(3))    # Line
        self.UI.ToolButton(self.toolbar, 'TP_assets/circle.png', 'Circle', lambda: self.ToolSelection(4))  # Circle
        self.UI.ToolButton(self.toolbar, 'TP_assets/rect.png', 'Rectangle', lambda: self.ToolSelection(5))   # Rect
        self.UI.ToolButton(self.toolbar, 'TP_assets/triangle.png', 'Triangle', lambda: self.ToolSelection(6))  # Triangle
        self.UI.ToolButton(self.toolbar, 'TP_assets/diamond.png', 'Diamond', lambda: self.ToolSelection(7))  # Diamond
        self.option_btn = self.UI.ToolButton(self.toolbar, 'TP_assets/outline.png', "Outline", self.Outline_Fill, 1, (80,35))
        self.toolbar.addSeparator()
        self.comboSize = self.UI.ComboBoxDetail(self.toolbar, True, size_combo_str, size_combo_icon, "Thickness", (85,30), lambda :self.Outline_Fill(True), (38,30))
        self.colorBtn = self.UI.ToolButton(self.toolbar, 'TP_assets/color2.png', "Edit Color", lambda: self.colorDialog(1), 2)
        self.toolbar.addSeparator()
        self.ColCvt_combo = self.UI.ComboBoxDetail(self.toolbar, True, ColCvt_combo_str, ColCvt_combo_icon, "Color Conversion", (165,30), self.Color_Conversion)
        self.toolbar.addSeparator()
        self.UI.ToolDetail(self.toolbar, 'TP_assets/love.png', 'Save as collection', lambda : self.collectionDialog(4))
        self.UI.ToolDetail(self.toolbar, 'TP_assets/addlove.png', 'Insert from collection', lambda: self.viewAvailableImage(True))
        self.toolbar.setEnabled(False)

    def UpdateText(self):
        image = self.image_backup.copy()
        CV.drawText(image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
        self.Render(image)

    def FontStyle_Update(self):
        if not self.toolSelected==8:
            return
        self.font[0] = self.fontStyle.currentIndex()
        self.font[1] = self.fontSize.value()
        self.UpdateText()

    def ShowHide(self, flag):
        if flag==1: #status
            if self.status_show.isChecked():
                self.statusBar().show()
            else:
                self.statusBar().hide()
        elif flag==2:   #toolbar
            if self.toolbar_show.isChecked():
                self.toolbar.show()
            else:
                self.toolbar.hide()
        elif flag==3:   #Filtration
            if self.filtration_show.isChecked():
                self.dockProperties.show()
                self.dockPreview.show()
            else:
                self.dockProperties.hide()
                self.dockPreview.hide()

    def ComboRotation(self, comboRot):
        index = comboRot.currentIndex()
        if index == 0 or self.new:
            comboRot.setCurrentIndex(0)
            return
        comboRot.blockSignals(True)
        if self.selection:
            image = self.image_backup.copy()
            temp_image = self.image_backup2.copy()
            image2 = self.image_CVT_backup.copy()

            image2, _ = CV.RotateImage(image2, self.toolCoords, index)
            image, self.toolCoords = CV.RotateImage(image, self.toolCoords, index)
            self.image_backup = image.copy()           # renew n save latest image
            self.image_CVT_backup = image2.copy()      # renew n save latest image
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
            temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        else:
            self.image, self.toolCoords = CV.RotateImage(self.image.copy(), (0,0,self.image.shape[1], self.image.shape[0]), index)
            self.image_CVT, _ = CV.RotateImage(self.image_CVT.copy(), (0,0,self.image_CVT.shape[1], self.image_CVT.shape[0]), index)
            temp_image = self.image
        self.Render(temp_image)
        comboRot.setCurrentIndex(0)
        comboRot.blockSignals(False)

    def ToolSelection(self, slc):
        if self.new:
            return
        self.CleanSelectedRegion()
        self.toolSelected = slc
        if self.toolSelected==2 or self.toolSelected==3 or 8<=self.toolSelected<=10:
            self.Outline_Fill()

    def CleanSelectedRegion(self):
        if self.toolSelected == 1 and self.selection:
            self.selection = self.Move = self.complete_selection = self.manual_selection = False
            self.image = CV.OverlayImage(self.image_backup.copy(), self.image, self.toolCoords)
            image2 = self.image_CVT_backup.copy()
            self.image_CVT = CV.OverlayImage(image2, self.image_CVT, self.toolCoords)

    def Color_Conversion(self):
        if self.new:
            self.ColCvt_combo.setCurrentIndex(0)
            return
        self.CleanSelectedRegion()
        if self.filtered:
            ori_image = self.image_FLT.copy()
        else:
            ori_image = self.image_CVT.copy()
        self.image = CV.ConvertColor(self.ColCvt_combo.currentIndex(), ori_image)
        self.Render(self.image)
        self.RenderPreviewIMG(self.image)
        self.hist.Plot(self.image)

    def Outline_Fill(self, flag=None):
        if flag:
            self.thickness = self.comboSize.currentIndex()+1
        else:
            if self.thickness!=-1 and 4<=self.toolSelected<=7:
                self.option_btn.setText("Fill")
                self.option_btn.setIcon(QIcon('TP_assets/fill.png'))
                self.thickness = -1
            else:
                self.option_btn.setText("Outline")
                self.option_btn.setIcon(QIcon('TP_assets/outline.png'))
                self.thickness = self.comboSize.currentIndex()+1
        if self.point:
            self.UpdateText()

    def CropTool(self):
        if not self.selection:
            return
        self.selection = self.Move = self.complete_selection = self.manual_selection = False
        self.image = self.image_backup.copy()
        self.Render(self.image)
        self.image_CVT = self.image_CVT_backup.copy()

    def HV_input(self, hv):
        if self.Aspc_ratio:
            if hv=='h':
                self.v_input.setText(self.h_input.text())
            elif hv=='v':
                self.h_input.setText(self.v_input.text())

    def By_resize(self):
        if self.by_2.isChecked():
            self.resize_value[0], self.resize_value[1] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[2]))
            self.v_input.setText(str(self.resize_value[3]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)
        elif self.by_1.isChecked():
            self.resize_value[2], self.resize_value[3] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[0]))
            self.v_input.setText(str(self.resize_value[1]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)

    def AspectRatio(self):
        if self.Aspc_ratio:
            self.Aspc_ratio = False
        else:
            self.Aspc_ratio = True

    def CollectionSave(self, dlg, flag):
        dlg.close()
        self.ApplyRestore(flag)

    def collectionDialog(self, flag):
        dlg = QDialog(self)
        dlg.setFixedSize(300,50)
        dlg.setWindowTitle("Save Collection")
        layout = QHBoxLayout()
        self.collection_name = self.UI.LineEdit("Untitled collection", size=(150,25))
        layout.addWidget(self.UI.Label_TextOnly("Collection", font=('Georgia', 11)))
        layout.addWidget(self.collection_name)
        layout.addWidget(self.UI.PushBtnIcon("TP_assets/save.png", lambda : self.CollectionSave(dlg, flag)))
        dlg.setLayout(layout)
        dlg.exec_()

    def resizeOption(self, dlg, flag=None):
        dlg.close()
        w, h = int(self.h_input.text()), int(self.v_input.text())
        if w==0:
            w = 1
        if h==0:
            h = 1
        if flag:    # new page
            self.image = CV.ResizeImage(self.image, (w, h))
            self.colorDialog(2)
            return
        if self.selection:
            image = self.image_backup.copy()
            image2 = self.image_CVT_backup.copy()
        else:
            image = self.image.copy()
            image2 = self.image_CVT.copy()
        if self.by_1.isChecked():
            w, h = int(w / 100 * image.shape[1]), int(h / 100 * image.shape[0])
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        else:
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        self.image_backup = image
        self.image_CVT_backup = image2
        if not self.selection:
            self.image = image
            self.image_CVT = image2
        else:
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
            temp_image = self.image_backup2.copy()
            center = self.toolCoords[0]+(self.toolCoords[2]-self.toolCoords[0])//2, self.toolCoords[1]+(self.toolCoords[3]-self.toolCoords[1])//2
            self.toolCoords = [center[0]-w//2, center[1]-h//2, center[0]+w//2, center[1]+h//2]
            image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(image)
        self.Aspc_ratio = True

    def resizeDialog(self, flag=None):
        if flag:    # New Page
            self.image = np.zeros((500, 500, 3), np.uint8)
        if self.selection:
            image = self.image_backup.copy()
            self.resize_value[2], self.resize_value[3] = image.shape[1], image.shape[0]
        else:
            self.resize_value[2], self.resize_value[3] = self.image.shape[1], self.image.shape[0]
        dlg = QDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setFixedSize(300,250)
        main_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        if flag:
            dlg.setWindowTitle("Dimension")
            text1 = self.UI.Label_TextOnly("By pixels:", ('Times New Roman', 12))
            layout1.addWidget(text1)
            text = '500'
        else:
            dlg.setWindowTitle("Resize")
            text1 = self.UI.Label_TextOnly("By: ", ('Times New Roman', 12))
            layout1.addWidget(text1)
            layout1.addStretch(1)
            self.by_1 = QRadioButton(self)
            self.by_1.setText("Percentage")
            self.by_1.setFont(QFont('Times New Roman', 11))
            self.by_1.setChecked(True)
            layout1.addWidget(self.by_1)
            layout1.addStretch(1)
            self.by_2 = QRadioButton(self)
            self.by_2.setText("Pixel    ")
            self.by_2.setFont(QFont('Times New Roman', 11))
            self.by_2.toggled.connect(self.By_resize)
            layout1.addWidget(self.by_2)
            text = '100'
        h_label = QLabel(self)
        h_label.setPixmap(QPixmap("TP_assets/horizontal.png"))
        layout2.addWidget(h_label)
        layout2.addStretch(1)
        h_text = self.UI.Label_TextOnly("Horizontal :", ('Times New Roman', 11))
        layout2.addWidget(h_text)
        layout2.addStretch(1)
        self.h_input = self.UI.LineEdit(text, lambda :self.HV_input('h'), (60, 30), QIntValidator())
        layout2.addWidget(self.h_input)
        v_label = QLabel(self)
        v_label.setPixmap(QPixmap("TP_assets/vertical.png"))
        layout3.addWidget(v_label)
        layout3.addStretch(1)
        v_text = self.UI.Label_TextOnly("Vertical :", ('Times New Roman', 11))
        layout3.addWidget(v_text)
        layout3.addStretch(1)
        self.v_input = self.UI.LineEdit(text, lambda :self.HV_input('v'), (60, 30), QIntValidator())
        layout3.addWidget(self.v_input)
        ratio_check = QCheckBox(self)
        ratio_check.setChecked(True)
        ratio_check.setText("Maintain aspect ratio")
        ratio_check.stateChanged.connect(self.AspectRatio)
        option_btn = self.UI.PushBtnText("APPLY", lambda : self.resizeOption(dlg, flag))
        main_layout.addLayout(layout1)
        main_layout.addStretch(1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        main_layout.addStretch(1)
        main_layout.addWidget(ratio_check)
        main_layout.addWidget(option_btn)
        dlg.setLayout(main_layout)
        dlg.exec_()

    def newLAUNCH(self):
        self.selection = self.Move = self.complete_selection = self.manual_selection = False
        self.zoomTool(4)
        self.Render(self.image)
        for atr in self.grid_list:
            atr.setCheckable(True)

    def colorDialog(self, flag):
        dlg = QColorDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        col = QColorDialog.getColor()
        if col.isValid():
            if flag==1:     # edit color
                self.color = tuple(reversed(col.getRgb()[:3]))
                CV.Color_picker(self.color)
                self.colorBtn.setIcon(QIcon("TP_assets/color.png"))
                if self.point:
                    self.UpdateText()
            elif flag==2:   # open new page color
                if self.new:
                    self.new = False
                    self.toolbar.setEnabled(True)
                    self.dockPreview.setEnabled(True)
                    self.dockProperties.setEnabled(True)
                self.color_bg = tuple(reversed(col.getRgb()[:3]))
                self.image[:] = self.color_bg
                self.image_CVT = self.image
                self.newLAUNCH()
            elif flag==3:
                self.color_backdrop = tuple(reversed(col.getRgb()[:3]))
                self.ACTIONImageFROMlist(4)

    def fileDialog(self, flag):
        filter = "Images (*.png *.jpg)"
        if flag==1:     #open
            file, _ = QFileDialog.getOpenFileName(self, "File Directory", QDir.currentPath(), filter)
            if file == (""):
                return
            if self.new:
                self.new = False
                self.toolbar.setEnabled(True)
                self.dockPreview.setEnabled(True)
                self.dockProperties.setEnabled(True)
            self.color_bg = (255, 255, 255)
            self.image = CV.LoadImage(file)
            self.image_CVT = CV.LoadImage(file) # creating image backup for Conversion
            self.filtered = False
            self.hist.Plot(self.image)
            self.RenderPreviewIMG(self.image)
            self.collection.append((self.image, os.path.basename(file)))
            self.newLAUNCH()
        elif flag==3:
            file, _ = QFileDialog.getOpenFileName(self, "File Directory", QDir.currentPath(), filter)
            if file == (""):
                return
            self.collection.append((CV.LoadImage(file), os.path.basename(file)))
            self.AddImageTOlist(self.collection[-1])
            self.ImageSource.setCurrentRow(len(self.collection)-1)
            self.ACTIONImageFROMlist(1)
        elif flag==2:   #save
            file, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.currentPath(), "PNG(*.png);;JPEG(*.jpg *.jpeg)")
            if file == ("") or self.new:
                return
            status = CV.SaveImage(file, self.image)
            if status:
                self.UI.InfoDialog(file)

    def grid_option(self, value):
        if self.new:
            return
        for grid in self.grid_list:
            grid.setChecked(False)
        self.grid_list[value].setChecked(True)

        self.grid = value
        self.Render(self.image)

    def Grid(self, image):
        image = image.copy()
        if self.grid == 1:   # 3x3grid
            CV.drawPrimitive(image, (0, image.shape[0] // 3, image.shape[1], image.shape[0] // 3), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (0, image.shape[0] // 3 * 2, image.shape[1], image.shape[0] // 3 * 2), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3, 0, image.shape[1]//3, image.shape[0]), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3*2, 0, image.shape[1]//3*2, image.shape[0]), 3, (123, 123, 123), 1)
        elif self.grid == 2: # 10x10px
            for i in range(1, int(image.shape[1]/10)+1):
                CV.drawPrimitive(image, (10*i, 0, 10*i, image.shape[0]), 2, (150, 150, 150), 1)
            for i in range(1, int(image.shape[0]/10)+1):
                CV.drawPrimitive(image, (0, 10*i, image.shape[1], 10*i), 2, (150, 150, 150), 1)
        return image

    def RenderPreviewIMG(self, image):
        # image = CV.Histogram(self.image_CVT, 1)
        image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        self.UI.prevImg.setPixmap(QPixmap.scaled(QPixmap.fromImage(QtImg), 250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def Render(self, image):
        image = self.Grid(image)
        image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        # Display the image to the label;
        self.UI.canvas.setPixmap(QPixmap.scaled(QPixmap.fromImage(QtImg), int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1]), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.UI.canvas.resize(int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1]))
        self.pixel_dim.setText("Dimension : "+str(image.shape[1])+" x "+str(image.shape[0])+'px\t')

def main():
    app = QApplication(sys.argv)
    win = Paint()
    win.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()

