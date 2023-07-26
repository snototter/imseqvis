from qtpy.QtWidgets import QWidget, QVBoxLayout

from .image_viewer import ImageViewer
from .control_widget import SequenceControlWidget

class SequenceViewer(QWidget):
    """
    TODO doc
    """
    
    def __init__(
            self,
            image_sequence):
        """
        Args:
          image_sequence: A random access sequence of images. Indexing must be
            0-based and return the image at the given index as a numpy array
            of dtype=np.uint8.
        """
        super().__init__()
        self.image_sequence = image_sequence
        self.initUI()
        # Ensure that the first image is shown
        self.onIndexChanged(1)
    
    def initUI(self):
        self.viewer = ImageViewer()

        self.controls = SequenceControlWidget(
            max_value=len(self.image_sequence),
            playback_wait_for_viewer_ready=True)
        self.controls.indexChanged.connect(self.onIndexChanged)

        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addWidget(self.controls)
        self.setLayout(layout)

    def onIndexChanged(self, index: int):
        # The control index is 1-based, but the sequence index is 0-based.
        img = self.image_sequence[index - 1]
        self.viewer.showImage(img)
        self.controls.onViewerReady()
        
