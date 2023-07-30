# Image & Sequence Visualization
[![View on PyPI](https://img.shields.io/pypi/v/imseqvis.svg)](https://pypi.org/project/imseqvis)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/snototter/imseqvis/blob/main/LICENSE?raw=true)

This package provides GUI widgets to show images and playback image sequences.

![Screenshot Sequence Viewer](https://github.com/snototter/imseqvis/blob/main/examples/screenshot.jpg?raw=true "SequenceViewer widget")

### Installation
It is highly recommended to set up a separate virtual environment with an up-to-date `pip`:
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
```

Then, simply install `imseqvis` via:
```bash
python -m pip install imseqvis
```

If you want to try the latest alpha, i.e. the latest `main` branch packaged and
published to [TestPyPI](https://test.pypi.org/), you can instead install it via:
```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "imseqvis[pyside2]"
```

### Qt Backend
`imseqvis` requires a [Qt](https://www.qt.io/) backend. In Python, you need to
either install [PyQt](https://www.riverbankcomputing.com/software/pyqt/download)
or [PySide](https://doc.qt.io/qtforpython-6/).  
The default installation **will not install** any of these backends, you have
to select one on your own.

Optionally, you can install `imseqvis` with a specific backend. Currently,
`pyqt5`, `pyqt6`, `pyside2`, and `pyside6` are supported:
```bash
# PyQt5
python -m pip install "imseqvis[pyqt5]"

# OR PyQt6
python -m pip install "imseqvis[pyqt6]"

# OR PySide2
python -m pip install "imseqvis[pyside2]"

# OR PySide6
python -m pip install "imseqvis[pyside6]"
```

### Usage as Standalone Application
To quickly visualize all images within a folder or sequence (and nothing else),
you can use the provided wrappers to start a standalone GUI application:
```python
import imseqvis
# Show all images in the given folder.
imseqvis.show_folder('path/to/images')

# Show all images in a random access container. For an exemplary data source
# refer to `imseqvis.sequence_viewer.ImageSequence`.
sequence = [...]
imseqvis.show_sequence(sequence)
```

Alternatively, you could simply use the provided `show` functionality:
```python
import imseqvis
imseqvis.show('path/to/images')

sequence = [...]
imseqvis.show(sequence)
```

### Usage as Widget
To integrate the viewer into your own application, use the `ImageSequenceViewer`
widget:
```python
# Prepare the image data source. This must allow random access to the images.
# For an exemplary data source refer to
# `imseqvis.sequence_viewer.ImageSequence`.
sequence = [...]

# Create & use the widget.
viewer = SequenceViewer(image_sequence=sequence)
layout.addWidget(viewer)
...

# Alternatively, the widget can also be created without a data source:
viewer = SequenceViewer(image_sequence=None)
...
# Later on, the image sequence can be set via:
viewer.setSequence(new_sequence)
```

To show a different sequence within the same viewer, simply call:
```python
viewer.setSequence(new_sequence)
```

More detailed usage examples are provided within `examples/`. These also
demonstrate how to use the available signals to be notified of the user's
interactions with the viewer:
* `examples/demo_standalone.py` demonstrates the basic usage with a dummy
  sequence.
* `examples/demo_folder.py` will playback all images within a local folder.
