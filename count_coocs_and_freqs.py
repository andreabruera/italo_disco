import logging
import multiprocessing
import os

from tqdm import tqdm

from utils import count_frequencies, count_coocs

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# Setting up the output folder

output_folder = '/import/cogsci/andrea/github/SISSA-EEG/resources'
os.makedirs(output_folder, exist_ok=True)

# Setting up the input paths

'''
logging.info('Loading ItWac files')
itwac_path = '/import/cogsci/andrea/dataset/corpora/itwac_lemma_reorganized'
assert os.path.exists(itwac_path)

itwac_paths = [os.path.join(root, f) for root, direct, files in os.walk(itwac_path) for f in files]
'''
logging.info('Loading OpenSubtitles files')
subs_path = '/import/cogsci/andrea/dataset/corpora/open_subtitles_cleaned'
assert os.path.exists(subs_path)

subs_paths = [os.path.join(root, f) for root, direct, files in os.walk(subs_path) for f in files]
'''

paths = itwac_paths.copy() + subs_paths.copy()

del subs_paths
del itwac_paths
'''

logging.info('Counting frequencies')
with multiprocessing.Pool() as p:
    counters = p.map(count_frequencies, subs_paths)
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

counter = {c[0] : c[1] for c in sorted(final_counter.items(), key=lambda t: t[1], reverse=True)}
del final_counter

vocab = dict()

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
        absolute_frequency = count[1]

        vocab[word] = word_rank if word_rank <= 20000000000 else 0
        #subsample_dict[word_rank] = subsampling_prob if word_rank <= 2000000000000 else 1.1
        #subsampling_prob = 1 - math.sqrt(0.00005/relative_frequency)

        relative_frequency = float(absolute_frequency) / float(full_counter)
        o.write('{}\t{}\t{}\t{}\n'.format(word_rank, \
                                              word, \
                                              absolute_frequency, \
                                              relative_frequency, \
                                              #subsampling_prob, \
                                              ))

logging.info('Counting co-occurrences')
with multiprocessing.Pool() as p:
    coocs = p.map(count_coocs, [[s, vocab] for s in subs_paths])
    p.terminate()
    p.join()
logging.info('Done counting co-occurrences')
logging.info('Now merging co-occurrences')

final_coocs = dict()
for plain_coocs in coocs:

    for k_one, v_one in plain_coocs.items():
        if k_one not in final_coocs.keys():
            final_coocs[k_one] = dict()
        for k_two, v_two in v_one.items():
            if k_two not in final_coocs[k_one].keys():
                final_coocs[k_one][k_two] = v_two
            else:
                final_counter[k_one][k_two] += v_two
del coocs
logging.info('Done merging co-occurrences')

import pdb; pdb.set_trace()
