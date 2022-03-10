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


def compute_association(model, word):
    data = pd.DataFrame(model.most_similar(positive=word), columns=[[word, 'Similarity']])
    return data


def compute_analogy(model, positve_a, positve_b, negative_a):
    data = pd.DataFrame(model.most_similar(negative=negative_a, positive=[positve_a, positve_b]),
                        columns=[["Analogy", 'Similarity']])
    return data


class AnalyserCore:
    def __init__(self):
        self.model_array = []

    # TODO: Think of alternatives for fast loading and implement loading of different file types besides word2vec.txt
    # Returns True if successful and a Message to display on Error
    def load_model(self, index, name, path, model_type):
        _limit = 50000
        try:
            # Word2Vec Plaintext
            if model_type == 0:
                # Loads with a limit of 50,000 vectors to reduce load times during testing
                model = KeyedVectors.load_word2vec_format(path, binary=False, limit=_limit)
            # Word2Vec Binary
            elif model_type == 1:
                model = KeyedVectors.load_word2vec_format(path, binary=True, limit=_limit)
            # Glove Plaintext
            elif model_type == 2:
                output_path = path.removesuffix(".txt") + ".w2v.txt"
                glove2word2vec(path, output_path)
                model = KeyedVectors.load_word2vec_format(output_path, binary=False, limit=_limit)
            else:
                print("State 1")
                return "Unimplemented Model Type"
            if index < len(self.model_array):
                del self.model_array[index]
            self.model_array.insert(index, (name, model))
        except ValueError:
            return "Model loading failed. The reason is probably an incorrect model type."
        except:
            return "Model loading failed, for unknown reasons."
        else:
            return True

    def compute_association_models(self, word):
        table_models = []
        for model in self.model_array:
            try:
                output = PandasTableModel(compute_association(model[1], word))
            except KeyError as e:
                output = str(e)
            table_models.append(output)
        return table_models

    def compute_analogy_models(self, positive_a, positive_b, negative_a):
        table_models = []
        for model in self.model_array:
            try:
                output = PandasTableModel(compute_analogy(model[1], positive_a, positive_b, negative_a))
            except KeyError as e:
                output = str(e)
            table_models.append(output)
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
    def __init__(self, data: pd.DataFrame):
        super().__init__()
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

                    return self.raw_data.columns[section][0]
                else:
                    return None
            return None
        return None
