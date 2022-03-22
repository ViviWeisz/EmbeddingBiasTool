import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.spatial.distance import cosine
import csv
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


def compute_analogy(model, positive_a, positive_b, negative_a):
    data = pd.DataFrame(model.most_similar(negative=negative_a, positive=[positive_a, positive_b]),
                        columns=[["Analogy", 'Similarity']])
    return data


def load_group_words(bias_type):
    with open("group_words.csv", "r") as filehandle:
        csvreader = csv.reader(filehandle)
        rows = []
        for row in csvreader:
            rows.append(row)
    g1 = rows[bias_type*2]
    g2 = rows[bias_type*2+1]
    return g1, g2


def make_neutral_words():
    with open("neutral_words.csv", "r") as filehandle:
        csvreader = csv.reader(filehandle)
        rows = []
        for row in csvreader:
            rows.append(row)
    return rows


def compute_group_vector(model, group, dimension):
    group_vector = np.zeros((dimension,), dtype=float)
    for w in group:
        w = w.strip()
        if w not in model:
            continue
        w_vec = model[w] / norm(model[w])
        group_vector = np.add(group_vector, w_vec)
    return group_vector


def compute_group_vectors(model: KeyedVectors, bias_type):
    g1, g2, = load_group_words(bias_type)
    dimension = model.vector_size
    g1_vec = compute_group_vector(model, g1, dimension)
    g2_vec = compute_group_vector(model, g2, dimension)
    g1_vec, g2_vec = g1_vec / norm(g1_vec), g2_vec / norm(g2_vec)
    return g1_vec, g2_vec


def compute_bias_score(model, bias_type):
    neutral_words = make_neutral_words()
    g1_vec, g2_vec = compute_group_vectors(model, bias_type)
    categories = ["Profession", "Physical Appearance", "Extremism", "Personality"]
    bias = []
    for words in neutral_words:
        bias_score = 0
        count = 0
        for word in words:
            if model.has_index_for(word.lower()) is not True:
                continue
            bias_score += abs(cosine(g1_vec, model[word.lower()]) - cosine(g2_vec, model[word.lower()]))
            count += 1
        bias_score = bias_score / count
        bias.append(bias_score)
    d = {"Category": categories, "Bias": bias}
    df = pd.DataFrame(data=d)
    return df


class AnalyserCore:
    def __init__(self):
        self.model_array = []

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

    def compute_bias_score_model(self, bias_type):
        table_models = []
        for model in self.model_array:
            output = PandasTableModel(compute_bias_score(model[1], bias_type))
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
                    if isinstance(self.raw_data.columns[section], str):
                        return self.raw_data.columns[section]
                    return self.raw_data.columns[section][0]
                else:
                    return None
            return None
        return None
