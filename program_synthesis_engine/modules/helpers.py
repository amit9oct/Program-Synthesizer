import spacy.tokens

from commonglobals import nlp
from dependency import *
from first_order_logic import *

subjects = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
objects = ["dobj", "dative", "attr", "oprd"]
conjunctions = ["or", "and"]


def similarity_score(word1, word2):
    """
    This returns the similarity between two words in isolation.
    :param word1: First Unicode word
    :param word2: Second Unicode word
    :return: Floating point score for similarity between the given two words
    """
    return nlp(word1).similarity(nlp(word2))


def dump_object(obj):
    """
    This method dumps the various attributes of the object
    :param obj: The given object
    :return: returns nothing
    """
    for attr in dir(obj):
        print ("obj.%s = %r" % (attr, getattr(obj, attr)))


def is_root(token):
    assert isinstance(token, spacy.tokens.Token)
    return token.dep_ == "ROOT"


def get_root(doc):
    assert isinstance(doc, spacy.tokens.Doc)
    for tkn in doc:
        if is_root(tkn):
            return tkn
    return None


def get_starting_token(doc):
    assert isinstance(doc, spacy.tokens.Doc)
    return doc[0]


def is_question(doc):
    assert isinstance(doc, spacy.tokens.Doc)
    start_token = get_starting_token(doc)
    # Check if it is WH question
    if start_token.tag_ == "WDT" or \
            start_token.tag_ == "WP" or \
            start_token.tag_ == "WP$" or \
            start_token.tag_ == "WRB":
        return True
    root_token = get_root(doc)
    # Check if root token is the start token and it is verb
    if start_token == root_token and root_token.pos_ == "VERB":
        return True
    return False


def get_all_paths(doc):
    assert isinstance(doc, spacy.tokens.Doc)
    root_token = get_root(doc)
    return _get_all_paths(root_token)


def _get_all_paths(token):
    assert isinstance(token, spacy.tokens.Token)
    ans = []
    for tkn in token.children:
        lsts = _get_all_paths(tkn)
        for lst in lsts:
            ans.append([token] + lst)
    if not ans:
        ans.append([token])
    return ans


def parse_question(doc):
    """
    :param doc: Returns list of tokens, when returns None it means it is not a valid question
    :return:
    """
    assert isinstance(doc, spacy.tokens.Doc)
    if is_question(doc):
        # Get the distinct object
        root_element = get_root(doc)
        return Actions.parse_action(root_element)
    return None


def to_unicode(string):
    if isinstance(string, basestring):
        if type(string) is unicode:
            return string
        else:
            return string.decode("utf-8", "ignore")
    else:
        return str(string).decode("utf-8", "ignore")



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
