# Image Sequence Visualizer

### Installation
It is highly recommended to set up a separate virtual environment with an up-to-date `pip`:
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
```

Then, simply install `imseqvis` via:
```bash
python -m pip install git+https://github.com/snototter/imseqvis.git
```

### Qt Backend
`imseqvis` requires a [Qt](https://www.qt.io/) backend. In Python, you need to
either install [PyQt](https://www.riverbankcomputing.com/software/pyqt/download)
or [PySide](https://doc.qt.io/qtforpython-6/).  
The default installation **will not install** any of these backends, you have
to select one on your own.


### Usage

```python
# Prepare the image data source. This must allow random access to the images.
# See the provided data sources within the examples/ folder for best practices.
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

More detailed usage examples are provided within `examples/`:
* `examples/demo_standalone.py` demonstrates the basic usage with a dummy
  sequence. It will run out-of-the-box.
* `examples/demo_folder.py` will playback all images within a local folder.
  This demo additionally requires the [vito](https://pypi.org/project/vito/)
  package to load image files.


### TODOs
* [x] Switch to a more sophisticated image viewer
* [x] Implement a stateful viewer (keep zoom & ROI during playback/seek)
* [ ] Allow optional qt/pyside selection
* [ ] Allow initialization without any sequence


