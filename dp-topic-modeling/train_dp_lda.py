"""
Use a differentially private method to train an LDA topic model. Details on
the private algorithm are from Zhu et al., "Privacy-preserving topic model for tagging recommender system"
"""
from nltk.stem.porter import *
from gensim import corpora, models
import numpy as np
import pandas as pd
import nltk
import gensim
import time
import string
from random import sample
from tqdm import tqdm
import json

# internal code
from topic_model_helpers import preprocess


# columns of interest
column_names = ['id',  # email id
                'content', # the content itself
                'subject', # the subject
                ]

# time each algorithm
s = time.time()
# read df from csv
df = pd.read_csv("../dataframes/full_email_tm_df.csv", usecols=column_names)
e = time.time()
t = e - s
num_docs = len(df)
print("reading df took " + str(round(t, 4)) + " seconds. ")
print("number of emails in loaded df: " + str(num_docs))


s = time.time()
# topic_column = 'subject'
topic_column = 'content'

document_limit = None
docs = None
if document_limit is not None:
    docs = list(df[topic_column][:document_limit])
else:
    docs = list(df[topic_column])


# can also choose to take a random sample of the docs
training_proportion = 0.01
docs = sample(docs, int(num_docs * training_proportion))

# from https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                        filename='./logs/lda.log', filemode = "w+")


# create sets of stopwords from local text files
first_names = set([])
f = open("../content-stopwords/first-names.txt", "r")
for x in f:
    first_names.add(x.lower().strip())
f.close()
house_names = set([])
f = open("../content-stopwords/house-names.txt", "r")
for x in f:
    house_names.add(x.lower().strip())
f.close()
thousand_common_words = set([])
f = open("../content-stopwords/1000-common-words.txt", "r")
for x in f:
    thousand_common_words.add(x.lower().strip())
f.close()
uninformative_stopwords = set([])
f = open("../content-stopwords/uninformative-stopwords.txt", "r")
for x in f:
    uninformative_stopwords.add(x.lower().strip())
f.close()

# Tokenize the documents
from nltk.tokenize import RegexpTokenizer
# Remove empty doc strings
docs = [doc for doc in docs if not isinstance(doc, float)]
# Split the documents into tokens
for idx in range(len(docs)):
    docs[idx] = docs[idx].lower()  # Convert to lowercase.
    # use string splitting to manually remove custom stopwords
    words = docs[idx].split()
    filtered_words = []
    for word in words:
        # remove punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))
        # remove house names
        if word in house_names:
            continue
        # remove common first names
        elif word in first_names:
            continue
        # remove the 1000 most common words in the english language
        elif word in thousand_common_words:
            continue
        # remove specific uninformative stopwords found in previous trained models
        elif word in uninformative_stopwords:
            continue
        else:
            filtered_words.append(word)

    # rejoin filtered words and preprocess using gensim
    docs[idx] = (' ').join(filtered_words)
    docs[idx] = preprocess(docs[idx])


# Compute bigrams
from gensim.models import Phrases
# Add bigrams and trigrams to docs (only ones that appear 20 times or more).
bigram = Phrases(docs, min_count=20)
for idx in range(len(docs)):
    for token in bigram[docs[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            docs[idx].append(token)

# Remove rare and common tokens
from gensim.corpora import Dictionary
# Create a dictionary representation of the documents
dictionary = Dictionary(docs)
# Filter out words that occur less than 75 documents, or more than 5% of the documents
# dictionary.filter_extremes(no_below=75, no_above=0.05)
dictionary.filter_extremes(no_below=2, no_above=0.05)

# Bag-of-words representation of the documents
bow_corpus = [dictionary.doc2bow(doc) for doc in docs]
print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(bow_corpus))
e = time.time()
t = e - s
print("Full preprocessing of data took " + str(round(t, 4)) + " seconds." )


# number of topics K
K = 15
# number of iterations for training loop
ITERATIONS = 15
# LDA training hyperparameters
ALPHA = 0.1
BETA = 0.001
# privacy loss parameter
EPSILON = 1


# initialize dictionary to keep track of how many times a word
# is labeled under a particular topic
word_topic_occurrences = {val:{k:0 for k in range(K)} for val in list(dictionary.values())}
NUM_WORDS = len(list(word_topic_occurrences.keys()))

def initialize_word_topic_assignments():
    initial_word_topic_assignments = {}
    for idx in range(len(docs)):
        initial_word_topic_assignments[idx] = {}
        for token in docs[idx]:
            # the token may have been filtered out by the dictionary object. If so, ignore
            if token not in word_topic_occurrences:
                continue
            initial_word_topic_assignments[idx][token] = np.random.randint(K)
    return initial_word_topic_assignments


word_topic_assignments = initialize_word_topic_assignments()

def count_word_topic_occurrences():
    for doc in word_topic_assignments:
        for word in word_topic_assignments[doc]:
            # the token may have been filtered out by the dictionary object. If so, ignore
            if word not in word_topic_occurrences:
                continue
            curr_topic_assignment = word_topic_assignments[doc][word]
            word_topic_occurrences[word][curr_topic_assignment] += 1

count_word_topic_occurrences()


iters = 0
s = time.time()
for iters in tqdm(range(ITERATIONS)):
    logging.info("Iteration: {iter}".format(iter=iters))
    iter_s = time.time()
    num_reassignments = 0

    # do this summing calculation in an outer loop to save time. Only needs to be updated once per training iteration
    summed_words_per_topic = {k:0 for k in dictionary.keys()}
    for word in word_topic_occurrences:
        for k in range(K):
            summed_words_per_topic[k] += word_topic_occurrences[word][k]

    # iterate through each document
    for d, doc in enumerate(docs):

        # do this summing calculation in an outer loop to save time. Only needs to be updated once per doc iteration
        d_words_per_topic = {k:0 for k in dictionary.keys()}
        for word in word_topic_assignments[d]:
            topic = word_topic_assignments[d][word]
            d_words_per_topic[topic] += 1
        # iterate through each token in the doc
        for j in range(len(doc)):
            # token j we are examining
            token = doc[j]
            # the token may have been filtered out by the dictionary object. If so, ignore
            if token not in word_topic_occurrences:
                continue
            # token's topic to be updated
            prev_topic = word_topic_assignments[d][token]
            # total number of words in the d'th document
            # have to use bow_corpus instead of 'doc' because doc has words which may have been filtered out by dictionary
            n_d = len(bow_corpus[d])
            # initialize optimization values
            best_p_w_given_k_and_d = 0
            best_topic = prev_topic

            for k in range(K):
                # number of words in the d'th document with assigned topic k
                n_dk = d_words_per_topic[k]
                # we ignore the current word in the calculation
                if word_topic_assignments[d][token] == k:
                    n_dk -= 1
                # probability of document d being assigned to topic k
                p_k_given_d = (n_dk + ALPHA) / (n_d - 1 + K * ALPHA)
                # number of times token j is assigned to topic k
                m_jk = word_topic_occurrences[token][k]
                # total number of words assigned to topic k
                n_k = summed_words_per_topic[k]
                # probability of a word occurring in topic k
                p_w_given_k = (m_jk + BETA) / (n_k + NUM_WORDS * BETA)
                # probability of word occurring for particular document and topic
                p_w_given_k_and_d = p_k_given_d * p_w_given_k

                if p_w_given_k_and_d > best_p_w_given_k_and_d:
                    best_p_w_given_k_and_d = p_w_given_k_and_d
                    best_topic = k


            if best_topic != prev_topic:
                # reassign the token's topic based on maximization in inner loop
                word_topic_assignments[d][token] = best_topic
                # update word occurrences
                word_topic_occurrences[token][prev_topic] -= 1
                word_topic_occurrences[token][best_topic] += 1
                # update reassignment counter
                num_reassignments += 1

    iter_e = time.time()
    iter_t = round(iter_e - iter_s, 4)
    print("Iteration {iter} finished in {t} seconds with {n} new reassignments.".format(iter=iters, t=iter_t, n=num_reassignments))


e = time.time()
t = round(e - s, 4)
print("Training the LDA model took {t} seconds. ".format(t=t))

# synthesize model data
final_topics = {k:{} for k in range(K)}
sum_words_for_each_k = {k:0 for k in range(K)}
# calculate the sum of words in each topic
for word in word_topic_occurrences:
    for k in final_topics.keys():
        final_topics[k][word] = word_topic_occurrences[word][k]
        sum_words_for_each_k[k] += word_topic_occurrences[word][k]

# find proportion of words in each topic and sort them
for k in final_topics.keys():
    for word in final_topics[k]:
        final_topics[k][word] = round(final_topics[k][word] / sum_words_for_each_k[k], 4)
    final_topics[k] = {k: v for k, v in sorted(final_topics[k].items(), key=lambda item: item[1], reverse=True)}


saved_words = {}
# print final topics results and associated tags
for k in final_topics.keys():
    print("*"*80)
    print("Topic number {topic_num}: ".format(topic_num=k))
    counter = 0
    saved_words_k = {}
    for val in final_topics[k]:
        print("{word}: {percentage}".format(word=val, percentage=final_topics[k][val]))
        saved_words_k[val] = final_topics[k][val]
        counter += 1
        if counter > 20:
            break
    saved_words[k] = saved_words_k



# For the last training iteration, add Laplacian noise and make final reassignments
num_reassignments = 0
# current sum of words per topic
summed_words_per_topic = {k:0 for k in dictionary.keys()}
for word in word_topic_occurrences:
    for k in range(K):
        summed_words_per_topic[k] += word_topic_occurrences[word][k]

# iterate through each document
for d, doc in enumerate(docs):
    # do this summing calculation in an outer loop to save time
    d_words_per_topic = {k:0 for k in dictionary.keys()}
    for word in word_topic_assignments[d]:
        topic = word_topic_assignments[d][word]
        d_words_per_topic[topic] += 1
    # iterate through each token in the doc
    for j in range(len(doc)):
        # token j we are examining
        token = doc[j]
        # the token may have been filtered out by the dictionary object. If so, ignore
        if token not in word_topic_occurrences:
            continue
        # token's topic to be updated
        prev_topic = word_topic_assignments[d][token]
        # total number of words in the d'th document
        n_d = len(bow_corpus[d])
        # initialize optimization values
        best_p_w_given_k_and_d = 0
        best_topic = prev_topic
        for k in range(K):
            # number of words in the d'th document with assigned topic k
            n_dk = d_words_per_topic[k]
            # we ignore the current word in the calculation
            if word_topic_assignments[d][token] == k:
                n_dk -= 1
            # sample laplacian noise
            l1 = np.random.laplace(scale=2/EPSILON)
            l2 = np.random.laplace(scale=2/EPSILON)
            # probability of document d being assigned to topic k, with laplacian noise
            p_k_given_d = (n_dk + l1 + ALPHA) / (n_d - 1 - l1 + K * ALPHA)
            # number of times token j is assigned to topic k
            m_jk = word_topic_occurrences[token][k]
            # total number of words assigned to topic k
            n_k = summed_words_per_topic[k]
            # probability of a word occurring in topic k
            p_w_given_k = (m_jk + l2 + BETA) / (n_k - l2 + NUM_WORDS * BETA)
            # probability of word occurring for particular document and topic
            p_w_given_k_and_d = p_k_given_d * p_w_given_k

            # update local best
            if p_w_given_k_and_d > best_p_w_given_k_and_d:
                best_p_w_given_k_and_d = p_w_given_k_and_d
                best_topic = k

        if best_topic != prev_topic:
            # reassign the token's topic based on maximization in inner loop
            word_topic_assignments[d][token] = best_topic
            # update word occurrences
            word_topic_occurrences[token][prev_topic] -= 1
            word_topic_occurrences[token][best_topic] += 1
            # update reassignment counter
            num_reassignments += 1



print("Number of final reassignments with Laplacian noise: {n}".format(n=num_reassignments))

# synthesize model data
final_topics = {k:{} for k in range(K)}
sum_words_for_each_k = {k:0 for k in range(K)}
# calculate the sum of words in each topic
for word in word_topic_occurrences:
    for k in final_topics.keys():
        final_topics[k][word] = word_topic_occurrences[word][k]
        sum_words_for_each_k[k] += word_topic_occurrences[word][k]

# find proportion of words in each topic and sort them
for k in final_topics.keys():
    for word in final_topics[k]:
        final_topics[k][word] = round(final_topics[k][word] / sum_words_for_each_k[k], 4)
    final_topics[k] = {k: v for k, v in sorted(final_topics[k].items(), key=lambda item: item[1], reverse=True)}


saved_words = {}
# print final topics results and associated tags
for k in final_topics.keys():
    print("*"*80)
    print("Topic number {topic_num}: ".format(topic_num=k))
    counter = 0
    saved_words_k = {}
    for val in final_topics[k]:
        print("{word}: {percentage}".format(word=val, percentage=final_topics[k][val]))
        saved_words_k[val] = final_topics[k][val]
        counter += 1
        if counter > 20:
            break
    saved_words[k] = saved_words_k


# save results
with open('./dp_lda_model_results.txt', 'w') as file:
     file.write(json.dumps(saved_words))
