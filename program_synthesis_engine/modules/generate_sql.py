from helpers import *
from dependency import *
from first_order_logic import FirstOrderOperators, FirstOrderExpression


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
    def __init__(self, first_order_expression):
        """
        Initialize it with a FirstOrderExpression
        """
        assert isinstance(first_order_expression, FirstOrderExpression)
        self.first_order_tree = first_order_expression
