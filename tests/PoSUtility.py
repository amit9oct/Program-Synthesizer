import os
import sys
import tempfile
import webbrowser

from program_synthesis_engine.modules.commonglobals import \
    render_pos_html, \
    get_textacy_subject_verb_object_triples, \
    get_semi_structured_statements, \
    get_pos_regex_matches, \
    get_noun_chunk, \
    nlp
from program_synthesis_engine.modules.helpers import dump_object


def create_tempfile_and_render(content, frmt=".html"):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    p = tmp.name + frmt
    try:
        f = open(p, 'w')
        f.write(content)
        f.flush()
        f.close()
        webbrowser.open('file://' + os.path.realpath(p))
    except:
        print "Something went wrong {}".format(sys.exc_info()[0])
        raise
    return p


while True:
    # Take input and decode it into utf8 as spacy takes in only utf-8
    inp = raw_input("Enter Sentence:").decode('utf8')
    doc = nlp(inp)
    p1 = create_tempfile_and_render(render_pos_html([doc]))
#    svo = "Subject verb Object for {} is:\r\n".format(inp)\
#        .join(map(lambda x: str(x), get_subject_verb_object_triples(doc)))
#    print svo
#    p2 = create_tempfile_and_render(svo, ".txt")
    print list(get_textacy_subject_verb_object_triples(doc))
    raw_input("Press enter to continue")
    os.remove(p1)
#    os.remove(p2)
