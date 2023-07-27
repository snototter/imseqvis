import numpy as np
import qimage2ndarray

from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLineEdit, QLabel, QToolButton
from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import QPixmap, QImage, QFont, QFontMetrics, QIcon, QPainter, QPen, QColor


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


class ImageLabel(QWidget):
    """
    Widget to display an image, always resized to the widgets dimensions.
    
    This class has been taken as is from the iminspect project:
    https://github.com/snototter/iminspect/
    """
    def __init__(self, pixmap=None, parent=None):
        super(ImageLabel, self).__init__(parent)
        self._pixmap = pixmap

    def pixmap(self):
        return self._pixmap

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        super(ImageLabel, self).paintEvent(event)
        if self._pixmap is None:
            return
        painter = QPainter(self)
        pm_size = self._pixmap.size()
        pm_size.scale(event.rect().size(), Qt.KeepAspectRatio)
        # Draw resized pixmap using nearest neighbor interpolation instead
        # of bilinear/smooth interpolation (omit the Qt.SmoothTransformation
        # parameter).
        scaled = self._pixmap.scaled(
                pm_size, Qt.KeepAspectRatio)
        pos = QPoint(
            (event.rect().width() - scaled.width()) // 2,
            (event.rect().height() - scaled.height()) // 2)
        painter.drawPixmap(pos, scaled)


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
        self.label = ImageLabel()
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """Custom event filter for keyboard inputs."""
        if event.key() in [Qt.Key_P, Qt.Key_Return, Qt.Key_Enter]:
            print('TODO P, return or enter pressed in ImageViewer')


    def showImage(self, img_np: np.array):
        self.label.setPixmap(pixmapFromNumPy(img_np))
