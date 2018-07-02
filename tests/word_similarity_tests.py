from program_synthesis_engine.modules.helpers import similarity_score


def print_and_assert_similarity(word1, word2, expected_similarity, cmp_symbol='>'):
    similarity = similarity_score(word1, word2)
    print "Word Similarity for {} and {} = {}. Expected similarity {} {}".format(word1, word2, similarity, cmp_symbol,
                                                                                 expected_similarity)
    statement = eval("{} {} {}".format(similarity, cmp_symbol, expected_similarity))
    assert statement, "Doesn't match the expected similarity"
    return similarity


print_and_assert_similarity(u"younger", u"age", 0.5, '>')
print_and_assert_similarity(u"Younger", u"Age", 0.5, '>')
print_and_assert_similarity(u"younger", u"Age", 0.5, '>')
print_and_assert_similarity(u"Younger", u"age", 0.5, '>')
younger_less1 = print_and_assert_similarity(u"Younger", u"less than", 0, '>')
younger_greater1 = print_and_assert_similarity(u"Younger", u"greater than", 0, '>')
assert younger_greater1 < younger_less1, "Couldn't understand younger"
younger_less2 = print_and_assert_similarity(u"Younger", u"less", 0, '>')
younger_greater2 = print_and_assert_similarity(u"Younger", u"more", 0, '>')
assert younger_greater1 < younger_less1, "Couldn't understand younger"
print_and_assert_similarity(u"younger", u"name", 0.5, '<=')
print_and_assert_similarity(u"Younger", u"Name", 0.5, '<=')
print_and_assert_similarity(u"younger", u"person", 0.5, '<=')
print_and_assert_similarity(u"Younger", u"height", 0.5, '<=')

location_name = print_and_assert_similarity(u"Location", u"name", 0, '>')
location_banana = print_and_assert_similarity(u"Location", u"banana", 0, '>')
location_city = print_and_assert_similarity(u"Location", u"city", 0, '>')
location_delhi = print_and_assert_similarity(u"Location", u"Delhi", 0, '>')
loc_arr = [location_banana, location_city, location_delhi, location_city]
assert location_banana == min(loc_arr), "Banana is not least related"
assert location_city >= max(loc_arr), "City is not getting related to location"
