from commonglobals import nlp


def similarity_score(word1, word2):
    """
    This returns the similarity between two words in isolation.
    :param word1: First Unicode word
    :param word2: Second Unicode word
    :return: Floating point score for similarity between the given two words
    """
    return nlp(word1).similarity(nlp(word2))
