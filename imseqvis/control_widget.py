from qtpy.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
        QPushButton, QSlider, QLineEdit, QLabel, QToolButton)
from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QIcon, QFontMetrics


class SequenceControlWidget(QWidget):
    """
    Playback/seeking controls for a sequence/video player.

    TODO doc

    Note that the emitted index is 1-based.
    """
    
    # Signaled whenever the selected frame (i.e. slider value) changes.
    indexChanged = Signal(int)

    # Signaled whenever the user requests the previous sequence (if
    # these buttons are enabled).
    previousSequenceRequested = Signal()

    # Signaled whenever the user requests the next sequence (if
    # these buttons are enabled).
    nextSequenceRequested = Signal()

    def __init__(
            self,
            max_value: int,
            playback_timeout: int = 100,
            playback_wait_for_viewer_ready: bool = True,
            include_sequence_buttons: bool = False):
        """
        Initialize the controls widget.
        
        Args:
          max_value: The slider will range from 1 to max_value (incl.)
          playback_timeout: Timeout of the playback timer in milliseconds.
          playback_wait_for_viewer_ready: If True, the timer playback will
            only advance to the next index if `onViewerReady` has been
            called since the last emitted `indexChanged` signal.
          include_sequence_buttons: If True, controls to skip to the previous
            or next sequence will be shown. If clicked, the corresponding
            `previousSequenceRequested` or `nextSequenceRequested` signal will
            be emitted.
        """
        super().__init__()
        self.max_value = max_value
        self.playback_timeout = playback_timeout
        
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.onPlaybackTimeout)
        self.playback_wait_for_viewer_ready = playback_wait_for_viewer_ready
        self.is_viewer_ready = True
        
        self.initUI(include_sequence_buttons)

    def setMaxValue(self, max_value):
        self.max_value = max_value
        self.slider.setRange(1, self.max_value)
        self.current_value_label.setFixedWidth(QFontMetrics(self.font()).width(str(self.max_value)) + 10)
        self.sliderValueChanged(1)
    
    def onViewerReady(self):
        self.is_viewer_ready = True

    def initUI(
            self,
            include_sequence_buttons: bool):
        # Theme icon names:
        # https://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html

        # Automatic playback button (toggles between play/pause)
        self.playback_button = QToolButton()
        self.playback_button.setIcon(QIcon.fromTheme('media-playback-start'))
        self.playback_button.clicked.connect(self.togglePlayback)

        # Reset button        
        reload_button = QToolButton()
        reload_button.setIcon(QIcon.fromTheme('view-refresh'))
        reload_button.clicked.connect(self.resetSlider)
        
        # Navigation buttons (step forward/backward)
        self.previous_button = QToolButton()
        self.previous_button.setIcon(QIcon.fromTheme('go-previous'))
        self.previous_button.clicked.connect(lambda: self.skip(self.previous_button, -1))
        
        self.next_button = QToolButton()
        self.next_button.setIcon(QIcon.fromTheme('go-next'))
        self.next_button.clicked.connect(lambda: self.skip(self.next_button, +1))

        # Navigation buttons (skip to previous/next sequence)
        previous_seq_button = QToolButton()
        previous_seq_button.setIcon(QIcon.fromTheme('go-up'))
        previous_seq_button.clicked.connect(self.previousSequenceRequested)

        next_seq_button = QToolButton()
        next_seq_button.setIcon(QIcon.fromTheme('go-down'))
        next_seq_button.clicked.connect(self.nextSequenceRequested)

        # The slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, self.max_value)
        self.slider.setMinimumWidth(100)
        self.slider.valueChanged.connect(lambda value: self.sliderValueChanged(value))

        # Text box to manually set the slider value
        self.manual_input = QLineEdit()
        self.manual_input.setFixedWidth(100)
        self.manual_input.setPlaceholderText('Jump to:')
        self.manual_input.returnPressed.connect(self.updateSliderFromTextBox)

        # Label to display the current value
        max_label_width = QFontMetrics(self.font()).width(str(self.max_value))
        self.current_value_label = QLabel('')
        self.current_value_label.setFixedWidth(max_label_width + 10)  # Minor padding added
        self.current_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Align all controls horizontally
        layout = QHBoxLayout()
        if include_sequence_buttons:
            layout.addWidget(previous_seq_button)
            layout.addWidget(next_seq_button)
        layout.addWidget(self.previous_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.playback_button)
        layout.addWidget(reload_button)

        layout.addWidget(self.slider)

        layout.addWidget(self.current_value_label)
        layout.addWidget(self.manual_input)

        self.setLayout(layout)
        # Emit signal & update labels by skipping to the first value.
        self.sliderValueChanged(1)
        #self.show() # TODO remove if not needed

    def keyPressEvent(self, event):
        """Custom event filter for keyboard inputs."""
        # Do not use:
        # * Space - leads to different behavior depending on which sub-widget
        #   has the focus. For example, if a button was previously clicked,
        #   space will re-trigger the button.
        # * Return/Enter - will (re-)start the timer every time the user
        #   manually selects a frame via the text box.
        # * Left/Right/PageUp/PageDown - these are handled by the slider and
        #   overriding them here would be confusing for the user (e.g.
        #   inconsistent step sizes).
        if event.key() == Qt.Key_Escape:
            self.resetSlider()
        elif event.key() in [Qt.Key_P, Qt.Key_X]:
            self.togglePlayback()
        elif event.key() == Qt.Key_B:
            self.skip(self.previous_button, -1)
        elif event.key() == Qt.Key_V:
            self.skip(self.previous_button, -10)
        elif event.key() == Qt.Key_N:
            self.skip(self.next_button, +1)
        elif event.key() == Qt.Key_M:
            self.skip(self.next_button, +10)
        elif event.key() == Qt.Key_R:
            self.resetSlider()

    def sliderValueChanged(self, value):
        self.is_viewer_ready = False
        self.previous_button.setEnabled(value > 1)
        self.next_button.setEnabled(value < self.max_value)
        self.current_value_label.setText(str(value))
        self.indexChanged.emit(value)
        
    def resetSlider(self):
        self.stopPlayback()
        self.updateSlider(1)
    
    def skip(self, button, step):
        if not button.isEnabled():
            return
        self.updateSlider(self.slider.value() + step)
        # A manual fwd/bwd request always stops the playback
        self.stopPlayback()
    
    def stopPlayback(self):
        self.playback_timer.stop()
        self.playback_button.setIcon(QIcon.fromTheme('media-playback-start'))
    
    def startPlayback(self):
        if self.slider.value() >= self.max_value:
            # Restart playback from the beginning
            self.updateSlider(1)
        self.playback_timer.start(self.playback_timeout)
        self.playback_button.setIcon(QIcon.fromTheme('media-playback-pause'))
    
    def togglePlayback(self):
        if self.playback_timer.isActive():
            self.stopPlayback()
        else:
            self.startPlayback()
    
    def onPlaybackTimeout(self):
        if self.playback_wait_for_viewer_ready and not self.is_viewer_ready:
            # Skip this timeout if the viewer has not shown the last image yet
            return
        value = self.slider.value() + 1
        if value <= self.max_value:
            self.updateSlider(value)
        else:
            self.stopPlayback()
        
    def updateSlider(self, value):
        # Update the slider and label with the new value
        if 1 <= value <= self.max_value:
            self.slider.setValue(value)
            self.current_value_label.setText(str(value))

    def updateSliderFromTextBox(self):
        # Get the value from the text box
        try:
            value = int(self.manual_input.text())
            self.stopPlayback()
            self.updateSlider(value)
        except ValueError:
            pass
        # Always reset the input text box
        self.manual_input.setText('')

