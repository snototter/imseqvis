import numpy as np
import qimage2ndarray
from pathlib import Path

from qtpy.QtWidgets import QWidget, QScrollArea, QApplication
from qtpy.QtCore import Qt, QPoint, QPointF, Signal, Slot, QRect, QMimeData
from qtpy.QtGui import (
    QPixmap, QImage, QFont, QPainter, QPen, QColor, QBrush, QPalette)


def pixmapFromNumpy(img_np: np.array) -> QPixmap:
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
    Simple widget to display an image as a QLabel, always resized to the
    widget's dimensions.
    
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


def isMimeDataLocalPath(mime_data: QMimeData) -> bool:
    """
    Returns True if the given mime_data belongs to a file which can
    be dropped onto the ImageViewer/Canvas, i.e. it must be either a file
    or a URI of a local file.
    """
    if mime_data.hasUrls():
        is_local_file = [Path(url.toLocalFile()).exists() for url in mime_data.urls()]
        if any(is_local_file):
            return True
    if mime_data.hasText():
        return mime_data.text().startswith('file://')
    return False


def getLocalPathFromMimeData(mime_data: QMimeData) -> Path:
    """
    Returns the path of a file or folder dropped onto the canvas.
    """
    if mime_data.hasUrls():
        # Return the first locally existing file
        for url in mime_data.urls():
            fpath = Path(url.toLocalFile())
            if fpath.exists():
                return fpath
    if mime_data.hasText():
        txt = mime_data.text()
        if txt.startswith('file://'):
            return Path(txt[7:].strip())
    raise ValueError('Unsupported QMimeData for dropped file!')


class ImageCanvas(QWidget):
    """Widget to display a zoomable/scrollable image."""

    # User wants to zoom in/out by a given amount (mouse wheel delta).
    zoomRequest = Signal(int)

    # User wants to scroll (Qt.Horizontal or Qt.Vertical, mouse wheel delta).
    scrollRequest = Signal(int, int)
    
    # Mouse moved to this pixel position
    mouseMoved = Signal(QPointF)

    # Left mouse button clicked at this pixel position.
    mouseClickedLeft = Signal(QPointF)

    # Middle mouse button (wheel) clicked at this pixel position.
    mouseClickedMiddle = Signal(QPointF)

    # Right mouse button clicked at this pixel position.
    mouseClickedRight = Signal(QPointF)
        
    # Scaling factor of displayed image changed
    imageScaleChanged = Signal(float)
    
    # File or folder has been dropped onto canvas
    pathDropped = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale = 1.0
        self._pixmap = QPixmap()
        self._painter = QPainter()
        self._is_dragging = False
        self._prev_drag_pos = None  # Parent widget position, i.e. usually the position within the ImageViewer (scroll area)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

    def setScale(self, scale):
        prev_scale = self._scale
        self._scale = scale
        self.adjustSize()
        self.update()
        if prev_scale != self._scale:
            self.imageScaleChanged.emit(self._scale)

    def loadPixmap(self, pixmap):
        self._pixmap = pixmap
        self.repaint()

    def pixmap(self):
        return self._pixmap

    def mouseMoveEvent(self, event):
        pos = self.transformPos(event.pos())
        if Qt.RightButton & event.buttons():
            # Skip mouse move signals while panning the image
            self._is_dragging = True
            self.drag(event.pos())
        else:
            self.mouseMoved.emit(pos)

    def drag(self, new_pos):
        new_pos = self.mapToParent(new_pos)
        # Previous position will always be set when the mouse is pressed
        delta_pos = new_pos - self._prev_drag_pos
        dx = int(delta_pos.x())
        dy = int(delta_pos.y())
        if self.parent() is not None:
            pr = self.parent().rect()
            new_pos.setX(max(pr.left(), min(pr.right(), new_pos.x())))
            new_pos.setY(max(pr.top(), min(pr.bottom(), new_pos.y())))
        self._prev_drag_pos = new_pos
        # The magic scale factor ensures that dragging is a bit more subtle
        # than scrolling with the mouse wheel. On my gnome-based system, a
        # factor of 6 means that the dragged image follows exactly the
        # mouse pointer...
        dx and self.scrollRequest.emit(dx * 6, Qt.Horizontal)
        dy and self.scrollRequest.emit(dy * 6, Qt.Vertical)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Viewer can be panned via the right button
            self._prev_drag_pos = self.mapToParent(event.pos())
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if not self._is_dragging:
            pos = self.transformPos(event.pos())
            if event.button() == Qt.LeftButton:
                self.mouseClickedLeft.emit(pos)
            elif event.button() == Qt.MiddleButton:
                self.mouseClickedMiddle.emit(pos)
            elif event.button() == Qt.RightButton:
                self.mouseClickedRight.emit(pos)
        if event.button() == Qt.LeftButton:
            QApplication.restoreOverrideCursor()
        self._is_dragging = False

    def dragEnterEvent(self, event):
        if isMimeDataLocalPath(event.mimeData()):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if isMimeDataLocalPath(event.mimeData()):
            fpath = getLocalPathFromMimeData(event.mimeData())
            self.pathDropped.emit(fpath)

    def paintEvent(self, event):
        if not self._pixmap:
            return super(ImageCanvas, self).paintEvent(event)
        qp = self._painter
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setRenderHint(QPainter.HighQualityAntialiasing)
        # qp.setRenderHint(QPainter.SmoothPixmapTransform)
        qp.fillRect(self.rect(), QBrush(self.palette().color(QPalette.Background)))
        qp.scale(self._scale, self._scale)
        # Adapted fast drawing from:
        # https://www.qt.io/blog/2006/05/13/fast-transformed-pixmapimage-drawing
        # If the painter has an invertible world transformation matrix, we use
        # it to get the visible rectangle (saves a lot of drawing resources).
        inv_wt, valid = qp.worldTransform().inverted()
        if valid:
            qp.translate(self.offsetToCenter())
            exposed_rect = inv_wt.mapRect(event.rect()).adjusted(-1, -1, 1, 1)
            qp.drawPixmap(exposed_rect, self._pixmap, exposed_rect)
        else:
            qp.translate(self.offsetToCenter())
            qp.drawPixmap(0, 0, self._pixmap)
            exposed_rect = QRect(0, 0, self._pixmap.width(), self._pixmap.height())
        qp.end()

    def transformPos(self, point):
        """Convert from widget coordinates to painter coordinates."""
        return QPointF(point.x()/self._scale, point.y()/self._scale) - self.offsetToCenter()

    def pixelAtWidgetPos(self, widget_pos):
        """Returns the pixel position at the given widget coordinate."""
        return self.transformPos(widget_pos)

    def pixelToWidgetPos(self, pixel_pos):
        """Compute the widget position of the given pixel position."""
        return (pixel_pos + self.offsetToCenter()) * self._scale

    def offsetToCenter(self):
        area = super(ImageCanvas, self).size()
        aw, ah = area.width(), area.height()
        w = self._pixmap.width() * self._scale
        h = self._pixmap.height() * self._scale
        x = (aw - w) / (2 * self._scale) if aw > w else 0
        y = (ah - h) / (2 * self._scale) if ah > h else 0
        return QPointF(x, y)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self._pixmap:
            return self._scale * self._pixmap.size()
        return super(ImageCanvas, self).minimumSizeHint()

    def wheelEvent(self, event):
        delta = event.angleDelta()
        dx, dy = delta.x(), delta.y()
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier:
            if modifiers & Qt.ShiftModifier:
                dy *= 10
            if dy:
                self.zoomRequest.emit(dy)
        else:
            if modifiers & Qt.ShiftModifier:
                dx *= 10
                dy *= 10
            dx and self.scrollRequest.emit(dx, Qt.Horizontal)
            dy and self.scrollRequest.emit(dy, Qt.Vertical)
        event.accept()
    

class ImageViewer(QScrollArea):
    """
    A zoom- and scrollable widget to display image data.

    This class has been adapted (stripped down functionality & simplified) from
    the iminspect project:
    https://github.com/snototter/iminspect
    """
    
    # Mouse moved to this pixel position
    mouseMoved = Signal(QPointF)

    # Left mouse button clicked at this pixel position.
    mouseClickedLeft = Signal(QPointF)

    # Middle mouse button (wheel) clicked at this pixel position.
    mouseClickedMiddle = Signal(QPointF)

    # Right mouse button clicked at this pixel position.
    mouseClickedRight = Signal(QPointF)
    
    # Scaling factor of displayed image changed
    imageScaleChanged = Signal(float)
    
    # The view changed due to the user scrolling or zooming
    viewChanged = Signal()
    
    # A file or folder has been dropped onto the canvas
    pathDropped = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._img_np = None
        self._img_scale = 1.0
        self._min_img_scale = None
        self._canvas = None
        self._prepareLayout()

    def imageNumpy(self) -> np.array:
        """Returns the shown image as numpy ndarray."""
        return self._img_np

    def imagePixmap(self) -> QPixmap:
        """Returns the shown image as QPixmap."""
        return self._canvas.pixmap()

    def pixelFromGlobal(self, global_pos):
        """
        Maps a global position, e.g. QCursor.pos(), to the corresponding
        pixel location.
        """
        return self._canvas.pixelAtWidgetPos(self._canvas.mapFromGlobal(global_pos))

    def _prepareLayout(self):
        self._canvas = ImageCanvas(self)
        self._canvas.zoomRequest.connect(self.zoom)
        self._canvas.scrollRequest.connect(self.scrollRelative)
        self._canvas.mouseMoved.connect(self.mouseMoved)
        self._canvas.mouseClickedLeft.connect(self.mouseClickedLeft)
        self._canvas.mouseClickedMiddle.connect(self.mouseClickedMiddle)
        self._canvas.mouseClickedRight.connect(self.mouseClickedRight)
        self._canvas.imageScaleChanged.connect(self.imageScaleChanged)
        self._canvas.imageScaleChanged.connect(lambda _scale: self.viewChanged.emit())
        self._canvas.pathDropped.connect(self.pathDropped)

        self.setWidget(self._canvas)
        self.setWidgetResizable(True)
        self._scoll_bars = {
            Qt.Vertical: self.verticalScrollBar(),
            Qt.Horizontal: self.horizontalScrollBar()
        }
        # Observe the valueChanged signal so we know whether the user dragged
        # a scroll bar or used the keyboard (e.g. arrow keys) to adjust the
        # bar's position.
        self.verticalScrollBar().valueChanged.connect(
            lambda new_value: self.scrollAbsolute(new_value, Qt.Vertical))
        self.horizontalScrollBar().valueChanged.connect(
            lambda new_value: self.scrollAbsolute(new_value, Qt.Horizontal))

    def currentImageScale(self):
        """Returns the currently applied image scale factor."""
        return self._img_scale

    @Slot(int)
    def zoom(self, delta: int):
        """Scale the displayed image. Zoom in if delta > 0.
        Usually to be called with mouse wheel delta values, thus
        the actual zoom steps are computed as delta/120.
        """
        self._img_scale += 0.05 * delta / 120
        self.paintCanvas()

    @Slot(int, int)
    def scrollRelative(self, delta, orientation):
        """Slot for scrollRequest signal of image canvas."""
        steps = -delta / 120
        bar = self._scoll_bars[orientation]
        value = bar.value() + bar.singleStep() * steps
        self.scrollAbsolute(value, orientation)

    @Slot(int, int)
    def scrollAbsolute(self, value, orientation):
        """Sets the scrollbar to the given value."""
        bar = self._scoll_bars[orientation]
        if value < bar.minimum():
            value = bar.minimum()
        if value > bar.maximum():
            value = bar.maximum()
        bar.setValue(value)
        self.viewChanged.emit()

    def showImage(self, img: np.array, reset_scale: bool = True) -> None:
        """
        Displays the given image.
        
        Args:
          img: The image to be displayed.
          reset_scale: If True, the zoom setting of the viewer will be reset.
        """
        pixmap = pixmapFromNumpy(img)
        self._img_np = img.copy()
        self._canvas.loadPixmap(pixmap)

        # Ensure that image has a minimum size of about 32x32 px (unless it is
        # actually smaller)
        self._min_img_scale = min(1.0, 32.0/img.shape[0], 32.0/img.shape[1])

        if reset_scale:
            self._img_scale = 1.0
        self.paintCanvas()

    def scaleToFitWindow(self) -> None:
        """Scale the image such that it fills the canvas area."""
        if self._img_np is None:
            return
        eps = 2.0  # Prevent scrollbars
        w1 = self.width() - eps
        h1 = self.height() - eps
        a1 = w1 / h1
        w2 = float(self._canvas.pixmap().width())
        h2 = float(self._canvas.pixmap().height())
        a2 = w2 / h2
        self._img_scale = w1 / w2 if a2 >= a1 else h1 / h2
        self.paintCanvas()

    def setScale(self, scale: float) -> None:
        self._img_scale = scale
        self.paintCanvas()

    def scale(self) -> float:
        return self._img_scale

    def paintCanvas(self) -> None:
        if self._img_np is None:
            return
        self._img_scale = max(self._min_img_scale, self._img_scale)
        self._canvas.setScale(self._img_scale)
        self._canvas.adjustSize()
        self._canvas.update()
