import gzip
import os
import sys
import spacy
import json
import tempfile
import webbrowser
import random
from program_synthesis_engine.modules.commonglobals import render_pos_html
nlp = spacy.load('en_core_web_lg')


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

def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)


def write_as_json():
    p = os.path.dirname(sys.argv[0])
    f = open(os.path.join(p, r"qna_test_set\qa_Industrial_and_Scientific.json"), 'w+')
    for l in parse(os.path.join(p, r"qna_test_set\qa_Industrial_and_Scientific.json.gz")):
        f.write(l['question'] + '\n')
    f.close()


# write_as_json()


def analyse_question():
    p = os.path.dirname(sys.argv[0])
    dump_f = open(os.path.join(p, r"qna_test_set\qa_Industrial_and_Scientific_sents.json"), 'w+')
    with open(os.path.join(p, r"qna_test_set\qa_Industrial_and_Scientific.json"), 'r') as f:
        i = 0
        all_lines = {}
        for line in f:
            doc = nlp(u"{}".format(line[:-1]))
            temp = []
            for token in doc:
                if token.pos_ == "NOUN":
                    temp.append({'text': token.text, 'dep': token.dep_})
            all_lines[line] = {'nouns': temp}
        json.dump(all_lines, dump_f)


def sample_question():
    p = os.path.dirname(sys.argv[0])
    with open(os.path.join(p, r"qna_test_set\qa_Industrial_and_Scientific_sents.json"), 'r') as f:
        all_lines = json.load(f)
        print "Got all lines"
        lines = list(all_lines.keys())
        random.shuffle(lines)
        print "Shuffled all lines"
        for line in lines[0:10]:
            print line
            p1 = create_tempfile_and_render(render_pos_html([nlp(u"{}".format(line.strip()))]))


sample_question()
