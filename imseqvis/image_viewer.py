from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLineEdit, QLabel, QToolButton
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap, QImage, QFont, QFontMetrics, QIcon, QPainter, QPen, QColor


import numpy as np
import qimage2ndarray
#from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLineEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

def pixmapFromNumPy(img_np: np.array) -> QPixmap:
    """
    Converts the given NumPy array image into a QPixmap.
    
    Args:
      img_np: The (1, 3, or 4-channel) image. This parameter must not be None.
    """
    if (img_np.ndim < 3) or img_np.shape[2] in [1, 3, 4]:
        qimage = qimage2ndarray.array2qimage(img_np.copy())
    else:
        img_width = max(400, min(img_np.shape[1], 1200))
        img_height = max(200, min(img_np.shape[0], 1200))
        qimage = QImage(img_width, img_height, QImage.Format_RGB888)
        qimage.fill(Qt.white)
        qp = QPainter()
        qp.begin(qimage)
        qp.setRenderHint(QPainter.HighQualityAntialiasing)
        qp.setPen(QPen(QColor(200, 0, 0)))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setFamily('Helvetica')
        qp.setFont(font)
        qp.drawText(qimage.rect(), Qt.AlignCenter, "Error!\nCannot display a\n{:d}-channel image.".format(img_np.shape[2]))
        qp.end()
    if qimage.isNull():
        raise ValueError('Invalid NumPy image received, cannot convert it to QImage')
    return QPixmap.fromImage(qimage)


# TODO ImageViewer class similar to iminspect (w/stripped down functionality)
class ImageViewer(QWidget):
    """
    TODO doc
    """
    
    def __init__(
            self):
        """
        Args:
          TODO
        """
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.label = QLabel('')
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """Custom event filter for keyboard inputs."""
        if event.key() in [Qt.Key_P, Qt.Key_Return, Qt.Key_Enter]:
            print('TODO P, return or enter pressed in ImageViewer')


    def showImage(self, img_np: np.array):
        self.label.setPixmap(pixmapFromNumPy(img_np))
