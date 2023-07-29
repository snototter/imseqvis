"""
This demo shows how to instantiate the SequenceViewer, create an
application and use some of its signals.

If you only want to show an image folder, a simpler way would be:
```python
import imseqvis
imseqvis.show("path/to/folder")
```
"""
from imseqvis.sequence_viewer import SequenceViewer, ImageFolder
import sys
from pathlib import Path
from qtpy.QtWidgets import QApplication


if __name__ == "__main__":
    FOLDER = Path(__file__).parent

    # The image data source
    sequence = ImageFolder(FOLDER)

    # Simple demo GUI that shows how to use the SequenceViewer
    app = QApplication(sys.argv)
    viewer = SequenceViewer(
        image_sequence=sequence,
        playback_timeout=500,
        include_sequence_navigation_buttons=False,
        include_zoom_buttons=True)

    # Demo, how to use the other available signals:
    def onMouseClicked(pixel, button):
        print(f'Mouse clicked "{button}" at pixel {pixel.x()}, {pixel.y()}')
    viewer.mouseClickedLeft.connect(lambda px: onMouseClicked(px, 'left'))
    viewer.mouseClickedMiddle.connect(lambda px: onMouseClicked(px, 'middle'))
    viewer.mouseClickedRight.connect(lambda px: onMouseClicked(px, 'right'))
   
    # Run the application
    viewer.setWindowTitle("Image Folder Viewer")
    viewer.show()
    sys.exit(app.exec())
