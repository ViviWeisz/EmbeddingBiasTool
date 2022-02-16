import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QGroupBox, QLabel, QWidget, QLineEdit, \
    QPushButton, QTabWidget, QVBoxLayout


# Uses QMainWindow to create the main window
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Embedding Bias Tool")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)

        # Main Widget
        main_widget = QWidget()
        main_layout = QGridLayout()

        # Three Boxes to select different models
        self.create_model_selection_widgets()

        main_layout.addWidget(self._model_selection_widget_one, 0, 0)
        main_layout.addWidget(self._model_selection_widget_two, 0, 1)
        main_layout.addWidget(self._model_selection_widget_three, 0, 2)

        # Tab Widget for different analysis types
        tab_widget = QTabWidget()
        tab_widget.addTab(FirstAnalysisTab(self), "First Analysis")
        tab_widget.addTab(SecondAnalysisTab(self), "First Analysis")
        tab_widget.addTab(ThirdAnalysisTab(self), "First Analysis")

        main_layout.addWidget(tab_widget, 1, 0, 3, 0)

        # Set the main layout
        main_layout.setRowStretch(0, 0)
        main_layout.setRowStretch(1, 20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Test status")

        # Window Dimensions
        geometry = self.screen().availableGeometry()
        self.setBaseSize(geometry.width() * 0.8, geometry.height() * 0.7)


    # Slots
    @Slot()
    def exit_app(self, checked):
        QApplication.quit()

    def create_model_selection_widgets(self):
        self._model_selection_widget_one = self._create_selection_widget("First")
        self._model_selection_widget_two = self._create_selection_widget("Second")
        self._model_selection_widget_three = self._create_selection_widget("Third")

    def _create_selection_widget(self, name):
        selection_widget = QGroupBox(f"{name} Model")
        layout = QGridLayout()

        filepath_input = QLineEdit("File Path")
        filepath_button = QPushButton("Browse")
        title_input = QLineEdit("Name")
        load_button = QPushButton("Load")
        status_label = QLabel("Status")

        layout.addWidget(filepath_input, 0, 0)
        layout.addWidget(filepath_button, 0, 1)
        layout.addWidget(title_input, 1, 0)
        layout.addWidget(load_button, 1, 1)
        layout.addWidget(status_label, 2, 0, 1, 2)

        selection_widget.setLayout(layout)
        return selection_widget


class FirstAnalysisTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        placeholder_label = QLabel("Placeholder Label")
        main_layout = QVBoxLayout()
        main_layout.addWidget(placeholder_label)
        self.setLayout(main_layout)


class SecondAnalysisTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        placeholder_label = QLabel("Placeholder Label")
        main_layout = QVBoxLayout()
        main_layout.addWidget(placeholder_label)
        self.setLayout(main_layout)


class ThirdAnalysisTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        placeholder_label = QLabel("Placeholder Label")
        main_layout = QVBoxLayout()
        main_layout.addWidget(placeholder_label)
        self.setLayout(main_layout)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
