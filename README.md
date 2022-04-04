# Embedding Bias Tool

This tool is meant for analysing biases in word embeddings, it can load Word2Vec and GloVe embeddings and analyse them.


## Setup

The tool requires Python 3.10.
To start the tool install the required packages from the requirements.txt using pip.

```bash
pip install -r requirements.txt
```

Then run main.py

```bash
python3 main.py
```
or
```bash
python main.py
```
## Usage

Import embeddings at the top and then use the different analysis tabs for analysing.
By default, the tool will load the entire models, which takes a long time. To speed it up change the model limit that's set to None at line 13 of BiasAnalyserCore.py.

```python
# Limit for model loading
model_limit = 200000
```

List of example embeddings:
- [Google News Vectors](https://code.google.com/archive/p/word2vec/)
- [GloVe Embeddings](https://nlp.stanford.edu/projects/glove/)
- [Google News Debiased](https://github.com/tolga-b/debiaswe)


## License
[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)