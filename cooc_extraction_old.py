import os
import math
import random
import spacy
import re
import string
import collections
import tqdm
import argparse
import multiprocessing
import logging

from tqdm import tqdm

from file_reader import itWacReader, itWikiReader

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', required=True, choices=['itwac', 'wikipedia_italian'], \
                       help='indicates which corpus to use, whether \'itwac\' or \'wikipedia_italian\'')
parser.add_argument('--input_path', required=True, type=str, help='Folder where the corpus files are to be found')
parser.add_argument('--output_path', required=True, type=str, help='Folder where to store the output files')
parser.add_argument('--max_vocabulary', default=150000, help='Max number of words considered')
parser.add_argument('--window_size', default=5, help='Size of the window around the current word')
parser.add_argument('--subsampling', action='store_true', default=False, \
                            help='Indicates whether to implement \
                            Word2Vec-style random subsampling of words depending on their frequency \
                            and a t parameter set to 0.00005: \
                            p_subsampling = 1 - math.sqrt((t/word_frequency))')
args = parser.parse_args() 

### Collecting words to be written out to file
with open('../SISSA-EEG/lab/lab_two/chosen_words.txt') as i:
    relevant_words = [l.strip().split('\t')[0] for l in i.readlines()][1:]
assert len(relevant_words) == 32

relevant_words.extend(['oca', 'bus'])

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

all_counts = collections.defaultdict(int)
vocab = dict()
subsample_dict = dict()

corpus = itWacReader(args.input_path) if args.corpus == 'itwac' else itWikiReader(args.input_path)
logging.info('Now counting word frequencies')

for l in tqdm(corpus):
    for w in l:
        all_counts[w] += 1

logging.info('Now finished counting word frequencies')

counter = {c[0] : c[1] for c in sorted(all_counts.items(), key=lambda t: t[1], reverse=True)}

os.makedirs(args.output_path, exist_ok=True)

print('Now writing to file word frequencies')
with open(os.path.join(args.output_path, '{}_frequencies.txt'.format(args.corpus)), 'w') as o:
    full_counter = sum([v for k, v in counter.items()])
    o.write('Frequency_rank\tLemma\tAbsolute frequency\tRelative frequency\tSubsampling probability\t(Number of words in total: {})\n'.format(full_counter))
    for i, count in tqdm(enumerate(counter.items())):
        word_rank = i+1
        word_lemma = count[0]
        if word_lemma == 'passero':
            continue
        elif word_lemma == 'passerotto':
            word_lemma = 'passero'
            absolute_frequency = count[1] + counter['passero']
        else:
            absolute_frequency = count[1]

        vocab[word_lemma] = word_rank if word_rank <= args.max_vocabulary else 0
        subsample_dict[word_rank] = subsampling_prob if word_rank <= args.max_vocabulary else 1.1

        if word_lemma in relevant_words:
            relative_frequency = float(absolute_frequency) / float(full_counter)
            subsampling_prob = 1 - math.sqrt(0.00005/relative_frequency)
            o.write('{}\t{}\t{}\t{}\t{}\n'.format(word_rank, word_lemma, absolute_frequency, relative_frequency, subsampling_prob))

vocab['passerotto'] = vocab['passero']

eeg_vocab = {k : vocab[k] for k in relevant_words}

relative_counter = {vocab[w] : (counter[w]+0.1) / float(full_counter) for w in vocab.keys()}

### Collecting co-occurrences

puncts = string.punctuation

cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
harmonic_window_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
w2v_window_matrix = collections.defaultdict(lambda : collections.defaultdict(int))

print('Now counting full co-occurrences')
for l in tqdm(corpus):

    ### Turning words into indices
    l = [vocab[w] for w in l if vocab[w] != 0]
    ### Removing rare and extremely frequent words according to the subsampling parameter
    if args.subsampling:
        l = [word_index for word_index in l if random.random() > subsample_dict[word_index]]

    ### Finally collecting co-occurrences
    for index, current_word_index in enumerate(l):

        # Left window
        left = [(l[word], \
                 1./float(index-abs(word)), \
                 float(args.window_size+1-(index-abs(word)))/float(args.window_size)) \
                 for word in range(max(index-args.window_size, 0), index)]

        # Right window
        right = [(l[word], \
                  1./float(abs(word)-index), \
                  float(args.window_size+1-(abs(word)-index))/float(args.window_size)) \
                  for word in range(index+1, min(index+args.window_size, len(l)-1))]

        window = left + right
        for cooc_index, harmonic_distance, w2v_distance in window:
            cooc_matrix[current_word_index][cooc_index] += 1

            ### Also collecting other window weightings
            harmonic_window_matrix[current_word_index][cooc_index] += harmonic_distance
            w2v_window_matrix[current_word_index][cooc_index] += w2v_distance

### Adding the diagonals as simple word counts
for w, absolute_frequency in counter.items(): 

    word_index = vocab[w]

    cooc_matrix[word_index][word_index] = absolute_frequency
    harmonic_window_matrix[word_index][word_index] = absolute_frequency
    w2v_window_matrix[word_index][word_index] = absolute_frequency


### Now writing to file the co-occurrences

logging.info('Now writing co-occurrences...')

### Cleaning up the vocabulary and computing the relative frequencies


cooc_out = os.path.join(args.output_path, 'co_occurrences_{}_vocab_{}_window_{}_subsampling_{}'.format(args.corpus, args.max_vocabulary, args.window_size, args.subsampling))
os.makedirs(cooc_out, exist_ok=True)

for word_lemma, word_index_one in tqdm(eeg_vocab.items()):
    short_folder = word_lemma[:3]
    word_out = os.path.join(cooc_out, short_folder)
    os.makedirs(word_out, exist_ok=True)
    with open(os.path.join(word_out, '{}.cooc'.format(word_lemma)), 'w') as o:
        o.write('Co-oc word\tAbsolute co-oc\tRelative co-oc\tPPMI\tHarmonic weight co-oc\tW2V co-oc\n')
        for word_lemma_two, word_index_two in eeg_vocab.items():

            absolute_cooc = cooc_matrix[word_index_one][word_index_two] 
            absolute_freq_one = cooc_matrix[word_index_one][word_index_one] 
            absolute_freq_two = cooc_matrix[word_index_two][word_index_two]

            ### Computing the (Laplacian smoothed) relative cooccurrences counts
            relative_cooc = (absolute_cooc+0.1) / float(full_counter)
            relative_freq_one = relative_counter[word_index_one]
            relative_freq_two = relative_counter[word_index_two]

            # Correcting for low-frequency words following Levy et al. 2015 (context distribution smoothing, CDS)
            relative_freq_two = relative_freq_two**0.75
            
            ppmi_score = max(0, math.log((relative_cooc / (relative_freq_one * relative_freq_two)), 2))
            o.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(\
                      word_lemma_two, absolute_cooc, relative_cooc, ppmi_score, \
                      harmonic_window_matrix[word_index_one][word_index_two], \
                      w2v_window_matrix[word_index_one][word_index_two]))
