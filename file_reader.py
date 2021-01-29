import os 
import re

from tqdm import tqdm

class itWikiReader:

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def __iter__(self):

        for root, direct, files in os.walk(self.folder_path):
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

class itWacReader:

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def __iter__(self):

        for i in range(1, 22):
            with open(os.path.join(self.folder_path, 'itwac3.{}.xml'.format(i)), encoding='utf-8', errors='ignore') as opened_file:
                sentence = []
                for l in opened_file:
                    l = l.strip().split()
                    if len(l) == 3:
                        if l[1] != 'PUN' and l[1] != 'NUM' and '/' not in l[2]:
                            if l[1] != 'SENT':
                                sentence.append(l[2])
                            else:
                                last_sentence = sentence.copy()
                                sentence = []
                                yield last_sentence
