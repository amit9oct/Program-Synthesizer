import os
import sqlite3

import helpers
import spell_corrector
import helpers


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
        print "Current working directory " + os.getcwd()
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

        print "Fetching all tables in the database " + db_name

        for table in cursor.execute(sqlite_db_helpers.get_tables_query).fetchall():
            print "Fetching schema of table " + table[0]
            self._columns[table[0]] = []
            self._distinct_values[table[0]] = {}

            # fetch all columns in the table
            columns = cursor.execute(sqlite_db_helpers.get_table_schema % (table[0])).fetchall()

            # fetch number of rows
            count_of_rows = cursor.execute(sqlite_db_helpers.get_count_of_rows % (table[0])).fetchall()[0][0]
            print "Total number of rows in " + table[0] + ": " + str(count_of_rows)

            for column in columns:
                # add the column to list
                self._columns[table[0]].append((column[1], column[2]))

                # fetch all distinct values
                distinct_val_query = sqlite_db_helpers.get_distinct_of_column % (column[1], table[0], column[1])
                distinct_values = cursor.execute(distinct_val_query).fetchall()

                if column[2] != "TEXT":
                    print "Not a text value. Skipping memoization."
                    continue

                if count_of_rows > distinct_values.__len__():
                    print "Adding distinct values: " + str(distinct_values)
                    self._distinct_values[table[0]][column[1]] = distinct_values

                # add them to cache for later use
                print distinct_values
                """
                0 - index of column
                1 - name of column
                2 - type of column
                3 - can the column be null
                4 - default value of column
                5 - whether the column is a primary key
                """

        print self._columns

    def get_matching_columns(self, phrase, value):
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
            # go through each column in the table
            found_some_column = False
            for column in self._columns[table]:
                # check if types match
                if type(value) == str and column[1] == "TEXT":
                    # check if it's a perfect match
                    if column[0] in self._distinct_values[table] and \
                            value in self._distinct_values[table][column[0]]:
                        # it's a perfect match
                        to_return.append((table, column[0], 1))
                        found_some_column = True

                    elif column[0] in self._distinct_values[table] and \
                            any(value in string for string in self._distinct_values[table][column[0]]):
                        # it's an imperfect match
                        # TODO::Add better logic here based on string lengths, matching length, context, etc.
                        # scope for improvement
                        to_return.append((table, column[0], 0.5))
                        found_some_column = True

                # TODO::Improve matching logic by considering a small error range
                elif (type(value) == int or type(value) == float) and (column[1] == "INT" or column[1] == "REAL"):
                    if column[0] in self._distinct_values[table] and \
                            value in self._distinct_values[table][column[0]]:
                        # perfect match
                        to_return.append((table, column[0], 1))
                        found_some_column = True

            if not found_some_column:
                # find the column which matches the most
                match_score = 0.0
                match_col = ""
                for column in self._columns[table]:
                    col_score = self.match_with_column_name(phrase, value, column[0])
                    # TODO::Refine the filtering logic
                    if col_score > 0 and col_score > match_score:
                        match_score = col_score
                        match_col = column[0]

                to_return.append((table, match_col, match_score))

        return to_return

    def match_with_column_name(self, phrase, value, column_name):
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
        word_similarity = helpers.similarity_score(\
            helpers.to_unicode(corrected_name), \
            helpers.to_unicode(value))

        phrase_similarity = helpers.similarity_score( \
            helpers.to_unicode(corrected_name), \
            helpers.to_unicode(phrase))

        return max(word_similarity, phrase_similarity)


helper = sqlite_db_helpers()
helper.init('test.db')
matching_cols1 = helper.get_matching_columns(u'cheaper than 30000', u'30000')
matching_cols2 = helper.get_matching_columns(u'', u'')
print matching_cols1
print matching_cols2
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