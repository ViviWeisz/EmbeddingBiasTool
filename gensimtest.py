
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from gensim.test.utils import datapath
from gensim import utils

class MyCorpus:
    """AWOOGA"""

    def __iter__(self):
        corpus_path = datapath('lee_background.cor')
        for line in open(corpus_path):
            yield utils.simple_preprocess(line)

import gensim.models

sentences = MyCorpus()
model = gensim.models.Word2Vec(sentences=sentences)

for index, word in enumerate(model.wv.index_to_key):
    if index == 10:
        break
    print(f"word #{index}/{len(model.wv.index_to_key)} is {word}")












