import os
import re

from tqdm import tqdm

base_folder = '/import/cogsci/andrea/dataset/corpora/'
out_folder = os.path.join(base_folder ,'open_subtitles_cleaned')
os.makedirs(out_folder, exist_ok=True)

final_sentences = list()
file_counter = 0

subs_folder = os.path.join(base_folder, 'OpenSubtitles', 'xml')
sub_files = [(root, direc, files) for root, direc, files in os.walk(subs_folder)]
for root, direc, files in tqdm(sub_files):
    for f in files:
        with open(os.path.join(root, f), encoding='utf-8') as i:
            lines = list(i.readlines())
        doc = [re.sub(r'.+\"|>|<.+', '', l).strip() for l in lines if '<w' in l or '</s>' in l]
        split_points = [0] + [w_i for w_i, w in enumerate(doc) if w == ''] + [len(doc)-1]
        split_doc = [doc[s+1:split_points[s_i+1]] for s_i, s in enumerate(split_points) \
                                                             if s_i < len(split_points)-1]
        ### Setting a limit of 128 tokens per sentence
        new_sentence = split_doc[0]
        for sent in split_doc[1:]:
            if len(new_sentence) + len(sent) <= 128:
                new_sentence = new_sentence + sent
            else:
                final_sentences.append(new_sentence)
                new_sentence = sent

        if len(final_sentences) > 1000:
            
            with open(os.path.join(out_folder, \
                                   '{:06}.subs'.format(file_counter)), 'w') as o:
                for f in final_sentences:
                    for w in f:
                        o.write('{} '.format(w))
                    o.write('\n')
            
            file_counter += 1
            final_sentences = list()
