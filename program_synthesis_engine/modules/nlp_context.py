from commonglobals import nlp


class NlpContext:
    def __init__(self, phrase):
        """
        This class isolates the internals getting implemented in any NLP library
        :type phrase: str
        """
        assert isinstance(phrase, basestring)
        self.phrase = phrase
        self.doc = nlp(phrase)

    @property
    def tokens(self):
        """
        :return: Returns the individual tokens for the parsed phrase
        """
        return [token for token in self.doc]

    @property
    def compressed_tree(self):
        """
        It returns a compact version of the parsed tree.
        :return: Array of tuples which contains relationship info between the individual tokens and
        their corresponding head tokens.
        """
        return [(token.pos_, token.text, token.dep_, token.head.text, token.head.pos_) for token in self.doc]

    def print_tree(self):
        for printable in self.compressed_tree:
            print printable
