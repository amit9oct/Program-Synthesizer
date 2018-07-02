import spacy
from spacy import displacy

# This is common global object which is used for computing similarity
nlp = spacy.load('en_core_web_lg')