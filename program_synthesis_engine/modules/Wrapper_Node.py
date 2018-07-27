import spacy
import spacy.tokens


class wrapper_node:
    def __init__(self, token, word_similarity, phrase_similarity):
        assert isinstance(token, spacy.tokens.Token)
        for t in word_similarity:
            assert(len(t) == 3)
        for t in phrase_similarity:
            assert(len(t) == 3)

        self.token = token
        self.word_similarity = word_similarity
        self.phrase_similarity = phrase_similarity
        self.ent_tag = self.token.ent_type_
        self.ent_iob = self.token.ent_iob_  # "B" means begins the entity, "I" means inside the entity, "O" outside entity, "" means no ent tagging

    def __str__(self):
        return str(self.token)