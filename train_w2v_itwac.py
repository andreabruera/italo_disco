import gensim
import logging
import os

from utils import prepare_combined_paths, prepare_file

class CombinedCorpus:

    def __init__(self, paths):
        self.paths = paths

    def __iter__(self):
        for p in self.paths:
            lines = prepare_file(p)
            for l in lines:
                yield l

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

paths = prepare_combined_paths()

corpus = CombinedCorpus(paths)

output_folder = os.path.join('/import/cogsci/andrea/github/SISSA-EEG/resources/', 'w2v_it_combined_corpora')
os.makedirs(output_folder, exist_ok=True)

model = gensim.models.Word2Vec(sentences=corpus, size=300, sg=1, workers=os.cpu_count(), max_final_vocab=150000)
model.save(os.path.join(output_folder, 'w2v_it_combined_corpora_vocab_150000'))
