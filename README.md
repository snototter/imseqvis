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

**Notes:**
* `imseqvis` requires an existing `PyQt5/6` or `PySide2/6` installation  
  For example, install either
  ```
  pip install pyqt5
  ```
  or
  ```
  pip install PySide2
  ```

### Usage

For now, refer to the provided scripts within `examples/`


### TODOs
* [ ] Switch to a more sophisticated image viewer
* [ ] Implement a stateful viewer (keep zoom & ROI during playback/seek)
* [ ] Allow optional qt/pyside selection


