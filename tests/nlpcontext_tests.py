from program_synthesis_engine.modules.nlp_context import NlpContext


sample_texts = \
    [
        u'This is a test sentence',
        u"Add two numbers and get it's sum",
        u"A name uniquley identifies a person. Find all person whose name starts with 'S'",
        u'Who is Tom Cruse ?',
        u'Who is Steve Richards ?',
        u'Who is Ramanujam ?',
        u"Find all users who are above average height.",
        u"This is a tree. What is this? "
    ]

for text in sample_texts:
    print "----------------------------------------------------------------"
    print "CONTEXT: {}".format(text)
    print "****************************************************************"
    context = NlpContext(text)
    print context.print_tree()
    print "----------------------------------------------------------------"
    print ""
    print ""
