import Stemmer
from nltk import word_tokenize
import re
from nltk.corpus import stopwords
import time

start_time = time.time()

stemming = Stemmer.Stemmer("russian")

with open("sentences.txt", encoding='utf-8') as opener:
    sentences = []
    for line in opener:
        string = line.strip()
        sentences.append(string)
print("Elapsed time for loading: {:.3f} sec".format(time.time() - start_time))

reg_exp_words = re.compile('\W+')
stop_words = stopwords.words("russian")
stop_words = stemming.stemWords(stop_words)

stems_ids = []

for sentence in sentences:
    stems = stemming.stemWords(word_tokenize(sentence.lower()))

    for stem in stems:
        if stem in stems_ids:
            pass
        else:
            stems_ids.append(stem)

print("Elapsed time for stem_table: {:.3f} sec".format(time.time() - start_time))
"""
with open('stem_table.csv', 'w', encoding='utf-8') as stem_writer:
    stem_writer.write("stem_id\tstem\n")
    for ind, stem in enumerate(stems_ids):
        stem_writer.write("%d\t%s\n" % (ind+1, stem))"""

header = '\t'.join("wordform_id sent_id stem_id repetition_id wordform gram_cat pos_in_sent\n".split(' '))
wordform_id_counter = 0
repetition_id_counter = 1

with open('wordform_table.csv', 'w', encoding='utf-8') as wordform_writer:
    wordform_writer.write(header)

    for sent_ind, sentence in enumerate(sentences):
        tokens = word_tokenize(sentence.lower())
        stems = stemming.stemWords(tokens)
        repetitions = {}
        strings_to_write = []

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
            stem_id = 1 + stems_ids.index(stem)
            #rep_id = 0
            #wordform_writer.write("%d\t%d\t%d\t%d\t%s\t%s\t%d\n" % (wordform_id_counter+cur_ind+1, sent_ind+1, stem_id,
            #                                                        rep_id, tokens[cur_ind], "nil", cur_ind+1))
            strings_to_write.append([str(wordform_id_counter+cur_ind+1), str(sent_ind+1), str(stem_id), "nope"
                                        , tokens[cur_ind], 'nil', str(cur_ind+1)])
        for value in repetitions.values():
            for ident in value:
                strings_to_write[ident][3] = str(repetition_id_counter)
            repetition_id_counter += 1

        strings_to_write = ['\t'.join(string)+'\n' for string in strings_to_write]
        wordform_writer.write(''.join(strings_to_write))
        wordform_id_counter += len(stems)

#str(wordform_id_counter+cur_ind+1)\tstr(sent_ind+1)\tstr(stem_id)\tstr(rep_id)\ttokens[cur_ind]\t"nil"\tstr(cur_ind+1).split('\t)
print("Elapsed time for wordform_table: {:.3f} sec".format(time.time() - start_time))