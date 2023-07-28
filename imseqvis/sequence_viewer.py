from PyQt5 import QtGui
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from qtpy.QtCore import Signal

from .image_viewer import ImageViewer
from .control_widget import SequenceControlWidget


class SequenceViewer(QWidget):
    """
    TODO doc
    """
    # Signaled whenever the user requests the previous sequence (if
    # these buttons are enabled).
    previousSequenceRequested = Signal()

    # Signaled whenever the user requests the next sequence (if
    # these buttons are enabled).
    nextSequenceRequested = Signal()

    def __init__(
            self,
            image_sequence,
            playback_timeout: int = 100,
            include_sequence_buttons: bool = False):
        """
        Args:
          image_sequence: A random access sequence of images. Indexing must be
            0-based and return the image at the given index as a numpy array
            of dtype=np.uint8.
          playback_timeout: Timeout of the playback timer in milliseconds.
          include_sequence_buttons: If True, controls to skip to the previous
            or next sequence will be shown. If clicked, the corresponding
            `previousSequenceRequested` or `nextSequenceRequested` signal will
            be emitted.
        """
        super().__init__()
        self.image_sequence = image_sequence
        self.initUI(playback_timeout, include_sequence_buttons)
        self.setSequence(image_sequence)
    
    def setSequence(self, image_sequence):
        self.image_sequence = image_sequence
        self.controls.setMaxValue(len(self.image_sequence))
        # Ensure that the first image is shown
        self.onIndexChanged(1)
        # self.viewer.scaleToFitWindow()
    
    def initUI(
            self,
            playback_timeout: int, 
            include_sequence_buttons: bool):
        self.viewer = ImageViewer()
        self.viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.controls = SequenceControlWidget(
            max_value=len(self.image_sequence),
            playback_timeout=playback_timeout,
            playback_wait_for_viewer_ready=True,
            include_sequence_buttons=include_sequence_buttons)
        self.controls.indexChanged.connect(self.onIndexChanged)
        self.controls.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.controls.nextSequenceRequested.connect(self.nextSequenceRequested)
        self.controls.previousSequenceRequested.connect(self.previousSequenceRequested)

        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(self.controls)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        # Forward key events to the control widget
        self.controls.keyPressEvent(event)

    def onIndexChanged(self, index: int):
        # The control index is 1-based, but the sequence index is 0-based.
        img = self.image_sequence[index - 1]
        self.viewer.showImage(img)
        # self.viewer.showImage(img, reset_scale=False)
        self.controls.onViewerReady()
        
