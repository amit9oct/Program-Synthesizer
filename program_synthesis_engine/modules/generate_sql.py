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
    @staticmethod
    def get_all_operators():
        for key in SqlKeyWords.KEYWORDS.keys():
            if ('is_language_operator' in SqlKeyWords.KEYWORDS[key]) and \
                    (SqlKeyWords.KEYWORDS[key]['is_language_operator']):
                yield SqlKeyWords.KEYWORDS[key]

    @staticmethod
    def get_all_language_construct():
        for key in SqlKeyWords.KEYWORDS.keys():
            if 'is_language_construct' in SqlKeyWords.KEYWORDS[key] and \
                    (SqlKeyWords.KEYWORDS[key]['is_language_construct']):
                yield SqlKeyWords.KEYWORDS[key]

    @staticmethod
    def get_all_functions():
        for key in SqlKeyWords.KEYWORDS.keys():
            if 'is_language_function' in SqlKeyWords.KEYWORDS[key] and \
                    (SqlKeyWords.KEYWORDS[key]['is_language_function']):
                yield SqlKeyWords.KEYWORDS[key]


class SqlGrammarHelper:
    OPERATOR_ALIAS_TOKENS = [(op["lexeme"], [nlp(helpers.to_unicode(x)) for x in op['alias']]) for op in
                             SqlGrammar.get_all_operators()]
    FUNCTION_ALIAS_TOKENS = [(fun["lexeme"], [nlp(helpers.to_unicode(x)) for x in fun['alias']]) for fun in
                             SqlGrammar.get_all_functions()]


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
            if SqlGenerator.is_useful_node(node):
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
            if SqlGenerator.is_useful_node(node):
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

    def get_possible_where_expressions(self, wrapped_expression, tables=[]):
        """
        :param wrapped_expression:
        :return: List of tuples containing the central token and the sql expression according to that token.
        """
        assert isinstance(wrapped_expression, FirstOrderExpression)
        list_nodes = self.flatten_tree(wrapped_expression)
        token_node_map = dict([(node.token, node) for node in list_nodes])
        useful_nodes = [x for x in list_nodes if SqlGenerator.is_useful_node(x)]
        operators = SqlGrammarHelper.OPERATOR_ALIAS_TOKENS
        functions = SqlGrammarHelper.FUNCTION_ALIAS_TOKENS

        dates = []
        money = []
        quantity = []
        ordinal = []
        geo_political = []
        cardinal = []
        percent = []
        ent_time = []
        other_loc = []
        # filter out different types of entities
        for node in useful_nodes:
            assert isinstance(node, wrapper_node)
            if node.ent_iob == "B" or node.ent_iob == "I":
                if phrase_helper.is_ent_date(node.ent_tag):
                    dates.append(node)
                elif phrase_helper.is_ent_money(node.ent_tag):
                    money.append(node)
                elif phrase_helper.is_ent_quantity(node.ent_tag):
                    quantity.append(node)
                elif phrase_helper.is_ent_ordinal(node.ent_tag):
                    ordinal.append(node)
                elif phrase_helper.is_ent_geo_political(node.ent_tag):
                    geo_political.append(node)
                elif phrase_helper.is_cardinal(node.ent_tag):
                    cardinal.append(node)
                elif phrase_helper.is_ent_percent(node.ent_tag):
                    percent.append(node)
                elif phrase_helper.is_ent_time(node.ent_tag):
                    ent_time.append(node)
                elif phrase_helper.is_ent_loc(node.ent_tag):
                    other_loc.append(node)

        column_op_ent_triplet = []
        for node in money + quantity + cardinal:
            # Find out adjectives closest to the numeric filters
            if node.token.pos_ == "NUM":
                closest_adjs = [token_node_map[adj] for adj in Adjective.get_closest_adjectives(node.token)]
                closest_nouns = [token_node_map[noun] for adj in Noun.get_closest_adjectives(node.token)]
                [self.phrase_helper.db_helper.get_column_info(table) for table in tables]
        # Find out matching operators to the adjectives
        # Find out operator aliases closest to the string filters
        # If there is no close matching adjective then  Equals is the operator
        adjective_nodes = [x for x in useful_nodes if Adjective.is_adjective(x.token)]

        # Filter number and dates
        operator_similarity_scores = [(node.token,
                                       operator[0],  # Just take the lexeme
                                       max(map(lambda op_alias: helpers.similarity_score(node.token, op_alias),
                                               operator[1])))  # Take maximum of score out of all possible alias\
                                      for operator in operators for node in list_nodes if
                                      SqlGenerator.is_useful_node(node)]
        functions_similarity_scores = [(node.token,
                                        fun[0],  # Just take the lexeme
                                        max(map(lambda fun_alias: helpers.similarity_score(node.token, fun_alias),
                                                fun[1])))  # Take maximum of score out of all possible alias\
                                       for fun in functions for node in list_nodes if
                                       SqlGenerator.is_useful_node(node)]
        return operator_similarity_scores + functions_similarity_scores

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

    @staticmethod
    def is_useful_node(node):
        assert isinstance(node, wrapper_node)
        return Noun.is_noun(node.token) or \
               ((not helpers.is_root(node.token)) and
                (not Nominals.is_nominal(node.token)) and
                (not Coordination.is_prepositional_modifier(node.token) or
                 not UnnecessaryWords.is_ignorable_prepositions(node.token)))

    def get_sqlite_phrase(self, table_name, triplet_list, tree):
        """
        :param triplet_list:
        :param tree:
        :return:
        """
        if isinstance(tree, FirstOrderExpression):
            child_queries = []
            # concatenate the nodes with right operator
            for node in tree:
                cur_query = self.get_sqlite_phrase(triplet_list, node)
                # add only if it isn't empty
                if cur_query != "":
                    child_queries.append(cur_query)

            final_query = ""
            cur_operator = self.get_sqlite_operator(tree.operator)
            if child_queries.__len__() > 1:
                final_query = cur_operator.join(child_queries)
            return final_query
        else:
            # currently only tokens are supported
            matching_triplet = self.get_matching_triplet(triplet_list, tree)
            if matching_triplet:
                col_info = self.phrase_helper.db_helper.get_column_info(table_name, matching_triplet[0])
                if col_info[1] == "INTEGER" or col_info[1] == "REAL":
                    return "(" + col_info[0] + " " + matching_triplet[1] + " " + matching_triplet[2].token.text + ")"
                else:
                    return "(" + col_info[0] + " " + matching_triplet[1] + " '" + matching_triplet[2].token.text + "')"
            else:
                return ""

    def get_sqlite_operator(self, fo_operator):
        if fo_operator == FirstOrderOperators.CONJUNCTION:
            return " AND "
        elif fo_operator == FirstOrderOperators.DISJUNCTION:
            return " OR "
        else:
            # default it to and
            return " AND "

    def get_matching_triplet(self, triplet_list, node):
        assert isinstance(node, wrapper_node)
        for triplet in triplet_list:
            if node == triplet[2]:
                return triplet
        return None

def print_on_screen(something):
    print something


def __main__():
    sql_gen = SqlGenerator('..\\..\\tests\\testing.db')
    parsed_question = helpers.parse_question(nlp(u'Get all employees who are younger than 15.'))
    wrapped_tree = sql_gen.get_wrapped_tree(parsed_question)
    table_names = sql_gen.get_table_names(wrapped_tree)
    column_names = sql_gen.get_column_names(wrapped_tree, {table_names[0]}, 5)
    similarities = sql_gen.get_possible_where_expressions(wrapped_tree)
    print table_names
    print column_names
    [print_on_screen((str(similarity[0]), similarity[1], similarity[2])) for similarity in similarities]


__main__()
