import spacy


class wrapper_node:
    def __init__(self, token, word_similarity, phrase_similarity):

        for t in word_similarity:
            assert(len(t) == 3)
        for t in phrase_similarity:
            assert(len(t) == 3)
        #spacy tag

        self.token = token
        self.word_similarity = word_similarity
        self.phrase_similarity = phrase_similarity

    def __str__(self):
        return str(self.token)