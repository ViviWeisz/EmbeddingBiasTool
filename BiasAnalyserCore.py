import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.spatial.distance import cosine
import csv

from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

# Limit for model loading
model_limit = None


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
    g1 = rows[bias_type * 2]
    g2 = rows[bias_type * 2 + 1]
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


def compute_bias_score(model: KeyedVectors, bias_type, normalized, category):
    neutral_words = make_neutral_words()
    g1_vec, g2_vec = compute_group_vectors(model, bias_type)
    categories = ["Profession", "Physical Appearance", "Extremism", "Personality", "Cultivation"]
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
        # Normalizes the score to the distance of the 2 groups
        if normalized:
            bias_score = bias_score / cosine(g1_vec, g2_vec)
        bias.append(bias_score)
    if category is not True:
        bias_score = 0
        count = len(model.index_to_key)
        for word in model.key_to_index:
            if model.has_index_for(word.lower()) is not True:
                continue
            bias_score += abs(cosine(g1_vec, model[word.lower()]) - cosine(g2_vec, model[word.lower()]))
        bias_score = bias_score / count
        # Normalizes the score to the distance of the 2 groups
        if normalized:
            bias_score = bias_score / cosine(g1_vec, g2_vec)
        bias.append(bias_score)
        categories.append("All Words")
    d = {"Category": categories, "Bias": bias}
    df = pd.DataFrame(data=d)
    return df


class AnalyserCore:
    def __init__(self):
        self.model_array = []

    # Returns True if successful or a Message to display on Error when not working
    def load_model(self, index, name, path, model_type):
        _limit = model_limit
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

    def compute_bias_score_model(self, bias_type, normalized, category):
        table_models = []
        for model in self.model_array:
            output = PandasTableModel(compute_bias_score(model[1], bias_type, normalized, category))
            table_models.append(output)
        return table_models


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
