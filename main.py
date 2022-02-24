import sys
import time

from contextlib import contextmanager

from PySide6 import QtCore
from PySide6.QtCore import Slot, Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QAction, QKeySequence, QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QGroupBox, QLabel, QWidget, QLineEdit, \
    QPushButton, QTabWidget, QVBoxLayout, QFileDialog, QStatusBar, QListView, QTableView

import BiasAnalyserCore
from BiasAnalyserCore import BaseTableModel

loaded_models = []


# Uses QMainWindow to create the main window
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Create Analyser Backend
        self.bias_analyser = BiasAnalyserCore.AnalyserCore()

        # Set Window Title
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

        main_layout.addWidget(ModelBrowserWidget(self, 0), 0, 0)
        main_layout.addWidget(ModelBrowserWidget(self, 1), 0, 1)
        main_layout.addWidget(ModelBrowserWidget(self, 2), 0, 2)

        # Tab Widget for different analysis types
        tab_widget = QTabWidget()
        tab_widget.addTab(FirstAnalysisTab(self), "First Analysis")
        tab_widget.addTab(SecondAnalysisTab(self), "Second Analysis")
        tab_widget.addTab(ThirdAnalysisTab(self), "Third Analysis")

        main_layout.addWidget(tab_widget, 1, 0, 3, 0)

        # Set the main layout
        main_layout.setRowStretch(0, 0)
        main_layout.setRowStretch(1, 20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Ready")

        # Window Dimensions
        geometry = self.screen().availableGeometry()
        self.setMinimumSize(geometry.width() * 0.6, geometry.height() * 0.6)

    # Slots
    # TODO: Implement Model loading in a different module and then add the loaded model to a list of tuples
    #  with names + model
    @Slot()
    def load_model(self, model_path, model_name, model_status, _id):
        with self.wait_context():
            model_status.setText("Loading Model")
            self.bias_analyser.load_model(_id, model_name.text(), model_path.text())
            model_status.setText("Loaded {0} Model".format(model_name.text()))
            pass
        print(loaded_models)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()

    # Methods
    def change_status(self, _status):
        self.status.showMessage(_status)

    @contextmanager
    def wait_context(self):
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            MainWindow.change_status(self, "Loading...")
            QApplication.processEvents()

            yield
        finally:
            QApplication.restoreOverrideCursor()
            MainWindow.change_status(self, "Done!")


class ModelBrowserWidget(QGroupBox):
    name = ["First", "Second", "Third"]

    def __init__(self, parent: MainWindow, _id):
        super().__init__(parent)
        self.id = _id
        self.parent = parent

        self.setTitle(f"{self.name[_id]} Model")
        self.layout = QGridLayout()

        self.filepath_input = QLineEdit()
        self.filepath_input.setPlaceholderText("File Path")
        self.filepath_button = QPushButton("Browse")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Model Name")
        self.load_button = QPushButton("Load")
        self.status_label = QLabel("Status")

        self.filepath_button.clicked.connect(self.browse_file)
        self.load_button.clicked.connect(
            lambda: self.parent.load_model(self.filepath_input, self.title_input, self.status_label, self.id))

        self.layout.addWidget(self.filepath_input, 0, 0)
        self.layout.addWidget(self.filepath_button, 0, 1)
        self.layout.addWidget(self.title_input, 1, 0)
        self.layout.addWidget(self.load_button, 1, 1)
        self.layout.addWidget(self.status_label, 2, 0, 1, 2)

        self.setLayout(self.layout)

    @Slot()
    def browse_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setDirectory(r"D:\Uni\Bachelor\Datasets")
        dialog.setNameFilter("Models (*.model *.txt *.npy *.bin)")
        if dialog.exec():
            self.filepath_input.setText(dialog.selectedFiles()[0])
            print("FILE: " + dialog.selectedFiles()[0])


# TODO: Implement different types of analysis: Association, Analogy, Bias score,
#  https://dl.acm.org/doi/pdf/10.1145/3351095.3372843#page=12&zoom=100,76,805
class FirstAnalysisTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        model = BaseTableModel(self, ["Test 1", "test 2"], ["Wa wa", "Wa We"], "test")

        data_view = QTableView()
        data_view.setModel(model)
        main_layout = QVBoxLayout()
        main_layout.addWidget(data_view)
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
