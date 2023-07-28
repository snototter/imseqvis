import sys
sys.path.append('.')

from imseqvis.sequence_viewer import SequenceViewer
import numpy as np

from qtpy.QtWidgets import QApplication


class DummySequence(object):
    def __init__(self, num_images: int = 100, channel: int = 2):
        self.num_images = num_images
        self.channel = channel
    
    def __len__(self):
        return self.num_images
        
    
    def __getitem__(self, index: int) -> np.array:
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        # Gradually change the color of the image
        step = index % 10
        if step > 5:
            step = 10 - step
        img[:, :, self.channel] = min(255, step * 51)
        return img

    def nextSequence(self):
        return DummySequence(
            self.num_images,
            (self.channel + 1) % 3)
   
    def previousSequence(self):
        return DummySequence(
            self.num_images,
            (self.channel - 1) % 3)


if __name__ == "__main__":
    SHOW_SEQUENCE_BUTTONS = True
    PLAYBACK_TIMEOUT = 150

    sequence = DummySequence(142)

    app = QApplication(sys.argv)
    viewer = SequenceViewer(
        image_sequence=sequence,
        playback_timeout=PLAYBACK_TIMEOUT,
        include_sequence_buttons=SHOW_SEQUENCE_BUTTONS)
    viewer.setWindowTitle("Demo Viewer")
    viewer.show()
    
    def onNextSequence():
        viewer.setSequence(viewer.image_sequence.nextSequence())
    def onPreviousSequence():
        viewer.setSequence(viewer.image_sequence.previousSequence())
        
    viewer.nextSequenceRequested.connect(onNextSequence)
    viewer.previousSequenceRequested.connect(onPreviousSequence)
    
    sys.exit(app.exec_())

