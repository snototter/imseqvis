from imseqvis.sequence_viewer import SequenceViewer
import numpy as np
import sys
from pathlib import Path

try:
    from vito import imutils
except ImportError as e:
    print('\n************************************************\n')
    print('This example requires vito to load images.')
    print('Please install via:\n')
    print('    python -m pip install vito\n')
    print('************************************************\n')
    raise e

from qtpy.QtWidgets import QApplication


class ImageFolder(object):
    """
    Simple demo sequence that allows you to visualize all images within a
    local folder.
    """
    def __init__(self, folder: Path):
        assert folder.is_dir(), f'{folder} is not a directory'

        self.files = sorted(
            [f for f in folder.iterdir() if f.is_file()
             and f.suffix in ['.png', '.jpg', '.jpeg']])
        assert len(self.files) > 0, f'No images found in {folder}'
    
    def __len__(self) -> int:
        return len(self.files)
    
    def __getitem__(self, index: int) -> np.array:
        return imutils.imread(self.files[index])


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
    sys.exit(app.exec_())
