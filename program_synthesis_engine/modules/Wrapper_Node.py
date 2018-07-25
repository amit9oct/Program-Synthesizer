import spacy

class wrapper_node:
    def __init__(self, token, word_similarity, phrase_similarity):
        assert(len(word_similarity) == 3)
        assert(len(phrase_similarity) == 3)
        #spacy tag