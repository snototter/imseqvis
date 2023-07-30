from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from qtpy.QtCore import Signal, Slot, QPointF
from pathlib import Path
import numpy as np
from vito import imutils
from natsort import natsorted
from typing import List

from .image_viewer import ImageViewer
from .control_widget import SequenceControlWidget


class ImageSequence(object):
    """
    Provides random access to a list of image files.
    """
    def __init__(self, files: List[Path]):
        """
        Creates the image sequence.

        Args:
          files: List of image files.
        """
        self.files = files
    
    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, index: int) -> np.array:
        return imutils.imread(self.files[index])


class ImageFolder(ImageSequence):
    """
    Provides a random access sequence of images from a local folder.
    """
    def __init__(
            self,
            folder: Path,
            image_extensions: List[str] = ['.png', '.jpg', '.jpeg']):
        """
        Creates the image sequence.

        Args:
          folder: Path to the folder containing the images.
          image_extensions: The file extensions to consider as images.
        """
        if not isinstance(folder, Path):
            folder = Path(folder)
        if not folder.is_dir():
            raise ValueError(f'Folder "{folder}" is not a directory!')

        files = natsorted(
            [f for f in folder.iterdir() if f.is_file()
             and f.suffix in image_extensions])
        super().__init__(files)


class SequenceViewer(QWidget):
    """
    A widget to display a sequence of images.

    The current image is displayed within a zoom- and scrollable area.
    The sequence can be navigated using playback controls and key
    bindings:
    * x/p: Toggle play/pause.
    * b/n: Jump to previous/next image.
    * v/m: Skip 10 images backward/forward.
    * 'r'/ESC: Reset the sequence (jump to first image).
    """
    # The user wants to advance to the previous sequence. Only available if
    # the sequence navigation buttons have been enabled.
    previousSequenceRequest = Signal()

    # The user wants to advance to the next sequence. Only available if
    # the sequence navigation buttons have been enabled.
    nextSequenceRequest = Signal()

    # A file or folder has been dropped onto the canvas.
    pathDropped = Signal(Path)

    # Mouse moved to this pixel position.
    mouseMoved = Signal(QPointF)

    # Left mouse button clicked at this pixel position.
    mouseClickedLeft = Signal(QPointF)

    # Middle mouse button (wheel) clicked at this pixel position.
    mouseClickedMiddle = Signal(QPointF)

    # Right mouse button clicked at this pixel position.
    mouseClickedRight = Signal(QPointF)

    def __init__(
            self,
            image_sequence,
            playback_timeout: int = 100,
            include_sequence_navigation_buttons: bool = False,
            include_zoom_buttons: bool = True):
        """
        Args:
          image_sequence: A random access sequence of images. Indexing must be
            0-based and return the image at the given index as a numpy array
            of dtype=np.uint8.
          playback_timeout: Timeout of the playback timer in milliseconds.
          include_sequence_navigation_buttons: If True, controls to skip to the
            previous or next sequence will be shown. If clicked, the
            corresponding `previousSequenceRequest` or `nextSequenceRequest`
            will be emitted.
          include_zoom_buttons: If True, buttons to zoom the image are shown.
        """
        super().__init__()
        self.image_sequence = [] if (image_sequence is None) else image_sequence
        self.initUI(
            playback_timeout,
            include_sequence_navigation_buttons,
            include_zoom_buttons)
        self.setSequence(self.image_sequence)

    def setSequence(self, image_sequence):
        self.image_sequence = image_sequence
        self.controls.setMaxValue(len(self.image_sequence))
        # Ensure that the first image is shown.
        self.onIndexChanged(1)

    def initUI(
            self,
            playback_timeout: int,
            include_sequence_navigation_buttons: bool,
            include_zoom_buttons: bool):
        # Image viewer can expand across the available space.
        self.viewer = ImageViewer()
        self.viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.viewer.pathDropped.connect(self.pathDropped)
        self.viewer.mouseMoved.connect(self.mouseMoved)
        self.viewer.mouseClickedLeft.connect(self.mouseClickedLeft)
        self.viewer.mouseClickedMiddle.connect(self.mouseClickedMiddle)
        self.viewer.mouseClickedRight.connect(self.mouseClickedRight)

        # The playback control widget.
        self.controls = SequenceControlWidget(
            max_value=len(self.image_sequence),
            playback_timeout=playback_timeout,
            playback_wait_for_viewer_ready=True,
            include_sequence_navigation_buttons=include_sequence_navigation_buttons,
            include_zoom_buttons=include_zoom_buttons)
        self.controls.indexChanged.connect(self.onIndexChanged)
        self.controls.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.controls.nextSequenceRequest.connect(self.nextSequenceRequest)
        self.controls.previousSequenceRequest.connect(self.previousSequenceRequest)
        self.controls.zoomFitToWindowRequest.connect(self.zoomFitToWindow)
        self.controls.zoomOriginalSizeRequest.connect(self.zoomOriginalSize)

        # Layouting.
        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(self.controls)
        self.setLayout(layout)

    @Slot()
    def zoomFitToWindow(self):
        """Scales the image such that it fits the available space."""
        self.viewer.scaleToFitWindow()
    
    @Slot()
    def zoomOriginalSize(self):
        """Displays the image in its original size."""
        self.viewer.setScale(1)

    @Slot()
    def zoomIn(self):
        """Zooms in by 1 step, identical to 1 click of the mouse wheel."""
        self.viewer.zoom(120)  # Mouse wheel deltas are 120 per step.

    @Slot()
    def zoomOut(self):
        """Zooms out by 1 step, identical to 1 click of the mouse wheel."""
        self.viewer.zoom(-120)

    @Slot()
    def focusOnManualInput(self):
        """Sets the focus to the manual input field."""
        self.controls.focusOnManualInput()
    
    @Slot()
    def togglePlayback(self):
        """Toggles the playback."""
        self.controls.togglePlayback()

    def keyPressEvent(self, event):
        # Forward key events to the control widget.
        self.controls.keyPressEvent(event)

    def onIndexChanged(self, index: int):
        # The control index is 1-based, but the sequence index is 0-based.
        index -= 1
        if index < 0 or index >= len(self.image_sequence):
            return
        img = self.image_sequence[index]
        self.viewer.showImage(img, reset_scale=False)
        self.controls.onViewerReady()
