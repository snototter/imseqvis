import sys
sys.path.append('.')

from imseqvis.sequence_viewer import SequenceViewer
import numpy as np

from qtpy.QtWidgets import QApplication


class DummySequence(object):
    def __init__(self, num_images: int = 100):
        self.num_images = num_images
    
    def __len__(self):
        return self.num_images
    
    def __getitem__(self, index: int) -> np.array:
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        # Gradually change the blue color of the image
        step = index % 10
        if step > 5:
            step = 10 - step
        img[:, :, 2] = min(255, step * 51)
        return img


if __name__ == "__main__":
    sequence = DummySequence(100)
    app = QApplication(sys.argv)
    widget = SequenceViewer(sequence)
    widget.setWindowTitle("Demo Viewer")
    widget.show()
    sys.exit(app.exec_())
