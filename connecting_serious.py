import MySQLdb
import Stemmer
from nltk import word_tokenize
import re
from nltk.corpus import stopwords

db = MySQLdb.connect(user="***", passwd="***", db="repetition_db", use_unicode=True, charset='utf8mb4')

c = db.cursor()

#print(results[:5], len(results))

reg_exp_words = re.compile('\W+')
stemming = Stemmer.Stemmer("russian")
stop_words = stopwords.words("russian")
stop_words = stemming.stemWords(stop_words)

sentences_to_add = ["Что я делал, дорогие россияне?", "Почему я иду, или не иду?"]
stem_adder = 0

source, year, name, author = None, None, None, None

c.execute("""select max(text_id) from repetition_db.sentence""")
text_id = int(c.fetchall()[0][0]) + 1

c.execute("""select max(meta_id) from repetition_db.metadata""")
meta_id = int(c.fetchall()[0][0]) + 1

for sent_ind, sentence in enumerate(sentences_to_add):
    tokens = word_tokenize(sentence.lower())
    stems = stemming.stemWords(tokens)
    repetitions = {}
    strings_to_write = []

    c.execute("""select max(repetition_id) from repetition_db.wordform""")
    repetitions_max = int(c.fetchall()[0][0])

    c.execute("""select max(stem_id) from repetition_db.wordform""")
    stem_max = int(c.fetchall()[0][0])

    c.execute("""select max(wordform_id) from repetition_db.wordform""")
    wordform_max = int(c.fetchall()[0][0])

    c.execute("""select max(sent_id) from repetition_db.wordform""")
    sent_id = int(c.fetchall()[0][0]) + 1

    for cur_ind, stem in enumerate(stems):
        if reg_exp_words.search(stem) or stem in stop_words:
            pass

        else:
            for step_ind, elem in enumerate(stems):
                if cur_ind != step_ind:
                    if stem == elem:

                        if stem not in repetitions:
                            repetitions[stem] = {cur_ind, step_ind}
                        else:
                            current_repetitions = repetitions[stem]
                            current_repetitions.add(cur_ind)
                            current_repetitions.add(step_ind)
                            repetitions[stem] = current_repetitions

        c.execute("""select * from repetition_db.stem where stem = %s""", (stem,))
        results = c.fetchall()
        try:
            stem_id = int(results[0][0])

        except IndexError:
            stem_id = stem_max + 1
            stem_max += 1
            c.execute(
                """INSERT INTO stem (stem_id, stem)
              VALUES (%s, %s)""",
                (stem_id, stem)
            )

        wordform_id = wordform_max + cur_ind + 1

        strings_to_write.append([wordform_id, sent_id, stem_id, None, tokens[cur_ind], 'nil', cur_ind + 1])

    for ind, value in enumerate(repetitions.values()):
        repetition_id = repetitions_max + ind + 1

        for ident in value:
            strings_to_write[ident][3] = repetition_id

    if sent_ind == 0:
        c.execute(
        """INSERT INTO texts (text_id)
      VALUES (%s)""",
          (text_id,))

        c.execute(
        """INSERT INTO metadata (meta_id, text_id, source, year, name, author)
        VALUES (%s, %s, %s, %s, %s, %s)""",
            (meta_id, text_id, source, year, name, author)
        )

    c.execute(
        """INSERT INTO sentence (sent_id, text_id)
    VALUES (%s, %s)""",
        (sent_id, text_id)
    )

    for string in strings_to_write:
        c.execute(
            """INSERT INTO wordform (wordform_id, sent_id, stem_id, repetition_id, wordform, gram_cat, pos_in_sent)
          VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (string)
            )
    db.commit()

c.close()
db.close()