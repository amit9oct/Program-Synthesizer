import spacy
import spacy.tokens
from first_order_logic import *


def _iter_children_left_right(token):
    assert isinstance(token, spacy.tokens.Token)
    left = [x for x in token.lefts]
    right = [x for x in token.rights]
    left_right = left + right
    children = set([x for x in token.children])
    for ele in left_right:
        if ele in children:
            yield ele


class DependencyParseException(Exception):
    def __str__(self):
        return str(self.message) + " -> \n" + str(self.args)


class Nominals:
    def __init__(self):
        pass

    @staticmethod
    def is_numeric_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "nummod"

    @staticmethod
    def is_adjectival_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "amod"

    @staticmethod
    def is_possession_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "poss"

    @staticmethod
    def is_nominal_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "nmod"

    @staticmethod
    def is_clausal_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "acl"

    @staticmethod
    def is_appositional_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "appos"

    @staticmethod
    def is_determiner(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "det" and \
               (token.tag_ == "DT" or token.tag_ == "WDT" or token.tag_ == "WP")

    @staticmethod
    def is_predeterminer(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "predet" and \
               token.tag_ == "PDT"

    @staticmethod
    def is_compound_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "compound"

    @staticmethod
    def is_relative_clause_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "relcl"

    @staticmethod
    def is_nominal(token):
        return Nominals.is_determiner(token) or \
               Nominals.is_adjectival_modifier(token) or \
               Nominals.is_appositional_modifier(token) or \
               Nominals.is_clausal_modifier(token) or \
               Nominals.is_adjectival_modifier(token) or \
               Nominals.is_compound_modifier(token) or \
               Nominals.is_clausal_modifier(token) or \
               Nominals.is_numeric_modifier(token) or \
               Nominals.is_predeterminer(token) or \
               Nominals.is_possession_modifier(token) or \
               Nominals.is_nominal_modifier(token) or \
               Nominals.is_relative_clause_modifier(token)

    @staticmethod
    def parse_nominal(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Nominals.is_nominal(token)
        if (not Nominals.is_relative_clause_modifier(token)) and (not Nominals.is_clausal_modifier(token)):
            return token
        else:
            if Actions.is_verb(token):
                return Actions.parse_action(token)
            else:
                raise DependencyParseException("Cannot parse Nominal", token)


class Prepositions:
    def __init__(self):
        pass

    @staticmethod
    def is_prepositional_object(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "pobj"

    @staticmethod
    def is_prepositional_complement(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "pcomp"

    @staticmethod
    def is_prepositional(token):
        assert isinstance(token, spacy.tokens.Token)
        return Prepositions.is_prepositional_object(token) or \
               Prepositions.is_prepositional_complement(token)

    @staticmethod
    def parse_prepositional(token):
        assert isinstance(token, spacy.tokens.Token)
        conjunction_args = [token]
        operator = FirstOrderOperators.CONJUNCTION
        if str(token.lemma).lower() == "except":
            operator = FirstOrderOperators.NEGATION
        for child in _iter_children_left_right(token):
            if Noun.is_noun(child):
                conjunction_args.append(Noun.parse_noun(child))
            if Actions.is_verb(child):
                conjunction_args.append(Actions.parse_action(child))
        return make_expression(operator, conjunction_args)

    @staticmethod
    def has_prepositional_ancestor(token):
        assert isinstance(token, spacy.tokens.Token)
        if token.dep_ != "ROOT":
            if token.pos_ == "PREP":
                return True
            else:
                return Prepositions.has_prepositional_ancestor(token.head)
        else:
            return token.pos_ == "PREP"


class Subjects:
    def __init__(self):
        pass

    @staticmethod
    def is_nominal_subject(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "nsubj"

    @staticmethod
    def is_nominal_subject_passive(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "nsubjpass"

    @staticmethod
    def is_clausal_subject(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "csubj"

    @staticmethod
    def is_clausal_subject_passive(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "csubjpass"

    @staticmethod
    def is_agent(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "agent"

    @staticmethod
    def is_expletive(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "expl"

    @staticmethod
    def is_subject(token):
        return Subjects.is_agent(token) or \
               Subjects.is_clausal_subject(token) or \
               Subjects.is_expletive(token) or \
               Subjects.is_nominal_subject(token) or \
               Subjects.is_nominal_subject_passive(token) or \
               Subjects.is_clausal_subject(token)

    @staticmethod
    def parse_subject(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Subjects.is_subject(token)
        conjunct_args = [token]
        for child in _iter_children_left_right(token):
            if Nominals.is_nominal(child):
                conjunct_args.append(Nominals.parse_nominal(child))
            elif Coordination.is_prepositional_modifier(child):
                conjunct_args.append(Prepositions.parse_prepositional(child))
            elif Noun.is_noun(token):
                conjunct_args.append(Noun.parse_noun(token))
            elif Actions.is_verb(token):
                conjunct_args.append(Actions.parse_action(token))
        return make_expression(FirstOrderOperators.CONJUNCTION, conjunct_args)


class Objects:
    def __init__(self):
        pass

    @staticmethod
    def is_direct_object(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "dobj"

    @staticmethod
    def is_dative(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "dative"

    @staticmethod
    def is_attribute(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "attr"

    @staticmethod
    def is_object_predicate(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "oprd"

    @staticmethod
    def is_object(token):
        assert isinstance(token, spacy.tokens.Token)
        return \
            Objects.is_direct_object(token) or \
            Objects.is_dative(token) or \
            Objects.is_attribute(token) or \
            Objects.is_object_predicate(token)

    @staticmethod
    def parse_object(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Objects.is_object(token), "Expected token to be an object (usually a noun phrase)"
        conjunct_args = [token]
        for child in _iter_children_left_right(token):
            if Nominals.is_nominal(child):
                conjunct_args.append(Nominals.parse_nominal(child))
            elif Coordination.is_prepositional_modifier(child):
                conjunct_args.append(Prepositions.parse_prepositional(child))
            elif Noun.is_noun(token):
                conjunct_args.append(Noun.parse_noun(token))
            elif Actions.is_verb(token):
                conjunct_args.append(Actions.parse_action(token))
        return make_expression(FirstOrderOperators.CONJUNCTION, conjunct_args)


class Noun:
    def __init__(self):
        pass

    @staticmethod
    def is_noun(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.pos_ == "NOUN" or token.pos_ == "PROPN"

    @staticmethod
    def is_propn(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.pos_ == "PROPN"

    @staticmethod
    def parse_noun(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Noun.is_noun(token)
        conjunction_args = [] if UnnecessaryWords.is_wh_question(token) else [token]
        for child in _iter_children_left_right(token):
            if Coordination.is_coordinating_conjunction(child) or \
                    UnnecessaryWords.is_punct(child):
                continue
            elif Coordination.is_conjunct(child):
                conjunction_args.append(Coordination.parse_conjunct(child))
            elif Coordination.is_precorrelative_conjunction(token):
                conjunction_args.append(Coordination.parse_preconj(child))
            elif Nominals.is_nominal(child):
                conjunction_args.append(Nominals.parse_nominal(child))
            elif Coordination.is_prepositional_modifier(child):
                conjunction_args.append(Prepositions.parse_prepositional(child))
            else:
                conjunction_args.append( \
                    make_expression(FirstOrderOperators.CONJUNCTION, Adhoc.post_order(child)))
        return make_expression(FirstOrderOperators.CONJUNCTION, conjunction_args)


class Actions:

    def __init__(self):
        pass

    @staticmethod
    def is_root_verb(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "ROOT"

    @staticmethod
    def is_verb(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.pos_ == "VERB"

    @staticmethod
    def is_aux(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "aux" or token.dep_ == "auxpass"

    @staticmethod
    def get_verb_subjects(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Actions.is_verb(token)
        return [tkn for tkn in token.children if Subjects.is_subject(tkn)]

    @staticmethod
    def get_verb_objects(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Actions.is_verb(token)
        return [tkn for tkn in token.children if Objects.is_object(tkn)]

    @staticmethod
    def _parse_verb(token, all_objects, all_subjects):
        assert isinstance(token, spacy.tokens.Token)
        useful_objects = [x for x in all_objects if Objects.is_direct_object(x) or Objects.is_dative(x)]
        useful_subjects = [x for x in all_subjects \
                           if Subjects.is_nominal_subject(x) or \
                           Subjects.is_nominal_subject_passive(x)]
        conjunction_args = [] if Actions.is_aux(token) or UnnecessaryWords.is_ignorable_verb(token) else [token]
        if useful_objects:
            for useful_object in useful_objects:
                conjunction_args.append(Objects.parse_object(useful_object))
        elif useful_subjects:
            for useful_subject in useful_subjects:
                if not UnnecessaryWords.is_wh_question(useful_subject):
                    conjunction_args.append(Subjects.parse_subject(useful_subject))
        else:
            raise DependencyParseException("Don't know how to parse non-direct objects", all_objects)
        for child in _iter_children_left_right(token):
            if Coordination.is_coordinating_conjunction(child) or \
                    UnnecessaryWords.is_punct(child):
                continue
            elif Coordination.is_conjunct(child):
                conjunction_args.append(Coordination.parse_conjunct(child))
            elif Coordination.is_precorrelative_conjunction(token):
                conjunction_args.append(Coordination.parse_preconj(child))
            elif Nominals.is_nominal(child):
                conjunction_args.append(Nominals.parse_nominal(child))
            elif Coordination.is_prepositional_modifier(child):
                conjunction_args.append(Prepositions.parse_prepositional(child))
            elif (child not in useful_objects) and (child not in useful_subjects):
                conjunction_args.append( \
                    make_expression(FirstOrderOperators.CONJUNCTION, Adhoc.post_order(child)))
        return make_expression(FirstOrderOperators.CONJUNCTION, conjunction_args)

    @staticmethod
    def parse_action(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Actions.is_verb(token)
        all_objects = Actions.get_verb_objects(token)
        all_subjects = Actions.get_verb_subjects(token)
        return Actions._parse_verb(token, all_objects, all_subjects)


class Complements:
    def __init__(self):
        pass

    @staticmethod
    def is_clausal_complement(token):
        """
        This generally means this clause has an internal subject
        :return:
        """
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "ccomp"

    @staticmethod
    def is_open_clausal_complement(token):
        """
        This doesn't have any internal subject
        :return:
        """
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "xcomp"

    @staticmethod
    def is_adjective_complement(token):
        """
        This usually modifies the verb
        :return:
        """
        return token.dep_ == "acomp"


class Adverbials:
    def __init__(self):
        pass

    @staticmethod
    def is_adverbial_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "advmod"

    @staticmethod
    def is_adverbial_clause_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "advcl"

    @staticmethod
    def is_noun_phrase_adverbial_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "npmod"


class NegationModifier:
    def __init__(self):
        pass

    @staticmethod
    def is_negation(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "neg"


class Coordination:
    IGNORABLE_CONJUNCTS = {'and', 'or'}

    def __init__(self):
        pass

    @staticmethod
    def is_conjunct(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "conj"

    @staticmethod
    def is_coordinating_conjunction(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "cc"

    @staticmethod
    def is_precorrelative_conjunction(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "preconj"

    @staticmethod
    def is_prepositional_modifier(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.dep_ == "prep"

    @staticmethod
    def is_coordination(token):
        assert isinstance(token, spacy.tokens.Token)
        return Coordination.is_conjunct(token) or \
               Coordination.is_coordinating_conjunction(token) or \
               Coordination.is_precorrelative_conjunction(token) or \
               Coordination.is_prepositional_modifier(token)

    @staticmethod
    def get_cc(token):
        assert isinstance(token, spacy.tokens.Token)
        head_token = token.head
        for tkn in _iter_children_left_right(token):
            if Coordination.is_coordinating_conjunction(tkn):
                return tkn
        if Coordination.is_conjunct(head_token):
            return Coordination.get_cc(head_token)
        else:
            for tkn in _iter_children_left_right(head_token):
                if Coordination.is_coordinating_conjunction(tkn):
                    return tkn
            return Coordination.get_cc(head_token)

    @staticmethod
    def parse_preconj(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Coordination.is_precorrelative_conjunction(token)
        operator = FirstOrderOperators.CONJUNCTION
        conjunct_args = Adhoc.post_order(token)
        return make_expression(operator, conjunct_args)

    @staticmethod
    def parse_conjunct(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Coordination.is_conjunct(token)
        cc = Coordination.get_cc(token)
        assert isinstance(cc, spacy.tokens.Token)
        operator = FirstOrderOperators.CONJUNCTION
        opset = [token]
        for child in _iter_children_left_right(token):
            if UnnecessaryWords.is_punct(child) or \
                    (Coordination.is_coordinating_conjunction(child) and (str(child) in Coordination.IGNORABLE_CONJUNCTS)):
                continue
            elif Coordination.is_conjunct(child):
                opset.append(Coordination.parse_conjunct(child))
            elif Actions.is_verb(child):
                opset.append(Actions.parse_action(child))
            elif Noun.is_noun(child):
                opset.append(Noun.parse_noun(child))
            else:
                opset.append(make_expression(operator, Adhoc.post_order(child)))

        # identify the meaning of conjunction
        if str(cc.lemma_).lower() == "and":
            if Prepositions.has_prepositional_ancestor(token):
                operator = FirstOrderOperators.DISJUNCTION
            else:
                operator = FirstOrderOperators.CONJUNCTION
        elif str(cc.lemma_).lower() == "or":
            operator = FirstOrderOperators.DISJUNCTION
        elif str(cc.lemma_).lower() == "but":
            operator = FirstOrderOperators.NEGATION
            # Conjunct everything before negating it
            opset = [make_expression(FirstOrderOperators.CONJUNCTION, opset)]
        return make_expression(operator, opset)


class Adhoc:
    def __init__(self):
        pass

    @staticmethod
    def post_order(token):
        assert isinstance(token, spacy.tokens.Token)
        post = []
        for child in _iter_children_left_right(token):
            post.extend(Adhoc.post_order(child))
        post.append(token)
        return post


class UnnecessaryWords:
    IGNORABLE_VERB_LEMMA = {'be'}
    IGNORABLE_PREP_LEMMA = {'of', 'in', 'for'}
    IGNORABLE_PUNCT_LEMMA = {',', ':', '.', '?', '"', '`'}

    def __init__(self):
        pass

    @staticmethod
    def is_wh_question(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.tag_ == "WDT" or token.tag_ == "WP" or token.tag_ == "WP$" or token.tag_ == "WRB"

    @staticmethod
    def is_ignorable_verb(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Actions.is_verb(token)
        return str(token.lemma_).lower() in UnnecessaryWords.IGNORABLE_VERB_LEMMA

    @staticmethod
    def is_ignorable_prepositions(token):
        assert isinstance(token, spacy.tokens.Token)
        assert Coordination.is_prepositional_modifier(token)
        return str(token.lemma_).lower() in UnnecessaryWords.IGNORABLE_PREP_LEMMA

    @staticmethod
    def is_punct(token):
        assert isinstance(token, spacy.tokens.Token)
        return token.pos_ == "PUNCT" and \
               (str(token.tag_) in UnnecessaryWords.IGNORABLE_PUNCT_LEMMA)
