import spacy
import spacy.tokens
import program_synthesis_engine.modules.helpers as helpers

nlp = spacy.load('en_core_web_lg')


def test_get_subjects():
    doc = nlp(u'Ram and Shyam are best friends')
    all_subs = list(helpers.get_verb_subjects(doc[3]))  # and
    print all_subs


def test_get_starting_token():
    doc = nlp(u'Get all employees who are younger than 15')
    start_token = helpers.get_starting_token(doc)
    print start_token
    assert str(start_token) == "Get", "Starting sentence not matching"


def test_get_root_token():
    doc1 = nlp(u'Get all employees who are younger than 15')
    doc2 = nlp(u'Find all employees who are younger than 15')
    doc3 = nlp(u'List the employees who are shorter than 5 feet')
    doc4 = nlp(u'Which employees have age less than 20 ?')
    doc5 = nlp(u'Who are the most rich employees ?')
    doc6 = nlp(u'What are the most expensive t-shirts available in the market ?')
    doc7 = nlp(u'Where is Chandani Chowk located ?')
    print doc1, helpers.get_root(doc1)
    print doc2, helpers.get_root(doc2)
    print doc3, helpers.get_root(doc3)
    print doc4, helpers.get_root(doc4)
    print doc5, helpers.get_root(doc5)
    print doc6, helpers.get_root(doc6)
    print doc7, helpers.get_root(doc7)


def test_is_question():
    doc1 = nlp(u'Get all employees who are younger than 15')
    doc2 = nlp(u'Find all employees who are younger than 15')
    doc3 = nlp(u'List the employees who are shorter than 5 feet')
    doc4 = nlp(u'Which employees have age less than 20 ?')
    doc5 = nlp(u'Who are the most rich employees ?')
    doc6 = nlp(u'What are the most expensive t-shirts available in the market ?')
    doc7 = nlp(u'Where is Chandani Chowk located ?')
    doc8 = nlp(u'Ravi and Kavi are best.')
    doc9 = nlp(u'I hope this helps.')
    doc10 = nlp(u'Micheal goes to school.')
    doc11 = nlp(u'Sum of two any two sides of a triangle is greater than the third side of the triangle')
    print doc1, helpers.is_question(doc1)
    print doc2, helpers.is_question(doc2)
    print doc3, helpers.is_question(doc3)
    print doc4, helpers.is_question(doc4)
    print doc5, helpers.is_question(doc5)
    print doc6, helpers.is_question(doc6)
    print doc7, helpers.is_question(doc7)
    print doc8, helpers.is_question(doc8)
    print doc9, helpers.is_question(doc9)
    print doc10, helpers.is_question(doc10)
    print doc11, helpers.is_question(doc11)


def print_token(token):
    assert isinstance(token, spacy.tokens.Token)
    return "({},pos = {},dep = {},tag = {})".format(str(token), token.pos_, token.dep_, token.tag_)


def split_on_conj():
    l = [u'Get all employees who are younger than 15 and are males', \
         u'Find all employees who are taller than 15 cm but weigh less than 100 kg', \
         u'Get list of cakes which have calories greater than 15 kCal and less than 40 kCal', \
         u'Get all employees who have annual income in the range from Rs 1000 to Rs 5000', \
         u'Get salaries of Suresh, Phani and Venkatesh', \
         u'Find all employees younger than 25 and older than 20 and living in Delhi', \
         u'Find all female employees who are younger than 25 and older than 20 and living in Delhi', \
         u'Which employees have more height than the average height ?']
    for line in l:
        all_paths = helpers.get_all_paths(nlp(line))
        print line
        # for p in all_paths:
        #     tab = "    "
        #     print "{}{}".format(tab, p)
        #     for tkn in p:
        #         print "{}{}{}".format(tab, tab, print_token(tkn))
        print helpers.parse_question(nlp(line))
        print "*************************************************************"


# test_get_starting_token()
# test_get_root_token()
# test_is_question()
split_on_conj()
