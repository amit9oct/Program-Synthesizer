import spacy
from spacy import displacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

text =  u'Get all users whose age is less than 15'
sqlQuery = ["" for x in range(8)]
sqlQuery[0] = u'SELECT UserId from UserDetailsTable where Age < 15'
sqlQuery[1] = u'SELECT UserId from UserDetailsTable where Age > 15'
sqlQuery[2] = u'SELECT * from UserDetailsTable where Age < 15'
sqlQuery[3] = u'SELECT LastLogin, Age from UserDetailsTable where UserId == 15'
sqlQuery[4] = u'SELECT UserId from UserDetailsTable where Sex == \'Male\''
sqlQuery[5] = u'SELECT Age from UserDetailsTable where UserId == 15'
sqlQuery[6] = u'SELECT Age from UserDetailsTable where UserId == 1'
sqlQuery[7] = u'SELECT LastLogin from UserDetailsTable where Sex == \'Male\''

schema1 = ["UserName", "UserId", "LastLogin", "Sex"]
schema2 = ["UserId","Age"]
schema2 = ["FirstName", "LastName"]
text1 = u'Get all female users who are younger than 15'
text2 = u'List all people whose FirstName starts with Ravi.'
doc = nlp(text)
displacy.serve(doc, style='dep')
context =  nlp(text)

for token in context:
	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)

i = 0
print text
while i < 7:
	print(sqlQuery[i], '->' , context.similarity(nlp(sqlQuery[i])))
	i += 1
	pass