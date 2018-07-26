from phrase_helper import phrase_helper
import helpers
from commonglobals import nlp
from dependency import *
from first_order_logic import FirstOrderExpression
from Wrapper_Node import wrapper_node


class SqlKeyWords:
    KEYWORDS = {
        'SELECT': {"lexeme": "SELECT", "alias": ['select', 'get', 'list', 'find'], "is_language_construct": True},
        'DISTINCT': {"lexeme": "DISTINCT", "alias": ['distinct', 'unique'], "is_language_construct": True},
        'FROM': {"lexeme": "FROM", "alias": [], "is_language_construct": True},
        'WHERE': {"lexeme": "WHERE", "alias": [], "is_language_construct": True},
        'AND': {"lexeme": "AND", "alias": ['and', 'conjunction'], "is_language_construct": True,
                "num_operands": 2},
        'OR': {"lexeme": "OR", "alias": ['or', 'disjunction'], "is_language_operator": True, "num_operands": 2},
        'NOT': {"lexeme": "NOT", "alias": ['not', 'negation'], "is_language_operator": True, "num_operands": 1},
        'PLUS': {"lexeme": "+", "alias": ['+', 'add', 'sum'], "is_language_operator": True, "num_operands": 2},
        'MINUS': {"lexeme": "-", "alias": ['-', 'subtract', 'difference'], "is_language_operator": True,
                  "num_operands": 2},
        'MULTIPLY': {"lexeme": "*", "alias": ['*', 'multiply', 'product'], "is_language_operator": True,
                     "num_operands": 2},
        'DIVIDE': {"lexeme": "/", "alias": ['/', 'divide'], "is_language_operator": True, "num_operands": 2},
        'CONCAT': {"lexeme": "||", "alias": ['concatenation'], "is_language_operator": True, "num_operands": 2},
        # Comparision Operators
        'EQUALS': {"lexeme": "=", "alias": ['=', 'equals', 'equality'], "is_language_operator": True,
                   "num_operands": 2},
        'NOT_EQUALS': {"lexeme": "!=", "alias": ['not equals'], "is_language_operator": True,
                       "num_operands": 2},
        'LESS_THAN': {"lexeme": "<", "alias": ['less than', 'lesser than'], "is_language_operator": True,
                      "num_operands": 2},
        'LESS_THAN_EQ': {"lexeme": "<=", "alias": ['less than equal to'], "is_language_operator": True,
                         "num_operands": 2},
        'GREATER_THAN': {"lexeme": "<=", "alias": ['greater than', 'more than'], "is_language_operator": True,
                         "num_operands": 2},
        'GREATER_THAN_EQ': {"lexeme": ">=", "alias": ['greater than equal to', 'more than equal to'],
                            "is_language_operator": True, "num_operands": 2},
        'IS_NULL': {"lexeme": "IS NULL", "alias": ['is null', 'null'], "is_language_operator": True,
                    "num_operands": 2},
        'LIKE': {"lexeme": "LIKE", "alias": ['like', 'starts with', 'ends with', 'matches'],
                 "is_language_operator": True, "num_operands": 2},
        'BETWEEN': {"lexeme": "BETWEEN", "alias": ['between', 'from to', 'range'], "is_language_operator": True,
                    "num_operands": 2},
        'IN': {"lexeme": "IN", "alias": ['in'], "is_language_operator": True, "num_operands": 1},
        # Functions
        'ABS': {"lexeme": "ABS", "alias": ['abs', 'absolute'], "is_language_function": True, "num_params": 1},
        'SQRT': {"lexeme": "SQRT", "alias": ['sqrt', 'square root'], "is_language_function": True,
                 "num_params": 1},
        'CONCAT_FUNC': {"lexeme": "CONCAT", "alias": ['concatenate'], "is_language_function": True,
                        "num_params": 1},
        'AVG': {"lexeme": "AVG", "alias": ['average', 'mean', 'expected'], "is_language_function": True,
                "num_params": 1},
        'COUNT': {"lexeme": "COUNT", "alias": ['count', 'number of', 'total number of'], "is_language_function": True,
                  "num_params": 1},
        'MIN': {"lexeme": "MIN", "alias": ['min', 'minimum', 'least', 'lowest'], "is_language_function": True,
                "num_params": 1},
        'MAX': {"lexeme": "MAX", "alias": ['max', 'maximum', 'highest'], "is_language_function": True,
                "num_params": 1},
        'STDDEV': {"lexeme": "STDDEV", "alias": ['standard deviation', 'deviation'], "is_language_function": True,
                   "num_params": 1},
        'SUM': {"lexeme": "SUM", "alias": ['sum', 'total', 'sum total'], "is_language_function": True,
                "num_params": 1},
        'VARIANCE': {"lexeme": "VARIANCE", "alias": ['variance'], "is_language_function": True, "num_params": 1}
    }


class SqlGrammar:
    grammar_rules = []


class SqlGenerator:
    def __init__(self, db_path):
        """
        Initialize it with a FirstOrderExpression
        """
        self.db_path = db_path
        self.phrase_helper = phrase_helper(self.db_path)

    def get_table_names(self, wrapped_tree_expression, top=1):
        """
        :return: Iterates through the wrapped tree
        """
        assert isinstance(wrapped_tree_expression, FirstOrderExpression)
        list_nodes = self.flatten_tree(wrapped_tree_expression)
        tables = {}
        cnts = {}
        for node in list_nodes:
            assert isinstance(node, wrapper_node)
            if Noun.is_noun(node.token):
                phrase_similarities = node.phrase_similarity
                for phrase_similarity in phrase_similarities:
                    tables[phrase_similarity[0]] = phrase_similarity[2] if phrase_similarity[0] not in tables else \
                        tables[phrase_similarity[0]] + phrase_similarity[2]
                    cnts[phrase_similarity[0]] = 1 if phrase_similarity[0] not in cnts else cnts[phrase_similarity[
                        0]] + 1
        # Normalized the probabilities
        tuples = [(tables[key] / cnts[key], key) for key in tables.keys()]
        tuples.sort()
        tuples.reverse()
        return [x[1] for x in tuples[:min(top, len(tuples))]]

    def get_column_names(self, wrapped_tree_expression, tables, top=3):
        assert isinstance(wrapped_tree_expression, FirstOrderExpression)
        assert isinstance(tables, set)
        list_nodes = self.flatten_tree(wrapped_tree_expression)
        cols = {}
        cols_info = {}
        cnts = {}
        for node in list_nodes:
            assert isinstance(node, wrapper_node)
            if Noun.is_noun(node.token) or \
                    ((not helpers.is_root(node.token)) and \
                     (not Nominals.is_nominal(node.token)) and \
                     (Coordination.is_prepositional_modifier(node.token) and not UnnecessaryWords.is_ignorable_prepositions(node.token))):
                phrase_similarities = node.phrase_similarity
                for phrase_similarity in phrase_similarities:
                    if phrase_similarity[0] in tables:
                        cols[phrase_similarity[1]] = phrase_similarity[2] if phrase_similarity[1] not in cols else \
                            cols[phrase_similarity[1]] + phrase_similarity[2]
                        cols_info[phrase_similarity[1]] = phrase_similarity
                        cnts[phrase_similarity[1]] = 1 if phrase_similarity[1] not in cnts else cnts[phrase_similarity[
                            1]] + 1
        # Normalized the probabilities
        tuples = [(cols[key] / cnts[key], cols_info[key]) for key in cols.keys()]
        tuples.sort()
        tuples.reverse()
        if tuples:
            return [x[1] for x in tuples[:min(top, len(tuples))]]
        else:
            return []

    def get_wrapped_tree(self, first_order_expression):
        assert isinstance(first_order_expression, FirstOrderExpression)
        return self.phrase_helper.get_wrapped_tree(first_order_expression)

    def flatten_tree(self, wrapped_tree_expression):
        assert isinstance(wrapped_tree_expression, FirstOrderExpression)
        post = []
        for expr in wrapped_tree_expression.expressions:
            if isinstance(expr, FirstOrderExpression):
                post.extend(self.flatten_tree(expr))
            else:
                post.append(expr)
        return post


def __main__():
    sql_gen = SqlGenerator('..\\..\\tests\\testing.db')
    parsed_question = helpers.parse_question(nlp(u'Get all employees who are younger than 15.'))
    wrapped_tree = sql_gen.get_wrapped_tree(parsed_question)
    table_names = sql_gen.get_table_names(wrapped_tree)
    column_names = sql_gen.get_column_names(wrapped_tree, {table_names[0]}, 5)
    print (table_names, column_names)


__main__()
