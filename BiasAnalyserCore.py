import pandas as pd
import numpy as np
import os

import gensim
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.test.utils import datapath, get_tmpfile

# new_model = gensim.models.Word2Vec.load(r'D:\Uni\Bachelor\Datasets\GoogleNews-vectors-negative300.bin')
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget


# print("Start Loading")
# new_model_tuple = ("test", word2vec.KeyedVectors.load_word2vec_format(
#    r'D:\Uni\Bachelor\Datasets\GoogleNews-vectors-negative300.bin', binary=True))
# print("Finished Loading")

class AnalyserCore:
    def __init__(self):
        self.model_array = []

    # TODO: Think of alternatives for fast loading and implement loading of different file types besides word2vec.txt
    def load_model(self, index, name, path):
        # model = KeyedVectors.load_word2vec_format(r'D:\Uni\Bachelor\Datasets\GoogleNews-vectors-negative300.bin',
        #                                           binary=True)
        # Loads with a limit of 50,000 vectors to reduce load times during testing
        model = KeyedVectors.load_word2vec_format(path, binary=False, limit=100000)
        if index < len(self.model_array):
            del self.model_array[index]
        self.model_array.insert(index, (name, model))

    def compute_association_model(self, word):
        table_models = []
        for model in self.model_array:
            data = pd.DataFrame(model[1].most_similar(positive=word), columns=[[word, 'Similarity']])
            table_models.append(data)
        return table_models


class BaseTableModel(QAbstractTableModel):
    def __init__(self, parent: QWidget, horizontal_header, vertical_header, data):
        super().__init__(parent)
        self.test_data = [[0, 1], [2, 3], [4, 5], [6, 7]]
        self.raw_data = data
        self.horizontal_header = horizontal_header
        self.vertical_header = vertical_header

    def rowCount(self, parent=QModelIndex()):
        return len(self.test_data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.test_data[0])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            return '{0}'.format(self.test_data[row][column])
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.horizontal_header):
                    return self.horizontal_header[section]
                else:
                    return None
            elif orientation == Qt.Vertical:
                if section < len(self.vertical_header):
                    return self.vertical_header[section]
                else:
                    return None
            return None
        return None


class PandasTableModel(QAbstractTableModel):
    def __init__(self, parent: QWidget,  data: pd.DataFrame):
        super().__init__(parent)
        self.test_data = [[0, 1], [2, 3], [4, 5], [6, 7]]
        self.raw_data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self.raw_data.index)

    def columnCount(self, parent=QModelIndex()):
        return self.raw_data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            return '{0}'.format(self.raw_data.iloc[row][column])
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.raw_data.columns):
                    return self.raw_data.columns[section]
                else:
                    return None
            return None
        return None
