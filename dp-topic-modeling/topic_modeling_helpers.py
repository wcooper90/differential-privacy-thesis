"""
Preprocessing helper functions for stemming, tokenizing, and lemmatizing email text. 
"""

import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
# from https://github.com/LaurentVeyssier/Topic-Modeling-and-Document-Categorization-using-Latent-Dirichlet-Allocation/blob/main/Latent_dirichlet_allocation.ipynb
# and from https://www.projectpro.io/recipes/save-and-load-lda-model-gensim

def lemmatize_stemming(text):
    stemmer = SnowballStemmer("english")
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    # catch empty contents
    if isinstance(text, float):
        return ""
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            x = lemmatize_stemming(token)
            if x != '':
                result.append(x)
            else:
                continue

    return result
