from pathlib import Path
from typing import Union


def show_sequence(
        image_sequence,
        window_title: str = "Image Sequence Viewer",
        **kwargs) -> int:
    """
    Runs the ImageSequenceViewer for the given image sequence.
    
    Args:
      image_sequence: Any object that provides random access to
        the image sequence. Must implement `__len__` and `__getitem__`,
        where the latter returns the image at the given index as numpy array.
      window_title: The title of the application window.
      kwargs: Additional arguments passed to the SequenceViewer.

    Returns:
      The application's exit code.
    """
    from qtpy.QtWidgets import QApplication, QShortcut
    from qtpy.QtGui import QKeySequence
    import sys
    from .sequence_viewer import SequenceViewer

    app = QApplication(sys.argv)
    viewer = SequenceViewer(image_sequence=image_sequence, **kwargs)

    # Add keyboard shortcuts for zooming.
    shortcut_zoom_fit = QShortcut(QKeySequence('Ctrl+F'), viewer)
    shortcut_zoom_fit.activated.connect(viewer.zoomFitToWindow)

    shortcut_zoom_original = QShortcut(QKeySequence('Ctrl+1'), viewer)
    shortcut_zoom_original.activated.connect(viewer.zoomOriginalSize)

    shortcut_zoom_in = QShortcut(QKeySequence('Ctrl++'), viewer)
    shortcut_zoom_in.activated.connect(viewer.zoomIn)

    shortcut_zoom_in = QShortcut(QKeySequence('Ctrl+-'), viewer)
    shortcut_zoom_in.activated.connect(viewer.zoomOut)

    # Add keyboard shortcut to focus onto the "jump to" input field.
    shortcut_jump = QShortcut(QKeySequence('Ctrl+J'), viewer)
    shortcut_jump.activated.connect(viewer.focusOnManualInput)

    # Run the application.
    viewer.setWindowTitle(window_title)
    viewer.show()
    viewer.resize(
        QApplication.desktop().availableGeometry(viewer).size() * 0.7)
    return app.exec()


def show_folder(
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
    from .sequence_viewer import ImageFolder
    return show_sequence(ImageFolder(folder))


def show(
        data_source: Union[Path, str, object],
        window_title: str = "Image Sequence Viewer",
        **kwargs) -> int:
    """
    Runs the ImageSequenceViewer for the given data source.

    Args:
      data_source: Any object that provides random access to
        the image sequence. Must implement `__len__` and `__getitem__`,
        where the latter returns the image at the given index as numpy array.
        If a string or Path is given, all images within this folder will be
        displayed.
      window_title: The title of the application window.
      kwargs: Additional arguments passed to the SequenceViewer.

    Returns:
      The application's exit code.
    """
    if isinstance(data_source, (str, Path)):
        return show_folder(data_source, window_title, **kwargs)
    else:
        return show_sequence(data_source, window_title, **kwargs)
