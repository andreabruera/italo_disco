import collections
import re

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

    window_size = 5

    lines = prepare_file(file_path)

    #cooc_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
    cooc_matrix = {v : {v : 0 for k, v in vocab.items()} for k, v in vocab.items()}
    '''
    harmonic_window_matrix = collections.defaultdict(lambda : collections.defaultdict(int))
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

                '''
                ### Also collecting other window weightings
                harmonic_window_matrix[current_word_index][cooc_index] += harmonic_distance
                w2v_window_matrix[current_word_index][cooc_index] += w2v_distance
                '''

    return cooc_matrix
