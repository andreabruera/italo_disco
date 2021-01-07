import os
import spacy
import re
import string
import collections
import tqdm
import argparse

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', default='itWac', choices=['itWac', 'itWiki'], help='indicates which corpus to use, whether itWac or itWiki')
args = parser.parse_args() 

puncts = string.punctuation
all_counts = collections.defaultdict(int)
vocab = collections.defaultdict(int)

cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
weighted_window_matrix = collections.defaultdict(lambda : collections.defaultdict(int))


class itWiki():
    def __iter__(self):
        for root, direct, files in os.walk('extracted_wiki_italian'):
            print('Current folder: {}'.format(root))
            for f in tqdm(files):
                with open(os.path.join(root, f)) as i:
                    for l in i:
                        l = l.strip()
                        if l != '' and 'https' not in l:
                            l = re.sub(r'[^\w\s]+', ' ', l)
                            l = re.sub(r'\s+', ' ', l)
                            l = l.lower()
                            l = l.split()
                            if len(l) > 4:
                                yield l 

class itWac():

    def __iter__(self):
        for i in range(1, 22):
            with open('itwac/itwac3.{}.xml'.format(i), encoding='utf-8', errors='ignore') as f:
                sentence = []
                for l in f:
                    l = l.strip().split()
                    if len(l) == 3:
                        if l[1] != 'PUN' and l[1] != 'NUM':
                            if l[1] != 'SENT':
                                sentence.append(l[2])
                            else:
                                last_sentence = sentence.copy()
                                sentence = []
                                yield last_sentence

corpus = itWac() if args.corpus == 'itWac' else itWiki()

print('Now counting word frequencies')
for l in corpus:
    for w in l:
        all_counts[w] += 1

counter = {c[0] : c[1] for c in sorted(all_counts.items(), key=lambda t: t[1], reverse=True)}

print('Now writing to file word frequencies')
with open('italian_{}_counter.txt'.format(args.corpus), 'w') as o:
    full_counter = sum([v for k, v in counter.items()])
    o.write('N_WORDS_TOTAL\t{}\n'.format(full_counter))
    for i, count in enumerate(counter.items()):
        o.write('{}\t{}\t{}\n'.format(i+1, count[0], count[1]))
        vocab[w] = i

print('Now counting co-occurrences')
for l in corpus:
    for index, w in enumerate(l):
        # Left window
        left = [(l[word], 1/(index-abs(word))) for word in range(max(index-5, 0), index)]
        # Right window
        right = [(l[word], 1/(abs(word)-index)) for word in range(index+1, min(index+5, len(l)-1))]
        print(left)
        print(right)
        window = left + right
        current_index = vocab[w]
        for cooc_word, importance in window:
            cooc_index = vocab[cooc_word]
            cooc_matrix[current_index][cooc_index] += 1
            weighted_window_matrix[current_index][cooc_index] += importance

for i in [50000, 100000, 150000]:
    for count_dict, label in [(cooc_matrix, 'cooc'), (weighted_window_matrix, 'weighted_window')]:
        print('Now writing co-occurrences with max vocabulary={} and window weighting mode={}'.format(i, label))

        selected_vocab = [k for k, v in counter.items() if v > i]

        cooc_out = '{}_{}_50000'.format(args.corpus, label)
        os.makedirs(cooc_out, exist_ok=True)
        for word in selected_vocab:
            index = vocab[word]
            with open(os.path.join(cooc_out, 'word_{:05}.{}'.format(index, label)), 'w') as o:
                for word_two in selected_vocab:
                    index_two = vocab[word_two]
                    o.write('{}\t{}'.format(index_two, count_dict[index][index_two]))
