from db_helpers import *
import spacy.tokens
import helpers
from first_order_logic import *
from itertools import permutations
from Wrapper_Node import *
from commonglobals import nlp


class phrase_helper:
    def __init__(self, db_path):
        self.db_helper = sqlite_db_helpers(db_path)
        self.db_helper.init()

    def iterate(self, current_node):

        if current_node is None:
            return

        if isinstance(current_node, spacy.tokens.Token):
            possible_ent = current_node.ent_type_
            tag = []
            if current_node.ent_iob_ == "B" or current_node.ent_iob_ == "I":
                tag.append(phrase_helper.get_ent_meaning(possible_ent))
            word_matching_cols = self.db_helper.get_matching_columns(helpers.to_unicode(str(current_node)),
                                                                     helpers.to_unicode(str(current_node)),
                                                                     tags=tag)
            phrase_matching_cols = self.db_helper.get_matching_columns(helpers.to_unicode(str(current_node)),
                                                                       u'',
                                                                       tags=tag)
            return wrapper_node(current_node, word_matching_cols, phrase_matching_cols)

        if isinstance(current_node, FirstOrderExpression):
            if current_node.are_all_expressions_tokens():
                phrase_permutations = list(permutations(current_node.expressions))
                phrase_matching_cols = []
                phrase = u''
                assert isinstance(current_node.expressions[0], spacy.tokens.Token)
                original_sent = str(current_node.expressions[0].doc)
                for perm in phrase_permutations:
                    phrase = helpers.to_unicode(" ".join([str(x) for x in perm]))
                    if phrase in original_sent:
                        phrase_matching_cols = self.db_helper.get_matching_columns(phrase, u'')
                        break

                output = []
                for expression in current_node.expressions:
                    assert isinstance(expression, spacy.tokens.Token)
                    tag = [phrase_helper.get_ent_meaning(expression.ent_type_)] if expression.ent_iob_ == "B" or \
                                                                                   expression.ent_iob_ == "I" or \
                                                                                   expression.ent_iob_ == "O" else []
                    word_matching_cols = self.db_helper.get_matching_columns(phrase,
                                                                             helpers.to_unicode(str(expression)),
                                                                             tags=tag)
                    output.append(wrapper_node(expression, word_matching_cols, phrase_matching_cols))
                return FirstOrderExpression(current_node.operator, output)
            else:
                output = []
                for smaller_exp in current_node.expressions:
                    output.append(self.iterate(smaller_exp))
                return FirstOrderExpression(current_node.operator, output)

    def get_wrapped_tree(self, parse_tree):
        output = []
        for expression in parse_tree.expressions:
            output.append(self.iterate(expression))
        return FirstOrderExpression(parse_tree.operator, output)

    @staticmethod
    def get_ent_meaning(ent_short):
        return spacy.explain(ent_short)


def __main__():
    line = u'Get all employees who are younger than 15.'
    parse_tree = helpers.parse_question(nlp(line))
    phelper = phrase_helper('..\\..\\tests\\testing.db')
    wrapped_tree = phelper.get_wrapped_tree(parse_tree)
    print wrapped_tree

#__main__()