import sys

from contextlib import contextmanager

from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QKeySequence, QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QGroupBox, QLabel, QWidget, QLineEdit, \
    QPushButton, QTabWidget, QVBoxLayout, QFileDialog, QTableView, QComboBox, QMessageBox, \
    QHeaderView, QSizePolicy, QRadioButton, QCheckBox

import BiasAnalyserCore


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
        tab_widget.addTab(AssociationAnalysisTab(self), "Association Analysis")
        tab_widget.addTab(AnalogyAnalysisTab(self), "Analogy Analysis")
        tab_widget.addTab(GroupBiasAnalysisTab(self), "Group Bias Analysis")

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

    def show_message(self, main_text, detail_text=""):
        message = QMessageBox()
        message.setText(main_text)
        message.setInformativeText(detail_text)
        message.setWindowTitle("Popup")
        message.setStandardButtons(QMessageBox.Ok)
        message.exec()

    # Slots
    @Slot()
    def load_model(self, model_path, model_name, model_status, _id, combo_box):
        if model_name.text() == "":
            self.show_message("Please insert a Model Name")
        else:
            if combo_box.currentIndex() == -1:
                self.show_message("Please select a Model Type")
            elif 0 <= combo_box.currentIndex() <= 2:
                with self.wait_context():
                    model_status.setText("Loading Model")
                    QApplication.processEvents()
                    status = self.bias_analyser.load_model(_id, model_name.text(), model_path.text(),
                                                           combo_box.currentIndex())
                    if status is True:
                        model_status.setText("Loaded {0} Model".format(model_name.text()))
                    else:
                        self.show_message(status)
            else:
                self.show_message("Invalid Model Type")

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
        self.status_label = QLabel()

        self.combo_box = QComboBox()
        self.combo_box.setPlaceholderText("Select Model Type ...")
        self.combo_box.addItem("Word2Vec .txt file")
        self.combo_box.addItem("Word2Vec .bin file")
        self.combo_box.addItem("Glove .txt file (Generates Word2Vec file in the same location)")

        self.filepath_button.clicked.connect(self.browse_file)
        self.load_button.clicked.connect(
            lambda: self.parent.load_model(self.filepath_input, self.title_input, self.status_label, self.id,
                                           self.combo_box))

        self.layout.addWidget(self.filepath_input, 0, 0)
        self.layout.addWidget(self.filepath_button, 0, 1)
        self.layout.addWidget(self.title_input, 1, 0)
        self.layout.addWidget(self.load_button, 1, 1)
        self.layout.addWidget(self.status_label, 2, 1)
        self.layout.addWidget(self.combo_box, 2, 0)

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


class AnalysisTab(QWidget):

    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.parent = parent

        # Create Input Box
        self.top_box = QGroupBox()
        self.top_box.setTitle("Input")
        self.top_box.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))
        self.top_layout = QGridLayout()

        # Setup Output Box
        self.bot_box = QGroupBox()
        self.bot_box.setTitle("Output")
        self.bot_layout = QGridLayout()
        self.bot_box.setLayout(self.bot_layout)

        # Setup Main Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.top_box)
        self.main_layout.addWidget(self.bot_box)
        self.setLayout(self.main_layout)

    def create_basic_table(self, models):
        for idx, model in enumerate(models):
            label = QLabel()
            label.setText(self.parent.bias_analyser.model_array[idx][0])

            if isinstance(model, str):
                data_view = QLabel(model)

            else:
                data_view = QTableView()
                data_view.setModel(model)
                data_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

            if None is not self.bot_layout.itemAtPosition(0, idx):
                self.bot_layout.itemAtPosition(0, idx).widget().hide()
                self.bot_layout.removeItem(self.bot_layout.itemAtPosition(0, idx))

            self.bot_layout.addWidget(label, 0, idx, alignment=Qt.AlignTop)

            if None is not self.bot_layout.itemAtPosition(1, idx):
                self.bot_layout.itemAtPosition(1, idx).widget().hide()
                self.bot_layout.removeItem(self.bot_layout.itemAtPosition(1, idx))

            self.bot_layout.addWidget(data_view, 1, idx)
            self.bot_layout.setColumnStretch(idx, 1)

        self.setLayout(self.main_layout)


class AssociationAnalysisTab(AnalysisTab):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.parent = parent

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.compute_data)
        self.top_layout.addWidget(self.start_button, 0, 1, 1, 1, alignment=Qt.AlignTop)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Input Word")
        self.top_layout.addWidget(self.text_input, 0, 0, 2, 1, alignment=Qt.AlignTop)
        self.top_box.setLayout(self.top_layout)

    @Slot()
    def compute_data(self):
        models = self.parent.bias_analyser.compute_association_models(self.text_input.text().lower())

        self.create_basic_table(models)


class AnalogyAnalysisTab(AnalysisTab):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.parent = parent

        self.word_a_input = QLineEdit()
        self.word_a_input.setPlaceholderText("Word 1")
        self.top_layout.addWidget(self.word_a_input, 0, 0, alignment=Qt.AlignTop)

        self.to_label = QLabel("is to")
        self.top_layout.addWidget(self.to_label, 0, 1)

        self.word_b_input = QLineEdit()
        self.word_b_input.setPlaceholderText("Word 2")
        self.top_layout.addWidget(self.word_b_input, 0, 2, alignment=Qt.AlignTop)

        self.other_label = QLabel("as")
        self.top_layout.addWidget(self.other_label, 0, 3)

        self.word_c_input = QLineEdit()
        self.word_c_input.setPlaceholderText("Word 3")
        self.top_layout.addWidget(self.word_c_input, 0, 4, alignment=Qt.AlignTop)

        self.other_label = QLabel("is to ...")
        self.top_layout.addWidget(self.other_label, 0, 5)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.compute_data)
        self.top_layout.addWidget(self.start_button, 0, 6, alignment=Qt.AlignTop)
        self.top_box.setLayout(self.top_layout)

    @Slot()
    def compute_data(self):
        models = self.parent.bias_analyser.compute_analogy_models(self.word_b_input.text().lower(),
                                                                  self.word_c_input.text().lower(),
                                                                  self.word_a_input.text().lower())

        self.create_basic_table(models)


class GroupBiasAnalysisTab(AnalysisTab):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.gender_button = QRadioButton("Gender")
        self.gender_button.setChecked(True)
        self.race_button = QRadioButton("Race")
        self.religion_button = QRadioButton("Religion")
        self.economic_button = QRadioButton("Economic")
        self.bias_selection_layout = QVBoxLayout()
        self.bias_selection_layout.addWidget(self.gender_button)
        self.bias_selection_layout.addWidget(self.race_button)
        self.bias_selection_layout.addWidget(self.religion_button)
        self.bias_selection_layout.addWidget(self.economic_button)
        self.top_layout.addLayout(self.bias_selection_layout, 0, 0, 4, 1)

        self.normalize_check = QCheckBox("Normalized")
        self.top_layout.addWidget(self.normalize_check, 2, 1, 1, 1)

        self.category_check = QCheckBox("Limit to categories")
        self.category_check.setChecked(True)
        self.top_layout.addWidget(self.category_check, 1, 1, 1, 1)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.compute_data)
        self.top_layout.addWidget(self.start_button, 3, 1, 1, 1, alignment=Qt.AlignTop)
        self.top_box.setLayout(self.top_layout)

    @Slot()
    def compute_data(self):
        bias_type = "gender"
        if self.gender_button.isChecked():
            bias_type = 0
        elif self.race_button.isChecked():
            bias_type = 1
        elif self.religion_button.isChecked():
            bias_type = 2
        elif self.economic_button.isChecked():
            bias_type = 3

        category = self.category_check.isChecked()
        normalize = self.normalize_check.isChecked()
        models = self.parent.bias_analyser.compute_bias_score_model(bias_type, normalize, category)
        self.create_basic_table(models)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
