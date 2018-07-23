import spacy.tokens
from nlp_context import NlpContext
from networkx import DiGraph


def add_node(digraph, token):
    assert isinstance(digraph, DiGraph)
    assert isinstance(token, spacy.tokens.Token)
    digraph.add_node(WordSemantic(token))


def add_edge(digraph, node1, edge, node2):
    assert isinstance(digraph, DiGraph)
    assert isinstance(node1, spacy.tokens.Token)
    assert isinstance(node2, spacy.tokens.Token)
    assert isinstance(edge, spacy.tokens.Token)
    digraph.add_edges_from(WordSemantic(node1), WordSemantic(node2), \
                           edge_name=str(edge.text), \
                           edge_info=WordSemantic(edge))


class WordSemantic:
    def __init__(self, token):
        assert isinstance(token, spacy.tokens.Token), "Only spacy token allowed"
        self.word_prop = token
        self.word_info = {}  # Empty dictionary

    def __hash__(self):
        return self.word_prop.__hash__()

    def __eq__(self, other):
        assert isinstance(other, WordSemantic)
        return self.word_prop == self.word_prop

    def __str__(self):
        return str(self.word_prop.text)


class Semantics:
    def __init__(self, nlp_context):
        assert isinstance(nlp_context, NlpContext)
        self.nlp_context = nlp_context
        self._digraph = None

    @property
    def graph(self):
        if self._digraph is not None:
            return self._digraph
        else:
            return None
