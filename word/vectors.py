import numpy as np
from scipy.spatial.distance import cosine

from gensim.models import KeyedVectors
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer as MorphyPos

import torch
import torch.nn as nn


class Word2vecGensim(object):
    def __init__(self, w2v_model_file):
        self.stem = MorphyPos()
        self.word2vec = KeyedVectors.load_word2vec_format(w2v_model_file, binary=True)
        # TODO: Оригінальна index2word в цьому словнику: слово_POS, можна би це використати
        self.lemma2word = {word.split('_')[0]: i for i, word in enumerate(self.word2vec.index2word)}

    def _word_vector(self, word):
        w_index = self._word_index(word)
        if w_index == -1:
            return None
        return self.word2vec.vectors[w_index]

    def _word_index(self, word):
        lemma = str(self.stem.parse(word)[0].normal_form)
        index = self.lemma2word.get(lemma, -1)
        return index

    def text_vector(self, text):
        word_vectors = [
            self._word_vector(token)
            for token in word_tokenize(text.lower())
            if token.isalpha()
            ]
        word_vectors = [vec for vec in word_vectors if vec is not None]
        if not word_vectors:
            return np.zeros(*self.word2vec.vectors[0].shape)

        return np.mean(word_vectors, axis=0)

    def _distance(self, word, vector):
        w_vector = self._word_vector(word)
        if w_vector is None:
            return 1
        return cosine(w_vector, vector)

    def distance(self, words, vector):
        return [self._distance(word, vector) for word in words]


class Word2VecTorch(Word2vecGensim):
    def __init__(self, *args):
        super().__init__(*args)

        self.use_cuda = torch.cuda.is_available()

        embed = torch.FloatTensor(self.word2vec.syn0)
        self.embed = embed.cude() if self.use_cuda else embed

        unk_embed = torch.zeros(1, embed.size()[1])
        self.unk_embed = unk_embed.cuda() if self.use_cuda else unk_embed

        self.similarity = nn.CosineSimilarity()

    def distance(self, words, vector):
        """
        Computes words similarities for a given vector.

        :param words: list of strings
        :param vector: FloatTensor
        :return: list of similarities
        """

        # (n_words, embed_length)
        words_tensor = self._vectorize_and_embed(words)
        # (n_words)
        similarity_tensor = 1-self.similarity(words_tensor, vector)
        return similarity_tensor.tolist()

    def text_vector(self, text):
        words = word_tokenize(text)
        # (n_words, embed_length)
        embeds = self._vectorize_and_embed(words)
        # (1, embed_length)
        text_vector = torch.mean(embeds, 0,keepdim=True)
        return text_vector

    def _vectorize_and_embed(self, words):
        # convert to indices
        indices = [self._word_index(word) for word in words]
        # [(1, embed_length)]
        vectors = [self.embed[i].unsqueeze(0) if i != -1 else self.unk_embed for i in indices]
        # (n_words, embed_length)
        embeds = torch.cat(vectors)
        return embeds


