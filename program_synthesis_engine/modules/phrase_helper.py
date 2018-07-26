from db_helpers import *
import spacy
import helpers
from first_order_logic import *
from itertools import permutations
from Wrapper_Node import *

nlp = spacy.load('en_core_web_sm')

line = u'Get all employees who are younger than 15.'
parse_tree = helpers.parse_question(nlp(line))

"""
spacy_entities = []
for ent in line.ents:
    spacy_entities.append([ent.text, ent.label_])
"""

db_helper = sqlite_db_helpers()
db_helper.init('test.db')

def iterate(current_node):
    print current_node

    if current_node is None:
        return

    if isinstance(current_node, spacy.tokens.Token):
        word_matching_cols = db_helper.get_matching_columns(current_node, helpers.to_unicode(str(current_node)))
        phrase_matching_cols = db_helper.get_matching_columns(current_node, u'')
        return wrapper_node(current_node, word_matching_cols, phrase_matching_cols)

    if isinstance(current_node, FirstOrderExpression):
        if current_node.are_all_expressions_tokens():
            phrase_permutations = list(permutations(current_node.expressions))
            phrase_matching_cols = []
            for p in phrase_permutations:
                phrase = u''
                for tok in p:
                    phrase += str(tok) + " "
                    if(phrase in line):
                        print phrase
                        phrase_matching_cols = db_helper.get_matching_columns(phrase, u'')
                        break

            output = []
            for expression in current_node.expressions:
                word_matching_cols = db_helper.get_matching_columns(phrase, helpers.to_unicode(str(expression)))
                output.append(wrapper_node(current_node, word_matching_cols,phrase_matching_cols))
            return FirstOrderExpression(current_node.operator, output)
        else:
            output = []
            for smaller_exp in current_node.expressions:
                output.append(iterate(smaller_exp))
            return FirstOrderExpression(current_node.operator, output)

output = []
for expression in parse_tree.expressions:
    output.append(iterate(expression))

print FirstOrderExpression(parse_tree.operator, output)
# some error in printing
