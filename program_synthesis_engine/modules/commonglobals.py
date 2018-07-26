import spacy
import textacy
from spacy import displacy, tokens
from textacy import extract

# This is common global object which is used for computing similarity
# Some private members so as to make it work
nlp = spacy.load('en_core_web_sm')
lang_en = textacy.load_spacy('en_core_web_sm')
possible_docs = {'textacy', 'spacy'}
subjects = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
objects = ["dobj", "dative", "attr", "oprd"]
conjunctions = ["or", "and"]


def render_pos_html(list_of_docs):
    return displacy.render(map(lambda x: get_spacy_doc(x), list_of_docs), style='dep', page=True)


def get_new_doc(phrase, doc_type='textacy'):
    assert isinstance(phrase, basestring)
    assert isinstance(doc_type, str)
    assert doc_type in possible_docs, "Only {} doc types are supported".format(possible_docs)

    if doc_type == 'textacy':
        return textacy.Doc(phrase, lang=lang_en)
    elif doc_type == 'spacy':
        return nlp(phrase)


def get_spacy_doc(doc):
    if isinstance(doc, textacy.Doc):
        return doc.spacy_doc
    elif isinstance(doc, spacy.tokens.Doc):
        return doc


def get_subs_from_conjunctions(subs):
    more_subs = []
    for sub in subs:
        # rights is a generator
        rights = list(sub.rights)
        right_deps = {tok.lower_ for tok in rights}
        if "and" in right_deps:
            more_subs.extend([tok for tok in rights if tok.dep_ in subjects or tok.pos_ == "NOUN"])
            if len(more_subs) > 0:
                more_subs.extend(get_subs_from_conjunctions(more_subs))
    return more_subs


def get_objs_from_conjunctions(objs):
    more_objs = []
    for obj in objs:
        # rights is a generator
        rights = list(obj.rights)
        right_deps = {tok.lower_ for tok in rights}
        if "and" in right_deps:
            more_objs.extend([tok for tok in rights if tok.dep_ in objects or tok.pos_ == "NOUN"])
            if len(more_objs) > 0:
                more_objs.extend(get_objs_from_conjunctions(more_objs))
    return more_objs


def get_verbs_from_conjunctions(verbs):
    moreVerbs = []
    for verb in verbs:
        rightDeps = {tok.lower_ for tok in verb.rights}
        if "and" in rightDeps:
            moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
            if len(moreVerbs) > 0:
                moreVerbs.extend(get_verbs_from_conjunctions(moreVerbs))
    return moreVerbs


def find_subs(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
        head = head.head
    if head.pos_ == "VERB":
        subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
        if len(subs) > 0:
            verbNegated = is_negated(head)
            subs.extend(get_subs_from_conjunctions(subs))
            return subs, verbNegated
        elif head.head != head:
            return find_subs(head)
    elif head.pos_ == "NOUN":
        return [head], is_negated(tok)
    return [], False


def is_negated(tok):
    negations = {"no", "not", "n't", "never", "none"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False


def find_svs(tokens):
    svs = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
    for v in verbs:
        subs, verbNegated = get_all_subs(v)
        if len(subs) > 0:
            for sub in subs:
                svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
    return svs


def get_objs_from_prepositions(deps):
    objs = []
    for dep in deps:
        if dep.pos_ == "ADP" and dep.dep_ == "prep":
            objs.extend(
                [tok for tok in dep.rights if tok.dep_ in objects or (tok.pos_ == "PRON" and tok.lower_ == "me")])
    return objs


def get_objs_from_attrs(deps):
    for dep in deps:
        if dep.pos_ == "NOUN" and dep.dep_ == "attr":
            verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
            if len(verbs) > 0:
                for v in verbs:
                    rights = list(v.rights)
                    objs = [tok for tok in rights if tok.dep_ in objects]
                    objs.extend(get_objs_from_prepositions(rights))
                    if len(objs) > 0:
                        return v, objs
    return None, None


def get_obj_from_xcomp(deps):
    for dep in deps:
        if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
            v = dep
            rights = list(v.rights)
            objs = [tok for tok in rights if tok.dep_ in objects]
            objs.extend(get_objs_from_prepositions(rights))
            if len(objs) > 0:
                return v, objs
    return None, None


def get_all_subs(v):
    verbNegated = is_negated(v)
    subs = [tok for tok in v.lefts if tok.dep_ in subjects and tok.pos_ != "DET"]
    if len(subs) > 0:
        subs.extend(get_subs_from_conjunctions(subs))
    else:
        foundSubs, verbNegated = find_subs(v)
        subs.extend(foundSubs)
    return subs, verbNegated


def get_all_objs(v):
    # rights is a generator
    rights = list(v.rights)
    objs = [tok for tok in rights if tok.dep_ in objects]
    objs.extend(get_objs_from_prepositions(rights))

    # potentialNewVerb, potentialNewObjs = getObjsFromAttrs(rights)
    # if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
    #    objs.extend(potentialNewObjs)
    #    v = potentialNewVerb

    potentialNewVerb, potentialNewObjs = get_obj_from_xcomp(rights)
    if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        objs.extend(potentialNewObjs)
        v = potentialNewVerb
    if len(objs) > 0:
        objs.extend(get_objs_from_conjunctions(objs))
    return v, objs


def find_svos(tokens):
    svos = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
    for v in verbs:
        subs, verbNegated = get_all_subs(v)
        # hopefully there are subs, if not, don't examine this verb any longer
        if len(subs) > 0:
            v, objs = get_all_objs(v)
            for sub in subs:
                for obj in objs:
                    objNegated = is_negated(obj)
                    svos.append((sub.lower_, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj.lower_))
    return svos


def get_named_entities(doc):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    return extract.named_entities(doc)


def get_noun_chunk(doc):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    return extract.noun_chunk(doc)


def get_pos_regex_matches(doc, pattern):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    assert isinstance(pattern, basestring), "The pattern should be a string"
    return extract.pos_regex_matches(doc, pattern)


def get_semi_structured_statements(doc, entity, cue='be'):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    assert isinstance(entity, basestring)
    assert isinstance(cue, basestring)
    return extract.semistructured_statements(doc, entity, cue)


def get_textacy_subject_verb_object_triples(doc):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    return extract.subject_verb_object_triples(doc)


def get_acronyms_and_definitions(doc, known_acro_defs=None):
    assert isinstance(doc, textacy.Doc) or isinstance(doc, spacy.tokens.Doc), "Only {} are supported".format(
        possible_docs)
    return extract.acronyms_and_definitions(doc, known_acro_defs)
