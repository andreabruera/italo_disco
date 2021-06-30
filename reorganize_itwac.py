import logging
import os

from tqdm import tqdm

from file_reader import itWacReader, itWikiReader

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
corpus = itWacReader('/import/cogsci/andrea/dataset/corpora/itwac')
logging.info('Reorganizing ItWac')

out_folder = '/import/cogsci/andrea/dataset/corpora/itwac_lemma_reorganized'
os.makedirs(out_folder, exist_ok=True)

current_file = list()
current_paragraph = list()
file_counter = 0

for l in tqdm(corpus):

    # Adding sentences to paragraph
    if len(current_paragraph) + len(l) <= 128:
        current_paragraph = current_paragraph + l
    else:
        current_file.append(current_paragraph)
        current_paragraph = list()

    # Adding paragraphs to file
    if len(current_file) == 1000:
        file_path = os.path.join(out_folder, '{:06}.itwac'.format(file_counter))
        with open(file_path, encoding='utf-8', mode='w') as o:
            for l in current_file:
                for w in l:
                    if w == 'passerotto':
                        w = 'passero'
                    o.write('{} '.format(w))
                o.write('\n')
       

        file_counter += 1
        current_file = list()
