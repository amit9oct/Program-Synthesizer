import spacy.tokens
from Wrapper_Node import *

class FirstOrderOperators:
    CONJUNCTION = "/\\"
    DISJUNCTION = "\\/"
    NEGATION = "~"
    IMPLICATION = "->"
    EXISTENTIAL = "\\E"  # There exists
    UNIVERSAL = "\\A"  # for every
    OPERATORS = [CONJUNCTION, DISJUNCTION, NEGATION, IMPLICATION, EXISTENTIAL, UNIVERSAL]

    def __init__(self):
        pass


class FirstOrderAtomicExpression:
    def __init__(self, operand1, operator, operator2=None):
        assert operator in FirstOrderOperators.OPERATORS
        assert operand1 is spacy.tokens.Token

        self.operand1 = operand1
        self.operator = operator
        self.operand2 = operator2

    def is_binary(self):
        return self.operand2 is not None

    def is_unary(self):
        return self.operand2 is None

    def print_tree(self):
        if self.is_binary():
            return "(({}) {} ({}))".format(self.operand1, self.operator, self.operand2)
        else:
            return "({} ())".format(self.operator, self.operand1)

    def __str__(self):
        return self.print_tree()


class FirstOrderExpression:
    def __init__(self, operator, expressions):
        assert operator in FirstOrderOperators.OPERATORS
        for expression in expressions:
            assert isinstance(expression, FirstOrderAtomicExpression) or \
                   isinstance(expression, FirstOrderExpression) or \
                   isinstance(expression, spacy.tokens.Token) or \
                   isinstance(expression, wrapper_node)
        if operator == FirstOrderOperators.NEGATION:
            assert len(expressions) == 1
        self.operator = operator
        self.expressions = list(expressions)

    def are_all_expressions_tokens(self):
        return reduce(lambda x, y: isinstance(y, spacy.tokens.Token) and isinstance(x, spacy.tokens.Token), \
                      self.expressions)

    def print_tree(self):
        if len(self.expressions) == 1:
            str_expr = self.expressions[0].print_tree() if isinstance(self.expressions[0], FirstOrderExpression) or \
                                                         isinstance(self.expressions[0], FirstOrderAtomicExpression) \
                else str(self.expressions[0])
            return "[{} ({})]".format(self.operator, str_expr)
        elif self.operator == FirstOrderOperators.NEGATION:
            assert len(self.expressions) == 1, "Negation should have exactly one operand"
            str_expr = self.expressions[0].print_tree() if isinstance(self.expressions[0], FirstOrderExpression) or \
                                                         isinstance(self.expressions[0], FirstOrderAtomicExpression) \
                else str(self.expressions[0])
            return "[{} ({})]".format(self.operator, str_expr)
        elif self.operator == FirstOrderOperators.EXISTENTIAL or \
                self.operator == FirstOrderOperators.UNIVERSAL:
            str_exprs = [self.operator]
            for expr in self.expressions:
                if isinstance(expr, FirstOrderExpression) or isinstance(expr, FirstOrderAtomicExpression):
                    str_exprs.append(expr.print_tree())
                elif isinstance(expr, spacy.tokens.Token):
                    str_exprs.append(str(expr))
                else:
                    raise Exception("FirstOrderExpression got corrupted!!", expr)
            return " ".join(str_exprs)
        elif self.are_all_expressions_tokens():
            str_args = [self.operator] + map(lambda x: str(x), self.expressions)
            return "({})".format(" ".join(str_args))
        else:
            str_exprs = []
            idx = 0
            expr_count = len(self.expressions)
            while idx < expr_count:
                cur = self.expressions[idx]
                if isinstance(cur, spacy.tokens.Token):
                    if idx < expr_count - 1:
                        nex = self.expressions[idx + 1]
                        str_nex = nex.print_tree() if isinstance(nex, FirstOrderExpression) or \
                                                      isinstance(nex, FirstOrderAtomicExpression) else str(nex)
                        if isinstance(nex, FirstOrderAtomicExpression) or isinstance(nex, FirstOrderExpression):
                            str_exprs.append("(({}) {} ({}))".format(str(cur), self.operator, str_nex))
                        else:
                            str_exprs.append("({} {} {})".format(self.operator, str(cur), str_nex))
                        idx += 2
                    else:
                        str_exprs.append("({})".format(cur))
                        idx += 1
                elif isinstance(cur, FirstOrderAtomicExpression) or \
                        isinstance(cur, FirstOrderExpression):
                    str_exprs.append(cur.print_tree())
                    idx += 1
                else:
                    raise Exception("The object FirstOrderExpressions got corrupted")
            return str(" {} ".format(self.operator).join(str_exprs))

    def __str__(self):
        return self.print_tree()


def make_expression(operator, expressions):
    assert operator in FirstOrderOperators.OPERATORS
    assert isinstance(expressions, list)
    if operator == FirstOrderOperators.NEGATION:
        assert len(expressions) == 1, "Negation can have only one operand"
    elif len(expressions) == 1:
        return expressions[0]
    else:
        assert len(expressions) >= 2, "At least two operand expected"

    expression_list = list(expressions)
    return FirstOrderExpression(operator, expression_list)
