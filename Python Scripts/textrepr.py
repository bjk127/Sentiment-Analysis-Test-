from sklearn.feature_extraction.text import TfidfVectorizer
import Glassdoor

def Tfidf_extractor(docs, n_features=300):
    vectorizer = TfidfVectorizer(max_df=0.75, min_df=0.01, max_features=n_features)
    docs1 = [ Glassdoor.lemmatize_text(doc) for doc in docs ]
    matrix = vectorizer.fit_transform(docs1)

    return matrix

