import collections
import logging
import math
import numpy
import os
import re

from scipy import sparse

def prepare_combined_paths():
    # Setting up the input paths

    logging.info('Loading ItWac files')
    itwac_path = '/import/cogsci/andrea/dataset/corpora/itwac_lemma_reorganized'
    assert os.path.exists(itwac_path)

    itwac_paths = [os.path.join(root, f) for root, direct, files in os.walk(itwac_path) for f in files]
    logging.info('Loading OpenSubtitles files')
    subs_path = '/import/cogsci/andrea/dataset/corpora/open_subtitles_cleaned'
    assert os.path.exists(subs_path)

    subs_paths = [os.path.join(root, f) for root, direct, files in os.walk(subs_path) for f in files]

    paths = itwac_paths.copy() + subs_paths.copy()

    del subs_paths
    del itwac_paths
    return paths

def prepare_file(file_path):

    with open(file_path, encoding='utf-8') as i:
        lines = [l.strip() for l in i.readlines()]

    lines = [re.sub(r'[^\w\s]', '', l).lower().split() for l in lines]
    lines = [[w for w in l if w!=''] for l in lines]    

    return lines

def count_frequencies(file_path):

    lines = prepare_file(file_path)

    counter = dict()
    for l in lines:
        for w in l:
            if w not in counter.keys():
                counter[w] = 1
            else:
                counter[w] += 1

    return counter

def count_coocs(all_args):

    file_path = all_args[0]
    vocab = all_args[1]
    cooc_matrix = all_args[2]
    #cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))

    window_size = 5

    lines = prepare_file(file_path)

    #cooc_list = list()
    #cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
    #cooc_matrix = {v : {v : 0 for k, v in vocab.items()} for k, v in vocab.items()}
    '''
    w2v_window_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
    '''

    for l in lines:

        ### Turning words into indices
        l = [vocab[w] for w in l if vocab[w] != 0]
        '''
        ### Removing rare and extremely frequent words according to the subsampling parameter
        if args.subsampling:
            l = [word_index for word_index in l if random.random() > subsample_dict[word_index]]
        '''

        ### Finally collecting co-occurrences
        for index, current_word_index in enumerate(l):

            # Left window
            left = [\
                   #(
                   l[word] \
                   #, \
                   #1./float(index-abs(word)), \
                   #float(window_size+1-(index-abs(word)))/float(window_size) \
                   #) \
                   for word in range(max(index-window_size, 0), index)]

            # Right window
            right = [\
                    #(
                    l[word] \
                    #, \
                    #1./float(abs(word)-index), \
                    #float(window_size+1-(abs(word)-index))/float(window_size) \
                    #) \
                    for word in range(index+1, min(index+window_size, len(l)-1))]

            window = left + right
            #for cooc_index, harmonic_distance, w2v_distance in window:
            for cooc_index in window:
                cooc_matrix[current_word_index][cooc_index] += 1
                #cooc_matrix[current_word_index, cooc_index] += 1
                #cooc_matrix[cooc_index, current_word_index] += 1
                #cooc_list.append((current_word_index, cooc_index))

                '''
                ### Also collecting other window weightings
                harmonic_window_matrix[current_word_index][cooc_index] += harmonic_distance
                w2v_window_matrix[current_word_index][cooc_index] += w2v_distance
                '''

    return cooc_matrix

def write_coocs_and_ppmi_to_file(args):

    current_word_coocs = args[0]
    word = args[1]
    index = args[2]
    word_out = args[3]
    full_counter = args[4]

    inverted_vocab = args[5]
    counter = args[6]
                            
    with open(os.path.join(word_out, '{}.coocs'.format(word)), 'w') as o:
        o.write('Co-oc word\tAbsolute co-oc\tRelative co-oc\tPPMI\n')
        for index_two, absolute_cooc in current_word_coocs.items():

            word_two = inverted_vocab[index_two]

            #absolute_cooc = cooc_matrix[index][index_two]

            absolute_freq_one = counter[index][0]
            absolute_freq_two = counter[index_two][0]

            ### Computing the (Laplacian smoothed) relative cooccurrences counts
            relative_cooc = (absolute_cooc+0.1) / float(full_counter)
            relative_freq_one = counter[index][1]
            relative_freq_two = counter[index_two][1]

            # Correcting for low-frequency words following Levy et al. 2015 (context distribution smoothing, CDS)
            relative_freq_two = relative_freq_two**0.75
            
            ppmi_score = max(0, \
                             math.log(\
                               (relative_cooc / \
                               (relative_freq_one * relative_freq_two)),\
                                2))
            o.write('{}\t{}\t{}\t{}\n'.format(word_two, \
                                              absolute_cooc, \
                                              relative_cooc, \
                                              ppmi_score))
