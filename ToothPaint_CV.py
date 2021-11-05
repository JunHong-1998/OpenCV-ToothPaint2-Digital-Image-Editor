from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
import numpy as np
import cv2
import math

class Paint_CV:
    def __init__(self):
        pass

    def Filter(self, image, flag, Ksize=None, depth=None, colspace=None, contrast=None, sharpen=None, bitLevel=None, customFilter=None):
        if flag==3:     #Gaussian Blur
            image = cv2.GaussianBlur(image, (Ksize, Ksize), 0)
        elif flag==4:   #Median Blur
            image = cv2.medianBlur(image, Ksize)
        elif flag==5:   #Average Blur
            image = cv2.blur(image, (Ksize, Ksize))
        elif flag==6:   #Box Filter
            image = cv2.boxFilter(image, 0, (Ksize, Ksize))
        elif flag==7:   #Bilateral Filter
            image = cv2.bilateralFilter(image, depth, colspace, colspace)
        elif flag==8:
            image = cv2.addWeighted(image, contrast, np.zeros(image.shape, image.dtype), 0,0)
        elif flag==9:
            kernel = np.ones((Ksize, Ksize), np.float32) * (-1)
            kernel[math.floor(Ksize / 2), math.floor(Ksize / 2)] = sharpen
            image = cv2.filter2D(image, -1, kernel)
        elif flag==10:  #Emboss
            filter = np.array([[0,1,0],[0,0,0],[0,-1,0]])
            image = cv2.filter2D(image, -1, filter)
            image += 128
        elif flag==11:  #Sepia
            filter = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
            image = cv2.transform(image, filter)
        elif flag==12:  #Mexican
            filter = np.array([[0,0,-1,0,0],[0,-1,-2,-1,0],[-1,-2,16,-2,-1],[0,-1,-2,-1,0],[0,0,-1,0,0]])
            image = cv2.filter2D(image, -1, filter)
        elif flag==13:
            gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            r, c = gray_img.shape
            x = np.zeros((r, c, 8), dtype=np.uint8)
            x[:, :, bitLevel] = 2 ** bitLevel
            r = np.zeros((r, c, 8), dtype=np.uint8)
            r[:, :, bitLevel] = cv2.bitwise_and(gray_img, x[:, :, bitLevel])
            mask = r[:, :, bitLevel] > 0
            r[mask] = 255
            img = r[:, :, bitLevel]
            image = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif flag==14:
            filter = np.array(customFilter)
            image = cv2.filter2D(image, -1, filter)
        return image

    def Histogram(self, image, type, flag):
        if flag==1: #Equalize
            img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
            image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        elif flag==2:
            img_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            img_lab[:,:,0] = clahe.apply(img_lab[:,:,0])
            image = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)
        image = self.ConvertColor(type, image)
        return image

    def CropImage(self, image, coords):
        return image[min(coords[1], coords[3]):max(coords[1], coords[3])+1, min(coords[0], coords[2]):max(coords[0], coords[2])+1]

    def SaveImage(self, filename, image):
        return cv2.imwrite(filename, image)

    def LoadImage(self, filepath):
        return cv2.imread(filepath)

    def ResizeImage(self, image, dim):
        return cv2.resize(image, (dim[0], dim[1]))

    def ConvertColor(self, type, image):
        if type==0:
            return image
        elif type==1:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif type==2:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif type==3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,0]
        elif type==4:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,1]
        elif type==5:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,2]
        elif type==6:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        elif type==7:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)[:,:,1]
        elif type == 8:
            return cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        elif type == 9:
            return cv2.cvtColor(image, cv2.COLOR_RGB2LUV)
        elif type == 10:
            return cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        elif type == 11:
            return cv2.cvtColor(image, cv2.COLOR_RGB2XYZ)

    def OverlayImage(self, image, background, coords):
        top, bottom, left, right = coords[1], coords[1] + image.shape[0], coords[0], coords[0] + image.shape[1]
        if left>background.shape[1] or right<0 or top>background.shape[0] or bottom<0:
            return background
        if left<0:
            image = self.CropImage(image, (abs(left), 0, image.shape[1], image.shape[0]))
            left = 0
        if right>background.shape[1]:
            image = self.CropImage(image, (0, 0, image.shape[1]-(right-background.shape[1])-1, image.shape[0]))
            right = background.shape[1]
        if top<0:
            image = self.CropImage(image, (0, abs(top), image.shape[1], image.shape[0]))
            top = 0
        if bottom>background.shape[0]:
            image = self.CropImage(image, (0, 0, image.shape[1], image.shape[0]-(bottom-background.shape[0])-1))
            bottom = background.shape[0]
        background[top:bottom, left:right] = image
        return background

    def RotateImage(self, image, coords, index):
        if index < 4:
            ang = 0
            lst = []
            center = (coords[0] + image.shape[1] / 2, coords[1] + image.shape[0] / 2)
            if index == 1:
                ang = -90, 3
            elif index == 2:
                ang = 90, 1
            elif index == 3:
                ang = 180, 2
            M = cv2.getRotationMatrix2D(center, ang[0], 1)
            coordes = np.array([[coords[0], coords[1], 1], [coords[0] + image.shape[1], coords[1], 1], [coords[0] + image.shape[1], coords[1] + image.shape[0], 1], [coords[0], coords[1] + image.shape[0], 1]])
            for coord in coordes:
                lst.append(np.array(np.round(M.dot(coord), 0)).astype(int).tolist())
            coords = (min(lst)[0], min(lst)[1], max(lst)[0],max(lst)[1])
            image = np.rot90(image, ang[1]).copy()
        else:
            if index == 4:
                image = cv2.flip(image, 0)  # flip vertical
            elif index == 5:
                image = cv2.flip(image, 1)  # flip horizontal
        return image, coords

    def drawPrimitive(self, image, coords, type, color=(255,255,255), thick=None):      # dotted square, line, filled-square, square,
        if type == 1:
            color = (150,150,150)
            width = 5
            thick = 1
            LR, UD, dst = self.calcRegion(coords)
            if sum(dst) == 0:
                return
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2] + width * 2 * LR * i * -1, coords[3]), (coords[2] + width * 2 * LR * i * -1 + width * LR * -1, coords[3]), color, thick, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2], coords[3] + width * 2 * UD * i * -1), (coords[2], coords[3] + width * 2 * UD * i * -1 + width * UD * -1), color, thick, cv2.LINE_AA)
        elif type==2:
            color = (150, 150, 150)
            width = 2
            LR, UD, dst = self.calcRegion(coords)
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, 1, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, 1, cv2.LINE_AA)
        elif type == 3:
            cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 5:
            cv2.rectangle(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 4:
            center, radius = self.recalc_Center_Radius(coords)
            cv2.circle(image, center, max(radius), color, thick, cv2.LINE_AA)
        elif type == 6:
            cv2.polylines(image, [self.Triangle(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 8:
            cv2.fillPoly(image, [self.Triangle(coords)], color)
        elif type == 7:
            cv2.polylines(image, [self.Diamond(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 9:
            cv2.fillPoly(image, [self.Diamond(coords)], color)


    def drawText(self, image, text, coords, fontstyle, scale, color, thick):
        font = None
        if fontstyle == 0:
            font = cv2.FONT_HERSHEY_COMPLEX
        elif fontstyle == 1:
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        elif fontstyle == 2:
            font = cv2.FONT_HERSHEY_DUPLEX
        elif fontstyle == 3:
            font = cv2.FONT_HERSHEY_PLAIN
        elif fontstyle == 4:
            font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        elif fontstyle == 5:
            font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        elif fontstyle == 6:
            font = cv2.FONT_HERSHEY_TRIPLEX
        elif fontstyle == 7:
            font = cv2.FONT_ITALIC
        cv2.putText(image, text, coords, font, scale, color, thick)

    def recalc_Center_Radius(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        radius = [dst[0]//2, dst[1]//2]
        center = (int(coords[0]+radius[0]*LR), int(coords[1]+radius[1]*UD))
        return center, radius

    def Triangle(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        c = [center[0], center[1]-radius[1]]
        b = [center[0] +radius[0], center[1]+radius[1]]
        a = [center[0] -radius[0], center[1]+radius[1]]
        return np.array([a,b,c], np.int32)

    def Diamond(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        return np.array([[center[0]-radius[0], center[1]], [center[0], center[1]-radius[1]], [center[0]+radius[0], center[1]], [center[0], center[1]+radius[1]]], np.int32)


    def ReLocateCoords(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        if LR==-1:
            coords[0] -= dst[0]
            coords[2] += dst[0]
        if UD == -1:
            coords[1] -= dst[1]
            coords[3] += dst[1]
        return coords


    def calcRegion(self, coords):
        LR = UD = 0
        dst = [0, 0]
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]
        if x2 < x1:
            LR = -1
            dst[0] = x1 - x2
        elif x2 > x1:
            LR = 1
            dst[0] = x2 - x1
        if y2 < y1:
            UD = -1
            dst[1] = y1 - y2
        elif y2 > y1:
            UD = 1
            dst[1] = y2 - y1
        return LR, UD, dst

    def Color_picker(self, color):
        image = np.zeros((300, 300, 3), np.uint8)
        image[:] = color
        self.drawPrimitive(image, (int(300*.01), int(300*.01), int(300*.99), int(300*.99)), 5, (0,0,0), 10)
        self.drawPrimitive(image, (int(300*.1), int(300*.1), int(300*.9), int(300*.9)), 5, (255,255,255), 20)
        self.SaveImage("TP_assets/color.png", image)

class HistogramPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas()
        self.layout().addWidget(self.canvas)

    def Plot(self, image):
        self.canvas.plot(image)

class PlotCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize=(4, 4), dpi=72)
        FigureCanvas.__init__(self, fig)
        self.axes = fig.add_subplot(111)
        self.axes.axis('off')
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, image):
        self.axes.clear()
        self.axes.hist(image.ravel(), 256, [0, 256], color='black')
        if len(image.shape)==3:
            color = ('b', 'g', 'r')
            for i, col in enumerate(color):
                histr = cv2.calcHist([image], [i], None, [256], [0, 256])
                self.axes.plot(histr, color=col)
        self.axes.set_ylim(ymin=0)
        self.axes.set_xlim(xmin=0, xmax=256)
        self.axes.set_position([0, 0, 1, 1])
        self.draw()