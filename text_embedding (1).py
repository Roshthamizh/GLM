# -*- coding: utf-8 -*-
"""TEXT EMBEDDING.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Js0IXTJBepZIk8_twYAFHWzGVf0Pj33x
"""

sentences=["The quick brown fox jumps over the lazy dog.",
        "Machine learning algorithms can significantly enhance data analysis.",
        "Deep learning is a subset of machine learning that focuses on neural networks.",
        "Natural language processing involves analyzing and understanding human language.",
        "Reading books can expand your knowledge and improve your imagination."]

"""TEXT PREPROCESSING"""

import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
def preprocess(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    tokens = text.split()  # Tokenization
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words] #stopwords removal
    return ' '.join(tokens)

sentence = [preprocess(sentence) for sentence in sentences]

print(sentence[:2])

"""SIMILARITY MEASURES

**COSINE SIMILARITY**
"""

from math import sqrt, pow, exp
import numpy as np

def cos_similarity(x,y):
  similarity_matrix = np.dot(x, y.T)
  # Magnitudes of vectors in x and y
  x_magnitudes = np.sqrt(np.sum(x ** 2, axis=1, keepdims=True))
  y_magnitudes = np.sqrt(np.sum(y ** 2, axis=1, keepdims=True))
  cosine_sim_matrix = similarity_matrix / (x_magnitudes * y_magnitudes.T)

  return np.round(cosine_sim_matrix, 3)

"""**EUCLEDIAN DISTANCE**"""

def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2) ** 2))

def compute_pairwise_distances(vectors):
    num_vectors = len(vectors)
    distances = np.zeros((num_vectors, num_vectors))
    for i in range(num_vectors):
        for j in range(num_vectors):
            distances[i, j] = euclidean_distance(vectors[i], vectors[j])
    return distances

def distance_to_similarity(distances):
  return 1/exp(distances)

"""TEXT EMBEDDING

**TF-IDF VECTORIZATION**
"""

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(sentence)

embedding_array = tfidf_matrix.toarray()

feature_names = vectorizer.get_feature_names_out()

embedding_array, feature_names

#  cosine similarity
cosine_sim_tfidf = cos_similarity(tfidf_matrix, tfidf_matrix)

print("Cosine Similarity (TF-IDF):")
print(cosine_sim_tfidf)

# Euclidean distance
euclidean_dist_tfidf= compute_pairwise_distances(embedding_array)
dist_tfidf=distance_to_similarity(euclidean_dist_tfidf)
print("Euclidean Distance (Bag of Words):\n", dist_tfidf)

"""**BAG OF WORDS**"""

from sklearn.feature_extraction.text import CountVectorizer

count_vectorizer = CountVectorizer()

bow_matrix = count_vectorizer.fit_transform(sentence)

bow_array = bow_matrix.toarray()

bow_feature_names = count_vectorizer.get_feature_names_out()

bow_array, bow_feature_names

# cosine similarity
cosine_sim_bow = cos_similarity(bow_array, bow_array)

print("Cosine Similarity (BOW):")
print(cosine_sim_bow)

# Euclidean distances
euclidean_dist_bow = compute_pairwise_distances(bow_array)
dist_bow=distance_to_similarity(euclidean_dist_bow)
print("Euclidean Distance (Bag of Words):\n", dist_bow)

"""CLUSTERING"""

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
sum_of_squared_distances = []
K = range(2, 5)
for k in K:
    km = KMeans(n_clusters=k, random_state=0)
    km = km.fit(tfidf_matrix)
    sum_of_squared_distances.append(km.inertia_)

# Elbow curve
plt.figure(figsize=(8, 5))
plt.plot(K, sum_of_squared_distances, 'bx-')
plt.xlabel('Number of clusters')
plt.ylabel('Sum of squared distances')
plt.title('Elbow Method For Optimal k')
plt.show()

# K-Means using TFIDF vectorized data
num_clusters =3
km = KMeans(n_clusters=num_clusters, random_state=0)
km.fit(tfidf_matrix)

clusters = km.labels_.tolist()

for i, cluster in enumerate(clusters):
    print(f"Sentence {i + 1}: Cluster {cluster}")

# Kmeans clustering using Bag of Words
num_clusters =3
km1 = KMeans(n_clusters=num_clusters, random_state=0)
km1.fit(bow_matrix)

from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(tfidf_matrix.toarray())

df = pd.DataFrame(X_reduced, columns=['PC1', 'PC2'])
df['Cluster'] = km.labels_
df['Sentence'] = sentences

sns.scatterplot(data=df, x='PC1', y='PC2', hue='Cluster', palette='Set1', s=100)
for i in range(len(df)):
    plt.text(df.PC1[i], df.PC2[i], df.Sentence[i], fontsize=12)

plt.title('Sentence Clusters')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title='Cluster')
plt.show()

#  Silhouette Score
# Kmeans clustering using tfidf
from sklearn.metrics import silhouette_score
silhouette_avg = silhouette_score(tfidf_matrix.toarray(), km.labels_)
print(f'Silhouette Score: {silhouette_avg}')

# kmeans clustering for bag of words
silhouette_avg = silhouette_score(bow_matrix.toarray(), km1.labels_)
print(f'Silhouette Score: {silhouette_avg}')

import numpy as np
from scipy.spatial.distance import cdist

def dunn_index(X, labels):
    unique_labels = np.unique(labels)
    num_clusters = len(unique_labels)

    distances = cdist(X, X, 'euclidean')

    min_intercluster_distance = np.inf
    max_intracluster_distance = -np.inf

    for i in range(num_clusters):
        cluster_points = X[labels == i]

        if len(cluster_points) < 2:
            continue
        intra_dist = np.max(cdist(cluster_points, cluster_points, 'euclidean'))
        max_intracluster_distance = max(max_intracluster_distance, intra_dist)

        for j in range(num_clusters):
            if i == j:
                continue
            cluster_points_other = X[labels == j]
            inter_dist = np.min(cdist(cluster_points, cluster_points_other, 'euclidean'))
            min_intercluster_distance = min(min_intercluster_distance, inter_dist)

    if max_intracluster_distance == 0:
        return np.inf
    return min_intercluster_distance / max_intracluster_distance


# Dunn Index for tfidf clustered data
dunn_idx = dunn_index(tfidf_matrix.toarray(), km.labels_)
print(f'Dunn Index: {dunn_idx}')

# Dunn Index for tfidf clustered data
dunn_idx1 = dunn_index(bow_matrix.toarray(), km1.labels_)
print(f'Dunn Index: {dunn_idx1}')

!python -m spacy download en_core_web_md

"""WORD EMBEDDING"""

import spacy
nlp = spacy.load('en_core_web_md')
docs = [nlp(sentences) for sentences in sentence]

print(docs[0].vector)

labels = [headline[:20] for headline in sentence]
def create_heatmap(similarity, cmap = "YlGnBu"):
  df = pd.DataFrame(similarity)
  df.columns = labels
  df.index = labels
  fig, ax = plt.subplots(figsize=(5,5))
  sns.heatmap(df, cmap=cmap)
similarity = []
for i in range(len(docs)):
    row = []
    for j in range(len(docs)):
      row.append(docs[i].similarity(docs[j]))
    similarity.append(row)
create_heatmap(similarity)