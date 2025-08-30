import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Shaurya is learning Python and Machine Learning.")
print([token.lemma_ for token in doc])
