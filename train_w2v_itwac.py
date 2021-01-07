import gensim
import logging
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class itWac():

    def __iter__(self):
        for i in range(1, 22):
            with open('itwac3.{}.xml'.format(i), encoding='utf-8', errors='ignore') as f:
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
                            
itWac()

for i in [50000, 100000, 150000]:
    itwac = itWac()
    current_folder = 'w2v_vocab_{}'.format(i)
    os.makedirs(current_folder, exist_ok=True)
    model = gensim.models.Word2Vec(sentences=itwac, size=300, sg=1, workers=48, max_final_vocab=i)
    model.save(os.path.join(current_folder, 'w2v_itwac_vocab_{}'.format(i)))
