import math
import sqlite3

import helpers
import spell_corrector


class sqlite_db_helpers:
    """
    This class has helpers to go through a Database given its name,
    and helper functions to anonymize words in a sentence
    """

    # constant SQL queries
    get_tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
    get_table_schema = "PRAGMA table_info('%s')"
    get_distinct_of_column = "SELECT DISTINCT %s FROM %s ORDER BY %s"
    get_count_of_rows = "SELECT count(*) FROM %s"

    # private dictionaries used internally
    _columns = {}
    _distinct_values = {}

    def init(self, db_name):
        """
        takes name of the database and processes it for anonymization
        """
        # connect to db
        try:
            conn = sqlite3.connect(db_name)
        except:
            print "Error opening db " + db_name
            return

        # get cursor
        try:
            cursor = conn.cursor()
        except:
            print "Error while fetching the cursor"
            return

        ### print "Fetching all tables in the database " + db_name

        for table in cursor.execute(sqlite_db_helpers.get_tables_query).fetchall():
            ### print "Fetching schema of table " + table[0]
            self._columns[table[0]] = []
            self._distinct_values[table[0]] = {}

            # fetch all columns in the table
            columns = cursor.execute(sqlite_db_helpers.get_table_schema % (table[0])).fetchall()

            # fetch number of rows
            count_of_rows = cursor.execute(sqlite_db_helpers.get_count_of_rows % (table[0])).fetchall()[0][0]
            ### print "Total number of rows in " + table[0] + ": " + str(count_of_rows)

            for column in columns:
                # add the column to list
                self._columns[table[0]].append((column[1], column[2], column[5]))

                # Below is schema of returned data
                """
                0 - index of column
                1 - name of column
                2 - type of column
                3 - can the column be null
                4 - default value of column
                5 - whether the column is a primary key
                """

                if column[2] != "TEXT":
                    ### print "Not a text value. Skipping memoization."
                    continue

                # fetch all distinct values
                distinct_val_query = sqlite_db_helpers.get_distinct_of_column % (column[1], table[0], column[1])
                distinct_values = cursor.execute(distinct_val_query).fetchall()

                if self.should_store(column[1], distinct_values.__len__(), count_of_rows):
                    ### print "Adding distinct values: " + str(distinct_values)
                    # add them to cache for later use
                    self._distinct_values[table[0]][column[1]] = distinct_values

                ### print distinct_values

        ### print self._columns

    def should_store(self, column_name, distinct_count, row_count):
        # if number of distinct values is less than number or rows
        # it's probably something matchable
        if distinct_count > 0 and distinct_count < row_count:
            return True
        # let's match names
        if helpers.similarity_score(helpers.to_unicode(column_name), helpers.to_unicode("name")) > 0.2:
            return True

    def get_representative_columns(self, table_name):
        """
        This function should return potential columns that can represent a row
        to a human
        For example, they should return columns like ID, Name, Description
        :param table_name:
        :return:
        """
        to_return = []
        if False == table_name in self._columns.keys():
            print "Table not found: " + table_name
            return to_return

        for column in self._columns[table_name]:

            # add if it's a primary key
            if column[2]:
                to_return.append(column[0])
            elif helpers.similarity_score(helpers.to_unicode(column[0]), helpers.to_unicode("name")) > 0.5:
                to_return.append(column[0])
            elif helpers.similarity_score(helpers.to_unicode(column[0]), helpers.to_unicode("description")) > 0.5:
                to_return.append(column[0])

        return to_return

    def get_matching_table(self, phrase):
        """
        Takes a phrase or word and returns the table that
        potentially contains necessary info
        :param phrase:
        :return:
        """
        to_return = []

        max_score = 0.0
        max_score_table = ""
        corrector = spell_corrector.bing_spell_corrector()
        for table in self._columns.keys():
            corrected_table_name = corrector.spell_correct(table)
            cur_score = helpers.similarity_score(helpers.to_unicode(corrected_table_name), helpers.to_unicode(phrase))
            if cur_score > max_score:
                max_score = cur_score
                max_score_table = table

        return (max_score_table, max_score)

    def get_matching_columns(self, phrase, value, tags=[], table_name=""):
        """
        Goes through all the tables
        Matches with all columns
        Returns potential matches
        :param phrase: phrase for which we are figuring out query
        :param value: value to be looked up in cached data
        :return: list of (table_name, column_name)
        """
        to_return = []

        # it's possible that we get numbers as strings
        if helpers.is_number(value):
            value = float(value)

        # go through all the tables
        for table in self._columns.keys():

            # if a table name is provided, search only in that table
            if table_name.strip() != "" and table != table_name:
                continue

            # go through each column in the table
            found_some_column = False
            for column in self._columns[table]:
                # check if types match
                if type(value) == str and column[1] == "TEXT":
                    # check if it's a perfect match
                    if column[0] in self._distinct_values[table]:
                        match_result = self.match_with_values(self._distinct_values[table][column[0]], value)

                        # sometimes we can have substring in names
                        # in such cases, let's make similarity score 0.5
                        if helpers.similarity_score(helpers.to_unicode(column[0]), helpers.to_unicode("name")) > 0.5 \
                                and any(value in string for string in self._distinct_values[table][column[0]]):
                            if match_result[0] < 0.5:
                                match_result = 0.5

                        if match_result[0] > 0:
                            to_return.append(table, column[0], match_result[0])
                            found_some_column = True

                # TODO::Improve matching logic by considering a small error range
                elif (type(value) == int or type(value) == float) and (column[1] == "INTEGER" or column[1] == "REAL"):
                    if column[0] in self._distinct_values[table]:
                        match_result = self.match_for_numbers(self._distinct_values[table][column[0]], value)
                        if (match_result[0] > 0):
                            to_return.append((table, column[0], match_result[0]))
                            found_some_column = True

            if not found_some_column:
                # find the column which matches the most
                match_score = 0.0
                match_col = ""
                for column in self._columns[table]:
                    col_score = self.match_with_column_name(phrase, value, column[0], tags)
                    # TODO::Refine the filtering logic
                    if col_score > 0 and col_score > match_score:
                        match_score = col_score
                        match_col = column[0]

                to_return.append((table, match_col, match_score))

        return to_return

    def match_for_numbers(self, distinct_values, value):
        match_score = 0.0
        match_value = 0
        for col_value in distinct_values:
            cur_score = (abs(col_value - value) / col_value)
            cur_score = 1 - math.sqrt(cur_score)
            if cur_score > match_score:
                match_score = cur_score
                match_value = col_value

        return (cur_score, match_value)

    def match_with_values(self, distinct_values, value):
        max_score = 0.0
        max_score_val = ""
        for col_value in distinct_values:
            # use spacy's matching index
            cur_score = helpers.similarity_score(col_value, value)
            if cur_score > max_score:
                max_score = cur_score
                max_score_val = col_value
        return (max_score, max_score_val)

    def match_with_column_name(self, phrase, value, column_name, tags=[]):
        """
        Uses NLP similarity to estimate matching index of column and phrase/value
        :param phrase:
        :param value:
        :param column_name:
        :return: a real value indicating match index of phrase/value and column
        """
        bing_corrector = spell_corrector.bing_spell_corrector()
        corrected_name = bing_corrector.spell_correct(column_name)
        # use corrected name to find similarity
        word_similarity = helpers.similarity_score( \
            helpers.to_unicode(corrected_name), \
            helpers.to_unicode(value))

        phrase_similarity = helpers.similarity_score( \
            helpers.to_unicode(corrected_name), \
            helpers.to_unicode(phrase))

        tag_similarity = 0.0
        if tags.__len__() > 0:
            for tag in tags:
                cur_sim = helpers.similarity_score( \
                    helpers.to_unicode(tag), \
                    helpers.to_unicode(corrected_name))
                if cur_sim > tag_similarity:
                    tag_similarity = cur_sim

        return max(word_similarity, phrase_similarity, tag_similarity)


helper = sqlite_db_helpers()
helper.init('..\\..\\tests\\testing.db')
matching_cols = helper.get_matching_columns("employees from chennai", "chennai", tags=["location"])
print matching_cols
print helper.get_representative_columns("Employees")

"""
Schema of table

id          INTEGER PRIMARY KEY
name        TEXT
maker       TEXT
type        TEXT
ram         INTEGER
harddisk    REAL
screensize  REAL
price       REAL
processor   TEXT
graphics    TEXT
resolution  TEXT
"""
