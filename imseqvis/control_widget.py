from qtpy.QtWidgets import (
    QWidget, QHBoxLayout, QSlider, QLineEdit, QLabel, QToolButton)
from qtpy.QtCore import Qt, Signal, Slot, QTimer
from qtpy.QtGui import QIcon, QFontMetrics


class SequenceControlWidget(QWidget):
    """
    Playback/seeking controls for a sequence/video player.

    This widget provides a user interface to navigate a sequence and scale
    the displayed image. Optionally, it also provides buttons to navigate to
    the previous/next sequence.

    Note that the emitted index is 1-based.
    """

    # Signaled whenever the selected frame (i.e. slider value) changes. Note
    # that this index is 1-based.
    indexChanged = Signal(int)

    # The user wants to display the image at its original size.
    zoomOriginalSizeRequest = Signal()

    # The user wants to display the image scaled to fit the window.
    zoomFitToWindowRequest = Signal()

    # The user wants to advance to the previous sequence. Only available if
    # the sequence navigation buttons have been enabled.
    previousSequenceRequest = Signal()

    # The user wants to advance to the next sequence. Only available if
    # the sequence navigation buttons have been enabled.
    nextSequenceRequest = Signal()

    def __init__(
            self,
            max_value: int,
            playback_timeout: int = 100,
            playback_wait_for_viewer_ready: bool = True,
            include_sequence_navigation_buttons: bool = False,
            include_zoom_buttons: bool = True):
        """
        Initialize the controls widget.

        Args:
          max_value: The slider will range from 1 to max_value (incl.)
          playback_timeout: Timeout of the playback timer in milliseconds.
          playback_wait_for_viewer_ready: If True, the timer playback will
            only advance to the next index if `onViewerReady` has been
            called since the last emitted `indexChanged` signal.
          include_sequence_navigation_buttons: If True, controls to skip to the
            previous or next sequence will be shown. If clicked, the
            corresponding `previousSequenceRequest` or `nextSequenceRequest`
            will be emitted.
          include_zoom_buttons: If True, buttons to zoom the image will be
            shown and the corresponding `zoomXXXRequest` will be emitted.
        """
        super().__init__()
        self.max_value = max_value
        self.playback_timeout = playback_timeout

        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.onPlaybackTimeout)
        self.playback_wait_for_viewer_ready = playback_wait_for_viewer_ready
        self.is_viewer_ready = True

        self.initUI(include_sequence_navigation_buttons, include_zoom_buttons)

    @Slot(int)
    def setMaxValue(self, max_value):
        self.max_value = max_value
        self.slider.setRange(1, self.max_value)
        self.label_current_value.setFixedWidth(
            QFontMetrics(self.font()).width(str(self.max_value)) + 10)
        self.updateSlider(1)

    @Slot()
    def onViewerReady(self):
        self.is_viewer_ready = True

    def initUI(
            self,
            include_sequence_navigation_buttons: bool,
            include_zoom_buttons: bool):
        # List of theme icon names:
        # https://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html

        # Automatic playback button (toggles between play/pause).
        self.button_playback = QToolButton()
        self.button_playback.setIcon(QIcon.fromTheme('media-playback-start'))
        self.button_playback.setToolTip('Toggle play/pause')
        self.button_playback.clicked.connect(self.togglePlayback)

        # Reset button to skip to the first frame.
        button_reload = QToolButton()
        button_reload.setIcon(QIcon.fromTheme('view-refresh'))
        button_reload.setToolTip('Reset sequence')
        button_reload.clicked.connect(self.resetSlider)

        # Navigation buttons (step forward/backward).
        self.button_previous_frame = QToolButton()
        self.button_previous_frame.setIcon(QIcon.fromTheme('go-previous'))
        self.button_previous_frame.setToolTip('Previous frame')
        self.button_previous_frame.clicked.connect(
            lambda: self.skip(self.button_previous_frame, -1))

        self.button_next_frame = QToolButton()
        self.button_next_frame.setIcon(QIcon.fromTheme('go-next'))
        self.button_next_frame.setToolTip('Next frame')
        self.button_next_frame.clicked.connect(
            lambda: self.skip(self.button_next_frame, +1))

        # Navigation buttons (skip to previous/next sequence).
        button_previous_sequence = QToolButton()
        button_previous_sequence.setIcon(QIcon.fromTheme('go-up'))
        button_previous_sequence.setToolTip('Previous sequence')
        button_previous_sequence.clicked.connect(self.previousSequenceRequest)

        button_next_sequence = QToolButton()
        button_next_sequence.setIcon(QIcon.fromTheme('go-down'))
        button_next_sequence.setToolTip('Next sequence')
        button_next_sequence.clicked.connect(self.nextSequenceRequest)

        # The slider.
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, self.max_value)
        self.slider.setMinimumWidth(100)
        self.slider.valueChanged.connect(
            lambda value: self.sliderValueChanged(value))

        # Text box to manually set the slider value.
        self.manual_input = QLineEdit()
        self.manual_input.setFixedWidth(100)
        self.manual_input.setPlaceholderText('Jump to:')
        self.manual_input.setToolTip('Enter frame to jump to')
        self.manual_input.returnPressed.connect(self.updateSliderFromTextBox)

        # Label to display the current value.
        max_label_width = QFontMetrics(self.font()).width(str(self.max_value))
        self.label_current_value = QLabel('')
        # Add minor padding to the label.
        self.label_current_value.setFixedWidth(max_label_width + 10)
        self.label_current_value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Buttons to zoom the image viewer.
        button_zoom_fit = QToolButton()
        button_zoom_fit.setIcon(QIcon.fromTheme('zoom-fit-best'))
        button_zoom_fit.setToolTip('Fit to window')
        button_zoom_fit.clicked.connect(self.zoomFitToWindowRequest)

        button_zoom_original = QToolButton()
        button_zoom_original.setIcon(QIcon.fromTheme('zoom-original'))
        button_zoom_original.setToolTip('Show at original size')
        button_zoom_original.clicked.connect(self.zoomOriginalSizeRequest)

        # Align all controls horizontally.
        layout = QHBoxLayout()
        if include_sequence_navigation_buttons:
            layout.addWidget(button_previous_sequence)
            layout.addWidget(button_next_sequence)
        layout.addWidget(self.button_previous_frame)
        layout.addWidget(self.button_next_frame)
        layout.addWidget(self.button_playback)
        layout.addWidget(button_reload)

        layout.addWidget(self.slider)

        layout.addWidget(self.label_current_value)
        layout.addWidget(self.manual_input)

        if include_zoom_buttons:
            layout.addWidget(button_zoom_fit)
            layout.addWidget(button_zoom_original)

        self.setLayout(layout)
        # Emit signal & update labels.
        self.sliderValueChanged(1)

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
        if event.key() in [Qt.Key_Escape, Qt.Key_R]:
            self.resetSlider()
        elif event.key() in [Qt.Key_P, Qt.Key_X]:
            self.togglePlayback()
        elif event.key() == Qt.Key_B:
            self.skip(self.button_previous_frame, -1)
        elif event.key() == Qt.Key_V:
            self.skip(self.button_previous_frame, -10)
        elif event.key() == Qt.Key_N:
            self.skip(self.button_next_frame, +1)
        elif event.key() == Qt.Key_M:
            self.skip(self.button_next_frame, +10)

    def sliderValueChanged(self, value):
        self.is_viewer_ready = False
        self.button_previous_frame.setEnabled(value > 1)
        self.button_next_frame.setEnabled(value < self.max_value)
        self.label_current_value.setText(str(value))
        self.indexChanged.emit(value)

    def resetSlider(self):
        self.stopPlayback()
        self.updateSlider(1)

    def skip(self, button, step):
        if not button.isEnabled():
            return
        self.updateSlider(self.slider.value() + step)
        # A manual fwd/bwd request always stops the playback.
        self.stopPlayback()

    def stopPlayback(self):
        self.playback_timer.stop()
        self.button_playback.setIcon(QIcon.fromTheme('media-playback-start'))

    def startPlayback(self):
        if self.slider.value() >= self.max_value:
            # Restart playback from the beginning.
            self.updateSlider(1)
        self.playback_timer.start(self.playback_timeout)
        self.button_playback.setIcon(QIcon.fromTheme('media-playback-pause'))

    def togglePlayback(self):
        if self.playback_timer.isActive():
            self.stopPlayback()
        else:
            self.startPlayback()

    def onPlaybackTimeout(self):
        if self.playback_wait_for_viewer_ready and not self.is_viewer_ready:
            # Skip this timeout if the viewer has not shown the last image yet.
            return
        value = self.slider.value() + 1
        if value <= self.max_value:
            self.updateSlider(value)
        else:
            self.stopPlayback()

    def updateSlider(self, value):
        # Update the slider and label with the new value.
        if 1 <= value <= self.max_value:
            self.slider.setValue(value)
            self.label_current_value.setText(str(value))

    def updateSliderFromTextBox(self):
        # Get the value from the text box.
        try:
            value = int(self.manual_input.text())
            self.stopPlayback()
            self.updateSlider(value)
        except ValueError:
            pass
        # Always reset the input text box.
        self.manual_input.setText('')
    
    @Slot()
    def focusOnManualInput(self):
        """Focus the manual input text box and select all text."""
        self.manual_input.setFocus()
        self.manual_input.selectAll()
