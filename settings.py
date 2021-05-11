import PySide2
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton


class SettingsWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent = parent

        self.setMinimumWidth(320)
        self.setMinimumHeight(100)

        layout = QVBoxLayout()

        self.sliderLabel = QLabel("Window transparency: 5")
        self.sliderLabel.setAlignment(Qt.AlignCenter)
        self.sliderLabel.setFont(QFont('Arial', 11))
        self.sliderLabel.setContentsMargins(8, 8, 8, 8)

        self.mySlider = QSlider(Qt.Horizontal, self)

        self.mySlider.sliderMoved[int].connect(self.opacityChangeValue)
        self.mySlider.sliderReleased.connect(self.opacityRelease)
        self.mySlider.setMinimum(1)
        self.mySlider.setMaximum(10)
        self.mySlider.setSingleStep(1)
        self.mySlider.setValue(5)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.close)

        layout.addWidget(self.sliderLabel)
        layout.addWidget(self.mySlider)
        layout.addWidget(self.saveButton)

        self.setLayout(layout)

        self.setWindowTitle("Chat Settings")

    def opacityChangeValue(self, value):
        self.sliderLabel.setText("Window transparency: " + str(value))
        self.setWindowOpacity(float(value) / 10)
        self.parent.defaultUnfocusOpacity = (float(value) / 10)

    def opacityRelease(self):
        self.setWindowOpacity(1.0)

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        self.parent.show()
