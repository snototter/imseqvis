from pathlib import Path


def show(
        folder: Path,
        window_title: str = "Image Folder Viewer",
        **kwargs) -> int:
    """
    Runs the ImageSequenceViewer for the given folder.

    Args:
      folder: Path to the folder containing the images.
      window_title: The title of the application window.
      kwargs: Additional arguments passed to the SequenceViewer.
    
    Returns:
      The application's exit code.
    """
    from qtpy.QtWidgets import QApplication
    import sys
    from .sequence_viewer import SequenceViewer, ImageFolder
    seq = ImageFolder(folder)

    app = QApplication(sys.argv)
    viewer = SequenceViewer(image_sequence=seq, **kwargs)

    # Run the application
    viewer.setWindowTitle(window_title)
    viewer.show()
    
    return app.exec()
