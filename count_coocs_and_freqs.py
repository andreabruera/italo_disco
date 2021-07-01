import collections
import logging
import math
import multiprocessing
import numpy
import os

from scipy import sparse
from tqdm import tqdm

from utils import count_frequencies, count_coocs, prepare_combined_paths, \
                  write_coocs_and_ppmi_to_file

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# Setting up the output folder

output_folder = '/import/cogsci/andrea/github/SISSA-EEG/resources'
os.makedirs(output_folder, exist_ok=True)

combined_paths = prepare_combined_paths()

logging.info('Counting frequencies')
with multiprocessing.Pool() as p:
    counters = p.map(count_frequencies, combined_paths)
    p.terminate()
    p.join()
logging.info('Done counting frequencies')
logging.info('Now merging counters')

final_counter = dict()
for c in counters:
    for k, v in c.items():
        if k not in final_counter.keys():
            final_counter[k] = v
        else:
            final_counter[k] += v
del counters

logging.info('Done merging counters')
logging.info('Vocabulary size: {}'.format(len(final_counter)))

sorted_freqs = sorted(final_counter.items(), key=lambda t: t[1], reverse=True)
counter = {c[0] : c[1] for c in sorted_freqs}

#del final_counter

vocab = dict()
index_counter = dict()

logging.info('Now writing to file word frequencies')
with open(os.path.join(output_folder, 'itwac_and_subs_frequencies.txt'), 'w') as o:
    full_counter = sum([v for k, v in counter.items()])
    o.write('Frequency_rank\t'\
            'Word\t'\
            'Absolute frequency\t'\
            'Relative frequency\t'\
            #'Subsampling probability\t'\
            '(Number of words in total: {})\n'.format(full_counter))

    for i, count in tqdm(enumerate(counter.items())):
        word_rank = i+1
        word = count[0]

        if word_rank > 150000:
            vocab[word] =  0
        else:
            vocab[word] = word_rank
            #subsample_dict[word_rank] = subsampling_prob if word_rank <= 2000000000000 else 1.1
            #subsampling_prob = 1 - math.sqrt(0.00005/relative_frequency)

            absolute_frequency = count[1]
            relative_frequency = float(absolute_frequency) / float(full_counter)
            index_counter[word_rank] = [absolute_frequency, relative_frequency]
            o.write('{}\t{}\t{}\t{}\n'.format(word_rank, \
                                                  word, \
                                                  absolute_frequency, \
                                                  relative_frequency, \
                                                  #subsampling_prob, \
                                                  ))

del final_counter
logging.info('Counting co-occurrences')

cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
for s in tqdm(combined_paths):
    cooc_matrix = count_coocs([s, vocab, cooc_matrix])

logging.info('Done counting co-occurrences')
    
inverted_vocab = {v : k for k, v in vocab.items()}
reduced_vocab = [w for w, i in vocab.items() if i != 0]

logging.info('Writing to file')

for word in tqdm(reduced_vocab):

    index = vocab[word]
    current_word_coocs = cooc_matrix[index].copy()
    del cooc_matrix[index]
    short_folder = word[:3]
    word_out = os.path.join(output_folder,\
                            'cooc_combined_corpora_window_5', \
                            short_folder)
    os.makedirs(word_out, exist_ok=True)

    write_coocs_and_ppmi_to_file([current_word_coocs, \
                         word, \
                         index, \
                         word_out, \
                         full_counter, \
                         inverted_vocab, \
                         index_counter, \
                         ])
