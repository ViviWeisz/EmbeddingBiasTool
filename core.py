import gensim.models
import gensim.models.keyedvectors as word2vec

#new_model = gensim.models.Word2Vec.load(r'D:\Uni\Bachelor\Datasets\GoogleNews-vectors-negative300.bin')
print("Start Loading")
new_model_tuple = ("test",word2vec.KeyedVectors.load_word2vec_format(r'D:\Uni\Bachelor\Datasets\GoogleNews-vectors-negative300.bin', binary=True))
print("Finished Loading")

