"""
This demo shows how to instantiate the SequenceViewer, create an
application and use some of its signals.
"""
from imseqvis.sequence_viewer import SequenceViewer
import numpy as np
import sys

from qtpy.QtWidgets import QApplication


class DummySequence(object):
    """
    Simple demo sequence that gradually changes the color of the selected
    RGB channel.
    """
    def __init__(self, num_images: int = 100, channel: int = 2):
        self.num_images = num_images
        self.channel = channel
    
    def __len__(self) -> int:
        """Required. An image sequence must provide its length."""
        return self.num_images
    
    def __getitem__(self, index: int) -> np.array:
        """Required. An image sequence must provide random access."""
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        # Gradually change the color of the image
        step = index % 10
        if step > 5:
            step = 10 - step
        img[:, :, self.channel] = min(255, step * 51)
        return img

    def nextSequence(self):
        """Dummy implementation to navigate between different sequences."""
        return DummySequence(
            self.num_images,
            (self.channel + 1) % 3)
   
    def previousSequence(self):
        """Dummy implementation to navigate between different sequences."""
        return DummySequence(
            self.num_images,
            (self.channel - 1) % 3)


if __name__ == "__main__":
    SHOW_SEQUENCE_BUTTONS = True
    SHOW_ZOOM_BUTTONS = True
    PLAYBACK_TIMEOUT = 150
    LOG_EVERY_MOUSE_MOVE = False  # Very verbose!

    # The image data source
    sequence = DummySequence(142)

    # Simple demo GUI that shows how to use the SequenceViewer
    app = QApplication(sys.argv)
    viewer = SequenceViewer(
        image_sequence=sequence,
        playback_timeout=PLAYBACK_TIMEOUT,
        include_sequence_navigation_buttons=SHOW_SEQUENCE_BUTTONS,
        include_zoom_buttons=SHOW_ZOOM_BUTTONS)
    
    # Demo slots to show how to navigate between different sequences
    def onNextSequence():
        viewer.setSequence(viewer.image_sequence.nextSequence())
    def onPreviousSequence():
        viewer.setSequence(viewer.image_sequence.previousSequence())

    viewer.nextSequenceRequest.connect(onNextSequence)
    viewer.previousSequenceRequest.connect(onPreviousSequence)

    # Demo, how to use the other available signals:
    def onMouseClicked(pixel, button):
        print(f'Mouse clicked "{button}" at pixel {pixel.x()}, {pixel.y()}')
    viewer.mouseClickedLeft.connect(lambda px: onMouseClicked(px, 'left'))
    viewer.mouseClickedMiddle.connect(lambda px: onMouseClicked(px, 'middle'))
    viewer.mouseClickedRight.connect(lambda px: onMouseClicked(px, 'right'))
    
    if LOG_EVERY_MOUSE_MOVE:
        def onMouseMoved(pixel):
            print(f'Mouse moved to pixel position {pixel.x()}, {pixel.y()}')
        viewer.mouseMoved.connect(onMouseMoved)

    def onPathDropped(path):
        print(f'Path dropped onto canvas: {path}')
    viewer.pathDropped.connect(onPathDropped)
    
    # Run the application
    viewer.setWindowTitle("Demo Viewer")
    viewer.show()
    sys.exit(app.exec())
