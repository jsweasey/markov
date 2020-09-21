from collections import *
import re as re
import math as math
import random as random
import json as json
import os as os
from itertools import count

class model():

    class gram():

        _id = count(0)

        def __init__(self, item:str, start:str, end:str, category='uncatagorized', counter=0):
            self.id = next(self._id)
            self.item = item
            self.next = defaultdict(int)
            self.start = start
            self.end = end
            self.category = category
            self.counter = counter


    def parseSentence(self, sample_text: str, sentence_stopper: str,) -> list: #TO AID IN SIMPLICITY, CURRENTLY REMOVES ALL NON-LETTER CHARACTERS E.G PUNCTUATION

        char, prev_char, word = '','',''
        sentence_number = 0
        current_sentence, parsed_sentences = [],[]

        add_extra = False #VAR TO ALLOW FOR WORDS AFTER LAST SENTENCE STOPPER TO BE ADDED TO parsed_sentences

        for char in sample_text:
            if char == sentence_stopper and (len(word) > 0 or len(current_sentence[-1:])):
                if len(word) > 0 : current_sentence.append(word.lower())
                parsed_sentences.append(current_sentence)
                current_sentence = []
                sentence_number += 1
                word = ''
            elif re.search(r'\s', char) and not re.search(r'\.|\s', prev_char):
                current_sentence.append(word.lower())
                word = ''
            elif re.search(r'\w', char):
                word += char
            else:
                pass
            prev_char = char
        if add_extra:
            if len(current_sentence) > 0:
                parsed_sentences.append(current_sentence)

        return parsed_sentences

    def loadSampleText(self, file_location: str,) -> str:

        with open(file_location, 'r+') as file_to_read:
            sample_text = str(file_to_read.read())

        return sample_text

    def createModel(self, parsed_sentences: list,):

        item_counter = 0
        sentence_len = []
        n_gram = self.n_gram
        for sentence in parsed_sentences:
            item_counter = 0
            sentence_len.append(len(sentence))
            for x,item in enumerate(sentence):
                to_add, to_add_next = '', ''
                to_add_list, to_add_next_list = [], []
                for y in range(n_gram):
                    if (x+y) > (len(sentence) - 1):
                        break
                    else:
                        to_add_list.append(sentence[(x+y)])
                if len(to_add_list) == n_gram:
                    to_add = ' '.join(to_add_list)
                    for y in range(n_gram):
                        if (x+y+n_gram) > (len(sentence) - 1):
                            to_add_next = '<'
                            to_add_next_list = []
                            break
                        else:
                            to_add_next_list.append(sentence[(x+y+n_gram)])
                    if len(to_add_next_list) > 0:
                        to_add_next = ' '.join(to_add_next_list)
                    if x == 0:
                        if to_add not in list(self.grams_indexed.keys()):
                            self.grams_indexed.update({to_add:self.gram(to_add, to_add_list[0], to_add_list[len(to_add_list)-1])})
                        self.grams_indexed['>'].next[to_add] += 1
                        self.grams_indexed[to_add].next[to_add_next] += 1
                        self.grams_indexed[to_add].counter += 1
                    else:
                        if to_add not in list(self.grams_indexed.keys()):
                            self.grams_indexed.update({to_add:self.gram(to_add, to_add_list[0], to_add_list[len(to_add_list)-1])})
                        self.grams_indexed[to_add].next[to_add_next] += 1
                        self.grams_indexed[to_add].counter += 1
        self.avg_sentence_len = sum(sentence_len)/len(sentence_len)


    def initializeModel(self):
        file_location = self.file_location
        self.grams_indexed.update({'>':self.gram('>','>','>')}) #MAYBE THINK ABOUT MOVING THIS INITIALIZATION
        if self.file_good:
            sample_text = self.loadSampleText(file_location)
            sample_text2parsed_sentences = self.parseSentence(sample_text, self.sentence_stopper)
            self.createModel(sample_text2parsed_sentences)
            print('Initialized model succesfully')
        else:
            print('Issue with %s, please re initialize' %file_location)

    def checkFile(self, file_location : str) -> bool:

        if (os.path.exists(file_location)) and (os.path.getsize(file_location) > 0):
            return_bool = True
        elif os.path.exists(file_location) == False:
            return_bool = False
        elif os.path.getsize(file_location) == 0:
            return_bool = False

        return return_bool

    def __init__(self, file_location: str, sentence_stopper: str, n_gram: int, **keyword_args): #ARGS= auto_init(bool)
        self.grams_indexed = {}
        self.file_good = False
        self.file_location = file_location
        self.sentence_stopper = sentence_stopper
        self.n_gram = n_gram
        self.file_good = self.checkFile(self.file_location)

        if self.file_good == False:
            print('File %s is not good, please check' %self.file_location)
        else:
            if ('auto_init' in keyword_args) and (keyword_args['auto_init'] == True):
                self.initializeModel()

    def wordCanBeSeed(self, word2check:str) -> bool:
        return_bool = False
        seed_words = list(self.grams_indexed['>'].next.keys())
        if (word2check in seed_words):
            return_bool = True

        return return_bool

    def nextGenWord(self, word2check:str) -> str:
        prob_list = []
        next_list = list(self.grams_indexed[word2check].next.keys())
        for word in next_list:
            for i in range(self.grams_indexed[word2check].next.get(word)):
                prob_list.append(word)
        word_return = prob_list[random.randint(0, (len(prob_list)-1))]

        return word_return

    def list2str(self, list2convert:list) -> str:
        word_return = ''
        for word in list2convert:
            word_return += ('%s ' %word)

        return word_return


    def generate(self, **keyword_args): #args = seed_word, min_length, sentence_num,

        seed = ''
        m_len = 0
        no_min = False
        past_min = False
        s_num = 10
        w_num = 0
        g_sentence = []
        g_sentences = []

        #checking kwargs
        if ('seed_word' in keyword_args and self.wordCanBeSeed(keyword_args['seed_word'])):
            seed = keyword_args['seed_word']
        else:
            rand_int = random.randint(0, len(self.grams_indexed['>'].next)-1)
            seed = list(self.grams_indexed['>'].next.keys())[rand_int]
        if ('min_length' in keyword_args and isinstance(keyword_args['min_length'], int)):
            m_len = keyword_args['min_length']
        else:
            no_min = True
        if ('sentence_num' in keyword_args and isinstance(keyword_args['sentence_num'], int)):
            s_num = keyword_args['sentence_num']
        print('n_gram: %s, seed: %s, m_len: %s, s_num: %s' %(self.n_gram, seed, m_len, s_num))

        for x in range(s_num):
            w_num = 0
            n_word = ''
            g_sentence = []
            if no_min:
                past_min = True
            else:
                past_min = False
            while True:
                if (w_num > m_len) and (past_min == False):
                    past_min = True
                if n_word == '<':
                    if (w_num > m_len) or (past_min):
                        g_sentences.append(self.list2str(g_sentence))
                        break
                    else:
                        g_sentence = []
                        n_word = seed
                if w_num == 0:
                    g_sentence.append(seed)
                    n_word = self.nextGenWord(seed)
                else:
                    g_sentence.append(n_word)
                    if n_word != '<':
                        n_word = self.nextGenWord(n_word)
                w_num = len(g_sentence)

        print(g_sentences)

    def statistics(self):
        n_of_grams = len(self.grams_indexed)
        sum_n, sum_u = 0,0
        for gram in self.grams_indexed:
            for next in list(self.grams_indexed[gram].next):
                sum_n += self.grams_indexed[gram].next.get(next)
                sum_u += 1
        avg_n_next = sum_n/n_of_grams
        avg_u_next = sum_u/n_of_grams
        print('Average number of next grams: %s' %avg_n_next)
        print('Average number of unique next grams: %s' %avg_u_next)
        print('Number of grams: %s' %n_of_grams)
        print('Average sentence length: %s' %self.avg_sentence_len)


m = model('sampletext.txt','.',1,auto_init=True)
#m.initializeModel()
m.generate()
m.statistics()
